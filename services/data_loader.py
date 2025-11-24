import yfinance as yf
import pandas as pd
import streamlit as st

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
