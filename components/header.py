import streamlit as st

def inject_global_css():
    st.markdown(
        """
        <style>
        /* ============================
           Layout / Page Base
        ============================= */
        html, body, .stApp {
            background-color: #ffffff !important; /* near-black */
            color: #e5e7eb !important;
        }

        .block-container {
            padding-top: 1.0rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        /* ============================
           GLASS / STICKY HEADER BAR
        ============================= */
        .header-bar {
            width: 100%;
            padding: 0.7rem 1.1rem;
            margin-bottom: 0.9rem;
            border-radius: 12px;

            background: linear-gradient(
                120deg,
                rgba(15, 23, 42, 0.92),
                rgba(15, 23, 42, 0.78)
            );
            border: 1px solid rgba(148, 163, 184, 0.7);
            box-shadow:
                0 18px 45px rgba(15, 23, 42, 0.75),
                0 0 0 1px rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);

            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.2rem;

            position: sticky;
            top: 0;
            z-index: 999;
        }

        .header-left {
            display: flex;
            flex-direction: column;
            gap: 0.18rem;
        }

        .header-kicker {
            font-size: 0.7rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: #a5b4fc;
            font-weight: 600;
        }

        .header-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #f9fafb;
        }

        .header-sub {
            font-size: 0.85rem;
            color: #9ca3af;
        }

        .header-chip {
            font-size: 0.78rem;
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            border: 1px solid rgba(34, 197, 94, 0.8);
            background: radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.32), rgba(22, 163, 74, 0.18));
            color: #bbf7d0;
            font-weight: 600;
            white-space: nowrap;
        }

        /* ============================
           Controls row (Ticker / Period)
        ============================= */
        label {
            color: #e5e7eb;
            font-size: 0.82rem;
        }

        input, select, textarea {
            color-scheme: dark;
        }

        div[data-baseweb="input"] input {
            background-color: #020617 !important;
            border-radius: 6px !important;
            border: 1px solid #334155 !important;
            color: #e5e7eb !important;
            font-size: 0.9rem !important;
        }

        div[data-baseweb="select"] > div {
            background-color: #020617 !important;
            border-radius: 6px !important;
            border: 1px solid #334155 !important;
            color: #e5e7eb !important;
            font-size: 0.9rem !important;
        }

        button[kind="primary"] {
            background: linear-gradient(135deg, #22c55e, #16a34a) !important;
            color: #020617 !important;
            border-radius: 6px !important;
            border: 0 !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
        }

        /* ============================
           Tabs – dark chips
        ============================= */
        div[role="tablist"] {
            border-bottom: 1px solid #1e293b;
            margin-bottom: 0.8rem;
            gap: 6px;
        }

        button[role="tab"] {
            padding: 0.3rem 0.9rem !important;
            border-radius: 999px !important;
            font-size: 0.85rem;
            border: 1px solid transparent !important;
            box-shadow: none !important;
            font-weight: 500;
            margin-right: 4px;
            background-color: #020617 !important;
            color: #94a3b8 !important;
        }

        button[role="tab"][aria-selected="true"] {
            background: #0f172a !important;
            border-color: #22c55e !important;
            color: #e5e7eb !important;
        }

        /* ============================
           Metrics – dark cards
        ============================= */
        div[data-testid="stMetric"] {
            background: #020617;
            border-radius: 10px;
            padding: 10px 14px;
            border: 1px solid #1e293b;
            box-shadow: 0 0 0 1px rgba(15,23,42,0.8);
        }

        div[data-testid="stMetric"] > label {
            font-size: 0.75rem;
            color: #9ca3af;
        }

        div[data-testid="stMetric"] span {
            font-size: 1rem;
        }

        /* ============================
           DataFrames – dark grid
        ============================= */
        div[data-testid="stDataFrame"] {
            border-radius: 10px;
            border: 1px solid #1e293b;
            box-shadow: 0 0 0 1px rgba(15,23,42,0.9);
            padding: 4px;
            background: #020617;
        }

        /* Alerts */
        div[data-testid="stAlert"] {
            border-radius: 8px;
            border: 1px solid #1d4ed8;
            background-color: rgba(30, 64, 175, 0.15);
            color: #e5e7eb;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_header():
    st.markdown(
        """
        <div class="header-bar">
            <div class="header-left">
                <div class="header-kicker">EQUITIES • ETFs • FUNDAMENTALS</div>
                <div class="header-title">Stock Research Terminal</div>
                <div class="header-sub">
                    Bloomberg-style research view for price, valuation, fundamentals & financials (Yahoo Finance).
                </div>
            </div>
            <div class="header-right">
                <span class="header-chip">Research Mode</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Controls: Ticker / Period / Search
PERIOD_MAP = {
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y",
    "5Y": "5y",
    "Max": "max",
}

def render_controls():
    row1_col1, row1_col2, row1_col3 = st.columns([2, 2, 1])

    with row1_col1:
        ticker = st.text_input("Ticker", "AAPL", key="ticker_input")

    with row1_col2:
        period = st.selectbox(
            "Price history window",
            list(PERIOD_MAP.keys()),
            index=3,
            key="period_select"
        )

    with row1_col3:
        run_search = st.button("Search", type="primary", key="search_btn")

    ticker_input = ticker.strip().upper()

    st.caption(
        "Single place to look up a stock and see price, valuation, fundamentals, and financials. "
        "Data via yfinance / Yahoo Finance."
    )

    return ticker_input, period, run_search, PERIOD_MAP
