import streamlit as st

def inject_global_css():
    st.markdown(
        """
        <style>

        /* ============================================
           GLOBAL WHITE THEME — BASE PAGE COLORS
        ============================================ */

        html, body, .stApp {
            background-color: #ffffff !important;
            color: #111827 !important; /* dark gray for text */
        }

        /* Fix Streamlit’s padding */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            max-width: 1400px !important;
        }


        /* ============================================
           BLOOMBERG-STYLE GLASS HEADER BAR (STICKY)
        ============================================ */

        .header-bar {
            width: 100%;
            padding: 0.9rem 1.2rem;
            margin-bottom: 1.3rem;
            border-radius: 14px;

            /* Glass effect */
            background: linear-gradient(
                120deg,
                rgba(15, 23, 42, 0.82),
                rgba(15, 23, 42, 0.72)
            );
            border: 1px solid rgba(148, 163, 184, 0.6);
            box-shadow:
                0 18px 45px rgba(15, 23, 42, 0.25),
                0 0 0 1px rgba(15, 23, 42, 0.35);
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
            gap: 0.22rem;
        }

        .header-kicker {
            font-size: 0.74rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: #a5b4fc;
            font-weight: 600;
        }

        .header-title {
            font-size: 1.45rem;
            font-weight: 700;
            color: #e5e7eb;
        }

        .header-sub {
            font-size: 0.87rem;
            color: #cbd5e1;
        }

        .header-chip {
            font-size: 0.78rem;
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            border: 1px solid rgba(34, 197, 94, 0.7);
            background: radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.24), rgba(22, 163, 74, 0.12));
            color: #16a34a;
            font-weight: 600;
            white-space: nowrap;
        }


        /* ============================================
           TABS STYLE (Money Themed)
        ============================================ */

        div[role="tablist"] {
            border-bottom: 1px solid #e5e7eb;
            margin-top: 0.5rem;
            gap: 6px;
        }

        button[role="tab"] {
            padding: 0.5rem 1.2rem !important;
            border-radius: 999px !important;
            font-size: 0.9rem;
            border: 1px solid transparent !important;
            background: #f8fafc !important;
            color: #1e293b !important;
            box-shadow: 0 1px 3px rgba(15,23,42,0.06);
            font-weight: 500;
        }

        /* Overview - green tint */
        button[role="tab"]:nth-child(1) { 
            background-color: #ecfdf5 !important; 
            color: #166534 !important; 
        }
        button[role="tab"][aria-selected="true"]:nth-child(1) {
            border-color: #16A34A !important;
            background-color: #d1fae5 !important;
            color: #14532D !important;
        }

        /* Valuation - teal */
        button[role="tab"]:nth-child(2) { 
            background-color: #e0f7f5 !important; 
            color: #0F766E !important;
        }
        button[role="tab"][aria-selected="true"]:nth-child(2) {
            border-color: #0D9488 !important;
            background-color: #ccfbf1 !important;
        }

        /* Fundamentals - gold */
        button[role="tab"]:nth-child(3) {
            background-color: #fef9c3 !important;
            color: #92400E !important;
        }
        button[role="tab"][aria-selected="true"]:nth-child(3) {
            border-color: #D97706 !important;
            background-color: #fde68a !important;
        }

        /* Financials - blue */
        button[role="tab"]:nth-child(4) {
            background-color: #eff6ff !important;
            color: #1D4ED8 !important;
        }
        button[role="tab"][aria-selected="true"]:nth-child(4) {
            border-color: #1D4ED8 !important;
            background-color: #dbeafe !important;
        }


        /* ============================================
           METRIC CARDS (white cards)
        ============================================ */

        div[data-testid="stMetric"] {
            background: #ffffff !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            border: 1px solid #e5e7eb !important;
            box-shadow: 0 2px 6px rgba(15,23,42,0.08) !important;
            color: #1f2937 !important;
        }


        /* ============================================
           TABLES — modern card style
        ============================================ */
        div[data-testid="stDataFrame"] {
            background: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 12px !important;
            padding: 10px !important;
            box-shadow: 0 1px 4px rgba(15,23,42,0.06) !important;
        }


        /* Alerts (info boxes) */
        div[data-testid="stAlert"] {
            border-radius: 10px !important;
            border: 1px solid #c7d2fe !important;
            background-color: #f0f4ff !important;
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
                <div class="header-kicker">Equities • ETFs • Fundamentals</div>
                <div class="header-title">Stock Research Terminal</div>
                <div class="header-sub">
                    Research-grade price history, valuation, fundamentals & financials (Yahoo Finance API).
                </div>
            </div>
            <div class="header-right">
                <span class="header-chip">Research Mode</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_controls():
    col1, col2, col3 = st.columns([2.4, 2, 1])

    with col1:
        ticker = st.text_input("Ticker", "AAPL", key="main_ticker")

    with col2:
        period = st.selectbox(
            "Price Window",
            ["1M", "3M", "6M", "1Y", "5Y", "Max"],
            index=3,
            key="period_select"
        )

    with col3:
        run = st.button("Search", type="primary", key="search_btn")

    period_map = {
        "1M": "1mo",
        "3M": "3mo",
        "6M": "6mo",
        "1Y": "1y",
        "5Y": "5y",
        "Max": "max",
    }

    return ticker.strip().upper(), period, run, period_map
