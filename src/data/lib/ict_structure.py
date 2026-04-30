import pandas as pd 

def detect_swings(price_df: pd.DataFrame, swing_window: int = 3) -> pd.DataFrame:
    df = price_df.copy()
    df["swing_high"] = False
    df["swing_low"] =False
    df["swing_high_value"] = pd.NA
    
    for idx in range(swing_window, len(df) - swing_window):
        high_window = df.iloc[idx - swing_window : idx + swing_window + 1]["High"]
        low_window = df.iloc[idx - swing_window : idx + swing_window + 1["Low"]]
        current_high = float(df.iloc[idx]["High"])
        current_low = float(df.iloc[idx]["Low"])
        
        if current_high == float(high_window.max()):
            df.at[df.index[idx], "swing_high"] = True 
            df.at[df.index[idx], "swing_high_value"] = current_high
        
        if current_low == float(low_window.min()):
            df.at[df.index[idx], "swing_low"] = True
            df.at[df.index[idx], "swing_low_value"] = current_low
    
    return df

def add_previous_swing_levels(price_df: pd.DataFrame) -> pd.DataFrame:
    df = price_df.copy()
    previous_high = pd.NA
    previous_low = pd.NA
    high_values = []
    low_values = []
    
    for _, row in df.iterrows():
        high_values.append(previous_high)
        low_values.append(previous_low)
        
        if bool(row.get("swing_high", False)):
            previous_high = float(row["High"])
        if bool(row.get("swing_low", False)):
            previous_low = float(row["Low"])
    
    df["previous_swing_high"] = high_values
    df["previous_swing_low"] = low_values
    
    return df

def detect_structure_shift(price_df: pd.DataFrame, min_displacement_pct: float = 0.002) -> pd.DataFrame:
    df = add_previous_swing_levels(price_df)
    df["bullish_structure_shift"] = False
    df["bearish_structure_shift"] = False
    df["structure_direction"] = "neutral"

def find_recent_external_liquidity():
    pass

def detect_external_liquidity_sweep():
    pass

