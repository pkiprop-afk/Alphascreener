import pandas as pd 

from lib.ict_fvg import find_recent_fvg_context, price_touches_fvg
from lib.ict_structure import find_recent_external_liquidity

def add_liquidity_context(price_df: pd.DataFrame, liquidity_lookback: int = 40) -> pd.DataFrame:
    df = price_df.copy()
    df["external_high"] = pd.NA
    df["external_low"] = pd.NA
    df["touches_internal_liquidity"] = False
    df["touches_external_high"] = False
    df["touches_external_low"] = False
    
    for idx in range(len(df)):
        external = find_recent_external_liquidity(df, idx, lookback=liquidity_lookback)
        external_high = external.get("external_high")
        external_low = external.get("external_low")
        df.at[df.index[idx], "external_high"] = external_high
        df.at[df.index[idx], "external_low"] = external_low
        
        row = df.iloc[idx]
        candle_high = float(row["High"])
        candle_low = float(row["Low"])
        
        if external_high is not None:
            df.at[df.index[idx], "touches_external_high"] = candle_high >= float(external_high)
        if external_low is not None:
            df.at[df.index[idx], "touches_external_low"] = candle_low <= float(external_low)
        
        recent_fvg_context = find_recent_fvg_context(df, idx, lookback=min(liquidity_lookback, 12))
        has_internal_touch = price_touches_fvg(row, recent_fvg_context.get("latest_bullish_fvg")) or price_touches_fvg(
            row, recent_fvg_context.get("latest_bearish_fvg")
        )
        df.at[df.index[idx], "touches_internal_liquidity"] = has_internal_touch
        
    return df

def summarize_liquidity(price_df: pd.DataFrame, end_index: int) -> dict:
    row = price_df.iloc[end_index]
    return {
        "external_high": row.get("external_high"),
        "external_low": row.get("external_low"),
        "touches_internal_liquidity": bool(row.get("touches_internal_liquidity", False)),
        "touches_external_high": bool(row.get("touched_external_high", False)),
        "touches_external_low": bool(row.get("touches_external_low", False)),
    }
