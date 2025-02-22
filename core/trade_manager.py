class TradeManager:
    """
    Handles trade execution and order management.
    """

    def __init__(self, broker_api):
        """
        Initialize trade manager with broker API instance.

        :param broker_api: Broker API client for executing trades.
        """
        self.broker_api = broker_api

    def place_order(self, symbol, quantity, order_type, price=None):
        """
        Place a new trade order.

        :param symbol: Trading symbol.
        :param quantity: Number of shares/contracts.
        :param order_type: Order type ('market', 'limit').
        :param price: Limit price (if applicable).
        :return: Order response from the broker API.
        """
        order_data = {
            "symbol": symbol,
            "quantity": quantity,
            "order_type": order_type,
            "price": price
        }
        return self.broker_api.place_order(order_data)

    def cancel_order(self, order_id):
        """
        Cancel an existing order.

        :param order_id: ID of the order to cancel.
        :return: Response from the broker API.
        """
        return self.broker_api.cancel_order(order_id)

    def get_order_status(self, order_id):
        """
        Retrieve the status of an order.

        :param order_id: ID of the order.
        :return: Order status details.
        """
        return self.broker_api.get_order_status(order_id)
