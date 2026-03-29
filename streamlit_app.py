import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import time

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
page_title="⚾ HR EV Scout",
page_icon="⚾”,
layout="wide”,
initial_sidebar_state="expanded”,
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0e1a;
    color: #e8eaf0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1526;
    border-right: 1px solid #1e2740;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #12192e 0%, #0f1526 100%);
    border: 1px solid #1e2740;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 8px;
}

.metric-card h4 {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #5c6a8a;
    margin: 0 0 6px 0;
}

.metric-card .val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 36px;
    letter-spacing: 1px;
    line-height: 1;
}

/* EV table rows */
.ev-row {
    display: grid;
    grid-template-columns: 28px 1fr 90px 80px 80px 90px 100px;
    align-items: center;
    gap: 10px;
    padding: 14px 18px;
    border-bottom: 1px solid #141b2d;
    transition: background 0.15s;
}
.ev-row:hover { background: #141b2d; }

.ev-row.header {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #3d4e73;
    border-bottom: 1px solid #1e2740;
    padding-top: 10px;
    padding-bottom: 10px;
}

.rank { font-family: 'Bebas Neue'; font-size: 20px; color: #3d4e73; }
.top3 { color: #f5c842; }

.player-name { font-weight: 600; font-size: 15px; }
.player-team { font-size: 11px; color: #5c6a8a; margin-top: 1px; font-family: 'DM Mono'; }

.book-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    padding: 3px 8px;
    border-radius: 4px;
    letter-spacing: 1px;
}
.pp   { background: #1a2d1a; color: #4cde80; border: 1px solid #2a4a2a; }
.ud   { background: #2d1a1a; color: #de6a4c; border: 1px solid #4a2a2a; }
.fl   { background: #1a1a2d; color: #6a9cde; border: 1px solid #2a2a4a; }
.bt   { background: #2d2d1a; color: #deb84c; border: 1px solid #4a4a2a; }
.fd   { background: #1a2535; color: #4cafde; border: 1px solid #1e3050; }

.odds-mono { font-family: 'DM Mono', monospace; font-size: 13px; }
.odds-pos  { color: #4cde80; }
.odds-neg  { color: #de6a4c; }

.fair-prob { font-family: 'DM Mono', monospace; font-size: 13px; color: #9aa8c8; }

.ev-pill {
    display: inline-block;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 17px;
    letter-spacing: 0.5px;
    padding: 4px 12px;
    border-radius: 6px;
}
.ev-hot  { background: #0d3320; color: #3dfa8c; border: 1px solid #1a5530; }
.ev-warm { background: #1a2e0d; color: #8dde4c; border: 1px solid #2a4a18; }
.ev-cold { background: #2e1a0d; color: #de8c4c; border: 1px solid #4a2a18; }

.grade {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 22px;
    text-align: center;
}

.source-status {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px;
    border-radius: 8px;
    margin-bottom: 6px;
    font-size: 13px;
    background: #0f1526;
    border: 1px solid #1e2740;
}
.dot-green { width:8px;height:8px;border-radius:50%;background:#3dfa8c;flex-shrink:0; }
.dot-yellow{ width:8px;height:8px;border-radius:50%;background:#f5c842;flex-shrink:0; }
.dot-red   { width:8px;height:8px;border-radius:50%;background:#fa3d5a;flex-shrink:0; }

/* Streamlit overrides */
div[data-testid="stMetric"] { display: none; }
.stButton>button {
    background: linear-gradient(135deg, #1e3a5f, #153060);
    color: #7bb8f5;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 10px 20px;
    width: 100%;
    transition: all 0.2s;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #254870, #1a3870);
    border-color: #4a90d9;
    color: #a8d0ff;
}
.stTextInput>div>div>input {
    background: #0a0e1a;
    border: 1px solid #1e2740;
    border-radius: 8px;
    color: #e8eaf0;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
}
h1 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 2px !important; }
h2 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 1px !important; }
h3 { font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; }

.stDataFrame { display: none; }

.table-wrap {
    background: #0d1221;
    border: 1px solid #1e2740;
    border-radius: 14px;
    overflow: hidden;
    margin-top: 12px;
}
</style>

“””, unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def american_to_prob(odds: float) -> float:
“”“Convert American odds to implied probability.”””
if odds >= 0:
return 100 / (odds + 100)
else:
return abs(odds) / (abs(odds) + 100)

def prob_to_american(prob: float) -> float:
“”“Convert probability to American odds.”””
if prob <= 0 or prob >= 1:
return 0
if prob >= 0.5:
return -(prob / (1 - prob)) * 100
else:
return ((1 - prob) / prob) * 100

def remove_vig(yes_odds: float, no_odds: float) -> tuple:
“”“Return (fair_yes_prob, fair_no_prob) with vig removed.”””
p_yes = american_to_prob(yes_odds)
p_no  = american_to_prob(no_odds)
total = p_yes + p_no
return p_yes / total, p_no / total

def calc_ev(fair_prob: float, bet_odds: float) -> float:
“”“EV per $1 wagered.”””
if bet_odds >= 0:
payout = bet_odds / 100
else:
payout = 100 / abs(bet_odds)
return fair_prob * payout - (1 - fair_prob) * 1

def ev_grade(ev: float) -> str:
if ev >= 0.12: return “A+”
if ev >= 0.08: return “A”
if ev >= 0.05: return “B+”
if ev >= 0.03: return “B”
if ev >= 0.01: return “C”
return “D”

def ev_class(ev: float) -> str:
if ev >= 0.06: return “ev-hot”
if ev >= 0.02: return “ev-warm”
return “ev-cold”

def odds_class(odds: float) -> str:
return “odds-pos” if odds >= 0 else “odds-neg”

def fmt_odds(odds: float) -> str:
return f”+{int(odds)}” if odds >= 0 else str(int(odds))

def fmt_pct(p: float) -> str:
return f”{p*100:.1f}%”

# ── Data fetching ─────────────────────────────────────────────────────────────

PRIZEPICKS_URL = (
“https://api.prizepicks.com/projections”
“?league_id=2&per_page=500&single_stat=true&state_code=CA”
)
PRIZEPICKS_HEADERS = {
“User-Agent”: “Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) “
“AppleWebKit/537.36 (KHTML, like Gecko) “
“Chrome/122.0.0.0 Safari/537.36”,
“Accept”: “application/json”,
“Referer”: “https://app.prizepicks.com/”,
}

UNDERDOG_URL = “https://api.underdogfantasy.com/beta/v5/over_under_lines”
UNDERDOG_HEADERS = {
“User-Agent”: “Mozilla/5.0”,
“Accept”: “application/json”,
}

@st.cache_data(ttl=180, show_spinner=False)
def fetch_fanduel_hrs(api_key: str) -> tuple:
“”“Fetch FanDuel HR odds from The Odds API. Returns (list_of_props, error_msg).”””
if not api_key:
return [], “No Odds API key provided”
try:
url = (
“https://api.the-odds-api.com/v4/sports/baseball_mlb/events”
f”?apiKey={api_key}&dateFormat=iso”
)
r = requests.get(url, timeout=10)
if r.status_code == 401:
return [], “Invalid Odds API key”
if r.status_code != 200:
return [], f”Odds API error {r.status_code}”

```
    events = r.json()
    if not events:
        return [], "No MLB games found today"

    props = []
    for ev in events[:20]:  # limit to first 20 games
        event_id = ev["id"]
        prop_url = (
            f"https://api.the-odds-api.com/v4/sports/baseball_mlb/events/{event_id}/odds"
            f"?apiKey={api_key}&regions=us&markets=batter_home_runs&oddsFormat=american"
            f"&bookmakers=fanduel"
        )
        pr = requests.get(prop_url, timeout=10)
        if pr.status_code != 200:
            continue
        data = pr.json()
        for bm in data.get("bookmakers", []):
            if bm["key"] != "fanduel":
                continue
            for mkt in bm.get("markets", []):
                if mkt["key"] != "batter_home_runs":
                    continue
                for outcome in mkt.get("outcomes", []):
                    props.append({
                        "player":    outcome["description"],
                        "book":      "FanDuel",
                        "line_type": outcome["name"],   # "Over" / "Under"
                        "line":      outcome.get("point", 0.5),
                        "odds":      outcome["price"],
                        "game":      f"{ev.get('home_team','')} vs {ev.get('away_team','')}",
                        "commence":  ev.get("commence_time", ""),
                    })
        time.sleep(0.15)
    return props, None
except Exception as e:
    return [], str(e)
```

@st.cache_data(ttl=180, show_spinner=False)
def fetch_other_books_hrs(api_key: str) -> tuple:
“”“Fetch HR odds from multiple books (PrizePicks, Underdog, DraftKings, BetMGM) via Odds API + direct APIs.”””
results = []
errors  = {}

```
# ── PrizePicks (unofficial API) ──────────────────────────────────────────
try:
    r = requests.get(PRIZEPICKS_URL, headers=PRIZEPICKS_HEADERS, timeout=10)
    if r.status_code == 200:
        data   = r.json()
        players = {p["id"]: p for p in data.get("included", []) if p.get("type") == "new_player"}
        for proj in data.get("data", []):
            attrs = proj.get("attributes", {})
            if attrs.get("stat_type", "").lower() not in ("home runs", "homeruns", "hr"):
                continue
            pid   = proj.get("relationships", {}).get("new_player", {}).get("data", {}).get("id")
            pinfo = players.get(pid, {}).get("attributes", {})
            name  = pinfo.get("display_name") or attrs.get("description") or "Unknown"
            team  = pinfo.get("team_abbreviation", "")
            line  = float(attrs.get("line_score", 0.5))
            # PrizePicks pays fixed ~2x for single-pick over/under on most apps
            # Treat as implied +100 / +100 (breakeven at 50%)
            results.append({
                "player": name, "team": team, "book": "PrizePicks",
                "line": line, "line_type": "Over", "odds": 100,
                "payout_multiplier": 2.0,
            })
        errors["PrizePicks"] = None
    else:
        errors["PrizePicks"] = f"HTTP {r.status_code}"
except Exception as e:
    errors["PrizePicks"] = str(e)

# ── Underdog Fantasy (unofficial API) ────────────────────────────────────
try:
    r = requests.get(UNDERDOG_URL, headers=UNDERDOG_HEADERS, timeout=10)
    if r.status_code == 200:
        data    = r.json()
        appears = {a["id"]: a for a in data.get("appearances", [])}
        players = {p["id"]: p for p in data.get("players", [])}

        for ol in data.get("over_under_lines", []):
            stat = ol.get("stat_value", "")
            if stat.lower() not in ("home runs", "hr"):
                continue
            app_id = ol.get("appearance_id")
            app    = appears.get(app_id, {})
            pl     = players.get(app.get("player_id", ""), {})
            name   = (pl.get("first_name", "") + " " + pl.get("last_name", "")).strip()
            team   = app.get("team", {}).get("abbreviation", "") if isinstance(app.get("team"), dict) else ""
            line   = float(ol.get("stat_value_decimal", 0.5))
            results.append({
                "player": name, "team": team, "book": "Underdog",
                "line": line, "line_type": "Over", "odds": 100,
                "payout_multiplier": 2.0,
            })
        errors["Underdog"] = None
    else:
        errors["Underdog"] = f"HTTP {r.status_code}"
except Exception as e:
    errors["Underdog"] = str(e)

# ── Fliff & Betr via The Odds API (if key available) ─────────────────────
for book_key, book_label in [("fliff", "Fliff"), ("betr", "Betr")]:
    if not api_key:
        errors[book_label] = "Odds API key required"
        continue
    try:
        url = (
            "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
            f"?apiKey={api_key}&regions=us&markets=batter_home_runs"
            f"&oddsFormat=american&bookmakers={book_key}"
        )
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for ev in r.json():
                for bm in ev.get("bookmakers", []):
                    for mkt in bm.get("markets", []):
                        for outcome in mkt.get("outcomes", []):
                            results.append({
                                "player": outcome.get("description", ""),
                                "team": "",
                                "book": book_label,
                                "line": outcome.get("point", 0.5),
                                "line_type": outcome.get("name", "Over"),
                                "odds": outcome["price"],
                                "payout_multiplier": None,
                            })
            errors[book_label] = None
        else:
            errors[book_label] = f"HTTP {r.status_code}"
    except Exception as e:
        errors[book_label] = str(e)

# ── DraftKings as bonus via Odds API ─────────────────────────────────────
if api_key:
    try:
        url = (
            "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
            "?apiKey=" + api_key +
            "&regions=us&markets=batter_home_runs"
            "&oddsFormat=american&bookmakers=draftkings"
        )
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for ev in r.json():
                for bm in ev.get("bookmakers", []):
                    for mkt in bm.get("markets", []):
                        for outcome in mkt.get("outcomes", []):
                            results.append({
                                "player": outcome.get("description", ""),
                                "team": "",
                                "book": "DraftKings",
                                "line": outcome.get("point", 0.5),
                                "line_type": outcome.get("name", "Over"),
                                "odds": outcome["price"],
                                "payout_multiplier": None,
                            })
    except Exception:
        pass

return results, errors
```

def build_ev_table(fd_props: list, other_props: list) -> pd.DataFrame:
“””
For each player+line found on other books, look up FanDuel no-vig fair prob
and compute EV.
“””
# Build FanDuel fair-prob lookup: (player_lower, line, “over”) -> fair_prob
fd_lookup = {}
# Group FD props by player+line
from collections import defaultdict
fd_by_player = defaultdict(list)
for p in fd_props:
key = (p[“player”].lower().strip(), float(p[“line”]))
fd_by_player[key].append(p)

```
for (player_key, line), group in fd_by_player.items():
    over  = next((x for x in group if x["line_type"].lower() == "over"),  None)
    under = next((x for x in group if x["line_type"].lower() == "under"), None)
    if over and under:
        fp_over, fp_under = remove_vig(over["odds"], under["odds"])
        fd_lookup[(player_key, line, "over")]  = (fp_over,  over["odds"],  under["odds"])
        fd_lookup[(player_key, line, "under")] = (fp_under, over["odds"],  under["odds"])
    elif over:
        fp = american_to_prob(over["odds"])
        fd_lookup[(player_key, line, "over")] = (fp, over["odds"], None)

rows = []
for p in other_props:
    name      = p["player"].strip()
    line      = float(p.get("line", 0.5))
    lt        = p.get("line_type", "Over").lower()
    odds      = float(p.get("odds", 100))
    book      = p["book"]
    team      = p.get("team", "")
    mult      = p.get("payout_multiplier")

    key = (name.lower(), line, lt)
    if key not in fd_lookup:
        # try partial match on first/last name
        for (pk, pl, plt), val in fd_lookup.items():
            name_parts = name.lower().split()
            if any(part in pk for part in name_parts) and abs(pl - line) < 0.26 and plt == lt:
                key = (pk, pl, plt)
                name = pk.title()
                break

    if key not in fd_lookup:
        continue

    fair_prob, fd_over_odds, fd_under_odds = fd_lookup[key]

    # EV calculation
    if mult:
        # DFS-style: payout is (mult - 1) per $1 on win
        ev = fair_prob * (mult - 1) - (1 - fair_prob) * 1
    else:
        ev = calc_ev(fair_prob, odds)

    if ev <= 0:
        continue

    rows.append({
        "player":       name.title(),
        "team":         team.upper(),
        "book":         book,
        "line":         line,
        "line_type":    lt.title(),
        "odds":         odds,
        "fd_over":      fd_over_odds,
        "fd_under":     fd_under_odds,
        "fair_prob":    fair_prob,
        "ev":           ev,
        "grade":        ev_grade(ev),
        "mult":         mult,
    })

if not rows:
    return pd.DataFrame()

df = pd.DataFrame(rows).sort_values("ev", ascending=False).drop_duplicates(
    subset=["player", "book", "line_type"]
).head(10).reset_index(drop=True)
return df
```

def book_badge(book: str) -> str:
cls = {“PrizePicks”: “pp”, “Underdog”: “ud”, “Fliff”: “fl”,
“Betr”: “bt”, “FanDuel”: “fd”, “DraftKings”: “fd”}.get(book, “fd”)
short = {“PrizePicks”: “PP”, “Underdog”: “UD”, “Fliff”: “FL”,
“Betr”: “BT”, “DraftKings”: “DK”}.get(book, book[:2].upper())
return f’<span class="book-badge {cls}">{short}</span>’

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
st.markdown(”””
<div style="padding:12px 0 20px;">
<div style="font-family:'Bebas Neue',sans-serif;font-size:32px;
letter-spacing:2px;line-height:1;">⚾ HR EV Scout</div>
<div style="font-family:'DM Mono',monospace;font-size:10px;
color:#3d4e73;letter-spacing:2px;margin-top:4px;">
HOMERUN EXPECTED VALUE FINDER
</div>
</div>
“””, unsafe_allow_html=True)

```
odds_api_key = st.text_input(
    "🔑 The Odds API Key",
    type="password",
    placeholder="Enter key for FanDuel + Fliff + Betr",
    help="Free key at the-odds-api.com — needed for FanDuel fair value, Fliff, and Betr odds.",
)

st.markdown("---")
st.markdown("""
<div style="font-family:'DM Mono',monospace;font-size:10px;
            color:#3d4e73;letter-spacing:1.5px;margin-bottom:10px;">
    FAIR VALUE SOURCE
</div>
""", unsafe_allow_html=True)

fair_value_book = st.selectbox(
    "", ["FanDuel (default)", "DraftKings"], label_visibility="collapsed"
)

min_ev = st.slider("Min EV threshold", 0.0, 0.20, 0.01, 0.005,
                   format="%.3f",
                   help="Only show picks above this EV per $1")

st.markdown("---")
refresh = st.button("⟳  REFRESH DATA")

st.markdown("""
<div style="margin-top:24px;">
    <div style="font-family:'DM Mono',monospace;font-size:10px;
                color:#3d4e73;letter-spacing:1.5px;margin-bottom:10px;">
        DATA SOURCES
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="source-status"><span class="dot-green"></span>
    <span style="font-size:12px;">PrizePicks <span style="color:#3d4e73">— direct API</span></span></div>
<div class="source-status"><span class="dot-green"></span>
    <span style="font-size:12px;">Underdog <span style="color:#3d4e73">— direct API</span></span></div>
<div class="source-status"><span class="dot-yellow"></span>
    <span style="font-size:12px;">Fliff <span style="color:#3d4e73">— Odds API key</span></span></div>
<div class="source-status"><span class="dot-yellow"></span>
    <span style="font-size:12px;">Betr <span style="color:#3d4e73">— Odds API key</span></span></div>
<div class="source-status"><span class="dot-yellow"></span>
    <span style="font-size:12px;">FanDuel <span style="color:#3d4e73">— Odds API key</span></span></div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:24px;padding:14px;background:#090d19;
            border-radius:10px;border:1px solid #1e2740;">
    <div style="font-family:'DM Mono',monospace;font-size:10px;
                color:#3d4e73;letter-spacing:1.5px;margin-bottom:8px;">HOW EV IS CALCULATED</div>
    <div style="font-size:11px;color:#6a7a9a;line-height:1.7;">
        <b style="color:#9aa8c8;">Fair prob</b> = FanDuel no-vig implied probability<br>
        <b style="color:#9aa8c8;">EV</b> = P(win)×Payout − P(loss)×Stake<br>
        <b style="color:#9aa8c8;">Grade A+</b> = EV ≥ 12¢ per $1
    </div>
</div>
""", unsafe_allow_html=True)
```

# ── Main content ──────────────────────────────────────────────────────────────

col_title, col_ts = st.columns([3, 1])
with col_title:
st.markdown(”””
<h1 style="margin:0;padding:0;">TODAY’S HOMERUN EV PICKS</h1>
<p style="color:#3d4e73;font-family:'DM Mono',monospace;font-size:11px;
letter-spacing:1.5px;margin-top:4px;">
COMPARING PRIZEPICKS · UNDERDOG · FLIFF · BETR vs FANDUEL FAIR LINE
</p>
“””, unsafe_allow_html=True)
with col_ts:
st.markdown(f”””
<div style="text-align:right;padding-top:12px;">
<div style="font-family:'DM Mono',monospace;font-size:11px;color:#3d4e73;">
LAST UPDATED
</div>
<div style="font-family:'DM Mono',monospace;font-size:13px;color:#9aa8c8;">
{datetime.now().strftime(’%I:%M %p’)}
</div>
</div>
“””, unsafe_allow_html=True)

st.markdown(”<div style='height:12px'></div>”, unsafe_allow_html=True)

# ── Fetch data ────────────────────────────────────────────────────────────────

if “data_loaded” not in st.session_state or refresh:
st.session_state.data_loaded = True

with st.spinner(“Fetching odds from all sources…”):
fd_props,    fd_err     = fetch_fanduel_hrs(odds_api_key)
other_props, other_errs = fetch_other_books_hrs(odds_api_key)

# ── Source status row ─────────────────────────────────────────────────────────

def status_dot(err):
if err is None:          return “dot-green”,  “LIVE”
if “key” in str(err).lower() or “API” in str(err): return “dot-yellow”, “KEY REQ”
return “dot-red”, “ERROR”

books_status = {
“FanDuel”:    (fd_err if fd_err else None),
“PrizePicks”: other_errs.get(“PrizePicks”),
“Underdog”:   other_errs.get(“Underdog”),
“Fliff”:      other_errs.get(“Fliff”),
“Betr”:       other_errs.get(“Betr”),
}

scols = st.columns(5)
book_icons = {“FanDuel”: “🔵”, “PrizePicks”: “🟢”, “Underdog”: “🔴”,
“Fliff”: “🟣”, “Betr”: “🟡”}
for i, (bk, err) in enumerate(books_status.items()):
dot_cls, label = status_dot(err)
count = sum(1 for p in (fd_props if bk == “FanDuel” else other_props)
if p.get(“book”, “”) == bk)
with scols[i]:
st.markdown(f”””
<div class="metric-card">
<h4>{book_icons.get(bk,’’)} {bk}</h4>
<div class="val" style="font-size:28px;color:{'#4cde80' if err is None else '#f5c842' if 'key' in str(err).lower() else '#fa3d5a'};">
{count if err is None else ‘—’}
</div>
<div style="font-family:'DM Mono',monospace;font-size:10px;
color:#3d4e73;margin-top:4px;">HR PROPS</div>
</div>
“””, unsafe_allow_html=True)

st.markdown(”<div style='height:8px'></div>”, unsafe_allow_html=True)

# ── No FD data → show helpful message ────────────────────────────────────────

if not fd_props:
st.markdown(”””
<div style="background:#12192e;border:1px solid #2a3a5a;border-radius:12px;
padding:28px 32px;text-align:center;margin:20px 0;">
<div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:#4cafde;
letter-spacing:2px;margin-bottom:12px;">
🔑 ODDS API KEY REQUIRED FOR FANDUEL FAIR VALUE
</div>
<div style="font-family:'DM Sans',sans-serif;font-size:14px;color:#6a7a9a;
max-width:480px;margin:0 auto;line-height:1.7;">
Enter your free key from
<a href="https://the-odds-api.com" target="_blank"
style="color:#4cafde;">the-odds-api.com</a>
in the sidebar.<br>
Free tier includes 500 requests/month — enough for daily use.<br><br>
PrizePicks and Underdog props are shown below (no key needed).
</div>
</div>
“””, unsafe_allow_html=True)

```
# Show raw PrizePicks / Underdog props even without FD key
raw_df = pd.DataFrame([p for p in other_props if p["book"] in ("PrizePicks","Underdog")])
if not raw_df.empty:
    st.markdown("### 📋 Available HR Props (no fair value yet)")
    st.markdown("<div class='table-wrap'>", unsafe_allow_html=True)
    header = """<div class="ev-row header">
        <div>#</div><div>PLAYER</div><div>BOOK</div>
        <div>LINE</div><div>TYPE</div><div>ODDS</div><div>NOTE</div>
    </div>"""
    st.markdown(header, unsafe_allow_html=True)
    for i, row in raw_df.iterrows():
        st.markdown(f"""
        <div class="ev-row">
            <div class="rank">{i+1}</div>
            <div>
                <div class="player-name">{row['player'].title()}</div>
                <div class="player-team">{row.get('team','')}</div>
            </div>
            <div>{book_badge(row['book'])}</div>
            <div class="odds-mono">{row['line']:.1f}</div>
            <div class="odds-mono">{row.get('line_type','Over')}</div>
            <div class="odds-mono">{fmt_odds(row['odds'])}</div>
            <div style="font-size:11px;color:#3d4e73;font-family:'DM Mono'">
                ADD FD KEY FOR EV
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
```

else:
# ── Build EV table ────────────────────────────────────────────────────────
ev_df = build_ev_table(fd_props, other_props)

```
# Filter by min_ev
if not ev_df.empty:
    ev_df = ev_df[ev_df["ev"] >= min_ev].head(10).reset_index(drop=True)

# ── Summary metrics ───────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
total_props = len(fd_props) + len(other_props)
pos_ev      = len(ev_df) if not ev_df.empty else 0
best_ev     = ev_df["ev"].max() if not ev_df.empty else 0
best_grade  = ev_df["grade"].iloc[0] if not ev_df.empty else "—"

for col, label, val, color in [
    (m1, "TOTAL PROPS SCANNED",  total_props,              "#9aa8c8"),
    (m2, "POSITIVE EV PICKS",    pos_ev,                   "#4cde80"),
    (m3, f"BEST EV",             f"+{best_ev:.1%}",        "#f5c842"),
    (m4, "TOP GRADE",            best_grade,               "#4cafde"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <h4>{label}</h4>
            <div class="val" style="color:{color};">{val}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── EV Table ──────────────────────────────────────────────────────────────
if ev_df.empty:
    st.markdown("""
    <div style="background:#12192e;border:1px dashed #1e2740;border-radius:12px;
                padding:40px;text-align:center;color:#3d4e73;">
        <div style="font-size:40px;margin-bottom:12px;">🔍</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:22px;
                    letter-spacing:2px;margin-bottom:8px;">NO POSITIVE EV PICKS FOUND</div>
        <div style="font-size:13px;">Try lowering the EV threshold or check back later.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <h2 style="margin-bottom:4px;">🔥 TOP {len(ev_df)} EV PLAYS</h2>
    <p style="color:#3d4e73;font-family:'DM Mono',monospace;font-size:10px;
              letter-spacing:1.5px;">
        RANKED BY EXPECTED VALUE VS FANDUEL NO-VIG FAIR PROBABILITY
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<div class='table-wrap'>", unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="ev-row header">
        <div>#</div>
        <div>PLAYER</div>
        <div>BOOK</div>
        <div>ODDS</div>
        <div>FD LINE</div>
        <div>FAIR PROB</div>
        <div>EV / GRADE</div>
    </div>
    """, unsafe_allow_html=True)

    for i, row in ev_df.iterrows():
        rank_cls = "rank top3" if i < 3 else "rank"
        fd_o     = fmt_odds(row["fd_over"])  if row["fd_over"]  else "—"
        fd_u     = fmt_odds(row["fd_under"]) if row["fd_under"] else "—"
        fd_str   = f'{fd_o} / {fd_u}'
        ev_pct   = f"+{row['ev']*100:.1f}%"
        ev_cls_  = ev_class(row["ev"])
        oc       = odds_class(row["odds"])

        st.markdown(f"""
        <div class="ev-row">
            <div class="{rank_cls}">{i+1}</div>
            <div>
                <div class="player-name">{row['player']}</div>
                <div class="player-team">{row.get('team','') + ' · ' if row.get('team') else ''}{row['line_type'].upper()} {row['line']:.1f} HR</div>
            </div>
            <div>{book_badge(row['book'])}</div>
            <div class="odds-mono {oc}">{fmt_odds(row['odds'])}</div>
            <div class="fair-prob" style="font-size:12px;">{fd_str}</div>
            <div class="fair-prob">{fmt_pct(row['fair_prob'])}</div>
            <div>
                <span class="ev-pill {ev_cls_}">{ev_pct}</span>
                <span class="grade" style="color:{'#f5c842' if row['grade'].startswith('A') else '#9aa8c8'};
                      font-size:14px;margin-left:6px;">{row['grade']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── EV bar chart ──────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("### 📊 EV Breakdown")

    chart_df = ev_df[["player", "ev", "book"]].copy()
    chart_df["label"] = chart_df["player"] + " (" + chart_df["book"].str[:2].str.upper() + ")"
    chart_df["ev_pct"] = chart_df["ev"] * 100

    import altair as alt
    chart = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("label:N", sort="-y",
                     axis=alt.Axis(labelColor="#6a7a9a", labelFontSize=11,
                                   titleColor="#3d4e73", title="Player (Book)",
                                   labelAngle=-30)),
            y=alt.Y("ev_pct:Q",
                     axis=alt.Axis(labelColor="#6a7a9a", labelFontSize=11,
                                   titleColor="#3d4e73", title="EV (%)")),
            color=alt.condition(
                alt.datum.ev_pct >= 6,
                alt.value("#3dfa8c"),
                alt.condition(alt.datum.ev_pct >= 2,
                              alt.value("#8dde4c"),
                              alt.value("#de8c4c"))
            ),
            tooltip=["label", alt.Tooltip("ev_pct:Q", format=".2f", title="EV %")],
        )
        .properties(height=260, background="#0d1221")
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#1e2740", domainColor="#1e2740")
    )
    st.altair_chart(chart, use_container_width=True)
```

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown(”””

<div style="margin-top:40px;padding:16px;text-align:center;
            border-top:1px solid #1e2740;">
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#2a3a5a;
                letter-spacing:1.5px;">
        FOR INFORMATIONAL PURPOSES ONLY · NOT FINANCIAL OR GAMBLING ADVICE ·
        DATA MAY BE DELAYED · VERIFY LINES BEFORE BETTING
    </div>
</div>
""", unsafe_allow_html=True)
