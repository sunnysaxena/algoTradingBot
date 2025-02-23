import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, df, strategy_params, library="talib"):
        self.df = df
        self.strategy_params = strategy_params
        self.signals = None
        self.library = self._load_library(library)

    def _load_library(self, library_name):
        """Dynamically load talib or pandas_ta"""
        if library_name == "talib":
            import talib
            return talib
        elif library_name == "pandas_ta":
            import pandas_ta as ta
            return ta
        else:
            raise ValueError(f"Unsupported library: {library_name}")

    @abstractmethod
    def apply_strategy(self):
        """Define the strategy logic in child classes"""
        pass

    def backtest(self, initial_capital=100000, commission=0.001, slippage=0.0005):
        """Backtest logic (shared by all strategies)"""
        self.df["returns"] = self.df["close"].pct_change()
        self.df["strategy_returns"] = self.df["returns"] * self.signals["signal"].shift(1)

        # Apply transaction costs
        self.df["strategy_returns"] -= (commission + slippage)

        # Compute cumulative returns
        self.df["cumulative_returns"] = (1 + self.df["strategy_returns"]).cumprod() * initial_capital

        return self.df

    def plot_results(self):
        """Plot trading signals & cumulative returns"""
        fig, ax = plt.subplots(2, 1, figsize=(12, 8))

        # Price & Buy/Sell Signals
        ax[0].plot(self.df.index, self.df["close"], label="Close Price", color="black", linewidth=1)
        buy_signals = self.df[self.signals["signal"] == 1]
        sell_signals = self.df[self.signals["signal"] == -1]
        ax[0].scatter(buy_signals.index, buy_signals["close"], label="Buy Signal", marker="^", color="green")
        ax[0].scatter(sell_signals.index, sell_signals["close"], label="Sell Signal", marker="v", color="red")
        ax[0].set_title("Entry & Exit Points")
        ax[0].legend()

        # Cumulative Returns
        ax[1].plot(self.df.index, self.df["cumulative_returns"], label="Cumulative Returns", color="blue")
        ax[1].set_title("Portfolio Performance")
        ax[1].legend()

        plt.tight_layout()
        plt.show()
