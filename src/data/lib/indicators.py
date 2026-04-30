import pandas as pd 

def calculate_rsi(close_series: pd.Series, window: int = 14) -> pd.Series:
    """ 
    Compute the Relative Strength Index (RSI) for a series of closing prices.
    The function returns a smoothed momentum oscillator scaled between 0 and 100.

    Args:
        close_series: Series of closing prices indexed over time.
        window: Lookback period used to calculate average gains and losses.

    Returns:
        A pandas Series containing the RSI values aligned with the input index.
    """
    delta = close_series.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    
    average_gain = gains.rolling(window=window, min_periods=window).mean()
    average_loss = losses.rolling(window=window, min_periods=window).mean()
    
    rs = average_gain / average_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def add_indicators(price_df: pd.DataFrame) -> pd.DataFrame:
    """ 
    Add common technical indicators and derived metrics to a price DataFrame.
    The function returns a new DataFrame containing moving averages, volume statistics, and momentum measures.

    Args:
        price_df: OHLCV price data with at least 'Close', 'High', and 'Volume' columns.

    Returns:
        A copy of the input DataFrame with additional columns for moving averages, relative volume, RSI, and 52-week high statistics.
    """
    df = price_df.copy()
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df["AvgVolume20"] = df["Volume"].rolling(window=20).mean()
    df["RelVolume"] = df["Volume"]  / df["AvgVolume20"]
    df["RSI14"] = calculate_rsi(df["Close"], window=14)
    df["High52Week"] = df["High"].rolling(window=min(len(df), 252), min_periods=1).max()
    df["PctBelow52WHigh"] = ((df["High52Week"] - df["Close"]) / df["High52Week"]) * 100
    return df

def build_strategy_from_inputs(
    price_min: float,
    price_max: float,
    rsi_min: int,
    rsi_max: int,
    min_rel_volume: float,
    price_above_sma20: bool,
    price_above_sma50: bool,
    max_pct_from_52w_high: int,
    lookback_period: str,
    universe_size: int,
) -> dict:
    return {
        "price_min": price_min,
        "price_max": price_max,
        "rsi_min": rsi_min,
        "rsi_max": rsi_max,
        "min_rel_volume": min_rel_volume,
        "price_above_sma20": price_above_sma20,
        "price_above_sma50": price_above_sma50,
        "max_pct_from_52w_high": max_pct_from_52w_high,
        "lookback_period": lookback_period,
        "universe_size": universe_size,
    }

def passes_screen(latest_row: pd.Series, criteria: dict) -> bool:
    close_price = float(latest_row["Close"])
    price_ok = criteria["price_min"] <= close_price <= criteria["price_max"]
    rsi_ok = criteria["rsi_min"] <= float(latest_row["RSI14"] <= criteria["rsi_max"])
    volume_ok = float(latest_row["RelVolume"]) >= criteria["min_rel_volume"]
    high_ok = float(latest_row["PctBelow52WHigh"]) <= criteria["max_pct_from_52w_high"]
    
    sma20_ok = True
    if criteria["price_above_sma20"]:
        sma20_ok = close_price