
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Macro Strategy Dashboard", layout="wide")

# Apply dark/light theme toggle
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

theme = st.sidebar.radio("Theme", ["light", "dark"])
if theme != st.session_state["theme"]:
    st.session_state["theme"] = theme
    st.experimental_rerun()

if st.session_state["theme"] == "dark":
    st.markdown("""
        <style>
        body { background-color: #0e1117; color: white; }
        .stMetric { background-color: #1c1f26; padding: 1em; border-radius: 1em; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stMetric { background-color: #f3f4f6; padding: 1em; border-radius: 1em; }
        </style>
    """, unsafe_allow_html=True)

# Store screening results
if "results" not in st.session_state:
    st.session_state["results"] = []

def get_macro_signals():
    fed_rate = 5.25  # Static
    gdp = 2.1        # Static
    pmi = 52.3       # Static

    score = 0
    score += 1 if fed_rate <= 4.5 else -1
    score += 1 if gdp > 2 else -1
    score += 1 if pmi > 50 else -1

    if score >= 2:
        signal = "Strong Buy"
    elif score == 1:
        signal = "Buy"
    elif score == 0:
        signal = "Hold"
    else:
        signal = "Avoid"

    return fed_rate, gdp, pmi, score, signal

def check_stock(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    try:
        revenue_growth = info.get('revenueGrowth', 0)
        debt_to_equity = info.get('debtToEquity', 999)
        free_cash_flow = info.get('freeCashflow', 0)
        pe_ratio = info.get('trailingPE', 0)
        sector = info.get('sector', 'Unknown')
        summary = info.get('longBusinessSummary', '')[:500]
    except:
        return None

    fits_strategy = (revenue_growth > 0.05 and debt_to_equity < 100 and
                     free_cash_flow and free_cash_flow > 0 and pe_ratio and pe_ratio > 0)
    return {
        'Ticker': ticker,
        'Revenue Growth': revenue_growth,
        'Debt to Equity': debt_to_equity,
        'Free Cash Flow': free_cash_flow,
        'P/E Ratio': pe_ratio,
        'Sector': sector,
        'Summary': summary,
        'Fits Strategy': fits_strategy
    }

st.title("📈 Macro-Based Stock Strategy Dashboard")

st.header("1. 🧠 Macro Dashboard (No CPI)")
fed_rate, gdp, pmi, score, signal = get_macro_signals()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Fed Funds Rate (%)", fed_rate)
col2.metric("GDP YoY (%)", gdp)
col3.metric("PMI", pmi)
col4.metric("Macro Score", score)

st.subheader(f"✅ Current Trading Signal: {signal}")

st.divider()
st.header("2. 🔍 Stock Checker")
ticker = st.text_input("Enter stock ticker (e.g., AAPL)")
if ticker:
    result = check_stock(ticker)
    if result:
        st.write(result)
        if result['Fits Strategy']:
            st.success("✅ This stock fits the current macro strategy.")
        else:
            st.warning("❌ This stock does not fit the strategy.")

        # Store result in session state
        st.session_state["results"].append(result)
    else:
        st.error("Could not fetch stock data.")

# Export screening results
if st.session_state["results"]:
    st.subheader("📤 Export Screening Results")
    df_results = pd.DataFrame(st.session_state["results"])
    st.dataframe(df_results)
    csv = df_results.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download results as CSV",
        data=csv,
        file_name="screening_results.csv",
        mime="text/csv"
    )
