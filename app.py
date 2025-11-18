import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date
import altair as alt

st.set_page_config(page_title="Sam's Analyst Terminal", layout="wide")

st.title("📊 Sam's Financial Analyst App (APY v4)")
st.caption("Data via yfinance / Yahoo Finance. For research & education only – not a trading terminal.")

# ==============================
# 1. SIDEBAR – GLOBAL SETTINGS
# ==============================

st.sidebar.header("Portfolio Settings")

starting_value = st.sidebar.number_input("Starting portfolio value ($)", 1000.0, step=500.0)
monthly_contribution = st.sidebar.number_input("Monthly contribution ($)", 0.0, step=50.0)
years = st.sidebar.slider("Forecast horizon (years)", 1, 40, 10)

st.sidebar.markdown("---")
st.sidebar.write("Edit your tickers and weights below 👇")

# ==============================
# 2. DEFINE PORTFOLIO
# ==============================

st.subheader("1️⃣ Define Your Portfolio")

default_data = {
    "Ticker": ["QQQM", "QUBT", "IONQ", "IAU"],
    "Weight %": [60, 10, 20, 10]
}
portfolio_df = pd.DataFrame(default_data)

edited_df = st.data_editor(
    portfolio_df,
    num_rows="dynamic",
    use_container_width=True
)

edited_df["Ticker"] = edited_df["Ticker"].fillna("").str.upper().str.strip()
tickers = [t for t in edited_df["Ticker"] if t != ""]

if len(tickers) == 0:
    st.warning("Add at least one ticker symbol to see data.")
    st.stop()

edited_df["Weight %"] = edited_df["Weight %"].fillna(0)
total_weight = edited_df["Weight %"].sum()
if total_weight == 0:
    st.warning("Total weight is 0%. Adjust your weights.")
    st.stop()

edited_df["Weight (dec)"] = edited_df["Weight %"] / total_weight
edited_df = edited_df[edited_df["Ticker"] != ""].reset_index(drop=True)

# ==============================
# 3. DATE RANGE + PRICE DATA
# ==============================

st.subheader("2️⃣ Price Data Window")

range_label = st.radio(
    "Return period:",
    ["Day", "Week", "Month", "Year", "5 Year", "All"],
    horizontal=True
)

period_map = {
    "Day": "1d",
    "Week": "5d",
    "Month": "1mo",
    "Year": "1y",
    "5 Year": "5y",
    "All": "max"
}
selected_period = period_map[range_label]

try:
    raw = yf.download(tickers, period=selected_period, auto_adjust=False, progress=False)
except Exception as e:
    st.error(f"Error downloading price data: {e}")
    st.stop()

if raw.empty:
    st.error("No historical data returned. This could be a yfinance / Yahoo issue or invalid tickers.")
    st.stop()

# Handle 'Adj Close' vs 'Close' and MultiIndex
if isinstance(raw.columns, pd.MultiIndex):
    level0 = raw.columns.get_level_values(0)
    if "Adj Close" in level0:
        price_data = raw["Adj Close"]
    elif "Close" in level0:
        price_data = raw["Close"]
    else:
        st.error("Price data does not contain 'Adj Close' or 'Close' columns.")
        st.write("Columns found:", raw.columns)
        st.stop()
else:
    if "Adj Close" in raw.columns:
        price_data = raw["Adj Close"]
    elif "Close" in raw.columns:
        price_data = raw["Close"]
    else:
        st.error("Price data does not contain 'Adj Close' or 'Close' columns.")
        st.write("Columns found:", raw.columns)
        st.stop()

if isinstance(price_data, pd.Series):
    price_data = price_data.to_frame()

available_cols = [c for c in price_data.columns if c in tickers]
missing = [t for t in tickers if t not in price_data.columns]

if missing:
    st.warning(f"No data returned for: {', '.join(missing)}. They will be ignored in calculations.")

if not available_cols:
    st.error("None of the tickers have usable price data.")
    st.stop()

price_data = price_data[available_cols]
edited_df = edited_df[edited_df["Ticker"].isin(available_cols)].reset_index(drop=True)
tickers = list(price_data.columns)

# ==============================
# 4. OVERVIEW TABLE
# ==============================

st.subheader("3️⃣ Portfolio Overview – Prices & Period Return")

last_prices = price_data.iloc[-1]
first_prices = price_data.iloc[0]

period_return = (last_prices / first_prices - 1) * 100  # %

overview_df = pd.DataFrame({
    "Ticker": tickers,
    "Weight %": edited_df.set_index("Ticker").loc[tickers, "Weight %"].values,
    "Last Price": last_prices.values,
    f"{range_label} Return %": period_return.values
})

st.dataframe(overview_df, use_container_width=True)

# ==============================
# 5. APY (ANNUALIZED) & VOL
# ==============================

st.subheader("4️⃣ Asset APY & Volatility (from selected window)")

returns = price_data.pct_change().dropna()
if returns.empty or len(returns) < 2:
    st.error("Not enough return data to compute statistics for this range.")
    st.stop()

n_days = len(returns)
trading_days = 252

total_return_dec = (last_prices / first_prices - 1)
annualized_returns = (1 + total_return_dec) ** (trading_days / n_days) - 1
annualized_vol = returns.std() * np.sqrt(trading_days)

stats_df = pd.DataFrame({
    "Ticker": tickers,
    "Annualized Return (APY)": annualized_returns.values,
    "Annualized Volatility": annualized_vol.values,
    "Weight (dec)": edited_df.set_index("Ticker").loc[tickers, "Weight (dec)"].values
})

st.dataframe(stats_df, use_container_width=True)

# ==============================
# 6. STACKED APY COLUMN (Altair)
# ==============================

st.subheader("5️⃣ Stacked APY Contribution – By Ticker")

stats_df["APY Contribution"] = stats_df["Annualized Return (APY)"] * stats_df["Weight (dec)"]
portfolio_return = float(stats_df["APY Contribution"].sum())

# Data for stacked column – one column "Portfolio APY", stacked by ticker
contrib_df = stats_df[["Ticker", "APY Contribution"]].copy()
contrib_df["Label"] = "Portfolio APY"

chart = (
    alt.Chart(contrib_df)
    .mark_bar()
    .encode(
        x=alt.X("Label:N", title=""),
        y=alt.Y("APY Contribution:Q", stack="zero", title="Annualized Return (APY)"),
        color=alt.Color("Ticker:N", title="Ticker"),
        tooltip=[
            alt.Tooltip("Ticker:N"),
            alt.Tooltip("APY Contribution:Q", format=".2%"),
            alt.Tooltip("Label:N"),
        ],
    )
    .properties(title=f"APY Contribution by Ticker – {range_label} window annualized")
)

st.altair_chart(chart, use_container_width=True)

st.markdown(
    f"**Portfolio APY (sum of contributions):** `{portfolio_return:.2%}`"
)

# ==============================
# 7. CORRELATION & FORECAST
# ==============================

st.subheader("6️⃣ Correlation Matrix (Based on Selected Period)")

corr_df = returns.corr().loc[tickers, tickers]
st.dataframe(corr_df, use_container_width=True)

st.subheader("7️⃣ Forecast – Deterministic Projection (Using Portfolio APY)")

months = years * 12
if portfolio_return <= -1:
    monthly_rate = -1
else:
    monthly_rate = (1 + portfolio_return) ** (1/12) - 1

values = []
current_value = starting_value

for _ in range(months + 1):
    values.append(current_value)
    current_value = current_value * (1 + monthly_rate) + monthly_contribution

forecast_index = pd.date_range(start=date.today(), periods=months + 1, freq="M")
forecast_series = pd.Series(values, index=forecast_index)

st.line_chart(forecast_series)

st.write(f"📌 After **{years} years**, estimated portfolio value: **${forecast_series.iloc[-1]:,.0f}**")
st.caption("APY v4 – APY chart is a stacked column per your portfolio; only the forecast remains a line chart.")
