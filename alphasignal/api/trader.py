from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from config.settings import settings

logger = logging.getLogger(__name__)

# Try to import Alpaca, fall back to simulation
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import (
        MarketOrderRequest,
        LimitOrderRequest,
        GetOrdersRequest,
    )
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestQuoteRequest
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    TradingClient = None
    MarketOrderRequest = None
    LimitOrderRequest = None
    GetOrdersRequest = None
    OrderSide = None
    TimeInForce = None
    OrderStatus = None
    StockHistoricalDataClient = None
    StockLatestQuoteRequest = None


@dataclass
class Position:
    symbol: str
    qty: float
    side: str
    avg_entry_price: float
    market_value: float
    unrealized_pl: float
    unrealized_plpc: float


@dataclass
class OrderResult:
    success: bool
    order_id: Optional[str] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    qty: Optional[float] = None
    filled_price: Optional[float] = None
    status: Optional[str] = None
    error: Optional[str] = None


class PaperTrader:
    def __init__(self):
        self.simulation_mode = not ALPACA_AVAILABLE or not settings.ALPACA_API_KEY or not settings.ALPACA_SECRET_KEY
        
        if self.simulation_mode:
            logger.warning("Alpaca credentials not configured or alpaca-py not installed - running in SIMULATION mode")
            self.client = None
            self.data_client = None
        else:
            self.client = TradingClient(
                settings.ALPACA_API_KEY,
                settings.ALPACA_SECRET_KEY,
                paper=True,
            )
            self.data_client = StockHistoricalDataClient(
                settings.ALPACA_API_KEY,
                settings.ALPACA_SECRET_KEY,
            )

    def get_account(self) -> Dict[str, Any]:
        if self.simulation_mode:
            return {
                "portfolio_value": 100000.0,
                "cash": 100000.0,
                "buying_power": 200000.0,
                "equity": 100000.0,
            }
        account = self.client.get_account()
        return {
            "portfolio_value": float(account.portfolio_value),
            "cash": float(account.cash),
            "buying_power": float(account.buying_power),
            "equity": float(account.equity),
        }

    def get_positions(self) -> List[Position]:
        if self.simulation_mode:
            return []
        positions = self.client.get_all_positions()
        return [
            Position(
                symbol=p.symbol,
                qty=float(p.qty),
                side=p.side.value,
                avg_entry_price=float(p.avg_entry_price),
                market_value=float(p.market_value),
                unrealized_pl=float(p.unrealized_pl),
                unrealized_plpc=float(p.unrealized_plpc),
            )
            for p in positions
        ]

    def get_latest_price(self, symbol: str) -> float:
        if self.simulation_mode:
            import random
            return round(random.uniform(100, 500), 2)
        quote = self.data_client.get_stock_latest_quote(
            StockLatestQuoteRequest(symbol_or_symbols=symbol)
        )
        return float(quote[symbol].ask_price)

    def place_market_order(
        self,
        symbol: str,
        qty: int,
        side: str,
    ) -> OrderResult:
        if self.simulation_mode:
            price = self.get_latest_price(symbol)
            return OrderResult(
                success=True,
                order_id=f"SIM-{symbol}-{qty}",
                symbol=symbol,
                side=side,
                qty=qty,
                filled_price=price,
                status="FILLED",
            )

        try:
            order = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
            )
            result = self.client.submit_order(order)
            return OrderResult(
                success=True,
                order_id=result.id,
                symbol=result.symbol,
                side=result.side.value,
                qty=float(result.qty),
                filled_price=float(result.filled_avg_price) if result.filled_avg_price else None,
                status=result.status.value,
            )
        except Exception as e:
            logger.error(f"Order failed: {e}")
            return OrderResult(
                success=False,
                symbol=symbol,
                side=side,
                qty=qty,
                status="REJECTED",
                error=str(e),
            )

    def place_limit_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        limit_price: float,
    ) -> OrderResult:
        if self.simulation_mode:
            return OrderResult(
                success=True,
                order_id=f"SIM-LIMIT-{symbol}-{qty}",
                symbol=symbol,
                side=side,
                qty=qty,
                filled_price=limit_price,
                status="FILLED",
            )

        try:
            order = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price,
            )
            result = self.client.submit_order(order)
            return OrderResult(
                success=True,
                order_id=result.id,
                symbol=result.symbol,
                side=result.side.value,
                qty=float(result.qty),
                filled_price=float(result.filled_avg_price) if result.filled_avg_price else None,
                status=result.status.value,
            )
        except Exception as e:
            return OrderResult(
                success=False,
                symbol=symbol,
                side=side,
                qty=qty,
                status="REJECTED",
                error=str(e),
            )

    def cancel_all_orders(self):
        if not self.simulation_mode:
            self.client.cancel_orders()

    def get_order_history(self, limit: int = 50) -> List[Dict]:
        if self.simulation_mode:
            return []
        orders = self.client.get_orders(GetOrdersRequest(limit=limit, status="all"))
        return [
            {
                "id": o.id,
                "symbol": o.symbol,
                "side": o.side.value,
                "qty": float(o.qty),
                "filled_qty": float(o.filled_qty) if o.filled_qty else 0,
                "filled_price": float(o.filled_avg_price) if o.filled_avg_price else None,
                "status": o.status.value,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ]


paper_trader = PaperTrader()