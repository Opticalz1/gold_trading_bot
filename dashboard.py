import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gold Trading Bot Dashboard", layout="wide")
st.title("📊 Gold Trading Bot Dashboard")

# Load trade history
if os.path.exists("trades.csv"):
    df = pd.read_csv("trades.csv", names=["Time", "Direction", "Entry", "SL", "TP", "Units"])
    st.subheader("📈 Trade History")
    st.dataframe(df.tail(10))

    total_trades = len(df)
    last_trade = df.iloc[-1] if total_trades > 0 else None
    st.metric("Total Trades", total_trades)

    if last_trade is not None:
        st.subheader("📍 Last Trade")
        st.text(f"{last_trade['Time']}: {last_trade['Direction']} @ {last_trade['Entry']}")
else:
    st.warning("No trades have been logged yet.")
