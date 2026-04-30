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

def summarize_liquidity():
    pass 

