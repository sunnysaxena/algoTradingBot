from .base_broker import BaseBroker
from kiteconnect import KiteConnect  # Zerodha API


class ZerodhaBroker(BaseBroker):
    """Implementation for Fyers API"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Extract required parameters
        self.client_id = kwargs.get("client_id")
        self.access_token = kwargs.get("access_token")
        self.log_dir = kwargs.get("log_dir")

        # Initialize Fyers client
        self.client = KiteConnect(api_key=self.client_id)

    def get_token(self):
        return self.client.access_token

    def get_profile(self):
        return self.client.profile()

    def get_balance(self):
        pass

    def get_holdings(self):
        return self.get_holdings()

    def get_order_book(self):
        pass

    def get_positions(self):
        pass

    def trade_book(self):
        pass

    def place_order(self, data):
        pass

    def basket_order(self, data):
        pass

    def modify_order(self, data):
        pass

    def modify_basket_order(self, data):
        pass

    def cancel_order(self, data):
        pass

    def cancel_basket_orders(self, data):
        pass

    def exit_position(self, data):
        pass

    def exit_position_by_id(self, data):
        pass

    def pending_order_cancel(self, data):
        pass

    def convert_position(self, data):
        pass

    def history(self):
        pass

    def quotes(self):
        pass

    def market_depth(self):
        pass

    def option_chain(self):
        pass
