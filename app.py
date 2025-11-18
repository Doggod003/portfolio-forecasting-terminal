import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt

st.set_page_config(page_title="Sam's Analyst Terminal", layout="wide")

st.title("📊 Sam's Financial Analyst App (v1.1)")

st.caption("Uses Yahoo Finance data via yfinance – good for research & school, not a trading terminal.")

# Sidebar – global inputs
st.sidebar.header("Portfolio Settings")

# Shorter default history so it's faster and more visible
start_date = st.sidebar.date_input("Historical data from:", dt.date.today() - dt.timedelta(days=365))
end_date = st.sidebar.date_input("To:", dt.date.today())

starting_value = st.sidebar.number_input("Starting portfolio value ($)", 1000.0, step=500.0)
monthly_contribution = st.sidebar.number_input("Monthly contribution ($)", 0.0, step=50.0)
years = st.sidebar.slider("Forecast horizon (years)", 1, 40, 10)

st.sidebar.markdown("---")
st.sidebar.write("Edit your tickers and weights below 👇")

# --- 1. TICKER INPUT & PORTFOLIO TABLE ---

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
else:
    edited_df["Weight (dec)"] = edited_df["Weight %"] / total_weight

# --- 2. TICKER SNAPSHOT TABLE (CURRENT DATA) ---

st.subheader("2️⃣ Ticker Snapshot – Current Prices & Key Stats")

snapshot_rows = []

for t in tickers:
    try:
        tk = yf.Ticker(t)
        info = tk.fast_info  # lightweight summary

        last_price = info.get("last_price", None)
        prev_close = info.get("previous_close", None)
        year_high = info.get("year_high", None)
        year_low = info.get("year_low", None)
        market_cap = info.get("market_cap", None)

        if last_price is None:
            # fallback to history if fast_info missing
            hist = tk.history(period="5d")
            if not hist.empty:
                last_price = hist["Close"].iloc[-1]
                if len(hist) > 1:
                    prev_close = hist["Close"].iloc[-2]

        if last_price is not None and prev_close is not None:
            day_change = last_price - prev_close
            day_change_pct = (day_change / prev_close) * 100
        else:
            day_change = None
            day_change_pct = None

        snapshot_rows.append({
            "Ticker": t,
            "Last Price ($)": last_price,
            "Day Change ($)": day_change,
            "Day Change (%)": day_change_pct,
            "52W High": year_high,
            "52W Low": year_low,
            "Market Cap": market_cap
        })
    except Exception as e:
        snapshot_rows.append({
            "Ticker": t,
            "Last Price ($)": None,
            "Day Change ($)": None,
            "Day Change (%)": None,
            "52W High": None,
            "52W Low": None,
            "Market Cap": None
        })

snapshot_df = pd.DataFrame(snapshot_rows)

if snapshot_df.empty:
    st.error("No snapshot data returned for your tickers. Check symbols or try again later.")
else:
    st.dataframe(
        snapshot_df.style.format({
            "Last Price ($)": "{:.2f}",
            "Day Change ($)": "{:.2f}",
            "Day Change (%)": "{:.2f}",
            "52W High": "{:.2f}",
            "52W Low": "{:.2f}",
            "Market Cap": "{:,.0f}"
        }),
        use_container_width=True
    )

# --- 3. PRICE HISTORY & BASIC STATS ---

st.subheader("3️⃣ Price History & Basic Stats")

try:
    price_data = yf.download(tickers, start=start_date, end=end_date)["Adj Close"]
except Exception as e:
    st.error(f"Error downloading price data: {e}")
    st.stop()

if isinstance(price_data, pd.Series):
    price_data = price_data.to_frame()

if price_data.empty:
    st.error("No historical price data returned. Try a different date range or check tickers.")
    st.stop()

st.line_chart(price_data)

# Daily returns
returns = price_data.pct_change().dropna()

if returns.empty:
    st.error("Not enough return data to compute statistics. Try expanding the date range.")
    st.stop()

# Annualized stats
trading_days = 252
mean_returns = returns.mean() * trading_days
volatility = returns.std() * np.sqrt(trading_days)

stats_df = pd.DataFrame({
    "Ticker": price_data.columns,
    "Annualized Return": mean_returns.values,
    "Annualized Volatility": volatility.values
})

stats_df = stats_df.merge(edited_df[["Ticker", "Weight (dec)"]], on="Ticker", how="left")

st.write("📈 Asset-level statistics:")
st.dataframe(stats_df.style.format({
    "Annualized Return": "{:.2%}",
    "Annualized Volatility": "{:.2%}",
    "Weight (dec)": "{:.2%}"
}))

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
st.dataframe(returns.corr())

# --- 5. FORECASTING ---

st.subheader("5️⃣ Forecast (Deterministic Projection)")

months = years * 12
if portfolio_return <= -1:
    monthly_rate = -1  # guardrail
else:
    monthly_rate = (1 + portfolio_return) ** (1/12) - 1

values = []
current_value = starting_value

for m in range(months + 1):
    values.append(current_value)
    current_value = current_value * (1 + monthly_rate) + monthly_contribution

forecast_index = pd.date_range(start=dt.date.today(), periods=months+1, freq="M")
forecast_series = pd.Series(values, index=forecast_index)

st.line_chart(forecast_series)

st.write(f"📌 After **{years} years**, estimated value: **${forecast_series.iloc[-1]:,.0f}**")

st.caption("v1.1 – Educational use only. Data sourced via yfinance/Yahoo Finance; not guaranteed real-time or perfectly accurate.")
