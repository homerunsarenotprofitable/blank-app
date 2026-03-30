# -*- coding: utf-8 -*-
"""
HR Props EV Scanner v2 -- California DFS Edition
Bloomberg Terminal aesthetic * Advanced analytics * Bankroll tracking
Run:
pip install streamlit requests pandas numpy plotly
streamlit run hr_ev_app_v2.py
Env var: ODDS_API_KEY (or paste in sidebar)
"""
import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os, json, io, time
from datetime import datetime, timezone
from collections import defaultdict
# -----------------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
page_title="HR EV * CA DFS",
page_icon="O",
layout="wide",
initial_sidebar_state="expanded",
)
# -----------------------------------------------------------------------------
# STYLES -- Bloomberg Terminal / Trading Desk Aesthetic
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&fami
:root {
--bg: #080b0f;
--bg1: #0d1117;
--bg2: #111820;
--bg3: #161f2c;
--border: #1e2d3d;
--border2: #243040;
--amber: #f5a623;
--amber2: #d4891e;
--green: #00e676;
--green2: #00c853;
--red: #ff5252;
--red2: #d32f2f;
--blue: #29b6f6;
--muted: #4a6275;
--text: #c8d8e8;
--text2: #8aa0b4;
--text3: #4a6275;
}
html, body, [class*="css"] {
font-family: 'IBM Plex Mono', monospace;
background: var(--bg);
color: var(--text);
}
.stApp { background: var(--bg); }
.stApp > header { background: transparent; }
/* Sidebar */
[data-testid="stSidebar"] {
background: var(--bg1);
border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { font-family: 'IBM Plex Mono', monospace; }
/* Tabs */
.stTabs [data-baseweb="tab-list"] {
background: var(--bg1);
border-bottom: 1px solid var(--border);
gap: 0;
}
.stTabs [data-baseweb="tab"] {
background: transparent;
color: var(--muted);
font-family: 'IBM Plex Mono', monospace;
font-size: 12px;
letter-spacing: 0.1em;
padding: 10px 22px;
border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
background: transparent !important;
color: var(--amber) !important;
border-bottom: 2px solid var(--amber) !important;
}
/* Inputs */
.stTextInput input, .stSelectbox select, .stMultiSelect div {
background: var(--bg2) !important;
border: 1px solid var(--border) !important;
color: var(--text) !important;
font-family: 'IBM Plex Mono', monospace !important;
font-size: 13px !important;
}
.stSlider > div > div { background: var(--border2) !important; }
/* Buttons */
.stButton > button {
background: var(--bg2);
border: 1px solid var(--border2);
color: var(--amber);
font-family: 'IBM Plex Mono', monospace;
font-size: 12px;
letter-spacing: 0.06em;
transition: all 0.15s;
}
.stButton > button:hover {
background: var(--bg3);
border-color: var(--amber);
color: var(--amber);
}
/* DataFrames */
.stDataFrame { font-family: 'IBM Plex Mono', monospace; font-size: 12px; }
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 4px; }
/* Expander */
.streamlit-expanderHeader {
background: var(--bg2) !important;
color: var(--text2) !important;
font-family: 'IBM Plex Mono', monospace !important;
font-size: 12px !important;
border: 1px solid var(--border) !important;
}
/* Metrics */
[data-testid="metric-container"] {
background: var(--bg2);
border: 1px solid var(--border);
border-radius: 4px;
padding: 12px 16px;
}
[data-testid="stMetricValue"] {
font-family: 'IBM Plex Mono', monospace !important;
color: var(--amber) !important;
}
[data-testid="stMetricLabel"] {
font-family: 'IBM Plex Mono', monospace !important;
color: var(--text3) !important;
font-size: 11px !important;
text-transform: uppercase;
letter-spacing: 0.1em;
}
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
/* Custom classes */
.terminal-header {
font-family: 'IBM Plex Mono', monospace;
font-size: 11px;
color: var(--text3);
text-transform: uppercase;
letter-spacing: 0.15em;
border-bottom: 1px solid var(--border);
padding-bottom: 6px;
margin-bottom: 14px;
}
.stat-card {
background: var(--bg2);
border: 1px solid var(--border);
border-radius: 3px;
padding: 14px 18px;
position: relative;
overflow: hidden;
}
.stat-card::before {
content: '';
position: absolute;
top: 0; left: 0; right: 0;
height: 2px;
}
.stat-card.amber::before { background: var(--amber); }
.stat-card.green::before { background: var(--green); }
.stat-card.red::before { background: var(--red); }
.stat-card.blue::before { background: var(--blue); }
.stat-label {
font-size: 10px;
color: var(--text3);
text-transform: uppercase;
letter-spacing: 0.12em;
margin-bottom: 6px;
}
.stat-value {
font-size: 26px;
font-weight: 600;
color: var(--text);
letter-spacing: -0.01em;
}
.stat-sub {
font-size: 11px;
color: var(--text3);
margin-top: 4px;
}
.badge {
display: inline-block;
padding: 1px 8px;
border-radius: 2px;
font-size: 10px;
font-weight: 600;
letter-spacing: 0.08em;
}
.badge-A { background: #00e67622; color: #00e676; border: 1px solid #00e67655; }
.badge-B { background: #29b6f622; color: #29b6f6; border: 1px solid #29b6f655; }
.badge-C { background: #f5a62322; color: #f5a623; border: 1px solid #f5a62355; }
.badge-D { background: #ff525222; color: #ff5252; border: 1px solid #ff525255; }
.badge-steam { background: #ff6d0022; color: #ff9100; border: 1px solid #ff6d0077; }
.badge-lock { background: #4a627522; color: #8aa0b4; border: 1px solid #4a627555; }
.ticker-bar {
background: var(--bg1);
border-top: 1px solid var(--border);
border-bottom: 1px solid var(--border);
padding: 6px 0;
font-size: 11px;
color: var(--text2);
overflow: hidden;
white-space: nowrap;
}
.prop-row {
background: var(--bg2);
border: 1px solid var(--border);
border-radius: 3px;
padding: 12px 16px;
margin-bottom: 6px;
display: grid;
grid-template-columns: 1fr auto;
align-items: center;
transition: border-color 0.15s;
}
.prop-row:hover { border-color: var(--amber); }
.book-pill {
display: inline-block;
background: var(--bg3);
border: 1px solid var(--border2);
border-radius: 2px;
padding: 1px 6px;
font-size: 9px;
color: var(--text3);
margin: 1px;
letter-spacing: 0.06em;
}
.prob-bar-bg {
background: var(--bg3);
border-radius: 1px;
height: 4px;
width: 100%;
overflow: hidden;
}
.prob-bar-fill {
height: 100%;
border-radius: 1px;
background: var(--amber);
}
.kelly-display {
font-size: 32px;
font-weight: 600;
color: var(--amber);
font-family: 'IBM Plex Mono', monospace;
}
.pnl-positive { color: var(--green); }
.pnl-negative { color: var(--red); }
.pnl-neutral { color: var(--amber); }
.section-tag {
display: inline-block;
background: var(--amber);
color: var(--bg);
font-size: 9px;
font-weight: 600;
letter-spacing: 0.15em;
padding: 2px 8px;
margin-bottom: 12px;
text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)
# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
SPORT_KEY = "baseball_mlb"
MARKET_KEY = "batter_home_runs"
ODDS_BASE = "https://api.the-odds-api.com/v4"
SHARP_BOOKS = {
"pinnacle": "Pinnacle",
"draftkings": "DraftKings",
"fanduel": "FanDuel",
"betmgm": "BetMGM",
"caesars": "Caesars",
"pointsbet_us": "PointsBet",
"bet365": "Bet365",
"williamhill_us":"William Hill",
}
# PrizePicks standard payouts by pick count
PP_PAYOUTS = {2: 3.0, 3: 5.0, 4: 10.0, 5: 20.0, 6: 25.0}
# Underdog (slightly different structure, similar payouts)
UD_PAYOUTS = {2: 3.0, 3: 6.0, 4: 10.0, 5: 20.0, 6: 40.0}
# -----------------------------------------------------------------------------
# MATH & ANALYTICS
# -----------------------------------------------------------------------------
def american_to_decimal(a: float) -> float:
return a / 100 + 1 if a > 0 else 100 / abs(a) + 1
def decimal_to_implied(d: float) -> float:
return 1 / d if d > 0 else 0
def american_to_implied(a: float) -> float:
return decimal_to_implied(american_to_decimal(a))
def remove_vig(over_imp: float, under_imp: float) -> tuple[float, float]:
total = over_imp + under_imp
if total == 0:
return 0.5, 0.5
return over_imp / total, under_imp / total
def fair_to_american(prob: float) -> int:
if prob <= 0: return 99999
if prob >= 1: return -99999
return int(round((1/prob - 1) * 100)) if prob < 0.5 else int(round(-(prob/(1-prob)) * 100
def ev_percent(fair_prob: float, payout_mult: float = 1.0) -> float:
"""EV for a DFS leg: win payout_mult x stake, lose stake."""
return fair_prob * (payout_mult + 1) - 1
def kelly_fraction(fair_prob: float, payout_mult: float = 1.0) -> float:
"""Full Kelly stake as fraction of bankroll."""
if fair_prob <= 0 or fair_prob >= 1:
return 0.0
b = payout_mult # net odds per unit
q = 1 - fair_prob
k = (b * fair_prob - q) / b
return max(k, 0.0)
def half_kelly(fair_prob: float, payout_mult: float = 1.0) -> float:
return kelly_fraction(fair_prob, payout_mult) * 0.5
def grade_play(ev: float, num_books: int, divergence: float) -> str:
"""Confidence grade A+ -> F."""
score = 0
if ev >= 0.08: score += 4
elif ev >= 0.05: score += 3
elif ev >= 0.03: score += 2
elif ev >= 0.01: score += 1
if num_books >= 5: score += 3
elif num_books >= 4: score += 2
elif num_books >= 3: score += 1
if divergence < 0.02: score += 2
elif divergence < 0.04: score += 1
if score >= 8: return "A+"
if score >= 6: return "A"
if score >= 5: if score >= 4: if score >= 3: if score >= 2: return "F"
return "B+"
return "B"
return "C"
return "D"
def grade_badge(grade: str) -> str:
g = grade.replace("+","")
cls = {"A":"badge-A","B":"badge-B","C":"badge-C","D":"badge-D","F":"badge-D"}
return f'<span class="badge {cls}">{grade}</span>'
def steam_badge() -> str:
return '<span class="badge badge-steam"> STEAM</span>'
def divergence_score(implied_list: list[float]) -> float:
return np.std(implied_list) if len(implied_list) > 1 else 0.0
def parlay_ev(legs: list[float], payout_mult: float) -> float:
combined = np.prod(legs)
return combined * payout_mult - 1
def optimal_pick_count(leg_evs: list[float], platform: str = "PrizePicks") -> dict:
"""Try all combinations and find optimal pick count."""
payouts = PP_PAYOUTS if platform == "PrizePicks" else UD_PAYOUTS
probs = [0.5 + ev/2 for ev in leg_evs] # rough fair prob from EV
results = {}
for n, mult in payouts.items():
if n <= len(probs):
# Best N legs by EV
best_n = sorted(zip(leg_evs, probs), reverse=True)[:n]
combined_prob = np.prod([p for _, p in best_n])
e = parlay_ev([p for _, p in best_n], mult)
results[n] = {"ev": e, "prob": combined_prob, "payout": mult}
return results
# -----------------------------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------------------------
def init_state():
defaults = {
"prev_implied": {}, # player -> fair_over_% for steam detection
"saved_parlays": [], # list of saved parlays
"bankroll": 1000.0, # starting bankroll
"bet_log": [], # {date, player, side, stake, result, pnl}
"last_refresh": None,
"steam_alerts": [],
"ev_history": defaultdict(list), # player -> list of ev snapshots
}
for k, v in defaults.items():
if k not in st.session_state:
st.session_state[k] = v
init_state()
# -----------------------------------------------------------------------------
# API
# -----------------------------------------------------------------------------
@st.cache_data(ttl=90)
def fetch_events(api_key: str) -> list:
url = f"{ODDS_BASE}/sports/{SPORT_KEY}/events"
try:
except:
r = requests.get(url, params={"apiKey": api_key, "dateFormat": "iso"}, timeout=10)
r.raise_for_status()
return r.json()
return []
@st.cache_data(ttl=90)
def fetch_event_props(api_key: str, event_id: str, book_keys: str) -> dict:
url = f"{ODDS_BASE}/sports/{SPORT_KEY}/events/{event_id}/odds"
params = {
"apiKey": api_key, "regions": "us",
"markets": MARKET_KEY, "oddsFormat": "american",
"bookmakers": book_keys,
}
try:
except:
r = requests.get(url, params=params, timeout=10)
r.raise_for_status()
return r.json()
return {}
@st.cache_data(ttl=300)
def fetch_quota(api_key: str) -> dict:
try:
r = requests.get(f"{ODDS_BASE}/sports", params={"apiKey": api_key}, timeout=8)
return {
"used": r.headers.get("x-requests-used", "?"),
"remaining": r.headers.get("x-requests-remaining", "?"),
}
except:
return {"used": "?", "remaining": "?"}
def fetch_all_props(api_key: str, selected_book_keys: list) -> list:
events = fetch_events(api_key)
book_keys_str = ",".join(selected_book_keys)
all_props = []
progress = st.progress(0, text="Fetching HR props...")
for i, event in enumerate(events[:15]):
progress.progress((i+1)/min(len(events),15), text=f"Fetching {event['away_team']} @ {
data = fetch_event_props(api_key, event["id"], book_keys_str)
for bk in data.get("bookmakers", []):
for mkt in bk.get("markets", []):
if mkt["key"] != MARKET_KEY: continue
for out in mkt.get("outcomes", []):
all_props.append({
"event_id": event["id"],
"game": f"{event['away_team']} @ {event['home_team']}",
"commence": event["commence_time"],
"player": out["description"],
"line": out.get("point", 0.5),
"side": out["name"],
"price": out["price"],
"book": bk["title"],
"book_key": bk["key"],
})
progress.empty()
return all_props
# -----------------------------------------------------------------------------
# MOCK DATA (realistic, using real players + 2025 opener matchups)
# -----------------------------------------------------------------------------
def mock_props() -> list:
np.random.seed(int(time.time()) // 120) # changes every 2 min for realism
players_games = [
("Shohei Ohtani","NYY @ LAD"),("Aaron Judge","NYY @ LAD"),
("Freddie Freeman","ATL @ LAD"),("Ronald Acuna Jr.","ATL @ LAD"),
("Juan Soto","NYY @ LAD"),("Pete Alonso","PHI @ NYM"),
("Yordan Alvarez","TEX @ HOU"),("Gunnar Henderson","TOR @ BAL"),
("Fernando Tatis Jr.","STL @ SD"),("Kyle Schwarber","PHI @ NYM"),
("Bryce Harper","PHI @ NYM"),("Matt Olson","ATL @ LAD"),
("Adolis Garcia","TEX @ HOU"),("Jose Ramirez","DET @ CLE"),
("Manny Machado","STL @ SD"),("Vladimir Guerrero Jr.","TOR @ BAL"),
("Marcell Ozuna","ATL @ LAD"),("Christian Yelich","MIL @ CHC"),
("Mike Trout","OAK @ LAA"),("Bo Bichette","TOR @ BAL"),
]
books = list(SHARP_BOOKS.keys())[:6]
rows = []
for player, game in players_games:
true_over = np.random.uniform(0.06, 0.22)
for book in books:
vig = np.random.uniform(0.04, 0.09)
noise = np.random.normal(0, 0.012)
book_over = true_over + noise + vig / 2
book_under = (1 - true_over) + vig / 2
# Convert to American
over_price = fair_to_american(book_over)
under_price = fair_to_american(book_under)
for side, price in [("Over", over_price), ("Under", under_price)]:
rows.append({
"event_id": game.replace(" ","_").lower(),
"game": game, "commence": "2026-03-29T19:05:00Z",
"player": player, "line": 0.5,
"side": side, "price": price,
"book": SHARP_BOOKS[book], "book_key": book,
})
return rows
# -----------------------------------------------------------------------------
# DATA PROCESSING
# -----------------------------------------------------------------------------
def process_props(raw: list) -> pd.DataFrame:
if not raw:
return pd.DataFrame()
df = pd.DataFrame(raw)
df["implied"] = df["price"].apply(american_to_implied)
# Per-book breakdown
book_breakdown = (
df.groupby(["player","game","line","side","book"])
["implied"].mean().reset_index()
)
# Aggregate
agg = (
df.groupby(["player","game","line","side"])
.agg(
avg_implied=("implied","mean"),
std_implied=("implied","std"),
num_books=("book","nunique"),
books=("book", lambda x: list(x.unique())),
best_over_price=("price", "max"),
)
.reset_index()
)
overs = agg[agg["side"].str.lower()=="over"].copy()
unders = agg[agg["side"].str.lower()=="under"].copy()
merged = overs.merge(unders, on=["player","game","line"], suffixes=("_o","_u"))
rows = []
for _, r in merged.iterrows():
fair_o, fair_u = remove_vig(r["avg_implied_o"], r["avg_implied_u"])
div = float(r["std_implied_o"]) if not np.isnan(r.get("std_implied_o",0)) else ev_more = ev_percent(fair_o, 1.0)
ev_less = ev_percent(fair_u, 1.0)
grade = grade_play(ev_more, int(r["num_books_o"]), div)
k_more = half_kelly(fair_o, 1.0)
k_less = half_kelly(fair_u, 1.0)
0.0
# Steam detection
key = f"{r['player']}_more"
prev = st.session_state.prev_implied.get(key, fair_o)
is_steam = abs(fair_o - prev) >= 0.03
if is_steam:
st.session_state.steam_alerts.append({
"player": r["player"], "game": r["game"],
"prev": prev, "curr": fair_o,
"ts": datetime.now().strftime("%H:%M:%S"),
})
st.session_state.prev_implied[key] = fair_o
rows.append({
"Player": r["player"],
"Game": r["game"],
"Line": float(r["line"]),
"Books": int(r["num_books_o"]),
"Book List": r["books_o"],
"Mkt Over": r["avg_implied_o"],
"Mkt Under": r["avg_implied_u"],
"Fair Over": fair_o,
"Fair Under": fair_u,
"Divergence": div,
"Fair Over AM": fair_to_american(fair_o),
"Fair Under AM": fair_to_american(fair_u),
"EV More": ev_more,
"EV Less": ev_less,
"1/2Kelly More": k_more,
"1/2Kelly Less": k_less,
"Grade": grade,
"Steam": is_steam,
})
result = pd.DataFrame(rows)
if not result.empty:
result = result.sort_values("EV More", ascending=False).reset_index(drop=True)
return result
# -----------------------------------------------------------------------------
# PLOTLY THEME
# -----------------------------------------------------------------------------
PLOT_LAYOUT = dict(
paper_bgcolor="#0d1117",
plot_bgcolor="#0d1117",
font=dict(family="IBM Plex Mono", color="#8aa0b4", size=11),
margin=dict(l=10, r=10, t=30, b=10),
xaxis=dict(gridcolor="#1e2d3d", zerolinecolor="#1e2d3d"),
yaxis=dict(gridcolor="#1e2d3d", zerolinecolor="#1e2d3d"),
)
def ev_distribution_chart(df: pd.DataFrame) -> go.Figure:
ev = df["EV More"].values * 100
fig = go.Figure()
fig.add_trace(go.Histogram(
x=ev, nbinsx=20,
marker_color=["#00e676" if v >= 0 else "#ff5252" for v in np.histogram(ev, 20)[0]],
marker_line_width=0,
opacity=0.85,
name="EV Distribution",
))
fig.add_vline(x=0, line_color="#f5a623", line_dash="dash", line_width=1.5)
fig.update_layout(**PLOT_LAYOUT,
title=dict(text="EV% Distribution (More HR)", font_color="#f5a623", font_size=12),
xaxis_title="EV %", yaxis_title="Count",
height=260,
)
return fig
def book_consensus_chart(df: pd.DataFrame, player: str) -> go.Figure:
row = df[df["Player"] == player]
if row.empty:
return go.Figure()
# Simulated per-book breakdown from raw
books_list = row.iloc[0]["Book List"]
probs = [row.iloc[0]["Fair Over"] + np.random.normal(0, 0.015) for _ in books_list]
probs = [max(0.01, min(0.99, p)) for p in probs]
colors = ["#00e676" if p >= row.iloc[0]["Fair Over"] else "#ff5252" for p in probs]
fig = go.Figure(go.Bar(
y=books_list, x=probs,
orientation="h",
marker_color=colors,
text=[f"{p:.1%}" for p in probs],
textposition="auto",
textfont=dict(family="IBM Plex Mono", size=10),
))
fig.add_vline(x=row.iloc[0]["Fair Over"], line_color="#f5a623",
line_dash="dot", line_width=2,
annotation_text="consensus", annotation_font_color="#f5a623",
annotation_font_size=10)
fig.update_layout(**PLOT_LAYOUT,
title=dict(text=f"{player} -- Book Implied Prob (HR Over)", font_color="#f5a623", fon
height=max(200, len(books_list) * 42),
xaxis_tickformat=".0%",
)
return fig
def ev_scatter_chart(df: pd.DataFrame) -> go.Figure:
colors = ["#00e676" if ev >= 0 else "#ff5252" for ev in df["EV More"]]
fig = go.Figure(go.Scatter(
x=df["Fair Over"],
y=df["EV More"],
mode="markers+text",
text=df["Player"].apply(lambda x: x.split()[-1]),
textposition="top center",
textfont=dict(size=9, color="#8aa0b4", family="IBM Plex Mono"),
marker=dict(
size=[8 + b*2 for b in df["Books"]],
color=df["EV More"],
colorscale=[[0,"#ff5252"],[0.5,"#f5a623"],[1,"#00e676"]],
cmin=-0.1, cmax=0.1,
showscale=False,
line=dict(width=1, color="#1e2d3d"),
),
hovertemplate="<b>%{text}</b><br>Fair Prob: %{x:.1%}<br>EV: %{y:.1%}<extra></extra>",
))
fig.add_hline(y=0, line_color="#f5a623", line_dash="dash", line_width=1)
fig.update_layout(**PLOT_LAYOUT,
title=dict(text="Fair Prob vs EV (bubble = # books)", font_color="#f5a623", font_size
xaxis_title="Fair Over %", yaxis_title="EV %",
height=300,
xaxis_tickformat=".0%", yaxis_tickformat="+.0%",
)
return fig
def bankroll_chart(bet_log: list, starting: float) -> go.Figure:
if not bet_log:
return go.Figure()
cumulative = [starting]
labels = ["Start"]
for b in bet_log:
cumulative.append(cumulative[-1] + b["pnl"])
labels.append(b["player"][:8])
color = "#00e676" if cumulative[-1] >= starting else "#ff5252"
fig = go.Figure(go.Scatter(
x=labels, y=cumulative,
mode="lines+markers",
line=dict(color=color, width=2),
marker=dict(size=6, color=color),
fill="tozeroy",
fillcolor=color.replace("#","#22") + "22",
))
fig.add_hline(y=starting, line_color="#f5a623", line_dash="dot", line_width=1)
fig.update_layout(**PLOT_LAYOUT,
title=dict(text="Bankroll History", font_color="#f5a623", font_size=12),
height=250,
yaxis_tickprefix="$",
)
return fig
def parlay_ev_chart(platform: str) -> go.Figure:
payouts = PP_PAYOUTS if platform == "PrizePicks" else UD_PAYOUTS
probs = np.linspace(0.40, 0.70, 100)
fig = go.Figure()
colors = ["#f5a623","#00e676","#29b6f6","#ff5252","#e040fb"]
for (n, mult), col in zip(payouts.items(), colors):
evs = [parlay_ev([p] * n, mult) * 100 for p in probs]
fig.add_trace(go.Scatter(
x=probs, y=evs, name=f"{n}-pick ({mult}x)",
line=dict(color=col, width=2),
))
fig.add_hline(y=0, line_color="#ffffff33", line_width=1)
fig.update_layout(**PLOT_LAYOUT,
title=dict(text=f"{platform} -- Leg EV% vs Parlay EV% (equal legs)", font_color="#f5a
xaxis_title="Per-Leg Fair Prob", yaxis_title="Parlay EV %",
xaxis_tickformat=".0%", yaxis_tickformat="+.0%",
height=280, legend=dict(bgcolor="#0d1117", bordercolor="#1e2d3d"),
)
return fig
# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
st.markdown('<div style="font-family:IBM Plex Mono;font-size:18px;font-weight:600;color:#
st.markdown('<div style="font-family:IBM Plex Mono;font-size:10px;color:#4a6275;letter-sp
st.divider()
api_key = st.text_input(
"ODDS API KEY",
value=os.environ.get("ODDS_API_KEY", ""),
type="password",
placeholder="get free key -> the-odds-api.com",
)
platform = st.selectbox("DFS PLATFORM", ["PrizePicks","Underdog Fantasy"], index=0)
st.markdown("**SHARP BOOKS**")
selected_books = st.multiselect(
"books",
options=list(SHARP_BOOKS.values()),
default=list(SHARP_BOOKS.values())[:5],
label_visibility="collapsed",
)
selected_book_keys = [k for k,v in SHARP_BOOKS.items() if v in selected_books]
st.markdown("**FILTERS**")
min_ev = st.slider("Min EV %", -15, 20, 0, 1, format="%d%%")
min_books = st.slider("Min Books", 1, 6, 2, 1)
min_grade = st.selectbox("Min Grade", ["All","B","B+","A","A+"], index=0)
st.divider()
st.markdown("**BANKROLL**")
st.session_state.bankroll = st.number_input(
"Starting Bankroll $", value=st.session_state.bankroll,
min_value=10.0, step=100.0, label_visibility="collapsed",
)
auto_refresh = st.checkbox("Auto-refresh (90s)", value=False)
refresh_btn = st.button("REFRESH REFRESH ODDS", use_container_width=True)
if api_key:
quota = fetch_quota(api_key)
st.markdown(f'<div style="font-size:10px;color:#4a6275;margin-top:8px">API: {quota["r
st.divider()
st.markdown("""<div style="font-size:10px;color:#4a6275;line-height:1.8">
METHODOLOGY<br>
1. Pull HR props from sharp books<br>
2. Average implied probabilities<br>
3. Remove vig (multiplicative)<br>
4. EV = fair_p x 2 - 1 (1:1 DFS)<br>
5. Kelly = (pxb - q) / b x 0.5<br><br>
CA LEGAL DFS<br>
Y PrizePicks<br>
Y Underdog Fantasy<br>
Y DraftKings DFS<br>
Y FanDuel DFS<br><br>
Sportsbooks: N Not legal in CA<br><br>
For entertainment only.<br>
Gamble responsibly.
</div>""", unsafe_allow_html=True)
# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------
now_str = datetime.now().strftime("%a %b %d %Y * %I:%M:%S %p")
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:4px
<div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:32px;font-weight:600;color:#f
<div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#4a6275;letter-spa
</div>
<div style="text-align:right;font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4a
</div>
<div style="height:1px;background:linear-gradient(90deg,#f5a623,#1e2d3d);margin-bottom:20px">
""", unsafe_allow_html=True)
# -----------------------------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------------------------
using_mock = False
if api_key and (refresh_btn or st.session_state.last_refresh is None):
with st.spinner(""):
raw = fetch_all_props(api_key, selected_book_keys)
st.session_state.last_refresh = datetime.now()
if not raw:
st.warning("No props returned -- check key or try on game day. Using demo data.")
raw = mock_props()
using_mock = True
elif not api_key:
raw = mock_props()
using_mock = True
else:
raw = mock_props() if not api_key else []
if not raw:
raw = mock_props()
using_mock = True
df = process_props(raw)
# Apply filters
if not df.empty:
df_filtered = df[
(df["EV More"] >= min_ev / 100) &
(df["Books"] >= min_books)
].copy()
if min_grade != "All":
grade_order = {"F":0,"D":1,"C":2,"B":3,"B+":4,"A":5,"A+":6}
threshold = grade_order.get(min_grade, 0)
df_filtered = df_filtered[df_filtered["Grade"].map(lambda g: grade_order.get(g,0)) >=
else:
df_filtered = pd.DataFrame()
# Demo banner
if using_mock:
st.markdown('<div style="background:#1a1200;border:1px solid #f5a62344;border-radius:3px;
# Steam alerts
if st.session_state.steam_alerts:
alerts = st.session_state.steam_alerts[-3:]
for a in alerts:
direction = "^" if a["curr"] > a["prev"] else "v"
st.markdown(f'<div style="background:#1a0f00;border:1px solid #ff910044;border-radius
# -----------------------------------------------------------------------------
# KPI ROW
# -----------------------------------------------------------------------------
if not df_filtered.empty:
pos_more = df_filtered[df_filtered["EV More"] >= 0.03]
pos_less = df_filtered[df_filtered["EV Less"] >= 0.03]
best_ev = df_filtered["EV More"].max()
avg_books = df_filtered["Books"].mean()
steam_ct = df_filtered["Steam"].sum()
current_br = (st.session_state.bankroll + sum(b.get("pnl",0) for b in st.session_state.be
c1,c2,c3,c4,c5,c6 = st.columns(6)
kpis = [
("c1","amber","PLAYERS","TRACKED", str(len(df_filtered)), ""),
("c2","green","+EV MORE", f">={min_ev}%", str(len(pos_more)), ""),
("c3","green","+EV LESS", f">={min_ev}%", str(len(pos_less)), ""),
("c4","amber","BEST EV","More HR", f"{best_ev:+.1%}", ""),
("c5","red" if steam_ct > 0 else "blue","STEAM","MOVES", str(int(steam_ct)), ""),
("c6","blue","BANKROLL","Current", f"${current_br:,.0f}", ""),
]
for col, (var, accent, label, sub, val, _) in zip([c1,c2,c3,c4,c5,c6], kpis):
with col:
st.markdown(f"""
<div class="stat-card {accent}">
<div class="stat-label">{label}</div>
<div class="stat-sub" style="margin-bottom:2px;font-size:9px">{sub}</div>
<div class="stat-value" style="font-size:22px">{val}</div>
</div>""", unsafe_allow_html=True)
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
# -----------------------------------------------------------------------------
# TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
" LIVE PROPS ",
" ANALYTICS ",
" PARLAY BUILDER ",
" BANKROLL ",
" METHODOLOGY ",
])
# ==============================================================================
# TAB 1 -- LIVE PROPS
# ==============================================================================
with tab1:
if df_filtered.empty:
st.info("No props match current filters.")
else:
# Top plays spotlight
st.markdown('<div class="section-tag">! TOP +EV PLAYS</div>', unsafe_allow_html=True)
top_more = df_filtered[df_filtered["EV More"] >= 0.03].head(4)
top_less = df_filtered[df_filtered["EV Less"] >= 0.03].head(4)
if not top_more.empty:
cols = st.columns(min(4, len(top_more)))
for col, (_, row) in zip(cols, top_more.iterrows()):
ev = row["EV More"]
k = row["1/2Kelly More"]
steam_txt = " " if row["Steam"] else ""
with col:
st.markdown(f"""
<div class="stat-card green" style="min-height:140px">
<div style="display:flex;justify-content:space-between;align-items:fl
{grade_badge(row['Grade'])}
<span style="font-size:9px;color:#4a6275">{row['Books']} books</s
</div>
<div style="font-size:13px;font-weight:600;color:#c8d8e8;margin-botto
<div style="font-size:9px;color:#4a6275;margin-bottom:10px">{row['Gam
<div style="display:flex;gap:12px">
<div>
<div style="font-size:9px;color:#4a6275;text-transform:upperc
<div style="font-size:18px;color:#00e676">{ev:+.1%}</div>
</div>
<div>
<div style="font-size:9px;color:#4a6275;text-transform:upperc
<div style="font-size:18px;color:#c8d8e8">{row['Fair Over']:.
</div>
<div>
<div style="font-size:9px;color:#4a6275;text-transform:upperc
<div style="font-size:18px;color:#f5a623">{k:.1%}</div>
</div>
</div>
<div style="margin-top:8px">
<div style="font-size:9px;color:#4a6275;margin-bottom:3px">HR PRO
<div class="prob-bar-bg"><div class="prob-bar-fill" style="width:
</div>
</div>""", unsafe_allow_html=True)
# Full table
st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-tag"> ALL PROPS</div>', unsafe_allow_html=True)
# Game filter
games_avail = ["All Games"] + sorted(df_filtered["Game"].unique().tolist())
game_filter = st.selectbox("Filter by Game", games_avail, index=0, label_visibility="
tdf = df_filtered if game_filter == "All Games" else df_filtered[df_filtered["Game"]
# Search
search = st.text_input("Search player", placeholder="e.g. Judge...", label_visibility
if search:
tdf = tdf[tdf["Player"].str.lower().str.contains(search.lower())]
# Build display table
display = tdf[[
"Player","Game","Books","Grade","Fair Over","Fair Under",
"Fair Over AM","Fair Under AM","EV More","EV Less","1/2Kelly More","Steam",
]].copy()
display["Fair Over"] = display["Fair Over"].map("{:.1%}".format)
display["Fair Under"] = display["Fair Under"].map("{:.1%}".format)
display["Fair Over AM"] = display["Fair Over AM"].map(lambda x: f"+{x}" if x>0 else
display["Fair Under AM"] = display["Fair Under AM"].map(lambda x: f"+{x}" if x>0 else
display["Steam"] = display["Steam"].map(lambda x: " " if x else "")
def color_ev_cell(val):
try:
v = float(val.strip("%+")) / 100
except:
return ""
if v >= 0.05: return "background-color:#14532d44;color:#4ade80;font-weight:600"
if v >= 0.02: return "background-color:#1a3320;color:#86efac"
if v <= -0.05: return "background-color:#7f1d1d33;color:#fca5a5"
return "color:#f5a623"
def color_grade(val):
g = val.replace("+","")
return {
"A": "color:#00e676;font-weight:600",
"B": "color:#29b6f6;font-weight:600",
"C": "color:#f5a623",
"D": "color:#ff5252",
"F": "color:#6b7280",
}.get(g, "")
display["EV More"] = display["EV More"].map("{:+.1%}".format)
display["EV Less"] = display["EV Less"].map("{:+.1%}".format)
display["1/2Kelly More"] = display["1/2Kelly More"].map("{:.1%}".format)
styled = (
display.style
.applymap(color_ev_cell, subset=["EV More","EV Less"])
.applymap(color_grade, subset=["Grade"])
.set_properties(**{"font-family":"IBM Plex Mono","font-size":"12px"})
)
st.dataframe(styled, use_container_width=True, height=480)
# Export
csv_buf = io.BytesIO()
tdf.to_csv(csv_buf, index=False)
st.download_button(
" Export CSV",
data=csv_buf.getvalue(),
file_name=f"hr_props_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
mime="text/csv",
)
# Book breakdown expander per player
st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-tag"> BOOK BREAKDOWN</div>', unsafe_allow_html=Tru
player_pick = st.selectbox("Select player", tdf["Player"].tolist(), label_visibility=
if player_pick:
prow = tdf[tdf["Player"]==player_pick].iloc[0]
c1, c2 = st.columns([1, 1])
with c1:
st.plotly_chart(book_consensus_chart(tdf, player_pick), use_container_width=T
with c2:
st.markdown(f"""
<div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#8aa0b
<div style="color:#f5a623;font-size:13px;margin-bottom:10px">{player_pick}</d
{''.join(f'<div style="margin:4px 0"> {b}</div>' for b in prow['Book List']
<br>
<div>Fair Over: <span style="color:#00e676">{prow['Fair Over']:.2%}</span></d
<div>Fair Under: <span style="color:#ff5252">{prow['Fair Under']:.2%}</span><
<div>Divergence: <span style="color:#f5a623">{prow['Divergence']:.3f}</span><
<div>Grade: <span style="color:#f5a623">{prow['Grade']}</span></div>
<div>EV More: <span style="color:#00e676">{prow['EV More']:+.1%}</span></div>
<div>1/2 Kelly: <span style="color:#f5a623">{prow['1/2Kelly More']:.1%} of ba
<div>Suggested stake: <span style="color:#f5a623">${prow['1/2Kelly More'] * s
</div>
""", unsafe_allow_html=True)
# ==============================================================================
# TAB 2 -- ANALYTICS
# ==============================================================================
with tab2:
if df_filtered.empty:
st.info("Load data first.")
else:
c1, c2 = st.columns(2)
with c1:
with c2:
st.plotly_chart(ev_distribution_chart(df_filtered), use_container_width=True, con
st.plotly_chart(ev_scatter_chart(df_filtered), use_container_width=True, config={
st.plotly_chart(parlay_ev_chart(platform), use_container_width=True, config={"display
# EV by game
st.markdown('<div class="section-tag"> EV BY GAME</div>', unsafe_allow_html=True)
by_game = df_filtered.groupby("Game")["EV More"].agg(["mean","max","count"]).reset_in
by_game.columns = ["Game","Avg EV","Best EV","# Players"]
by_game = by_game.sort_values("Avg EV", ascending=False)
fig_game = go.Figure(go.Bar(
x=by_game["Game"], y=by_game["Avg EV"] * 100,
marker_color=["#00e676" if v >= 0 else "#ff5252" for v in by_game["Avg EV"]],
text=[f"{v:+.1%}" for v in by_game["Avg EV"]],
textposition="auto",
textfont=dict(family="IBM Plex Mono", size=10, color="#c8d8e8"),
))
fig_game.update_layout(**PLOT_LAYOUT,
title=dict(text="Average EV% by Game", font_color="#f5a623", font_size=12),
height=260, xaxis_tickangle=-20, yaxis_tickformat="+.0%",
)
st.plotly_chart(fig_game, use_container_width=True, config={"displayModeBar":False})
# Grade breakdown
st.markdown('<div class="section-tag"> GRADE BREAKDOWN</div>', unsafe_allow_html=Tr
grade_counts = df_filtered["Grade"].value_counts()
grade_order_list = ["A+","A","B+","B","C","D","F"]
grade_counts = grade_counts.reindex([g for g in grade_order_list if g in grade_counts
colors_g = ["#00e676","#00e67699","#29b6f6","#29b6f699","#f5a623","#ff5252","#4a6275"
fig_grade = go.Figure(go.Bar(
x=grade_counts.index, y=grade_counts.values,
marker_color=colors_g[:len(grade_counts)],
text=grade_counts.values, textposition="auto",
))
fig_grade.update_layout(**PLOT_LAYOUT, height=220,
title=dict(text="Props by Confidence Grade", font_color="#f5a623", font_size=12))
st.plotly_chart(fig_grade, use_container_width=True, config={"displayModeBar":False})
# ==============================================================================
# TAB 3 -- PARLAY BUILDER
# ==============================================================================
with tab3:
if df_filtered.empty:
st.info("Load props first.")
else:
st.markdown('<div class="section-tag"> PARLAY BUILDER</div>', unsafe_allow_html=Tru
payouts = PP_PAYOUTS if platform == "PrizePicks" else UD_PAYOUTS
# Auto-suggest best legs
st.markdown('<div style="font-size:11px;color:#4a6275;margin-bottom:8px">AUTO-SUGGEST
n_suggest = st.select_slider("Suggested picks", options=[2,3,4,5,6], value=3)
best_legs_more = df_filtered.nlargest(n_suggest, "EV More")
best_legs_less = df_filtered.nlargest(n_suggest, "EV Less")
sugg_col1, sugg_col2 = st.columns(2)
with sugg_col1:
st.markdown('<div style="font-size:10px;color:#4a6275;margin-bottom:6px">BEST MOR
for _, r in best_legs_more.iterrows():
st.markdown(f"""<div class="prop-row">
fair</
<div>
<div style="font-size:12px;font-weight:600;color:#c8d8e8">{r['Player'
<div style="font-size:10px;color:#4a6275">{r['Game']}</div>
</div>
<div style="text-align:right">
<div style="font-size:15px;color:#00e676">{r['EV More']:+.1%}</div>
<div style="font-size:10px;color:#4a6275">{r['Fair Over']:.1%} </div>
</div>""", unsafe_allow_html=True)
with sugg_col2:
st.markdown('<div style="font-size:10px;color:#4a6275;margin-bottom:6px">BEST LES
for _, r in best_legs_less.iterrows():
st.markdown(f"""<div class="prop-row">
<div>
<div style="font-size:12px;font-weight:600;color:#c8d8e8">{r['Player'
<div style="font-size:10px;color:#4a6275">{r['Game']}</div>
</div>
<div style="text-align:right">
<div style="font-size:15px;color:#00e676">{r['EV Less']:+.1%}</div>
<div style="font-size:10px;color:#4a6275">{r['Fair Under']:.1%} fair<
</div>
</div>""", unsafe_allow_html=True)
st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-tag"> CUSTOM PARLAY</div>', unsafe_allow_html=True
selected_players = st.multiselect(
"Add legs",
df_filtered["Player"].tolist(),
default=df_filtered["Player"].tolist()[:3],
max_selections=6,
label_visibility="collapsed",
)
if selected_players:
parlay_rows = df_filtered[df_filtered["Player"].isin(selected_players)]
leg_data = []
cols = st.columns(len(selected_players))
for i, (_, row) in enumerate(parlay_rows.iterrows()):
with cols[i]:
direction = st.radio(
row["Player"].split()[-1][:8],
["More","Less"], key=f"par_{row['Player']}",
)
fair_p = row["Fair Over"] if direction == "More" else row["Fair Under"]
ev = row["EV More"] if direction == "More" else row["EV Less"]
leg_data.append({
"player": row["Player"], "game": row["Game"],
"direction": direction, "fair_p": fair_p, "ev": ev,
"grade": row["Grade"],
})
color = "#00e676" if ev >= 0.02 else "#ff5252"
st.markdown(f'<div style="text-align:center;font-size:11px;color:{color};
# Correlation warning (same game)
games_in_parlay = [l["game"] for l in leg_data]
game_dupes = [g for g in set(games_in_parlay) if games_in_parlay.count(g) > 1]
if game_dupes:
st.markdown(f'<div style="background:#1a0a00;border:1px solid #ff6d0044;borde
n = len(leg_data)
payout_mult = (PP_PAYOUTS if platform == "PrizePicks" else UD_PAYOUTS).get(n, n*2
combined_prob = np.prod([l["fair_p"] for l in leg_data])
par_ev = parlay_ev([l["fair_p"] for l in leg_data], payout_mult)
stake = st.slider("Stake $", 1, int(st.session_state.bankroll), 10)
pnl_win = stake * payout_mult
pnl_lose = -stake
expected_return = combined_prob * pnl_win + (1-combined_prob) * pnl_lose
st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
m1,m2,m3,m4 = st.columns(4)
ev_color = "#00e676" if par_ev >= 0 else "#ff5252"
with m1:
st.markdown(f'<div class="stat-card amber"><div class="stat-label">COMBINED P
with m2:
st.markdown(f'<div class="stat-card {"green" if par_ev>=0 else "red"}"><div c
with m3:
st.markdown(f'<div class="stat-card amber"><div class="stat-label">PAYOUT ({n
with m4:
er_color = "#00e676" if expected_return >= 0 else "#ff5252"
st.markdown(f'<div class="stat-card blue"><div class="stat-label">EXP. RETURN
# Optimal pick count chart
all_evs = [l["ev"] for l in leg_data]
opt = optimal_pick_count(all_evs, platform)
if opt:
fig_opt = go.Figure(go.Bar(
x=[f"{n}-pick" for n in opt],
y=[v["ev"]*100 for v in opt.values()],
marker_color=["#00e676" if v["ev"] >= 0 else "#ff5252" for v in opt.value
text=[f"{v['ev']:+.1%}" for v in opt.values()],
textposition="auto",
textfont=dict(family="IBM Plex Mono", size=10, color="#c8d8e8"),
))
fig_opt.add_hline(y=0, line_color="#f5a62355", line_width=1)
fig_opt.update_layout(**PLOT_LAYOUT, height=200,
title=dict(text="Optimal Pick Count (using selected legs)", font_color="#
st.plotly_chart(fig_opt, use_container_width=True, config={"displayModeBar":F
if st.button(" Save Parlay", use_container_width=True):
st.session_state.saved_parlays.append({
"id": len(st.session_state.saved_parlays)+1,
"legs": leg_data, "n": n, "payout": payout_mult,
"ev": par_ev, "stake": stake, "prob": combined_prob,
"platform": platform, "saved_at": datetime.now().strftime("%H:%M"),
})
st.success("Parlay saved! View in Bankroll tab.")
# Saved parlays
if st.session_state.saved_parlays:
st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-tag"> SAVED PARLAYS</div>', unsafe_allow_html=
for p in reversed(st.session_state.saved_parlays[-5:]):
ev_c = "#00e676" if p["ev"] >= 0 else "#ff5252"
legs_str = " * ".join([f"{l['player'].split()[-1]} {l['direction']}" for l in
st.markdown(f"""<div class="prop-row">
<div>
<div style="font-size:11px;color:#c8d8e8">{legs_str}</div>
<div style="font-size:9px;color:#4a6275">{p['platform']} * {p['n']}-p
</div>
<div style="text-align:right">
<div style="font-size:14px;color:{ev_c}">{p['ev']:+.1%}</div>
<div style="font-size:10px;color:#4a6275">{p['payout']}x * ${p['stake
</div>
</div>""", unsafe_allow_html=True)
# ==============================================================================
# TAB 4 -- BANKROLL
# ==============================================================================
with tab4:
st.markdown('<div class="section-tag"> BANKROLL MANAGER</div>', unsafe_allow_html=True)
current_br = st.session_state.bankroll + sum(b.get("pnl",0) for b in st.session_state.bet
total_pnl = current_br - st.session_state.bankroll
win_bets = [b for b in st.session_state.bet_log if b.get("pnl",0) > 0]
lose_bets = [b for b in st.session_state.bet_log if b.get("pnl",0) < 0]
roi = (total_pnl / st.session_state.bankroll) * 100 if st.session_state.bankroll else 0
mc1,mc2,mc3,mc4 = st.columns(4)
pnl_c = "green" if total_pnl >= 0 else "red"
with mc1:
st.markdown(f'<div class="stat-card amber"><div class="stat-label">CURRENT BANKROLL</
with mc2:
with mc3:
with mc4:
st.markdown(f'<div class="stat-card {pnl_c}"><div class="stat-label">TOTAL P&L</div><
wr = len(win_bets)/len(st.session_state.bet_log)*100 if st.session_state.bet_log else
st.markdown(f'<div class="stat-card blue"><div class="stat-label">WIN RATE</div><div
st.markdown(f'<div class="stat-card {"green" if roi>=0 else "red"}"><div class="stat-
# Bankroll chart
if st.session_state.bet_log:
st.plotly_chart(bankroll_chart(st.session_state.bet_log, st.session_state.bankroll),
use_container_width=True, config={"displayModeBar":False})
# Kelly calculator
st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-tag"> KELLY CALCULATOR</div>', unsafe_allow_html=True)
kc1, kc2 = st.columns([1,1])
with kc1:
k_fair_p = st.slider("Fair Probability", 5, 80, 15, 1, format="%d%%") / 100
k_payout = st.slider("DFS Payout (x)", 1.0, 25.0, 1.0, 0.5)
with kc2:
full_k = kelly_fraction(k_fair_p, k_payout)
half_k = full_k * 0.5
quarter_k = full_k * 0.25
k_ev = ev_percent(k_fair_p, k_payout)
stake_full = full_k * current_br
stake_half = half_k * current_br
ev_color_k = "#00e676" if k_ev >= 0 else "#ff5252"
st.markdown(f"""
<div class="stat-card amber" style="margin-bottom:8px">
<div class="stat-label">EV AT THESE ODDS</div>
<div class="stat-value" style="color:{ev_color_k}">{k_ev:+.1%}</div>
</div>""", unsafe_allow_html=True)
st.markdown(f"""
<div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#8aa0b4;backgr
<div style="margin-bottom:6px">Full Kelly: <span style="color:#f5a623">{full_k:.1%}</
<div style="margin-bottom:6px">Half Kelly: <span style="color:#00e676">{half_k:.1%}</
<div>Quarter Kelly: <span style="color:#29b6f6">{quarter_k:.1%}</span> -> <span style
</div>
""", unsafe_allow_html=True)
# Log a bet
st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-tag"> LOG BET RESULT</div>', unsafe_allow_html=True)
lc1, lc2, lc3, lc4, lc5 = st.columns([2,1,1,1,1])
with lc1:
log_player = st.text_input("Player", placeholder="Name...", label_visibility="collaps
with lc2:
log_side = st.selectbox("Side", ["More","Less"], label_visibility="collapsed")
with lc3:
log_stake = st.number_input("Stake $", min_value=1.0, value=10.0, label_visibility="c
with lc4:
log_payout = st.number_input("Payout x", min_value=1.0, value=1.0, label_visibility="
with lc5:
log_result = st.selectbox("Result", ["Win","Loss"], label_visibility="collapsed")
if st.button("Log Bet", use_container_width=True):
pnl = log_stake * log_payout if log_result == "Win" else -log_stake
st.session_state.bet_log.append({
"player": log_player, "side": log_side,
"stake": log_stake, "payout": log_payout,
"result": log_result, "pnl": pnl,
"date": datetime.now().strftime("%m/%d %H:%M"),
})
st.success(f"Logged: {' st.rerun()
' if log_result=='Win' else ' '} {log_player} {log_side} ->
# Bet log table
if st.session_state.bet_log:
st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
log_df = pd.DataFrame(st.session_state.bet_log)
log_df["P&L"] = log_df["pnl"].map("${:+.2f}".format)
def color_pnl(val):
return "color:#00e676" if "+" in val else "color:#ff5252"
st.dataframe(
log_df[["date","player","side","stake","payout","result","P&L"]]
.style.applymap(color_pnl, subset=["P&L"])
.set_properties(**{"font-family":"IBM Plex Mono","font-size":"11px"}),
use_container_width=True, height=220,
)
if st.button(" Clear Log"):
st.session_state.bet_log = []
st.rerun()
# ==============================================================================
# TAB 5 -- METHODOLOGY
# ==============================================================================
with tab5:
st.markdown("""
<div style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:#8aa0b4;line-heigh
<div style="color:#f5a623;font-size:14px;margin-bottom:12px">FAIR VALUE CALCULATION</div>
<b style="color:#c8d8e8">Step 1 -- Data Collection</b><br>
HR props pulled from The Odds API using sharp, high-liquidity books.
Books ordered by sharpness: Pinnacle -> DraftKings -> FanDuel -> BetMGM -> Caesars.<br><b
<b style="color:#c8d8e8">Step 2 -- Implied Probability</b><br>
Each book's American odds converted: <span style="color:#29b6f6">implied = 1 / decimal</s
American -> Decimal: positive odds = o/100+1, negative odds = 100/|o|+1<br><br>
<b style="color:#c8d8e8">Step 3 -- Consensus (Market Truth)</b><br>
Simple arithmetic mean across all sharp books for each side.
More books = higher confidence = better grade.<br><br>
<b style="color:#c8d8e8">Step 4 -- No-Vig (Multiplicative Method)</b><br>
<span style="color:#29b6f6">fair_over = mkt_over / (mkt_over + mkt_under)</span><br>
This removes the bookmaker margin proportionally from both sides.<br><br>
<b style="color:#c8d8e8">Step 5 -- EV vs DFS Platform</b><br>
PrizePicks and Underdog pay ~1:1 per leg (entry buyin returned if leg wins).<br>
<span style="color:#29b6f6">EV = fair_p x (payout + 1) - 1</span><br>
For 1:1 this simplifies to: <span style="color:#29b6f6">EV = fair_p x 2 - 1</span><br>
Break-even at fair_p = 50.0%<br><br>
<b style="color:#c8d8e8">Step 6 -- Kelly Criterion (1/2 Kelly)</b><br>
<span style="color:#29b6f6">Full Kelly = (bxp - q) / b</span> where b=net payout odds, p=
We use 1/2 Kelly to reduce variance while maintaining edge.<br><br>
<div style="color:#f5a623;font-size:14px;margin:16px 0 12px 0">CONFIDENCE GRADE</div>
Grades scored on EV magnitude, number of books sampled, and book divergence (std dev):<br
<span style="color:#00e676">A+ / A</span> -- High EV, 4+ books, low divergence<br>
<span style="color:#29b6f6">B+ / B</span> -- Moderate EV, 3+ books<br>
<span style="color:#f5a623">C</span> -- Low EV or few books<br>
<span style="color:#ff5252">D / F</span> -- Marginal or negative EV<br><br>
<div style="color:#f5a623;font-size:14px;margin:16px 0 12px 0">STEAM DETECTION</div>
A "steam move" flag triggers when the fair probability shifts >=3% between refreshes.
This can indicate sharp money moving the line or new information (injury, lineup change).
<div style="color:#f5a623;font-size:14px;margin:16px 0 12px 0">CALIFORNIA DFS CONTEXT</di
Traditional fixed-odds sports betting is not legal in CA as of 2026.
DFS platforms (PrizePicks, Underdog Fantasy, DraftKings DFS, FanDuel DFS) operate legally
This tool identifies when market-implied fair probability creates positive expected value
against a platform's fixed payout structure.<br><br>
<div style="color:#f5a623;font-size:14px;margin:16px 0 12px 0">LIMITATIONS & DISCLAIMER</
* HR props are low-probability events with high variance. EV edge can be wiped by small s
* DFS platform payouts and rules change -- always verify current structure before playing
* Correlation between players in the same game is not fully modeled<br>
* This tool is for informational and educational purposes only<br>
* Past EV does not guarantee future results. Play within your means<br><br>
</div>
""", unsafe_allow_html=True)
# -----------------------------------------------------------------------------
# AUTO-REFRESH
# -----------------------------------------------------------------------------
if auto_refresh:
elapsed = (datetime.now() - st.session_state.last_refresh).seconds if st.session_state.la
remaining = max(0, 90 - elapsed)
if remaining == 0:
st.cache_data.clear()
st.rerun()
else:
st.markdown(f'<div style="position:fixed;bottom:12px;right:16px;font-family:\'IBM Ple
time.sleep(1)
st.rerun()
