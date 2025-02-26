"""
🔹 update/backfill_missing_data.py (Fill Missing Data in TimescaleDB)
This script finds missing timestamps and fills gaps using historical data from an API or another source.
"""

import psycopg2
from datetime import datetime, timedelta

# Database connection config
TIMESCALE_CONFIG = {
    "host": "your_host",
    "port": "your_port",
    "dbname": "your_database",
    "user": "your_user",
    "password": "your_password"
}


def get_last_record_timestamp():
    """Fetch the last stored timestamp from the database."""
    query = "SELECT MAX(timestamp) FROM nifty50.nifty50_1m;"
    try:
        conn = psycopg2.connect(**TIMESCALE_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query)
        last_timestamp = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return last_timestamp
    except psycopg2.Error as e:
        print(f"❌ TimescaleDB Error: {e}")
        return None


def backfill_missing_data(fetch_data_func):
    """
    Backfills missing 1-minute OHLC data.
    `fetch_data_func` should be a function that retrieves missing data from an API.
    """
    last_timestamp = get_last_record_timestamp()
    if last_timestamp is None:
        print("⚠️ No data found in the database. Full ingestion needed.")
        return

    current_time = datetime.utcnow()

    # Generate missing timestamps
    missing_timestamps = []
    while last_timestamp < current_time - timedelta(minutes=1):
        last_timestamp += timedelta(minutes=1)
        missing_timestamps.append(last_timestamp)

    if not missing_timestamps:
        print("✅ No missing data detected.")
        return

    print(f"⚠️ Missing {len(missing_timestamps)} records. Fetching data...")

    # Fetch missing OHLC data from an API
    missing_data = fetch_data_func(missing_timestamps)

    # Insert missing data
    insert_query = """
        INSERT INTO nifty50.nifty50_1m (timestamp, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (timestamp) DO NOTHING;
    """

    try:
        conn = psycopg2.connect(**TIMESCALE_CONFIG)
        cursor = conn.cursor()
        cursor.executemany(insert_query, missing_data)
        conn.commit()
        print(f"✅ Backfilled {len(missing_data)} missing records.")
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"❌ TimescaleDB Error: {e}")

# Example usage (pass a function that fetches missing data)
# backfill_missing_data(your_fetch_function)
