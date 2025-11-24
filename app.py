import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

from datetime import date, timedelta

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Stock Research Terminal", layout="wide")

# =========================
# GLOBAL CSS
# =========================
st.markdown(
    """
    <style>
    /* Make main area tighter and more dashboard-like */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Top bar container */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        box-shadow: 0 1px 4px rgba(15,23,42,0.06);
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .nav-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a1a1a;
        letter-spacing: 0.5px;
    }

    /* Search input/button look */
    .search-input input {
        padding: 0.45rem 0.75rem !important;
        font-size: 0.9rem !important;
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        width: 200px !important;
    }

    .search-btn button {
        background-color: #0d6efd !important;
        color: white !important;
        border: none !important;
        padding: 0.45rem 1rem !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        cursor: pointer !important;
        font-weight: 500 !important;
    }

    /* Tabs styling (money-themed) */
    div[role="tablist"] {
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 0.8rem;
        gap: 6px;
    }

    button[role="tab"] {
        padding: 0.45rem 1rem !important;
        border-radius: 999px !important;
        font-size: 0.9rem;
        border: 1px solid transparent !important;
        box-shadow: 0 1px 3px rgba(15,23,42,0.08);
        font-weight: 500;
        margin-right: 4px;
    }

    /* Overview – soft green */
    button[role="tab"]:nth-child(1) {
        background-color: #E6F4EA !important;
        color: #166534 !important;
    }
    button[role="tab"][aria-selected="true"]:nth-child(1) {
        border-color: #16A34A !important;
        color: #14532D !important;
    }

    /* Valuation – teal */
    button[role="tab"]:nth-child(2) {
        background-color: #E0F7F5 !important;
        color: #0F766E !important;
    }
    button[role="tab"][aria-selected="true"]:nth-child(2) {
        border-color: #0D9488 !important;
        color: #115E59 !important;
    }

    /* Fundamentals – gold */
    button[role="tab"]:nth-child(3) {
        background-color: #F8F3E6 !important;
        color: #92400E !important;
    }
    button[role="tab"][aria-selected="true"]:nth-child(3) {
        border-color: #D97706 !important;
        color: #854D0E !important;
    }

    /* Financials – blue */
    button[role="tab"]:nth-child(4) {
        background-color: #E5ECFF !important;
        color: #1D4ED8 !important;
    }
    button[role="tab"][aria-selected="true"]:nth-child(4) {
        border-color: #1D4ED8 !important;
        color: #1E3A8A !important;
    }

    /* Metric cards: rounded, border, soft shadow */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border-radius: 12px;
        padding: 12px 16px;
        border: 1px solid #e3e6ec;
        box-shadow: 0 2px 6px rgba(15,23,42,0.06);
    }

    /* Tables/DataFrames: card-like */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        border: 1px solid #e3e6ec;
        box-shadow: 0 2px 6px rgba(15,23,42,0.04);
        padding: 8px;
        background: #ffffff;
    }

    /* Info boxes */
    div[data-testid="stAlert"] {
        border-radius: 10px;
        border: 1px solid #e0e7ff;
        background-color: #f3f6ff;
    }

    .stColumns {
        margin-bottom: 0.7rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# TOP NAV BAR (TITLE)
# =========================
st.markdown(
    """
    <style>
    /* Top-right title only, no big white bar */
    .top-nav {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        margin-bottom: 0.75rem;
        padding-top: 0.25rem;
    }

    .nav-title-box {
        background-color: #E6F4EA;   /* light soft green */
        color: #166534;              /* dark green text */
        padding: 0.45rem 1rem;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: 600;
        border: 1px solid #16A34A22; /* soft outline */
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        white-space: nowrap;
    }
    </style>

    <div class="top-nav">
        <div class="nav-title-box">Stock Research Terminal</div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# SEARCH BAR (FUNCTIONAL)
# =========================
search_col1, search_col2, search_col3 = st.columns([5, 2, 1])

with search_col1:
    ticker = st.text_input("Search Ticker:", "AAPL", label_visibility="collapsed")

with search_col2:
    run_search = st.button("Search", type="primary")

with search_col3:
    st.write("")  # spacer

ticker_input = ticker.strip().upper()

# =========================
# PERIOD SELECTOR
# =========================
period_col1, period_col2, period_col3 = st.columns([2, 2, 6])
with period_col1:
    period = st.selectbox(
        "Price history window",
        ["1M", "3M", "6M", "1Y", "5Y", "Max"],
        index=3,
    )

period_map = {
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y",
    "5Y": "5y",
    "Max": "max",
}

st.caption("Single place to look up a stock and see price, valuation, fundamentals, and financials. Data via yfinance / Yahoo Finance.")

# =========================
# DATA LOADER
# =========================
@st.cache_data(show_spinner=True, ttl=300)
def load_ticker_data(ticker: str, price_period: str):
    tk = yf.Ticker(ticker)

    # Price history
    hist = tk.history(period=price_period)

    # Info – try get_info (new) first, fallback to .info
    info = {}
    try:
        info = tk.get_info()
    except Exception:
        try:
            info = tk.info
        except Exception:
            info = {}

    # Financials (quarterly)
    try:
        income_q = tk.quarterly_financials
    except Exception:
        income_q = pd.DataFrame()

    try:
        balance_q = tk.quarterly_balance_sheet
    except Exception:
        balance_q = pd.DataFrame()

    return hist, info, income_q, balance_q

# =========================
# FETCH DATA
# =========================
if ticker_input:
    try:
        hist, info, income_q, balance_q = load_ticker_data(
            ticker_input, period_map[period]
        )
    except Exception as e:
        st.error(f"Error loading data for {ticker_input}: {e}")
        st.stop()
else:
    hist, info, income_q, balance_q = pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame()

if hist.empty and not info:
    st.error(f"No data returned for {ticker_input}. Check the symbol or try another.")
    st.stop()

# =========================
# TOP SUMMARY / HEADER
# =========================
st.subheader(f"{ticker_input} — Overview")

col1, col2, col3 = st.columns(3)

last_price = hist["Close"].iloc[-1] if not hist.empty else np.nan
prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else np.nan
day_change = last_price - prev_close if not np.isnan(prev_close) else np.nan
day_change_pct = (day_change / prev_close * 100) if not np.isnan(prev_close) else np.nan

with col1:
    st.metric(
        "Last Price",
        f"${last_price:,.2f}" if not np.isnan(last_price) else "N/A",
        f"{day_change:+.2f} ({day_change_pct:+.2f}%)" if not np.isnan(day_change) else "N/A",
    )

with col2:
    fifty_two_wk_high = info.get("fiftyTwoWeekHigh", None)
    fifty_two_wk_low = info.get("fiftyTwoWeekLow", None)
    st.write("**52-Week Range**")
    st.write(f"High: {fifty_two_wk_high:.2f}" if fifty_two_wk_high else "High: N/A")
    st.write(f"Low: {fifty_two_wk_low:.2f}" if fifty_two_wk_low else "Low: N/A")

with col3:
    market_cap = info.get("marketCap", None)
    beta = info.get("beta", None)
    st.write("**Key Info**")
    st.write(f"Market Cap: {market_cap:,.0f}" if market_cap else "Market Cap: N/A")
    st.write(f"Beta: {beta:.2f}" if beta is not None else "Beta: N/A")

# Price chart
st.write("**Price History**")
if not hist.empty:
    st.line_chart(hist["Close"])
else:
    st.info("No price history available for this period.")

# =========================
# TABS
# =========================
tab_overview, tab_valuation, tab_fundamentals, tab_financials = st.tabs(
    ["Overview", "Valuation & Ratios", "Fundamentals", "Financials"]
)

# -------------------------
# OVERVIEW TAB
# -------------------------
with tab_overview:
    st.markdown("### Company Snapshot")

    long_name = info.get("longName", "")
    sector = info.get("sector", "")
    industry = info.get("industry", "")
    website = info.get("website", "")

    st.write(f"**Name:** {long_name or 'N/A'}")
    st.write(f"**Sector:** {sector or 'N/A'}")
    st.write(f"**Industry:** {industry or 'N/A'}")
    if website:
        st.write(f"**Website:** {website}")

    desc = info.get("longBusinessSummary", "")
    if desc:
        with st.expander("Business Description"):
            st.write(desc)

    colA, colB, colC = st.columns(3)
    with colA:
        vol = info.get("volume", None)
        avg_vol = info.get("averageVolume", None)
        st.write("**Volume**")
        st.write(f"Today: {vol:,}" if vol else "Today: N/A")
        st.write(f"Avg: {avg_vol:,}" if avg_vol else "Avg: N/A")

    with colB:
        dividend_yield = info.get("dividendYield", None)
        payout_ratio = info.get("payoutRatio", None)
        st.write("**Dividend**")
        st.write(f"Yield: {dividend_yield*100:.2f}%" if dividend_yield else "Yield: N/A")
        st.write(f"Payout Ratio: {payout_ratio*100:.2f}%" if payout_ratio else "Payout Ratio: N/A")

    with colC:
        eps_ttm = info.get("trailingEps", None)
        eps_fwd = info.get("forwardEps", None)
        st.write("**EPS**")
        st.write(f"Trailing EPS: {eps_ttm:.2f}" if eps_ttm else "Trailing EPS: N/A")
        st.write(f"Forward EPS: {eps_fwd:.2f}" if eps_fwd else "Forward EPS: N/A")

# -------------------------
# VALUATION & RATIOS TAB
# -------------------------
with tab_valuation:
    st.markdown("### Valuation Multiples")

    pe_trailing = info.get("trailingPE", None)
    pe_forward = info.get("forwardPE", None)
    ps_ratio = info.get("priceToSalesTrailing12Months", None)
    pb_ratio = info.get("priceToBook", None)
    ev_ebitda = info.get("enterpriseToEbitda", None)

    col1v, col2v, col3v = st.columns(3)

    with col1v:
        st.metric("Trailing P/E", f"{pe_trailing:.2f}" if pe_trailing else "N/A")
        st.metric("Forward P/E", f"{pe_forward:.2f}" if pe_forward else "N/A")

    with col2v:
        st.metric("Price / Sales (TTM)", f"{ps_ratio:.2f}" if ps_ratio else "N/A")
        st.metric("Price / Book", f"{pb_ratio:.2f}" if pb_ratio else "N/A")

    with col3v:
        st.metric("EV / EBITDA", f"{ev_ebitda:.2f}" if ev_ebitda else "N/A")
        st.write("")

    st.markdown("### Extra Metrics (Raw)")

    ratio_keys = [
        "enterpriseValue",
        "enterpriseToRevenue",
        "enterpriseToEbitda",
        "priceToSalesTrailing12Months",
        "priceToBook",
        "trailingPE",
        "forwardPE",
    ]

    ratio_data = {k: info.get(k, None) for k in ratio_keys}
    ratio_df = pd.DataFrame.from_dict(ratio_data, orient="index", columns=["Value"])
    ratio_df.index.name = "Metric"

    st.dataframe(ratio_df, use_container_width=True)

# -------------------------
# FUNDAMENTALS TAB
# -------------------------
with tab_fundamentals:
    st.markdown("### Profitability & Growth")

    revenue_ttm = info.get("totalRevenue", None)
    op_marg = info.get("operatingMargins", None)
    net_marg = info.get("profitMargins", None)

    colF1, colF2, colF3 = st.columns(3)

    with colF1:
        st.metric("Revenue (TTM)", f"${revenue_ttm:,.0f}" if revenue_ttm else "N/A")
    with colF2:
        st.metric("Operating Margin", f"{op_marg*100:.2f}%" if op_marg else "N/A")
    with colF3:
        st.metric("Net Margin", f"{net_marg*100:.2f}%" if net_marg else "N/A")

    st.markdown("### Balance Sheet Highlights")

    total_assets = info.get("totalAssets", None)
    total_debt = info.get("totalDebt", None)
    current_ratio = info.get("currentRatio", None)

    colB1, colB2, colB3 = st.columns(3)
    with colB1:
        st.metric("Total Assets", f"${total_assets:,.0f}" if total_assets else "N/A")
    with colB2:
        st.metric("Total Debt", f"${total_debt:,.0f}" if total_debt else "N/A")
    with colB3:
        st.metric("Current Ratio", f"{current_ratio:.2f}" if current_ratio else "N/A")

# -------------------------
# FINANCIALS TAB
# -------------------------
with tab_financials:
    st.markdown("### Quarterly Income Statement (Last Periods)")

    if isinstance(income_q, pd.DataFrame) and not income_q.empty:
        inc_display = income_q.copy()
        inc_display.index.name = "Line Item"
        st.dataframe(inc_display, use_container_width=True)
    else:
        st.info("No quarterly income statement data available.")

    st.markdown("### Quarterly Balance Sheet (Last Periods)")

    if isinstance(balance_q, pd.DataFrame) and not balance_q.empty:
        bal_display = balance_q.copy()
        bal_display.index.name = "Line Item"
        st.dataframe(bal_display, use_container_width=True)
    else:
        st.info("No quarterly balance sheet data available.")
