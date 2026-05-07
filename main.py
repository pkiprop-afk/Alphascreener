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

@st.cache_data
def load_sticker_universe() -> list[str]:
    if not os.path.exists(TICKERS_PATH):
        return []
    ticker_df = pd.read_csv(TICKERS_PATH)
    if "ticker" not in ticker_df.columns:
        return []
    return ticker_df["ticker"].dropna().astype(str).str.upper().tolist()

def load_strategy_library() -> list[dict]:
    return load_json_file(STRATEGIES_PATH, default=[DEFAULT_STRATEGY])

def initialize_session_state() -> None:
    defaults = {
        "selected_ticker": "AAPL",
        "selected_model_name": DEFAULT_STRATEGY["name"],
        "model_type": "swing",
        "require_structure_shift": DEFAULT_STRATEGY["entry_model"]["require_structure_shift"],
        "require_fvg": DEFAULT_STRATEGY["entry_model"]["require_fvg"],
        "require_cisd": DEFAULT_STRATEGY["entry_model"]["require_cisd"],
        "risk_reward": DEFAULT_STRATEGY["entry_model"]["risk_reward"],
        "max_holding_bars": DEFAULT_STRATEGY["entry_model"]["max_holding_bars"],
        "universe_size": 50,
        "scanner_results":pd.DataFrame(),
        "signal_timeline": pd.DataFrame(),
        "paper_test_result": {},
        "model_name_input": DEFAULT_STRATEGY["name"],
        "header_run_screen": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def build_focus_strategy() -> dict:
    """ 
    Construct a working strategy configuration based on the current UI-focused model settings.
    The function clones the default strategy template and overlays user-controlled session state values to produce a ready-to-use strategy dict.

    Returns:
        A dictionary representing the current focus strategy, including name, model_type, entry conditions, and risk parameters
    """
    strategy = json.loads(json.dumps(DEFAULT_STRATEGY))
    strategy["name"] = st.session_state.model_name_input.strip() or "Untitled Focus Model" 
    strategy["model_type"] = st.session_state.model_type
    strategy["entry_model"]["require_structure_shift"] = st.session_state.require_structure_shift
    strategy["entry_model"]["require_fvg"] = st.session_state.require_fvg
    strategy["entry_model"]["require_cisd"] = st.session_state.require_cisd
    strategy["risk_model"]["risk_reward"] = float(st.session_state.risk_reward)
    strategy["risk_model"]["max_holding_bars"] = int(st.session_state.max_holding_bars)
    return strategy

def sync_selected_model() -> None:
    """ 
    Synchronize the currently selected strategy model into Streamlit session state.
    The function loads the chosen strategy from the library and updates UI-controlled fields to reflect its configuration.

    Returns:
        None. The function mutates st.session_state in place to match the selected strategy or initializes a new model when requested
    """
    if st.session_state.selected_model_name == NEW_MODEL_OPTION:
        create_new_model()
        return
    
    library = load_strategy_library()
    selected = next((item for item in library if item["name"] == st.session_state.selected_model_name), None)
    if not selected:
        return
    st.session_state.model_name_input = selected.get("name", DEFAULT_STRATEGY["name"])
    st.session_state.model_type = selected.get("model_type", DEFAULT_STRATEGY["model_type"])
    st.session_state.require_structure_shift = selected.get("entry_model", {}).get("require_structure_shift", True)
    st.session_state.require_fvg = selected.get("entry_model", {}).get("require_fvg", True)
    st.session_state.require_cisd = selected.get("entry_model", {}).get("require_cisd", True)
    st.session_state.risk_reward = selected.get("risk_model", {}).get("risk_reward", 2.0)
    st.session_state.max_holding_bars = selected.get("risk_model", {}).get("max_holding_bars", 20)


def create_new_model() -> None:
    """ 
    Reset the current focus model configuration to a fresh, default swing strategy template.
    The function initializes key Streamlit session state fields for a new model, ready for user customization.

    Returns:
        None. The function updates st.session_state in place with default model name, type, and core entry and risk parameters
    """
    st.session_state.selected_model_name = NEW_MODEL_OPTION
    st.session_state.model_name_input = "Untitled Focus Model"
    st.session_state.model_type = "swing"
    st.session_state.require_structure_shift = True
    st.session_state.require_fvg = True
    st.session_state.require_cisd = True
    st.session_state.risk_reward = 2.0
    st.session_state.max_holding_bars = 20


def reset_paper_test_on_ticker_change() -> None:
    """ 
    Clear any existing paper test results when the selected ticker changes.
    The function ensures that backtest summaries do not persist across different symbols in the current session.

    Returns:
        None. The function resets st.session_state['paper_test_result'] to an empty dict if it exists
    """
    if "paper_test_result" in st.session_state:
        st.session_state.paper_test_result = {}

def render_header_row(strategy: dict) -> None:
    tickers = load_sticker_universe()
    

def render_control_strip():
    pass

def get_ticker_analysis():
    pass

def build_workspace_data():
    pass

def render_signal_timeliine():
    pass

