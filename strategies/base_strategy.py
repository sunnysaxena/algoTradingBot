from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.

    This class defines the structure for any trading strategy, enforcing the implementation
    of signal generation and trade execution methods. It also includes basic risk management
    and position tracking functionalities.
    """

    def __init__(self, config, broker, data_source):
        """
        Initialize the strategy with configuration, broker API, and data source.

        :param config: Dict containing strategy configuration.
        :param broker: Broker API interface for executing trades.
        :param data_source: Data source for fetching market data.
        """
        self.config = config
        self.broker = broker
        self.data_source = data_source
        self.positions = []  # Track open positions

    @abstractmethod
    def generate_signal(self, market_data):
        """
        Generate buy/sell/hold signals based on market data.

        :param market_data: Market data (OHLC, indicators, etc.).
        :return: Signal ('BUY', 'SELL', or 'HOLD').
        """
        pass

    @abstractmethod
    def execute_trade(self, signal, symbol):
        """
        Execute trade based on the generated signal.

        :param signal: The trade signal ('BUY', 'SELL').
        :param symbol: The trading symbol.
        """
        pass

    def risk_management(self, position):
        """
        Apply stop-loss and take-profit rules to manage risk.

        This method checks if the position has hit stop-loss or take-profit thresholds
        and executes a trade accordingly.

        :param position: The current open position.
        """
        stop_loss = self.config["trading"]["risk_management"]["stop_loss"]
        take_profit = self.config["trading"]["risk_management"]["take_profit"]

        # Example risk management logic (to be customized)
        if position["profit_pct"] <= -stop_loss:
            self.execute_trade("SELL", position["symbol"])
        elif position["profit_pct"] >= take_profit:
            self.execute_trade("SELL", position["symbol"])

    def update_positions(self, new_positions):
        """
        Update the list of current positions.

        This method updates the strategy's internal record of open positions
        based on the latest market data and executed trades.

        :param new_positions: List of updated positions.
        """
        self.positions = new_positions
