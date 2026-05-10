# AlphaLens
AlphaLens is a Streamlit-based market screening and trade setup research tool designed around ICT-style technical analysis concepts. The application downloads historical OHLCV market data, annotates each candle with structure, liquidity, fair value gap, and delivery-state signals, then helps the user evaluate whether a ticker matches a configurable trading model.

The project is built as a practical research dashboard. Its central purpose is to make the reasoning behind a potential setup visible through a TradingView chart, a signal timeline, status badges, scanner results, and a lightweight paper-testing workflow

# Table of Contents
### 1. Overview
### 2. Core Features
### 3. How the Signal Engine Works
### 4. Signal Timeline Explained
### 5. Project Structure
### 6. Installation
### 7. Running the app
### 8. Configuration and Data Files
### 9. Paper Testing
### 10. Development Notes
### 11. RoadMap Ideas 
### 12. Disclaimer

## 1. Overview  
AlphaLens brings together market data retrieval, ICT-inspired signal generation, and interactive strategy controls inside a single Streamlit dashboard. Streamlit is a Python framework for building interactive data applications, while the app currently uses **yfinance** to retrieve historical market data from Yahoo finance and **pandas** to structure and transform the resulting datasets.

The workflow is simple. A user selects a ticker, chooses or creates a model, enables the ICT conditions required by that model, and reviews whether recent candles satisfy the selected setup rules. The app can also scan a ticker universe and surface symbols whose latest bar matches the selected configuration.

| Area | Purpose |
| --- | --- |
| Ticker Search | Selects the active ticker from `src/data/tickers.csv`. |
| Strategy Panel | Controls model name, model type, required ICT rules, risk/reward, holding period, and scan size. |
| TradingView Lens | Embeds a TradingView chart for visual price inspection. |
| Signal Timeline | Displays the most recent signal states as a candle-by-candle checklist. |
| Status Badges | Summarizes whether the latest candle has active MSS, FVG, and liquidity sweep context. |
| Paper Test Summary | Runs a lightweight historical test using generated setup signals. |
| Screen Results | Shows matching tickers after running the scanner across the configured universe. |

## 2. Core Features
AlphaLens is organized around transparency. Instead of only producing a final **buy** or **sell** decision, it exposes the underlying conditions that caused a setup to pass or fail

| Feature | Description |
| --- | --- |
| Configurable strategy models | Saved models are stored as JSON and can be updated from the Streamlit sidebar. |
| ICT signal annotation | Historical candles are enriched with structure shifts, CISD, fair value gaps, and liquidity context. |
| Multi-ticker screening | The app can scan a defined ticker universe and return symbols that match the active model. |
| Signal timeline | Recent candles are displayed as boolean event flags so the user can audit the setup sequence. |
| TradingView integration | The middle panel embeds a TradingView widget for chart-based validation. |
| Paper testing | The app can run a simple backtest from `setup_valid` rows and summarize win rate and total R. |
| Local persistence | Strategies, ticker lists, watchlists, and backtest data are stored locally under the repository data folders. |

## 3. How the Signal Engine Works
The signal engine starts by downloading OHLCV data for the selected ticker. The app then applies a sequence of transformations that add technical context to each candle. These enriched rows are converted into a signal table, where each row represents one timestamp and each signal column represents one timestamp andd each signal column represents whether a specific condition was true on that candle

| Step | Function | Output |
| --- | --- | --- |
| Fetch history | `fetch_history_for_sticker()` | Downloads and cleans Open, High, Low, Close, and Volume data. |
| Detect swings | `detect_swings()` | Marks swing highs and swing lows using a configurable swing window. |
| Detect structure shift | `detect_structure_shift()` | Adds bullish and bearish market-structure shift flags. |
| Detect liquidity sweep | `detect_external_liquidity_sweep()` | Marks candles that sweep prior swing high or low liquidity. |
| Detect CISD | `detect_cisd()` | Marks bullish or bearish change in state of delivery. |
| Detect FVG zones | `detect_fvg_zones()` | Marks bullish and bearish fair value gaps. |
| Add liquidity context | `add_liquidity_context()` | Adds internal and external liquidity touch context. |
| Evaluate setup | `evaluate_bar_setup()` | Combines strategy requirements into `trade_side` and `setup_valid`. |

## 4. Signal Timeline
The Signal Timeline is a recent-bar diagnostic view. In the current implementation, the app displays the last 12 rows of the signal table with **signal_df.tail(12)**. The timestamp index is reset into the **datetime** column, and the selected boolean signal columns are shown in a Streamlit dataframe.

This is why the timeline appears as a checkbox-style grid. Each checkbox is simply visual representation of a Python boolean value. A checked box means the condition was **True** for that candle, while an empty box means the condition was **False**.

The table can look sparse because these are event-driven signals. A moving average has a value on every candle, but liquidity sweep, CISD event, fair value gap, or structure shift only appears when the underlying rule is triggered.

## 5. Project Structure
| File | Role |
| --- | --- |
| `main.py` | Streamlit UI, session state, model controls, chart panel, timeline, scanner, and paper-test panel. |
| `src/lib/market_data.py` | Market data retrieval, signal-table construction, setup evaluation, and ticker scanning. |
| `src/lib/ict_structure.py` | Swing detection, structure-shift detection, and external liquidity sweep detection. |
| `src/lib/ict_delivery.py` | Candle pattern classification and CISD detection. |
| `src/lib/ict_fvg.py` | Fair value gap detection and FVG touch helpers. |
| `src/lib/ict_liquidity.py` | Internal and external liquidity context. |
| `src/lib/paper_test.py` | Historical paper-test workflow based on valid setup rows. |
| `src/lib/storage.py` | JSON and CSV persistence helpers for strategies, watchlists, and results. |
| `src/lib/tradingview_widget.py` | Embedded TradingView chart component. |
| `src/data/strategies.json` | Saved model definitions and rule settings. |
| `src/data/tickers.csv` | Ticker universe used by the search box and scanner. |

## 6. Installation

git clone https://github.com/pkiprop-afk/Alphascreener.git
cd Alphascreener
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

| Package | Purpose |
| --- | --- |
| `streamlit` | Runs the interactive dashboard. |
| `pandas` | Structures and transforms OHLCV and signal data. |
| `yfinance` | Downloads historical market data from Yahoo Finance. |

## 7. Running the app

`streamlit run main.py`

The app will open in the browser. From there, select a ticker, review the chart, adjust the active model, and inspect the Signal Timeline and analysis panel.

## 8. Configuration and Data Files

The app persists its local configuration in JSON and CSV files. This makes it easy to edit strategies directly, version-control model changes, and expand the ticker universe.

| Data File | Description |
| --- | --- |
| `src/data/strategies.json` | Stores saved strategy models, including entry rules, risk settings, filters, and metadata. |
| `src/data/tickers.csv` | Stores the ticker universe used by ticker search and screening. |
| `src/data/watchlist.json` | Stores locally tracked watchlist symbols. |
| `src/data/backtest_results.json` | Stores or reserves space for paper-test output records. |

A strategy model contains three main sectors. The **entry_model** defines which technical conditions must be present, the **risk_model** defines trade management assumptions, and **filters** defines thresholds used by the signal engine.

| Strategy Section | Example Fields | Purpose |
| --- | --- | --- |
| `entry_model` | `require_structure_shift`, `require_cisd`, `require_fvg`, `require_external_liquidity_sweep` | Determines which signals are required before a setup becomes valid. |
| `risk_model` | `risk_reward`, `max_holding_bars`, `stop_type`, `target_type` | Determines how the paper test estimates exits and results. |
| `filters` | `swing_window`, `liquidity_lookback`, `fvg_min_pct`, `min_displacement_pct` | Controls how sensitive the signal-detection logic is. |

## 9. Paper Testing
The paper-testing module uses the generated signal table and enters trades from rows where **setup_valid** is **True**. It then evaluates future candles using a target, stop, and maximum holding period. The summary panel currently reports win rate and total R, which are useful first-pass metrics for comparing model configurations.

This testing workflow should be treated as a research aid. **It does not include all real-world trading factors such as fees, slippage, spread, liquidity constraints, changing market regimes, or execution quality.**

## 10. Development Notes

| Improvement Area | Suggested Direction |
| --- | --- |
| Signal accuracy | Add unit tests for structure shifts, CISD, FVG detection, and liquidity sweeps using small handcrafted OHLC datasets. |
| Timeline clarity | Distinguish between first-time event triggers and continuing conditions so structure-shift rows do not appear overly repetitive. |
| Backtest robustness | Add fees, slippage, position sizing, and long/short-specific performance breakdowns. |
| Data reliability | Add error handling for missing ticker data, API failures, and empty downloaded datasets. |
| Documentation | Add screenshots, example strategies, and a walkthrough of one complete setup from signal timeline to paper test. |
| Deployment | Add a deployment guide for Streamlit Community Cloud or another hosting option. |


