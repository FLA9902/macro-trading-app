import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Conservative Dividend Screener", layout="wide")

if "results" not in st.session_state:
    st.session_state["results"] = []
if "history" not in st.session_state:
    st.session_state["history"] = []

SUGGESTED_TICKERS = [
    "JNJ", "PG", "KO", "PEP", "XOM", "CVX", "MRK", "PFE", "T", "VZ",
    "MO", "MCD", "WMT", "CL", "MMM", "ABT", "MDT", "ADP", "TROW", "SYY"
]

sector_icons = {
    "Technology": "💻",
    "Financial Services": "🏦",
    "Healthcare": "🧬",
    "Consumer Defensive": "🛒",
    "Industrials": "🏗️",
    "Energy": "⚡",
    "Utilities": "💡",
    "Communication Services": "📡",
    "Consumer Cyclical": "🎯",
    "Real Estate": "🏠",
    "Basic Materials": "🧱"
}

# ... rest of unchanged functions (check_stock, pass_fail, etc.) remain

st.header("📈 Evaluate Up to 10 Stocks")
selected = st.multiselect("Choose from suggested tickers:", options=SUGGESTED_TICKERS)
custom_input = st.text_input("Or enter custom tickers (comma separated):")
show_only_pass = st.checkbox("Only show stocks that pass the strategy")

custom_tickers = [x.strip().upper() for x in custom_input.split(",") if x.strip()] if custom_input else []
tickers = (selected + custom_tickers)[:10]

if tickers:
    st.session_state["history"].append(", ".join(tickers))
    results = []
    for tkr in tickers:
        result = check_stock(tkr)
        if result:
            results.append(result)
        else:
            st.warning(f"⚠️ Could not fetch data for {tkr}")

    filtered_results = [r for r in results if r['Fits Strategy']] if show_only_pass else results

    if filtered_results:
        for res in filtered_results:
            # Display logic for results remains unchanged...
            pass  # placeholder to maintain brevity

# Display ticker history with clear button
if st.session_state["history"]:
    st.markdown("### 🧠 Last Screened Tickers")
    for i, tickers_str in enumerate(reversed(st.session_state["history"][-5:]), 1):
        st.markdown(f"**{i}.** {tickers_str}")
    if st.button("🧹 Clear History"):
        st.session_state["history"] = []
        st.experimental_rerun()
