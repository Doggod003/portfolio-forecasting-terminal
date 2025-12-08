import streamlit as st
import yfinance as yf  # still imported if services uses it elsewhere
import pandas as pd
import numpy as np

from datetime import date, timedelta
from components.header import inject_global_css, render_header, render_controls
from services.data_loader import load_ticker_data

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Stock Research Terminal", layout="wide")

# Global styling + sticky glass header from components/header.py
inject_global_css()
render_header()

# Ticker, period, search button, period_map from components/header.py
ticker_input, period, run_search, period_map = render_controls()

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
# PRICE TABLE WITH DATE SLICE (Under chart)
# =========================
if not hist.empty:
    st.markdown("### Price Table — Open / Close by Date")

    # Reset index to clean date column
    hist_reset = hist.reset_index().copy()
    hist_reset["Date"] = hist_reset["Date"].dt.date

    min_date = hist_reset["Date"].min()
    max_date = hist_reset["Date"].max()

    col_start, col_end = st.columns(2)

    with col_start:
        table_start_date = st.date_input(
            "Table start date",
            value=max_date - timedelta(days=30),
            min_value=min_date,
            max_value=max_date,
            key="table_price_start",
        )

    with col_end:
        table_end_date = st.date_input(
            "Table end date",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="table_price_end",
        )

    if table_start_date > table_end_date:
        st.warning("Start date cannot be after end date.")
    else:
        mask = (
            (hist_reset["Date"] >= table_start_date)
            & (hist_reset["Date"] <= table_end_date)
        )
        sliced = hist_reset.loc[mask, ["Date", "Open", "Close"]]

        if sliced.empty:
            st.info("No price data in this date range.")
        else:
            sliced = sliced.sort_values("Date", ascending=False)

            display_df = sliced.copy()
            display_df.rename(
                columns={"Open": "Open ($)", "Close": "Close ($)"},
                inplace=True,
            )

            display_df["Open ($)"] = display_df["Open ($)"].map(lambda x: f"{x:,.2f}")
            display_df["Close ($)"] = display_df["Close ($)"].map(lambda x: f"{x:,.2f}")

            st.dataframe(display_df, use_container_width=True)

# =========================
# PRICE TABLE WITH DATE SLICE
# =========================
if not hist.empty:
    st.markdown("### Price Table — Open / Close by Date")

    # Reset index so Date is a column, then convert to plain date
    hist_reset = hist.reset_index().copy()
    hist_reset["Date"] = hist_reset["Date"].dt.date  # yfinance index is Timestamp

    min_date = hist_reset["Date"].min()
    max_date = hist_reset["Date"].max()

    col_start, col_end = st.columns(2)
with col_start:
    start_date = st.date_input(
        "Start date",
        value=max_date - timedelta(days=30),
        min_value=min_date,
        max_value=max_date,
    )
with col_end:
    end_date = st.date_input(
        "End date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
    )


    if start_date > end_date:
        st.warning("Start date cannot be after end date.")
    else:
        mask = (hist_reset["Date"] >= start_date) & (hist_reset["Date"] <= end_date)
        sliced = hist_reset.loc[mask, ["Date", "Open", "Close"]]

        if sliced.empty:
            st.info("No price data in this date range.")
        else:
            # Sort with most recent first
            sliced = sliced.sort_values("Date", ascending=False)

            # Make a display copy with nicer column names + formatting
            display_df = sliced.copy()
            display_df.rename(
                columns={
                    "Date": "Date",
                    "Open": "Open ($)",
                    "Close": "Close ($)",
                },
                inplace=True,
            )

            # Format numbers as strings with 2 decimals + thousands
            display_df["Open ($)"] = display_df["Open ($)"].map(lambda x: f"{x:,.2f}")
            display_df["Close ($)"] = display_df["Close ($)"].map(lambda x: f"{x:,.2f}")

            st.dataframe(
                display_df,
                use_container_width=True,
            )


    # Convert index to date for slicing
    hist_reset = hist.reset_index().copy()
    hist_reset["Date"] = hist_reset["Date"].dt.date  # index column from yfinance is named "Date"

    min_date = hist_reset["Date"].min()
    max_date = hist_reset["Date"].max()

    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input("Start date", value=max_date - timedelta(days=30), min_value=min_date, max_value=max_date, key="price_start")
    with col_end:
        end_date = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date, key="price_end")

    # Ensure start <= end
    if start_date > end_date:
        st.warning("Start date cannot be after end date.")
    else:
        mask = (hist_reset["Date"] >= start_date) & (hist_reset["Date"] <= end_date)
        sliced = hist_reset.loc[mask, ["Date", "Open", "Close"]].sort_values("Date")

        if sliced.empty:
            st.info("No price data in this date range.")
        else:
            sliced_display = sliced.copy()
            sliced_display["Open"] = sliced_display["Open"].round(2)
            sliced_display["Close"] = sliced_display["Close"].round(2)

            st.dataframe(
                sliced_display,
                use_container_width=True,
            )

# =========================
# TABS
# =========================
tab_overview, tab_valuation, tab_fundamentals = st.tabs(
    ["Overview", "Valuation & Ratios", "Fundamentals"]
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
