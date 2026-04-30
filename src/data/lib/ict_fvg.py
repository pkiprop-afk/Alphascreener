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
        
        bullish_gap = current_high - low_two_bars_back
        bearish_gap = low_two_bars_back - current_high
        
        if high_two_bars_back > 0:
            bullish_gap_pct = bullish_gap / high_two_bars_back
        else:
            bullish_gap_pct = 0.0
        
        if low_two_bars_back > 0:
            bearish_gap_pct = bearish_gap / low_two_bars_back 
        else:
            bearish_gap_pct = 0.0
        
        if bullish_gap > 0 and bullish_gap_pct >= min_gap_pct:
            df.at[df.index[idx], "bullish fvg"] = True
            df.at[df.index[idx], "fvg_bottom"] = high_two_bars_back
            df.at[df.index[idx], "fvg_top"] = current_low
            df.at[df.index[idx], "fvg_gap_pct"] = round(bullish_gap_pct, 6)
        
        if bearish_gap > 0 and bearish_gap_pct >= min_gap_pct:
            df.at[df.index[idx], "bearish_fvg"] = True 
            df.at[df.index[idx], "fvg_top"] = low_two_bars_back
            df.at[df.index[idx], "fvg_bottom"] = current_high
            df.at[df.index[idx], "fvg_gap_pct"] = round(bearish_gap_pct, 6)
    
    return df

def find_recent_fvg_context():
    pass

def price_touches_fvg():
    pass