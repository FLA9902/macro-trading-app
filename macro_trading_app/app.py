
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Conservative Dividend Screener", layout="wide")

if "results" not in st.session_state:
    st.session_state["results"] = []

def check_stock(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    try:
        dividend_yield = info.get('dividendYield', 0)
        payout_ratio = info.get('payoutRatio', 1)
        revenue_growth = info.get('revenueGrowth', 0)
        pe_ratio = info.get('trailingPE', 0)
        debt_to_equity = info.get('debtToEquity', 999)
        roe = info.get('returnOnEquity', 0)
        gross_margin = info.get('grossMargins', 0)
        operating_margin = info.get('operatingMargins', 0)
        current_ratio = info.get('currentRatio', 0)
        free_cash_flow = info.get('freeCashflow', 0)
        sector = info.get('sector', 'Unknown')
        summary = info.get('longBusinessSummary', '')[:500]
    except:
        return None

    fits_strategy = (
        dividend_yield and dividend_yield >= 0.02 and
        payout_ratio and payout_ratio <= 0.7 and
        revenue_growth >= 0.02 and
        pe_ratio and 10 <= pe_ratio <= 25 and
        debt_to_equity <= 0.6 and
        roe >= 0.10 and
        gross_margin >= 0.35 and
        operating_margin >= 0.15 and
        current_ratio >= 1.5 and
        free_cash_flow and free_cash_flow > 0
    )

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
        'Fits Strategy': fits_strategy
    }

def pass_fail(val, condition):
    if val is None or pd.isna(val):
        return "❓ N/A"
    return f"✅ {val}" if condition else f"❌ {val}"

st.title("🛡️ Conservative Dividend Stock Screener")

st.markdown("""
    <style>
    .metric-card {
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        background-color: #ffffff;
        margin-bottom: 1.5rem;
        font-size: 1rem;
        max-width: 100%;
        color: #222;
    }
    @media (max-width: 768px) {
        .metric-card { font-size: 0.95rem; padding: 0.75rem; }
    }
    </style>
""", unsafe_allow_html=True)

st.header("📈 Evaluate Up to 10 Stocks")
user_input = st.text_area("Enter tickers (comma separated, max 10):")
show_only_pass = st.checkbox("Only show stocks that pass the strategy")

if user_input:
    tickers = [x.strip().upper() for x in user_input.split(",") if x.strip()][:10]
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
            st.markdown(f"""
            <div class='metric-card'>
                <h4>{res['Ticker']} ({res['Sector']})</h4>
                <p>{res['Summary']}</p>
                <div>
                    {pass_fail(res['Dividend Yield'], res['Dividend Yield'] >= 0.02)} — Dividend Yield ≥ 2%<br>
                    {pass_fail(res['Payout Ratio'], res['Payout Ratio'] <= 0.7)} — Payout Ratio ≤ 70%<br>
                    {pass_fail(res['Revenue Growth'], res['Revenue Growth'] >= 0.02)} — Revenue Growth ≥ 2%<br>
                    {pass_fail(res['P/E Ratio'], 10 <= res['P/E Ratio'] <= 25)} — P/E between 10 and 25<br>
                    {pass_fail(res['Debt to Equity'], res['Debt to Equity'] <= 0.6)} — Debt/Equity ≤ 0.6<br>
                    {pass_fail(res['ROE'], res['ROE'] >= 0.10)} — ROE ≥ 10%<br>
                    {pass_fail(res['Gross Margin'], res['Gross Margin'] >= 0.35)} — Gross Margin ≥ 35%<br>
                    {pass_fail(res['Operating Margin'], res['Operating Margin'] >= 0.15)} — Operating Margin ≥ 15%<br>
                    {pass_fail(res['Current Ratio'], res['Current Ratio'] >= 1.5)} — Current Ratio ≥ 1.5<br>
                    {pass_fail(res['Free Cash Flow'], res['Free Cash Flow'] > 0)} — FCF > 0
                </div>
                <p><strong>{'✅ Fits strategy!' if res['Fits Strategy'] else '❌ Does not fit strategy'}</strong></p>
            </div>
            """, unsafe_allow_html=True)

        df_results = pd.DataFrame(filtered_results)
        st.session_state["results"] = filtered_results

        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📤 Download Results as CSV",
            data=csv,
            file_name="screening_results.csv",
            mime="text/csv"
        )
