import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(page_title="Sam's Analyst Terminal", layout="wide")

st.title("📊 Sam's Financial Analyst App (Clean v2)")
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

# Keep only rows with non-empty tickers
edited_df = edited_df[edited_df["Ticker"] != ""].reset_index(drop=True)

# ==============================
# 3. DOWNLOAD PRICE DATA (ONE TIME)
# ==============================

st.subheader("2️⃣ Price History (1 Year)")

try:
    raw = yf.download(tickers, period="1y", auto_adjust=False, progress=False)
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

# Ensure DataFrame shape and columns
if isinstance(price_data, pd.Series):
    price_data = price_data.to_frame()

# Align tickers order to edited_df and drop any missing
available_cols = [c for c in price_data.columns if c in tickers]
missing = [t for t in tickers if t not in price_data.columns]

if missing:
    st.warning(f"No data returned for: {', '.join(missing)}. They will be ignored in calculations.")

if not available_cols:
    st.error("None of the tickers have usable price data.")
    st.stop()

price_data = price_data[available_cols]
# Filter edited_df to only tickers that have data
edited_df = edited_df[edited_df["Ticker"].isin(available_cols)].reset_index(drop=True)
tickers = list(price_data.columns)

# Show unified price chart for all tickers
st.line_chart(price_data)

# ==============================
# 4. BUILD SNAPSHOT & STATS TABLES
# ==============================

st.subheader("3️⃣ Portfolio Overview – Prices, Weights, 1Y Return")

# 1Y returns & last prices from price_data
last_prices = price_data.iloc[-1]
first_prices = price_data.iloc[0]

total_return = (last_prices / first_prices - 1) * 100  # in %

overview_df = pd.DataFrame({
    "Ticker": tickers,
    "Weight %": edited_df.set_index("Ticker").loc[tickers, "Weight %"].values,
    "Last Price": last_prices.values,
    "1Y Return %": total_return.values
})

st.dataframe(overview_df, use_container_width=True)

# ---- Asset-level stats ----
st.subheader("4️⃣ Asset-Level Stats – Annualized Return & Volatility")

returns = price_data.pct_change().dropna()
if returns.empty:
    st.error("Not enough return data to compute statistics.")
    st.stop()

trading_days = 252
mean_returns = returns.mean() * trading_days
volatility = returns.std() * np.sqrt(trading_days)

stats_df = pd.DataFrame({
    "Ticker": tickers,
    "Annualized Return": mean_returns.values,
    "Annualized Volatility": volatility.values,
    "Weight %": edited_df.set_index("Ticker").loc[tickers, "Weight %"].values
})

st.dataframe(stats_df, use_container_width=True)

# ==============================
# 5. PORTFOLIO METRICS & CORRELATION
# ==============================

st.subheader("5️⃣ Portfolio Metrics & Correlation")

weights_dec = (edited_df.set_index("Ticker").loc[tickers, "Weight (dec)"]).values

cov_matrix = returns.cov() * trading_days

portfolio_return = float(np.dot(weights_dec, mean_returns.loc[tickers].values))
portfolio_vol = float(np.sqrt(np.dot(weights_dec.T, np.dot(cov_matrix.loc[tickers, tickers].values, weights_dec))))

col1, col2 = st.columns(2)
with col1:
    st.metric("Expected Annual Portfolio Return", f"{portfolio_return:.2%}")
with col2:
    st.metric("Expected Annual Portfolio Volatility", f"{portfolio_vol:.2%}")

st.write("🔗 Correlation Matrix (1Y):")
corr_df = returns.corr().loc[tickers, tickers]
st.dataframe(corr_df, use_container_width=True)

# ==============================
# 6. FORECASTING
# ==============================

st.subheader("6️⃣ Forecast – Deterministic Projection")

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

st.caption("Clean v2 – All tables and metrics are based on the same 1-year price dataset and aligned tickers/weights.")
