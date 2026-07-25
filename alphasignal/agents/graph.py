from __future__ import annotations

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from api.youcom import YouComClient, FinanceResearchResult, SearchResult


class _DemoLLM(LLM):
    """Demo LLM that returns pre-canned responses for hackathon demo without API keys"""
    
    def __init__(self):
        super().__init__(model="demo", temperature=0.1)
        self.call_count = 0
        self.symbol = "NVDA"  # Default, will be detected from prompt
    
    def _detect_symbol(self, prompt: str) -> str:
        """Extract symbol from prompt"""
        import re
        # Look for common stock symbols in the prompt
        symbols = re.findall(r'\b(NVDA|AAPL|MSFT|TSLA|GOOGL|GOOG|AMZN|META|NFLX|AVGO|AMD|INTC|QCOM|CRM|ADBE|ORCL|IBM|CSCO|UBER|LYFT|SNAP|PINS|ROKU|ZM|DOCU|SNOW|PLTR|COIN|HOOD|SOFI|UPST|AFRM)\b', prompt.upper())
        if symbols:
            return symbols[0]
        return "NVDA"
    
    def _get_symbol_data(self, symbol: str) -> dict:
        """Get symbol-specific demo data"""
        data = {
            "NVDA": {
                "name": "NVIDIA",
                "sector": "Semiconductors",
                "key_metric": "Data Center revenue $26.3B (+154% YoY)",
                "catalyst": "Blackwell GPU ramp, AI training dominance 90%+ share",
                "risk": "China export restrictions",
                "target": 575.0,
                "thesis": "NVDA's Data Center dominance (90%+ AI training market share) creates sustained FCF inflection. Blackwell ramp de-risks 2025 estimates. Options flow and institutional accumulation confirm smart money conviction. Risk: China restrictions priced in.",
                "citations": [
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "NVDA 10-Q Q2 FY25", "snippet": "Data Center revenue $26.3B, up 154% YoY"},
                    {"source": "barchart.com", "url": "https://www.barchart.com/...", "title": "NVDA Options Flow", "snippet": "15,234 call contracts at $500/$525 strikes"},
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "13F Filings", "snippet": "Tiger Global: +2.3M shares, Renaissance: +1.8M shares"},
                ]
            },
            "AAPL": {
                "name": "Apple",
                "sector": "Technology",
                "key_metric": "Services revenue $24.2B (+14% YoY), iPhone $39.7B",
                "catalyst": "AI features driving upgrade cycle, Services margin expansion",
                "risk": "China iPhone sales decline, regulatory pressure",
                "target": 235.0,
                "thesis": "AAPL's Services flywheel (30%+ margins) offsets iPhone cyclicality. Apple Intelligence rollout creates multi-year upgrade catalyst. Berkshire Hathaway holding stable at 300M+ shares. Risk: China demand weakness, EU DMA regulation.",
                "citations": [
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "AAPL 10-Q Q3 FY24", "snippet": "Services revenue $24.2B, gross margin 74.1%"},
                    {"source": "barchart.com", "url": "https://www.barchart.com/...", "title": "AAPL Options Flow", "snippet": "Call skew at $220/$230 strikes, 8k contracts"},
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "13F Filings", "snippet": "Berkshire maintains 300M shares, Vanguard +5M"},
                ]
            },
            "MSFT": {
                "name": "Microsoft",
                "sector": "Technology",
                "key_metric": "Azure growth 29% YoY, Commercial Cloud $135B run-rate",
                "catalyst": "Copilot monetization, Azure AI capacity expansion",
                "risk": "Capex intensity ($55B+ FY25), GDPR/AI regulation",
                "target": 485.0,
                "thesis": "MSFT's enterprise distribution + OpenAI partnership creates unmatched AI moat. Azure AI services at inflection. Copilot 365 at $30/seat adds $10B+ ARR potential. Risk: Capex digestion, regulatory scrutiny on AI partnerships.",
                "citations": [
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "MSFT 10-Q Q4 FY24", "snippet": "Intelligent Cloud revenue $28.5B, up 19% YoY"},
                    {"source": "barchart.com", "url": "https://www.barchart.com/...", "title": "MSFT Options Flow", "snippet": "Put/call ratio 0.4, heavy $450/$470 calls"},
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "13F Filings", "snippet": "BlackRock +3M shares, State Street +2M"},
                ]
            },
            "TSLA": {
                "name": "Tesla",
                "sector": "Automotive",
                "key_metric": "Auto gross margin 18.2%, FSD beta 12.5",
                "catalyst": "Robotaxi reveal, FSD v13, Energy storage 200% growth",
                "risk": "EV demand slowdown, Musk distraction, China competition",
                "target": 280.0,
                "thesis": "TSLA's Energy business (Megapack) growing 200%+ with 25% margins. FSD optionality worth $100B+ if solved. Robotaxi unveil 10/10 catalyst. Risk: Auto margin compression, Elon key-person risk, BYD competition.",
                "citations": [
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "TSLA 10-Q Q2 FY24", "snippet": "Energy storage deployments 9.4 GWh, +157% YoY"},
                    {"source": "barchart.com", "url": "https://www.barchart.com/...", "title": "TSLA Options Flow", "snippet": "High IV rank 85%, $250/$300 straddle pricing"},
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "13F Filings", "snippet": "ARK Invest +1.2M shares, Baillie Gifford trimmed"},
                ]
            },
            "GOOGL": {
                "name": "Alphabet",
                "sector": "Technology",
                "key_metric": "Search revenue $48.5B (+14%), Cloud $10.3B (+29%)",
                "catalyst": "Gemini integration across products, Cloud AI margins inflecting",
                "risk": "DOJ antitrust remedy, AI search cannibalization",
                "target": 195.0,
                "thesis": "GOOGL's Search moat intact (90%+ share), Cloud approaching profitability inflection. Gemini 1.5 Pro outperforms GPT-4 on benchmarks. YouTube + Cloud = dual growth engines. Risk: DOJ breakup risk, AI search disruption.",
                "citations": [
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "GOOGL 10-Q Q2 FY24", "snippet": "Google Cloud revenue $10.3B, operating income $1.2B"},
                    {"source": "barchart.com", "url": "https://www.barchart.com/...", "title": "GOOGL Options Flow", "snippet": "Call buying at $180/$190 strikes post-earnings"},
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "13F Filings", "snippet": "Tiger Global +4M shares, Renaissance +2M"},
                ]
            },
            "AMZN": {
                "name": "Amazon",
                "sector": "Technology",
                "key_metric": "AWS $26.3B (+19%), Advertising $12.8B (+20%)",
                "catalyst": "AI workloads on AWS, Retail margin expansion, Kuiper satellite",
                "risk": "FTC lawsuit, Consumer spending slowdown",
                "target": 210.0,
                "thesis": "AMZN's AWS re-acceleration (AI training/inference) + Advertising high-margin growth = FCF inflection. Retail logistics optimization driving margin expansion. Risk: FTC antitrust, macro consumer weakness.",
                "citations": [
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "AMZN 10-Q Q2 FY24", "snippet": "AWS operating margin 36%, Advertising $12.8B"},
                    {"source": "barchart.com", "url": "https://www.barchart.com/...", "title": "AMZN Options Flow", "snippet": "Put/call 0.5, $195/$210 call spreads"},
                    {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": "13F Filings", "snippet": "Citadel +5M shares, Point72 new position"},
                ]
            },
        }
        return data.get(symbol.upper(), data["NVDA"])
    
    def _news_scanner_response(self, prompt: str) -> str:
        symbol = self._detect_symbol(prompt)
        d = self._get_symbol_data(symbol)
        return json.dumps({
            "events": [
                {"type": "earnings", "date": "2024-08-28", "summary": f"{d['name']} Q2 beat, guidance raised", "source": f"{d['name']} Investor Relations"},
                {"type": "product", "date": "2024-08-15", "summary": d['catalyst'], "source": f"{d['name']} Press Release"},
            ],
            "citations": [
                {"source": "sec.gov", "url": "https://www.sec.gov/...", "title": f"{symbol} 10-Q", "snippet": d['key_metric']},
            ]
        })
    
    def _filings_analyst_response(self, prompt: str) -> str:
        symbol = self._detect_symbol(prompt)
        d = self._get_symbol_data(symbol)
        return json.dumps({
            "risk_factors": f"Added {d['risk'].lower()}, removed legacy risk factors",
            "mda_highlights": d['key_metric'],
            "guidance": "Raised FY25 revenue guidance 5-8%, maintained margin outlook",
            "insider_activity": "CEO sold per 10b5-1 plan, CFO purchased shares",
        })
    
    def _sentiment_agent_response(self, prompt: str) -> str:
        symbol = self._detect_symbol(prompt)
        d = self._get_symbol_data(symbol)
        return json.dumps({
            "options_flow": f"Heavy call skew, put/call ratio 0.3-0.5, gamma exposure supporting upside",
            "dark_pool": "30-35% volume in dark pools, buyer aggressive",
            "short_interest": "Low at 1-2% of float, declining trend",
            "institutional": "Top holders accumulating: Tiger, Renaissance, Citadel adding",
        })
    
    def _peer_analyst_response(self, prompt: str) -> str:
        symbol = self._detect_symbol(prompt)
        d = self._get_symbol_data(symbol)
        return json.dumps({
            "valuation": f"{symbol} trades at premium to peers justified by 2x growth rate",
            "growth": f"{symbol} revenue growth 2-3x peer median",
            "quality": "ROIC 40%+, FCF margin 30%+, net cash position",
        })
    
    def _risk_manager_response(self, prompt: str) -> str:
        return json.dumps({
            "position_size_usd": 4350,
            "stop_loss_pct": 0.05,
            "max_risk_pct": 0.01,
            "rr_ratio": 3.2,
        })
    
    def _synthesizer_response(self, prompt: str) -> str:
        symbol = self._detect_symbol(prompt)
        d = self._get_symbol_data(symbol)
        return json.dumps({
            "signal_type": "bullish",
            "confidence": 0.87,
            "thesis": d['thesis'],
            "target_price": d['target'],
            "stop_loss": 0.05,
            "time_horizon": "2-4 weeks",
            "citations": d['citations']
        })
    
    def call(self, messages: list, **kwargs) -> str:
        self.call_count += 1
        prompt = " ".join([m.get("content", "") for m in messages])
        
        for key, func in {
            "news_scanner": self._news_scanner_response,
            "filings_analyst": self._filings_analyst_response,
            "sentiment_agent": self._sentiment_agent_response,
            "peer_analyst": self._peer_analyst_response,
            "risk_manager": self._risk_manager_response,
            "synthesizer": self._synthesizer_response,
        }.items():
            if key.replace("_", " ") in prompt.lower():
                return func(prompt)
        return self._synthesizer_response(prompt)


def _create_demo_llm():
    """Create a demo LLM that returns pre-canned responses"""
    return _DemoLLM()


class SignalType(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    CATALYST = "catalyst"
    RISK = "risk"


@dataclass
class Citation:
    source: str
    url: str
    title: str
    snippet: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AlphaSignal:
    symbol: str
    signal_type: SignalType
    confidence: float
    thesis: str
    citations: List[Citation]
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    time_horizon: str = "1-4 weeks"
    metadata: Dict[str, Any] = field(default_factory=dict)


class NewsScannerTool(BaseTool):
    name: str = "news_scanner"
    description: str = "Scan real-time news, earnings, and catalyst events for a symbol"

    def _run(self, symbol: str, hours_back: int = 24) -> str:
        client = YouComClient()
        result = asyncio.run(client.finance_research(
            f"Latest news, earnings announcements, FDA decisions, M&A rumors, "
            f"analyst actions, and catalyst events for {symbol} in the last {hours_back} hours. "
            f"Include source URLs and timestamps."
        ))
        return self._format_result(result)

    def _format_result(self, result: FinanceResearchResult) -> str:
        citations = [
            {"source": c.source, "url": c.url, "title": c.title, "snippet": c.snippet}
            for c in result.citations
        ]
        return json.dumps({
            "answer": result.answer,
            "citations": citations,
            "confidence": result.confidence,
        })


class FilingsAnalyzerTool(BaseTool):
    name: str = "filings_analyzer"
    description: str = "Analyze SEC filings (10-K, 10-Q, 8-K) for material changes and risks"

    def _run(self, symbol: str) -> str:
        client = YouComClient()
        result = asyncio.run(client.finance_research(
            f"Latest SEC filings analysis for {symbol}: 10-K risk factors, 10-Q MD&A highlights, "
            f"8-K material events, insider transactions, share buybacks, guidance changes. "
            f"Focus on changes vs prior period."
        ))
        return self._format_result(result)


class SentimentAnalyzerTool(BaseTool):
    name: str = "sentiment_analyzer"
    description: str = "Analyze options flow, social sentiment, and institutional positioning"

    def _run(self, symbol: str) -> str:
        client = YouComClient()
        result = asyncio.run(client.finance_research(
            f"Options flow analysis for {symbol}: unusual volume, put/call ratio, gamma exposure, "
            f"dealer positioning, dark pool prints. Social sentiment from Twitter/Reddit/StockTwits. "
            f"Institutional ownership changes, 13F filings, short interest."
        ))
        return self._format_result(result)


class PeerComparisonTool(BaseTool):
    name: str = "peer_comparison"
    description: str = "Compare valuation, growth, and quality metrics vs peers"

    def _run(self, symbol: str) -> str:
        client = YouComClient()
        result = asyncio.run(client.finance_research(
            f"Peer comparison for {symbol}: EV/EBITDA, P/E, PEG, revenue growth, EBITDA margins, "
            f"FCF yield, ROIC, debt/EBITDA vs top 5 competitors. Relative performance YTD, 1Y, 3Y."
        ))
        return self._format_result(result)


class RiskManagerTool(BaseTool):
    name: str = "risk_manager"
    description: str = "Calculate position sizing, stop-loss, and portfolio risk metrics"

    def _run(
        self,
        symbol: str,
        signal_confidence: float,
        portfolio_value: float,
        current_positions: Dict[str, float],
        max_position_pct: float = 0.10,
        max_portfolio_risk: float = 0.02,
    ) -> str:
        position_size = portfolio_value * max_position_pct * signal_confidence
        stop_loss_pct = 0.05 + (0.03 * (1 - signal_confidence))

        return json.dumps({
            "symbol": symbol,
            "recommended_position_usd": round(position_size, 2),
            "max_position_usd": round(portfolio_value * max_position_pct, 2),
            "stop_loss_pct": round(stop_loss_pct, 4),
            "portfolio_risk_pct": round(max_portfolio_risk, 4),
            "current_exposure_pct": sum(current_positions.values()) / portfolio_value if portfolio_value > 0 else 0,
        })


def create_news_scanner_agent(llm: LLM) -> Agent:
    return Agent(
        role="Real-Time News & Catalyst Scanner",
        goal=(
            "Identify all material news, earnings events, FDA decisions, M&A rumors, "
            "analyst actions, and catalyst events for the target symbol in the last 24-48 hours. "
            "Prioritize by market-moving potential."
        ),
        backstory=(
            "You are a former sell-side equity analyst turned prop trader. You know which "
            "headlines actually move stocks vs noise. You read 500+ headlines daily and "
            "extract the 3 that matter. Every claim must have a citation with URL and timestamp."
        ),
        tools=[NewsScannerTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def create_filings_analyst_agent(llm: LLM) -> Agent:
    return Agent(
        role="SEC Filings Forensic Analyst",
        goal=(
            "Extract material changes from SEC filings: risk factor additions/removals, "
            "MD&A tone shifts, guidance changes, related party transactions, insider activity. "
            "Flag anything not yet priced in."
        ),
        backstory=(
            "You spent 8 years reading 10-Ks and 10-Qs at a hedge fund. You know exactly where "
            "companies hide bad news (footnote 14, risk factors section, critical accounting estimates). "
            "You compare current filing vs prior quarter line-by-line. Every finding needs a citation."
        ),
        tools=[FilingsAnalyzerTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def create_sentiment_agent(llm: LLM) -> Agent:
    return Agent(
        role="Alternative Data & Sentiment Analyst",
        goal=(
            "Synthesize options flow, dark pool prints, social sentiment, short interest, "
            "and institutional positioning to gauge smart money direction and retail frenzy risk."
        ),
        backstory=(
            "You built the options flow desk at a market maker. You see the prints before they hit "
            "the tape. You know gamma squeezes, delta hedging flows, and when 0DTE volume signals "
            "top or bottom. Citations from CBOE, ORATS, WhaleWisdom, Quandl."
        ),
        tools=[SentimentAnalyzerTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def create_peer_analyst_agent(llm: LLM) -> Agent:
    return Agent(
        role="Comparative Valuation Specialist",
        goal=(
            "Determine if the symbol is rich/cheap vs peers on multiple frameworks: "
            "multiples, DCF, sum-of-parts, technical vs fundamental discrepancy."
        ),
        backstory=(
            "You ran the comps models at a long/short fund. You know when EV/EBITDA lies "
            "(capital intensity, pension liabilities, lease accounting). You normalize for "
            "accounting differences across peers. Every multiple needs a source."
        ),
        tools=[PeerComparisonTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def create_risk_manager_agent(llm: LLM) -> Agent:
    return Agent(
        role="Portfolio Risk Manager",
        goal=(
            "Size the position, set stop-loss, check correlation with existing portfolio, "
            "verify liquidity, enforce risk limits. Output executable order parameters."
        ),
        backstory=(
            "You blew up a fund once in 2008. Never again. You size by Kelly criterion "
            "adjusted for regime. You know VaR is garbage but use it anyway for compliance. "
            "Hard stops are religion."
        ),
        tools=[RiskManagerTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )


def create_synthesis_agent(llm: LLM) -> Agent:
    return Agent(
        role="Chief Investment Officer - Signal Synthesis",
        goal=(
            "Synthesize all agent outputs into a single AlphaSignal with thesis, "
            "confidence, price target, stop-loss, and full citation trail. "
            "Resolve conflicts between agents. No consensus = no trade."
        ),
        backstory=(
            "You make the final call. You've seen 10,000 pitches, took 200 positions, "
            "made money on 130. You know conviction without evidence is gambling. "
            "You write the investment memo that goes to the IC. Every sentence has a citation."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def build_alpha_signal_crew(
    symbol: str,
    portfolio_value: float = 100000,
    current_positions: Optional[Dict[str, float]] = None,
    model: str = "gpt-4o-mini",
) -> Crew:
    # Check if we have an API key for real LLM, otherwise use demo mode
    import os
    has_api_key = bool(os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))
    
    if has_api_key:
        llm = LLM(model=model, temperature=0.1)
    else:
        # Demo mode: use a mock LLM that returns predefined responses
        llm = _create_demo_llm()

    news_scanner = create_news_scanner_agent(llm)
    filings_analyst = create_filings_analyst_agent(llm)
    sentiment_analyst = create_sentiment_agent(llm)
    peer_analyst = create_peer_analyst_agent(llm)
    risk_manager = create_risk_manager_agent(llm)
    synthesizer = create_synthesis_agent(llm)

    scan_task = Task(
        description=f"Scan all material news and catalysts for {symbol} in last 48 hours",
        expected_output="JSON with key events, catalysts, and citations",
        agent=news_scanner,
    )

    filings_task = Task(
        description=f"Analyze latest SEC filings for {symbol} for material changes",
        expected_output="JSON with risk factor changes, MD&A shifts, guidance, insider activity",
        agent=filings_analyst,
    )

    sentiment_task = Task(
        description=f"Analyze options flow, dark pool, social sentiment, institutional positioning for {symbol}",
        expected_output="JSON with put/call ratio, gamma exposure, short interest, 13F changes",
        agent=sentiment_analyst,
    )

    peer_task = Task(
        description=f"Compare {symbol} valuation and fundamentals vs top 5 peers",
        expected_output="JSON with normalized multiples, growth, quality scores, relative performance",
        agent=peer_analyst,
    )

    def risk_task_callback(context: Dict[str, Any]) -> Task:
        return Task(
            description=(
                f"Calculate position size and risk parameters for {symbol} "
                f"given portfolio value ${portfolio_value:,.0f} and current positions {current_positions or {}}"
            ),
            expected_output="JSON with position_size_usd, stop_loss_pct, max_risk_pct",
            agent=risk_manager,
        )

    synthesis_task = Task(
        description=(
            f"Synthesize all agent outputs for {symbol} into a single AlphaSignal. "
            f"Resolve conflicts. If confidence < 0.65, output NEUTRAL with explanation. "
            f"Include full citation trail. Output valid JSON matching AlphaSignal schema."
        ),
        expected_output="AlphaSignal JSON with thesis, confidence, citations, target, stop",
        agent=synthesizer,
        context=[scan_task, filings_task, sentiment_task, peer_task],
        callback=risk_task_callback,
    )

    return Crew(
        agents=[
            news_scanner,
            filings_analyst,
            sentiment_analyst,
            peer_analyst,
            risk_manager,
            synthesizer,
        ],
        tasks=[scan_task, filings_task, sentiment_task, peer_task, synthesis_task],
        process=Process.sequential,
        verbose=True,
        memory=False,
    )


async def run_alpha_signal(
    symbol: str,
    portfolio_value: float = 100000,
    current_positions: Optional[Dict[str, float]] = None,
    model: str = "gpt-4o-mini",
) -> AlphaSignal:
    crew = build_alpha_signal_crew(symbol, portfolio_value, current_positions, model)
    result = await crew.kickoff_async()

    return parse_alpha_signal(result, symbol)


def parse_alpha_signal(crew_output: Any, symbol: str) -> AlphaSignal:
    raw = crew_output.raw if hasattr(crew_output, 'raw') else str(crew_output)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                # Return neutral signal if JSON is completely malformed
                return AlphaSignal(
                    symbol=symbol,
                    signal_type=SignalType.NEUTRAL,
                    confidence=0.5,
                    thesis=f"Could not parse agent output for {symbol}",
                    citations=[],
                )
        else:
            # Return neutral signal if no JSON found
            return AlphaSignal(
                symbol=symbol,
                signal_type=SignalType.NEUTRAL,
                confidence=0.5,
                thesis=f"Could not parse agent output for {symbol}",
                citations=[],
            )

    citations = [
        Citation(
            source=c.get("source", ""),
            url=c.get("url", ""),
            title=c.get("title", ""),
            snippet=c.get("snippet", ""),
        )
        for c in data.get("citations", [])
    ]

    return AlphaSignal(
        symbol=symbol,
        signal_type=SignalType(data.get("signal_type", "neutral")),
        confidence=float(data.get("confidence", 0.5)),
        thesis=data.get("thesis", ""),
        citations=citations,
        target_price=data.get("target_price"),
        stop_loss=data.get("stop_loss"),
        time_horizon=data.get("time_horizon", "1-4 weeks"),
        metadata=data.get("metadata", {}),
    )