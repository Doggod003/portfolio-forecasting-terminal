import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(page_title="Sam's Analyst Terminal", layout="wide")

st.title("📊 Sam's Financial Analyst App (v1.3)")
st.caption("Data via yfinance/Yahoo Finance – good for research & school, not a trading terminal.")

# --- SIDEBAR SETTINGS ---

st.sidebar.header("Portfolio Settings")

starting_value = st.sidebar.number_input("Starting portfolio value ($)", 1000.0, step=500.0)
monthly_contribution = st.sidebar.number_input("Monthly contribution ($)", 0.0, step=50.0)
years = st.sidebar.slider("Forecast horizon (years)", 1, 40, 10)

st.sidebar.markdown("---")
st.sidebar.write("Edit your tickers and weights below 👇")

# --- 1. DEFINE PORTFOLIO ---

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

# Clean tickers
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

# --- 2. TICKER SNAPSHOT (CURRENT DATA) ---

st.subheader("2️⃣ Ticker Snapshot – Current Prices & 1Y Range")

snapshot_rows = []

for t in tickers:
    try:
        tk = yf.Ticker(t)

        # 1-year history for high/low
        hist_1y = tk.history(period="1y")
        hist_5d = tk.history(period="5d")

        if hist_5d.empty and hist_1y.empty:
            snapshot_rows.append({
                "Ticker": t,
                "Last Price": None,
                "Day Change $": None,
                "Day Change %": None,
                "1Y High": None,
                "1Y Low": None
            })
            continue

        # last price from 5d history if available, otherwise 1y
        if not hist_5d.empty:
            last_close = float(hist_5d["Close"].iloc[-1])
            if len(hist_5d) > 1:
                prev_close = float(hist_5d["Close"].iloc[-2])
            else:
                prev_close = None
        else:
            last_close = float(hist_1y["Close"].iloc[-1])
            prev_close = None

        if prev_close is not None:
            day_change = last_close - prev_close
            day_change_pct = (day_change / prev_close) * 100
        else:
            day_change = None
            day_change_pct = None

        if not hist_1y.empty:
            year_high = float(hist_1y["Close"].max())
            year_low = float(hist_1y["Close"].min())
        else:
            year_high = None
            year_low = None

        snapshot_rows.append({
            "Ticker": t,
            "Last Price": last_close,
            "Day Change $": day_change,
            "Day Change %": day_change_pct,
            "1Y High": year_high,
            "1Y Low": year_low
        })

    except Exception as e:
        snapshot_rows.append({
            "Ticker": t,
            "Last Price": None,
            "Day Change $": None,
            "Day Change %": None,
            "1Y High": None,
            "1Y Low": None
        })

snapshot_df = pd.DataFrame(snapshot_rows)

if snapshot_df.empty:
    st.error("No snapshot data returned for your tickers. yfinance may be blocked or tickers invalid.")
else:
    st.dataframe(snapshot_df, use_container_width=True)

# --- 3. PRICE HISTORY & BASIC STATS ---

st.subheader("3️⃣ Price History (1 Year) & Basic Stats")

try:
    raw = yf.download(tickers, period="1y", auto_adjust=False, progress=False)

    if raw.empty:
        raise ValueError("Empty data returned from yfinance.")

    # Handle both MultiIndex and normal columns, and both 'Adj Close' / 'Close'
    if isinstance(raw.columns, pd.MultiIndex):
        level0 = raw.columns.get_level_values(0)
        if "Adj Close" in level0:
            price_data = raw["Adj Close"]
        elif "Close" in level0:
            price_data = raw["Close"]
        else:
            raise KeyError("No 'Adj Close' or 'Close' in downloaded data.")
    else:
        if "Adj Close" in raw.columns:
            price_data = raw["Adj Close"]
        elif "Close" in raw.columns:
            price_data = raw["Close"]
        else:
            raise KeyError("No 'Adj Close' or 'Close' in downloaded data.")

except Exception as e:
    st.error(f"Error downloading price data: {e}")
    st.write("Debug – columns returned:", list(raw.columns) if 'raw' in locals() else "No data")
    st.stop()


# Handle single-ticker case (Series → DataFrame)
if isinstance(price_data, pd.Series):
    price_data = price_data.to_frame()

st.write("Debug – price_data shape:", price_data.shape)

if price_data.empty:
    st.error("No historical price data returned (empty DataFrame). This usually means yfinance couldn't reach Yahoo or the tickers are invalid.")
    st.stop()

st.line_chart(price_data)

# Daily returns
returns = price_data.pct_change().dropna()

if returns.empty:
    st.error("Not enough return data to compute statistics.")
    st.stop()

trading_days = 252
mean_returns = returns.mean() * trading_days
volatility = returns.std() * np.sqrt(trading_days)

stats_df = pd.DataFrame({
    "Ticker": price_data.columns,
    "Annualized Return": mean_returns.values,
    "Annualized Volatility": volatility.values
})

stats_df = stats_df.merge(edited_df[["Ticker", "Weight (dec)"]], on="Ticker", how="left")

st.write("📈 Asset-level statistics (raw):")
st.dataframe(stats_df, use_container_width=True)

# --- 4. PORTFOLIO METRICS ---

st.subheader("4️⃣ Portfolio Metrics")

weights = stats_df["Weight (dec)"].fillna(0).values
cov_matrix = returns.cov() * trading_days

portfolio_return = float(np.dot(weights, mean_returns))
portfolio_vol = float(np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights))))

col1, col2 = st.columns(2)
with col1:
    st.metric("Expected Annual Return", f"{portfolio_return:.2%}")
with col2:
    st.metric("Expected Annual Volatility", f"{portfolio_vol:.2%}")

st.write("🔗 Correlation matrix:")
st.dataframe(returns.corr(), use_container_width=True)

# --- 5. FORECASTING ---

st.subheader("5️⃣ Forecast (Deterministic Projection)")

months = years * 12
if portfolio_return <= -1:
    monthly_rate = -1
else:
    monthly_rate = (1 + portfolio_return) ** (1/12) - 1

values = []
current_value = starting_value

for m in range(months + 1):
    values.append(current_value)
    current_value = current_value * (1 + monthly_rate) + monthly_contribution

forecast_index = pd.date_range(start=date.today(), periods=months+1, freq="M")
forecast_series = pd.Series(values, index=forecast_index)

st.line_chart(forecast_series)

st.write(f"📌 After **{years} years**, estimated value: **${forecast_series.iloc[-1]:,.0f}**")

st.caption("v1.3 – Educational use only. If you see empty data/graphs, yfinance may not be able to reach Yahoo Finance from this environment.")
