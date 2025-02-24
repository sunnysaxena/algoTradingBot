import logging
import time
import yaml
from .fyers_broker import FyersBroker
from .zerodha_broker import ZerodhaBroker

# Configure Logging
logging.basicConfig(
    filename="broker_factory.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class BrokerFactory:
    """Factory class for dynamically selecting and initializing brokers using YAML config."""

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
    def get_broker(cls, config_path="config.yml", retries=3):
        """Loads the broker from YAML file and initializes it with error handling & retries."""
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            broker_name = config.get("broker", "").lower()
            if broker_name not in cls._brokers:
                logging.error(f"Unsupported broker requested: {broker_name}")
                raise ValueError(f"Unsupported broker: {broker_name}")

            broker_params = config.get(broker_name, {})

            for attempt in range(1, retries + 1):
                try:
                    logging.info(f"Initializing broker: {broker_name} (Attempt {attempt})")
                    return cls._brokers[broker_name](**broker_params)

                except Exception as e:
                    logging.error(f"Error initializing broker '{broker_name}': {e}")
                    if attempt < retries:
                        logging.info(f"Retrying in 2 seconds... (Attempt {attempt + 1})")
                        time.sleep(2)
                    else:
                        logging.critical(f"Failed to initialize broker '{broker_name}' after {retries} attempts.")
                        raise e

        except Exception as e:
            logging.critical(f"Failed to load broker from YAML: {e}")
            raise e
