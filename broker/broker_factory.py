from .fyers_broker import FyersBroker
from .zerodha_broker import ZerodhaBroker
from .angel_broker import AngelBroker

class BrokerFactory:
    """Factory to instantiate brokers dynamically"""

    brokers = {
        "fyers": FyersBroker,
        "zerodha": ZerodhaBroker,
        "angel": AngelBroker
    }

    @staticmethod
    def get_broker(broker_name, api_key, api_secret, access_token):
        broker_class = BrokerFactory.brokers.get(broker_name.lower())
        if not broker_class:
            raise ValueError(f"Unsupported broker: {broker_name}")
        return broker_class(api_key, api_secret, access_token)
