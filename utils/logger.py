import os
import logging
import colorlog
import yaml

from utils.config_loader import load_config

config_yaml = load_config()

# Load Config
with open(config_yaml, "r") as file:
    config = yaml.safe_load(file)

log_config = config.get("logging", {})

# Extract values
root_dir = config.get("general", {}).get("root_dir", ".")  # Get root_dir
log_dir_template = log_config.get("log_dir", "logs")

# Perform variable substitution
LOG_DIR = log_dir_template.replace("${root_dir}", root_dir)

def setup_logging(log_level=logging.INFO):
    """Sets up colored logging and file logging."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Console Handler
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s' + log_format,
        datefmt=date_format,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)

    # Add console handler to root logger
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().setLevel(log_level)


def get_logger(name):
    """Returns a logger with the specified name and file handler."""
    logger = logging.getLogger(name)
    logger.propagate = False  # Prevent duplicate logs

    # Check if a file handler already exists for this logger
    file_handler_exists = any(
        isinstance(handler, logging.FileHandler) and handler.baseFilename.endswith(f"{name}.log")
        for handler in logger.handlers
    )

    if not file_handler_exists:
        log_file = os.path.join(LOG_DIR, f"{name}.log")
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
