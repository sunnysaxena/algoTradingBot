"""
MACD Crossover Strategy for Algorithmic Trading

The MACD (Moving Average Convergence Divergence) crossover strategy is a widely used momentum-based
trading approach that helps identify trend reversals and strength.

### Strategy Logic:
1. **MACD Line Calculation**:
   - The MACD line is the difference between a short-term and long-term exponential moving average (EMA).
2. **MACD Signal Line**:
   - A smoothed version of the MACD line.
3. **Buy/Sell Signals**:
   - A **Buy Signal (1)** is generated when the MACD line crosses **above** the Signal line (Bullish Crossover).
   - A **Sell Signal (-1)** is generated when the MACD line crosses **below** the Signal line (Bearish Crossover).

### Features:
✅ **Customizable Parameters**: Users can set fast EMA, slow EMA, and signal period lengths.
✅ **Library Agnostic**: Supports both `talib` and `pandas_ta` for indicator calculations.
✅ **Signal Generation**: Automatically detects bullish and bearish crossovers.
✅ **Backtest Integration**: Works seamlessly with `BaseStrategy` for performance evaluation.

### Usage:
- Initialize the class with OHLC price data and strategy parameters.
- Call `apply_strategy()` to compute buy/sell signals.
- Use `backtest()` from `BaseStrategy` to simulate portfolio performance.

"""

import talib
import numpy as np
import pandas as pd
import pandas_ta as ta
from strategies.base_strategy import BaseStrategy

class MACD_CrossoverStrategy(BaseStrategy):
    """
    MACD Crossover Strategy for Trading.

    Attributes:
        df (pd.DataFrame): Market data containing OHLC prices.
        strategy_params (dict): Dictionary containing MACD parameters.
        library (str): The technical analysis library ('talib' or 'pandas_ta').
    """

    def __init__(self, df, strategy_params, library="talib"):
        """
        Initializes the MACD crossover strategy.

        Parameters:
            df (pd.DataFrame): Market data with OHLC prices.
            strategy_params (dict): Dictionary containing strategy parameters:
                - 'macd_fast': Fast EMA period.
                - 'macd_slow': Slow EMA period.
                - 'macd_signal': Signal line period.
            library (str): The technical analysis library to use ('talib' or 'pandas_ta').
        """
        super().__init__(df, strategy_params)
        self.library = library  # Choose between "talib" or "pandas_ta"

    def apply_strategy(self):
        """
        Applies the MACD crossover strategy to generate trading signals.

        Logic:
        - Buy Signal (1): When the MACD line crosses above the Signal line.
        - Sell Signal (-1): When the MACD line crosses below the Signal line.

        Updates:
            self.signals (pd.DataFrame): Contains generated buy/sell signals.
        """
        signals = pd.DataFrame(index=self.df.index)
        signals["close"] = self.df["close"]

        fast_length = self.strategy_params["macd_fast"]
        slow_length = self.strategy_params["macd_slow"]
        signal_length = self.strategy_params["macd_signal"]

        # Compute MACD using the selected library
        if self.library == "talib":
            self.df["MACD"], self.df["MACD_Signal"], self.df["MACD_Hist"] = talib.MACD(
                self.df["close"].values,
                fastperiod=fast_length,
                slowperiod=slow_length,
                signalperiod=signal_length
            )

        elif self.library == "pandas_ta":
            macd_df = self.df.ta.macd(
                fast=fast_length, slow=slow_length, signal=signal_length, append=True
            )
            self.df["MACD"] = macd_df[f"MACD_{fast_length}_{slow_length}_{signal_length}"]
            self.df["MACD_Signal"] = macd_df[f"MACDs_{fast_length}_{slow_length}_{signal_length}"]
            self.df["MACD_Hist"] = macd_df[f"MACDh_{fast_length}_{slow_length}_{signal_length}"]

        # Generate buy/sell signals
        signals["signal"] = np.where(self.df["MACD"] > self.df["MACD_Signal"], 1, -1)

        self.signals = signals
