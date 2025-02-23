from order_config import OrderConfig

class OrderExecution:
    """Handles order placement based on configuration settings."""

    def __init__(self):
        self.config = OrderConfig()

    def place_order(self, symbol, index_name, order_type, side, product_type, price=None, quantity=None):
        """Places an order dynamically based on configuration settings."""
        order_data = {
            "symbol": symbol,
            "order_type": self.config.get_order_type(order_type),
            "side": self.config.get_order_type(side),
            "product_type": self.config.get_product_type(product_type),
            "quantity": quantity or self.config.get_lot_size(index_name),  # Use default lot size if not provided
            "price": price if order_type.lower() == "limit" else "MARKET",
        }
        print(f"Placing order: {order_data}")  # Replace with actual API call to broker

# Example Usage
if __name__ == "__main__":
    executor = OrderExecution()
    executor.place_order("NIFTY24FEB", "NIFTY", "market", "buy", "intraday")
