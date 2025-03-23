import pandas as pd
import numpy as np
from datetime import datetime


def timestamp_to_datetime(timestamp: int) -> datetime:
    """
    Convert a UNIX timestamp to a datetime object (assumes UTC).

    Args:
        timestamp (int): The UNIX timestamp to convert.

    Returns:
        datetime: A datetime object representing the given timestamp.

    Example:
        # >>> timestamp_to_datetime(1672527600)
        datetime.datetime(2023, 1, 1, 12, 0)
    """
    return datetime.fromtimestamp(timestamp)


def datetime_to_timestamp(dt: datetime) -> int:
    """
    Convert a datetime object to a UNIX timestamp.

    Args:
        dt (datetime): The datetime object to convert.

    Returns:
        int: The UNIX timestamp representing the given datetime.

    Example:
        # >>> datetime_to_timestamp(datetime(2023, 1, 1, 12, 0, 0))
        1672527600
    """
    return int(dt.timestamp())


def string_to_datetime(date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Convert a date string to a datetime object.

    Args:
        date_str (str): The date string to convert.
        fmt (str, optional): The format of the date string. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        datetime: A datetime object parsed from the string.

    Example:
        # >>> string_to_datetime("2023-01-01 12:00:00")
        datetime.datetime(2023, 1, 1, 12, 0)
    """
    return datetime.strptime(date_str, fmt)


def datetime_to_string(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Convert a datetime object to a formatted date string.

    Args:
        dt (datetime): The datetime object to convert.
        fmt (str, optional): The format for the date string. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: A formatted date string.

    Example:
        # >>> datetime_to_string(datetime(2023, 1, 1, 12, 0, 0))
        '2023-01-01 12:00:00'
    """
    return dt.strftime(fmt)


def timestamp_to_string(timestamp: int, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Convert a UNIX timestamp directly to a formatted date string.

    Args:
        timestamp (int): The UNIX timestamp to convert.
        fmt (str, optional): The format for the date string. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: A formatted date string.

    Example:
        # >>> timestamp_to_string(1672527600)
        '2023-01-01 12:00:00'
    """
    dt = timestamp_to_datetime(timestamp)
    return datetime_to_string(dt, fmt)


def string_to_timestamp(date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> int:
    """
    Convert a formatted date string directly to a UNIX timestamp.

    Args:
        date_str (str): The date string to convert.
        fmt (str, optional): The format of the date string. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        int: The UNIX timestamp representing the given date string.

    Example:
        # >>> string_to_timestamp("2023-01-01 12:00:00")
        1672527600
    """
    dt = string_to_datetime(date_str, fmt)
    return datetime_to_timestamp(dt)


def seconds_to_milliseconds(seconds):
    """
    Converts seconds to milliseconds (timezone-naive).

    Args:
        seconds (int, float, list, pd.Series, np.array): Seconds to convert.

    Returns:
        pd.Series: Milliseconds as a pandas Series.
    """
    return (pd.to_datetime(seconds, unit='s').astype(np.int64) // 10 ** 6).astype(np.int64)


def milliseconds_to_datetime(milliseconds, to_format='%Y-%m-%d %H:%M:%S'):
    """
    Converts milliseconds to datetime strings (timezone-naive).

    Args:
        milliseconds (int, float, list, pd.Series, np.array): Milliseconds to convert.
        to_format (str, optional): The desired datetime string format. Defaults to '%Y-%m-%d %H:%M:%S'.

    Returns:
        pd.Series: Datetime strings as a pandas Series.
    """
    return pd.to_datetime(milliseconds, unit='ms').to_series().dt.strftime(to_format)


def datetime_to_seconds(datetimes):
    """
    Converts datetime strings to seconds (timezone-naive).

    Args:
        datetimes (str, list, pd.Series, np.array): Datetime strings to convert.

    Returns:
        pd.Series: Seconds as a pandas Series.
    """
    return (pd.to_datetime(datetimes).astype(np.int64) // 10 ** 9).astype(np.int64)


def nanoseconds_to_milliseconds(nanoseconds):
    """
    Converts nanoseconds to milliseconds (timezone-naive).

    Args:
        nanoseconds (int, float, list, pd.Series, np.array): Nanoseconds to convert.

    Returns:
        pd.Series: Milliseconds as a pandas Series.
    """
    return (pd.to_datetime(nanoseconds, unit='ns').astype(np.int64) // 10 ** 6).astype(np.int64)


def microseconds_to_datetime(microseconds, to_format='%Y-%m-%d %H:%M:%S'):
    """
    Converts microseconds to datetime strings (timezone-naive).

    Args:
        microseconds (int, float, list, pd.Series, np.array): Microseconds to convert.
        to_format (str, optional): The desired datetime string format. Defaults to '%Y-%m-%d %H:%M:%S'.

    Returns:
        pd.Series: Datetime strings as a pandas Series.
    """
    return pd.to_datetime(microseconds, unit='us').to_series().dt.strftime(to_format)


def string_milliseconds_to_datetime(string_milliseconds, to_format='%Y-%m-%d %H:%M:%S'):
    """
    Converts string of milliseconds to datetime strings (timezone-naive).

    Args:
        string_milliseconds (str, list, pd.Series, np.array): Strings representing milliseconds to convert.
        to_format (str, optional): The desired datetime string format. Defaults to '%Y-%m-%d %H:%M:%S'.

    Returns:
        pd.Series: Datetime strings as a pandas Series.
    """
    return pd.to_datetime(pd.to_numeric(string_milliseconds), unit='ms').to_series().dt.strftime(to_format)


def format_timestamp(timestamp, from_format=None, to_format='%Y-%m-%d %H:%M:%S'):
    """
    Formats a timestamp into a specified datetime string format (timezone-naive).

    Args:
        timestamp (int, float, str, pd.Series, list, np.array): The timestamp to format.
        from_format (str, optional): The original format of the timestamp. If None, pandas will attempt to infer.
                                      Examples: 's', 'ms', 'us', 'ns', '%Y-%m-%d %H:%M:%S', etc.
        to_format (str, optional): The desired datetime string format. Defaults to '%Y-%m-%d %H:%M:%S'.

    Returns:
        pd.Series: The formatted timestamps as a pandas Series.
    """

    if isinstance(timestamp, (int, float, str)):
        timestamp = [timestamp]

    timestamps_series = pd.Series(timestamp)

    if from_format is None:
        timestamps_series = pd.to_datetime(timestamps_series)
    elif from_format in ['s', 'ms', 'us', 'ns']:
        timestamps_series = pd.to_datetime(pd.to_numeric(timestamps_series, errors='coerce'), unit=from_format)
    else:
        timestamps_series = pd.to_datetime(timestamps_series, format=from_format)

    return timestamps_series.dt.strftime(to_format)


if __name__ == '__main__':
    # Example Usage:
    seconds = [1678886400, 1678886460]
    milliseconds = [1678886400000, 1678886460000]
    datetimes = ['2023-03-15 00:00:00', '2023-03-15 00:01:00']
    nanos = np.array([1678886400000000000, 1678886460000000000])
    micros = [1678886400000000, 1678886460000000]
    string_millis = ["1678886400000", "1678886460000"]

    print("Seconds to Milliseconds:", seconds_to_milliseconds(seconds))
    print("Milliseconds to Datetime:", milliseconds_to_datetime(milliseconds))
    print("Datetime to Seconds:", datetime_to_seconds(datetimes))
    print("Nanoseconds to Milliseconds:", nanoseconds_to_milliseconds(nanos))
    print("Microseconds to Datetime:", microseconds_to_datetime(micros))
    print("String Milliseconds to Datetime:", string_milliseconds_to_datetime(string_millis))

    # Example usage for format_timestamp
    print("\nFormat Seconds:", format_timestamp(seconds, from_format='s'))
    print("Format Milliseconds:", format_timestamp(milliseconds, from_format='ms'))
    print("Format Datetimes:", format_timestamp(datetimes))  # infers
    print("Format Nanos:", format_timestamp(nanos, from_format='ns'))
    print("Format Micros:", format_timestamp(micros, from_format='us'))
    print("Format String Millis:", format_timestamp(string_millis, from_format='ms'))
