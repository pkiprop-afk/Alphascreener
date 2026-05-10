import csv
import json
import os
from datetime import datetime
from typing import Any

DEFAULT_STRATEGY = {
    "name": "ICT Reversal Starter",
    "market": "futures",
    "timeframe": "1d",
    "model_type"
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

def get_strategy_by_name(file_path: str, strategy_name: str) -> dict | None:
    """ Load strategies and find the first one matching the given name"""
    strategies = load_json_file(file_path, default=[])
    return [item.get("name", "Unnamed Strategy") for item in strategies]

def save_or_update_strategy(file_path: str, strategy_payload: dict) -> None:
    # loads existing strategies and prepares metadata
    strategies = load_json_file(file_path, default=[])
    strategy_name = strategy_payload.get("name", "Unnamed Strategy").strip()
    now = timestamp_now()
    
    # We find the index of an existing strategy if it exists
    existing_index = -1
    for i, item in enumerate(strategies):
        if item.get("name") == strategy_name:
            existing_index = i
            break
    
    if existing_index != -1:
        # If found, update the existing strategy
        strategies[existing_index].update(strategy_payload)
        strategies[existing_index]["updated_at"] = now
        
    else:
    # Otherwise, create a new strategy merged with defaults and append it to the list
        new_strategy = {
            **DEFAULT_STRATEGY,
            **strategy_payload,
            "name": strategy_name,
            "created_at": now,
            "updated_at": now,
        }
        strategies.append(new_strategy)
    write_json_file(file_path, strategies)

def delete_strategy(file_path: str, strategy_name: str) -> None:
    # Load strategies excluding the one to be deleted
    strategies = load_json_file(file_path, default=[])
    filtered = [item for item in strategies if item.get("name") != strategy_name]
    write_json_file(file_path, filtered)

def add_to_watchlist(file_path: str, ticker: str, notes: str, strategy_name: str = "" ) -> None:
    # Loads the watchlist and prepares the timestamp
    watchlist = load_json_file(file_path, default=[])
    now = timestamp_now()
    
    # Updates the entry if the ticker exists, otherwise append a new entry
    existing = next((item for item in watchlist if item.get("ticker") == ticker), None)
    if existing:
        existing["notes"] = notes
        existing["strategy_name"] = strategy_name
        existing["updated_at"] = now
    else:
        watchlist.append(
            {
                "ticker": ticker,
                "notes": notes,
                "strategy_name": strategy_name,
                "created_at": now,
                "updated_at": now,
            }
        )
    
    # Saves the updated watchlist
    write_json_file(file_path, watchlist)    

def append_backtest_result(file_path: str, result_payload: dict) -> None:
    # Loads existing features, add a timestamp to the new result, and save
    results = load_json_file(file_path, default=[])
    enriched = {**result_payload, "saved_at": timestamp_now()}
    results.append(enriched)
    write_json_file(file_path, results)