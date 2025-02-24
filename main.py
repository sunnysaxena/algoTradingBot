import os
from broker.broker_factory import BrokerFactory

try:
    # Get the absolute path of the credentials.ini file
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.yaml')
    # Load broker dynamically from YAML config
    broker = BrokerFactory.get_broker(config_path)

    # Fetch balance
    print("Balance:", broker.get_balance())

    # Fetch positions
    print("Open Positions:", broker.get_positions())

    # Place an order
    order_response = broker.place_order(symbol="NSE:RELIANCssE-EQ", qty=1, order_type=2, side=1)
    print("Order Response:", order_response)

except Exception as e:
    print(f"Error: {e}")
