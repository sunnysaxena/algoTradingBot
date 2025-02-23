import numpy as np
import pandas as pd
from strategies.base_strategy import BaseStrategy


class StraddleStrangleStrategy(BaseStrategy):
    """
    Straddle & Strangle Options Strategy Implementation
    This strategy automatically selects ATM (At-the-Money) and OTM (Out-of-the-Money) options and manages trades with stop-loss, take-profit, and trailing stop mechanisms.
    """

    def __init__(self, df, strategy_params):
        super().__init__(df, strategy_params)

    def apply_strategy(self):
        signals = pd.DataFrame(index=self.df.index)
        signals["close"] = self.df["close"]

        # Extract strategy parameters
        atm_strike_diff = self.strategy_params.get("atm_strike_diff", 50)  # ATM strike difference
        otm_strike_diff = self.strategy_params.get("otm_strike_diff", 100)  # OTM strike difference
        stop_loss_pct = self.strategy_params.get("stop_loss_pct", 0.02)  # 2%
        take_profit_pct = self.strategy_params.get("take_profit_pct", 0.05)  # 5%
        trailing_sl_pct = self.strategy_params.get("trailing_sl_pct", 0.03)  # 3%

        # Determine ATM strike price
        atm_strike = round(self.df["close"].iloc[-1] / atm_strike_diff) * atm_strike_diff
        otm_ce_strike = atm_strike + otm_strike_diff  # OTM CE
        otm_pe_strike = atm_strike - otm_strike_diff  # OTM PE

        # Simulated options pricing
        self.df["ATM_CE"] = self.df["close"] * 0.05  # Assume 5% premium for ATM CE
        self.df["ATM_PE"] = self.df["close"] * 0.05  # Assume 5% premium for ATM PE
        self.df["OTM_CE"] = self.df["close"] * 0.03  # Assume 3% premium for OTM CE
        self.df["OTM_PE"] = self.df["close"] * 0.03  # Assume 3% premium for OTM PE

        # Generate buy/sell signals for straddle & strangle
        signals["signal"] = 0
        signals["entry_price"] = np.nan
        signals["stop_loss"] = np.nan
        signals["take_profit"] = np.nan
        signals["trailing_stop"] = np.nan

        position = 0

        for i in range(1, len(signals)):
            current_price = self.df["close"].iloc[i]
            atm_ce_price = self.df["ATM_CE"].iloc[i]
            atm_pe_price = self.df["ATM_PE"].iloc[i]

            if position == 0:  # Enter trade
                entry_price = atm_ce_price + atm_pe_price
                stop_loss = entry_price * (1 - stop_loss_pct)
                take_profit = entry_price * (1 + take_profit_pct)
                trailing_stop = entry_price * (1 - trailing_sl_pct)

                signals.at[signals.index[i], "entry_price"] = entry_price
                signals.at[signals.index[i], "stop_loss"] = stop_loss
                signals.at[signals.index[i], "take_profit"] = take_profit
                signals.at[signals.index[i], "trailing_stop"] = trailing_stop

                signals.at[signals.index[i], "signal"] = 1
                position = 1  # Trade active

            elif position == 1:  # Manage trade
                current_price = atm_ce_price + atm_pe_price

                if current_price >= signals["take_profit"].iloc[i - 1]:  # Take profit hit
                    signals.at[signals.index[i], "signal"] = -1
                    position = 0
                elif current_price <= signals["stop_loss"].iloc[i - 1]:  # Stop-loss hit
                    signals.at[signals.index[i], "signal"] = -1
                    position = 0
                elif current_price > signals["trailing_stop"].iloc[i - 1]:  # Adjust trailing stop
                    new_trailing_stop = current_price * (1 - trailing_sl_pct)
                    signals.at[signals.index[i], "trailing_stop"] = new_trailing_stop
                else:
                    signals.at[signals.index[i], "trailing_stop"] = signals["trailing_stop"].iloc[i - 1]

        self.signals = signals
