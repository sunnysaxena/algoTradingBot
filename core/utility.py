import json
import datetime


class Utility:
    """
    A collection of utility functions for common operations.
    """

    @staticmethod
    def load_json(file_path):
        """
        Load a JSON file and return its contents.

        :param file_path: Path to the JSON file.
        :return: Parsed JSON data.
        """
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading JSON file: {e}")
            return None

    @staticmethod
    def save_json(file_path, data):
        """
        Save data to a JSON file.

        :param file_path: Path to the JSON file.
        :param data: Data to be saved.
        """
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"Error saving JSON file: {e}")

    @staticmethod
    def get_current_timestamp():
        """
        Get the current timestamp in a readable format.

        :return: Current timestamp as a string.
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
