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

def detect_cisd(price_df: pd.DataFrame, max_sequence: int = 5) -> pd.DataFrame:
    df = add_delivery_state(price_df)
    df["bullish_cisd"] = False
    df["bearish_cisd"] = False
    df["cisd_reference_open"] = pd.NA
    df["delivery_direction"] = "neutral"
    
    for idx in range(1, len(df)):
        bearish_sequence_start = None
        bullish_sequence_start = None
        
        up_run = 0
        back = idx - 1
        while back >= 0 and up_run < max_sequence and bool(df.iloc[back]["is_up_close"]):
            bearish_sequence_start = back
            up_run += 1
            back -= 1
        
        down_run = 0
        back = idx - 1
        while back >= 0 and down_run < max_sequence and bool(df.iloc[back]["is_down_close"]):
            bullish_sequence_start = back
            down_run += 1
            back -= 1
        
        current_close = float(df.iloc[idx]["Close"])
        
        if bearish_sequence_start is not None and up_run >= 1:
            reference_open = float(df.iloc[bearish_sequence_start]["Open"])

