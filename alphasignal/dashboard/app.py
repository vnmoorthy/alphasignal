"""
AlphaSignal Streamlit Dashboard - Live P&L & Citation Trail
Run with: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from api.trader import paper_trader, Position, OrderResult


st.set_page_config(
    page_title="AlphaSignal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Design System ────────────────────────────────────────────────────────────
COLORS = {
    "bg_base":      "#070B14",
    "bg_card":      "#0D1421",
    "bg_card2":     "#111827",
    "border":       "#1E2D45",
    "border_glow":  "#00D4FF33",
    "accent":       "#00D4FF",
    "accent_dim":   "#00D4FF22",
    "accent_green": "#00E5A0",
    "accent_red":   "#FF4D6A",
    "accent_yellow":"#FFB627",
    "accent_purple":"#7C6BFF",
    "text_primary": "#EEF2FF",
    "text_secondary":"#8899BB",
    "text_dim":     "#4A5A78",
}

st.markdown(f"""
<style>
    /* ── Base ── */
    html, body, [class*="css"] {{
        font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    .stApp {{
        background: {COLORS['bg_base']};
    }}
    section[data-testid="stSidebar"] {{
        background: {COLORS['bg_card']};
        border-right: 1px solid {COLORS['border']};
    }}
    /* Hide default Streamlit header bar */
    header[data-testid="stHeader"] {{
        background: transparent;
        border-bottom: none;
    }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {COLORS['bg_base']}; }}
    ::-webkit-scrollbar-thumb {{ background: {COLORS['border']}; border-radius: 3px; }}

    /* ── Logo / Brand ── */
    .brand-row {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 4px;
    }}
    .brand-icon {{
        font-size: 2rem;
        line-height: 1;
    }}
    .brand-title {{
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, {COLORS['accent']} 0%, {COLORS['accent_green']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .brand-sub {{
        font-size: 0.78rem;
        color: {COLORS['text_dim']};
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 500;
        margin-bottom: 20px;
    }}

    /* ── Metric Cards ── */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin: 20px 0 28px 0;
    }}
    .metric-card {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 20px 22px;
        position: relative;
        overflow: hidden;
        transition: border-color 0.2s;
    }}
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, {COLORS['accent']}88, {COLORS['accent_green']}88);
    }}
    .metric-card-accent {{
        border-color: {COLORS['accent']}44;
        box-shadow: 0 0 24px {COLORS['accent']}11;
    }}
    .metric-label {{
        font-size: 0.7rem;
        font-weight: 600;
        color: {COLORS['text_dim']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }}
    .metric-value {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {COLORS['text_primary']};
        letter-spacing: -0.02em;
        line-height: 1;
    }}
    .metric-sub {{
        font-size: 0.8rem;
        color: {COLORS['text_secondary']};
        margin-top: 6px;
    }}
    .metric-icon {{
        position: absolute;
        top: 18px; right: 18px;
        font-size: 1.4rem;
        opacity: 0.25;
    }}
    .positive {{ color: {COLORS['accent_green']} !important; }}
    .negative {{ color: {COLORS['accent_red']} !important; }}
    .neutral  {{ color: {COLORS['accent_yellow']} !important; }}

    /* ── Signal Badges ── */
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }}
    .badge-bullish  {{ background: {COLORS['accent_green']}22; color: {COLORS['accent_green']}; border: 1px solid {COLORS['accent_green']}44; }}
    .badge-bearish  {{ background: {COLORS['accent_red']}22;   color: {COLORS['accent_red']};   border: 1px solid {COLORS['accent_red']}44; }}
    .badge-neutral  {{ background: {COLORS['accent_yellow']}22;color: {COLORS['accent_yellow']};border: 1px solid {COLORS['accent_yellow']}44; }}
    .badge-catalyst {{ background: {COLORS['accent']}22;       color: {COLORS['accent']};       border: 1px solid {COLORS['accent']}44; }}
    .badge-risk     {{ background: {COLORS['accent_red']}22;   color: {COLORS['accent_red']};   border: 1px solid {COLORS['accent_red']}44; }}

    /* ── Signal Card ── */
    .signal-card {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 22px 24px;
        margin: 12px 0;
        position: relative;
    }}
    .signal-card-bullish  {{ border-left: 3px solid {COLORS['accent_green']}; }}
    .signal-card-bearish  {{ border-left: 3px solid {COLORS['accent_red']}; }}
    .signal-card-neutral  {{ border-left: 3px solid {COLORS['accent_yellow']}; }}
    .signal-card-catalyst {{ border-left: 3px solid {COLORS['accent']}; }}
    .signal-card-risk     {{ border-left: 3px solid {COLORS['accent_red']}; }}
    .signal-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
    }}
    .signal-symbol {{
        font-size: 1.4rem;
        font-weight: 800;
        color: {COLORS['text_primary']};
        letter-spacing: -0.02em;
    }}
    .signal-confidence {{
        margin-left: auto;
        font-size: 1.1rem;
        font-weight: 700;
        color: {COLORS['accent']};
    }}
    .signal-thesis {{
        font-size: 0.95rem;
        color: {COLORS['text_secondary']};
        line-height: 1.65;
        margin-bottom: 16px;
    }}
    .signal-meta {{
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
    }}
    .signal-meta-item {{
        display: flex;
        flex-direction: column;
        gap: 2px;
    }}
    .signal-meta-label {{
        font-size: 0.65rem;
        font-weight: 600;
        color: {COLORS['text_dim']};
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}
    .signal-meta-value {{
        font-size: 0.95rem;
        font-weight: 600;
        color: {COLORS['text_primary']};
    }}

    /* ── Citation Cards ── */
    .citation-card {{
        background: {COLORS['bg_card2']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 8px;
        display: flex;
        gap: 12px;
    }}
    .citation-num {{
        font-size: 0.7rem;
        font-weight: 700;
        color: {COLORS['accent']};
        background: {COLORS['accent_dim']};
        border-radius: 4px;
        padding: 2px 7px;
        height: fit-content;
        white-space: nowrap;
        margin-top: 2px;
    }}
    .citation-title {{
        font-size: 0.88rem;
        font-weight: 600;
        color: {COLORS['text_primary']};
        margin-bottom: 4px;
    }}
    .citation-meta {{
        font-size: 0.75rem;
        color: {COLORS['text_dim']};
        margin-bottom: 5px;
    }}
    .citation-snippet {{
        font-size: 0.8rem;
        color: {COLORS['text_secondary']};
        line-height: 1.5;
    }}
    .citation-link {{
        display: inline-block;
        font-size: 0.75rem;
        color: {COLORS['accent']};
        text-decoration: none;
        margin-top: 5px;
    }}

    /* ── Section Headers ── */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1rem;
        font-weight: 700;
        color: {COLORS['text_primary']};
        margin: 24px 0 14px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid {COLORS['border']};
    }}
    .section-header-icon {{
        font-size: 1.1rem;
    }}

    /* ── Pipeline Steps ── */
    .pipeline {{
        display: flex;
        flex-direction: column;
        gap: 6px;
    }}
    .pipeline-step {{
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 10px 12px;
        background: {COLORS['bg_card2']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        font-size: 0.82rem;
    }}
    .pipeline-num {{
        font-size: 0.7rem;
        font-weight: 700;
        color: {COLORS['accent']};
        background: {COLORS['accent_dim']};
        border-radius: 4px;
        padding: 1px 6px;
        margin-top: 1px;
        white-space: nowrap;
    }}
    .pipeline-name {{
        font-weight: 600;
        color: {COLORS['text_primary']};
    }}
    .pipeline-desc {{
        color: {COLORS['text_dim']};
        font-size: 0.75rem;
    }}

    /* ── Empty States ── */
    .empty-state {{
        text-align: center;
        padding: 48px 24px;
        color: {COLORS['text_dim']};
    }}
    .empty-state-icon {{
        font-size: 3rem;
        margin-bottom: 12px;
        opacity: 0.4;
    }}
    .empty-state-text {{
        font-size: 0.9rem;
        line-height: 1.6;
    }}

    /* ── Sidebar Brand ── */
    .sidebar-brand {{
        padding: 20px 0 8px 0;
        margin-bottom: 4px;
    }}
    .sidebar-brand-title {{
        font-size: 1.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, {COLORS['accent']} 0%, {COLORS['accent_green']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .sidebar-section {{
        font-size: 0.65rem;
        font-weight: 700;
        color: {COLORS['text_dim']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 18px 0 8px 0;
    }}
    .sidebar-tool {{
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 7px 10px;
        border-radius: 8px;
        background: {COLORS['bg_card2']};
        border: 1px solid {COLORS['border']};
        margin-bottom: 5px;
        font-size: 0.8rem;
    }}
    .sidebar-tool-name {{
        font-weight: 600;
        color: {COLORS['text_primary']};
    }}
    .sidebar-tool-desc {{
        color: {COLORS['text_dim']};
        font-size: 0.72rem;
    }}
    .sidebar-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: {COLORS['accent_green']};
        box-shadow: 0 0 6px {COLORS['accent_green']};
        flex-shrink: 0;
    }}

    /* ── Streamlit Overrides ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {COLORS['bg_card']};
        border-radius: 10px;
        padding: 4px;
        border: 1px solid {COLORS['border']};
        gap: 2px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 7px;
        color: {COLORS['text_secondary']};
        font-weight: 600;
        font-size: 0.85rem;
        padding: 7px 20px;
    }}
    .stTabs [aria-selected="true"] {{
        background: {COLORS['bg_base']} !important;
        color: {COLORS['text_primary']} !important;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['accent']} 0%, {COLORS['accent_green']} 100%);
        color: #000 !important;
        font-weight: 700;
        border: none;
        border-radius: 9px;
        font-size: 0.85rem;
        letter-spacing: 0.01em;
        transition: opacity 0.15s;
    }}
    .stButton > button:hover {{ opacity: 0.88; }}
    div[data-testid="stTextInput"] > div > div > input {{
        background: {COLORS['bg_card2']};
        border: 1px solid {COLORS['border']};
        border-radius: 9px;
        color: {COLORS['text_primary']};
        font-size: 0.9rem;
    }}
    div[data-testid="stTextInput"] > div > div > input:focus {{
        border-color: {COLORS['accent']}88;
        box-shadow: 0 0 0 2px {COLORS['accent_dim']};
    }}
    div[data-testid="stMetric"] {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 14px 16px;
    }}
    div[data-testid="stMetricValue"] {{
        color: {COLORS['text_primary']};
        font-weight: 700;
    }}
    div[data-testid="stMetricDelta"] {{ font-size: 0.8rem; }}
    .stDataFrame {{
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        overflow: hidden;
    }}
    [data-testid="stExpander"] {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
    }}
    .stAlert {{
        border-radius: 10px;
        border: none;
    }}
    /* multiselect */
    div[data-baseweb="select"] > div {{
        background: {COLORS['bg_card2']};
        border-color: {COLORS['border']};
        border-radius: 9px;
    }}
    /* spinner */
    .stSpinner > div {{
        border-top-color: {COLORS['accent']} !important;
    }}
    /* info box */
    div[data-testid="stInfo"] {{
        background: {COLORS['accent_dim']};
        border-left-color: {COLORS['accent']};
        border-radius: 10px;
    }}
</style>
""", unsafe_allow_html=True)


# ─── Plotly theme ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLORS["text_secondary"]),
    xaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"], zeroline=False),
    yaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"], zeroline=False),
    margin=dict(l=16, r=16, t=40, b=16),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=COLORS["border"]),
)


# ─── Data helpers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_account():
    return paper_trader.get_account()

@st.cache_data(ttl=30)
def get_positions():
    return paper_trader.get_positions()

@st.cache_data(ttl=30)
def get_orders():
    return paper_trader.get_order_history(limit=100)

def load_signals():
    output_dir = Path("output")
    if not output_dir.exists():
        return []
    signals = []
    for f in output_dir.glob("signal_*.json"):
        try:
            with open(f) as fp:
                data = json.load(fp)
                data["_file"] = f.name
                signals.append(data)
        except Exception:
            pass
    signals.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return signals

def load_latest_signal(symbol):
    for s in load_signals():
        if s.get("symbol", "").upper() == symbol.upper():
            return s
    return None


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">⚡ AlphaSignal</div>
            <div style="font-size:0.72rem;color:{COLORS['text_dim']};margin-top:2px;">Real-Time Alpha Hunter</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Quick stats via native Streamlit metrics
        st.markdown(f'<div class="sidebar-section">Portfolio</div>', unsafe_allow_html=True)
        account  = get_account()
        positions = get_positions()
        total_pl = sum(p.unrealized_pl for p in positions)
        pv       = account.get("portfolio_value", 0)
        pct      = (total_pl / pv * 100) if pv else 0
        st.metric("Value",     f"${pv:,.0f}")
        st.metric("P&L",       f"${total_pl:,.2f}", delta=f"{pct:+.2f}%")
        st.metric("Positions", len(positions))

        st.markdown("---")
        st.markdown(f'<div class="sidebar-section">Powered by</div>', unsafe_allow_html=True)

        tools = [
            ("🔍", "You.com",       "Finance Research API"),
            ("🤖", "CrewAI",        "Multi-Agent Orchestration"),
            ("⚡", "Parasail",      "Ultra-Fast Inference"),
            ("📊", "Alpaca",        "Paper Trading"),
            ("🛠", "Opsera Forge",  "CI/CD + Observability"),
            ("☁️", "Render",        "Hosting"),
        ]
        for icon, name, desc in tools:
            st.markdown(f"""
            <div class="sidebar-tool">
                <div class="sidebar-dot"></div>
                <div>
                    <div class="sidebar-tool-name">{icon} {name}</div>
                    <div class="sidebar-tool-desc">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────────────────────────
def render_header():
    col1, col2, col3 = st.columns([5, 1, 1])
    with col1:
        now = datetime.utcnow().strftime("%b %d, %Y  %H:%M UTC")
        st.markdown(f"""
        <div class="brand-row">
            <span class="brand-title">AlphaSignal</span>
        </div>
        <div class="brand-sub">Real-Time Alpha Hunter &nbsp;·&nbsp; You.com Hackathon &nbsp;·&nbsp; Track 1: Real-Time Intelligence &nbsp;·&nbsp; {now}</div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("⟳  Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col3:
        auto = st.checkbox("Auto (30s)", value=False)
        if auto:
            st.cache_data.clear()


# ─── Metric Cards ─────────────────────────────────────────────────────────────
def render_metrics(account, positions):
    pv    = account.get("portfolio_value", 0)
    cash  = account.get("cash", 0)
    bp    = account.get("buying_power", 0)
    pl    = sum(p.unrealized_pl for p in positions)
    pl_pct = (pl / pv * 100) if pv > 0 else 0
    pl_class = "positive" if pl >= 0 else "negative"
    pl_arrow  = "▲" if pl >= 0 else "▼"

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card metric-card-accent">
            <div class="metric-icon">💼</div>
            <div class="metric-label">Portfolio Value</div>
            <div class="metric-value">${pv:,.2f}</div>
            <div class="metric-sub">Paper trading account</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">📈</div>
            <div class="metric-label">Total P&amp;L</div>
            <div class="metric-value {pl_class}">${pl:,.2f}</div>
            <div class="metric-sub {pl_class}">{pl_arrow} {pl_pct:+.2f}% all-time</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">💵</div>
            <div class="metric-label">Cash</div>
            <div class="metric-value">${cash:,.2f}</div>
            <div class="metric-sub">Available to deploy</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">⚡</div>
            <div class="metric-label">Buying Power</div>
            <div class="metric-value">${bp:,.2f}</div>
            <div class="metric-sub">Including margin</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Positions ────────────────────────────────────────────────────────────────
def render_positions(positions):
    st.markdown('<div class="section-header"><span class="section-header-icon">📊</span> Current Positions</div>', unsafe_allow_html=True)

    if not positions:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <div class="empty-state-text">No open positions yet.<br>Run an analysis to generate your first trade signal.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    df = pd.DataFrame([{
        "Symbol":  p.symbol,
        "Qty":     p.qty,
        "Side":    p.side.upper(),
        "Entry":   f"${p.avg_entry_price:.2f}",
        "Current": f"${p.market_value/p.qty:.2f}" if p.qty else "N/A",
        "Value":   f"${p.market_value:,.2f}",
        "P&L ($)": p.unrealized_pl,
        "P&L (%)": p.unrealized_plpc,
    } for p in positions])

    def color_pl(val):
        if isinstance(val, (int, float)):
            return f"color: {'#00E5A0' if val >= 0 else '#FF4D6A'}"
        return ""

    styled = df.style.map(color_pl, subset=["P&L ($)", "P&L (%)"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    if positions:
        st.markdown('<div class="section-header" style="margin-top:28px;"><span class="section-header-icon">📉</span> Position P&L</div>', unsafe_allow_html=True)
        colors = [COLORS["accent_green"] if p.unrealized_pl >= 0 else COLORS["accent_red"] for p in positions]
        fig = go.Figure(go.Bar(
            x=[p.symbol for p in positions],
            y=[p.unrealized_pl for p in positions],
            marker=dict(
                color=colors,
                line=dict(width=0),
                opacity=0.85,
            ),
            text=[f"${p.unrealized_pl:+,.2f}" for p in positions],
            textposition="outside",
            textfont=dict(size=11, color=COLORS["text_secondary"]),
        ))
        fig.update_layout(
            **PLOTLY_LAYOUT,
            height=280,
            yaxis_title="Unrealized P&L ($)",
            bargap=0.35,
        )
        fig.add_hline(y=0, line_color=COLORS["border"], line_width=1)
        st.plotly_chart(fig, use_container_width=True)


# ─── Signal Analysis ──────────────────────────────────────────────────────────
def render_signal_analysis():
    st.markdown('<div class="section-header"><span class="section-header-icon">🔍</span> Signal Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        symbol  = st.text_input("Ticker Symbol", placeholder="e.g., NVDA, AAPL, MSFT").upper().strip()
        analyze = st.button("🚀  Run Agent Swarm", type="primary", use_container_width=True)

    with col2:
        st.markdown(f"""
        <div class="pipeline">
            <div class="pipeline-step">
                <div class="pipeline-num">01</div>
                <div>
                    <div class="pipeline-name">News Scanner</div>
                    <div class="pipeline-desc">24h news, earnings, FDA events · You.com Search API</div>
                </div>
            </div>
            <div class="pipeline-step">
                <div class="pipeline-num">02</div>
                <div>
                    <div class="pipeline-name">Filings Analyst</div>
                    <div class="pipeline-desc">10-K/Q, 8-K, 13F, Form 4 · You.com Finance Research</div>
                </div>
            </div>
            <div class="pipeline-step">
                <div class="pipeline-num">03</div>
                <div>
                    <div class="pipeline-name">Sentiment Agent</div>
                    <div class="pipeline-desc">Options flow, dark pool, short interest, 13F</div>
                </div>
            </div>
            <div class="pipeline-step">
                <div class="pipeline-num">04</div>
                <div>
                    <div class="pipeline-name">Risk Manager</div>
                    <div class="pipeline-desc">Kelly sizing · max 5% position · hard stops</div>
                </div>
            </div>
            <div class="pipeline-step">
                <div class="pipeline-num">05</div>
                <div>
                    <div class="pipeline-name">Executor</div>
                    <div class="pipeline-desc">Alpaca paper trade · audit trail</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if analyze and symbol:
        with st.spinner(f"Running agent swarm on {symbol} — this takes ~45 seconds…"):
            signal = load_latest_signal(symbol)
            if signal:
                render_signal_card(signal)
            else:
                st.info(f"No cached signal found for **{symbol}**. Run `python main.py analyze {symbol}` in the shell to generate one, then refresh.")
    elif analyze and not symbol:
        st.warning("Please enter a ticker symbol first.")


# ─── Signal Card ──────────────────────────────────────────────────────────────
def render_signal_card(signal):
    stype      = signal.get("signal_type", "neutral").lower()
    confidence = signal.get("confidence", 0)
    symbol     = signal.get("symbol", "N/A")
    ts         = signal.get("timestamp", "")[:19].replace("T", " ")

    st.markdown(f"""
    <div class="signal-card signal-card-{stype}">
        <div class="signal-header">
            <span class="signal-symbol">{symbol}</span>
            <span class="badge badge-{stype}">{stype.upper()}</span>
            <span style="color:{COLORS['text_dim']};font-size:0.78rem;">{ts} UTC</span>
            <span class="signal-confidence">{confidence:.0%} confidence</span>
        </div>
        <div class="signal-thesis">{signal.get('thesis', 'No thesis available.')}</div>
        <div class="signal-meta">
            <div class="signal-meta-item">
                <span class="signal-meta-label">🎯 Target Price</span>
                <span class="signal-meta-value">${signal.get('target_price', 0):.2f}</span>
            </div>
            <div class="signal-meta-item">
                <span class="signal-meta-label">🛑 Stop Loss</span>
                <span class="signal-meta-value">{signal.get('stop_loss', 0):.1%}</span>
            </div>
            <div class="signal-meta-item">
                <span class="signal-meta-label">⏱ Time Horizon</span>
                <span class="signal-meta-value">{signal.get('time_horizon', 'N/A')}</span>
            </div>
            <div class="signal-meta-item">
                <span class="signal-meta-label">📚 Citations</span>
                <span class="signal-meta-value">{len(signal.get('citations', []))}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    citations = signal.get("citations", [])
    if citations:
        st.markdown(f'<div class="section-header" style="margin-top:24px;"><span class="section-header-icon">📚</span> Citation Trail</div>', unsafe_allow_html=True)
        for i, c in enumerate(citations, 1):
            snippet = c.get("snippet", "")[:280]
            if snippet:
                snippet += "…"
            st.markdown(f"""
            <div class="citation-card">
                <div class="citation-num">{i:02d}</div>
                <div style="flex:1;min-width:0;">
                    <div class="citation-title">{c.get('title', 'Untitled')}</div>
                    <div class="citation-meta">{c.get('source', 'unknown')}</div>
                    <div class="citation-snippet">{snippet}</div>
                    <a class="citation-link" href="{c.get('url', '#')}" target="_blank">View source →</a>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─── Signal History ───────────────────────────────────────────────────────────
def render_signal_history():
    st.markdown('<div class="section-header"><span class="section-header-icon">📜</span> Signal History</div>', unsafe_allow_html=True)

    signals = load_signals()
    if not signals:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-state-icon">🔮</div>
            <div class="empty-state-text">No signals generated yet.<br>Head to the Analyze tab to run your first agent swarm.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    types    = list(set(s.get("signal_type", "unknown") for s in signals))
    selected = st.multiselect("Filter by type", types, default=types, label_visibility="collapsed")
    filtered = [s for s in signals if s.get("signal_type") in selected]

    # Summary chart
    if len(filtered) > 1:
        type_counts = pd.Series([s.get("signal_type", "unknown") for s in filtered]).value_counts()
        color_map = {
            "bullish": COLORS["accent_green"],
            "bearish": COLORS["accent_red"],
            "neutral": COLORS["accent_yellow"],
            "catalyst": COLORS["accent"],
            "risk": COLORS["accent_red"],
        }
        fig = go.Figure(go.Pie(
            labels=type_counts.index,
            values=type_counts.values,
            hole=0.6,
            marker=dict(colors=[color_map.get(t, COLORS["text_dim"]) for t in type_counts.index],
                        line=dict(color=COLORS["bg_base"], width=3)),
            textfont=dict(color=COLORS["text_primary"]),
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=220, showlegend=True,
                          legend=dict(orientation="h", y=-0.1))
        fig.add_annotation(text=f"<b>{len(filtered)}</b><br><span style='font-size:10px'>signals</span>",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=16, color=COLORS["text_primary"]))
        st.plotly_chart(fig, use_container_width=True)

    # Expandable signal list
    for signal in filtered[:20]:
        stype      = signal.get("signal_type", "unknown").lower()
        confidence = signal.get("confidence", 0)
        sym        = signal.get("symbol", "N/A")
        ts         = signal.get("timestamp", "")[:19].replace("T", " ")

        with st.expander(f"**{sym}**  ·  {stype.upper()}  ·  {confidence:.0%}  ·  {ts}"):
            render_signal_card(signal)


# ─── Order History ────────────────────────────────────────────────────────────
def render_order_history(orders):
    st.markdown('<div class="section-header"><span class="section-header-icon">📋</span> Order History</div>', unsafe_allow_html=True)

    if not orders:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <div class="empty-state-text">No orders placed yet.<br>Orders will appear here once you execute a trade.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    df = pd.DataFrame(orders)
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
        cols = ["created_at", "symbol", "side", "qty", "filled_price", "status"]
        df = df[cols].rename(columns={
            "created_at":    "Time",
            "symbol":        "Symbol",
            "side":          "Side",
            "qty":           "Qty",
            "filled_price":  "Fill Price",
            "status":        "Status",
        })

        def style_side(val):
            if val == "buy":
                return f"color: {COLORS['accent_green']}; font-weight: 600"
            elif val == "sell":
                return f"color: {COLORS['accent_red']}; font-weight: 600"
            return ""

        styled = df.style.map(style_side, subset=["Side"])
        st.dataframe(styled, use_container_width=True, hide_index=True)


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    render_sidebar()
    render_header()

    account   = get_account()
    positions = get_positions()
    orders    = get_orders()

    render_metrics(account, positions)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊  Positions",
        "🔍  Analyze",
        "📜  History",
        "📋  Orders",
    ])

    with tab1:
        render_positions(positions)
    with tab2:
        render_signal_analysis()
    with tab3:
        render_signal_history()
    with tab4:
        render_order_history(orders)


if __name__ == "__main__":
    main()
