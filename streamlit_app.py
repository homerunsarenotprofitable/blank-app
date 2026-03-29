import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EV Dashboard", layout="wide")

# --- AUTO REFRESH ---
st.markdown(
    """
    <meta http-equiv="refresh" content="60">
    """,
    unsafe_allow_html=True
)

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

# --- NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["🔥 Live EV", "📊 Performance", "📜 History"])

# =========================
# 🔥 LIVE EV TAB
# =========================
with tab1:
    st.header("🔥 Live +EV HR Bets")

    if not ev.empty:
        ev = ev.sort_values("ev", ascending=False)

        st.dataframe(
            ev,
            use_container_width=True
        )
    else:
        st.info("No +EV bets right now")

# =========================
# 📊 PERFORMANCE TAB
# =========================
with tab2:
    st.header("📊 Performance")

    if not history.empty:

        history = history.dropna(subset=["profit"])

        total_profit = history["profit"].sum()
        total_staked = history["stake"].sum()
        roi = total_profit / total_staked if total_staked > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Profit", f"${round(total_profit,2)}")
        col2.metric("Staked", f"${round(total_staked,2)}")
        col3.metric("ROI", f"{round(roi*100,2)}%")

        # Profit curve
        history["date"] = pd.to_datetime(history["date"])
        history = history.sort_values("date")
        history["cum_profit"] = history["profit"].cumsum()

        fig = px.line(history, x="date", y="cum_profit", title="Profit Over Time")
        st.plotly_chart(fig, use_container_width=True)

        # CLV
        if "closing_odds" in history.columns:
            history["clv"] = history["closing_odds"] - history["odds"]
            st.metric("Avg CLV", round(history["clv"].mean(), 2))

        # By book
        st.subheader("Profit by Book")
        fig2 = px.bar(history, x="book", y="profit")
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("No bet history yet")

# =========================
# 📜 HISTORY TAB
# =========================
with tab3:
    st.header("📜 Bet History")

    if not history.empty:

        # Filters
        books = st.multiselect("Filter by book", history["book"].unique())

        df = history.copy()

        if books:
            df = df[df["book"].isin(books)]

        st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)

    else:
        st.info("No data yet")
