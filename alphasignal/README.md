<div align="center">

```
 █████╗ ██╗     ██████╗ ██╗  ██╗ █████╗ ███████╗██╗ ██████╗ ███╗   ██╗ █████╗ ██╗
██╔══██╗██║     ██╔══██╗██║  ██║██╔══██╗██╔════╝██║██╔════╝ ████╗  ██║██╔══██╗██║
███████║██║     ██████╔╝███████║███████║███████╗██║██║  ███╗██╔██╗ ██║███████║██║
██╔══██║██║     ██╔═══╝ ██╔══██║██╔══██║╚════██║██║██║   ██║██║╚██╗██║██╔══██║██║
██║  ██║███████╗██║     ██║  ██║██║  ██║███████║██║╚██████╔╝██║ ╚████║██║  ██║███████╗
╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
```

**An AI agent swarm that does what a $500K/yr buy-side analyst does — in 30 seconds, with every claim cited.**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-youcom--hackathonzip.replit.app-00D4FF?style=for-the-badge)](https://youcom-hackathonzip.replit.app)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CrewAI 0.119](https://img.shields.io/badge/CrewAI-0.119.0-7C6BFF?style=for-the-badge)](https://crewai.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-00E5A0?style=for-the-badge)](LICENSE)
[![You.com Hackathon](https://img.shields.io/badge/You.com_Hackathon-Track_1_Real--Time_Intelligence-FF6B6B?style=for-the-badge)](https://you.com)

[![Stars](https://img.shields.io/github/stars/vnmoorthy/alphasignal?style=social)](https://github.com/vnmoorthy/alphasignal/stargazers)
[![Forks](https://img.shields.io/github/forks/vnmoorthy/alphasignal?style=social)](https://github.com/vnmoorthy/alphasignal/network/members)
[![Issues](https://img.shields.io/github/issues/vnmoorthy/alphasignal)](https://github.com/vnmoorthy/alphasignal/issues)

</div>

---

## 📖 Table of Contents

- [What It Does](#-what-it-does)
- [Live Demo](#-live-demo)
- [How It Works](#-how-it-works)
- [The 6 Agents](#-the-6-agents)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [CLI Reference](#-cli-reference)
- [REST API](#-rest-api)
- [Dashboard](#-dashboard)
- [Output Format](#-output-format)
- [Risk Model](#-risk-model)
- [LLM Routing](#-llm-routing)
- [Project Structure](#-project-structure)
- [Dependencies](#-dependencies)
- [Deployment](#-deployment)
- [Observability](#-observability)
- [Contributing](#-contributing)

---

## ⚡ What It Does

AlphaSignal takes a single stock ticker and runs a **swarm of 6 specialized AI agents** to produce a fully cited investment thesis with an executable paper trade — in about 30 seconds.

A professional equity analyst would spend **40 hours** to:
- Read SEC 10-K/10-Q/8-K filings for risk changes and guidance shifts
- Scan every headline for earnings surprises, M&A rumors, and analyst actions
- Pull options flow data to see what the smart money is doing
- Build a peer comps table to assess relative valuation
- Size the position correctly using portfolio risk math
- Write up the thesis with source citations

AlphaSignal does it automatically, and **every single conclusion links back to its primary source** — SEC filing, news article, 13F filing, or options data. No black box. No hallucinations without evidence.

---

## 🖥️ Live Demo

**[https://youcom-hackathonzip.replit.app](https://youcom-hackathonzip.replit.app)**

No setup required. The app falls back to a demo mode with pre-researched signals for 32 major symbols if no API keys are configured, so you can explore the full interface immediately.

---

## 🔬 How It Works

Type a ticker. Six agents run in sequence. You get a trade signal.

```
INPUT: "NVDA"
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ALPHASIGNAL AGENT SWARM                        │
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │  ① NEWS         │    │  ② FILINGS      │    │  ③ SENTIMENT    │  │
│  │  SCANNER        │    │  ANALYST        │    │  AGENT          │  │
│  │                 │    │                 │    │                 │  │
│  │  You.com        │    │  You.com        │    │  You.com        │  │
│  │  Search API     │    │  Finance API    │    │  Finance API    │  │
│  │                 │    │                 │    │                 │  │
│  │  24h headlines  │    │  10-K/10-Q/8-K  │    │  Options flow   │  │
│  │  Earnings dates │    │  Risk factors   │    │  Put/call ratio │  │
│  │  FDA decisions  │    │  MD&A shifts    │    │  13F filings    │  │
│  │  M&A rumors     │    │  Insider trades │    │  Short interest │  │
│  │  Analyst calls  │    │  Guidance Δ     │    │  Dark pool      │  │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘  │
│           └──────────────────────┴──────────────────────┘           │
│                                  │                                  │
│  ┌─────────────────┐             │             ┌─────────────────┐  │
│  │  ④ PEER         │             │             │  ⑤ RISK         │  │
│  │  ANALYST        │─────────────┘─────────────│  MANAGER        │  │
│  │                 │                           │                 │  │
│  │  You.com        │                           │  Kelly sizing   │  │
│  │  Finance API    │                           │  Stop-loss calc │  │
│  │                 │                           │  Portfolio heat │  │
│  │  EV/EBITDA      │                           │  R:R ratio      │  │
│  │  P/E, PEG       │                           │  Max 5% per     │  │
│  │  FCF yield      │                           │  position       │  │
│  │  vs top 5 peers │                           │                 │  │
│  └─────────────────┘                           └─────────────────┘  │
│                                  │                                  │
│                                  ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  ⑥ SYNTHESIZER (CIO)                        │    │
│  │                                                             │    │
│  │  Resolves agent conflicts · Sets confidence · Cites sources │    │
│  │  If confidence < 65% → NEUTRAL (no trade)                  │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
             ┌────────────────────┴────────────────────┐
             │           confidence ≥ 72% ?             │
             │                                          │
          YES ▼                                      NO ▼
  ┌─────────────────────┐                   ┌─────────────────────┐
  │  ALPACA PAPER TRADE │                   │  NEUTRAL SIGNAL     │
  │  BUY 8 NVDA @market │                   │  No trade placed    │
  │  Stop: $490.00      │                   │  Thesis still shown │
  └─────────────────────┘                   └─────────────────────┘
```

---

## 🤖 The 6 Agents

Each agent has a defined role, specialized goal, and a persona built from real Wall Street archetypes.

### ① News Scanner — *Real-Time News & Catalyst Scanner*

> *"You are a former sell-side equity analyst turned prop trader. You know which headlines actually move stocks vs noise. You read 500+ headlines daily and extract the 3 that matter. Every claim must have a citation with URL and timestamp."*

- **Tool:** `NewsScannerTool` → `YouComClient.finance_research()`
- **Scope:** Last 24–48 hours of news, earnings releases, FDA decisions, M&A rumors, analyst upgrades/downgrades, short squeeze alerts
- **Max iterations:** 3
- **Output:** Material events ranked by price-impact potential, each with source URL and timestamp

---

### ② Filings Analyst — *SEC Filings Forensic Analyst*

> *"You spent 8 years reading 10-Ks and 10-Qs at a hedge fund. You know exactly where companies hide bad news — footnote 14, risk factors section, critical accounting estimates. You compare current filing vs prior quarter line-by-line."*

- **Tool:** `FilingsAnalyzerTool` → `YouComClient.finance_research()`
- **Scope:** 10-K annual reports, 10-Q quarterly reports, 8-K material event filings, Form 4 insider transactions, S-3 registration statements
- **Max iterations:** 3
- **Output:** Risk factor additions/removals, MD&A tone shifts, guidance changes, insider buys/sells, share repurchase activity

---

### ③ Sentiment Agent — *Alternative Data & Sentiment Analyst*

> *"You built the options flow desk at a market maker. You see the prints before they hit the tape. You know gamma squeezes, delta hedging flows, and when 0DTE volume signals top or bottom. Citations from CBOE, ORATS, WhaleWisdom."*

- **Tool:** `SentimentAnalyzerTool` → `YouComClient.finance_research()`
- **Scope:** Options flow (unusual volume, put/call ratio, gamma exposure, dealer positioning), dark pool prints, social sentiment (Twitter/Reddit/StockTwits), 13F institutional filings, short interest trends
- **Max iterations:** 3
- **Output:** Positioning assessment, gamma squeeze risk flag, crowded trade warnings, smart money direction

---

### ④ Peer Analyst — *Comparative Valuation Specialist*

> *"You ran the comps models at a long/short fund. You know when EV/EBITDA lies — capital intensity, pension liabilities, lease accounting. You normalize for accounting differences across peers. Every multiple needs a source."*

- **Tool:** `PeerComparisonTool` → `YouComClient.finance_research()`
- **Scope:** EV/EBITDA, P/E, PEG ratio, revenue growth, EBITDA margins, FCF yield, ROIC, debt/EBITDA — vs top 5 competitors. Relative price performance YTD/1Y/3Y.
- **Max iterations:** 3
- **Output:** Normalized peer comparison table, rich/cheap verdict, valuation framework (multiples, DCF, sum-of-parts)

---

### ⑤ Risk Manager — *Portfolio Risk Manager*

> *"You blew up a fund once in 2008. Never again. You size by Kelly criterion adjusted for regime. You know VaR is garbage but use it anyway for compliance. Hard stops are religion."*

- **Tool:** `RiskManagerTool` — runs **local math**, no API call needed
- **Formula:**
  ```
  position_size  = portfolio_value × 0.05 × signal_confidence
  stop_loss_pct  = 0.05 + (0.03 × (1 − signal_confidence))
  ```
  *Example at 87% confidence on $100K portfolio:*
  ```
  position_size = $100,000 × 0.05 × 0.87 = $4,350
  stop_loss_pct = 0.05 + (0.03 × 0.13)  = 5.39%
  ```
- **Max iterations:** 2
- **Output:** `recommended_position_usd`, `max_position_usd`, `stop_loss_pct`, `portfolio_risk_pct`, `current_exposure_pct`

---

### ⑥ Synthesizer — *Chief Investment Officer*

> *"You make the final call. You've seen 10,000 pitches, took 200 positions, made money on 130. You know conviction without evidence is gambling. You write the investment memo that goes to the IC."*

- **Tools:** None — synthesizes context from all 5 prior agents
- **Logic:** Resolves conflicts between agents. If aggregate confidence < 0.65 → outputs `NEUTRAL` with explanation. Full citation trail required.
- **Max iterations:** 3
- **Output:** AlphaSignal JSON (see [Output Format](#-output-format))

---

## 🚀 Quick Start

### Requirements

- Python 3.11+
- At least one LLM key: `ANTHROPIC_API_KEY` (recommended) or `OPENAI_API_KEY`
- You.com API key: `YDC_API_KEY`
- Alpaca paper trading keys: `ALPACA_API_KEY` + `ALPACA_SECRET_KEY`

> **No keys?** The app auto-detects missing credentials and falls back to demo mode with pre-researched signals for 32 symbols — full UI, no cost.

### Install

```bash
git clone https://github.com/vnmoorthy/alphasignal.git
cd alphasignal/alphasignal

# Install with uv (recommended — faster)
pip install uv
uv sync

# Or with pip
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# Edit .env with your API keys (see Configuration section below)
```

### Run the Dashboard

```bash
streamlit run dashboard/app.py --server.port 5000
# → http://localhost:5000
```

### Run the CLI

```bash
# Analyze a stock
python main.py analyze NVDA

# Analyze with custom portfolio size
python main.py analyze AAPL --portfolio 250000

# Monitor a watchlist every 5 minutes
python main.py watch NVDA AAPL MSFT TSLA --interval 300
```

---

## ⚙️ Configuration

All settings are managed via environment variables (loaded from `.env`):

```env
# ── LLM ──────────────────────────────────────────────────────────────────────
# Anthropic is preferred; OpenAI is fallback; neither = demo mode (free)
ANTHROPIC_API_KEY=sk-ant-api03-...    # https://console.anthropic.com/settings/keys
OPENAI_API_KEY=sk-proj-...            # https://platform.openai.com/api-keys

# ── Research Data (You.com) ───────────────────────────────────────────────────
# Powers all 4 research agents — news, filings, sentiment, peer comparison
YDC_API_KEY=yd_...                    # https://api.you.com

# ── Paper Trading (Alpaca) ───────────────────────────────────────────────────
# Uses Alpaca's paper trading environment — zero real money, real market prices
ALPACA_API_KEY=PK...                  # https://app.alpaca.markets/paper-trading
ALPACA_SECRET_KEY=...
# ALPACA_BASE_URL=https://paper-api.alpaca.markets  (default — do not change)

# ── Optional ─────────────────────────────────────────────────────────────────
PARASAIL_API_KEY=...                  # Alternative fast-inference LLM backend
OPSERA_TOKEN=...                      # CI/CD + observability via Opsera Forge
RENDER_API_KEY=...                    # For Render.com deployment management

# ── App Tuning ───────────────────────────────────────────────────────────────
LOG_LEVEL=INFO
MAX_CONCURRENT_AGENTS=5
TRADE_CONFIDENCE_THRESHOLD=0.72       # Minimum confidence to place a paper trade
MAX_POSITION_SIZE_PCT=0.05            # Max 5% of portfolio per position
```

---

## 💻 CLI Reference

```
Usage: python main.py [COMMAND] [OPTIONS]
```

### `analyze <SYMBOL>`

Runs the full 6-agent swarm on a single symbol. Prints the thesis, confidence score, target, stop-loss, and all citations. Prompts for a paper trade if confidence ≥ 72%.

```bash
python main.py analyze NVDA
python main.py analyze AAPL --portfolio 250000
```

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AlphaSignal › NVDA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Signal      🟢 BULLISH
  Confidence  87%
  Target      $575.00
  Stop-Loss   $490.00 (−5.39%)
  Horizon     2–4 weeks
  Position    $4,350 (8 shares)

  Thesis
  NVDA's Data Center dominance (90%+ AI training market
  share) creates sustained FCF inflection. Blackwell ramp
  de-risks 2025 estimates...

  Citations (12)
  [1] SEC.gov — NVDA 10-Q Q2 FY25
      "Data Center revenue $26.3B, up 154% YoY"
  [2] CBOE — NVDA Options Flow
      "15,234 call contracts at $500/$525 strikes"
  ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Execute paper trade? [y/N]:
```

---

### `watch [SYMBOLS]...`

Continuously monitors a watchlist. Runs the full agent swarm on each symbol every `--interval` seconds. Optionally executes trades automatically when confidence clears the threshold.

```bash
python main.py watch NVDA AAPL MSFT TSLA --interval 300
```

For unattended background operation (with auto-trade), use the dedicated runner:

```bash
python scripts/watchlist_runner.py NVDA AAPL MSFT \
  --interval 300 \
  --portfolio 100000 \
  --auto-trade \
  --min-confidence 0.75
```

| Option | Default | Description |
|---|---|---|
| `--interval` | `300` | Seconds between scans |
| `--portfolio` | `100000` | Portfolio value for position sizing |
| `--auto-trade` | off | Execute trades without confirmation prompt |
| `--min-confidence` | `0.72` | Minimum confidence to trigger auto-trade |

---

### `account`

Displays current paper trading account state: portfolio value, cash, buying power, and all open positions with unrealized P&L.

```bash
python main.py account
```

```
Portfolio Value  $103,412.88
Cash             $ 89,127.44
Buying Power     $ 89,127.44

Open Positions
  NVDA   8 shares  Entry $512.40  Current $543.20  P&L +$246.40 (+4.8%)
  AAPL   5 shares  Entry $218.90  Current $224.15  P&L  +$26.25 (+2.4%)
```

---

### `trade <SYMBOL> <QTY> <SIDE>`

Places a manual market order via Alpaca Paper Trading.

```bash
python main.py trade NVDA 10 buy
python main.py trade TSLA 5 sell
```

---

### `test-api`

Verifies connectivity to all external APIs: You.com Search, You.com Finance Research, You.com Deep Research, and Alpaca.

```bash
python main.py test-api
```

---

### `demo`

Runs the scripted hackathon presentation — a polished 3-minute walkthrough of the full pipeline including simulated agent outputs, trade execution, and observability metrics.

```bash
python main.py demo
```

---

## 🌐 REST API

Start the API server:

```bash
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check — returns `{"status": "ok"}` |
| `GET` | `/metrics` | Prometheus-format metrics scrape endpoint |
| `GET` | `/api/metrics` | Human-readable metrics summary |
| `POST` | `/scan` | Start agent swarm analysis; returns `task_id` immediately |
| `GET` | `/scan/{task_id}` | Poll for results of a prior `/scan` call |
| `POST` | `/trade` | Execute a paper trade (market or limit) |
| `GET` | `/portfolio` | Account value, cash, buying power + all positions |
| `GET` | `/positions` | Open positions with unrealized P&L |
| `GET` | `/orders` | Order history |
| `GET` | `/watchlist/scan?symbols=NVDA,AAPL` | Sequential swarm scan across multiple symbols |
| `POST` | `/api/test` | Connectivity test for You.com and Alpaca |

### POST `/scan`

```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NVDA", "portfolio_value": 100000}'
```

```json
{
  "task_id": "a3f92bc1-4d8e-4f1a-9c2b-7e5d3a8f1b2c",
  "status": "running",
  "symbol": "NVDA"
}
```

### GET `/scan/{task_id}`

```bash
curl http://localhost:8000/scan/a3f92bc1-4d8e-4f1a-9c2b-7e5d3a8f1b2c
```

```json
{
  "status": "complete",
  "signal": {
    "symbol": "NVDA",
    "signal_type": "bullish",
    "confidence": 0.87,
    "thesis": "NVDA's Data Center dominance (90%+ AI training market share)...",
    "target_price": 575.0,
    "stop_loss": 0.0539,
    "time_horizon": "2-4 weeks",
    "citations": [
      {
        "source": "sec.gov",
        "url": "https://www.sec.gov/...",
        "title": "NVDA 10-Q Q2 FY25",
        "snippet": "Data Center revenue $26.3B, up 154% YoY"
      }
    ]
  }
}
```

### POST `/trade`

```bash
curl -X POST http://localhost:8000/trade \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NVDA", "qty": 8, "side": "buy", "order_type": "market"}'
```

---

## 📊 Dashboard

**[https://youcom-hackathonzip.replit.app](https://youcom-hackathonzip.replit.app)**

The Streamlit dashboard has four tabs:

### 📊 Positions Tab
- Live open positions table: symbol, quantity, entry price, current market price, unrealized P&L ($ and %)
- Bar chart: unrealized P&L per position, green/red color-coded
- Total portfolio value, cash, and buying power in header metric cards

### 🔍 Analyze Tab
- Enter any ticker symbol and click **"🚀 Run Agent Swarm"**
- Numbered pipeline steps animate as each agent completes
- Results display: signal type (🟢/🔴/⚪), confidence %, thesis paragraph, price target, stop-loss, time horizon
- Citation cards: each source shows title, domain, snippet, and a **"View source →"** link
- One-click **"🚀 Execute Paper Trade"** button appears when confidence ≥ 72%

### 📜 History Tab
- Full log of all past signals with timestamps
- Filter by signal type (Bullish / Bearish / Neutral / Catalyst / Risk)
- Pie chart: signal type distribution
- Expand any signal to see its full thesis and citation trail

### 📋 Orders Tab
- Complete Alpaca paper trade order history
- Columns: timestamp, symbol, side (Buy/Sell), quantity, fill price, status
- Auto-refreshes every 30 seconds (toggle in header)

---

## 📦 Output Format

The `AlphaSignal` object returned by the swarm:

```python
@dataclass
class AlphaSignal:
    symbol:       str                 # e.g. "NVDA"
    signal_type:  SignalType          # bullish | bearish | neutral | catalyst | risk
    confidence:   float               # 0.0 – 1.0
    thesis:       str                 # investment memo prose
    citations:    List[Citation]      # every claim linked to a source
    target_price: Optional[float]     # analyst price target
    stop_loss:    Optional[float]     # stop-loss as decimal (e.g. 0.05 = 5%)
    time_horizon: str                 # e.g. "2-4 weeks"
    metadata:     Dict[str, Any]      # raw agent outputs, debug info

@dataclass
class Citation:
    source:    str        # domain (e.g. "sec.gov", "barchart.com")
    url:       str        # direct link to the source document
    title:     str        # document title
    snippet:   str        # exact quoted passage
    timestamp: datetime   # when the citation was retrieved
```

---

## 📐 Risk Model

The Risk Manager agent calculates position size and stop-loss locally (no API call) using a Kelly-inspired formula:

```
position_size_usd  = portfolio_value × MAX_POSITION_SIZE_PCT × signal_confidence
stop_loss_pct      = 0.05 + (0.03 × (1 − signal_confidence))
```

**Examples across confidence levels:**

| Confidence | Position ($100K) | Stop-Loss |
|---|---|---|
| 65% (floor) | $3,250 | 6.05% |
| 72% (threshold) | $3,600 | 5.84% |
| 80% | $4,000 | 5.60% |
| 87% (high) | $4,350 | 5.39% |
| 95% (max) | $4,750 | 5.15% |

Hard limits enforced regardless of confidence:
- Max position: **5% of portfolio** (`MAX_POSITION_SIZE_PCT = 0.05`)
- Trade threshold: **72% confidence** (`TRADE_CONFIDENCE_THRESHOLD = 0.72`)
- Max concurrent agents: **5** (`MAX_CONCURRENT_AGENTS = 5`)

---

## 🧠 LLM Routing

The swarm auto-detects and uses the best available LLM at startup — no code changes needed when switching providers:

```python
def _resolve_llm(model: str) -> LLM:
    if os.getenv("ANTHROPIC_API_KEY"):
        return LLM(model="anthropic/claude-3-5-haiku-20241022", temperature=0.1)
    if os.getenv("OPENAI_API_KEY"):
        return LLM(model=model, temperature=0.1)       # default: gpt-4o-mini
    return _create_demo_llm()                           # no cost, pre-canned responses
```

| Priority | Provider | Model | When Used |
|---|---|---|---|
| 1st | **Anthropic** | `claude-3-5-haiku-20241022` | `ANTHROPIC_API_KEY` set |
| 2nd | **OpenAI** | `gpt-4o-mini` | `OPENAI_API_KEY` set, no Anthropic key |
| 3rd | **Demo Mode** | Built-in mock | Neither key present |

**Demo mode** supports 32 symbols with full signal data for `NVDA`, `AAPL`, `MSFT`, `TSLA`, `GOOGL`, `AMZN`. All other symbols map to NVDA data.

Full demo symbol list: `NVDA AAPL MSFT TSLA GOOGL GOOG AMZN META NFLX AVGO AMD INTC QCOM CRM ADBE ORCL IBM CSCO UBER LYFT SNAP PINS ROKU ZM DOCU SNOW PLTR COIN HOOD SOFI UPST AFRM`

---

## 🗂️ Project Structure

```
alphasignal/
│
├── agents/
│   └── graph.py              # All 6 agents, 5 tools, LLM routing, signal parsing
│                             # _resolve_llm() · build_alpha_signal_crew() · parse_alpha_signal()
│
├── api/
│   ├── youcom.py             # You.com API client (search, finance_research, deep_research)
│   │                         # Pydantic models: SearchResult, FinanceResearchResult, Citation
│   │                         # tenacity exponential-backoff retry on all POST requests
│   ├── trader.py             # Alpaca paper trading client
│   │                         # Simulation mode auto-activates if credentials absent
│   │                         # get_account() · get_positions() · place_market_order()
│   └── server.py             # FastAPI REST API
│                             # In-memory task_store (UUID) for async scan results
│                             # Prometheus metrics middleware
│
├── config/
│   └── settings.py           # Pydantic BaseSettings — all env vars with defaults
│                             # TRADE_CONFIDENCE_THRESHOLD=0.72 · MAX_POSITION_SIZE_PCT=0.05
│
├── dashboard/
│   └── app.py                # Streamlit dashboard (1,077 lines)
│                             # Tabs: Positions · Analyze · History · Orders
│                             # Dark theme design system, Plotly charts
│
├── scripts/
│   ├── demo.py               # Hackathon demo runner (scripted 3-min presentation)
│   └── watchlist_runner.py   # Background watchlist worker with --auto-trade flag
│
├── deploy/
│   ├── docker-compose.yml    # API + Dashboard + Prometheus + Grafana
│   ├── opsera-forge.yaml     # CI/CD pipeline + traces + alerts
│   └── grafana/              # Pre-built AlphaSignal dashboards
│
├── tests/                    # pytest suite
├── main.py                   # Click CLI entry point (analyze/watch/account/trade/test-api/demo)
├── Dockerfile
├── render.yaml               # Render.com one-click deploy (3 services)
└── pyproject.toml            # Python 3.11+ · uv-managed dependencies
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `crewai` | `0.119.0` | Multi-agent orchestration framework |
| `streamlit` | `1.37.1` | Dashboard web app |
| `fastapi` | `0.112.0` | REST API server |
| `uvicorn` | `0.30.5` | ASGI server |
| `alpaca-py` | `0.33.0` | Alpaca paper trading client |
| `openai` | `>=1.75.0` | OpenAI API (via LiteLLM in CrewAI) |
| `httpx` | `0.27.2` | Async HTTP client for You.com API |
| `aiohttp` | `3.10.5` | Async HTTP (agent tools) |
| `pydantic` | `2.8.2` | Data validation and settings |
| `pydantic-settings` | `2.4.0` | Environment variable management |
| `pandas` | `2.2.2` | Data manipulation for portfolio analytics |
| `plotly` | `5.23.0` | Interactive charts in dashboard |
| `numpy` | `1.26.4` | Numerical computing |
| `prometheus-client` | `0.19.0` | Metrics exposition |
| `tenacity` | `8.3.0` | Retry logic with exponential backoff |
| `python-dotenv` | `1.0.1` | `.env` file loading |
| `click` | `8.1.7` | CLI framework |
| `rich` | `13.7.1` | Beautiful terminal output |
| `pyyaml` | `6.0.1` | YAML config parsing |

---

## 🚢 Deployment

### Replit (Zero Config)

The app runs live on Replit at [https://youcom-hackathonzip.replit.app](https://youcom-hackathonzip.replit.app).

To fork and run your own instance:
1. Fork this repo on [Replit](https://replit.com)
2. Add your secrets in the Secrets panel: `ANTHROPIC_API_KEY`, `YDC_API_KEY`, `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`
3. Click **Run**

### Docker (Full Stack)

```bash
docker-compose up -d
```

Starts 4 services:

| Service | Port | Description |
|---|---|---|
| API | `8000` | FastAPI REST server |
| Dashboard | `8501` | Streamlit UI |
| Prometheus | `9090` | Metrics collection |
| Grafana | `3000` | Dashboards (admin / alphasignal) |

### Render (One-Click)

`render.yaml` defines 3 services: API server, Streamlit dashboard, and a cron job for watchlist scanning. Connect your GitHub repo on [Render](https://render.com) and it deploys automatically.

### Environment Variables for Production

Same variables as local development (see [Configuration](#-configuration)). Never commit `.env` — use your platform's secrets manager.

---

## 🔭 Observability

Prometheus metrics are exposed at `GET /metrics` and scraped by the included Grafana dashboards:

| Metric | Type | Labels | Description |
|---|---|---|---|
| `alphasignal_signals_generated_total` | Counter | `symbol`, `signal_type` | Total signals produced |
| `alphasignal_confidence_score` | Histogram | `symbol` | Confidence score distribution |
| `alphasignal_trades_executed_total` | Counter | `symbol`, `side`, `status` | Paper trades placed |
| `alphasignal_pnl_usd` | Gauge | `symbol` | Unrealized P&L per position |
| `alphasignal_api_latency_seconds` | Histogram | `endpoint` | API response time p50/p95/p99 |
| `alphasignal_agent_duration_seconds` | Histogram | `agent_name` | Per-agent execution time |

**Opsera Forge Alerts:**

| Condition | Channel |
|---|---|
| Signal confidence > 85% | Slack |
| Trade execution failure | PagerDuty |
| API latency p95 > 5s | Slack |
| Daily drawdown > $1,000 | Slack |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/alphasignal.git
cd alphasignal/alphasignal

# Create a branch
git checkout -b feat/your-feature

# Install dev dependencies
uv sync

# Run tests
pytest tests/ -v

# Lint
ruff check . && black --check .

# Push and open a PR
```

**Good first issues to tackle:**
- [ ] Live agent-by-agent progress bar in the dashboard (agents emit events as they complete)
- [ ] Side-by-side symbol comparison view (analyze two tickers and diff their signals)
- [ ] Persistent signal history (SQLite backend instead of in-memory store)
- [ ] Add more canned data to `_DemoLLM` for `META`, `NFLX`, `AMD`, etc.
- [ ] Watchlist persistence across app restarts

---

## 📄 License

MIT — see [LICENSE](LICENSE). Free to use, fork, and build on.

---

<div align="center">

Built at the **You.com Agentic Hackathon** · AWS Builder Loft, San Francisco

**[Live Demo](https://youcom-hackathonzip.replit.app)** · **[Open an Issue](https://github.com/vnmoorthy/alphasignal/issues)** · **[Request a Feature](https://github.com/vnmoorthy/alphasignal/issues/new)**

*If AlphaSignal saved you research time, consider starring the repo ⭐*

</div>
