import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt

st.set_page_config(page_title="Sam's Analyst Terminal", layout="wide")

st.title("📊 Sam's Financial Analyst App (v1)")

# Sidebar – global inputs
st.sidebar.header("Portfolio Settings")

start_date = st.sidebar.date_input("Historical data from:", dt.date(2018, 1, 1))
end_date = st.sidebar.date_input("To:", dt.date.today())

starting_value = st.sidebar.number_input("Starting portfolio value ($)", 1000.0, step=500.0)
monthly_contribution = st.sidebar.number_input("Monthly contribution ($)", 0.0, step=50.0)
years = st.sidebar.slider("Forecast horizon (years)", 1, 40, 10)

st.sidebar.markdown("---")
st.sidebar.write("Enter your tickers and weights on the main page 👇")

# --- TICKER INPUT & PORTFOLIO TABLE ---

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

# Normalize weights
edited_df["Weight %"] = edited_df["Weight %"].fillna(0)
total_weight = edited_df["Weight %"].sum()
if total_weight == 0:
    st.warning("Total weight is 0%. Adjust your weights.")
else:
    edited_df["Weight (dec)"] = edited_df["Weight %"] / total_weight

tickers = [t.strip().upper() for t in edited_df["Ticker"] if t.strip() != ""]

if len(tickers) == 0:
    st.stop()

# --- FETCH PRICE DATA ---

st.subheader("2️⃣ Price History & Basic Stats")

data = yf.download(tickers, start=start_date, end=end_date)["Adj Close"]

if isinstance(data, pd.Series):
    data = data.to_frame()

st.line_chart(data)

# Daily returns
returns = data.pct_change().dropna()

# Annualized stats
trading_days = 252
mean_returns = returns.mean() * trading_days
volatility = returns.std() * np.sqrt(trading_days)

stats_df = pd.DataFrame({
    "Ticker": data.columns,
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

# --- PORTFOLIO CALCULATIONS ---

st.subheader("3️⃣ Portfolio Metrics")

weights = stats_df["Weight (dec)"].values
cov_matrix = returns.cov() * trading_days

portfolio_return = np.dot(weights, mean_returns)
portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))

col1, col2 = st.columns(2)
with col1:
    st.metric("Expected Annual Return", f"{portfolio_return:.2%}")
with col2:
    st.metric("Expected Annual Volatility", f"{portfolio_vol:.2%}")

st.write("🔗 Correlation matrix:")
st.dataframe(returns.corr())

# --- FORECASTING ---

st.subheader("4️⃣ Forecast (Deterministic)")

months = years * 12
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

st.caption("v1 – for personal & educational use only. Not financial advice.")

