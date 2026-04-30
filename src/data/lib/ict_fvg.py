import pandas as pd 

def detect_fvg_zones(price_df: pd.DataFrame, min_gap_pct: float = 0.001) -> pd.DataFrame:
    df = price_df.copy()
    df["bullish_fvg"] = False
    df["bearish_fvg"] = False
    df["fvg_top"] = pd.NA

def find_recent_fvg_context():
    pass

def price_touches_fvg():
    pass