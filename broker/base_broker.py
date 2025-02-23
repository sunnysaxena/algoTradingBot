from abc import ABC, abstractmethod

class BaseBroker(ABC):
    """Abstract base class for all brokers."""

    def __init__(self, api_key, api_secret, access_token):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token

    @abstractmethod
    def get_balance(self):
        """Fetch account balance"""
        pass

    @abstractmethod
    def get_positions(self):
        """Fetch open positions"""
        pass

    @abstractmethod
    def place_order(self, symbol, qty, order_type, side):
        """Place an order"""
        pass

    @abstractmethod
    def cancel_order(self, order_id):
        """Cancel an order"""
        pass
