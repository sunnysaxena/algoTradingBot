# data_ingestion/store_timescale.py
import os
import psycopg2


def store_to_timescale(df, table_name="nifty50_1m"):
    """Store OHLC data in TimescaleDB."""
    conn = psycopg2.connect(
        host=os.getenv("TIMESCALEDB_HOST"),
        port=os.getenv("TIMESCALEDB_PORT"),
        user=os.getenv("TIMESCALEDB_USER"),
        password=os.getenv("TIMESCALEDB_PASSWORD"),
        database=os.getenv("TIMESCALEDB_DATABASE")
    )
    cursor = conn.cursor()
    for _, row in df.iterrows():
        query = f"""INSERT INTO {table_name} (timestamp, open, high, low, close, volume) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, tuple(row))
    conn.commit()
    cursor.close()
    conn.close()
    print("Data stored successfully.")

