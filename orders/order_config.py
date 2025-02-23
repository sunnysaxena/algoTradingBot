import yaml


class OrderConfig:
    """Loads order-related parameters from the YAML configuration file."""

    def __init__(self, config_path="config.yml"):
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def get_lot_size(self, index_name):
        """Fetch lot size dynamically based on index name."""
        return self.config["orders"]["lot_sizes"].get(index_name.upper(), 1)  # Default to 1 if not found

    def get_order_type(self, order_type):
        """Fetch order type ID (e.g., LIMIT -> 1, MARKET -> 2)."""
        return self.config["orders"]["types"].get(order_type.lower())

    def get_product_type(self, product):
        """Fetch product type (e.g., INTRADAY, MARGIN, CO, BO)."""
        return self.config["orders"]["product_types"].get(product.lower())


# Example Usage
if __name__ == "__main__":
    config = OrderConfig()
    print(f"NIFTY Lot Size: {config.get_lot_size('NIFTY')}")  # Output: 50
    print(f"Market Order Type: {config.get_order_type('market')}")  # Output: 2
