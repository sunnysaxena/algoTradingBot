from .base_broker import BaseBroker
from kiteconnect import KiteConnect  # Zerodha API

class ZerodhaBroker(BaseBroker):
    """Implementation for Zerodha API"""

    def __init__(self, api_key, api_secret, access_token):
        super().__init__(api_key, api_secret, access_token)
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)

    def get_balance(self):
        return self.kite.margins()

    def get_positions(self):
        return self.kite.positions()

    def place_order(self, symbol, qty, order_type, side):
        return self.kite.place_order(
            tradingsymbol=symbol,
            quantity=qty,
            exchange="NSE",
            transaction_type=side.upper(),
            order_type=order_type.upper(),
            product="MIS"
        )

    def cancel_order(self, order_id):
        return self.kite.cancel_order(order_id=order_id)
