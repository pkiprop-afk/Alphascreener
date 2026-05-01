import math

import pandas as pd 

def build_trade_record(entry_index: int, entry_time, side: str, entry_price: float, stop_price: float, target_price: float) -> dict:
    return{
        "entry_index": entry_index,
        "entry_time": str(entry_time),
        "side": side,
        "entry price": round(entry_price, 4),
        "stop-price": round(stop_price, 4),
        "target_price": round(target_price, 4),
    }

def resolve_trade(price_df: pd.DataFrame, trade: dict, max_holding_bars: int) -> dict:
    entry_index = trade["entry_index"]
    side = trade["side"]
    stop_price = float(trade["stop_price"])
    target_price = float(trade["target_price"])
    entry_price = float(trade["entry_price"])    
    
    risk = max(abs(entry_price - stop_price), 1e-9)
    final_index = min(len(price_df) - 1, entry_index + max_holding_bars)
    

def summarize_backtest():
    pass

def run_backtest_from_signals():
    pass
