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
        lower_wick = min(open_price)

def add_delivery_state():
    pass

def detect_cisd():
    pass

