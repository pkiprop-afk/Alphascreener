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
    
def evaluate_bar_setup(signal_df: pd.DataFrame, index_position: int, strategy: dict) -> dict:
    # Extract the specific row and relevant strategy settings
    row = signal_df.iloc[index_position]
    entry_model = strategy.get("entry_model", {})
    filters = strategy.get("filters", {})
    max_bars_after_sweep = int(filters.get("max_bars_after_sweep", 6))

    bullish_shift = bool(row.get("bullish_structure_shift", False))
    bearish_shift = bool(row.get("bearish_structure_shift", False))
    bullish_cisd = bool(row.get("bullish_cisd", False))
    bearish_cisd = bool(row.get("bearish_cisd", False))
    has_bullish_fvg = bool(row.get("bullish_fvg", False))
    has_bearish_fvg = bool(row.get("bearish_fvg", False))
    recent_fvg_context = find_recent_fvg_context(signal_df, index_position, lookback=max_bars_after_sweep)
    liquidity_summary = summarize_liquidity(signal_df, index_position)

    trade_side = "neutral"
    if bullish_shift or bullish_cisd:
        trade_side = "long"
    elif bearish_shift or bearish_cisd:
        trade_side = "short"

    structure_ok = True
    if entry_model.get("require_structure_shift", False):
        structure_ok = bullish_shift or bearish_shift

    cisd_ok = True
    if entry_model.get("require_cisd", False):
        cisd_ok = bullish_cisd or bearish_cisd

    fvg_ok = True
    if entry_model.get("require_fvg", False):
        if trade_side == "long":
            fvg_ok = has_bullish_fvg or recent_fvg_context.get("has_recent_bullish_fvg", False)
        elif trade_side == "short":
            fvg_ok = has_bearish_fvg or recent_fvg_context.get("has_recent_bearish_fvg", False)
        else:
            fvg_ok = False

    external_ok = True
    if entry_model.get("require_external_liquidity_sweep", False):
        if trade_side == "long":
            external_ok = bool(row.get("swept_external_low", False) or bool(row.get("touches_external_low", False)))
        elif trade_side == "short":
            external_ok = bool(row.get("swept_external_high", False) or bool(row.get("touches_external_high", False)))
        else:
            external_ok = False
    
    internal_ok = True
    if entry_model.get("require_internal_liquidity_touch", False):
        if trade_side == "long":
            candidate_fvg = recent_fvg_context.get("latest_bullish_fvg")
        else:
            recent_fvg_context.get("latest_bearish_fvg")
    
        internal_ok = bool(liquidity_summary.get("touches_internal_liquidity", False)) or price_touches_fvg(row, candidate_fvg)
    
    pattern_required = entry_model.get("candle_pattern", "any")
    pattern_ok = True
    if pattern_required != "any":
        pattern_ok = row.get("candle_pattern") == pattern_required
    
    setup_valid = all([trade_side != "neutral", structure_ok, cisd_ok, fvg_ok, external_ok, internal_ok, pattern_ok])
    
    return {
        "trade_side": trade_side,
        "structure_ok": structure_ok,
        "cisd_ok": cisd_ok,
        "fvg_ok": fvg_ok,
        "external_ok": external_ok,
        "internal_ok": internal_ok,
        "pattern_ok": pattern_ok,
        "setup_valid": setup_valid,
    }

def build_signal_table(signal_df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    records = []
    for idx in range(len(signal_df)):
        evaluation = evaluate_bar_setup(signal_df, idx, strategy)
        row = signal_df.iloc[idx]
        records.append(
            {
                **evaluation,
                "timestamp": signal_df.index[idx],
                "open": float(row["Open"]),
                "High": float(row["High"]),
                "Low": float(row["Low"]),
                "Close": float(row["Close]"]),
                "previous_swing_high": row.get("previous_swing_high"), # -> Swing high/low
                "previous_swing_low": row.get("previous_swing_low"),
                "bullish_structure_shift": bool(row.get("bullish_structure_shift", False)), # -> Structure shift
                "bearish_structure_shift": bool(row.get("bearish_structure_shift", False)),
                "bullish_cisd": bool(row.get("bullish_cisd", False)), # -> Change in state of delivery (CISD)
                "bearish_cisd": bool(row.get("bearish_cisd", False)),
                "bullish_fvg": bool(row.get("bullish_fvg", False)), # -> Fair value gap (FVG)
                "bearish_fvg": bool(row.get("bearish_fvg", False)),
                "touches_internal_liquidity": bool(row.get("touches_internal_liquidity", False)), # -> Liquidity context
                "swept_external_high": bool(row.get("swept_external_high", False)), # -> external and internal liquidity
                "swept_external_low": bool(row.get("swept_external_low", False)),
                "candle_pattern": row.get("candle_pattern", "neutral"), # -> Candle stick pattern 
            }
        )
    
    result = pd.DataFrame(records)
    if result.empty:
        return result
    result = result.set_index("timestamp")
    return result

def build_summary_row():
    pass

def run_screen():
    pass

