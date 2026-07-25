from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List, Dict, Any, Optional
import json
import asyncio

from config.settings import settings
from api.youcom import YouComClient, FinanceResearchResult, SearchResult


class NewsScannerTool(BaseTool):
    name: str = "news_scanner"
    description: str = "Scan real-time financial news, press releases, and SEC filings for a given symbol"

    def _run(self, symbol: str, hours_back: int = 24) -> str:
        async def _scan():
            async with YouComClient() as client:
                results = await client.search(
                    query=f"{symbol} stock news earnings SEC filing {hours_back}h",
                    count=15,
                    recency_days=1,
                )
                return json.dumps([r.model_dump() for r in results], indent=2)

        return asyncio.run(_scan())


class FilingsAnalyzerTool(BaseTool):
    name: str = "filings_analyzer"
    description: str = "Deep research on SEC filings (10-K, 10-Q, 8-K, 13F, Form 4) using You.com Finance Research"

    def _run(self, symbol: str, filing_types: str = "10-K,10-Q,8-K") -> str:
        async def _analyze():
            async with YouComClient() as client:
                result = await client.finance_research(
                    query=f"{symbol} {filing_types} key metrics guidance risk factors management discussion",
                    detail_level="comprehensive",
                )
                return result.model_dump_json(indent=2)

        return asyncio.run(_analyze())


class SentimentTool(BaseTool):
    name: str = "sentiment_analyzer"
    description: str = "Analyze social sentiment, options flow, and institutional positioning"

    def _run(self, symbol: str) -> str:
        async def _sentiment():
            async with YouComClient() as client:
                results = await client.search(
                    query=f"{symbol} options flow put call ratio dark pool short interest institutional holdings",
                    count=10,
                    recency_days=3,
                )
                return json.dumps([r.model_dump() for r in results], indent=2)

        return asyncio.run(_sentiment())


class RiskManagerTool(BaseTool):
    name: str = "risk_manager"
    description: str = "Calculate position sizing, stop-loss, and portfolio risk metrics"

    def _run(
        self,
        symbol: str,
        entry_price: float,
        conviction: float,
        portfolio_value: float,
        existing_positions: str = "{}",
    ) -> str:
        max_position_pct = settings.MAX_POSITION_SIZE_PCT
        confidence_threshold = settings.TRADE_CONFIDENCE_THRESHOLD

        if conviction < confidence_threshold:
            return json.dumps({
                "action": "REJECT",
                "reason": f"Conviction {conviction:.2f} below threshold {confidence_threshold}",
                "position_size": 0,
            })

        max_position_value = portfolio_value * max_position_pct
        risk_per_trade = portfolio_value * 0.01
        stop_loss_pct = 0.05
        shares = int(min(max_position_value, risk_per_trade / stop_loss_pct) / entry_price)

        return json.dumps({
            "action": "APPROVE" if shares > 0 else "REJECT",
            "shares": shares,
            "position_value": shares * entry_price,
            "stop_loss": entry_price * (1 - stop_loss_pct),
            "risk_amount": shares * entry_price * stop_loss_pct,
            "portfolio_pct": (shares * entry_price) / portfolio_value,
        }, indent=2)


class TradeExecutorTool(BaseTool):
    name: str = "trade_executor"
    description: str = "Execute paper trades via Alpaca API"

    def _run(
        self,
        symbol: str,
        shares: int,
        side: str,
        order_type: str = "market",
        limit_price: float = 0,
    ) -> str:
        from alpaca.trading.client import TradingClient
        from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce

        if not settings.ALPACA_API_KEY or not settings.ALPACA_SECRET_KEY:
            return json.dumps({
                "status": "SIMULATED",
                "message": "Alpaca keys not configured - paper trade simulated",
                "symbol": symbol,
                "shares": shares,
                "side": side,
            }, indent=2)

        client = TradingClient(settings.ALPACA_API_KEY, settings.ALPACA_SECRET_KEY, paper=True)

        try:
            if order_type == "market":
                order = MarketOrderRequest(
                    symbol=symbol,
                    qty=shares,
                    side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                )
            else:
                order = LimitOrderRequest(
                    symbol=symbol,
                    qty=shares,
                    side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                    limit_price=limit_price,
                )

            result = client.submit_order(order)
            return json.dumps({
                "status": "FILLED",
                "order_id": result.id,
                "symbol": result.symbol,
                "shares": result.qty,
                "side": result.side.value,
                "filled_price": result.filled_avg_price,
            }, indent=2)
        except Exception as e:
            return json.dumps({"status": "ERROR", "error": str(e)}, indent=2)


def create_agents(llm=None):
    llm = llm or settings.DEFAULT_MODEL

    news_scanner = Agent(
        role="Real-Time Financial News Scanner",
        goal=(
            "Scan all live news, press releases, SEC filings, and regulatory updates "
            "for the target symbol in the last 24 hours. Extract every material event "
            "with exact timestamps, sources, and quotes."
        ),
        backstory=(
            "You are a former Bloomberg terminal analyst who read 500 headlines a day. "
            "You know the difference between a material 8-K and noise. You cite every "
            "claim with the exact URL and timestamp."
        ),
        tools=[NewsScannerTool()],
        llm=llm,
        verbose=True,
        max_iter=3,
    )

    filings_analyst = Agent(
        role="SEC Filings Deep Research Analyst",
        goal=(
            "Perform comprehensive analysis of all recent SEC filings (10-K, 10-Q, 8-K, "
            "13F, Form 4, S-3, 424B). Extract: revenue/eps trends, guidance changes, "
            "risk factor changes, related party transactions, insider trades, share count "
            "changes, debt covenants, segment performance."
        ),
        backstory=(
            "You spent 10 years at a hedge fund reading 10-Ks cover to cover. You know "
            "where companies hide bad news (footnote 14, critical accounting estimates, "
            "MD&A tone shifts). You cite exact section numbers and paragraph references."
        ),
        tools=[FilingsAnalyzerTool()],
        llm=llm,
        verbose=True,
        max_iter=3,
    )

    sentiment_agent = Agent(
        role="Market Structure & Sentiment Analyst",
        goal=(
            "Analyze options flow (unusual volume, put/call skew, max pain), dark pool "
            "prints, short interest trends, institutional 13F holdings changes, "
            "analyst revisions, and social sentiment. Identify positioning extremes."
        ),
        backstory=(
            "You ran a prop desk's market structure team. You know when call skew "
            "implies hedging flow vs speculative buying. You track prime broker data "
            "for short locates. You cite OCC data, FINRA short interest, 13F filing dates."
        ),
        tools=[SentimentTool()],
        llm=llm,
        verbose=True,
        max_iter=3,
    )

    risk_manager = Agent(
        role="Portfolio Risk Manager",
        goal=(
            "Given the synthesized thesis, calculate exact position size, stop-loss, "
            "risk/reward, portfolio heat, correlation with existing positions, and "
            "Kelly-optimal sizing. Reject trades below conviction threshold."
        ),
        backstory=(
            "You managed risk at a multi-manager platform. You've seen 100 PMs blow up "
            "from sizing errors. You enforce: max 5% per position, 1% risk per trade, "
            "hard stops, no averaging down. You output exact share counts."
        ),
        tools=[RiskManagerTool()],
        llm=llm,
        verbose=True,
        max_iter=2,
    )

    trade_executor = Agent(
        role="Paper Trading Execution Agent",
        goal=(
            "Execute approved trades via Alpaca paper trading API. Record order ID, "
            "fill price, timestamp, and commission. Update position tracking."
        ),
        backstory=(
            "You built the order management system at a quant fund. You handle partial "
            "fills, reject bad orders, and maintain an audit trail. You never trade "
            "without risk manager approval."
        ),
        tools=[TradeExecutorTool()],
        llm=llm,
        verbose=True,
        max_iter=1,
    )

    return {
        "news_scanner": news_scanner,
        "filings_analyst": filings_analyst,
        "sentiment_agent": sentiment_agent,
        "risk_manager": risk_manager,
        "trade_executor": trade_executor,
    }


def create_tasks(agents: Dict[str, Agent], symbol: str, portfolio_value: float = 100000):
    news_task = Task(
        description=(
            f"Scan ALL news for {symbol} in last 24 hours. Return: "
            "1) Material events (earnings, guidance, M&A, FDA, contracts, management changes) "
            "2) Exact timestamps and source URLs "
            "3) Direct quotes from management "
            "4) Price reaction at time of release "
            "Filter out: generic market wrap, analyst price target changes without new info, "
            "social media rumors without source."
        ),
        expected_output="JSON array of material events with timestamp, source, headline, summary, url, price_impact",
        agent=agents["news_scanner"],
    )

    filings_task = Task(
        description=(
            f"Deep research on {symbol} SEC filings. Focus on: "
            "1) Last 10-Q/10-Q: revenue by segment, gross margin trends, operating leverage "
            "2) Guidance: exact numbers, tone changes, new/removed metrics "
            "3) Risk factors: new risks, removed risks, expanded language "
            "4) 8-Ks: material agreements, asset sales, bankruptcy risk, auditor changes "
            "5) Form 4: insider buys/sells >$100k, cluster buying "
            "6) 13F: top holder changes, new activists "
            "Cite exact filing date, accession number, section."
        ),
        expected_output="Structured report with citations: filing_date, form_type, section, key_finding, citation_url",
        agent=agents["filings_analyst"],
        context=[news_task],
    )

    sentiment_task = Task(
        description=(
            f"Analyze market structure for {symbol}: "
            "1) Options: unusual volume strikes, put/call ratio vs 20d avg, max pain, "
            "   skew term structure, gamma exposure (GEX) "
            "2) Dark pool: block print volume, % of ADV, buyer/seller aggression "
            "3) Short interest: latest FINRA report, days to cover, utilization, borrow fee "
            "4) 13F: top 10 holder changes, new 5%+ filers, activist entries "
            "5) Analyst: revision trends (est. EPS up/down), price target dispersion "
            "Identify: crowded longs, trapped shorts, gamma squeeze setups."
        ),
        expected_output="JSON with: options_flow, dark_pool, short_interest, institutional_flows, analyst_sentiment, positioning_assessment",
        agent=agents["sentiment_agent"],
        context=[news_task],
    )

    synthesis_task = Task(
        description=(
            "SYNTHESIZE all research into a single investment thesis. Output: "
            "1) THESIS: 2-sentence core thesis "
            "2) CATALYSTS: 3 near-term catalysts with dates/probabilities "
            "3) RISKS: 3 key risks with mitigation "
            "4) VALUATION: DCF/multiple framework with bear/base/bull "
            "5) CONVICTION: 0-1 score with reasoning "
            "6) ENTRY: suggested entry range "
            "7) TIME HORIZON: days/weeks/months "
            "Every claim must reference a citation from previous tasks."
        ),
        expected_output="Structured thesis JSON with all 7 sections and citation references",
        agent=agents["filings_analyst"],
        context=[news_task, filings_task, sentiment_task],
    )

    risk_task = Task(
        description=(
            "Given the thesis and conviction score, calculate: "
            "1) Exact share count for paper trade "
            "2) Stop-loss price (5% from entry) "
            "3) Risk amount ($ and % of portfolio) "
            "4) R:R ratio (target from valuation / stop distance) "
            "5) Portfolio heat impact "
            "6) Correlation check vs SPY/QQQ "
            "REJECT if conviction < 0.72 or R:R < 2:1"
        ),
        expected_output="JSON with action (APPROVE/REJECT), shares, entry, stop, target, risk_pct, rr_ratio",
        agent=agents["risk_manager"],
        context=[synthesis_task],
    )

    execution_task = Task(
        description=(
            "If risk_manager APPROVED: execute paper trade via Alpaca. "
            "Return order confirmation with fill details. "
            "If REJECTED: return rejection reason and no trade."
        ),
        expected_output="JSON with order_id, symbol, shares, side, fill_price, timestamp or rejection_reason",
        agent=agents["trade_executor"],
        context=[risk_task],
    )

    return [news_task, filings_task, sentiment_task, synthesis_task, risk_task, execution_task]


def run_alphasignal(symbol: str, portfolio_value: float = 100000) -> Dict[str, Any]:
    agents = create_agents()
    tasks = create_tasks(agents, symbol, portfolio_value)

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=False,
    )

    result = crew.kickoff(inputs={"symbol": symbol, "portfolio_value": portfolio_value})
    return {"symbol": symbol, "result": result, "tasks_output": [t.output for t in tasks]}