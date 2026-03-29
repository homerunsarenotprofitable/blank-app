import streamlit as st
import pandas as pd
import requests
import itertools

st.set_page_config(page_title="HR EV Finder", layout="wide")

st.title("⚾ MLB Home Run EV Dashboard")

# -----------------------------
# CONFIG
# -----------------------------

API_KEY = "2cbb0724119f3699ff79ba1834553df1"

SPORT = "baseball_mlb"
REGION = "us"
MARKET = "batter_home_runs"

PICKEM_IMPLIED_PROB = st.sidebar.slider(
    "Pick'em Implied Probability",
    0.50, 0.60, 0.545, 0.001
)

MIN_EDGE = st.sidebar.slider("Minimum Edge Filter", 0.0, 0.10, 0.01, 0.005)

# -----------------------------
# FUNCTIONS
# -----------------------------

def american_to_prob(odds):
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)


def remove_vig(p1, p2):
    total = p1 + p2
    return p1 / total, p2 / total


def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "american"
    }

    response = requests.get(url, params=params)
    return response.json()


def extract_hr_props(data):
    players = {}

    for game in data:
        for book in game["bookmakers"]:
            for market in book["markets"]:
                if market["key"] != "batter_home_runs":
                    continue

                for outcome in market["outcomes"]:
                    name = outcome["description"]  # player name
                    odds = outcome["price"]
                    label = outcome["name"]  # Over / Under

                    if name not in players:
                        players[name] = {"over": [], "under": []}

                    if label.lower() == "over":
                        players[name]["over"].append(odds)
                    else:
                        players[name]["under"].append(odds)

    return players


def calculate_ev(players_dict):
    rows = []

    for player, odds_dict in players_dict.items():
        if not odds_dict["over"] or not odds_dict["under"]:
            continue

        # Average across books
        avg_over_odds = sum(odds_dict["over"]) / len(odds_dict["over"])
        avg_under_odds = sum(odds_dict["under"]) / len(odds_dict["under"])

        over_prob = american_to_prob(avg_over_odds)
        under_prob = american_to_prob(avg_under_odds)

        true_over, true_under = remove_vig(over_prob, under_prob)

        edge_over = true_over - PICKEM_IMPLIED_PROB
        edge_under = true_under - PICKEM_IMPLIED_PROB

        best_edge = max(edge_over, edge_under)
        best_bet = "HR" if edge_over > edge_under else "No HR"

        rows.append({
            "Player": player,
            "True HR Prob": round(true_over, 4),
            "Edge HR": round(edge_over, 4),
            "Edge No HR": round(edge_under, 4),
            "Best Bet": best_bet,
            "Best Edge": round(best_edge, 4),
            "EV+": best_edge > 0
        })

    df = pd.DataFrame(rows)
    return df.sort_values(by="Best Edge", ascending=False)


def generate_slips(df, legs=2):
    ev_df = df[df["EV+"] == True]

    combos = list(itertools.combinations(ev_df.to_dict("records"), legs))

    slips = []

    for combo in combos:
        prob = 1
        players = []

        for leg in combo:
            prob *= leg["True HR Prob"]
            players.append(leg["Player"])

        # PrizePicks payout approximation
        payout_map = {2: 3, 3: 5}
        payout = payout_map.get(legs, 3)

        ev = (prob * payout) - 1

        slips.append({
            "Players": ", ".join(players),
            "Hit Prob": round(prob, 4),
            "Payout": payout,
            "Slip EV": round(ev, 4)
        })

    return pd.DataFrame(slips).sort_values(by="Slip EV", ascending=False)


# -----------------------------
# FETCH DATA
# -----------------------------

if st.button("🔄 Pull Live Odds"):
    with st.spinner("Fetching odds..."):
        raw_data = get_odds()
        players = extract_hr_props(raw_data)
        df = calculate_ev(players)

        df = df[df["Best Edge"] > MIN_EDGE]

        st.session_state["data"] = df

# -----------------------------
# DISPLAY RESULTS
# -----------------------------

if "data" in st.session_state:
    df = st.session_state["data"]

    st.subheader("📊 +EV Home Run Props")
    st.dataframe(df, use_container_width=True)

    # -----------------------------
    # SLIP BUILDER
    # -----------------------------

    st.subheader("🧠 Best Slips")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate 2-Leg Slips"):
            slips_2 = generate_slips(df, legs=2)
            st.dataframe(slips_2.head(10), use_container_width=True)

    with col2:
        if st.button("Generate 3-Leg Slips"):
            slips_3 = generate_slips(df, legs=3)
            st.dataframe(slips_3.head(10), use_container_width=True)

else:
    st.info("Click 'Pull Live Odds' to begin")

# -----------------------------
# FOOTER
# -----------------------------

st.markdown("""
### ⚠️ Notes
- Uses multi-book average for sharper probabilities
- Removes vig before EV calculation
- Pick’em apps approximated at ~54–56%
- HR bets are high variance — bankroll management matters

### 🚀 Future Upgrades
- PrizePicks scraping
- Line mismatch detection (HUGE edge)
- CLV tracking
- Auto-refresh odds
""")
