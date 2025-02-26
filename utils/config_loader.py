import yaml
import os


def load_config():
    """Load and resolve paths in the YAML configuration file."""

    # Get the absolute path of the config directory
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get current script's directory
    config_path = os.path.join(script_dir, "../config/config.yaml")  # Adjust path to config.yaml

    # Ensure the path is normalized
    config_path = os.path.normpath(config_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    # Resolve root_dir
    root_dir = config.get("general", {}).get("root_dir", os.getcwd())  # Default to current directory

    # Replace ${root_dir} placeholders in config
    def resolve_paths(obj):
        if isinstance(obj, dict):
            return {k: resolve_paths(v) for k, v in obj.items()}
        elif isinstance(obj, str) and "${root_dir}" in obj:
            return obj.replace("${root_dir}", root_dir)
        return obj

    return resolve_paths(config)


# Example usage
if __name__ == "__main__":
    config = load_config()
    print("Loaded Config:", config)  # Verify resolved paths
