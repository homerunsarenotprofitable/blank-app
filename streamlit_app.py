import requests
import pandas as pd
import streamlit as st
import numpy as np
from itertools import combinations

# -------------------------
# CONFIG
# -------------------------
API_KEY = "2cbb0724119f3699ff79ba1834553df1"
PRIMARY_BOOK = "fanduel"  # market truth anchor

st.set_page_config(layout="wide")
st.title("⚾ HR EV Engine (Market Truth + Kelly + Correlation)")

# -------------------------
# SIDEBAR SETTINGS
# -------------------------
st.sidebar.header("Settings")

payout = st.sidebar.selectbox(
    "Pick'em Payout",
    {"2-pick (3x)": 3.0, "3-pick (6x)": 6.0, "4-pick (10x)": 10.0}
)

kelly_fraction = st.sidebar.slider("Kelly Fraction", 0.1, 1.0, 0.5)
bankroll = st.sidebar.number_input("Bankroll ($)", value=1000)

min_ev = st.sidebar.slider("Min EV % Filter", -10, 20, 0)

# -------------------------
# FETCH DATA
# -------------------------
@st.cache_data(ttl=60)
def fetch_data():
    url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
    params = {
        "apiKey": API_KEY,
        "markets": "player_home_runs",
        "regions": "us",
        "oddsFormat": "american"
    }
    return requests.get(url, params=params).json()

data = fetch_data()

# -------------------------
# PARSE SHARP BOOK ONLY
# -------------------------
rows = []

for game in data:
    matchup = f"{game.get('home_team')} vs {game.get('away_team')}"

    for bookmaker in game.get("bookmakers", []):
        if bookmaker["key"] == PRIMARY_BOOK:
            for market in bookmaker["markets"]:
                for outcome in market["outcomes"]:
                    odds = outcome["price"]

                    if odds > 0:
                        implied = 100 / (odds + 100)
                    else:
                        implied = -odds / (-odds + 100)

                    rows.append({
                        "Player": outcome["name"],
                        "Game": matchup,
                        "Odds": odds,
                        "Implied": implied
                    })

df = pd.DataFrame(rows)

# -------------------------
# TRUE PROBABILITY (DE-VIG)
# -------------------------
# Conservative HR adjustment
df["True Prob"] = df["Implied"] * 0.96

# -------------------------
# EV CALCULATION
# -------------------------
df["EV"] = (df["True Prob"] * payout) - 1
df["EV %"] = df["EV"] * 100

# -------------------------
# KELLY CRITERION
# -------------------------
b = payout - 1

df["Kelly %"] = ((b * df["True Prob"] - (1 - df["True Prob"])) / b)
df["Kelly %"] = df["Kelly %"].clip(lower=0)

df["Adj Kelly %"] = df["Kelly %"] * kelly_fraction

df["Bet $"] = df["Adj Kelly %"] * bankroll
df["Units"] = df["Bet $"] / 100  # 1 unit = $100

# -------------------------
# FILTER
# -------------------------
df = df[df["EV %"] >= min_ev]

# -------------------------
# CORRELATION MODEL
# -------------------------
def correlation_penalty(picks):
    penalty = 0

    for a, b in combinations(picks, 2):
        if a["Game"] == b["Game"]:
            penalty += 0.15  # same game correlation

    return penalty

def parlay_ev(picks):
    prob = np.prod([p["True Prob"] for p in picks])
    penalty = correlation_penalty(picks)

    adj_prob = prob * (1 - penalty)
    return (adj_prob * payout) - 1

# -------------------------
# PARLAY OPTIMIZER
# -------------------------
top_candidates = df.sort_values("EV %", ascending=False).head(20)

best_combo = None
best_ev = -999

for combo in combinations(top_candidates.to_dict("records"), 2):
    ev = parlay_ev(combo)

    if ev > best_ev:
        best_ev = ev
        best_combo = combo

# -------------------------
# DISPLAY
# -------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Top HR Probability")
    st.dataframe(
        df.sort_values("True Prob", ascending=False)
        [["Player", "Game", "Odds", "True Prob"]]
        .head(10),
        use_container_width=True
    )

with col2:
    st.subheader("💰 Top EV + Kelly")
    st.dataframe(
        df.sort_values("EV %", ascending=False)
        [["Player", "EV %", "True Prob", "Units"]]
        .head(10),
        use_container_width=True
    )

# -------------------------
# BEST PARLAY
# -------------------------
st.subheader("🧠 Best Parlay (Correlation Adjusted)")

if best_combo:
    for pick in best_combo:
        st.write(f"{pick['Player']} — {pick['Game']}")

    st.write(f"Parlay EV: {best_ev:.2%}")

# -------------------------
# INSIGHTS
# -------------------------
st.markdown("### 📊 Insights")

st.write(f"Avg HR Prob: {df['True Prob'].mean():.2%}")
st.write(f"% Positive EV: {(df['EV'] > 0).mean():.2%}")
st.write(f"Avg Bet Size: {df['Units'].mean():.2f} units")
