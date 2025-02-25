import os
import json
import datetime
from pathlib import Path


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
            with open(file_path, 'w') as fi:
                json.dump(data, fi, indent=4)
        except Exception as e:
            print(f"Error saving JSON file: {e}")

    @staticmethod
    def get_current_timestamp():
        """
        Get the current timestamp in a readable format.

        :return: Current timestamp as a string.
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_access_token(file_name):
        """
        Get the access token from a file with error handling.

        :param file_name: Path to the file containing the access token.
        :return: Access token as a string.
        :raises: Exception if file reading fails.
        """
        try:
            if not os.path.exists(file_name):
                raise FileNotFoundError(f"Error: File '{file_name}' not found.")

            if not os.path.isfile(file_name):
                raise IsADirectoryError(f"Error: '{file_name}' is a directory, not a file.")

            with open(file_name, 'r') as f:
                access_token = f.read().strip()

            if not access_token:
                raise ValueError(f"Error: File '{file_name}' is empty.")

            return access_token

        except FileNotFoundError as e:
            print(e)
        except IsADirectoryError as e:
            print(e)
        except PermissionError:
            print(f"Error: Permission denied while accessing '{file_name}'.")
        except IOError as e:
            print(f"Error: I/O error occurred while reading '{file_name}': {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        return None  # Return None if an error occurs


    @staticmethod
    def get_root_dir():
        """
        Returns the root directory of the project.
        """
        return Path(__file__).resolve().parent.parent  # Get root directory


if __name__ == '__main__':
    token = Utility.get_root_dir()
    print(token)