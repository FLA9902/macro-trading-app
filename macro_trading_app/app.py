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

def safe_check(val, condition):
    if val is None:
        return None  # Neutral if missing
    return condition

def check_stock(ticker):
    data = fetch_stock_data(ticker)
    if not data:
        return None

    dividend_yield = data.get("dividend_yield")
    payout_ratio = data.get("payout_ratio")
    revenue_growth = data.get("revenue_growth")
    pe_ratio = data.get("pe_ratio")
    debt_to_equity = data.get("debt_to_equity")
    roe = data.get("roe")
    gross_margin = data.get("gross_margin")
    operating_margin = data.get("operating_margin")
    current_ratio = data.get("current_ratio")
    free_cash_flow = data.get("free_cash_flow")

    checks = [
        safe_check(dividend_yield, dividend_yield >= 0.004),
        safe_check(payout_ratio, payout_ratio <= 0.80),
        safe_check(revenue_growth, revenue_growth >= 0),
        safe_check(pe_ratio, 9.5 <= pe_ratio <= 35),
        safe_check(debt_to_equity, debt_to_equity <= 2),
        safe_check(roe, roe >= 0.08),
        safe_check(gross_margin, gross_margin >= 0.30),
        safe_check(operating_margin, operating_margin >= 0.10),
        safe_check(current_ratio, current_ratio >= 1),
        safe_check(free_cash_flow, free_cash_flow > 0)
    ]

    checks_passed = sum(1 for c in checks if c is True)
    missing_checks = sum(1 for c in checks if c is None)
    total_effective_checks = len(checks) - missing_checks
    fits_strategy = total_effective_checks == 0 or checks_passed >= 7

    return {
        "Ticker": ticker,
        "Fits Strategy": fits_strategy,
        "Checks Passed": checks_passed,
        "Total Criteria": total_effective_checks,
        "Sector": data.get("sector", "Unknown"),
        "Summary": data.get("summary", "No summary available."),
        "Logo": data.get("logo")
    }

st.header("📈 Evaluate Up to 10 Stocks")
st.markdown("Enter up to 10 tickers using the dropdown or input field below. Conservative dividend stocks like JNJ, KO, PG are good starting points.")
selected = st.multiselect("Choose from suggested tickers:", options=SUGGESTED_TICKERS)
custom_input = st.text_input("Or enter custom tickers (comma separated):")
show_only_pass = st.checkbox("Only show stocks that pass the strategy")

custom_tickers = [x.strip().upper() for x in custom_input.split(",") if x.strip()] if custom_input else []
tickers = (selected + custom_tickers)[:10]

if tickers:
    st.session_state["history"].append(", ".join(tickers))
    results = []
    for tkr in tickers:
        try:
            result = check_stock(tkr)
            if result:
                results.append(result)
            else:
                st.warning(f"⚠️ Could not fetch data for {tkr}")
        except Exception as e:
            st.error(f"❌ Error checking {tkr}: {e}")

    if results:
    for res in results:
        st.markdown(f"### {res['Ticker']} {'✅' if res['Fits Strategy'] else '❌'}")
        if res['Logo']:
            st.image(res['Logo'], width=60)
        st.markdown(f"**Sector:** {sector_icons.get(res['Sector'], '')} {res['Sector']}")
        st.markdown(f"**Summary:** {res['Summary']}")
        st.markdown(f"**Checks Passed:** {res['Checks Passed']} / 10")
        st.markdown("**Criteria Evaluated:**")
        st.markdown("""
- Dividend Yield ≥ 0.4%  
- Payout Ratio ≤ 80%  
- Revenue Growth ≥ 0%  
- P/E Ratio between 9.5 and 35  
- Debt to Equity ≤ 2  
- ROE ≥ 8%  
- Gross Margin ≥ 30%  
- Operating Margin ≥ 10%  
- Current Ratio ≥ 1  
- Free Cash Flow > 0
""")
        st.markdown("---")
else:
        st.info("🔍 Please select or enter stock tickers to begin screening.")
else:
    st.info("🔍 Please select or enter stock tickers to begin screening.")
