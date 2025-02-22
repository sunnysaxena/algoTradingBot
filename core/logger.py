import os
import yaml
import logging
import logging.config

def setup_logging():
    """Loads logging configuration from YAML file."""
    log_config_path = os.path.join(os.path.dirname(__file__), "../config/logging_config.yaml")
    log_config_path = os.path.abspath(log_config_path)  # Convert to absolute path

    if not os.path.exists(log_config_path):
        raise FileNotFoundError(f"Logging configuration file not found: {log_config_path}")

    with open(log_config_path, "r") as file:
        config = yaml.safe_load(file)
        logging.config.dictConfig(config)


if __name__ == "__main__":
    # Initialize logging
    setup_logging()

    # Create a logger instance
    logger = logging.getLogger("trading_bot")

    # Example usage
    logger.info("Logger setup complete.")
    logger.debug("This is a debug message.")
    logger.error("An error occurred.")
    logger.warning("Warning: Check the configuration.")
