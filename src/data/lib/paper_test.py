import math

import pandas as pd 

def build_trade_record(entry_index: int, entry_time, side: str, entry_price: float, stop_price: float, target_price: float) -> dict:
    return{
        "entry_index": entry_index,
        "entry_time": str(entry_time),
        "side": side,
        "entry price": round(entry_price, 4),
        "stop-price": round(stop_price, 4),
        "target_price"
        
    }
    

def resolve_trade():
    pass

def summarize_backtest():
    pass

def run_backtest_from_signals():
    pass
