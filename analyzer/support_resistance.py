import numpy as np
import pandas as pd
import logging
from sqlalchemy import create_engine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection (Modify for your setup)
DB_URI = "mysql+pymysql://user:password@localhost/trading_db"
engine = create_engine(DB_URI)


def fetch_ohlc(symbol: str, interval: str = '1d', limit: int = 100):
    """Fetch historical OHLC data from database."""
    query = f"""
        SELECT date, open, high, low, close FROM ohlc_data
        WHERE symbol = '{symbol}' ORDER BY date DESC LIMIT {limit}
    """
    df = pd.read_sql(query, engine)
    df.sort_values('date', inplace=True)
    return df


def find_support_resistance(df: pd.DataFrame):
    """Identify four support and resistance levels using swing highs/lows."""
    df['s1'] = df['low'].rolling(window=5, center=True).min()
    df['s2'] = df['low'].rolling(window=10, center=True).min()
    df['s3'] = df['low'].rolling(window=15, center=True).min()
    df['s4'] = df['low'].rolling(window=20, center=True).min()

    df['r1'] = df['high'].rolling(window=5, center=True).max()
    df['r2'] = df['high'].rolling(window=10, center=True).max()
    df['r3'] = df['high'].rolling(window=15, center=True).max()
    df['r4'] = df['high'].rolling(window=20, center=True).max()

    return df[['date', 's1', 's2', 's3', 's4', 'r1', 'r2', 'r3', 'r4']]


def calculate_pivot_points(df: pd.DataFrame):
    """Calculate pivot points and key levels."""
    df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
    df['r1'] = 2 * df['pivot'] - df['low']
    df['s1'] = 2 * df['pivot'] - df['high']
    df['r2'] = df['pivot'] + (df['high'] - df['low'])
    df['s2'] = df['pivot'] - (df['high'] - df['low'])
    return df[['date', 'pivot', 'r1', 's1', 'r2', 's2']]


def main():
    symbol = 'NIFTY50'
    df = fetch_ohlc(symbol)
    if df.empty:
        logging.error("No data retrieved from the database.")
        return

    support_resistance = find_support_resistance(df)
    pivot_points = calculate_pivot_points(df)

    logging.info("Support and Resistance Levels:")
    logging.info(support_resistance.tail())

    logging.info("Pivot Points:")
    logging.info(pivot_points.tail())

    return support_resistance, pivot_points


if __name__ == "__main__":
    main()
