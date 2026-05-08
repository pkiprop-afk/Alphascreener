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

from src.lib.tradingview_widget import render_tradingview_widget


DATA_DIR = os.path.join(APP_PATH, "data")
STRATEGIES_PATH = os.path.join(DATA_DIR, "strategies.json")
TICKERS_PATH = os.path.join(DATA_DIR, "tickers.csv")
NEW_MODEL_OPTION = "+ Create New Model"

@st.cache_data
def load_ticker_universe() -> list[str]:
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

def render_header_row(strategy: dict) -> None:  # sourcery skip: extract-method
    """ 
    Render the main header controls for selecting a ticker and running the strategy scanner.
    The function updates session state with scan results, surfaces any scan errors, and can trigger a rerun of the app when a screen is executed.

    Args:
        strategy: Strategy configuration dict used when running the screening process across the ticker universe.

    Returns:
        None. The function interacts with Streamlit widgets and st.session_state to drive the header UI behaviour
    """
    # Setup the layout for ticker selection and the run button
    tickers = load_sticker_universe()
    header_left, header_right = st.columns([4, 1])
    
    with header_left:
        st.selectbox(
            "Ticker Search",
            options=tickers,
            key="selected_ticker",
            help= "Ticker universe loaded from data/tickers.csv",
            on_change=reset_paper_test_on_ticker_change,
        )
    
    # When the "Run Screen" button is clicked, scan the universe and update the results
    with header_right:
        st.write("")
        if st.button("Run Screen", use_container_width=True, type="primary"):
            tickers_to_scan = tickers[:st.session_state.universe_size]
            with st.spinner(f"Scanning {len(tickers_to_scan)} tickers..."):
                result_df, scan_errors = run_strategy_scan(tickers_to_scan, strategy)
                st.session_state.scanner_results = result_df
                
                for err in scan_errors:
                    st.warning(err)
    
                if not result_df.empty:
                    st.session_state.selected_ticker = result_df.iloc[0]["Ticker"]
                    
                st.session_state.header_run_screen = True
                st.rerun() # -> Rerun to reflect the new selected_ticker and shows results immediately

def render_control_strip(strategy: dict) -> None:  
    st.subheader("Strategy")
    
    with st.container(border=True):
        library = load_strategy_library()
        saved_model_names = [item.get("name", "Unnamed") for item in library] or [DEFAULT_STRATEGY["name"]]
        model_names = [NEW_MODEL_OPTION] + [name for name in saved_model_names if name != NEW_MODEL_OPTION]
        if st.session_state.selected_model_name not in model_names:
            st.session_state.selected_model_name = model_names[1] if len(model_names) > 1 else NEW_MODEL_OPTION

        top_a, top_b = st.columns([3, 1])
        with top_a:
            st.selectbox(
                "Model",
                options=model_names,
                key="selected_model_name",
                on_change=sync_selected_model,
            )
        with top_b:
            st.write("")
            st.button("New Model", use_container_width=True, on_click=create_new_model)
        st.text_input("Model Name", key="model_name_input")
        st.selectbox("Model Type", options=["Scalping", "Swing", "Fractal"], key="model_type")
        
    with st.container(border=True):
        st.markdown("#### Core ICT Rules")
        st.toggle("Market Structure Shift (MSS)", key="require_structure_shift")
        st.toggle("Fair Value Gap (FVG)", key="require_fvg")
        st.toggle("Change in State of Delivery (CISD)", key="require_cisd")
    
    with st.container(border=True):
        with st.expander("Risk & Scan  Settings", expanded=False):
            st.number_input(" Risk / Reward Ratio", min_value=1.0, max_value=10.0, step=0.5, key="risk_reward")
            st.number_input("Max Holding Bars", min_value=1.0, max_value=200, step=0.5, key="max_holding_bars")
            st.number_input(
                "Ticker to Scan",
                min_value=10,
                max_value=len(load_ticker_universe()),
                step=10,
                key="universe_size",
                help="Number of tickers from the universe to screen.",
            )
    
    with st.container(border=True):
        st.markdown("#### Model Actions")
        if st.button("Save Current Model", use_container_width=True):
            save_or_update_strategy(STRATEGIES_PATH, strategy)
            st.success(f"Saved model: {strategy["name"]}")
            load_strategy_library.clear()
        st.caption("This panel owns the active rule set and persists models without changing the backend logic.")
    
@st.cache_data(show_spinner="Analyzing ticker data...")
def get_sticker_analysis(ticker: str, interval: str, _strategy_json: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    strategy = json.loads(_strategy_json)
    ohlc_df = fetch_history_for_sticker(ticker, interval=interval)
    if ohlc_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    enriched_df = have_with_ict_signal(ohlc_df, strategy)
    signal_df = build_signal_table(enriched_df, strategy)
    return ohlc_df, enriched_df, signal_df

def build_workspace_data(strategy: dict) -> dict:
    ticker = st.session_state.selected_sticker
    interval = strategy.get("timeframe", "1d")
    
    workspace = {
        "ticker": ticker,
        "ohlc_df": pd.DataFrame(),
        "enriched_df": pd.DataFrame(),
        "signal_df": pd.DataFrame(),
        "full_signal_df": pd.DataFrame(),
        "latest_row": {},
        "paper_metrics": st.session_state.get("paper_test_result", {}),
        "screen_results": st.session_state
        
        
    }

def render_signal_timeline():
    pass

def render_lens_panel(strategy: dict, workspace: dict):
    """ 
    """
    st.subheader("Trade Setup")
    ticker = workspace["ticker"]
    app_interval = strategy.get("timeframe", "1d")
    tv_interval = INTERVAL_TRADINGVIEW_MAP.get(app_interval, "D")
    with st.container(border=True):
        render_tradingview_widget(ticker, interval=tv_interval, height=500)
    with st.container(border=True):
        render_signal_timeliine(workspace["signal_df"])

def render_status_badge(label: str, active: bool, active_text: str, inactive_text: str) -> None:
    with st.container(border=True):
        st.markdown(f"**{label}**")
        if active:
            st.success("Active")
            st.caption(active_text)
        else:
            st.info("Inactive")
            st.caption(inactive_text)

def render_analysis_panel(workspace: dict) -> None:
    # sourcery skip: extract-method
    st.subheader("Analysis")
    latest_row = workspace.get("latest_row", {})
    paper_metrics = workspace.get("paper_metrics", {})
    
    with st.container(border=True):
        is_valid = "Yes" if latest_row.get("setup_valid") else "No"
        st.metric("Latest Setup Valid?", is_valid)
        st.caption("Is the latest bar a valid setup based on the rules?")
    
    st.markdown("### Status Badges")
    render_status_badge(
        "MSS",
        bool(latest_row.get("bullish_structure_shift", False) or latest_row.get("bearish_structure_shift", False)),
        "Bullish or bearish shift confirmed.",
        "No current structure shift confirmation, ",
    )
    render_status_badge(
    "FVG",
    bool(latest_row.get("bullish_fvg", False) or latest_row.get("bearish_fvg", False)),
    "Fair value imbalance is active in the current sequence.",
    "No active fair value gap signal.",
    )
    render_status_badge(
        "Liquidity Sweep",
        bool(latest_row.get("swept_external_high", False) or latest_row.get("swept_external_low", False)),
        "Liquidity sweep is present in the current setup.",
        "No recent buyside or sellside sweep detected.",
    )
    
    with st.container(border=True):
        st.markdown("#### Paper Test Summary")
        
        if st.button("Run Paper Test", use_container_width=True):
            strategy = build_focus_strategy()
            ohlc_df = workspace.get("ohlc_df")
            signal_df = workspace.get("full_signal_df")
            
            if ohlc_df is not None and not ohlc_df.empty and signal_df is not None and not signal_df.empty:
                with st.spinner("Running Paper Test..."):
                    risk_reward = float(strategy.get("risk_model", {}).get("risk_reward", 2.0))
                    max_holding_bars = int(strategy.get("risk_model", {}).get("max_holding_bars", 12))
                    _, summary = run_backtest_from_signals(
                        ohlc_df, signal_df, risk_reward=risk_reward, max_holding_bars=max_holding_bars
                    )
                    st.session_state.paper_test_result = summary
                    st.rerun()
            else:
                st.warning("Not enough data to run paper test.")
        
        col_a, col_b = st.columns(2)
        col_a.metric("Win Rate", paper_metrics.get("win_rate", "N/A"))
        col_b.metric("Total R", paper_metrics.get("total_r", "N/A"))
        st.caption("Click button to run a backtest on the full history for this ticker.")
    
    if isinstance(workspace.get("screen_results"), pd.DataFrame) and not workspace["screen_results"].empty:
        with st.container(border=True):
            st.markdown("### Screen Results")
            st.dataframe(workspace["screen_results"].head(5), hide_index=True, use_container_width=True)
    
def main() -> None:
    st.set_page_config(page_title="", page_icon="", layout="wide")
    initialize_session_state()
    
    strategy = build_focus_strategy()
    
    st.title("")
    st.caption("")
    
    render_header_row(strategy)
    workspace = build_workspace_data(strategy)
    
    left_col, middle_col, right_col = st.columns([1, 2.75, 1.25], gap="medium")
    
    with left_col:
        render_control_strip(strategy)
    with middle_col:
        render_lens_panel(strategy, workspace)
    with right_col:
        render_analysis_panel(workspace)
    
if __name__ == "__main__":
    main()