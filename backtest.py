import os
import yaml
import asyncio
import logging
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

# Load environment variables
load_dotenv(load_env())
config_yaml = load_config()

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load Config
with open(config_yaml, "r") as file:
    config = yaml.safe_load(file)

# Strategy Mapping (String -> Actual Class)
strategy_mapping = {
    "EMA_CrossoverStrategy": EMA_CrossoverStrategy,
    "EMA_RSI_CrossoverStrategy": EMA_RSI_CrossoverStrategy,
    "MACD_CrossoverStrategy": MACD_CrossoverStrategy,
    "RSI_CrossoverStrategy": RSI_CrossoverStrategy,
    "RSI_MACD_CrossoverStrategy": RSI_MACD_CrossoverStrategy,
    # "StraddleStrangleStrategy": StraddleStrangleStrategy,
    # "BreakoutStrategy": BreakoutStrategy
}

db_type = config.get("database", {}).get("type", "timescaledb")  # Get database type from config
db_config = config.get("database", {}).get(db_type, {})
start_time = config["backtesting"]["start_date"]
end_time = config["backtesting"]["end_date"]

# Assuming `config` is loaded from YAML
active_strategy = config["trading"].get("active_strategy", None)
strategies = config["trading"].get("strategies", {})

# Ensure active strategy exists
if not active_strategy or active_strategy not in strategies:
    raise ValueError(f"⚠️ Active strategy '{active_strategy}' not found in configuration.")

# Load strategy parameters
strategy_params = strategies[active_strategy]

if not isinstance(strategy_params, dict):
    raise TypeError(f"🚨 Expected 'strategy_params' to be a dictionary but got {type(strategy_params)}")

strategy_name = strategy_params.get("name", active_strategy)  # Default to active strategy name
db_handler = DatabaseHandler(db_config)

# Get the list of symbols to backtest from the config
backtesting_symbols = config["backtesting"].get("symbols", ["NIFTY50", "SENSEX"])
timeframes = config["backtesting"].get("timeframes", ["1m", "1d"])

# Create a mapping of symbol to table name based on timeframe
symbol_table_mapping = {
    ("NIFTY50", "1m"): "nifty50_1m",
    # ("NIFTY50", "1d"): "nifty50_1d",
    # ("SENSEX", "1m"): "sensex_1m",
    # ("SENSEX", "1d"): "sensex_1d",
}

async def run_backtest():
    """Run backtest on historical data."""
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
                        await backtest_runner.run_backtest(
                            symbols=[symbol],  # Pass a list with a single symbol
                            start_date=start_time,
                            end_date=end_time,
                            timeframe=timeframe,
                            custom_table_name=table_name  # Pass the specific table name
                        )
                    else:
                        logger.warning(f"No table mapping found for symbol '{symbol}' and timeframe '{timeframe}'. Skipping.")

    finally:
        await db_handler.close()


if __name__ == "__main__":
    asyncio.run(run_backtest())