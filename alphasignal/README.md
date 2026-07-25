<div align="center">

<img src="https://img.shields.io/badge/⚡-AlphaSignal-00D4FF?style=for-the-badge&labelColor=070B14&color=00D4FF" height="40"/>

# AlphaSignal

### AI-powered equity research that turns 40 hours of analyst work into a 30-second cited trade thesis

[![Live Demo](https://img.shields.io/badge/Live%20Demo-youcom--hackathonzip.replit.app-00D4FF?style=for-the-badge&logo=replit&logoColor=white)](https://youcom-hackathonzip.replit.app)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-7C6BFF?style=for-the-badge)](https://crewai.com)
[![Alpaca](https://img.shields.io/badge/Alpaca-Paper%20Trading-FFB627?style=for-the-badge)](https://alpaca.markets)
[![License: MIT](https://img.shields.io/badge/License-MIT-00E5A0?style=for-the-badge)](LICENSE)

[![Stars](https://img.shields.io/github/stars/vnmoorthy/alphasignal?style=social)](https://github.com/vnmoorthy/alphasignal/stargazers)
[![Forks](https://img.shields.io/github/forks/vnmoorthy/alphasignal?style=social)](https://github.com/vnmoorthy/alphasignal/network)
[![Issues](https://img.shields.io/github/issues/vnmoorthy/alphasignal)](https://github.com/vnmoorthy/alphasignal/issues)

</div>

---

> **"The first open-source system that does what a $500K/yr buy-side analyst does — in 30 seconds, with every claim cited."**

AlphaSignal deploys a swarm of five specialized AI agents to scan news, read SEC filings, assess options flow, size the position with Kelly-criterion risk management, and execute a paper trade on Alpaca — all from a single ticker symbol. Every conclusion links back to its primary source.

**[→ Try it live](https://youcom-hackathonzip.replit.app)**

---

## ✨ What Makes It Different

| Feature | AlphaSignal | Traditional Tools |
|---|---|---|
| **Speed** | ~30 seconds end-to-end | Hours of manual research |
| **Citations** | Every claim sourced | Opaque black-box output |
| **Agents** | 5 specialized roles (News, Filings, Sentiment, Risk, Executor) | Single monolithic prompt |
| **Risk Management** | Kelly-criterion position sizing + hard stops | Manual guess |
| **Execution** | Automatic paper trade via Alpaca | Copy-paste to broker |
| **LLM** | Claude 3.5 Haiku / GPT-4o-mini (auto-detected) | Locked to one provider |

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/vnmoorthy/alphasignal.git
cd alphasignal/alphasignal

# 2. Install (Python 3.11+)
pip install uv
uv sync

# 3. Configure
cp .env.example .env
# Add: ANTHROPIC_API_KEY or OPENAI_API_KEY, YDC_API_KEY, ALPACA_API_KEY, ALPACA_SECRET_KEY

# 4. Run the dashboard
streamlit run dashboard/app.py --server.port 5000

# 5. Or run the CLI
python main.py analyze NVDA --portfolio 100000
```

> **No API key?** The app falls back to a pre-canned demo mode automatically — you can explore the full UI without any credentials.

---

## 🤖 The Agent Swarm

```
                        ┌─────────────────────────────┐
  You type: NVDA        │     ALPHASIGNAL SWARM        │
  ─────────────────────▶│                              │
                        │  ① NEWS SCANNER              │
                        │    └─ You.com Search API     │
                        │    └─ 24h headlines, filings │
                        │                              │
                        │  ② FILINGS ANALYST           │
                        │    └─ SEC 10-K/10-Q/8-K     │
                        │    └─ Risk factor diffs      │
                        │                              │
                        │  ③ SENTIMENT AGENT           │
                        │    └─ Options flow, 13F      │
                        │    └─ Dark pool prints       │
                        │                              │
                        │  ④ RISK MANAGER              │
                        │    └─ Kelly criterion        │
                        │    └─ Stop-loss calculation  │
                        │                              │
                        │  ⑤ SYNTHESIZER (CIO)         │
                        │    └─ Resolves conflicts     │
                        │    └─ Final confidence score │
                        └──────────────┬──────────────┘
                                       │
                                       ▼
                        ┌─────────────────────────────┐
                        │  ALPHASIGNAL OUTPUT          │
                        │                              │
                        │  Signal:  🟢 BULLISH         │
                        │  Confidence: 87%             │
                        │  Target:  $575               │
                        │  Stop:    $490 (−5%)         │
                        │  Horizon: 2–4 weeks          │
                        │                              │
                        │  Thesis: "NVDA's Data Center │
                        │  dominance (90%+ AI training │
                        │  share) creates sustained    │
                        │  FCF inflection..."          │
                        │                              │
                        │  📎 12 citations from        │
                        │     SEC.gov, CBOE, 13F       │
                        └──────────────┬──────────────┘
                                       │ confidence > 72%
                                       ▼
                        ┌─────────────────────────────┐
                        │  ALPACA PAPER TRADE          │
                        │  BUY 8 NVDA @ market         │
                        │  Stop: $490.00               │
                        └─────────────────────────────┘
```

---

## 🏗️ Architecture

```
alphasignal/
├── agents/
│   └── graph.py          # CrewAI agent definitions, LLM routing, signal parsing
├── api/
│   ├── youcom.py          # You.com Finance & Search API client
│   ├── trader.py          # Alpaca paper trading (positions, orders, P&L)
│   └── server.py          # FastAPI REST endpoints
├── config/
│   └── settings.py        # Pydantic settings, env var management
├── dashboard/
│   └── app.py             # Streamlit dashboard — live P&L, signals, citations
├── scripts/
│   ├── demo.py            # Hackathon demo runner
│   └── watchlist_runner.py# Continuous background monitoring
├── deploy/
│   ├── docker-compose.yml # Full stack: API + Dashboard + Prometheus + Grafana
│   ├── opsera-forge.yaml  # CI/CD pipeline + observability
│   └── grafana/           # Pre-built dashboards
├── tests/                 # pytest suite
├── main.py                # CLI entry point
├── render.yaml            # One-click Render deployment
└── Dockerfile
```

---

## ⚙️ Configuration

Copy `.env.example` and fill in your keys:

```env
# LLM — Anthropic takes priority; OpenAI is fallback; neither = demo mode
ANTHROPIC_API_KEY=sk-ant-...       # https://console.anthropic.com/settings/keys
OPENAI_API_KEY=sk-...              # https://platform.openai.com/api-keys

# You.com — powers all research (news, filings, sentiment)
YDC_API_KEY=...                    # https://api.you.com

# Alpaca Paper Trading — zero real money, real market prices
ALPACA_API_KEY=...                 # https://app.alpaca.markets/paper-trading
ALPACA_SECRET_KEY=...
```

**LLM Auto-Detection** — the agent swarm picks the best available provider at startup:

```
ANTHROPIC_API_KEY set?  →  Claude 3.5 Haiku  (fast, cheap, recommended)
OPENAI_API_KEY set?     →  GPT-4o-mini       (fallback)
Neither set?            →  Demo mode         (pre-canned responses, no cost)
```

---

## 💻 CLI Reference

```bash
# Full analysis — runs all 5 agents
python main.py analyze NVDA --portfolio 100000

# Continuous watchlist (re-scans every 5 min)
python main.py watch NVDA AAPL MSFT TSLA --interval 300

# Portfolio snapshot
python main.py account

# Manual paper trade
python main.py trade NVDA 10 buy

# Verify all API connections
python main.py test-api
```

---

## 🌐 REST API

```
GET  /health              → service status
GET  /account             → portfolio value, buying power
GET  /positions           → open positions with unrealized P&L
GET  /orders              → order history
GET  /signals             → past signals with citation trails
POST /analyze  { symbol } → trigger full agent swarm
POST /trade    { symbol, qty, side } → manual paper trade
GET  /metrics             → Prometheus metrics endpoint
```

---

## 📊 Dashboard

The Streamlit dashboard at [`https://youcom-hackathonzip.replit.app`](https://youcom-hackathonzip.replit.app) gives you:

- **Portfolio Overview** — live equity, cash, day P&L, unrealized gains
- **Signal History** — every past signal with confidence score, thesis, and full citation trail
- **Order Log** — all Alpaca orders with fill prices and status
- **Run Analysis** — enter any ticker and watch the swarm execute in real time
- **Watchlist** — background monitoring with auto-trade on high-confidence signals

---

## 🚢 Deployment

### Replit (Recommended — zero setup)
Fork this repo on Replit, add your secrets, click **Run**. Done.

### Docker
```bash
docker-compose up -d
# API:        http://localhost:8000
# Dashboard:  http://localhost:8501
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000  (admin / alphasignal)
```

### Render
Connect your GitHub repo to Render — `render.yaml` configures all three services automatically.

---

## 🔭 Observability

Pre-wired Prometheus metrics + Grafana dashboards (via Opsera Forge):

| Metric | Type | Description |
|---|---|---|
| `alphasignal_signals_total` | Counter | Signals by symbol and direction |
| `alphasignal_confidence` | Histogram | Confidence score distribution |
| `alphasignal_trades_total` | Counter | Trades by symbol, side, status |
| `alphasignal_pnl_usd` | Gauge | Unrealized P&L per position |
| `alphasignal_agent_duration_seconds` | Histogram | Per-agent latency |

Alerts fire to Slack when confidence exceeds 85%, trade execution fails, or daily drawdown crosses $1K.

---

## 🤝 Contributing

Contributions are welcome. Please open an issue first for major changes.

```bash
# Setup dev environment
git clone https://github.com/vnmoorthy/alphasignal.git
cd alphasignal/alphasignal
uv sync
pre-commit install

# Run tests
pytest tests/ -v

# Lint
ruff check . && black --check .
```

**Good first issues:**
- Add more demo symbols to the `_DemoLLM` fallback
- Implement the side-by-side symbol comparison view
- Add live agent-by-agent progress to the dashboard

---

## 📚 Tech Stack

| Layer | Technology |
|---|---|
| **Agent Orchestration** | [CrewAI](https://crewai.com) |
| **LLM** | Claude 3.5 Haiku (Anthropic) / GPT-4o-mini (OpenAI) |
| **Research Data** | [You.com Finance & Search API](https://api.you.com) |
| **Paper Trading** | [Alpaca Markets](https://alpaca.markets) |
| **Dashboard** | [Streamlit](https://streamlit.io) |
| **API Server** | [FastAPI](https://fastapi.tiangolo.com) |
| **CI/CD + Observability** | [Opsera Forge](https://opsera.io) |
| **Hosting** | [Replit](https://replit.com) / [Render](https://render.com) |

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

Built with ⚡ for the **You.com Agentic Hackathon** at AWS Builder Loft, San Francisco

**[Live Demo](https://youcom-hackathonzip.replit.app)** · **[Report Bug](https://github.com/vnmoorthy/alphasignal/issues)** · **[Request Feature](https://github.com/vnmoorthy/alphasignal/issues)**

</div>
