import os
import yaml
import talib
import pandas as pd
import pandas_ta as ta
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load the .env and config.yml file explicitly from config/
ROOT_DIR = Path(__file__).resolve().parent.parent  # Move up levels if needed
config_path = os.path.join(ROOT_DIR, "config/config.yaml")
env_path = os.path.join(ROOT_DIR, "config/.env")

# Load environment variables
load_dotenv(env_path)

# Load config.yml
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# Database Connection
DB_HOST = os.getenv("MYSQL_HOST")
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
# URL-encode the password
DB_PASSWORD = quote_plus(DB_PASSWORD)
DB_NAME = config["database"]["mysql"]["name"]
DB_TABLE = config['database']['mysql']['historical_data_table']

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")


# Load Historical Data
def load_historical_data(symbol=None):
    df = None
    query = f"SELECT timestamp, open, high, low, close, volume FROM {DB_TABLE} LIMIT 365"
    try:
        df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    except Exception as e:
        print("Exception : " + str(e))

    df.set_index("timestamp", inplace=True)
    return df


# Apply Strategy using pandas_ta
def apply_strategy(df, strategy_name, strategy_params, library):
    signals = pd.DataFrame(index=df.index)
    signals["close"] = df["close"]

    if library == 'talib':
        if strategy_name == "EMA_Crossover":

            # Convert Pandas Series to NumPy Array (Talib)
            df["EMA_Short"] = talib.EMA(df["close"].values, strategy_params["ema_short"])  # Manual conversion
            df["EMA_Long"] = talib.EMA(df["close"].values, strategy_params["ema_long"])  # Manual conversion
            signals["signal"] = np.where(df["EMA_Short"] > df["EMA_Long"], 1, -1)

        elif strategy_name == "RSI_Overbought_Oversold":
            # Convert Pandas Series to NumPy Array (Talib)
            df["RSI"] = talib.EMA(df["close"].values, strategy_params["rsi_period"])  # Manual conversion

            signals["signal"] = np.where(df["RSI"] < strategy_params["oversold"], 1,
                                         np.where(df["RSI"] > strategy_params["overbought"], -1, 0))

        elif strategy_name == "MACD_Crossover":
            # Calculate MACD using TA-Lib
            df["MACD"], df["Signal"], df["Hist"] = talib.MACD(df["close"], strategy_params["fast_length"],
                                                              strategy_params["slow_length"],
                                                              strategy_params["signal_length"])
            signals["signal"] = np.where(df["MACD"] > df["Signal"], 1, -1)

        elif strategy_name == "EMA_RSI_Crossover":

            # Calculate EMA Short & EMA Long (talib)
            df["EMA_Short"] = talib.EMA(df["close"].values, strategy_params["ema_short"])
            df["EMA_Long"] = talib.EMA(df["close"].values, strategy_params["ema_long"])

            # Calculate RSI
            df["RSI"] = talib.RSI(df["close"].values, strategy_params["rsi_period"])

            # Generate Buy & Sell Signals
            signals["signal"] = np.where(
                (df["EMA_Short"] > df["EMA_Long"]) & (df["EMA_Short"].shift(1) <= df["EMA_Long"].shift(1)) & (
                        df["RSI"] > 50), 1, np.where(
                    (df["EMA_Short"] < df["EMA_Long"]) & (df["EMA_Short"].shift(1) >= df["EMA_Long"].shift(1)) & (
                            df["RSI"] < 50), -1, 0)
            )
        return signals
    else:
        if strategy_name == "EMA_Crossover":
            # Directly apply Pandas_TA (No .values needed)
            df["EMA_Short"] = df.ta.ema(strategy_params["ema_short"])
            df["EMA_Long"] = df.ta.ema(strategy_params["ema_long"])
            signals["signal"] = np.where(df["EMA_Short"] > df["EMA_Long"], 1, -1)


        elif strategy_name == "RSI_Overbought_Oversold":
            # Directly apply Pandas_TA (No .values needed)
            df["RSI"] = df.ta.rsi(strategy_params["rsi_period"])
            signals["signal"] = np.where(df["RSI"] < strategy_params["oversold"], 1,
                                         np.where(df["RSI"] > strategy_params["overbought"], -1, 0))

        elif strategy_name == "MACD_Crossover":
            # Calculate MACD using Pandas_TA (macd, histogram, signal columns.)
            df.ta.macd(close="close", fast=strategy_params["fast_length"], slow=strategy_params["slow_length"],
                       signal=strategy_params["signal_length"], append=True)
            signals["signal"] = np.where(df["MACD_12_26_9"] > df["MACDs_12_26_9"], 1, -1)


        elif strategy_name == "EMA_RSI_Crossover":
            # Calculate EMA Short & EMA Long using (Pandas_TA)
            df["EMA_Short"] = df.ta.ema(strategy_params["ema_short"])
            df["EMA_Long"] = df.ta.ema(strategy_params["ema_long"])

            # Calculate RSI using Pandas_TA
            df["RSI"] = df.ta.rsi(strategy_params["rsi_period"])

            # Generate Buy & Sell Signals
            signals["signal"] = np.where(
                (df["EMA_Short"] > df["EMA_Long"]) & (df["EMA_Short"].shift(1) <= df["EMA_Long"].shift(1)) & (
                        df["RSI"] > 50), 1, np.where(
                    (df["EMA_Short"] < df["EMA_Long"]) & (df["EMA_Short"].shift(1) >= df["EMA_Long"].shift(1)) & (
                            df["RSI"] < 50), -1, 0)
            )

        return signals


# Backtesting Function
def backtest(df, signals):
    capital = config["backtesting"]["capital"]
    commission = config["backtesting"]["commission"]
    slippage = config["backtesting"]["slippage"]

    df["returns"] = df["close"].pct_change()
    df["strategy_returns"] = df["returns"] * signals["signal"].shift(1)
    df["signal"] = signals["signal"]  # Ensure signal column is retained

    # Apply transaction costs
    df["strategy_returns"] -= (commission + slippage)

    # Compute cumulative returns
    df["cumulative_returns"] = (1 + df["strategy_returns"]).cumprod() * capital

    return df


# Performance Metrics
def performance_metrics(df):
    final_pnl = df["cumulative_returns"].iloc[-1] - config["backtesting"]["capital"]
    total_trades = df["signal"].diff().fillna(0).abs().sum() // 2  # Count position changes
    win_trades = (df["strategy_returns"] > 0).sum()
    loss_trades = (df["strategy_returns"] < 0).sum()
    win_rate = (win_trades / (win_trades + loss_trades)) * 100 if win_trades + loss_trades > 0 else 0

    # Sharpe Ratio
    daily_returns = df["strategy_returns"].dropna()
    sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0

    # Max Drawdown
    cumulative = df["cumulative_returns"]
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    print("\n🔹 **Backtest Performance Summary** 🔹")
    print(f"📈 Final P&L: ₹{final_pnl:.2f}")
    print(f"📊 Total Trades: {int(total_trades)}")
    print(f"✅ Win Rate: {win_rate:.2f}%")
    print(f"📉 Max Drawdown: {max_drawdown:.2%}")
    print(f"⚡ Sharpe Ratio: {sharpe_ratio:.2f}")


# Plot Results
def plot_results(df, signals, strategy_name):
    fig, ax = plt.subplots(2, 1, figsize=(12, 8))

    # Price & Buy/Sell Signals
    ax[0].plot(df.index, df["close"], label="Close Price", color="black", linewidth=1)
    buy_signals = df[signals["signal"] == 1]
    sell_signals = df[signals["signal"] == -1]
    ax[0].scatter(buy_signals.index, buy_signals["close"], label="Buy Signal", marker="^", color="green", alpha=1)
    ax[0].scatter(sell_signals.index, sell_signals["close"], label="Sell Signal", marker="v", color="red", alpha=1)
    ax[0].set_title(f"{strategy_name} Strategy - Entry & Exit Points")
    ax[0].legend()

    # Cumulative Returns
    ax[1].plot(df.index, df["cumulative_returns"], label="Cumulative Returns", color="blue", linewidth=1.5)
    ax[1].set_title("Portfolio Performance")
    ax[1].legend()

    plt.tight_layout()
    plt.show()


# Main Execution
def run_backtest():
    library = config["trading"]["library"]['name']
    active_strategy = config["trading"]["active_strategy"]
    strategy_params = config["trading"]["strategies"][active_strategy]

    symbol = "NIFTY50"  # Change to test different stocks
    df = load_historical_data(symbol)
    print(f"\n🚀 Running Backtest for {active_strategy} on {symbol}...")

    signals = apply_strategy(df, active_strategy, strategy_params, library)
    results = backtest(df, signals)

    performance_metrics(results)
    plot_results(results, signals, active_strategy)


# Run Backtest
run_backtest()
