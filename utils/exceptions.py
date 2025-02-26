class TradingBotError(Exception):
    """Base class for all trading bot exceptions."""
    pass

class APIConnectionError(TradingBotError):
    """Raised when there's an issue connecting to an API."""
    pass

class DatabaseError(TradingBotError):
    """Raised when there's a database operation failure."""
    pass

class InvalidOrderError(TradingBotError):
    """Raised for invalid order placement requests."""
    pass

class RiskManagementError(TradingBotError):
    """Raised when risk management rules are violated."""
    pass

class DataIngestionError(TradingBotError):
    """Raised when there's an issue ingesting market data."""
    pass

class StrategyExecutionError(TradingBotError):
    """Raised when a trading strategy encounters an issue."""
    pass

def handle_exception(exc):
    """Logs exceptions and prevents crashes."""
    import logging
    logger = logging.getLogger("TradingBot")
    logger.error(f"Error occurred: {str(exc)}")
