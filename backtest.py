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
from backtest_engine.performance_analyzer import PerformanceAnalyzer

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
    "StraddleStrangleStrategy": StraddleStrangleStrategy,
    "BreakoutStrategy": BreakoutStrategy
}

db_type = "timescaledb"  # Change to "timescaledb" or "influxdb" as needed
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

# print(f"🚨 'Database Type' : {db_type}")
# print(f"🚨 'Database Config (Tables)' : {db_config}")
# print(f"🚨 'Active Strategy' : {active_strategy}")
# print(f"🚨 'Strategies' : {strategies}")
# print(f"🚨 'Strategy Name' : {strategy_name}")
# print(f"🚨 'Strategy Params' : {strategy_params}")
# print(f"🚨 'Database Handler' : {db_handler}")

async def run_backtest():
    """Run backtest on historical data."""
    try:
        for strategy_name, strategy_params in strategies.items():  # ✅ Iterate over name (string) and parameters (dict)
            if strategy_name not in strategy_mapping:
                logger.warning(f"⚠️ Strategy '{strategy_name}' is not recognized. Skipping...")
                continue

            strategy_class = strategy_mapping[strategy_name]  # Get actual class
            logger.info(f"Running strategy: {strategy_name}")

            backtest_runner = BacktestRunner(strategy_class, strategy_params, db_handler)
            await backtest_runner.run_backtest()

            #
            # strategy_runner = StrategyRunner(strategy_class, strategy_params, db_handler)
            #
            # trades, performance = await strategy_runner.run(start_time, end_time)
            #
            # analyzer = PerformanceAnalyzer(trades, performance)
            # results = analyzer.analyze()
            # logger.info(f"Performance Results for {strategy_name}: {results}")

    finally:
        db_handler.close_all()


if __name__ == "__main__":
    asyncio.run(run_backtest())
