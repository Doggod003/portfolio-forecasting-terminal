import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date
import plotly.express as px

st.set_page_config(page_title="Sam's Analyst Terminal", layout="wide")

st.title("📊 Sam's Financial Analyst App (APY v3)")
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

# Clean up tickers
edited_df["Ticker"] = edited_df["Ticker"].fillna("").str.upper().str.strip()
tickers = [t for t in edited_df["Ticker"] if t != ""]

if len(tickers) == 0:
    st.warning("Add at least one ticker symbol to see data.")
    st.stop()

# Normalize weights
edited_df["Weight %"] = edited_df["Weight %"].fillna(0)
total_weight = edited_df["Weight %"].sum()
if total_weight == 0:
    st.warning("Total weight is 0%. Adjust your weights.")
    st.stop()

edited_df["Weight (dec)"] = edited_df["Weight %"] / total_weight
edited_df = edited_df[edited_df["Ticker"] != ""].reset_index(drop=True)

# ==============================
# 3. DATE RANGE SELECTOR + PRICE DATA
# ==============================

st.subheader("2️⃣ Price Data & APY Period")

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

# Ensure DataFrame and align with tickers
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
# 4. PORTFOLIO OVERVIEW TABLE
# ==============================

st.subheader("3️⃣ Portfolio Overview – Prices & Period Return")

last_prices = price_data.iloc[-1]
first_prices = price_data.iloc[0]

# Total return over selected period (not annualized yet)
period_return = (last_prices / first_prices - 1) * 100  # %

overview_df = pd.DataFrame({
    "Ticker": tickers,
    "Weight %": edited_df.set_index("Ticker").loc[tickers, "Weight %"].values,
    "Last Price": last_prices.values,
    f"{range_label} Return %": period_return.values
})

st.dataframe(overview_df, use_container_width=True)

# ==============================
# 5. ASSET STATS & APY (ANNUALIZED)
# ==============================

st.subheader("4️⃣ Asset-Level APY & Volatility")

returns = price_data.pct_change().dropna()
if returns.empty or len(returns) < 2:
    st.error("Not enough return data to compute statistics for this range.")
    st.stop()

# Approximate number of trading days in the selected period
n_days = len(returns)  # # of daily steps
trading_days = 252

# Annualized return based on the selected period
# (1 + total_return) ** (trading_days / n_days) - 1
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
# 6. STACKED APY CONTRIBUTION CHART
# ==============================

st.subheader("5️⃣ Stacked APY Contribution – By Ticker")

weights_dec = stats_df["Weight (dec)"].values
# Contribution of each asset to portfolio APY (weight * APY)
stats_df["APY Contribution"] = stats_df["Annualized Return (APY)"] * stats_df["Weight (dec)"]

portfolio_return = float((stats_df["APY Contribution"]).sum())

# Build stacked bar: one column "Portfolio APY" stacked by ticker contribution
contrib_df = stats_df[["Ticker", "APY Contribution"]].copy()
contrib_df["Label"] = "Portfolio APY"

fig = px.bar(
    contrib_df,
    x="Label",
    y="APY Contribution",
    color="Ticker",
    text="APY Contribution",
    title=f"APY Contribution by Ticker – {range_label} window annualized",
)

fig.update_layout(
    xaxis_title="",
    yaxis_title="Annualized Return (APY)",
    legend_title="Ticker",
)
fig.update_yaxes(tickformat=".1%")
fig.update_traces(texttemplate="%{text:.1%}", textposition="inside")

# "Frozen" chart – no mode bar, no zoom tools
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "staticPlot": False})

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

forecast_index = pd.date_range(start=date.today(), periods=months+1, freq="M")
forecast_series = pd.Series(values, index=forecast_index)

st.line_chart(forecast_series)

st.write(f"📌 After **{years} years**, estimated portfolio value: **${forecast_series.iloc[-1]:,.0f}**")
st.caption("APY v3 – APY contributions, tables, and forecast all use the same period and aligned tickers/weights.")
