import streamlit as st
import pandas as pd
import requests
import itertools

st.set_page_config(page_title="HR EV Finder", layout="wide")

st.title("⚾ MLB Home Run EV Dashboard (FanDuel Powered)")

# -----------------------------
# CONFIG
# -----------------------------

PICKEM_IMPLIED_PROB = st.sidebar.slider(
    "Pick'em Implied Probability",
    0.50, 0.60, 0.545, 0.001
)

MIN_EDGE = st.sidebar.slider("Minimum Edge Filter", 0.0, 0.10, 0.01, 0.005)

AUTO_REFRESH = st.sidebar.checkbox("Auto Refresh (30s)")

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


# 🔥 FanDuel scraper (unofficial endpoint)
def get_fanduel_hr_props():
    url = "https://sportsbook.fanduel.com/api/content-managed-page"
    
    params = {
        "page": "mlb",
        "includePrices": "true"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, params=params, headers=headers)

    if r.status_code != 200:
        st.error("Failed to fetch FanDuel data")
        return []

    return r.json()


def extract_hr_data(data):
    players = {}

    try:
        events = data.get("attachments", {}).get("events", {})
        markets = data.get("attachments", {}).get("markets", {})

        for market_id, market in markets.items():
            name = market.get("marketName", "").lower()

            # 🔥 filter HR markets
            if "home run" not in name:
                continue

            runners = market.get("runners", [])

            for runner in runners:
                player = runner.get("runnerName")
                odds = runner.get("winRunnerOdds", {}).get("americanDisplayOdds", {}).get("americanOdds")

                if not player or odds is None:
                    continue

                if player not in players:
                    players[player] = {"over": [], "under": []}

                # HR prop is binary: treat as "over"
                players[player]["over"].append(odds)

        return players

    except Exception as e:
        st.error(f"Parsing error: {e}")
        return {}


def calculate_ev(players_dict):
    rows = []

    for player, odds_dict in players_dict.items():
        if not odds_dict["over"]:
            continue

        avg_odds = sum(odds_dict["over"]) / len(odds_dict["over"])

        true_prob = american_to_prob(avg_odds)

        edge = true_prob - PICKEM_IMPLIED_PROB

        rows.append({
            "Player": player,
            "HR Odds": round(avg_odds, 0),
            "True HR Prob": round(true_prob, 4),
            "Edge": round(edge, 4),
            "EV+": edge > 0
        })

    df = pd.DataFrame(rows)
    return df.sort_values(by="Edge", ascending=False)


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
# MAIN FLOW
# -----------------------------

if st.button("🔄 Pull FanDuel HR Props") or AUTO_REFRESH:
    with st.spinner("Scraping FanDuel..."):
        raw_data = get_fanduel_hr_props()

        if not raw_data:
            st.stop()

        players = extract_hr_data(raw_data)

        if not players:
            st.warning("No HR props found")
            st.stop()

        df = calculate_ev(players)

        df = df[df["Edge"] > MIN_EDGE]

        st.session_state["data"] = df


# -----------------------------
# DISPLAY
# -----------------------------

if "data" in st.session_state:
    df = st.session_state["data"]

    st.subheader("📊 +EV Home Run Props")
    st.dataframe(df, use_container_width=True)

    st.subheader("🔥 Top Plays")
    st.dataframe(df.head(10), use_container_width=True)

    # -----------------------------
    # SLIPS
    # -----------------------------

    st.subheader("🧠 Best Slips")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate 2-Leg"):
            slips = generate_slips(df, 2)
            st.dataframe(slips.head(10), use_container_width=True)

    with col2:
        if st.button("Generate 3-Leg"):
            slips = generate_slips(df, 3)
            st.dataframe(slips.head(10), use_container_width=True)

else:
    st.info("Click to load FanDuel HR props")

# -----------------------------
# AUTO REFRESH
# -----------------------------

if AUTO_REFRESH:
    import time
    time.sleep(30)
    st.experimental_rerun()
