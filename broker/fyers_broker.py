import os
import logging
from core.utility import Utility
from .base_broker import BaseBroker
from fyers_apiv3.fyersModel import FyersModel


class FyersBroker(BaseBroker):
    """Implementation for Fyers API"""

    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)

            # Extract required parameters
            self.client_id = kwargs.get("client_id")
            self.access_token = kwargs.get("access_token")
            self.log_dir = kwargs.get("log_dir")

            # Ensure required parameters are present
            if not self.client_id or not self.access_token:
                raise ValueError("Error: Missing required parameters 'client_id' or 'access_token'.")

            # Validate log directory
            if self.log_dir and not os.path.isdir(self.log_dir):
                raise ValueError(f"Error: Invalid log directory '{self.log_dir}'.")

            # Fetch and validate access token
            token = Utility.get_access_token(self.access_token)
            if not token:
                raise ValueError("Error: Failed to retrieve access token.")

            # Initialize Fyers client
            self.client = FyersModel(client_id=self.client_id, token=token, log_path=self.log_dir, is_async=False)
        except ValueError as ve:
            logging.error(f"ValueError: {ve}")
            raise ve
        except Exception as e:
            logging.critical(f"Critical Error during FyersBroker initialization: {e}")
            raise RuntimeError(f"FyersBroker initialization failed: {e}")

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

    def history(self, data):
        return self.client.history(data)

    def quotes(self, data):
        return self.client.quotes(data)

    def market_depth(self, data):
        return self.client.depth(data)

    def option_chain(self, data):
        return self.client.optionchain(data)
