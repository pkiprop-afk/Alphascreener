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
    average_r = total_r / total_trades
    
    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = math.inf
    else:
        profit_factor = 0.0
    
    return{
        "total_trades": total_trades,
        "win_rate": round(win_rate, 2),
        "average_r": round(average_r, 2),
        "total_r": round(total_r, 2),
        "profit_fator": round(profit_factor, 2) if math.isfinite(profit_factor) else "Infinity",
    }

def run_backtest_from_signals(price_df: pd.DataFrame, signal_df: pd.DataFrame, risk_reward: float = 2.0, max_holding_bars: int = 12) -> tuple[pd.DataFrame, dict] :
    trades = []
    
    for idx in range(len(signal_df) - 1):
        row = signal_df.iloc[idx]
        if not bool(row.get("setup_valid", False)):
            continue
    
        side = row.get("trade_side", "neutral")
        if side not in ["long", "short"]:
            continue
        
        entry_price = float(signal_df.iloc[idx + 1]["Open"])
        is_long = side == "long" # --> eliminated the DRY rule
        
        swing_level = row.get("previous_swing_lows") if is_long else row.get("previous_swing_highs")
        fallback_level = row["low"] if is_long else row["High"]
        stop_price = float(swing_level) if pd.notna(swing_level) else float(fallback_level)
        
        risk_direction = 1 if is_long else -1 
        risk = max(risk_direction * (entry_price - stop_price), 0.01)
        target_price = entry_price + (risk * risk_reward *risk_direction)
        
        trade = build_trade_record(idx + 1, signal_df.index[idx + 1], side, entry_price, stop_price, target_price)
        resolved = resolve_trade(signal_df, trade, max_holding_bars=max_holding_bars)
        
