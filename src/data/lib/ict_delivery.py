import pandas as pd 

def classify_candle_patterns(price_df: pd.DataFrame) -> pd.DataFrame:
    df = price_df.copy()
    df["candle_pattern"] = "neutral"
    
    for idx in range(len(df)):
        row = df.iloc[idx]
        open_price = float(row["Open"])
        high_price = float(row["High"])
        low_price = float(row["Low"])
        close_price = float(row["Close"])
        body = abs(close_price - open_price)
        full_range = max(high_price - low_price, 1e-9)
        upper_wick = high_price - max(open_price, close_price)
        lower_wick = min(open_price, close_price) - low_price
        
        pattern = "neutral"
        if close_price > open_price and body / full_range >= 0.6:
            pattern = "Bullish displacement"
        elif close_price < open_price and body / full_range >= 0.6:
            pattern = "Bearish displacement"
        elif close_price > open_price and lower_wick > body:
            pattern = "Bullish rejection"
        elif close_price < open_price and upper_wick > body:
            pattern = "bearish_rejection"
        
        df.at[df.index[idx], "candle_pattern"] = pattern
    
    return df

def add_delivery_state(price_df: pd.DataFrame) -> pd.DataFrame:
    df = price_df.copy()
    df["is_up_close"] = df["Close"] > df["Open"]
    df["is_down_close"] = df["Close"] < df["Open"]
    return df

def detect_cisd():
    pass

