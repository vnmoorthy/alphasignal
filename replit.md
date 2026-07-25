# AlphaSignal — Real-Time Alpha Hunter

A multi-agent AI system that transforms equity research into trade signals, built for the You.com Agentic Hackathon 2024.

## How to Run

The **Streamlit dashboard** starts automatically and is visible in the preview pane.

### Dashboard (default)
```bash
cd alphasignal
streamlit run dashboard/app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
```

### FastAPI server (separate terminal)
```bash
cd alphasignal
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

### CLI commands (run from `alphasignal/` directory)
```bash
cd alphasignal
python main.py analyze NVDA           # Run full agent swarm on a symbol
python main.py watch NVDA AAPL MSFT   # Continuous watchlist monitoring
python main.py account                # Show paper trading account
python main.py trade NVDA 10 buy      # Manual paper trade
python main.py test-api               # Test You.com API connectivity
python main.py demo                   # Hackathon demo
```

## Required Secrets

All set as Replit Secrets:

| Secret | Purpose |
|--------|---------|
| `YDC_API_KEY` | You.com API — live news & finance data |
| `OPENAI_API_KEY` | OpenAI — powers the AI agents (CrewAI) |
| `ALPACA_API_KEY` | Alpaca paper trading |
| `ALPACA_SECRET_KEY` | Alpaca paper trading secret |

## Stack

- **Python 3.11**
- **CrewAI** — multi-agent orchestration (5 agents: News Scanner, Filings Analyst, Sentiment, Risk Manager, Executor)
- **You.com APIs** — live finance research & search
- **Alpaca** — paper trading execution
- **Streamlit** — dashboard UI
- **FastAPI** — REST API server
- **Plotly** — charts

## Project Structure

```
alphasignal/
├── config/settings.py    # All configuration & API keys
├── api/                  # You.com client, Alpaca trader, FastAPI server
├── agents/               # CrewAI agent definitions
├── dashboard/app.py      # Streamlit dashboard (main UI)
├── scripts/              # Demo, watchlist runner
├── main.py               # CLI entry point
└── requirements.txt
```

## User Preferences

- Run the Streamlit dashboard as the primary web interface on port 5000
- Python 3.11 (required; pinned packages incompatible with 3.13)
