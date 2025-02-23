"""
EMA & RSI Crossover Strategy for Algorithmic Trading

This strategy combines two popular indicators:
1. **Exponential Moving Average (EMA) Crossover**:
   - A short-term EMA crossing above a long-term EMA indicates a bullish trend.
   - A short-term EMA crossing below a long-term EMA indicates a bearish trend.

2. **Relative Strength Index (RSI)**:
   - RSI above the overbought level suggests a potential sell signal.
   - RSI below the oversold level suggests a potential buy signal.

Key Features:
- **Customizable Parameters**: Allows users to set EMA periods, RSI period, and overbought/oversold thresholds.
- **Library Agnostic**: Supports both `talib` and `pandas_ta` for indicator calculations.
- **Dynamic Signal Generation**: Generates buy/sell signals based on EMA crossovers and RSI conditions.
- **Compatible with Backtesting**: Extends `BaseStrategy` to integrate seamlessly with the backtesting framework.

Usage:
- Initialize the class with a price DataFrame (`df`) and strategy parameters.
- Call `apply_strategy()` to compute buy/sell signals.
- Use `backtest()` from `BaseStrategy` to simulate performance.
"""

import talib
import numpy as np
import pandas as pd
import pandas_ta as ta
from strategies.base_strategy import BaseStrategy

class EMA_RSI_CrossoverStrategy(BaseStrategy):
    """
    EMA & RSI Crossover Strategy for Trading.

    Attributes:
        df (pd.DataFrame): Market data containing OHLC prices.
        strategy_params (dict): Dictionary containing EMA and RSI parameters.
        library (str): The technical analysis library ('talib' or 'pandas_ta').
    """
    def __init__(self, df, strategy_params, library="talib"):
        """
        Initializes the EMA & RSI crossover strategy.

        Parameters:
            df (pd.DataFrame): Market data with OHLC prices.
            strategy_params (dict): Dictionary containing strategy parameters:
                - 'ema_short': Short EMA period.
                - 'ema_long': Long EMA period.
                - 'rsi_period': RSI calculation period.
                - 'rsi_overbought': RSI overbought level.
                - 'rsi_oversold': RSI oversold level.
            library (str): The technical analysis library to use ('talib' or 'pandas_ta').
        """
        super().__init__(df, strategy_params)
        self.library = library  # Choose between "talib" or "pandas_ta"

    def apply_strategy(self):
        """
        Applies the EMA & RSI crossover strategy to generate trading signals.

        Logic:
        - Buy Signal (1): When the short EMA is below the long EMA and RSI is in oversold territory.
        - Sell Signal (-1): When the short EMA is above the long EMA and RSI is in overbought territory.
        - No Signal (0): When neither condition is met.

        Updates:
            self.signals (pd.DataFrame): Contains generated buy/sell signals.
        """
        signals = pd.DataFrame(index=self.df.index)
        signals["close"] = self.df["close"]

        short_period = self.strategy_params["ema_short"]
        long_period = self.strategy_params["ema_long"]
        rsi_period = self.strategy_params["rsi_period"]
        overbought = self.strategy_params["rsi_overbought"]
        oversold = self.strategy_params["rsi_oversold"]

        # Compute indicators using the selected library
        if self.library == "talib":
            self.df["EMA_Short"] = talib.EMA(self.df["close"].values, timeperiod=short_period)
            self.df["EMA_Long"] = talib.EMA(self.df["close"].values, timeperiod=long_period)
            self.df["RSI"] = talib.RSI(self.df["close"].values, timeperiod=rsi_period)

        elif self.library == "pandas_ta":
            self.df["EMA_Short"] = self.df.ta.ema(length=short_period)
            self.df["EMA_Long"] = self.df.ta.ema(length=long_period)
            self.df["RSI"] = self.df.ta.rsi(length=rsi_period)

        # Generate buy/sell signals based on EMA crossover and RSI levels
        signals["signal"] = np.where(
            (self.df["EMA_Short"] > self.df["EMA_Long"]) & (self.df["RSI"] > overbought), -1,  # Sell Signal
            np.where((self.df["EMA_Short"] < self.df["EMA_Long"]) & (self.df["RSI"] < oversold), 1, 0)  # Buy Signal
        )

        self.signals = signals
