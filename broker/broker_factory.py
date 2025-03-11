"""
4️⃣ Registering a New Broker
    If you want to add a new broker, you can register it dynamically.

Example: Register a New Broker

from broker.broker_factory import BrokerFactory
from my_custom_broker import MyCustomBroker  # Import your new broker class

# Register new broker
BrokerFactory.register_broker("custom", MyCustomBroker)

# Get broker instance
broker = BrokerFactory.get_broker()
print(broker)

"""


import os
import time
import yaml
import logging

from dotenv import load_dotenv

from core.utility import Utility
from .fyers_broker import FyersBroker
from .zerodha_broker import ZerodhaBroker

from utils.env_loader import load_env
from utils.config_loader import load_config

# Load environment variables
_config_path = load_config()

# Configure Logging
logging.basicConfig(
    filename="broker_factory.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# _config_path = os.path.join(Utility.get_root_dir(), "config/config.yaml")
# _env_path = os.path.join(Utility.get_root_dir(), "config/.env")


class BrokerFactory:
    """Factory class for dynamically selecting and initializing brokers with YAML config and .env credentials."""

    _brokers = {
        "fyers": FyersBroker,
        "zerodha": ZerodhaBroker
    }

    @classmethod
    def register_broker(cls, name, broker_class):
        """Register a new broker dynamically."""
        cls._brokers[name.lower()] = broker_class
        logging.info(f"Broker '{name}' registered successfully.")

    @classmethod
    def get_broker(cls, retries=3):
        """Loads broker from config.yml, fetches credentials from .env, and initializes the broker."""
        try:
            # Load broker from config.yml
            with open(_config_path, "r") as file:
                config = yaml.safe_load(file)

            broker_name = config.get("broker", "").lower()
            if broker_name not in cls._brokers:
                logging.error(f"Unsupported broker requested: {broker_name}")
                raise ValueError(f"Unsupported broker: {broker_name}")

            # Load .env file
            load_dotenv(load_env())

            # Fetch broker credentials dynamically from environment variables
            credentials = {
                "client_id": os.getenv(f"{broker_name.upper()}_CLIENT_ID"),
                "access_token": os.path.join(Utility.get_root_dir(), os.getenv(f"{broker_name.upper()}_ACCESS_TOKEN")),
                "log_dir": os.getenv(f"{broker_name.upper()}_LOG_DIR"),
            }

            # Ensure all required credentials are available
            if None in credentials.values():
                missing = [k for k, v in credentials.items() if v is None]
                logging.error(f"Missing credentials: {missing} for broker {broker_name}")
                raise ValueError(f"Missing credentials: {missing}")

            # Attempt initialization with retry mechanism
            for attempt in range(1, retries + 1):
                try:
                    logging.info(f"Initializing broker: {broker_name} (Attempt {attempt})")
                    return cls._brokers[broker_name](**credentials)

                except Exception as e:
                    logging.error(f"Error initializing broker '{broker_name}': {e}")
                    if attempt < retries:
                        logging.info(f"Retrying in 2 seconds... (Attempt {attempt + 1})")
                        time.sleep(2)
                    else:
                        logging.critical(f"Failed to initialize broker '{broker_name}' after {retries} attempts.")
                        raise e

        except Exception as e:
            logging.critical(f"Failed to load broker configuration: {e}")
            raise e


if __name__ == '__main__':
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