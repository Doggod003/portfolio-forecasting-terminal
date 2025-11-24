import streamlit as st

def inject_global_css():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }

        /* ===== Glass / Sticky Header ===== */
        .header-bar {
            width: 100%;
            padding: 0.7rem 1.1rem;
            margin-bottom: 0.9rem;
            border-radius: 14px;

            background: linear-gradient(
                120deg,
                rgba(15, 23, 42, 0.82),
                rgba(15, 23, 42, 0.72)
            );
            border: 1px solid rgba(148, 163, 184, 0.6);
            box-shadow:
                0 18px 45px rgba(15, 23, 42, 0.55),
                0 0 0 1px rgba(15, 23, 42, 0.6);
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
            font-size: 0.75rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: #a5b4fc;
            font-weight: 600;
        }

        .header-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #e5e7eb;
        }

        .header-sub {
            font-size: 0.85rem;
            color: #9ca3af;
        }

        .header-chip {
            font-size: 0.78rem;
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            border: 1px solid rgba(34, 197, 94, 0.7);
            background: radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.24), rgba(22, 163, 74, 0.12));
            color: #bbf7d0;
            font-weight: 600;
            white-space: nowrap;
        }

        /* Tabs / cards / tables / alerts can stay simple for now */
        </style>
        """,
        unsafe_allow_html=True
    )

def render_header():
    st.markdown(
        """
        <div class="header-bar">
            <div class="header-left">
                <div class="header-kicker">Equities • ETFs • Fundamentals</div>
                <div class="header-title">Stock Research Terminal</div>
                <div class="header-sub">
                    Frosted-glass research view for prices, valuation, fundamentals & financials (Yahoo Finance).
                </div>
            </div>
            <div class="header-right">
                <span class="header-chip">Research Mode</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

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
        ticker = st.text_input("Ticker", "AAPL")

    with row1_col2:
        period = st.selectbox(
            "Price history window",
            list(PERIOD_MAP.keys()),
            index=3,
        )

    with row1_col3:
        run_search = st.button("Search", type="primary")

    ticker_input = ticker.strip().upper()

    st.caption(
        "Single place to look up a stock and see price, valuation, fundamentals, and financials. "
        "Data via yfinance / Yahoo Finance."
    )

    return ticker_input, period, run_search, PERIOD_MAP
