import os
from dotenv import load_dotenv


def load_env():
    """Load and resolve paths in the .env configuration file."""

    # Get the absolute path of the config directory
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get current script's directory
    config_path = os.path.join(script_dir, "../config/.env")  # Adjust path to config.yaml

    # Ensure the path is normalized
    config_path = os.path.normpath(config_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Environment variable file not found: {config_path}")
    return config_path


# Example usage
if __name__ == "__main__":
    env = load_dotenv(load_env())
    print("Env Config:", env)  # Verify resolved paths
