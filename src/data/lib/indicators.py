import pandas as pd 

def calculate_rsi(close_series: pd.Series, window: int = 14) -> pd.Series:
    delta = close_series.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    
    average_gain = gains.rolling(window=window, min_periods=window).mean()

def add_indicators():
    pass

def build_strategy_from_inputs():
    pass

def passes_screen():
    pass