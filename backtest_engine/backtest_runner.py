import asyncio
import logging
import pandas as pd
from backtest_engine.strategy_runner import StrategyRunner
from backtest_engine.performance_analyzer import PerformanceAnalyzer

logger = logging.getLogger(__name__)

class BacktestRunner:
    """
    Orchestrates the backtesting process for a given trading strategy.
    """
    def __init__(self, strategy_class, strategy_params, db_handler):
        """
        Initializes the BacktestRunner.

        Args:
            strategy_class (type): The class of the trading strategy to backtest.
            strategy_params (dict): Parameters for initializing the strategy.
            db_handler (DatabaseHandler): An instance of the database handler.
        """
        self.strategy_class = strategy_class
        self.strategy_params = strategy_params
        self.db_handler = db_handler
        self.performance_analyzer = None
        self.trades = []

    async def run_backtest(self, symbols=None, start_date=None, end_date=None, timeframe='1m', custom_table_name=None):
        """
        Runs the backtest for the specified strategy on the given symbols and date range.

        Args:
            symbols (list, optional): A list of trading symbols to backtest. If None, will use a default.
            start_date (str, optional): The start date for the backtest. If None, will use a default.
            end_date (str, optional): The end date for the backtest. If None, will use a default.
            timeframe (str, optional): The timeframe for the historical data. Defaults to '1m'.
            custom_table_name (str, optional): The specific table name to use for fetching data.
        """
        if symbols is None:
            # You might want to load default symbols from your config
            symbols = ["NSE:NIFTY50-INDEX"]
            logger.info(f"No symbols provided, using default: {symbols}")

        # Load backtesting specific configurations
        backtest_config = self.db_handler.config.get("backtesting", {})
        start_date = start_date or backtest_config.get("start_date")
        end_date = end_date or backtest_config.get("end_date")
        slippage = backtest_config.get("slippage", 0.0)
        commission = backtest_config.get("commission", 0.0)
        initial_capital = backtest_config.get("initial_capital", 1000000) # Get initial capital

        if not start_date or not end_date:
            logger.error("Start and end dates for backtesting are not configured.")
            return

        all_trades = []
        all_performance = {}

        for symbol in symbols:
            logger.info(f"Backtesting strategy '{self.strategy_class.__name__}' on {symbol} from {start_date} to {end_date} ({timeframe})...")

            strategy_runner = StrategyRunner(self.strategy_class, self.strategy_params, self.db_handler, initial_capital=initial_capital)
            trades, performance = await strategy_runner.run(symbol, start_date, end_date, timeframe, slippage, commission, custom_table_name=custom_table_name)

            if trades:
                all_trades.extend(trades)
                all_performance[symbol] = performance
                logger.info(f"Completed backtest for {symbol}. Total trades: {len(trades)}")
            else:
                logger.warning(f"No trades generated for {self.strategy_class.__name__} on {symbol}.")

        if all_trades:
            self.trades = all_trades
            self.performance_analyzer = PerformanceAnalyzer(self.trades)
            overall_performance = self.performance_analyzer.analyze()
            logger.info(f"Overall Backtesting Performance for '{self.strategy_class.__name__}':\n{overall_performance}")
            for symbol, perf in all_performance.items():
                logger.info(f"Performance for {symbol}:\n{perf}")
        else:
            logger.info("No trades were generated during the backtest.")