import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import mysql.connector
import logging

# Configure logging
logging.basicConfig(filename="backtest.log", level=logging.INFO, format="%(asctime)s - %(message)s")


class EMARsiBacktester:
    def __init__(self, data, initial_balance=10000, risk_per_trade=0.02, commission=0.0005, slippage=0.01):
        """
        Backtest EMA 9-21 & RSI crossover strategy with risk management.

        :param data: DataFrame containing OHLCV data
        :param initial_balance: Starting capital
        :param risk_per_trade: % of capital risked per trade
        :param commission: Commission per trade (0.05% default)
        :param slippage: Slippage amount
        """
        self.data = data.copy()
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.commission = commission
        self.slippage = slippage
        self.positions = []
        self.trades = []
        self.apply_strategy()

    def apply_strategy(self):
        """Calculates EMA 9, EMA 21, RSI (14) and generates buy/sell signals."""
        self.data["Short_EMA"] = ta.ema(self.data["close"], length=9)
        self.data["Long_EMA"] = ta.ema(self.data["close"], length=21)
        self.data["RSI"] = ta.rsi(self.data["close"], length=14)

        self.data["Signal"] = "HOLD"

        for i in range(1, len(self.data)):
            if (
                    self.data["Short_EMA"][i] > self.data["Long_EMA"][i]
                    and self.data["RSI"][i] < 70
            ):
                self.data.loc[self.data.index[i], "Signal"] = "BUY"
            elif (
                    self.data["Short_EMA"][i] < self.data["Long_EMA"][i]
                    and self.data["RSI"][i] > 30
            ):
                self.data.loc[self.data.index[i], "Signal"] = "SELL"

    def run_backtest(self, stop_loss_pct=0.02, take_profit_pct=0.04):
        """Executes trades with SL & TP."""
        for i in range(len(self.data)):
            price = self.data["close"][i] * (1 + self.slippage)
            signal = self.data["Signal"][i]
            size = (self.balance * self.risk_per_trade) / price  # Position size

            if signal == "BUY" and not self.positions:
                stop_loss = price * (1 - stop_loss_pct)
                take_profit = price * (1 + take_profit_pct)
                self.positions.append((price, stop_loss, take_profit, size))
                logging.info(f"BUY at {price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")

            elif signal == "SELL" and self.positions:
                entry_price, stop_loss, take_profit, size = self.positions.pop(0)
                if price >= take_profit or price <= stop_loss:
                    profit = (price - entry_price) * size - (price * size * self.commission)
                    self.balance += profit
                    self.trades.append(profit)
                    logging.info(f"SELL at {price:.2f}, Profit: {profit:.2f}")

        self.data["Equity"] = self.initial_balance + pd.Series(self.trades).cumsum().fillna(0)

    def plot_results(self):
        """Plots equity curve & trade signals."""
        plt.figure(figsize=(12, 6))
        plt.plot(self.data.index, self.data["close"], label="Close Price", color="blue")
        plt.plot(self.data.index, self.data["Short_EMA"], label="EMA 9", linestyle="dashed", color="green")
        plt.plot(self.data.index, self.data["Long_EMA"], label="EMA 21", linestyle="dashed", color="red")

        buy_signals = self.data[self.data["Signal"] == "BUY"]
        sell_signals = self.data[self.data["Signal"] == "SELL"]

        plt.scatter(buy_signals.index, buy_signals["close"], marker="^", color="green", label="Buy Signal", alpha=1,
                    edgecolors="black")
        plt.scatter(sell_signals.index, sell_signals["close"], marker="v", color="red", label="Sell Signal", alpha=1,
                    edgecolors="black")

        plt.title("Enhanced EMA 9-21 & RSI Strategy Backtest")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.show()

    def print_performance(self):
        """Prints performance metrics."""
        total_trades = len(self.trades)
        wins = len([t for t in self.trades if t > 0])
        losses = total_trades - wins
        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
        total_profit = sum(self.trades)
        profit_factor = sum(t for t in self.trades if t > 0) / abs(
            sum(t for t in self.trades if t < 0)) if losses > 0 else "N/A"

        print(f"Initial Balance: ${self.initial_balance}")
        print(f"Final Balance: ${self.balance:.2f}")
        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {wins} | Losing Trades: {losses}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Total Profit: ${total_profit:.2f}")
        print(f"Profit Factor: {profit_factor}")


# Load historical data from MySQL
def load_data_from_mysql():
    conn = mysql.connector.connect(
        host="localhost",
        user="your_user",
        password="your_password",
        database="your_database"
    )
    query = "SELECT date, open, high, low, close, volume FROM historical_ohlc_data"
    df = pd.read_sql(query, conn, parse_dates=["date"])
    conn.close()
    df.set_index("date", inplace=True)
    return df


# Fetch data and run backtest
df = load_data_from_mysql()
backtester = EMARsiBacktester(df)
backtester.run_backtest()
backtester.print_performance()
backtester.plot_results()
