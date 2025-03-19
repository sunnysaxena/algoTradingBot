import numpy as np
import pandas as pd
from strategies.base_strategy import BaseStrategy

class BreakoutStrategy(BaseStrategy):
    """
    Implements a Breakout Strategy based on historical high and low levels.
    """

    def __init__(self, df, strategy_params):
        """
        Initializes the Breakout Strategy.
        """
        super().__init__(df, strategy_params)

    def apply_strategy(self):
        """
        Applies the Breakout strategy to generate buy and sell signals.
        """
        signals = pd.DataFrame(index=self.df.index)
        signals["close"] = self.df["close"]

        breakout_period = self.strategy_params["breakout_period"]

        # Calculate breakout levels
        self.df["High_Breakout"] = self.df["high"].rolling(window=breakout_period).max()
        self.df["Low_Breakout"] = self.df["low"].rolling(window=breakout_period).min()

        # Handle NaN values (fill with the first valid value)
        self.df["High_Breakout"].fillna(method='bfill', inplace=True)
        self.df["Low_Breakout"].fillna(method='bfill', inplace=True)

        # Generate signals
        signals["signal"] = np.where(
            self.df["close"] > self.df["High_Breakout"], 1,  # Buy Signal (Breakout Up)
            np.where(self.df["close"] < self.df["Low_Breakout"], -1, 0)  # Sell Signal (Breakout Down)
        )

        self.signals = signals

    def generate_signal(self, row, positions):
        """
        Generates a trading signal for a given data row and position.

        Args:
            row (pd.Series): A single row of market data.
            positions (dict): Dictionary tracking the current positions.

        Returns:
            int: 1 for buy, -1 for sell, 0 for no signal.
        """

        print(f"Close: {row['close']}, High_Breakout: {row['High_Breakout']}, Low_Breakout: {row['Low_Breakout']}")
        input()


        if row["close"] > row["High_Breakout"]:
            return 1  # Buy signal
        elif row["close"] < row["Low_Breakout"]:
            return -1  # Sell signal
        else:
            return 0  # No signal