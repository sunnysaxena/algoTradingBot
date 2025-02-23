import talib
import numpy as np
import pandas as pd
import pandas_ta as ta
from strategies.base_strategy import BaseStrategy

class EMA_RSI_CrossoverStrategy(BaseStrategy):
    def __init__(self, df, strategy_params, library="talib"):
        super().__init__(df, strategy_params)
        self.library = library  # Choose between "talib" or "pandas_ta"

    def apply_strategy(self):
        signals = pd.DataFrame(index=self.df.index)
        signals["close"] = self.df["close"]

        short_period = self.strategy_params["ema_short"]
        long_period = self.strategy_params["ema_long"]
        rsi_period = self.strategy_params["rsi_period"]
        overbought = self.strategy_params["rsi_overbought"]
        oversold = self.strategy_params["rsi_oversold"]

        if self.library == "talib":
            self.df["EMA_Short"] = talib.EMA(self.df["close"].values, timeperiod=short_period)
            self.df["EMA_Long"] = talib.EMA(self.df["close"].values, timeperiod=long_period)
            self.df["RSI"] = talib.RSI(self.df["close"].values, timeperiod=rsi_period)

        elif self.library == "pandas_ta":
            self.df["EMA_Short"] = self.df.ta.ema(length=short_period)
            self.df["EMA_Long"] = self.df.ta.ema(length=long_period)
            self.df["RSI"] = self.df.ta.rsi(length=rsi_period)

        signals["signal"] = np.where(
            (self.df["EMA_Short"] > self.df["EMA_Long"]) & (self.df["RSI"] > overbought), -1,  # Sell Signal
            np.where((self.df["EMA_Short"] < self.df["EMA_Long"]) & (self.df["RSI"] < oversold), 1, 0)  # Buy Signal
        )

        self.signals = signals
