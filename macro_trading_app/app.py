
import streamlit as st
import yfinance as yf
import requests

QUANDL_API_KEY = 'DSMfTqzSXn6N9zsxLfaB'

def get_quandl_data(code):
    url = f"https://data.nasdaq.com/api/v3/datasets/{code}/data.json?api_key={QUANDL_API_KEY}"
    response = requests.get(url)
    try:
        data = response.json()
        return float(data['dataset_data']['data'][0][1])
    except Exception as e:
        st.warning(f"⚠️ Could not fetch {code}. Using fallback.")
        return None

def get_macro_signals():
    cpi = get_quandl_data("RATEINF/CPI_USA")  # US CPI YoY in %
    fed_rate = 5.25  # Static fallback
    gdp = 2.1        # Static fallback
    pmi = 52.3       # Static fallback

    score = 0
    score += 1 if cpi and cpi < 3 else -1
    score += 1 if fed_rate <= 4.5 else -1
    score += 1 if gdp > 2 else -1
    score += 1 if pmi > 50 else -1

    if score >= 3:
        signal = "Strong Buy"
    elif score == 2:
        signal = "Buy"
    elif score == 1:
        signal = "Hold"
    else:
        signal = "Avoid"

    return cpi, fed_rate, gdp, pmi, score, signal

def check_stock(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    try:
        revenue_growth = info.get('revenueGrowth', 0)
        debt_to_equity = info.get('debtToEquity', 999)
        sector = info.get('sector', 'Unknown')
        summary = info.get('longBusinessSummary', '')[:500]
    except:
        return None

    fits_strategy = revenue_growth > 0.05 and debt_to_equity < 100
    return {
        'Revenue Growth': revenue_growth,
        'Debt to Equity': debt_to_equity,
        'Sector': sector,
        'Summary': summary,
        'Fits Strategy': fits_strategy
    }

st.title("📈 Macro-Based Stock Strategy Dashboard")
st.header("1. 🧠 Macro Dashboard")
cpi, fed_rate, gdp, pmi, score, signal = get_macro_signals()
st.metric("US CPI YoY (%)", round(cpi, 2) if cpi else "Unavailable")
st.metric("Fed Funds Rate (%)", fed_rate)
st.metric("GDP YoY (%)", gdp)
st.metric("PMI", pmi)
st.metric("Macro Score", score)
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
    else:
        st.error("Could not fetch stock data.")
