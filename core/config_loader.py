import yaml
import os


def load_config():
    """Loads configuration from the YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), "../config/config.yaml")
    config_path = os.path.abspath(config_path)  # Convert to absolute path

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config


# Load config
config = load_config()

if __name__ == "__main__":
    print("Config loaded successfully!")
    print(config)  # Debug: Print loaded config
