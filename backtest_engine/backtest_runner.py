from backtest_engine.strategy_runner import StrategyRunner
from backtest_engine.performance_analyzer import PerformanceAnalyzer
from utils.logger import get_logger  # Import get_logger

logger = get_logger(__name__)  # Get logger for this module

class BacktestRunner:
    """
    Orchestrates the backtesting process for a given trading strategy.
    """
    def __init__(self, strategy_class, strategy_params, db_handler):
        """
        Initializes the BacktestRunner.
        """
        self.strategy_class = strategy_class
        self.strategy_params = strategy_params
        self.db_handler = db_handler
        self.performance_analyzer = None
        self.trades = []

    async def run_backtest(self, symbols=None, start_date=None, end_date=None, timeframe='1m', custom_table_name=None):
        """
        Runs the backtest for the specified strategy on the given symbols and date range.
        """
        if symbols is None:
            symbols = ["NIFTY50"]
            logger.info(f"No symbols provided, using default: {symbols}")

        backtest_config = self.db_handler.config.get("backtesting", {})
        start_date = start_date or backtest_config.get("start_date")
        end_date = end_date or backtest_config.get("end_date")
        slippage = backtest_config.get("slippage", 0.0)
        commission = backtest_config.get("commission", 0.0)
        initial_capital = backtest_config.get("initial_capital", 1000000)

        if not start_date or not end_date:
            logger.error("Start and end dates for backtesting are not configured.")
            return [], {}  # Return empty lists/dicts instead of None

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

        return all_trades, all_performance  # Always return a tuple