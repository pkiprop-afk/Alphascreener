import pandas as pd 

def detect_fvg_zones(price_df: pd.DataFrame, min_gap_pct: float = 0.001) -> pd.DataFrame:
    df = price_df.copy()
    df["bullish_fvg"] = False
    df["bearish_fvg"] = False
    df["fvg_top"] = pd.NA
    df["fvg_bottom"] = pd.NA
    df["fvg_gap_pct"] = 0.0
    
    for idx in range(2, len(df)):
        high_two_bars_back = float(df.iloc[idx - 2]["High"])
        low_two_bars_back = float(df.iloc[idx - 2]["Low"])
        current_low = float(df.iloc[idx]["Low"])
        current_high = float(df.iloc[idx]["High"])

def find_recent_fvg_context():
    pass

def price_touches_fvg():
    pass