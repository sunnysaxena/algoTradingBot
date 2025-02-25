from broker.broker_factory import BrokerFactory

try:
    # Initialize broker dynamically from YAML and .env
    broker = BrokerFactory.get_broker()

    # Fetch balance
    print("Balance:", broker.get_balance())

    # Fetch positions
    print("Open Positions:", broker.get_positions()['netPositions'])

except Exception as e:
    print(f"Error: {e}")
