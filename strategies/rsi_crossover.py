"""
RSI Crossover Strategy for Algorithmic Trading

The RSI (Relative Strength Index) crossover strategy is a momentum-based trading approach
that helps identify overbought and oversold market conditions. This strategy enhances
the traditional RSI approach by integrating multi-timeframe confirmation, divergence detection,
and a trailing stop-loss mechanism.

### Strategy Logic:
1. **RSI Calculation**:
   - RSI measures the magnitude of recent price changes to evaluate overbought/oversold conditions.
   - The user can specify the RSI calculation period.

2. **Multi-Timeframe Confirmation (Optional)**:
   - Uses a rolling mean of RSI from a higher timeframe to confirm signals.

3. **Buy/Sell Signal Generation**:
   - **Buy Signal (1)**: When RSI crosses below the oversold level (e.g., 30).
   - **Sell Signal (-1)**: When RSI crosses above the overbought level (e.g., 70).
   - Uses higher timeframe RSI confirmation (if provided).

4. **RSI Divergence Detection**:
   - **Bullish Divergence**: Price forms a lower low while RSI forms a higher low.
   - **Bearish Divergence**: Price forms a higher high while RSI forms a lower high.

5. **Trailing Stop-Loss**:
   - Dynamically adjusts stop-loss based on a percentage (user-defined).

### Features:
✅ **Customizable RSI Period & Levels**: Users can adjust RSI settings and thresholds.
✅ **Multi-Timeframe Analysis**: Higher timeframe RSI confirmation for stronger signals.
✅ **RSI Divergence Detection**: Identifies trend exhaustion points.
✅ **Trailing Stop-Loss**: Automatically adjusts risk management dynamically.
✅ **Library-Agnostic**: Supports both `TA-Lib` and `pandas_ta` for indicator calculations.
✅ **Seamless Backtesting**: Works with the `BaseStrategy` framework for performance evaluation.

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

class RSI_CrossoverStrategy(BaseStrategy):
    """
    RSI Crossover Strategy for Trading.

    Attributes:
       df (pd.DataFrame): Market data containing OHLC prices.
       strategy_params (dict): Dictionary containing RSI parameters.
       library (str): The technical analysis library ('talib' or 'pandas_ta').
    """
    def __init__(self, df, strategy_params, library="talib"):
        """
        Initializes the RSI Crossover Strategy.

        Parameters:
            df (pd.DataFrame): Market data with OHLC prices.
            strategy_params (dict): Dictionary containing strategy parameters:
                - 'rsi_period': RSI calculation period.
                - 'rsi_overbought': Overbought threshold (e.g., 70).
                - 'rsi_oversold': Oversold threshold (e.g., 30).
                - 'higher_tf_rsi_period' (optional): Rolling period for higher timeframe RSI.
                - 'trailing_sl': Percentage-based trailing stop-loss.
            library (str): The technical analysis library to use ('talib' or 'pandas_ta').
        """
        super().__init__(df, strategy_params)
        self.library = library  # Choose between "talib" or "pandas_ta"

    def apply_strategy(self):
        """
        Applies the RSI Crossover Strategy to generate trading signals.

        Logic:
        - Buy Signal (1): When RSI crosses below the oversold threshold.
        - Sell Signal (-1): When RSI crosses above the overbought threshold.
        - Uses higher timeframe RSI for confirmation (if provided).
        - Detects RSI divergence for additional insights.

        Updates:
            self.signals (pd.DataFrame): Contains generated buy/sell signals.
        """

        # Select the correct library (TA-Lib or Pandas_TA)
        if self.library == "talib":
            self.df["RSI"] = talib.RSI(self.df["close"], timeperiod=self.strategy_params["rsi_period"])
        else:
            self.df["RSI"] = self.df.ta.rsi(self.strategy_params["rsi_period"])

        # Multi-Timeframe Confirmation (Higher Timeframe RSI)
        if "higher_tf_rsi_period" in self.strategy_params:
            self.df["RSI_HigherTF"] = self.df["RSI"].rolling(self.strategy_params["higher_tf_rsi_period"]).mean()

        # Define Buy/Sell Signals
        self.signals = pd.DataFrame(index=self.df.index)
        self.signals["signal"] = np.where(
            (self.df["RSI"] < self.strategy_params["rsi_oversold"]) &
            (self.df["RSI_HigherTF"] < self.strategy_params["rsi_oversold"] if "RSI_HigherTF" in self.df else True), 1,  # Buy Signal

            np.where(
                (self.df["RSI"] > self.strategy_params["rsi_overbought"]) &
                (self.df["RSI_HigherTF"] > self.strategy_params["rsi_overbought"] if "RSI_HigherTF" in self.df else True), -1, 0)  # Sell Signal
        )

        # RSI Divergence Detection
        self.df["Divergence"] = self.detect_rsi_divergence()

        # Trailing Stop-Loss Logic
        self.df["stop_loss"] = np.where(self.signals["signal"] == 1,
                                        self.df["close"] * (1 - self.strategy_params["trailing_sl"]),  # Buy SL
                                        np.where(self.signals["signal"] == -1,
                                                 self.df["close"] * (1 + self.strategy_params["trailing_sl"]), None))  # Sell SL

    def detect_rsi_divergence(self):
        """
        Detects RSI Divergence (Bullish/Bearish).

        - Bullish Divergence: Price forms a lower low while RSI forms a higher low.
        - Bearish Divergence: Price forms a higher high while RSI forms a lower high.

        Returns:
            np.array: An array indicating divergence signals:
                      1 for bullish divergence, -1 for bearish divergence, 0 otherwise.
        """

        divergence = np.zeros(len(self.df))

        for i in range(2, len(self.df)):
            # Bullish Divergence (Price Lower Low, RSI Higher Low)
            if self.df["close"].iloc[i] < self.df["close"].iloc[i - 1] and self.df["RSI"].iloc[i] > self.df["RSI"].iloc[i - 1]:
                divergence[i] = 1

            # Bearish Divergence (Price Higher High, RSI Lower High)
            elif self.df["close"].iloc[i] > self.df["close"].iloc[i - 1] and self.df["RSI"].iloc[i] < self.df["RSI"].iloc[i - 1]:
                divergence[i] = -1

        return divergence
