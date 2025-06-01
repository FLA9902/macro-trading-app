import streamlit as st
import yfinance as yf

def safe_check(value, condition):
    if value is None:
        return None
    try:
        return condition
    except:
        return None

def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "dividend_yield": info.get("dividendYield"),
            "payout_ratio": info.get("payoutRatio"),
            "revenue_growth": info.get("revenueGrowth"),
            "pe_ratio": info.get("trailingPE"),
            "debt_to_equity": info.get("debtToEquity"),
            "roe": info.get("returnOnEquity"),
            "gross_margin": info.get("grossMargins"),
            "operating_margin": info.get("operatingMargins"),
            "current_ratio": info.get("currentRatio"),
            "free_cash_flow": info.get("freeCashflow"),
            "sector": info.get("sector", "Unknown"),
            "summary": info.get("longBusinessSummary", ""),
            "logo": info.get("logo_url")
        }
    except Exception as e:
        return None

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

sector_icons = {
    "Technology": "💻", "Healthcare": "🧬", "Consumer Defensive": "🛒", "Financial Services": "💰",
    "Industrials": "🏗️", "Energy": "⛽", "Utilities": "🔌", "Communication Services": "📡",
    "Real Estate": "🏠", "Basic Materials": "⚙️", "Consumer Cyclical": "🛍️"
}

st.set_page_config(page_title="Stock Screener", layout="centered")
st.title("🧠 Stock Screener")

tickers = st.text_input("Enter up to 10 stock tickers separated by commas (e.g., KO,PG,PEP)").upper()
submit = st.button("Check Stocks")

if submit and tickers:
    results = []
    for tkr in tickers.split(",")[:10]:
        tkr = tkr.strip()
        result = check_stock(tkr)
        if result:
            results.append(result)

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
        st.warning("No valid results to display.")
