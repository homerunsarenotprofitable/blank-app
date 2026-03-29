import streamlit as st
import pandas as pd
import itertools
import requests

st.set_page_config(page_title="HR DFS EV Engine", layout="wide")

st.title("⚾ HR DFS +EV Engine (Market-Based)")

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "2cbb0724119f3699ff79ba1834553df1"

# -----------------------------
# FUNCTIONS
# -----------------------------
def american_to_prob(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

def calculate_ev(prob, payout):
    return (prob * payout) - 1

def parlay_ev(probs, payout):
    win_prob = 1
    for p in probs:
        win_prob *= p
    ev = (win_prob * payout) - 1
    return win_prob, ev

def kelly(win_prob, payout):
    b = payout - 1
    p = win_prob
    q = 1 - p

    if b == 0:
        return 0

    k = (b * p - q) / b
    k = max(0, k)
    k = min(k, 0.25)
    return k

# -----------------------------
# FETCH ODDS (SPORTBOOKS)
# -----------------------------
def fetch_odds():
    url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/"
    
    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "player_home_runs",
        "oddsFormat": "american"
    }

    r = requests.get(url, params=params)
    if r.status_code != 200:
        return []

    data = r.json()
    rows = []

    for game in data:
        for book in game.get("bookmakers", []):
            book_name = book["key"]

            for market in book.get("markets", []):
                if market["key"] == "player_home_runs":
                    for outcome in market["outcomes"]:
                        rows.append({
                            "Player": outcome["description"],
                            "Odds": outcome["price"],
                            "Sportsbook": book_name,
                            "Game": game.get("home_team","") + " vs " + game.get("away_team","")
                        })

    return rows

# -----------------------------
# PROCESS MARKET PROBABILITIES
# -----------------------------
def build_market_probs(data):
    df = pd.DataFrame(data)
    df["Prob"] = df["Odds"].apply(american_to_prob)

    grouped = df.groupby("Player").agg({
        "Prob": "mean",
        "Game": "first"
    }).reset_index()

    grouped = grouped.rename(columns={"Prob": "HR Probability"})
    return grouped

# -----------------------------
# DFS INPUT (MANUAL)
# -----------------------------
def get_dfs_lines(players):
    st.subheader("🎯 Enter DFS Lines (PrizePicks / Underdog)")

    dfs_data = []

    for player in players:
        line = st.number_input(f"{player} HR Line (0.5)", 0.0, 2.0, 0.5, key=player)

        dfs_data.append({
            "Player": player,
            "DFS Line": line
        })

    return pd.DataFrame(dfs_data)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs(["📊 Market Data", "⚖️ DFS Comparison", "🤖 Optimizer"])

# -----------------------------
# TAB 1: MARKET DATA
# -----------------------------
with tab1:
    if st.button("Pull Live HR Odds"):
        raw = fetch_odds()

        if raw:
            df = build_market_probs(raw)
            df = df.sort_values(by="HR Probability", ascending=False)

            st.session_state["df"] = df

            st.subheader("🏆 Market HR Probabilities")
            st.dataframe(df)

            st.subheader("🔥 Top 10")
            st.dataframe(df.head(10))
        else:
            st.error("Failed to fetch odds")

# -----------------------------
# TAB 2: DFS COMPARISON
# -----------------------------
with tab2:
    if "df" not in st.session_state:
        st.warning("Pull market data first")
    else:
        df = st.session_state["df"]

        dfs_df = get_dfs_lines(df["Player"].tolist())

        merged = df.merge(dfs_df, on="Player")

        # Assume DFS 0.5 HR = binary event
        # Approx implied probability threshold ~ 57.7% for 2-pick
        dfs_prob = 0.577

        merged["Edge"] = merged["HR Probability"] - dfs_prob

        st.subheader("⚖️ DFS Edge Comparison")
        st.dataframe(merged.sort_values(by="Edge", ascending=False))

        st.session_state["merged"] = merged

# -----------------------------
# TAB 3: OPTIMIZER
# -----------------------------
with tab3:
    if "merged" not in st.session_state:
        st.warning("Complete DFS comparison first")
    else:
        df = st.session_state["merged"]

        num_picks = st.selectbox("Parlay Size", [2, 3, 4])
        payout_map = {2: 3, 3: 5, 4: 10}
        payout = payout_map[num_picks]

        bankroll = st.number_input("Bankroll (units)", 1.0, 1000.0, 10.0)
        unit_size = 100

        top_n = st.slider("Use Top N Players", 5, 15, 10)

        data = df.sort_values(by="HR Probability", ascending=False).head(top_n)

        combos = itertools.combinations(data.to_dict('records'), num_picks)

        results = []

        for combo in combos:
            players = [p["Player"] for p in combo]
            probs = [p["HR Probability"] for p in combo]

            win_prob, ev = parlay_ev(probs, payout)
            k = kelly(win_prob, payout)

            results.append({
                "Players": ", ".join(players),
                "Win Prob": win_prob,
                "EV": ev,
                "Kelly %": k,
                "Units": k * bankroll,
                "Bet ($)": k * bankroll * unit_size
            })

        results_df = pd.DataFrame(results)

        if not results_df.empty:
            results_df = results_df.sort_values(by="EV", ascending=False)

            st.subheader("🔥 Best Combos")
            st.dataframe(results_df.head(10))

            st.subheader("✅ +EV Only")
            st.dataframe(results_df[results_df["EV"] > 0])
