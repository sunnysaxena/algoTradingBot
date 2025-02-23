"""
RSI & MACD Crossover Strategy for Algorithmic Trading

### Strategy Overview:
This strategy combines the **Relative Strength Index (RSI)** and the **Moving Average Convergence Divergence (MACD)**
to generate buy and sell signals. It also incorporates risk management features such as **stop-loss**, **take-profit**,
and **trailing stop-loss** to enhance trading performance.

### Strategy Logic:
1. **RSI Calculation:**
   - Measures momentum and identifies overbought (>=70) and oversold (<=30) conditions.

2. **MACD Calculation:**
   - Uses the MACD line (difference between short and long EMA) and the signal line (smoothed MACD) to detect trends.

3. **Trade Entry Rules:**
   - **Buy Signal:** RSI crosses below the oversold level (e.g., 30) AND MACD crosses above its signal line.
   - **Sell Signal:** RSI crosses above the overbought level (e.g., 70) AND MACD crosses below its signal line.

4. **Risk Management:**
   - **Stop-Loss:** Set at a percentage below/above the entry price to limit losses.
   - **Take-Profit:** Automatically exits trades when a target profit percentage is reached.
   - **Trailing Stop-Loss:** Adjusts dynamically to lock in profits as price moves favorably.

### Features:
✅ **Customizable RSI & MACD parameters** (period, thresholds, fast/slow/signal lengths).
✅ **Dual Confirmation** with RSI & MACD to reduce false signals.
✅ **Integrated Risk Management** (Stop-Loss, Take-Profit, and Trailing Stop-Loss).
✅ **Compatible with both TA-Lib and pandas_ta** for flexibility.
✅ **Seamless Backtesting** with `BaseStrategy` framework.
"""

import talib
import numpy as np
import pandas as pd
import pandas_ta as ta
from strategies.base_strategy import BaseStrategy


class RSI_MACD_CrossoverStrategy(BaseStrategy):
    """
    RSI & MACD Crossover Strategy

    This strategy combines the Relative Strength Index (RSI) and the Moving Average Convergence Divergence (MACD)
    indicators to generate buy and sell signals.

    Features:
    - Uses either TA-Lib or pandas_ta for indicator computation.
    - Generates buy signals when RSI is oversold and MACD crosses above its signal line.
    - Generates sell signals when RSI is overbought and MACD crosses below its signal line.
    - Provides flexibility to configure RSI and MACD parameters via strategy_params.
    """

    def __init__(self, df, strategy_params, library="talib"):
        """
        Initializes the RSI_MACD_CrossoverStrategy.

        Parameters:
        - df (pd.DataFrame): Historical market data containing 'close' prices.
        - strategy_params (dict): Dictionary of strategy parameters including:
            - rsi_period (int): Lookback period for RSI calculation.
            - rsi_overbought (int): RSI threshold for overbought condition.
            - rsi_oversold (int): RSI threshold for oversold condition.
            - macd_fast (int): Fast EMA period for MACD.
            - macd_slow (int): Slow EMA period for MACD.
            - macd_signal (int): Signal line period for MACD.
        - library (str): Choice of library for calculations ('talib' or 'pandas_ta').
        """
        super().__init__(df, strategy_params)
        self.library = library  # Choose between "talib" or "pandas_ta"

    def apply_strategy(self):
        """
        Applies the RSI and MACD crossover strategy to generate trading signals.
        """
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