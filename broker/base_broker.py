"""
💡 Key Features
✅ Modular Design: Each broker has a separate implementation file.
✅ Factory Pattern: Dynamically selects and initializes the appropriate broker.
✅ Easily Extendable: Add new brokers without modifying existing logic.
✅ Encapsulation: Each broker class follows a structured interface (BaseBroker).
"""

from abc import ABC, abstractmethod

class BaseBroker(ABC):
    """Abstract base class for all brokers."""

    def __init__(self, **kwargs):
        """
        Initializes broker with dynamic parameters.
        Each broker implementation should handle its own required parameters.
        """
        self.params = kwargs  # Store all parameters as a dictionary

    @abstractmethod
    def get_token(self):
        """Fetch access token"""
        pass

    @abstractmethod
    def get_profile(self):
        pass

    @abstractmethod
    def get_balance(self):
        """Fetch account balance"""
        pass

    @abstractmethod
    def get_holdings(self):
        pass

    @abstractmethod
    def get_order_book(self):
        pass

    @abstractmethod
    def get_positions(self):
        """Fetch open positions"""
        pass

    @abstractmethod
    def trade_book(self):
        pass

    @abstractmethod
    def place_order(self, data):
        """Place an order"""
        pass

    @abstractmethod
    def basket_order(self, data):
        pass

    @abstractmethod
    def modify_order(self, data):
        pass

    @abstractmethod
    def modify_basket_order(self, data):
        pass

    @abstractmethod
    def cancel_order(self, data):
        """Cancel an order"""
        pass

    @abstractmethod
    def cancel_basket_orders(self, data):
        pass

    @abstractmethod
    def exit_position(self, data):
        pass

    @abstractmethod
    def exit_position_by_id(self, data):
        pass

    @abstractmethod
    def pending_order_cancel(self, data):
        pass

    @abstractmethod
    def convert_position(self, data):
        pass

    @abstractmethod
    def history(self):
        pass

    @abstractmethod
    def quotes(self):
        pass

    @abstractmethod
    def market_depth(self):
        pass

    @abstractmethod
    def option_chain(self):
        pass
