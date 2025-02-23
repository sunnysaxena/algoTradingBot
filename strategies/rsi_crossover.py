import talib
import numpy as np
import pandas as pd
import pandas_ta as ta
from strategies.base_strategy import BaseStrategy

class RSI_CrossoverStrategy(BaseStrategy):
    def __init__(self, df, strategy_params, library="talib"):
        super().__init__(df, strategy_params)
        self.library = library  # Choose between "talib" or "pandas_ta"

    def apply_strategy(self):
        """Apply RSI Crossover Strategy with Enhancements"""

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
        """Detect RSI Divergence (Bullish/Bearish)"""
        divergence = np.zeros(len(self.df))

        for i in range(2, len(self.df)):
            # Bullish Divergence (Price Lower Low, RSI Higher Low)
            if self.df["close"].iloc[i] < self.df["close"].iloc[i - 1] and self.df["RSI"].iloc[i] > self.df["RSI"].iloc[i - 1]:
                divergence[i] = 1

            # Bearish Divergence (Price Higher High, RSI Lower High)
            elif self.df["close"].iloc[i] > self.df["close"].iloc[i - 1] and self.df["RSI"].iloc[i] < self.df["RSI"].iloc[i - 1]:
                divergence[i] = -1

        return divergence
