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