from .base_broker import BaseBroker
import fyers_apiv3  # Import Fyers API

class FyersBroker(BaseBroker):
    """Implementation for Fyers API"""

    def __init__(self, api_key, api_secret, access_token):
        super().__init__(api_key, api_secret, access_token)
        self.client = fyers_apiv3.FyersModel(client_id=api_key, token=access_token)

    def get_balance(self):
        return self.client.funds()

    def get_positions(self):
        return self.client.positions()

    def place_order(self, symbol, qty, order_type, side):
        order_data = {
            "symbol": symbol,
            "qty": qty,
            "type": order_type,
            "side": side,
            "productType": "INTRADAY"
        }
        return self.client.place_order(data=order_data)

    def cancel_order(self, order_id):
        return self.client.cancel_order(order_id=order_id)
