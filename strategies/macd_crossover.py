import talib
import pandas_ta as ta
import numpy as np
import pandas as pd
from strategies.base_strategy import BaseStrategy

class MACD_CrossoverStrategy(BaseStrategy):
    def __init__(self, df, strategy_params, library="talib"):
        super().__init__(df, strategy_params)
        self.library = library  # Choose between "talib" or "pandas_ta"

    def apply_strategy(self):
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
