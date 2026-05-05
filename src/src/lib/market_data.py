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
    """ 
    Fetch historical OHLCV price data for a ticker from Yahoo Finance over an interval-appropriate lookback. 
    The function returns a cleaned DataFrame with a datetime index and only the core pricing and volume columns.

    Args:
        ticker: Symbol string to download historical data for.
        interval: Bar interval supported by yfinance (for example, '1d' or '1h').

    Returns:
        A pandas DataFrame containing cleaned OHLCV data indexed by timestamp, or an empty DataFrame if no data is available.
    """
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
    
def have_with_ict_signal(price_df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """ 
    Apply a configured set of ICT-based technical signals to a historical price DataFrame.
    The function returns an enriched DataFrame containing swing structure, liquidity, displacement, and fair value gap annotations.

    Args:
        price_df: Historical OHLCV price data to which ICT indicators and context will be applied.
        strategy: Strategy configuration dictionary providing filter parameters such as swing window and liquidity lookback.

    Returns:
        A pandas DataFrame with additional columns representing ICT structure, liquidity sweeps, CISD, FVGs, and liquidity context.
    """
    # Extracts configuration parameters from the strategy filters
    filters = strategy.get("filters", {})
    swing_window = int(filters.get("swing_window", 3))
    liquidity_lookback = int(filters.get("liquidity_lookback", 40))
    fvg_min_pct = float(filters.get("fvg_min_pct", 0.001))
    min_displacement_pct = float(filters.get("min_displacement_pct", 0.002))
    
    # Applies a series of ICT technical indicators to the price data
    df = detect_swings(price_df, swing_window=swing_window)
    df = detect_structure_shift(df, min_displacement_pct=min_displacement_pct)
    df = detect_external_liquidity_sweep(df)
    df = detect_cisd(df)
    df = detect_fvg_zones(df, min_gap_pct=fvg_min_pct)
    df = add_liquidity_context(df, liquidity_lookback=liquidity_lookback)
    return df
    
    
def build_summary_row():
    pass

def run_screen():
    pass

