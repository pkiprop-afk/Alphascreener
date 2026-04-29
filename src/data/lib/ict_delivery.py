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
        full_range = 

def add_delivery_state():
    pass

def detect_cisd():
    pass

