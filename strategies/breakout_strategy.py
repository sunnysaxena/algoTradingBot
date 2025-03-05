"""
Breakout Trading Strategy

This strategy identifies breakouts above resistance or below support based on the highest high
and lowest low over a specified period.

Features:
- Uses a rolling high and low to define breakout levels.
- Generates buy (1) and sell (-1) signals based on breakouts.
- Can be configured with different breakout periods.

Signal Generation:
- Buy Signal (1) → When the closing price breaks above the highest high over `breakout_period`.
- Sell Signal (-1) → When the closing price breaks below the lowest low over `breakout_period`.

Usage:
- Configure `breakout_period` in `config.yml`.
"""

import numpy as np
import pandas as pd
from strategies.base_strategy import BaseStrategy

class BreakoutStrategy(BaseStrategy):
    """
    Implements a Breakout Strategy based on historical high and low levels.

    Attributes:
        df (pd.DataFrame): Market data containing OHLC prices.
        strategy_params (dict): Dictionary containing strategy parameters like `breakout_period`.
    """

    def __init__(self, df, strategy_params):
        """
        Initializes the Breakout Strategy.

        Parameters:
            df (pd.DataFrame): Market data with OHLC prices.
            strategy_params (dict): Configuration containing breakout period.
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

        # Generate signals
        signals["signal"] = np.where(
            self.df["close"] > self.df["High_Breakout"], 1,  # Buy Signal (Breakout Up)
            np.where(self.df["close"] < self.df["Low_Breakout"], -1, 0)  # Sell Signal (Breakout Down)
        )

        self.signals = signals
