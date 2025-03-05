import asyncio
import logging
from database.handler import DatabaseHandler
from utils.config_loader import load_config
from backtest_engine.strategy_runner import StrategyRunner

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class BacktestRunner(object):
    def __init__(self, strategy_class, strategy_params, db_handler):
        """
        Initialize the backtest runner.
        """
        self.strategy_class = strategy_class
        self.strategy_params = strategy_params
        self.db_handler = db_handler
        self.strategy_runner = StrategyRunner(self.strategy_class, self.strategy_params, self.db_handler)

    async def run_backtest(self, table=None, start_date=None, end_date=None):
        """
        Run backtesting on the given symbol and date range.
        """
        await self.strategy_runner.run_strategies()

        logger.info("Backtest completed.")




# Example Usage
if __name__ == "__main__":
    async def main():
        pass

    asyncio.run(main())
