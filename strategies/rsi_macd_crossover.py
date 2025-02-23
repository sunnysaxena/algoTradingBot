import talib
import pandas_ta as ta
import numpy as np
import pandas as pd
from strategies.base_strategy import BaseStrategy


class RSI_MACD_CrossoverStrategy(BaseStrategy):
    def __init__(self, df, strategy_params, library="talib"):
        super().__init__(df, strategy_params)
        self.library = library  # Choose between "talib" or "pandas_ta"

    def apply_strategy(self):
        signals = pd.DataFrame(index=self.df.index)
        signals["close"] = self.df["close"]

        rsi_period = self.strategy_params["rsi_period"]
        rsi_overbought = self.strategy_params["rsi_overbought"]
        rsi_oversold = self.strategy_params["rsi_oversold"]
        fast_length = self.strategy_params["macd_fast"]
        slow_length = self.strategy_params["macd_slow"]
        signal_length = self.strategy_params["macd_signal"]

        # Compute RSI and MACD based on selected library
        if self.library == "talib":
            self.df["RSI"] = talib.RSI(self.df["close"].values, timeperiod=rsi_period)
            self.df["MACD"], self.df["MACD_Signal"], self.df["MACD_Hist"] = talib.MACD(
                self.df["close"].values,
                fastperiod=fast_length,
                slowperiod=slow_length,
                signalperiod=signal_length
            )

        elif self.library == "pandas_ta":
            self.df["RSI"] = self.df.ta.rsi(length=rsi_period)

            macd_df = self.df.ta.macd(
                fast=fast_length, slow=slow_length, signal=signal_length, append=True
            )
            self.df["MACD"] = macd_df[f"MACD_{fast_length}_{slow_length}_{signal_length}"]
            self.df["MACD_Signal"] = macd_df[f"MACDs_{fast_length}_{slow_length}_{signal_length}"]
            self.df["MACD_Hist"] = macd_df[f"MACDh_{fast_length}_{slow_length}_{signal_length}"]

        # Generate buy/sell signals based on RSI and MACD crossover
        buy_condition = (self.df["RSI"] < rsi_oversold) & (self.df["MACD"] > self.df["MACD_Signal"])
        sell_condition = (self.df["RSI"] > rsi_overbought) & (self.df["MACD"] < self.df["MACD_Signal"])

        signals["signal"] = np.where(buy_condition, 1, np.where(sell_condition, -1, 0))

        self.signals = signals


class RSI_MACD_CrossoverStrategyV1(BaseStrategy):
    def __init__(self, df, strategy_params, library="talib"):
        super().__init__(df, strategy_params)
        self.library = library  # Choose between "talib" or "pandas_ta"

    def apply_strategy(self):
        signals = pd.DataFrame(index=self.df.index)
        signals["close"] = self.df["close"]

        # Extract parameters
        rsi_period = self.strategy_params.get("rsi_period", 14)
        rsi_overbought = self.strategy_params.get("rsi_overbought", 70)
        rsi_oversold = self.strategy_params.get("rsi_oversold", 30)
        fast_length = self.strategy_params.get("macd_fast", 12)
        slow_length = self.strategy_params.get("macd_slow", 26)
        signal_length = self.strategy_params.get("macd_signal", 9)
        stop_loss_pct = self.strategy_params.get("stop_loss_pct", 0.02)  # 2%
        take_profit_pct = self.strategy_params.get("take_profit_pct", 0.05)  # 5%
        trailing_sl_pct = self.strategy_params.get("trailing_sl_pct", 0.03)  # 3%

        # Compute RSI & MACD
        if self.library == "talib":
            self.df["RSI"] = talib.RSI(self.df["close"], timeperiod=rsi_period)
            self.df["MACD"], self.df["MACD_Signal"], _ = talib.MACD(
                self.df["close"], fastperiod=fast_length, slowperiod=slow_length, signalperiod=signal_length
            )
        elif self.library == "pandas_ta":
            self.df["RSI"] = self.df.ta.rsi(length=rsi_period)
            macd_df = self.df.ta.macd(fast=fast_length, slow=slow_length, signal=signal_length, append=True)
            self.df["MACD"] = macd_df[f"MACD_{fast_length}_{slow_length}_{signal_length}"]
            self.df["MACD_Signal"] = macd_df[f"MACDs_{fast_length}_{slow_length}_{signal_length}"]

        # Buy/Sell Conditions
        buy_condition = (self.df["RSI"] < rsi_oversold) & (self.df["MACD"] > self.df["MACD_Signal"])
        sell_condition = (self.df["RSI"] > rsi_overbought) & (self.df["MACD"] < self.df["MACD_Signal"])

        signals["signal"] = np.where(buy_condition, 1, np.where(sell_condition, -1, 0))

        # Stop-Loss & Take-Profit Implementation
        signals["entry_price"] = np.nan
        signals["stop_loss"] = np.nan
        signals["take_profit"] = np.nan
        signals["trailing_stop"] = np.nan
        position = 0

        for i in range(1, len(signals)):
            if signals["signal"].iloc[i] == 1 and position == 0:  # Buy
                entry_price = self.df["close"].iloc[i]
                stop_loss = entry_price * (1 - stop_loss_pct)
                take_profit = entry_price * (1 + take_profit_pct)
                trailing_stop = entry_price * (1 - trailing_sl_pct)

                signals.at[signals.index[i], "entry_price"] = entry_price
                signals.at[signals.index[i], "stop_loss"] = stop_loss
                signals.at[signals.index[i], "take_profit"] = take_profit
                signals.at[signals.index[i], "trailing_stop"] = trailing_stop

                position = 1  # Holding

            elif position == 1:  # Manage trade
                current_price = self.df["close"].iloc[i]
                if current_price >= signals["take_profit"].iloc[i-1]:  # Take profit hit
                    signals.at[signals.index[i], "signal"] = -1
                    position = 0
                elif current_price <= signals["stop_loss"].iloc[i-1]:  # Stop-loss hit
                    signals.at[signals.index[i], "signal"] = -1
                    position = 0
                elif current_price > signals["trailing_stop"].iloc[i-1]:  # Adjust trailing stop
                    new_trailing_stop = current_price * (1 - trailing_sl_pct)
                    signals.at[signals.index[i], "trailing_stop"] = new_trailing_stop
                else:
                    signals.at[signals.index[i], "trailing_stop"] = signals["trailing_stop"].iloc[i-1]

        self.signals = signals