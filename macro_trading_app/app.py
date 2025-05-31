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
        'Checks Passed': checks_passed
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
    .status-green { color: #148a00; font-weight: bold; }
    .status-yellow { color: #c78400; font-weight: bold; }
    .status-red { color: #b00020; font-weight: bold; }
    .progress-bar {
        height: 16px;
        width: 100%;
        background-color: #eee;
        border-radius: 10px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .progress-fill {
        height: 100%;
        text-align: center;
        color: white;
        font-size: 12px;
        line-height: 16px;
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
            percent = int((res['Checks Passed'] / 10) * 100)
            color = "#148a00" if percent >= 80 else "#c78400" if percent == 70 else "#b00020"
            st.markdown(f"""
            <div class='metric-card'>
                <h4>{res['Ticker']} ({res['Sector']})</h4>
                <p>{res['Summary']}</p>
                <div>
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
                <div class="progress-bar">
                    <div class="progress-fill" style="width:{percent}%; background-color:{color};">{percent}%</div>
                </div>
                <p class='{"status-green" if percent >= 80 else "status-yellow" if percent == 70 else "status-red"}'><strong>{'✅ Fits strategy!' if res['Fits Strategy'] else '❌ Does not fit strategy'} — {res['Checks Passed']} / 10 checks passed</strong></p>
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
