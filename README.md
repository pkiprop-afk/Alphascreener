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

The workflow is simple. A user selects a ticker, chooses or creates a model