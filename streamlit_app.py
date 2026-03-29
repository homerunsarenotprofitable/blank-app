import streamlit as st
import requests
import pandas as pd

API_KEY = "2cbb0724119f3699ff79ba1834553df1"

st.set_page_config(page_title="HR EV Finder", layout="wide")

st.title("⚾ Home Run EV Finder (Market-Based)")
st.caption("Using FanDuel, DraftKings, BetMGM as fair value")

# --- Functions ---
def american_to_prob(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

@st.cache_data(ttl=60)
def fetch_odds():
    url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/"
    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "player_home_runs",
        "oddsFormat": "american"
    }
    res = requests.get(url, params=params)
    return res.json()

data = fetch_odds()

# --- Process Data ---
players = {}

for game in data:
    for book in game["bookmakers"]:
        if book["key"] not in ["fanduel", "draftkings", "betmgm"]:
            continue

        for market in book["markets"]:
            for outcome in market["outcomes"]:
                name = outcome["name"]
                odds = outcome["price"]
                prob = american_to_prob(odds)

                players.setdefault(name, []).append(prob)

# --- Build Results ---
rows = []

for player, probs in players.items():
    if len(probs) < 2:
        continue

    avg_prob = sum(probs) / len(probs)
    under_prob = 1 - avg_prob

    # Compare to 2-pick PrizePicks break-even (~57.7%)
    edge = under_prob - 0.577

    rows.append({
        "Player": player,
        "HR Probability": round(avg_prob, 3),
        "Under Probability": round(under_prob, 3),
        "Edge vs 2-Pick": round(edge, 3)
    })

df = pd.DataFrame(rows)
df = df.sort_values(by="Under Probability", ascending=False)

# --- Filters ---
min_edge = st.slider("Minimum Edge", 0.0, 0.5, 0.05)

filtered_df = df[df["Edge vs 2-Pick"] > min_edge]

# --- Display ---
st.subheader("🔥 Best Under 0.5 HR Plays")
st.dataframe(filtered_df, use_container_width=True)

# --- Top Picks ---
st.subheader("⭐ Top 10 Plays")
st.table(filtered_df.head(10))
