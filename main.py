import json
import os
import sys
from datetime import datetime

import pandas as pd 
import streamlit as st 

APP_PATH = os.path.dirname(os.path.abspath(__file__))
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)

from src.lib.market_data import (
    INTERVAL_TRADINGVIEW_MAP,
    build_signal_table,
    build_summary_latest_setup,
    fetch_history_for_sticker,
    have_with_ict_signal,
    run_strategy_scan,
)

from src.lib.paper_test import run_backtest_from_signals
from src.lib.storage import(
    DEFAULT_STRATEGY,
    load_json_file,
    save_or_update_strategy
)

DATA_DIR = os.path.join(APP_PATH, "data")
STRATEGIES_PATH = os.path.join(DATA_DIR, "strategies.json")
TICKERS_PATH = os.path.join(DATA_DIR, "tickers.csv")
NEW_MODEL_OPTION = "+ Create New Model"
