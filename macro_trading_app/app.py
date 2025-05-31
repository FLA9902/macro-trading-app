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
    return condition if val is not None else True

def check_stock(ticker):
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
        hist = stock.history(period="6mo")
        dividend_yield = info.get('dividendYield', None)
        payout_ratio = info.get('payoutRatio', None)
        revenue_growth = info.get('revenueGrowth', None)
        pe_ratio = info.get('trailingPE', None)
        debt_to_equity = info.get('debtToEquity', None)
        roe = info.get('returnOnEquity', None)
        gross_margin = info.get('grossMargins', None)
        operating_margin = info.get('operatingMargins', None)
        current_ratio = info.get('currentRatio', None)
        free_cash_flow = info.get('freeCashflow', None)
        sector = info.get('sector', 'Unknown')
        summary = info.get('longBusinessSummary', '')[:500]
        logo = info.get('logo_url', '')
    except:
        return None

    checks = [
        safe_check(dividend_yield, dividend_yield >= 0.019),
        safe_check(payout_ratio, payout_ratio <= 0.82),
        safe_check(revenue_growth, revenue_growth >= 0.009),
        safe_check(pe_ratio, 9.5 <= pe_ratio <= 26),
        safe_check(debt_to_equity, debt_to_equity <= 0.72),
        safe_check(roe, roe >= 0.095),
        safe_check(gross_margin, gross_margin >= 0.295),
        safe_check(operating_margin, operating_margin >= 0.115),
        safe_check(current_ratio, current_ratio >= 1.35),
        safe_check(free_cash_flow, free_cash_flow > 0)
    ]

    checks_passed = sum(checks)
    fits_strategy = checks_passed >= 7

    return {
        'Ticker': ticker,
        'Dividend Yield': dividend_yield,
        'Payout Ratio': payout_ratio,
        'Revenue Growth': revenue_growth,
        'P/E Ratio': pe_ratio,
        'Debt to Equity': debt_to_equity,
        'ROE': roe,
        'Gross Margin': gross_margin,
        'Operating Margin': operating_margin,
        'Current Ratio': current_ratio,
        'Free Cash Flow': free_cash_flow,
        'Sector': sector,
        'Summary': summary,
        'Logo': logo,
        'Fits Strategy': fits_strategy,
        'Checks Passed': checks_passed,
        'Price History': hist['Close'] if not hist.empty else None
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

    st.write("Results would be displayed here.")
else:
    st.info("🔍 Please select or enter stock tickers to begin screening.")
