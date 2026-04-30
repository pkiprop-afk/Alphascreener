import pandas as pd 

def calculate_rsi(close_series: pd.Series, window: int = 14) -> pd.Series:
    delta = close_series.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    
    average_gain = gains.rolling(window=window, min_periods=window).mean()
    average_loss = losses.rolling(window=window, min_periods=window).mean()
    
    rs = average_gain / average_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def add_indicators(price_df: pd.DataFrame) -> pd.DataFrame:
    df = price_df.copy()
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df["AvgVolume20"] = df["Volume"].rolling(window=20).mean()
    df["RelVolume"] = df["Volume"]  / df["AvgVolume20"]
    df["RSI14"]
def build_strategy_from_inputs():
    pass

def passes_screen():
    pass