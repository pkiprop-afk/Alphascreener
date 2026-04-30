import pandas as pd 

def detect_fvg_zones(price_df: pd.DataFrame, min_gap_pct: float = 0.001) -> pd.DataFrame:
    df = price_df.copy()
    
    # Initializing columns
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
        
        # Bullish FVG is the gap between current Low and previous High
        bullish_gap = current_low - high_two_bars_back
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

def find_recent_fvg_context(price_df: pd.DataFrame, end_index: int, lookback: int = 12) -> dict:
    start_index = max(0, end_index - lookback)
    recent = price_df.iloc[start_index : end_index + 1]
    
    bullish = recent[recent["bullish_fvg"] == True]
    bearish = recent[recent["bearish_fvg"] == True]
    
    latest_bullish = None if bullish.empty else bullish.iloc[-1].to_dict()
    latest_bearish = None if bearish.empty else bearish.iloc[-1].to_dict()
    
    return{
        "has_recent_bullish_fvg": latest_bullish is not None,
        "has_recent_bearish_fvg": latest_bearish is not None,
        "latest_bullish_fvg": latest_bullish,
        "latest_bearish_fvg": latest_bearish,
    }
    

def price_touches_fvg(price_row: pd.Series, fvg_payload: dict | None) -> bool:
    if not fvg_payload:
        return False
    
    top = fvg_payload.get("fvg_top")
    bottom =  fvg_payload.get("fvg_bottom")
    if pd.isna(top) or pd.isna(bottom):
        return False
    
    candle_high = float(price_row["High"])
    candle_low = float(price_row["Low"])
    zone_low = min(float(top), float(bottom))
    zone_high = max(float(top), float(bottom))
    return candle_low <= zone_high and candle_high >= zone_low