import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="HR Prop EV + Kelly", layout="wide")

st.title("⚾ HR Prop EV + Kelly Tool")

# -----------------------
# CONFIG
# -----------------------
API_KEY = st.secrets["API_KEY"]

SPORT = "baseball_mlb"
REGION = "us"
MARKET = "batter_home_runs"
BOOKS = ["fanduel", "draftkings", "caesars", "betmgm"]

UNIT_SIZE = 100  # $100 = 1 unit

# -----------------------
# ODDS FUNCTIONS
# -----------------------
def american_to_prob(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


def prob_to_american(prob):
    if prob >= 0.5:
        return - (prob / (1 - prob)) * 100
    else:
        return ((1 - prob) / prob) * 100


def calculate_ev(prob, odds):
    if odds > 0:
        payout = odds / 100
    else:
        payout = 100 / abs(odds)
    return prob * payout - (1 - prob)


def kelly_fraction(prob, odds):
    if odds > 0:
        b = odds / 100
    else:
        b = 100 / abs(odds)

    k = (prob * (b + 1) - 1) / b
    return max(k, 0)


# -----------------------
# FETCH DATA
# -----------------------
@st.cache_data(ttl=60)
def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "bookmakers": ",".join(BOOKS),
        "oddsFormat": "american"
    }
    res = requests.get(url, params=params)
    return res.json()


data = fetch_odds()

# -----------------------
# PARSE DATA
# -----------------------
players = {}

for game in data:
    for book in game["bookmakers"]:
        book_name = book["key"]

        for market in book["markets"]:
            if market["key"] != MARKET:
                continue

            for outcome in market["outcomes"]:
                player = outcome["name"]
                odds = outcome["price"]

                if player not in players:
                    players[player] = {}

                players[player][book_name] = odds

# -----------------------
# SETTINGS
# -----------------------
st.sidebar.header("Settings")

min_ev = st.sidebar.slider("Min EV %", -5.0, 20.0, 2.0)
min_kelly = st.sidebar.slider("Min Kelly Units", 0.0, 0.5, 0.02)
kelly_fraction_scale = st.sidebar.selectbox(
    "Kelly Fraction",
    options=[1, 0.5, 0.25],
    format_func=lambda x: f"{x}x",
    index=2
)

# -----------------------
# BUILD DATAFRAME
# -----------------------
rows = []

for player, books in players.items():
    if len(books) < 2:
        continue

    probs = [american_to_prob(o) for o in books.values()]

    total = sum(probs)
    devig_probs = [p / total for p in probs]

    fair_prob = sum(devig_probs) / len(devig_probs)
    fair_odds = prob_to_american(fair_prob)

    for book, odds in books.items():
        ev = calculate_ev(fair_prob, odds)

        kelly = kelly_fraction(fair_prob, odds) * kelly_fraction_scale

        rows.append({
            "Player": player,
            "Book": book,
            "Odds": odds,
            "Fair Odds": round(fair_odds, 0),
            "Fair Prob": round(fair_prob, 4),
            "EV %": round(ev * 100, 2),
            "Kelly Units": round(kelly, 3),
            "Bet ($)": round(kelly * UNIT_SIZE, 2)
        })

df = pd.DataFrame(rows)

# -----------------------
# FILTER
# -----------------------
filtered = df[
    (df["EV %"] >= min_ev) &
    (df["Kelly Units"] >= min_kelly)
]

# -----------------------
# DISPLAY
# -----------------------
st.dataframe(
    filtered.sort_values("Kelly Units", ascending=False),
    use_container_width=True
)

# -----------------------
# TOP BETS
# -----------------------
st.subheader("🔥 Top Bets")

top = filtered.sort_values("Kelly Units", ascending=False).head(10)

for _, row in top.iterrows():
    st.write(
        f"{row['Player']} | {row['Book']} | "
        f"{row['Odds']} | EV: {row['EV %']}% | "
        f"{row['Kelly Units']}u (${row['Bet ($)']})"
    )
