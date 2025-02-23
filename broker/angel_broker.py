from .base_broker import BaseBroker
from SmartApi import SmartConnect  # AngelOne API

class AngelBroker(BaseBroker):
    """Implementation for AngelOne API"""

    def __init__(self, api_key, api_secret, access_token):
        super().__init__(api_key, api_secret, access_token)
        self.client = SmartConnect(api_key=api_key)
        self.client.generateSession(clientCode=api_key, password=api_secret, totp=access_token)

    def get_balance(self):
        return self.client.rmsLimit()

    def get_positions(self):
        return self.client.position()

    def place_order(self, symbol, qty, order_type, side):
        order_data = {
            "tradingsymbol": symbol,
            "quantity": qty,
            "transactiontype": side.upper(),
            "exchange": "NSE",
            "ordertype": order_type.upper(),
            "producttype": "INTRADAY"
        }
        return self.client.placeOrder(order_data)

    def cancel_order(self, order_id):
        return self.client.cancelOrder(order_id=order_id)
