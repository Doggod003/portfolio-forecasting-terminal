import streamlit as st
import pandas as pd
import numpy as np

from components.header import inject_global_css, render_header, render_controls
from services.data_loader import load_ticker_data

st.set_page_config(page_title="Stock Research Terminal", layout="wide")

# Global styles + header
inject_global_css()
render_header()

# Controls (ticker + period)
ticker_input, period, run_search, period_map = render_controls()
