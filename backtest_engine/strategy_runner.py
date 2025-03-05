import os
import yaml
import logging
import pandas as pd
from dotenv import load_dotenv
from utils.env_loader import load_env
from utils.config_loader import load_config

# Load environment variables
load_dotenv(load_env())
config_yaml = load_config()

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load config
with open(config_yaml, "r") as config_file:
    config = yaml.safe_load(config_file)


class StrategyRunner(object):
    def __init__(self, strategy_class, strategy_params, db_handler):
        """
        Initialize the strategy runner with multiple strategies.
        :param db_handler: DatabaseHandler instance
        :param strategy_classes: List of strategy classes (subclasses of BaseStrategy)
        """
        self.db_handler = db_handler

        # print("DEBUG: strategy_params ->", strategy_params)
        # print("DEBUG: strategy_params type ->", type(strategy_params))

        if not callable(strategy_class):
            raise TypeError(f"🚨 Expected a strategy class but got {type(strategy_class)}")

        # self.strategy = strategy_class(db_handler, strategy_params)  # Instantiate the strategy with params

    async def load_historical_data(self, table=None, start_date=None, end_date=None):
        """
        Load historical data from the database.
        """
        # Fetch historical data
        query = f"SELECT timestamp, open, high, low, close, volume FROM nifty50.nifty50_1d LIMIT 10;"

        return await self.db_handler.execute_query(query)

    async def run_strategies(self, table=None, start_date=None, end_date=None):
        """
        Run all strategies for the given time range.
        """
        # logger.info(f"🚀 Running strategies from {start_time} to {end_time}")

        historical_data = await self.load_historical_data()
        columns = ["timestamp", "open", "high", "low", "close", "volume"]
        df = pd.DataFrame(historical_data, columns=columns)

        # Convert timestamp to datetime if it's not already
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        print(df)

        if not historical_data:
            logger.warning("⚠ No data available for backtesting.")
            return



        # print(self.strategy)
        # logger.info(f"📈 Running {self.strategy.__class__.__name__}")

        # Run the strategy on historical data
        # if hasattr(self.strategy, "run_strategy"):
        #     await self.strategy.run_strategy(df)  # ✅ Use existing method
        # elif hasattr(self.strategy, "apply_strategy"):
        #     await self.strategy.apply_strategy(df)  # ✅ If method name is different
        # else:
        #     raise AttributeError(f"❌ Strategy '{self.strategy.__class__.__name__}' has no valid run method.")

    async def close(self):
        """
        Close database connections.
        """
        await self.db_handler.close_all()