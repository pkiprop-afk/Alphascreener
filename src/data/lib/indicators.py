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
    price
):
    pass

def passes_screen():
    pass