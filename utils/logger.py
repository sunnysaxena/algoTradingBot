import logging
import os
from logging.handlers import RotatingFileHandler
from utils.config_loader import load_config

# Load config
config = load_config()
log_config = config.get("logging", {})

# Extract values
LOG_DIR = log_config.get("log_dir", "logs")
LOG_FILE = log_config.get("log_file", "algo_trading.log")
ERROR_LOG_FILE = log_config.get("error_log_file", "errors.log")

# Create log directory if not exists
os.makedirs(LOG_DIR, exist_ok=True)

# Log file paths
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)
ERROR_LOG_PATH = os.path.join(LOG_DIR, ERROR_LOG_FILE)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    handlers=[
        RotatingFileHandler(LOG_PATH, maxBytes=5*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

# Error log handler
error_handler = RotatingFileHandler(ERROR_LOG_PATH, maxBytes=5*1024*1024, backupCount=5)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s"))

# Get logger instance
def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.addHandler(error_handler)  # Attach error log handler
    return logger

# Example usage
if __name__ == "__main__":
    logger = get_logger("TestLogger")
    logger.info("Logging setup complete.")
    logger.error("This is an error message.")
