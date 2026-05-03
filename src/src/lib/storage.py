import csv
import json
import os
from datetime import datetime
from typing import Any

DEFAULT_STRATEGY = {
    "name": "ICT Reversal Starter",
    "market": "futures",
    "timeframe": "1d",
    "entry_model":{
        "require_structure_shift": True,
        "require_cisd": True,
        "require_fvg": True,
        "require_external_liquidity_sweep": True,
        "require_internal_liquidity_touch": False,
        "candle_pattern": "any",
    },
    "risk_model":{
        "stop_type": "swing",
        "target_type": "risk_reward",
        "risk_reward": 2.0,
        "max_holding_bars": 12,
    },
    "filters": {
        "swing_window": 3,
        "liquidity_lookback": 40,
        "fvg_min_pct": 0.001,
        "min_displacement_pct": 0.002,
        "max_bars_after_sweep": 6,
    },
}

def ensure_parents_exist(file_path = str) -> None:
    """ ensures the directory containing the file exists"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

def timestamp_now() -> str:
    "Returns the current time as an ISO formatted string"
    return datetime.now().isoformat(timespec="seconds")

def load_json_file(file_path: str, default: Any):
    """ Ensures the directory exists and initialize the file with default data if it's missing"""
    ensure_parents_exist(file_path)
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(default, file, indent=2)
        return default
    
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return default


def write_json_file(file_path: str, data: Any) -> None:
    """ ensures the directory exists and writes the data to the file as formatted JSON"""
    ensure_parents_exist(file_path)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

def load_ticker_universe(csv_path: str) -> list[str]:
    # Return an empty list if the CSV file does not exist
    ensure_parents_exist(csv_path)
    if not os.path.exists(csv_path):
        return []
    
    # Parses the CSV and extract a cleaned ticker symbols from the 'ticker' column
    tickers = []
    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            ticker = (row.get("ticker") or"").strip().upper()
            if ticker:
                tickers.append(ticker)
    return tickers

def list_strategy_names(file_path: str) -> list[str]:
    """ Loads the strategy and returns a list of their names"""
    strategies = load_json_file(file_path, default=[])
    return [item.get("name","Unnamed Strategy") for item in strategies]

def save_or_update_strategy():
    pass

def delete_strategy():
    pass

def add_to_watchlist():
    pass

def append_backtest_result():
    pass