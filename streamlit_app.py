import streamlit as st
import pandas as pd
from itertools import combinations

st.set_page_config(page_title="DFS +EV Dashboard", layout="wide")

# --- DATA LOADING FUNCTION ---
@st.cache_data(ttl=30)
def load_data():
    try:
        history = pd.read_csv("history.csv")
    except:
        history = pd.DataFrame()
    try:
        ev = pd.read_csv("live_ev.csv")
    except:
        ev = pd.DataFrame()
    return history, ev

# --- REFRESH BUTTON ---
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()  # Clear cache so data reloads
    st.experimental_rerun()  # Re-run the app to load new data

# --- LOAD DATA ---
history, ev = load_data()

# --- CONVERT DFS ODDS TO IMPLIED PROBABILITY ---
def convert_odds_to_prob(row):
    if "decimal_odds" in row and not pd.isna(row["decimal_odds"]):
        return 1 / row["decimal_odds"]
    elif "american_odds" in row and not pd.isna(row["american_odds"]):
        odds = row["american_odds"]
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    return None

if not ev.empty:
    ev["implied_prob"] = ev.apply(convert_odds_to_prob, axis=1)
    baseline = ev[ev["book"] == "fanduel"]
    if not baseline.empty:
        ev = ev.merge(baseline[["player","implied_prob"]].rename(columns={"implied_prob":"baseline_prob"}), on="player", how="left")
        ev["EV"] = ev["decimal_odds"] * ev["baseline_prob"] - (1 - ev["baseline_prob"])
        ev = ev[ev["EV"] >= 0.05]

# --- KELLY FUNCTION ---
def kelly_fraction(prob, payout):
    f = (payout * prob - (1 - prob)) / payout
    return max(f, 0)

# --- DASHBOARD TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔥 Top 10 Props", "🧩 Slate Builder", "💡 Suggested Slates", "📊 Performance", "📜 History"])

# The rest of your dashboard code remains the same as before
# Top 10 single props, Slate Builder, Suggested Slates with Kelly units, Performance, History
