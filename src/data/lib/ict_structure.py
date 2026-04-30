import pandas as pd 

def detect_swings(price_df: pd.DataFrame, swing_window: int = 3) -> pd.DataFrame:
    df = price_df.copy()
    df["swing_high"] = False
    df["swing_low"] =False
    df["swing_high_value"] = pd.NA
    
    for idx in range(swing_window, len(df) - swing_window):
        high_window = df.iloc[idx - swing_window : idx + swing_window + 1]["High"]

def add_previous_swing_levels():
    pass

def detect_structure_shift():
    pass

def find_recent_external_liquidity():
    pass

def detect_external_liquidity_sweep():
    pass

