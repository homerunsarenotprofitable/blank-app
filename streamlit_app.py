import streamlit as st
import pandas as pd

st.set_page_config(page_title="EV Betting Dashboard", layout="wide")

# --- AUTO REFRESH every 60 seconds ---
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

# --- NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs(["🔥 Live EV", "📊 Performance", "📜 History"])

# =========================
# 🔥 LIVE EV TAB
# =========================
with tab1:
    st.header("🔥 Live +EV HR Bets")

    if not ev.empty:
        ev = ev.sort_values("ev", ascending=False)

        # Highlight EV
        def highlight_ev(val):
            if val >= 0.1:
                return "background-color: #00ff99"
            elif val >= 0.05:
                return "background-color: #ccffcc"
            return ""

        st.dataframe(ev.style.applymap(highlight_ev, subset=["ev"]), use_container_width=True)
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
        col1.metric("Total Profit", f"${round(total_profit,2)}")
        col2.metric("Total Staked", f"${round(total_staked,2)}")
        col3.metric("ROI", f"{round(roi*100,2)}%")

        # Profit curve
        history["date"] = pd.to_datetime(history["date"])
        history = history.sort_values("date")
        history["cum_profit"] = history["profit"].cumsum()

        st.line_chart(history.set_index("date")["cum_profit"], use_container_width=True)

        # CLV
        if "closing_odds" in history.columns:
            history["clv"] = history["closing_odds"] - history["odds"]
            st.metric("Avg CLV", round(history["clv"].mean(), 2))

        # Profit by Book
        st.subheader("Profit by Book")
        profit_by_book = history.groupby("book")["profit"].sum()
        st.bar_chart(profit_by_book, use_container_width=True)

        # Profit by EV Bucket
        st.subheader("Profit by EV Bucket")
        history["ev_bucket"] = pd.cut(history["ev"], bins=[0,0.05,0.1,0.2,1])
        profit_by_ev = history.groupby("ev_bucket")["profit"].sum()
        st.bar_chart(profit_by_ev, use_container_width=True)

    else:
        st.info("No bet history yet")

# =========================
# 📜 HISTORY TAB
# =========================
with tab3:
    st.header("📜 Bet History")

    if not history.empty:

        # Filter by book
        books = st.multiselect("Filter by book", history["book"].unique())
        df = history.copy()
        if books:
            df = df[df["book"].isin(books)]

        st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
    else:
        st.info("No data yet")
