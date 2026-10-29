"""
ChronosMatch - Trading Terminal Dashboard (educational simulation)

The dashboard combines synthetic matching-engine analytics with an
optional, separate public Binance BTC/USDT market-data feed.
"""

from datetime import datetime, timezone
from html import escape

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from chronos.matching_engine import MatchingEngine
from chronos.dashboard_data import (
    get_order_book_data,
    get_trade_history_data,
    get_dashboard_summary,
)
from chronos.live_market_worker import LiveMarketWorker
from chronos.live_charts_component import render_live_charts
from scripts.generate_orders import generate_orders



# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ChronosMatch | Trading Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

LADDER_ROWS = 7    # rows shown per side in the order-book ladders
TAPE_ROWS = 7      # rows shown in the trade tape


# ============================================================
# THEMES (dark + light)
# Every colour used on the page comes from one of these two sets.
# ============================================================

DARK = dict(
    bg1="#050914", bg2="#0a1224", glow1="rgba(52,104,235,.22)", glow2="rgba(139,84,240,.16)",
    text="#eef3ff", strong="#ffffff", muted="#9fb2d3", muted2="#8fa5c8", label="#c3d1ea",
    border="rgba(110,150,230,.26)", line="rgba(110,150,230,.18)",
    nav_a="rgba(28,46,84,.78)", nav_b="rgba(11,19,38,.82)",
    card_a="rgba(27,44,80,.82)", card_b="rgba(11,19,38,.9)",
    panel_a="rgba(20,33,62,.82)", panel_b="rgba(8,14,29,.88)",
    shadow="rgba(0,0,0,.32)", rowalt="rgba(80,120,200,.08)", track="rgba(110,150,230,.16)",
    input="#101c34", inputb="#2f4568", sb_a="#0f1a33", sb_b="#070d1c",
    empty="rgba(14,24,46,.55)", thead="#0f1a33",
    buy="#2fe3b0", sell="#ff5c85", cyan="#3fe6f5", blue="#4a86ff",
    purple="#a77bff", amber="#f5b84a",
    depthbuy="rgba(47,227,176,.24)", depthsell="rgba(255,92,133,.26)",
    plot_bg="rgba(6,12,26,.55)", grid="rgba(120,160,230,.14)", tip="#0d1730",
    donutline="#0a1224", plotly="plotly_dark",
    scale=["#345bce", "#36c9ef", "#a779ff"],
)

LIGHT = dict(
    bg1="#e9f0fb", bg2="#f7faff", glow1="rgba(60,120,255,.16)", glow2="rgba(150,100,255,.12)",
    text="#13213d", strong="#0b1630", muted="#4b5f84", muted2="#5a6e92", label="#33476b",
    border="rgba(50,90,170,.24)", line="rgba(50,90,170,.16)",
    nav_a="rgba(255,255,255,.95)", nav_b="rgba(234,241,255,.95)",
    card_a="#ffffff", card_b="#eff4ff",
    panel_a="#ffffff", panel_b="#f0f5ff",
    shadow="rgba(30,60,120,.16)", rowalt="rgba(50,90,170,.06)", track="rgba(50,90,170,.14)",
    input="#ffffff", inputb="#b7c6e4", sb_a="#ffffff", sb_b="#e6edfa",
    empty="rgba(240,245,255,.85)", thead="#eef3ff",
    buy="#0e9f72", sell="#d92f5f", cyan="#0a8fb0", blue="#2f63e0",
    purple="#7b4ae0", amber="#c98a12",
    depthbuy="rgba(14,159,114,.20)", depthsell="rgba(217,47,95,.18)",
    plot_bg="rgba(244,248,255,.95)", grid="rgba(50,90,170,.14)", tip="#ffffff",
    donutline="#ffffff", plotly="plotly_white",
    scale=["#7fa2f5", "#2fa8d6", "#8a5be0"],
)

# The toggle lives in the sidebar, but its value is already in session state
# at the start of each run, so the theme can be chosen before drawing anything.
LIGHT_MODE = bool(st.session_state.get("light_mode", False))
T = LIGHT if LIGHT_MODE else DARK


# ============================================================
# DESIGN SYSTEM (CSS)
# ============================================================

STATIC_CSS = """
html, body, [class*="css"], .stApp {
    font-family: 'Sora', Inter, ui-sans-serif, system-ui, "Segoe UI", sans-serif;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(ellipse 60% 40% at 10% 0%, var(--glow1), transparent 60%),
        radial-gradient(ellipse 50% 40% at 92% 8%, var(--glow2), transparent 60%),
        linear-gradient(160deg, var(--bg1) 0%, var(--bg2) 100%);
}

/* ---------- Streamlit chrome ---------- */
[data-testid="stHeader"] { background: transparent; }
footer { visibility: hidden; }

/* Hide the Deploy button */
[data-testid="stAppDeployButton"],
.stAppDeployButton,
.stDeployButton { display: none !important; }

/* Keep the remaining toolbar icons readable in both themes */
[data-testid="stToolbar"] button,
[data-testid="stToolbar"] svg,
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"] { color: var(--text) !important; }

.block-container { max-width: 1800px; padding: 1rem 1.6rem 2.5rem; }

/* ---------- Navbar ---------- */
.top-nav {
    display: flex; align-items: center; justify-content: space-between;
    gap: 1.2rem; padding: .95rem 1.25rem; margin-bottom: 1.1rem;
    border: 1px solid var(--border); border-radius: 20px;
    background: linear-gradient(115deg, var(--nav-a), var(--nav-b));
    backdrop-filter: blur(14px);
    box-shadow: 0 18px 50px var(--shadow), inset 0 1px rgba(255,255,255,.08);
}
.brand-wrap { display: flex; align-items: center; gap: .9rem; min-width: 0; }
.brand-icon {
    display: grid; place-items: center; width: 50px; height: 50px; flex: 0 0 50px;
    border-radius: 15px; color: #06101f; font-size: 1.6rem; font-weight: 800;
    background: linear-gradient(135deg, #3fe6f5, #5f8bff 60%, #a77bff);
    box-shadow: 0 0 26px rgba(63,230,245,.28);
}
.brand-name {
    font-size: clamp(1.4rem, 2.3vw, 2rem); font-weight: 800;
    letter-spacing: -.6px; line-height: 1.1; color: var(--strong);
}
.brand-name span {
    background: linear-gradient(90deg, var(--cyan), var(--blue), var(--purple));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.brand-subtitle { margin-top: .3rem; color: var(--muted); font-size: .84rem; }

.nav-right { display: flex; flex-direction: column; align-items: flex-end; gap: .4rem; }
.status-pill {
    display: inline-flex; align-items: center; gap: .55rem; padding: .5rem .9rem;
    border: 1px solid color-mix(in srgb, var(--buy) 45%, transparent);
    border-radius: 999px;
    background: color-mix(in srgb, var(--buy) 14%, transparent);
    color: var(--buy); font-size: .78rem; font-weight: 700; letter-spacing: .6px;
    white-space: nowrap;
}
.status-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--buy); animation: pulse 2s infinite; }
@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 color-mix(in srgb, var(--buy) 60%, transparent); }
    70%  { box-shadow: 0 0 0 9px transparent; }
    100% { box-shadow: 0 0 0 0 transparent; }
}
.nav-note { color: var(--muted2); font-size: .76rem; }

/* ---------- KPI cards ---------- */
.kpi-grid {
    display: grid; grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: .9rem; margin-bottom: 1.1rem;
}
@media (max-width: 1350px) { .kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 700px)  { .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.kpi {
    position: relative; padding: 1rem 1.1rem 1.05rem;
    border: 1px solid var(--border); border-radius: 18px;
    background: linear-gradient(150deg, var(--card-a), var(--card-b));
    backdrop-filter: blur(10px);
    box-shadow: 0 12px 30px var(--shadow), inset 0 1px rgba(255,255,255,.06);
    overflow: hidden;
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
.kpi::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    background: var(--accent); box-shadow: 0 0 14px var(--accent);
}
.kpi:hover {
    transform: translateY(-3px); border-color: var(--accent);
    box-shadow: 0 14px 34px var(--shadow), 0 0 26px color-mix(in srgb, var(--accent) 24%, transparent);
}
.kpi-label { color: var(--label); font-size: .84rem; font-weight: 600; }
.kpi-value {
    margin: .35rem 0 .3rem; font-size: clamp(1.7rem, 2.1vw, 2.2rem);
    font-weight: 800; letter-spacing: -.8px; color: var(--strong);
    font-variant-numeric: tabular-nums;
}
.kpi-note { color: var(--muted2); font-size: .76rem; }

/* ---------- Panels (st.container with key="panel_...") ---------- */
[class*="st-key-panel"] {
    padding: 1.05rem 1.15rem 1.1rem;
    border: 1px solid var(--border); border-radius: 20px;
    background: linear-gradient(160deg, var(--panel-a), var(--panel-b));
    backdrop-filter: blur(12px);
    box-shadow: 0 16px 40px var(--shadow), inset 0 1px rgba(255,255,255,.06);
}
.panel-head { display: flex; align-items: baseline; justify-content: space-between; gap: .6rem; margin-bottom: .15rem; }
.panel-title { font-size: 1.05rem; font-weight: 700; color: var(--strong); letter-spacing: -.2px; }
.panel-title i {
    display: inline-block; width: 4px; height: 16px; margin-right: .55rem;
    vertical-align: -2px; border-radius: 4px;
    background: linear-gradient(180deg, var(--cyan), var(--blue), var(--purple));
}
.panel-title { white-space: nowrap; }
.panel-tag { color: var(--muted2); font-size: .74rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.panel-caption { color: var(--muted); font-size: .8rem; margin: .1rem 0 .6rem; }

/* Fixed panel heights so every box in a row lines up */
[class*="st-key-panel"] { box-sizing: border-box; overflow-x: hidden; overflow-y: auto; }
.st-key-panel_price, .st-key-panel_book { height: 720px; }
.st-key-panel_summary { height: 350px; }
.st-key-panel_flow { height: 354px; }
.st-key-panel_trades, .st-key-panel_history { height: 430px; }
@media (max-width: 900px) { [class*="st-key-panel"] { height: auto !important; } }

/* ---------- Order book ladders ---------- */
.ladder-title { font-size: .85rem; font-weight: 700; margin: .2rem 0 .4rem; }
.ladder-title.buy { color: var(--buy); }
.ladder-title.sell { color: var(--sell); }
.lhead, .lrow {
    display: grid; grid-template-columns: 1fr 1.2fr 1fr .9fr; gap: .4rem;
    padding: .34rem .6rem; font-size: .8rem; font-variant-numeric: tabular-nums;
}
.lhead { color: var(--muted2); font-size: .72rem; border-bottom: 1px solid var(--line); }
.lrow {
position: relative;
isolation: isolate;
display: grid;
grid-template-columns: 1fr 1.2fr 1fr .9fr;
gap: .4rem;
padding: .42rem .6rem;
margin-top: 3px;
border-radius: 6px;
color: var(--text);
font-size: .8rem;
font-variant-numeric: tabular-nums;
overflow: hidden;
background: var(--rowalt);
}

.lrow::before {
content: "";
position: absolute;
inset: 0 auto 0 0;
width: var(--w);
background: var(--bar);
opacity: .22;
pointer-events: none;
z-index: -1;
}

.lrow.buy {
--bar: var(--depthbuy);
}

.lrow.sell {
--bar: var(--depthsell);
}

.lrow .px.buy {
color: var(--buy);
font-weight: 700;
}

.lrow .px.sell {
color: var(--sell);
font-weight: 700;
}

.lrow .ty {
color: var(--muted);
}

.lrow:hover {
outline: 1px solid var(--border);
}

.lrow.buy  { --bar: var(--depthbuy); }
.lrow.sell { --bar: var(--depthsell); }
.lrow .px.buy  { color: var(--buy);  font-weight: 700; }
.lrow .px.sell { color: var(--sell); font-weight: 700; }
.lrow .ty { color: var(--muted); }
.lrow:hover { outline: 1px solid var(--border); }
.ladder-empty {
    padding: 1.4rem .8rem; text-align: center; color: var(--muted); font-size: .84rem;
    border: 1px dashed var(--border); border-radius: 12px;
}

.midrow {
    display: flex; justify-content: space-between; align-items: baseline; gap: .5rem;
    padding: .55rem .7rem; margin: .4rem 0; border-radius: 10px;
    border-top: 1px solid var(--line); border-bottom: 1px solid var(--line);
    background: var(--rowalt);
}
.midrow b { font-size: 1.2rem; color: var(--strong); font-variant-numeric: tabular-nums; }
.midrow span { color: var(--muted2); font-size: .74rem; }

/* ---------- Trade tape ---------- */
.thead, .trow {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: .4rem;
    padding: .38rem .7rem; font-size: .82rem; font-variant-numeric: tabular-nums;
}
.thead { color: var(--muted2); font-size: .72rem; border-bottom: 1px solid var(--line); }
.trow { margin-top: 2px; border-radius: 6px; color: var(--text); }
.trow:nth-child(odd) { background: var(--rowalt); }
.trow .tp { color: var(--cyan); font-weight: 700; }
.trow .tq { color: var(--purple); font-weight: 700; }

/* ---------- Full data tables (theme-aware replacement for st.dataframe) ---------- */
.dtable-wrap {
    max-height: 320px; overflow: auto;
    border: 1px solid var(--border); border-radius: 12px;
}
.dtable { width: 100%; border-collapse: collapse; font-size: .82rem; font-variant-numeric: tabular-nums; }
.dtable th {
    position: sticky; top: 0; text-align: left; padding: .5rem .7rem;
    background: var(--thead); color: var(--muted2); font-weight: 600; font-size: .74rem;
    border-bottom: 1px solid var(--line);
}
.dtable td { padding: .4rem .7rem; color: var(--text); }
.dtable tr:nth-child(even) td { background: var(--rowalt); }
.dtable td.buy  { color: var(--buy);  font-weight: 700; }
.dtable td.sell { color: var(--sell); font-weight: 700; }

/* ---------- Market summary ---------- */
.stat-row { display: flex; justify-content: space-between; padding: .5rem 0;
            border-bottom: 1px solid var(--line); font-size: .88rem; }
.stat-row span:first-child { color: var(--muted); }
.stat-row span:last-child { color: var(--strong); font-weight: 700; font-variant-numeric: tabular-nums; }
.bar-label { display: flex; justify-content: space-between; margin: .75rem 0 .3rem; color: var(--label); font-size: .8rem; }
.bar { height: 8px; border-radius: 99px; background: var(--track); overflow: hidden; }
.bar i { display: block; height: 100%; border-radius: 99px; }
.bar.buy i  { background: var(--buy);  box-shadow: 0 0 12px color-mix(in srgb, var(--buy) 50%, transparent); }
.bar.sell i { background: var(--sell); box-shadow: 0 0 12px color-mix(in srgb, var(--sell) 45%, transparent); }

.empty-panel {
    padding: 2.2rem 1rem; text-align: center; color: var(--muted); font-size: .9rem;
    border: 1px dashed var(--border); border-radius: 14px; background: var(--empty);
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--sb-a) 0%, var(--sb-b) 100%);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] h3 { color: var(--strong) !important; font-weight: 700 !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: var(--text); }
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: var(--muted) !important; }
section[data-testid="stSidebar"] hr { border-color: var(--line) !important; }

.side-brand {
    display: flex; align-items: center; gap: .7rem; padding: .85rem .9rem; margin-bottom: 1rem;
    border: 1px solid var(--border); border-radius: 16px;
    background: linear-gradient(135deg, var(--card-a), var(--card-b));
}
.side-logo {
    display: grid; place-items: center; width: 38px; height: 38px; border-radius: 11px;
    color: #06101f; font-weight: 800;
    background: linear-gradient(135deg, #3fe6f5, #5f8bff 60%, #a77bff);
}
.side-brand-title { color: var(--strong); font-size: 1.05rem; font-weight: 800; }
.side-brand-sub { color: var(--muted); font-size: .72rem; margin-top: .15rem; }
.side-note { color: var(--muted); font-size: .78rem; line-height: 1.5; margin: .2rem 0 .8rem; }

.stButton, div[data-testid="stButton"] { width: 100% !important; }
.stButton > button {
    width: 100% !important; min-height: 46px;
    border: 1px solid rgba(110,160,255,.5); border-radius: 12px; font-weight: 700;
    background: linear-gradient(105deg, #2859d9, #426ff0 60%, #6a58ea);
    transition: transform .18s ease, filter .18s ease, box-shadow .18s ease;
}
.stButton > button, .stButton > button p, .stButton > button span { color: #ffffff !important; }
.stButton > button:hover {
    transform: translateY(-2px); filter: brightness(1.1); border-color: #86e2f6;
    box-shadow: 0 8px 24px rgba(66,111,240,.35);
}
.stButton > button:active { transform: translateY(0); }
.stButton > button:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }

div[data-baseweb="input"] > div { background: var(--input); border-color: var(--inputb); border-radius: 10px; }
div[data-baseweb="input"] input { color: var(--text) !important; -webkit-text-fill-color: var(--text); }
div[data-baseweb="input"] button { background: transparent; color: var(--text); }

div[data-testid="stExpander"] { border: 1px solid var(--border); border-radius: 12px; background: var(--empty); }
div[data-testid="stExpander"] summary, div[data-testid="stExpander"] summary p,
div[data-testid="stExpander"] summary span { color: var(--text) !important; }
div[data-testid="stExpander"] svg { color: var(--text); }

/* Tabs */
button[data-baseweb="tab"] p { color: var(--muted) !important; font-weight: 600; }
button[data-baseweb="tab"][aria-selected="true"] p { color: var(--strong) !important; }
div[data-baseweb="tab-border"] { background-color: var(--line) !important; }

/* Number input in both themes */
[data-testid="stNumberInputContainer"], div[data-baseweb="base-input"],
div[data-baseweb="base-input"] input { background: var(--input) !important; color: var(--text) !important; }
[data-testid="stTooltipIcon"] svg { color: var(--muted) !important; }

.footer {
    margin-top: 1.4rem; padding: 1rem .5rem .2rem; text-align: center;
    color: var(--muted2); font-size: .8rem; line-height: 1.7; border-top: 1px solid var(--line);
}
.footer strong { color: var(--strong); }

/* ---------- Responsive ---------- */
@media (max-width: 900px) {
    .block-container { padding: .8rem .7rem 2rem; }
    .top-nav { flex-direction: column; align-items: flex-start; }
    .nav-right { align-items: flex-start; }
    .lhead, .lrow, .thead, .trow { font-size: .74rem; padding-left: .4rem; padding-right: .4rem; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
}
"""

# Turn the theme dictionary into CSS variables: {"nav_a": "x"} -> --nav-a: x;
theme_variables = ":root{" + ";".join(
    f"--{key.replace('_', '-')}:{value}"
    for key, value in T.items()
    if isinstance(value, str)
) + "}"

st.markdown(
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&display=swap');"
    + theme_variables
    + STATIC_CSS
    + "</style>",
    unsafe_allow_html=True,
)


# ============================================================
# SMALL HELPERS
# ============================================================


def show_chart(fig, chart_key):
    """Render a Plotly chart using a stable, unique Streamlit key."""
    fig.update_layout(uirevision=chart_key)

    try:
        st.plotly_chart(
            fig,
            width="stretch",
            theme=None,
            key=chart_key,
        )
    except TypeError:
        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None,
            key=chart_key,
        )




def rgba(hex_colour, alpha):
    """'#2fe3b0' -> 'rgba(47,227,176,0.25)' (for translucent chart fills)."""
    h = hex_colour.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def panel_header(title, tag=""):
    st.markdown(
        f'<div class="panel-head"><div class="panel-title"><i></i>{title}</div>'
        f'<div class="panel-tag">{tag}</div></div>',
        unsafe_allow_html=True,
    )


def empty_state(message):
    st.markdown(f'<div class="empty-panel">{message}</div>', unsafe_allow_html=True)


def style_figure(fig, height=380):
    fig.update_layout(
        height=height,
        template=T["plotly"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=T["plot_bg"],
        font=dict(family="Sora, Arial, sans-serif", size=12, color=T["text"]),
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        hoverlabel=dict(bgcolor=T["tip"], bordercolor=T["blue"], font_color=T["text"]),
    )
    fig.update_xaxes(gridcolor=T["grid"], zerolinecolor=T["grid"], showline=False)
    fig.update_yaxes(gridcolor=T["grid"], zerolinecolor=T["grid"], showline=False)
    return fig


def kpi_card(label, value, note, accent_var):
    return (
        f'<div class="kpi" style="--accent:var(--{accent_var})">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-note">{note}</div></div>'
    )


def ladder_html(df, side, reverse=False, header=True):
    """Order-book ladder with depth bars, built from real order-book rows."""
    css = "buy" if side == "BUY" else "sell"
    if df.empty:
        return f'<div class="ladder-empty">No active {side.lower()} orders</div>'

    top = df.head(LADDER_ROWS)
    max_qty = max(float(top["Remaining Quantity"].max()), 1.0)
    rows = []
    if header:
        rows.append(
            '<div class="lhead"><span>Order ID</span><span>Price</span>'
            '<span>Quantity</span><span>Type</span></div>'
        )
    records = list(zip(top["Order ID"], top["Price"], top["Remaining Quantity"], top["Order Type"]))
    if reverse:
        records.reverse()
    for oid, price, qty, otype in records:
        width = float(qty) / max_qty * 100
        rows.append(
            f'<div class="lrow {css}" style="--w:{width:.0f}%">'
            f'<span>{escape(str(oid))}</span>'
            f'<span class="px {css}">{float(price):,.2f}</span>'
            f'<span>{int(qty):,}</span>'
            f'<span class="ty">{escape(str(otype))}</span></div>'
        )
    return "".join(rows)


def empty_chart(height, message, x_title, y_title):
    """A real chart frame (axes + grid) shown before any data exists."""
    fig = go.Figure()
    fig.add_annotation(text=message, x=5, y=5, showarrow=False,
                       font=dict(size=14, color=T["muted"]))
    style_figure(fig, height)
    fig.update_xaxes(title_text=x_title, range=[0, 10], showticklabels=False)
    fig.update_yaxes(title_text=y_title, range=[0, 10], showticklabels=False)
    return fig


def tape_html(df):
    """Trade tape (newest first), built from real recorded executions."""
    rows = [
        '<div class="thead"><span>Buy order ID</span><span>Sell order ID</span>'
        '<span>Price</span><span>Quantity</span></div>'
    ]
    recent = df.iloc[::-1].head(TAPE_ROWS)
    for b, s, price, qty in zip(
        recent["Buy Order ID"], recent["Sell Order ID"], recent["Price"], recent["Quantity"]
    ):
        rows.append(
            f'<div class="trow"><span>{escape(str(b))}</span><span>{escape(str(s))}</span>'
            f'<span class="tp">{float(price):,.2f}</span>'
            f'<span class="tq">{int(qty):,}</span></div>'
        )
    return "".join(rows)


def format_cell(column, value):
    """Format one table cell by column name (IDs plain, prices 2 decimals)."""
    if "ID" in column:
        return str(value)
    if "Price" in column:
        return f"{float(value):,.2f}"
    if "Quantity" in column:
        return f"{int(value):,}"
    return str(value)


def html_table(df):
    """Scrollable, theme-aware table (shows every column of the DataFrame)."""
    columns = list(df.columns)
    head = "".join(f"<th>{escape(str(c))}</th>" for c in columns)
    body = []
    for row in df.itertuples(index=False, name=None):
        cells = []
        for column, value in zip(columns, row):
            css = ""
            if column == "Side" and str(value) in ("BUY", "SELL"):
                css = ' class="buy"' if str(value) == "BUY" else ' class="sell"'
            cells.append(f"<td{css}>{escape(format_cell(str(column), value))}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    st.markdown(
        f'<div class="dtable-wrap"><table class="dtable"><thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# SESSION STATE
# ============================================================

if "engine" not in st.session_state:
    st.session_state.engine = MatchingEngine()

if "next_order_id" not in st.session_state:
    st.session_state.next_order_id = 1

if "last_generated_count" not in st.session_state:
    st.session_state.last_generated_count = 0

if "live_market_worker" not in st.session_state:
    st.session_state.live_market_worker = LiveMarketWorker()
# ============================================================
# SIDEBAR CONTROL CENTER
# ============================================================

st.sidebar.markdown(
    """
    <div class="side-brand">
        <div class="side-logo">C</div>
        <div>
            <div class="side-brand-title">ChronosMatch</div>
            <div class="side-brand-sub">Order-matching simulation</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("### Appearance")
st.sidebar.toggle("Light mode", key="light_mode", help="Switch between dark and light themes.")
st.sidebar.divider()

st.sidebar.markdown("### Control center")
st.sidebar.markdown(
    '<div class="side-note">Generate a repeatable batch of synthetic orders and '
    'send them through the matching engine.</div>',
    unsafe_allow_html=True,
)

order_count = st.sidebar.slider(
    "Orders to generate",
    min_value=1,
    max_value=1000,
    value=100,
    help="Number of synthetic orders to process.",
)

seed = st.sidebar.number_input(
    "Random seed",
    min_value=0,
    max_value=100000,
    value=42,
    step=1,
    help="Use the same seed to reproduce the generated order sequence.",
)

if st.sidebar.button("▶  Generate & Process Orders", type="primary"):
    engine = st.session_state.engine
    new_orders = generate_orders(count=order_count, seed=int(seed))

    next_id = st.session_state.next_order_id
    for order in new_orders:
        order.order_id = next_id
        next_id += 1
        engine.add_order(order)

    st.session_state.next_order_id = next_id
    st.session_state.last_generated_count = len(new_orders)
    st.rerun()

if st.sidebar.button("↻  Reset Simulation"):
    st.session_state.engine = MatchingEngine()
    st.session_state.next_order_id = 1
    st.session_state.last_generated_count = 0
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("### System information")
st.sidebar.caption("Engine: Python matching engine")
st.sidebar.caption("Interface: Streamlit")
st.sidebar.caption("Charts: Plotly")
st.sidebar.caption("Simulation: synthetic orders")
st.sidebar.caption("Market data: optional Binance BTC/USDT feed")
st.sidebar.caption("Educational use only. No real orders are placed.")


# ============================================================
# FETCH CURRENT ENGINE DATA
# ============================================================

engine = st.session_state.engine
summary = get_dashboard_summary(engine)
order_book_data = get_order_book_data(engine)
trade_history_data = get_trade_history_data(engine)

total_traded_quantity = 0
average_trade_price = None

if not trade_history_data.empty:
    total_traded_quantity = int(trade_history_data["Quantity"].sum())
    average_trade_price = float(trade_history_data["Price"].mean())

# Sorted views of the real order book
if order_book_data.empty:
    buy_orders = order_book_data
    sell_orders = order_book_data
else:
    buy_orders = order_book_data[order_book_data["Side"] == "BUY"].sort_values("Price", ascending=False)
    sell_orders = order_book_data[order_book_data["Side"] == "SELL"].sort_values("Price", ascending=True)

best_bid = float(buy_orders["Price"].max()) if not buy_orders.empty else None
best_ask = float(sell_orders["Price"].min()) if not sell_orders.empty else None
buy_volume = int(buy_orders["Remaining Quantity"].sum()) if not buy_orders.empty else 0
sell_volume = int(sell_orders["Remaining Quantity"].sum()) if not sell_orders.empty else 0
total_volume = buy_volume + sell_volume


# ============================================================
# TOP NAVBAR
# ============================================================

st.markdown(
    f"""
    <div class="top-nav">
        <div class="brand-wrap">
            <div class="brand-icon">C</div>
            <div>
                <div class="brand-name">Chronos<span>Match</span></div>
                <div class="brand-subtitle">Order-matching engine simulation &nbsp;·&nbsp; Trading terminal</div>
            </div>
        </div>
        <div class="nav-right">
            <div class="status-pill"><span class="status-dot"></span>SIMULATION MODE</div>
            <div class="nav-note">Synthetic matching engine &nbsp;·&nbsp; Optional Binance BTC/USDT feed &nbsp;·&nbsp; Last run: {st.session_state.last_generated_count:,} orders</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KPI CARDS
# ============================================================

active = summary["Active Orders"]
buy_share = (summary["Active Buy Orders"] / active * 100) if active else 0
sell_share = (summary["Active Sell Orders"] / active * 100) if active else 0

kpis = [
    kpi_card("Active Orders", f"{active:,}", "Resting in the order book", "blue"),
    kpi_card("Buy Orders", f'{summary["Active Buy Orders"]:,}', f"{buy_share:.0f}% of active orders", "buy"),
    kpi_card("Sell Orders", f'{summary["Active Sell Orders"]:,}', f"{sell_share:.0f}% of active orders", "sell"),
    kpi_card("Executed Trades", f'{summary["Executed Trades"]:,}', "Recorded by the matching engine", "cyan"),
    kpi_card("Total Traded Quantity", f"{total_traded_quantity:,}", "Units matched across all trades", "purple"),
    kpi_card(
        "Average Trade Price",
        f"{average_trade_price:,.2f}" if average_trade_price is not None else "–",
        "Mean execution price" if average_trade_price is not None else "No trades yet",
        "amber",
    ),
]
st.markdown(f'<div class="kpi-grid">{"".join(kpis)}</div>', unsafe_allow_html=True)


# ============================================================
# TERMINAL LAYOUT
# Row 1: summary rail | main price chart | order book  (all 720 px tall)
# Row 2: trade quantity chart | trade history          (both 430 px tall)
# Panel heights are fixed in the CSS so every box in a row lines up.
# ============================================================

spread = (best_ask - best_bid) if (best_bid is not None and best_ask is not None) else None
mid = ((best_ask + best_bid) / 2) if spread is not None else None
dash = "–"

rail_left, centre, rail_right = st.columns([0.95, 2.5, 1.35])

# ---------------- LEFT RAIL: book summary + order flow ----------------
with rail_left:
    with st.container(key="panel_summary"):
        panel_header("Book summary")
        st.markdown(
            f"""
            <div class="stat-row"><span>Best bid</span><span style="color:var(--buy)">{f"{best_bid:,.2f}" if best_bid is not None else dash}</span></div>
            <div class="stat-row"><span>Best ask</span><span style="color:var(--sell)">{f"{best_ask:,.2f}" if best_ask is not None else dash}</span></div>
            <div class="stat-row"><span>Spread</span><span>{f"{spread:,.2f}" if spread is not None else dash}</span></div>
            <div class="stat-row"><span>Mid price</span><span>{f"{mid:,.2f}" if mid is not None else dash}</span></div>
            """,
            unsafe_allow_html=True,
        )
        if total_volume > 0:
            buy_pct = buy_volume / total_volume * 100
            sell_pct = 100 - buy_pct
            st.markdown(
                f"""
                <div class="bar-label"><span>Buy volume</span><span>{buy_volume:,} · {buy_pct:.0f}%</span></div>
                <div class="bar buy"><i style="width:{buy_pct:.0f}%"></i></div>
                <div class="bar-label"><span>Sell volume</span><span>{sell_volume:,} · {sell_pct:.0f}%</span></div>
                <div class="bar sell"><i style="width:{sell_pct:.0f}%"></i></div>
                """,
                unsafe_allow_html=True,
            )

    with st.container(key="panel_flow"):
        panel_header("Order flow")
        if total_volume == 0:
            empty_state("Nothing resting in the book.")
        else:
            donut = go.Figure(
                go.Pie(
                    labels=["Buy", "Sell"],
                    values=[buy_volume, sell_volume],
                    hole=0.72,
                    marker=dict(colors=[T["buy"], T["sell"]], line=dict(color=T["donutline"], width=3)),
                    textinfo="percent",
                    hovertemplate="%{label}: %{value:,} units (%{percent})<extra></extra>",
                    sort=False,
                    insidetextorientation="horizontal",
                )
            )
            style_figure(donut, 250)
            donut.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
                annotations=[dict(text=f"<b>{total_volume:,}</b><br>units", x=0.5, y=0.5,
                                  showarrow=False, font=dict(size=16, color=T["text"]))],
            )
            show_chart(donut, "dashboard_donut")

# ---------------- CENTRE: main analytics (tabs) ----------------
with centre:
    with st.container(key="panel_price"):
        panel_header("Market analytics", "Built from real engine data")
        tab_price, tab_depth, tab_orders = st.tabs(["Execution price", "Market depth", "Order scatter"])

        # ----- Tab 1: execution price wave (one point per recorded trade) -----
        with tab_price:
            st.markdown(
                '<div class="panel-caption">Price of each recorded trade in execution order (trade number, not clock time). '
                'Dashed line: average of the last 5 trades.</div>',
                unsafe_allow_html=True,
            )
            if trade_history_data.empty:
                show_chart(empty_chart(500, "No trades yet: generate orders so buy and sell prices can cross", "Trade #", "Price"), "empty_trade_price")
            else:
                td = trade_history_data.reset_index(drop=True).copy()
                td["Trade #"] = td.index + 1
                td["Average"] = td["Price"].rolling(5, min_periods=1).mean()
                low, high = float(td["Price"].min()), float(td["Price"].max())
                pad = max((high - low) * 0.15, 1.0)
                base = low - pad

                wave = go.Figure()
                wave.add_trace(go.Scatter(
                    x=td["Trade #"], y=[base] * len(td), mode="lines",
                    line=dict(width=0), hoverinfo="skip", showlegend=False,
                ))
                wave.add_trace(go.Scatter(
                    x=td["Trade #"], y=td["Price"], mode="lines+markers", name="Execution price",
                    line=dict(color=T["cyan"], width=3, shape="spline", smoothing=0.7),
                    marker=dict(size=6, color=T["cyan"]),
                    fill="tonexty", fillcolor=rgba(T["cyan"], 0.18),
                    customdata=td[["Quantity", "Buy Order ID", "Sell Order ID"]].to_numpy(),
                    hovertemplate=("Trade %{x}<br>Price %{y:,.2f}<br>Quantity %{customdata[0]:,}"
                                   "<br>Buy order %{customdata[1]} · Sell order %{customdata[2]}<extra></extra>"),
                ))
                wave.add_trace(go.Scatter(
                    x=td["Trade #"], y=td["Average"], mode="lines", name="5-trade average",
                    line=dict(color=T["purple"], width=2, dash="dash"),
                    hovertemplate="Trade %{x}<br>Average %{y:,.2f}<extra></extra>",
                ))
                style_figure(wave, 500)
                wave.update_yaxes(title_text="Price", range=[base, high + pad])
                wave.update_xaxes(title_text="Trade #")
                show_chart(wave, "dashboard_wave")

        # ----- Tab 2: market depth (cumulative resting quantity by price) -----
        with tab_depth:
            st.markdown(
                '<div class="panel-caption">Total quantity waiting at or beyond each price. '
                'Buy depth builds downward from the best bid, sell depth upward from the best ask.</div>',
                unsafe_allow_html=True,
            )
            if order_book_data.empty:
                show_chart(empty_chart(500, "No active orders yet", "Price", "Cumulative quantity"), "empty_order_depth")
            else:
                depth = go.Figure()
                if not buy_orders.empty:
                    bids = buy_orders.sort_values("Price", ascending=False).copy()
                    bids["Cumulative"] = bids["Remaining Quantity"].cumsum()
                    depth.add_trace(go.Scatter(
                        x=bids["Price"], y=bids["Cumulative"], name="Buy depth", mode="lines",
                        line=dict(color=T["buy"], width=2.5, shape="hv"),
                        fill="tozeroy", fillcolor=rgba(T["buy"], 0.22),
                        hovertemplate="Price %{x:,.2f}<br>Cumulative quantity %{y:,}<extra></extra>",
                    ))
                if not sell_orders.empty:
                    asks = sell_orders.sort_values("Price", ascending=True).copy()
                    asks["Cumulative"] = asks["Remaining Quantity"].cumsum()
                    depth.add_trace(go.Scatter(
                        x=asks["Price"], y=asks["Cumulative"], name="Sell depth", mode="lines",
                        line=dict(color=T["sell"], width=2.5, shape="hv"),
                        fill="tozeroy", fillcolor=rgba(T["sell"], 0.20),
                        hovertemplate="Price %{x:,.2f}<br>Cumulative quantity %{y:,}<extra></extra>",
                    ))
                style_figure(depth, 500)
                depth.update_xaxes(title_text="Price")
                depth.update_yaxes(title_text="Cumulative quantity")
                show_chart(depth, "dashboard_depth")

        # ----- Tab 3: order scatter (every active order) -----
        with tab_orders:
            st.markdown(
                '<div class="panel-caption">Every active order by ID and price. Bubble size = remaining quantity. '
                'Dashed lines mark the best bid and best ask.</div>',
                unsafe_allow_html=True,
            )
            if order_book_data.empty:
                show_chart(empty_chart(500, "No active orders yet", "Order ID", "Price"), "empty_order_price")
            else:
                price_chart = px.scatter(
                    order_book_data,
                    x="Order ID",
                    y="Price",
                    color="Side",
                    size="Remaining Quantity",
                    size_max=20,
                    hover_data={"Order Type": True, "Remaining Quantity": True, "Price": ":.2f"},
                    color_discrete_map={"BUY": T["buy"], "SELL": T["sell"]},
                    category_orders={"Side": ["BUY", "SELL"]},
                )
                price_chart.update_traces(marker=dict(opacity=0.85, line=dict(width=0.6, color=T["donutline"])))
                if best_bid is not None:
                    price_chart.add_hline(
                        y=best_bid, line_dash="dash", line_color=T["buy"], line_width=1,
                        annotation_text=f"Best bid {best_bid:,.2f}", annotation_font_color=T["buy"],
                        annotation_position="bottom right",
                    )
                if best_ask is not None:
                    price_chart.add_hline(
                        y=best_ask, line_dash="dash", line_color=T["sell"], line_width=1,
                        annotation_text=f"Best ask {best_ask:,.2f}", annotation_font_color=T["sell"],
                        annotation_position="top right",
                    )
                style_figure(price_chart, 500)
                price_chart.update_yaxes(title_text="Price")
                show_chart(price_chart, "dashboard_price")


# ---------------- RIGHT RAIL: order book ----------------
with rail_right:
    with st.container(key="panel_book"):
        panel_header("Order book", f"Top {LADDER_ROWS} per side")
        st.markdown(
            '<div class="panel-caption">Best prices meet at the middle: lowest sells above, highest buys below.</div>',
            unsafe_allow_html=True,
        )
        if order_book_data.empty:
            empty_state("The order book is empty.<br>Generate synthetic orders from the sidebar.")
        else:
            st.markdown(f'<div class="ladder-title sell">Sell side · {len(sell_orders):,} orders</div>', unsafe_allow_html=True)
            st.markdown(ladder_html(sell_orders, "SELL", reverse=True), unsafe_allow_html=True)
            st.markdown(
                f'<div class="midrow"><span>Mid price</span><b>{f"{mid:,.2f}" if mid is not None else dash}</b>'
                f'<span>Spread {f"{spread:,.2f}" if spread is not None else dash}</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<div class="ladder-title buy">Buy side · {len(buy_orders):,} orders</div>', unsafe_allow_html=True)
            st.markdown(ladder_html(buy_orders, "BUY", header=False), unsafe_allow_html=True)

st.write("")

# ---------------- ROW 2: trade quantity chart | trade history ----------------
row2_left, row2_right = st.columns([3.45, 1.35])

with row2_left:
    with st.container(key="panel_trades"):
        panel_header("Executed trade quantity", "One bar per recorded trade")
        st.markdown(
            '<div class="panel-caption">Quantity matched in each execution. Hover for price and order IDs.</div>',
            unsafe_allow_html=True,
        )
        if trade_history_data.empty:
            show_chart(empty_chart(290, "No trades yet: a trade is recorded when buy and sell prices cross", "Trade #", "Quantity"), "empty_trade_quantity")
        else:
            trade_chart_data = trade_history_data.reset_index(drop=True).copy()
            trade_chart_data["Trade #"] = trade_chart_data.index + 1

            trade_chart = px.bar(
                trade_chart_data,
                x="Trade #",
                y="Quantity",
                color="Quantity",
                color_continuous_scale=T["scale"],
                hover_data={"Price": ":.2f", "Buy Order ID": True, "Sell Order ID": True, "Trade #": False},
            )
            style_figure(trade_chart, 290)
            trade_chart.update_layout(coloraxis_showscale=False)
            trade_chart.update_yaxes(title_text="Quantity")
            show_chart(trade_chart, "dashboard_trade_history")

with row2_right:
    with st.container(key="panel_history"):
        panel_header("Trade history", f"{len(trade_history_data):,} executions")
        if trade_history_data.empty:
            empty_state("No trades recorded yet.<br>Trades occur when buy and sell prices cross.")
        else:
            st.markdown(
                f'<div class="panel-caption">Newest first. Latest {min(TAPE_ROWS, len(trade_history_data))} shown.</div>',
                unsafe_allow_html=True,
            )
            st.markdown(tape_html(trade_history_data), unsafe_allow_html=True)


# ============================================================
# FULL DATA TABLES (every row, every column)
# ============================================================

st.write("")

with st.expander("View full order book tables"):
    if order_book_data.empty:
        st.caption("No active orders.")
    else:
        t1, t2 = st.columns(2)
        with t1:
            st.caption("Buy orders (highest price first)")
            html_table(buy_orders)
        with t2:
            st.caption("Sell orders (lowest price first)")
            html_table(sell_orders)

with st.expander("View full trade history table"):
    if trade_history_data.empty:
        st.caption("No trades recorded yet.")
    else:
        html_table(trade_history_data)


# ============================================================
# LIVE BINANCE MARKET DATA (separate from simulated executions)
# ============================================================

st.write("")
st.markdown("## Live Market Data")
st.caption(
    "Public Binance BTC/USDT trades. This feed is separate from "
    "the synthetic orders and simulated executions above."
)


@st.fragment(run_every="5s", key="live_market_panel")
def render_live_market_panel():
    worker = st.session_state.live_market_worker

    status_col, count_col = st.columns(2)

    with status_col:
        st.metric("Feed status", worker.status)

    with count_col:
        st.metric("Trades received", f"{worker.received_count:,}")

    start_col, stop_col = st.columns(2)

    with start_col:
        if st.button(
            "Start live feed",
            key="start_live_market_feed",
            disabled=worker.is_running,
            use_container_width=True,
        ):
            worker.start()

    with stop_col:
        if st.button(
            "Stop live feed",
            key="stop_live_market_feed",
            disabled=not worker.is_running,
            use_container_width=True,
        ):
            worker.stop(timeout=7.0)

    if worker.last_error:
        st.warning(f"Market-data error: {worker.last_error}")

    trades = worker.get_trades(limit=50)

    if not trades:
        st.info(
            "No live trades received yet. Start the feed to connect "
            "to Binance and receive public BTC/USDT trade data."
        )
        return

    latest_trade = trades[-1]

    price_col, quantity_col, side_col = st.columns(3)

    with price_col:
        st.metric(
            "Latest BTC/USDT price",
            f"${latest_trade['price']:,.2f}",
        )

    with quantity_col:
        st.metric(
            "Latest trade quantity",
            f"{latest_trade['quantity']:.6f} BTC",
        )

    with side_col:
        st.metric(
            "Aggressor side",
            latest_trade["aggressor_side"],
        )



    # Live BTC/USDT price chart
    chart_trades = worker.get_trades(limit=500)
    chart_df = pd.DataFrame(chart_trades)
    # Live market activity statistics
    total_live_trades = len(chart_df)

    buy_volume = chart_df.loc[
        chart_df["aggressor_side"] == "BUY",
        "quantity",
    ].sum()

    sell_volume = chart_df.loc[
        chart_df["aggressor_side"] == "SELL",
        "quantity",
    ].sum()

    volume_difference = buy_volume - sell_volume

    st.markdown("### Live Market Statistics")

    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

    with stats_col1:
        st.metric(
            "Recent Trades",
            f"{total_live_trades:,}",
        )

    with stats_col2:
        st.metric(
            "Aggressive Buy Volume",
            f"{buy_volume:.6f} BTC",
        )

    with stats_col3:
        st.metric(
            "Aggressive Sell Volume",
            f"{sell_volume:.6f} BTC",
        )

    with stats_col4:
        st.metric(
            "Buy − Sell Volume",
            f"{volume_difference:+.6f} BTC",
        )


    chart_df["Time"] = pd.to_datetime(
        chart_df["timestamp"],
        unit="ms",
        utc=True,
    )

    st.markdown("### Live Market Charts")
    render_live_charts(
        times=chart_df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist(),
        prices=chart_df["price"].astype(float).tolist(),
        quantities=chart_df["quantity"].astype(float).tolist(),
        buy_volume=buy_volume,
        sell_volume=sell_volume,
    )

    st.caption(
        "Charts show recent public Binance BTC/USDT trades. "
        "They are separate from simulated executions."
    )

    live_df = pd.DataFrame(trades)

    live_df["Time (UTC)"] = pd.to_datetime(
        live_df["timestamp"],
        unit="ms",
        utc=True,
    ).dt.strftime("%Y-%m-%d %H:%M:%S")

    live_df = live_df[
        [
            "Time (UTC)",
            "symbol",
            "price",
            "quantity",
            "aggressor_side",
        ]
    ].rename(
        columns={
            "symbol": "Symbol",
            "price": "Price (USDT)",
            "quantity": "Quantity (BTC)",
            "aggressor_side": "Aggressor",
        }
    )

    st.dataframe(
        live_df.iloc[::-1].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Showing up to 50 recent trades, newest first. "
        "Prices are public market data, not simulated execution prices."
    )


render_live_market_panel()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        <strong>ChronosMatch</strong> · Zero-Copy High-Frequency Trading Engine (educational project)<br>
        The matching engine processes synthetic orders and simulated executions.
        An optional public Binance BTC/USDT feed provides live market data separately.
        No real orders are placed, and live market data does not represent simulated executions.
    </div>
    """,
    unsafe_allow_html=True,
)