from .base_broker import BaseBroker
from fyers_apiv3 import fyersModel
from fyers_apiv3.fyersModel import FyersModel


class FyersBroker(BaseBroker):
    """Implementation for Fyers API"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Extract required parameters
        self.client_id = kwargs.get("client_id")
        self.access_token = kwargs.get("access_token")
        self.log_dir = kwargs.get("log_dir")

        # Initialize Fyers client
        self.client = FyersModel(client_id=self.client_id, token=self.access_token,
                                 log_path=self.log_dir, is_async=False)

    def get_token(self):
        return self.client.token

    def get_profile(self):
        return self.client.get_profile()

    def get_balance(self):
        return self.client.funds()

    def get_holdings(self):
        return self.get_holdings()

    def get_order_book(self):
        return self.client.orderbook()

    def get_positions(self):
        return self.client.positions()

    def trade_book(self):
        return self.client.tradebook()

    def place_order(self, data):
        return self.client.place_order(data)

    def basket_order(self, data):
        return self.client.place_basket_orders(data)

    def modify_order(self, data):
        return self.client.modify_order(data)

    def modify_basket_order(self, data):
        return self.client.modify_basket_orders(data)

    def cancel_order(self, data):
        return self.client.place_basket_orders(data)

    def cancel_basket_orders(self, data):
        return self.client.place_basket_orders(data)

    def exit_position(self, data):
        return self.client.place_basket_orders(data)

    def exit_position_by_id(self, data):
        return self.client.place_basket_orders(data)

    def pending_order_cancel(self, data):
        return self.client

    def convert_position(self, data):
        return self.client.convert_position(data)

    def history(self):
        return self.client.history()

    def quotes(self):
        return self.client.quotes()

    def market_depth(self):
        return self.client.depth()

    def option_chain(self):
        return self.client.optionchain()
