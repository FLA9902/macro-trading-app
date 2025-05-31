import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Conservative Dividend Screener", layout="wide")

if "results" not in st.session_state:
    st.session_state["results"] = []

def check_stock(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    try:
        hist = stock.history(period="6mo")
    except:
        hist = pd.DataFrame()
    try:
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
    except:
        return None

    checks = []

    if dividend_yield is not None:
        checks.append(dividend_yield >= 0.019)
    if payout_ratio is not None:
        checks.append(payout_ratio <= 0.82)
    if revenue_growth is not None:
        checks.append(revenue_growth >= 0.009)
    if pe_ratio is not None:
        checks.append(9.5 <= pe_ratio <= 26)
    if debt_to_equity is not None:
        checks.append(debt_to_equity <= 0.72)
    if roe is not None:
        checks.append(roe >= 0.095)
    if gross_margin is not None:
        checks.append(gross_margin >= 0.295)
    if operating_margin is not None:
        checks.append(operating_margin >= 0.115)
    if current_ratio is not None:
        checks.append(current_ratio >= 1.35)
    if free_cash_flow is not None:
        checks.append(free_cash_flow > 0)

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
        'Fits Strategy': fits_strategy,
        'Checks Passed': checks_passed,
        'Price History': hist['Close'] if not hist.empty else None
    }

def pass_fail(val, condition):
    if val is None or pd.isna(val):
        return "❓ N/A"
    return f"✅ {val}" if condition else f"❌ {val}"

st.title("🛡️ Conservative Dividend Stock Screener")

st.markdown("""
    <style>
    .metric-card {
        padding: 1.5rem;
        border-radius: 1.25rem;
        box-shadow: 0 3px 8px rgba(0,0,0,0.12);
        background: linear-gradient(145deg, #f4f4f4, #ffffff);
        margin-bottom: 2rem;
        font-size: 1rem;
        color: #222;
        transition: 0.3s ease;
    }
    .metric-card:hover {
        box-shadow: 0 6px 16px rgba(0,0,0,0.18);
    }
    .status-green { color: #148a00; font-weight: bold; }
    .status-yellow { color: #c78400; font-weight: bold; }
    .status-red { color: #b00020; font-weight: bold; }
    .metrics-table { line-height: 1.6; margin-top: 1rem; font-size: 0.95rem; }
    @media screen and (max-width: 768px) {
        .metric-card { font-size: 0.9rem; padding: 1rem; }
    }
    </style>
""", unsafe_allow_html=True)

st.header("📈 Evaluate Up to 10 Stocks")
user_input = st.text_area("Enter tickers (comma separated, max 10):")
show_only_pass = st.checkbox("Only show stocks that pass the strategy")

triggered_balloons = False

if user_input:
    tickers = [x.strip().upper() for x in user_input.split(",") if x.strip()][:10]
    results = []

    for tkr in tickers:
        result = check_stock(tkr)
        if result:
            results.append(result)
            if result['Fits Strategy']:
                triggered_balloons = True
        else:
            st.warning(f"⚠️ Could not fetch data for {tkr}")

    if triggered_balloons:
        st.balloons()

    filtered_results = [r for r in results if r['Fits Strategy']] if show_only_pass else results

    if filtered_results:
        for res in filtered_results:
            color_class = "status-green" if res['Checks Passed'] >= 8 else "status-yellow" if res['Checks Passed'] == 7 else "status-red"
            st.markdown(f"""
            <div class='metric-card'>
                <h4>{res['Ticker']} ({res['Sector']})</h4>
                <p>{res['Summary']}</p>
                <div class="metrics-table">
                    {pass_fail(res['Dividend Yield'], res['Dividend Yield'] is not None and res['Dividend Yield'] >= 0.019)} — Dividend Yield ≥ 1.9%<br>
                    {pass_fail(res['Payout Ratio'], res['Payout Ratio'] is not None and res['Payout Ratio'] <= 0.82)} — Payout Ratio ≤ 82%<br>
                    {pass_fail(res['Revenue Growth'], res['Revenue Growth'] is not None and res['Revenue Growth'] >= 0.009)} — Revenue Growth ≥ 0.9%<br>
                    {pass_fail(res['P/E Ratio'], res['P/E Ratio'] is not None and 9.5 <= res['P/E Ratio'] <= 26)} — P/E between 9.5 and 26<br>
                    {pass_fail(res['Debt to Equity'], res['Debt to Equity'] is not None and res['Debt to Equity'] <= 0.72)} — Debt/Equity ≤ 0.72<br>
                    {pass_fail(res['ROE'], res['ROE'] is not None and res['ROE'] >= 0.095)} — ROE ≥ 9.5%<br>
                    {pass_fail(res['Gross Margin'], res['Gross Margin'] is not None and res['Gross Margin'] >= 0.295)} — Gross Margin ≥ 29.5%<br>
                    {pass_fail(res['Operating Margin'], res['Operating Margin'] is not None and res['Operating Margin'] >= 0.115)} — Operating Margin ≥ 11.5%<br>
                    {pass_fail(res['Current Ratio'], res['Current Ratio'] is not None and res['Current Ratio'] >= 1.35)} — Current Ratio ≥ 1.35<br>
                    {pass_fail(res['Free Cash Flow'], res['Free Cash Flow'] is None or res['Free Cash Flow'] > 0)} — FCF > 0 (if known)
                </div>
                <p class='{color_class}'><strong>{'✅ Fits strategy!' if res['Fits Strategy'] else '❌ Does not fit strategy'} — {res['Checks Passed']} / 10 checks passed</strong></p>
            </div>
            """, unsafe_allow_html=True)

            if res['Price History'] is not None:
                fig, ax = plt.subplots(figsize=(6, 2))
                res['Price History'].plot(ax=ax, color='gray')
                ax.set_title(f"6-Month Price Chart for {res['Ticker']}", fontsize=10)
                ax.set_ylabel('Price')
                ax.set_xlabel('Date')
                ax.grid(True, linestyle='--', linewidth=0.5)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info(f"📉 No 6-month price data available for {res['Ticker']}")

        df_results = pd.DataFrame(filtered_results)
        st.session_state["results"] = filtered_results

        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📤 Download Results as CSV",
            data=csv,
            file_name="screening_results.csv",
            mime="text/csv"
        )
