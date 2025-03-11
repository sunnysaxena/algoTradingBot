"""
# Entry point for live trading
"""

from broker.broker_factory import BrokerFactory

try:
    broker = BrokerFactory.get_broker()
    print(f"Successfully initialized broker: {broker.__class__.__name__}")

    # Example usage:
    # List all methods associated with the broker object
    methods = [method for method in dir(broker) if
               callable(getattr(broker, method)) and not method.startswith("__")]
    print("Available methods:", methods)

except Exception as e:
    print(f"Error initializing broker: {e}")
