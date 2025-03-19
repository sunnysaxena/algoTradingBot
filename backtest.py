# backtest.py
import os
import yaml
import asyncio
import logging
import json
import pandas as pd
from dotenv import load_dotenv
from utils.env_loader import load_env
from utils.config_loader import load_config
from database.handler import DatabaseHandler
from strategies.ema_crossover import EMA_CrossoverStrategy
from strategies.ema_rsi_crossover import EMA_RSI_CrossoverStrategy
from strategies.macd_crossover import MACD_CrossoverStrategy
from strategies.rsi_macd_crossover import RSI_MACD_CrossoverStrategy
from strategies.rsi_crossover import RSI_CrossoverStrategy
from strategies.straddle_strangle import StraddleStrangleStrategy
from strategies.breakout_strategy import BreakoutStrategy
from backtest_engine.backtest_runner import BacktestRunner
from utils.logger import setup_logging, get_logger

# Load environment variables
load_dotenv(load_env())
config_yaml = load_config()

# Configure Logging
setup_logging()
logger = get_logger(__name__)

# Load Config
with open(config_yaml, "r") as file:
    config = yaml.safe_load(file)

# Strategy Mapping
strategy_mapping = {
    "EMA_CrossoverStrategy": EMA_CrossoverStrategy,
    "EMA_RSI_CrossoverStrategy": EMA_RSI_CrossoverStrategy,
    "MACD_CrossoverStrategy": MACD_CrossoverStrategy,
    "RSI_CrossoverStrategy": RSI_CrossoverStrategy,
    "RSI_MACD_CrossoverStrategy": RSI_MACD_CrossoverStrategy,
    # "StraddleStrangleStrategy": StraddleStrangleStrategy,
    # "BreakoutStrategy": BreakoutStrategy
}

db_type = config.get("database", {}).get("type", "timescaledb")
db_config = config.get("database", {}).get(db_type, {})
start_time = config["backtesting"]["start_date"]
end_time = config["backtesting"]["end_date"]

active_strategy = config["trading"].get("active_strategy", None)
strategies = config["trading"].get("strategies", {})

if not active_strategy or active_strategy not in strategies:
    raise ValueError(f"⚠️ Active strategy '{active_strategy}' not found in configuration.")

strategy_params = strategies[active_strategy]

if not isinstance(strategy_params, dict):
    raise TypeError(f"🚨 Expected 'strategy_params' to be a dictionary but got {type(strategy_params)}")

strategy_name = strategy_params.get("name", active_strategy)
db_handler = DatabaseHandler(db_config)

backtesting_symbols = config["backtesting"].get("symbols", ["NIFTY50"])
timeframes = config["backtesting"].get("timeframes", ["1m", "5m", "15m", "1h", "1d"])

symbol_table_mapping = {
    ("NIFTY50", "1m"): "nifty50_1m",
    ("NIFTY50", "5m"): "nifty50_1m",
    ("NIFTY50", "15m"): "nifty50_1m",
    ("NIFTY50", "1h"): "nifty50_1m",
    ("NIFTY50", "1d"): "nifty50_1m",


    ("SENSEX", "1m"): "sensex_1m",
    ("SENSEX", "5m"): "sensex_1m",
    ("SENSEX", "15m"): "sensex_1m",
    ("SENSEX", "1h"): "sensex_1m",
    ("SENSEX", "1d"): "sensex_1m",
}

async def run_backtest():
    """Run backtest on historical data and store results in JSON."""
    all_backtest_results = []
    try:
        for strategy_name, strategy_params in strategies.items():
            if strategy_name not in strategy_mapping:
                logger.warning(f"⚠️ Strategy '{strategy_name}' is not recognized. Skipping...")
                continue

            strategy_class = strategy_mapping[strategy_name]
            logger.info(f"Running strategy: {strategy_name}")

            backtest_runner = BacktestRunner(strategy_class, strategy_params, db_handler)

            for symbol in backtesting_symbols:
                for timeframe in timeframes:
                    table_name = symbol_table_mapping.get((symbol, timeframe))
                    if table_name:
                        logger.info(f"Backtesting {symbol} with timeframe {timeframe} using table '{table_name}'")
                        trades, performance = await backtest_runner.run_backtest(
                            symbols=[symbol],
                            start_date=start_time,
                            end_date=end_time,
                            timeframe=timeframe,
                            custom_table_name=table_name
                        )

                        if trades:
                            serializable_trades = []
                            for trade in trades:
                                serializable_trade = {
                                    "symbol": trade["symbol"],
                                    "timestamp": trade["timestamp"].isoformat() if isinstance(trade["timestamp"], pd.Timestamp) else str(trade["timestamp"]),
                                    "action": trade["action"],
                                    "price": trade["price"],
                                    "quantity": trade["quantity"],
                                    "commission": trade["commission"],
                                    "profit": trade["profit"]
                                }
                                serializable_trades.append(serializable_trade)

                            all_backtest_results.append({
                                "strategy": strategy_name,
                                "symbol": symbol,
                                "timeframe": timeframe,
                                "trades": serializable_trades,
                                "performance": performance
                            })
                        else:
                            logger.warning(f"No trades generated for {strategy_name} on {symbol} with timeframe {timeframe}.")
                    else:
                        logger.warning(f"No table mapping found for symbol '{symbol}' and timeframe '{timeframe}'. Skipping.")

    finally:
        await db_handler.close()

    with open("backtest_results.json", "w") as f:
        json.dump(all_backtest_results, f, indent=4)

    logger.info("Backtest results saved to backtest_results.json")

if __name__ == "__main__":
    asyncio.run(run_backtest())