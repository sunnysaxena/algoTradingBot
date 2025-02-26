"""
🔹 update/resample_data.py (Resample 1-Minute Data to Higher Intervals)
Converts 1m data into 5m, 15m, 1h intervals.
"""

import psycopg2

# Database connection config
TIMESCALE_CONFIG = {
    "host": "your_host",
    "port": "your_port",
    "dbname": "your_database",
    "user": "your_user",
    "password": "your_password"
}

def resample_ohlc(interval="5m"):
    """Resample 1m OHLC data into 5m, 15m, or 1h intervals."""
    interval_map = {"5m": "5 minutes", "15m": "15 minutes", "1h": "1 hour"}
    if interval not in interval_map:
        print("❌ Invalid interval. Choose '5m', '15m', or '1h'.")
        return

    query = f"""
    INSERT INTO nifty50.nifty50_{interval} (timestamp, open, high, low, close, volume)
    SELECT time_bucket('{interval_map[interval]}', timestamp) AS timestamp,
           first(open, timestamp) AS open,
           MAX(high) AS high,
           MIN(low) AS low,
           last(close, timestamp) AS close,
           SUM(volume) AS volume
    FROM nifty50.nifty50_1m
    GROUP BY timestamp
    ORDER BY timestamp;
    """

    try:
        conn = psycopg2.connect(**TIMESCALE_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        print(f"✅ Resampled data to {interval}.")
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"❌ TimescaleDB Error: {e}")

# Example usage
# resample_ohlc("5m")
