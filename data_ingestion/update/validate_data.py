"""
🔹 update/validate_data.py (Check for Inconsistent Data)
Ensures high > low and open/close within high-low.
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

def validate_ohlc_data():
    """Check for OHLC violations in TimescaleDB."""
    query = """
    SELECT * FROM nifty50.nifty50_1m
    WHERE high <= low OR open < low OR open > high OR close < low OR close > high;
    """
    try:
        conn = psycopg2.connect(**TIMESCALE_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query)
        invalid_rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if invalid_rows:
            print(f"⚠️ Found {len(invalid_rows)} invalid OHLC records.")
            return invalid_rows
        else:
            print("✅ Data is consistent.")
            return []
    except psycopg2.Error as e:
        print(f"❌ TimescaleDB Error: {e}")
        return []

# Example usage
# invalid_data = validate_ohlc_data()
