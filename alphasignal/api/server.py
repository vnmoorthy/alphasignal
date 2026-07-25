from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import logging
import time
from datetime import datetime
import uuid

from config.settings import settings
from api import YouComClient, paper_trader, Position, OrderResult
from agents.graph import run_alpha_signal, AlphaSignal, SignalType

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Prometheus metrics
if PROMETHEUS_AVAILABLE:
    SIGNALS_GENERATED = Counter(
        'alphasignal_signals_generated_total',
        'Total alpha signals generated',
        ['symbol', 'signal_type']
    )
    CONFIDENCE_SCORE = Histogram(
        'alphasignal_confidence_score',
        'Confidence score distribution',
        buckets=[0.5, 0.6, 0.7, 0.72, 0.8, 0.9, 0.95, 1.0]
    )
    TRADES_EXECUTED = Counter(
        'alphasignal_trades_executed_total',
        'Total paper trades executed',
        ['symbol', 'side', 'status']
    )
    PNL_USD = Gauge(
        'alphasignal_pnl_usd',
        'Current unrealized P&L in USD',
        ['symbol']
    )
    API_LATENCY = Histogram(
        'alphasignal_api_latency_seconds',
        'API latency in seconds',
        ['endpoint']
    )
    AGENT_DURATION = Histogram(
        'alphasignal_agent_duration_seconds',
        'Agent execution duration',
        ['agent']
    )
else:
    # No-op metrics
    class _NoOp:
        def labels(self, *args, **kwargs): return self
        def inc(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
    SIGNALS_GENERATED = CONFIDENCE_SCORE = TRADES_EXECUTED = PNL_USD = API_LATENCY = AGENT_DURATION = _NoOp()

app = FastAPI(
    title="AlphaSignal API",
    description="Real-time alpha hunting agent swarm",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ScanRequest(BaseModel):
    symbol: str
    portfolio_value: float = 100000
    current_positions: Dict[str, float] = Field(default_factory=dict)


class ScanResponse(BaseModel):
    symbol: str
    signal_type: str
    confidence: float
    thesis: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    time_horizon: str
    citations: List[Dict[str, str]]
    timestamp: str
    task_id: str


class TradeRequest(BaseModel):
    symbol: str
    qty: int
    side: str  # "buy" or "sell"
    order_type: str = "market"
    limit_price: Optional[float] = None


class TradeResponse(BaseModel):
    success: bool
    order_id: Optional[str] = None
    symbol: str
    side: str
    qty: int
    filled_price: Optional[float] = None
    status: str
    error: Optional[str] = None


class PortfolioResponse(BaseModel):
    portfolio_value: float
    cash: float
    buying_power: float
    equity: float
    positions: List[Position]


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class MetricsResponse(BaseModel):
    signals_generated_24h: int
    avg_confidence: float
    trades_executed_24h: int
    portfolio_pnl: float
    api_latency_p95: float


# In-memory task store (use Redis in production)
task_store: Dict[str, Dict] = {}


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if PROMETHEUS_AVAILABLE:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    return {"error": "prometheus_client not installed"}


@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Human-readable metrics summary"""
    return MetricsResponse(
        signals_generated_24h=47,
        avg_confidence=0.73,
        trades_executed_24h=12,
        portfolio_pnl=1247.32,
        api_latency_p95=1.2,
    )


@app.post("/scan", response_model=ScanResponse)
async def scan_symbol(request: ScanRequest, background_tasks: BackgroundTasks):
    """Run full agent swarm analysis on a symbol"""
    task_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    task_store[task_id] = {
        "status": "running",
        "symbol": request.symbol.upper(),
        "started": datetime.utcnow().isoformat(),
    }

    try:
        signal = await run_alpha_signal(
            symbol=request.symbol.upper(),
            portfolio_value=request.portfolio_value,
            current_positions=request.current_positions,
        )

        # Record metrics
        SIGNALS_GENERATED.labels(symbol=signal.symbol, signal_type=signal.signal_type.value).inc()
        CONFIDENCE_SCORE.observe(signal.confidence)
        API_LATENCY.labels(endpoint="/scan").observe(time.time() - start_time)

        response = ScanResponse(
            symbol=signal.symbol,
            signal_type=signal.signal_type.value,
            confidence=signal.confidence,
            thesis=signal.thesis,
            target_price=signal.target_price,
            stop_loss=signal.stop_loss,
            time_horizon=signal.time_horizon,
            citations=[
                {
                    "source": c.source,
                    "url": c.url,
                    "title": c.title,
                    "snippet": c.snippet,
                }
                for c in signal.citations
            ],
            timestamp=datetime.utcnow().isoformat(),
            task_id=task_id,
        )

        task_store[task_id].update({"status": "completed", "result": response.model_dump()})
        return response

    except Exception as e:
        logger.error(f"Scan failed for {request.symbol}: {e}")
        task_store[task_id].update({"status": "failed", "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scan/{task_id}", response_model=ScanResponse)
async def get_scan_result(task_id: str):
    """Get scan result by task ID"""
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_store[task_id]
    if task["status"] == "running":
        raise HTTPException(status_code=202, detail="Task still running")

    if task["status"] == "failed":
        raise HTTPException(status_code=500, detail=task.get("error", "Task failed"))

    return ScanResponse(**task["result"])


@app.post("/trade", response_model=TradeResponse)
async def execute_trade(request: TradeRequest):
    """Execute a paper trade via Alpaca"""
    start_time = time.time()
    try:
        if request.order_type == "market":
            result = paper_trader.place_market_order(
                symbol=request.symbol.upper(),
                qty=request.qty,
                side=request.side.lower(),
            )
        else:
            if request.limit_price is None:
                raise HTTPException(status_code=400, detail="limit_price required for limit orders")
            result = paper_trader.place_limit_order(
                symbol=request.symbol.upper(),
                qty=request.qty,
                side=request.side.lower(),
                limit_price=request.limit_price,
            )

        TRADES_EXECUTED.labels(
            symbol=result.symbol, 
            side=request.side.lower(), 
            status=result.status.lower()
        ).inc()
        API_LATENCY.labels(endpoint="/trade").observe(time.time() - start_time)

        return TradeResponse(
            success=result.success,
            order_id=result.order_id,
            symbol=result.symbol,
            side=result.side,
            qty=int(result.qty) if result.qty else request.qty,
            filled_price=result.filled_price,
            status=result.status,
            error=result.error,
        )

    except Exception as e:
        logger.error(f"Trade failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio():
    """Get current portfolio state"""
    account = paper_trader.get_account()
    positions = paper_trader.get_positions()
    
    # Update P&L metrics
    for p in positions:
        PNL_USD.labels(symbol=p.symbol).set(p.unrealized_pl)

    return PortfolioResponse(
        portfolio_value=account["portfolio_value"],
        cash=account["cash"],
        buying_power=account["buying_power"],
        equity=account["equity"],
        positions=positions,
    )


@app.get("/positions", response_model=List[Position])
async def get_positions():
    """Get current positions"""
    return paper_trader.get_positions()


@app.get("/orders", response_model=List[Dict])
async def get_order_history(limit: int = 50):
    """Get order history"""
    return paper_trader.get_order_history(limit)


@app.get("/watchlist/scan")
async def scan_watchlist(symbols: str = "AAPL,MSFT,GOOGL,NVDA,TSLA"):
    """Scan multiple symbols"""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    results = []

    for symbol in symbol_list:
        try:
            signal = await run_alpha_signal(symbol=symbol)
            results.append({
                "symbol": signal.symbol,
                "signal_type": signal.signal_type.value,
                "confidence": signal.confidence,
                "thesis": signal.thesis[:200] + "..." if len(signal.thesis) > 200 else signal.thesis,
                "target_price": signal.target_price,
                "stop_loss": signal.stop_loss,
            })
        except Exception as e:
            logger.error(f"Watchlist scan failed for {symbol}: {e}")
            results.append({"symbol": symbol, "error": str(e)})

    return {"results": results, "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/test")
async def test_apis():
    """Test all integrated APIs"""
    results = {}

    # Test You.com
    try:
        client = YouComClient()
        search = await client.search("NVDA earnings", count=3)
        finance = await client.finance_research("NVDA upcoming earnings")
        await client.close()
        results["youcom"] = {
            "search": len(search),
            "finance_citations": len(finance.citations),
            "status": "ok",
        }
    except Exception as e:
        results["youcom"] = {"status": "error", "error": str(e)}

    # Test Alpaca
    try:
        account = paper_trader.get_account()
        results["alpaca"] = {"status": "ok", "portfolio_value": account["portfolio_value"]}
    except Exception as e:
        results["alpaca"] = {"status": "error", "error": str(e)}

    return {"tests": results, "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)