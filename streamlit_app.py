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

# ✅ KEEP RAW COPY FOR TEST TAB
ev_raw = ev.copy()

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

        # ✅ Correct EV formula
        ev["EV"] = ev["baseline_prob"] * (ev["decimal_odds"] - 1) - (1 - ev["baseline_prob"])

        # Filter +EV
        ev = ev[ev["EV"] >= 0.05]

# --- KELLY FUNCTION ---
def kelly_fraction(prob, decimal_odds):
    b = decimal_odds - 1
    if b <= 0:
        return 0
    f = (b * prob - (1 - prob)) / b
    return max(f, 0)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5, tab_test = st.tabs([
    "🔥 Top 10 Props",
    "🧩 Slate Builder",
    "💡 Suggested Slates",
    "📊 Performance",
    "📜 History",
    "🧪 Test Odds"
])

# =========================
# 🔥 TOP 10
# =========================
with tab1:
    st.header("🔥 Top 10 Single +EV Props")

    if not ev.empty:
        top10 = ev.sort_values("EV", ascending=False).head(10)

        def ev_bar(val):
            width = min(int(val * 500), 100)
            color = "#00ff99" if val >= 0.1 else "#ccffcc"
            return f"background: linear-gradient(90deg, {color} {width}%, transparent {width}%); font-weight:bold;"

        st.dataframe(
            top10[["player", "book", "prop", "decimal_odds", "EV"]]
            .style.applymap(ev_bar, subset=["EV"]),
            use_container_width=True
        )
    else:
        st.info("No +EV DFS props currently available")

# =========================
# 🧩 SLATE BUILDER
# =========================
with tab2:
    st.header("🧩 Slate Builder")

    if not ev.empty:
        labels = ev["player"] + " | " + ev["prop"]

        selections = st.multiselect("Select picks", labels)

        payout = st.number_input("Payout multiplier", value=2.0, min_value=1.0, step=0.1)

        if selections:
            selected_rows = ev[labels.isin(selections)]

            probs = selected_rows["baseline_prob"].tolist()

            combined_prob = 1
            for p in probs:
                combined_prob *= p

            slate_ev = combined_prob * (payout - 1) - (1 - combined_prob)
            units = kelly_fraction(combined_prob, payout)

            st.metric("Combined Probability", f"{round(combined_prob*100,2)}%")
            st.metric("Slate EV", f"{round(slate_ev,4)}")
            st.metric("Suggested Units", f"{round(units,4)}")
        else:
            st.info("Select picks")
    else:
        st.info("No +EV picks available")

# =========================
# 💡 SUGGESTED SLATES
# =========================
with tab3:
    st.header("💡 Suggested Slates")

    if not ev.empty:
        top_picks = ev.sort_values("EV", ascending=False).head(10)
        labels = top_picks["player"] + " | " + top_picks["prop"]

        max_size = st.slider("Max picks", 2, 5, 3)
        payout = st.number_input("Payout", value=2.0, key="payout2")

        slates = []

        for r in range(2, max_size + 1):
            for combo in combinations(labels, r):
                probs = []

                for c in combo:
                    prob = top_picks[
                        (top_picks["player"] + " | " + top_picks["prop"]) == c
                    ]["baseline_prob"].values[0]

                    probs.append(prob)

                combined_prob = 1
                for p in probs:
                    combined_prob *= p

                slate_ev = combined_prob * (payout - 1) - (1 - combined_prob)
                units = kelly_fraction(combined_prob, payout)

                slates.append({
                    "Slate": combo,
                    "Prob %": round(combined_prob*100,2),
                    "EV": round(slate_ev,4),
                    "Units": round(units,4)
                })

        df = pd.DataFrame(slates).sort_values("EV", ascending=False).head(5)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data")

# =========================
# 📊 PERFORMANCE
# =========================
with tab4:
    st.header("📊 Performance")

    if not history.empty:
        history = history.dropna(subset=["profit"])

        profit = history["profit"].sum()
        staked = history["stake"].sum()
        roi = profit / staked if staked > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Profit", f"${round(profit,2)}")
        c2.metric("Staked", f"${round(staked,2)}")
        c3.metric("ROI", f"{round(roi*100,2)}%")

        history["date"] = pd.to_datetime(history["date"])
        history = history.sort_values("date")
        history["cum"] = history["profit"].cumsum()

        st.line_chart(history.set_index("date")["cum"])
        st.bar_chart(history.groupby("book")["profit"].sum())
    else:
        st.info("No history")

# =========================
# 📜 HISTORY
# =========================
with tab5:
    st.header("📜 History")

    if not history.empty:
        books = st.multiselect("Books", history["book"].unique())

        df = history.copy()
        if books:
            df = df[df["book"].isin(books)]

        st.dataframe(df.sort_values("date", ascending=False))
    else:
        st.info("No data")

# =========================
# 🧪 TEST TAB (FIXED)
# =========================
with tab_test:
    st.header("🧪 Raw Odds Preview")

    if not ev_raw.empty:
        st.write("Raw rows:", len(ev_raw))
        st.write("Filtered (+EV) rows:", len(ev))
        st.dataframe(ev_raw.head(5), use_container_width=True)
    else:
        st.info("No odds data loaded from live_ev.csv")
