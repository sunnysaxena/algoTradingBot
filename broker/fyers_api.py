from core.config_loader import config

# Access broker API details from config.yaml
BROKER_API_KEY = config["broker"]["api_key"]
BROKER_SECRET = config["broker"]["api_secret"]
ACCESS_TOKEN = config["broker"]["access_token"]


def connect_to_broker():
    """Example function to connect to broker using API credentials."""
    print(f"Connecting to broker with API key: {BROKER_API_KEY}")
    # Add API connection logic here
