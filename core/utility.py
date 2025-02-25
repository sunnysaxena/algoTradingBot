import os
import json
import datetime
import logging
from typing import Any

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    filename="utility.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Cache for API responses
cache = {}
cache_expiry = timedelta(minutes=5)  # Expire cache after 5 minutes

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

    @staticmethod
    def today_date():
        return datetime.today().strftime("%Y-%m-%d")

    @staticmethod
    def get_timestamp(start_time: str = "09:15:00", end_time: str = None) -> tuple[int, int]:
        """
        Convert start and end time to epoch timestamps.

        :param start_time: Start time in HH:MM:SS format (default 09:15:00).
        :param end_time: End time in HH:MM:SS format. Defaults to current time.
        :return: Tuple of (start_epoch_time, end_epoch_time).
        """
        today_date = datetime.now().strftime("%Y-%m-%d")

        try:
            start_string = f"{today_date} {start_time}"
            start_epoch = int(datetime.strptime(start_string, "%Y-%m-%d %H:%M:%S").timestamp())

            if end_time:
                end_string = f"{today_date} {end_time}"
            else:
                end_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            end_epoch = int(datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S").timestamp())

            logging.info(f"Start Epoch Time: {start_epoch}, End Epoch Time: {end_epoch}")
            return start_epoch, end_epoch

        except Exception as e:
            logging.error(f"Error converting time to epoch: {e}")
            return 0, 0  # Return default values in case of error

    @staticmethod
    def get_todays_data(symbol: str, time_interval: str = "5",
                        start_time: str = "09:15:00", end_time: str = None,
                        client: Any = None) -> pd.DataFrame:
        """
        Fetch today's OHLC data for a given symbol from Fyers.

        :param client: Broker Object
        :param symbol: Stock symbol.
        :param time_interval: Time interval for candlestick data (default "5" min).
        :param start_time: Market start time.
        :param end_time: Market end time or current time.
        :return: Pandas DataFrame with OHLC data.
        """
        global cache
        cache_key = (symbol, time_interval, start_time, end_time)
        current_time = datetime.now()

        # Return cached data if not expired
        if cache_key in cache:
            cached_data, timestamp = cache[cache_key]
            if current_time - timestamp < cache_expiry:
                logging.info("Returning cached data.")
                return cached_data

        try:
            range_from, range_to = Utility.get_timestamp(start_time, end_time)
            data = {
                "symbol": symbol,
                "resolution": time_interval,
                "date_format": "0",
                "range_from": range_from,
                "range_to": range_to,
                "cont_flag": "1"
            }

            print(data)

            response = client.history(data=data)
            print(response)
            if 'candles' not in response:
                raise ValueError("Response does not contain 'candles' key")

            df = pd.DataFrame(response['candles'], columns=["epoch", "open", "high", "low", "close", "volume"])
            df['timestamp'] = pd.to_datetime(df['epoch'], unit='s', utc=True).dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df['volume'] = df['volume'].fillna(0)
            df.drop_duplicates(inplace=True)

            # Store in cache
            cache[cache_key] = (df, current_time)
            logging.info(f"Data fetched successfully for {symbol}.")
            return df

        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error

    def strike_price_to_symbol(symbol=None, client=None):
        """
        Fetch the low price of the given symbol from the Fyers API.

        Args:
            symbol (str): The symbol for which to fetch the low price. Default is 'BSE:SENSEX2521179400CE'.

        Returns:
            float: The low price of the symbol, or None if an error occurs.
        """
        try:
            data = {
                "symbols": symbol
            }
            response = client.get_quotes(data=data)
            ltp = response['d'][0]['v']['lp']
            low_price = response['d'][0]['v']['low_price']
            logging.info(f"symbol : {symbol} ==> Ltp : {ltp} ==> Low Price : {low_price}")
            return low_price
        except Exception as e:
            logging.error(f"An error occurred while fetching the low price for symbol {symbol}: {e}")
            return None

    def lots_to_buy(capital, lot_size, price_per_share, transaction_fee=0):
        """
        Calculate the number of lots you can buy with a fixed capital.

        Args:
            capital (float): The total amount of capital available.
            lot_size (int): The number of shares in one lot.
            price_per_share (float): The price of a single share.
            transaction_fee (float): Any fixed transaction fee (default is 0).

        Returns:
            int: The number of lots you can buy.
            float: The remaining capital after the purchase.

        Usage:
            capital = 21000  # Fixed capital
            lot_size = 75  # Number of shares in one lot
            price_per_share = 20  # Price of a single share

            lots, remaining_capital = calculate_lots_to_buy(capital, lot_size, price_per_share)

            print(f"Lots you can buy: {lots}")
            print(f"Total share : {lots*lot_size:}")
            print(f"Used capital: {(lots*lot_size)*price_per_share:}")
            print(f"Remaining capital: {remaining_capital:.2f}")
        """

        if price_per_share <= 0 or lot_size <= 0:
            raise ValueError("Price per share and lot size must be greater than zero.")
        if capital <= transaction_fee:
            return 0, capital  # Not enough to buy any lots after fees.

        # Calculate the price of one lot
        price_per_lot = lot_size * price_per_share

        # Capital available after deducting the transaction fee
        available_capital = capital - transaction_fee

        # Calculate the number of lots
        lots = int(available_capital // price_per_lot)  # Floor division to get whole lots

        # Calculate remaining capital
        # remaining_capital = available_capital - (lots * price_per_lot)

        total_share = lots * lot_size

        return total_share


if __name__ == '__main__':
    token = Utility.get_root_dir()
    print(token)