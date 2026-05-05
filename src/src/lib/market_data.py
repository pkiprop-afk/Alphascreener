import pandas as pd
import streamlit as st 
import yfinance as yf 

from lib.ict_delivery import detect_cisd
from lib.ict_fvg import detect_fvg_zones, find_recent_fvg_context, price_touches_fvg
from lib.ict_liquidity import add_liquidity_context, summarize_liquidity
from lib.ict_structure import detect_external_liquidity_sweep, detect_structure_shift, detect_swings

INTERVAL_PERIOD_MAP = {
    "1d": "2y",
    "1h": "180d",
}

INTERVAL_TRADINGVIEW_MAP = {
    "1d": "D",
    "1h": "60",
}

@st.cache_data(show_spinner=False, ttl=1800)
def fetch_history_for_sticker(ticker: str, interval: str = "1d") -> pd.DataFrame:
    # Determine the lookback period and downloads the raw data from yfinance
    period = INTERVAL_PERIOD_MAP.get(interval, "2y")
    raw_df = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)
    if raw_df.empty:
        return pd.DataFrame()
    
    # This flattens multi-index columns if it is necessary
    if isinstance(raw_df.columns, pd.MultiIndex):
        raw_df.columns = raw_df.columns.get_level_values(0)
    
    # Cleans the data and keeps required columns and drops missing values
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    clean_df = raw_df[required_cols].dropna().copy()
    clean_df.index = pd.to_datetime(clean_df.index)
    return clean_df
    
def build_summary_row():
    pass

def run_screen():
    pass

