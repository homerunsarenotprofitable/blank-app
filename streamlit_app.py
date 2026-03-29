import streamlit as st
import pandas as pd
from itertools import combinations

st.set_page_config(page_title="DFS +EV Dashboard", layout="wide")

# --- AUTO REFRESH ---
st.markdown('<meta http-equiv="refresh" content="60">', unsafe_allow_html=True)

# --- LOAD DATA ---
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

history, ev = load_data()

# --- CONVERT ODDS TO IMPLIED PROBABILITY ---
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
        ev = ev.merge(
            baseline[["player", "implied_prob"]].rename(columns={"implied_prob": "baseline_prob"}),
            on="player",
            how="left"
        )

        # ✅ FIXED EV FORMULA
        ev["EV"] = ev["baseline_prob"] * (ev["decimal_odds"] - 1) - (1 - ev["baseline_prob"])

        # Filter for +EV picks
        ev = ev[ev["EV"] >= 0.05]

# --- KELLY FUNCTION (FIXED) ---
def kelly_fraction(prob, decimal_odds):
    b = decimal_odds - 1
    if b <= 0:
        return 0
    f = (b * prob - (1 - prob)) / b
    return max(f, 0)

# --- NAVIGATION ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 Top 10 Props",
    "🧩 Slate Builder",
    "💡 Suggested Slates",
    "📊 Performance",
    "📜 History"
])

# =========================
# 🔥 TOP 10 SINGLE PROPS
# =========================
with tab1:
    st.header("🔥 Top 10 Single +EV Props")

    if not ev.empty:
        top10 = ev.sort_values("EV", ascending=False).head(10)

        def ev_bar(val):
            width = min(int(val * 500), 100)
            color = "#00ff99" if val >= 0.1 else "#ccffcc"
            return f"background: linear-gradient(90deg, {color} {width}%, transparent {width}%); font-weight:bold;"

        display_cols = ["player", "book", "prop", "decimal_odds", "EV"]

        st.dataframe(
            top10[display_cols].style.applymap(ev_bar, subset=["EV"]),
            use_container_width=True
        )
    else:
        st.info("No +EV DFS props currently available")

# =========================
# 🧩 SLATE BUILDER
# =========================
with tab2:
    st.header("🧩 Slate Builder (Manual)")

    if not ev.empty:
        label_series = ev["player"] + " | " + ev["prop"]

        selections = st.multiselect(
            "Select picks for your slate",
            label_series,
            default=[]
        )

        slate_payout = st.number_input(
            "Enter slate payout multiplier",
            value=2.0,
            min_value=1.0,
            step=0.1
        )

        if selections:
            # ✅ FIXED FILTERING
            selected_rows = ev[label_series.isin(selections)]

            probs = selected_rows["baseline_prob"].tolist()

            combined_prob = 1
            for p in probs:
                combined_prob *= p

            # EV (same corrected logic)
            slate_ev = combined_prob * (slate_payout - 1) - (1 - combined_prob)

            # ✅ FIXED KELLY
            suggested_units = kelly_fraction(combined_prob, slate_payout)

            st.metric("Combined Probability", f"{round(combined_prob * 100, 2)}%")
            st.metric("Slate EV", f"{round(slate_ev, 4)}")
            st.metric("Suggested Units", f"{round(suggested_units, 4)}")
        else:
            st.info("Select 2–10 picks to calculate slate EV")
    else:
        st.info("No +EV picks to build a slate")

# =========================
# 💡 SUGGESTED SLATES
# =========================
with tab3:
    st.header("💡 Suggested Slates (Auto +EV with Units)")

    if not ev.empty:
        top_picks = ev.sort_values("EV", ascending=False).head(10)

        label_series = top_picks["player"] + " | " + top_picks["prop"]

        max_slate_size = st.slider("Max picks per slate", 2, 5, value=3)

        slate_payout = st.number_input(
            "Enter slate payout multiplier for suggestions",
            value=2.0,
            min_value=1.0,
            step=0.1,
            key="suggestion_payout"
        )

        slates = []

        for r in range(2, max_slate_size + 1):
            for combo in combinations(label_series, r):
                probs = []

                for c in combo:
                    # ✅ FIXED FILTERING
                    prob = top_picks[
                        (top_picks["player"] + " | " + top_picks["prop"]) == c
                    ]["baseline_prob"].values[0]

                    probs.append(prob)

                combined_prob = 1
                for p in probs:
                    combined_prob *= p

                slate_ev = combined_prob * (slate_payout - 1) - (1 - combined_prob)

                suggested_units = kelly_fraction(combined_prob, slate_payout)

                slates.append({
                    "Slate": combo,
                    "Combined Prob": round(combined_prob * 100, 2),
                    "Slate EV": round(slate_ev, 4),
                    "Suggested Units": round(suggested_units, 4)
                })

        slate_df = pd.DataFrame(slates).sort_values("Slate EV", ascending=False).head(5)

        st.dataframe(slate_df, use_container_width=True)
    else:
        st.info("No +EV picks available for suggestions")

# =========================
# 📊 PERFORMANCE TAB
# =========================
with tab4:
    st.header("📊 Performance")

    if not history.empty:
        history = history.dropna(subset=["profit"])

        total_profit = history["profit"].sum()
        total_staked = history["stake"].sum()

        roi = total_profit / total_staked if total_staked > 0 else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Profit", f"${round(total_profit, 2)}")
        col2.metric("Total Staked", f"${round(total_staked, 2)}")
        col3.metric("ROI", f"{round(roi * 100, 2)}%")

        history["date"] = pd.to_datetime(history["date"])
        history = history.sort_values("date")
        history["cum_profit"] = history["profit"].cumsum()

        st.line_chart(history.set_index("date")["cum_profit"], use_container_width=True)

        st.subheader("Profit by Book")
        profit_by_book = history.groupby("book")["profit"].sum()

        st.bar_chart(profit_by_book, use_container_width=True)
    else:
        st.info("No bet history yet")

# =========================
# 📜 HISTORY TAB
# =========================
with tab5:
    st.header("📜 Bet History")

    if not history.empty:
        books = st.multiselect("Filter by book", history["book"].unique())

        df = history.copy()

        if books:
            df = df[df["book"].isin(books)]

        st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
    else:
        st.info("No data yet")

# =========================
# 🧪 TEST ODDS TAB
# =========================
tab_test = st.tab("🧪 Test Odds")

with tab_test:
    st.header("🧪 Raw Odds Preview (first 5 rows)")

    if not ev.empty:
        st.dataframe(ev.head(5), use_container_width=True)
    else:
        st.info("No odds data loaded from live_ev.csv")
