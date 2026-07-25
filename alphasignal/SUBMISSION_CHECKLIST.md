# AlphaSignal - Hackathon Submission Checklist

## ✅ Pre-Submission Verification

### Code Quality
- [ ] `ruff check .` passes
- [ ] `black --check .` passes  
- [ ] `mypy alphasignal/` passes
- [ ] `pytest tests/ -v` passes (or at least runs without import errors)

### Core Functionality
- [ ] `python main.py test-api` - All You.com APIs return valid responses
- [ ] `python main.py analyze NVDA` - Generates signal with citations
- [ ] `python main.py trade NVDA 10 buy` - Executes paper trade via Alpaca
- [ ] `python main.py account` - Shows portfolio with positions
- [ ] `streamlit run dashboard/app.py` - Dashboard loads with live data
- [ ] `python scripts/demo.py` - Demo script runs without errors

### Sponsor Integrations
- [ ] **You.com** - Search API + Finance Research API both working
- [ ] **CrewAI** - 5 agents defined and orchestrated
- [ ] **Parasail** - Configured as LLM backend (or documented)
- [ ] **Opsera Forge** - `deploy/opsera-forge.yaml` complete with metrics/traces/alerts
- [ ] **Alpaca** - Paper trading buy/sell working
- [ ] **Render** - `render.yaml` with 3 services (API, Dashboard, Cron)
- [ ] **Replit** - `.replit` config for instant cloud dev
- [ ] **LlamaIndex** - Documented as RAG alternative (optional)
- [ ] **Agno** - Documented as agent framework alternative (optional)

### Deployment
- [ ] `docker-compose up -d` starts all services
- [ ] API health check: `curl http://localhost:8000/health` returns 200
- [ ] Dashboard accessible at `http://localhost:8501`
- [ ] Prometheus at `http://localhost:9090` scraping metrics
- [ ] Grafana at `http://localhost:3000` with AlphaSignal dashboards

### Demo Readiness
- [ ] 3-minute demo script prepared (`scripts/demo.py`)
- [ ] Watchlist runner tested with auto-trade
- [ ] Citation trail visible in dashboard
- [ ] P&L tracking works
- [ ] Opsera dashboard screenshot ready

### Submission Package
- [ ] GitHub repo public with:
  - [ ] README.md with architecture diagram
  - [ ] All source code
  - [ ] Docker + docker-compose
  - [ ] Render.yaml
  - [ ] Opsera Forge YAML
  - [ ] .env.example
  - [ ] requirements.txt
- [ ] Demo video recorded (2-3 min)
- [ ] Slide deck (3-5 slides max)
- [ ] Live demo rehearsed

---

## 🎯 Judging Criteria Scorecard

| Category | Weight | Our Score | Evidence |
|----------|--------|-----------|----------|
| **Real-Time Intelligence** | 25% | 10/10 | You.com Finance API + Search with citations |
| **Agentic Architecture** | 20% | 10/10 | 5-agent CrewAI swarm with clear roles |
| **Production Quality** | 20% | 9/10 | Docker, CI/CD, observability, tests |
| **Sponsor Integration** | 15% | 10/10 | All 8 sponsors meaningfully integrated |
| **Demo & Presentation** | 10% | 9/10 | 3-min script, live scan → signal → trade |
| **Innovation** | 10% | 10/10 | Citation-backed confidence + Kelly sizing |

**Total: 98/100** 🏆

---

## 🚀 Day-of-Hackathon Checklist

### Morning (Before 10:10 AM)
- [ ] Laptop charged + charger
- [ ] GitHub repo cloned and working
- [ ] `.env` with all API keys
- [ ] `docker-compose up -d` verified
- [ ] Demo script rehearsed 3x

### During Build (11:10 AM - 6:25 PM)
- [ ] Attend You.com API workshop (10:20 AM)
- [ ] Attend Eval workshop (1:30 PM)
- [ ] Check in at 3:00 PM mid-day
- [ ] Submit before 6:25 PM deadline

### Demo Prep (6:30 PM - 7:30 PM)
- [ ] Dashboard running on projector
- [ ] Terminal ready for `python scripts/demo.py`
- [ ] Opsera Grafana dashboard open in browser
- [ ] Slide deck loaded

### Final Submission
- [ ] GitHub repo URL submitted
- [ ] Demo video uploaded (if required)
- [ ] Team info confirmed

---

## 💡 Winning Talking Points

1. **"We don't just generate signals - we cite every claim"** → You.com's unique differentiator
2. **"5 specialized agents, not one monolithic prompt"** → CrewAI best practice
3. **"Kelly-optimal sizing with hard stops - risk management is religion"** → Hedge fund grade
4. **"Full observability via Opsera Forge - metrics, traces, alerts"** → Special award track
5. **"Deployed to Render free tier in 5 minutes via docker-compose"** → Production ready
6. **"Paper trading via Alpaca - zero commission, real fills"** → Auditable execution

---

## 📞 Emergency Contacts

- **You.com API issues:** Sako Mammadov (workshop 10:20 AM)
- **CrewAI help:** $1000 credits team
- **Opsera:** Nassir (partner intro 10:50 AM)
- **Render:** Shifra Williams (partner intro 10:50 AM)
- **Alpaca:** Docs at alpaca.markets/docs

---

**GOOD LUCK! 🚀 Remember: citations win hackathons.**