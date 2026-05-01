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
    
    exit_index = final_index
    exit_price = float(price_df.iloc[final_index]["Close"])
    outcome = "time_exit"
    
    for idx in range(entry_index + 1, final_index + 1):
        row = price_df.iloc[idx]
        high_price = float(row["High"])
        low_price = float(row["Low"])
        
        stop_hit = (side == "long" and low_price <= stop_price) or (side == "short" and high_price >= stop_price)
        target_hit = (side == "long" and high_price >= target_price) or (side == "short" and low_price <= target_price)
        
        if stop_hit:
            exit_index = idx
            exit_price = stop_price
            outcome = "stop"
            break 
        
        if target_hit:
            exit_index = idx
            exit_price = target_price
            outcome = "target"
            break
    
    pnl = (exit_price - entry_price) if side == "long" else (entry_price - exit_price)
    pnl_r = pnl / risk
    
    return{
        **trade,
        "exit_index": exit_index,
        "exit_time": str(price_df.index[exit_index]),
        "exit_price": round(exit_price, 4),
        "outcome":  outcome,
        "pnl_r": round(pnl_r, 2),
    }

def summarize_backtest(trades: list[dict]) -> dict:
    if not trades:
        return{
            "total_trades": 0,
            "win_rate": 0.0,
            "average_r": 0.0,
            "total_r": 0.0,
            "profit_factor": 0.0,
        }
    
    pnl_values = [float(item["pnl_r"]) for item in trades]
    total_trades = len(pnl_values)
    
    wins = [ pnl for pnl in pnl_values if pnl > 0]
    gross_profit = sum(wins)
    gross_loss = abs(sum(pnl for pnl in pnl_values if pnl < 0))
    total_r = sum(pnl_values)
    
    win_rate = (len(wins) / total_trades) * 100

def run_backtest_from_signals():
    pass
