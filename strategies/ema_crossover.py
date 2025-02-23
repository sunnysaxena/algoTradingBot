"""
EMA Crossover Trading Strategy

This strategy is based on the Exponential Moving Average (EMA) crossover technique.
It uses two EMAs (short-term and long-term) to generate buy and sell signals.

Features:
- Supports both `TA-Lib` and `pandas_ta` for indicator calculation.
- Dynamically selects the library based on user preference.
- Generates buy (1) and sell (-1) signals based on EMA crossovers.

Signal Generation:
- Buy Signal (1) → When the short EMA crosses above the long EMA (Bullish Crossover).
- Sell Signal (-1) → When the short EMA crosses below the long EMA (Bearish Crossover).

Usage:
- Configure `ema_short` and `ema_long` in `config.yml`.
- Specify the library (`talib` or `pandas_ta`).
"""

import talib
import numpy as np
import pandas as pd
import pandas_ta as ta
from strategies.base_strategy import BaseStrategy

class EMA_CrossoverStrategy(BaseStrategy):
    """
    Implements the EMA Crossover Strategy for trend-following trading.

    Attributes:
        df (pd.DataFrame): Market data containing OHLC prices.
        strategy_params (dict): Dictionary containing strategy parameters like `ema_short` and `ema_long`.
        library (str): Defines which technical analysis library to use ('talib' or 'pandas_ta').
    """
    def __init__(self, df, strategy_params, library="talib"):
        """
        Initializes the EMA Crossover Strategy.

        Parameters:
            df (pd.DataFrame): Market data with OHLC prices.
            strategy_params (dict): Configuration containing EMA periods.
            library (str): The library to use for calculating indicators ('talib' or 'pandas_ta').
        """
        super().__init__(df, strategy_params)
        self.library = library  # Choose between "talib" or "pandas_ta"

    def apply_strategy(self):
        """
            Applies the EMA crossover strategy to generate buy and sell signals.
        """
        signals = pd.DataFrame(index=self.df.index)
        signals["close"] = self.df["close"]

        short_period = self.strategy_params["ema_short"]
        long_period = self.strategy_params["ema_long"]

        # Compute EMAs using the selected library
        if self.library == "talib":
            self.df["EMA_Short"] = talib.EMA(self.df["close"].values, timeperiod=short_period)
            self.df["EMA_Long"] = talib.EMA(self.df["close"].values, timeperiod=long_period)

        elif self.library == "pandas_ta":
            self.df["EMA_Short"] = self.df.ta.ema(length=short_period)
            self.df["EMA_Long"] = self.df.ta.ema(length=long_period)

        # Generate signals
        signals["signal"] = np.where(self.df["EMA_Short"] > self.df["EMA_Long"], 1, -1)

        self.signals = signals
