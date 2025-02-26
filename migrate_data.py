import os
import pymysql
import psycopg2
from dotenv import load_dotenv
from tqdm import tqdm

# Load database credentials from .env
load_dotenv('config/.env')

"""
# MySQL Credentials
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=Root@000###
MYSQL_DATABASE=fnodatabase

# TimescaleDB (PostgreSQL) Credentials
TIMESCALEDB_HOST=localhost
TIMESCALEDB_PORT=5432
TIMESCALEDB_USER=postgres
TIMESCALEDB_PASSWORD=Root@000###
TIMESCALEDB_DATABASE=fnodatabase
"""

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
}

TIMESCALE_CONFIG = {
    "host": os.getenv("TIMESCALEDB_HOST"),
    "port": int(os.getenv("TIMESCALEDB_PORT")),
    "user": os.getenv("TIMESCALEDB_USER"),
    "password": os.getenv("TIMESCALEDB_PASSWORD"),
    "database": os.getenv("TIMESCALEDB_DATABASE"),
}

TABLE_NAME = 'sensex_1d'
SCHEMA_NAME = 'sensex'


def fetch_mysql_data():
    """Fetch all data from MySQL nifty50_1m table."""
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = mysql_conn.cursor()
        query = F"SELECT id, timestamp, open, high, low, close, volume FROM {TABLE_NAME} ORDER BY timestamp ASC;"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        mysql_conn.close()
        print(f"✅ Fetched {len(data)} records from MySQL {TABLE_NAME}.")
        return data
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        return []


def insert_into_timescale(data):
    """Insert data into TimescaleDB nifty50_1m table."""
    try:
        timescale_conn = psycopg2.connect(**TIMESCALE_CONFIG)
        cursor = timescale_conn.cursor()

        insert_query = F"""
            INSERT INTO {SCHEMA_NAME}.{TABLE_NAME} (id, timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (timestamp, id) DO NOTHING;
        """

        for row in tqdm(data, desc="📥 Migrating Data", unit="rows"):
            cursor.execute(insert_query, row)

        timescale_conn.commit()
        cursor.close()
        timescale_conn.close()
        print("✅ Data migration to TimescaleDB completed!")
    except psycopg2.Error as e:
        print(f"❌ TimescaleDB Error: {e}")


if __name__ == "__main__":
    # Step 1: Fetch data from MySQL
    #$mysql_data = None # fetch_mysql_data()
    mysql_data = fetch_mysql_data()

    # Step 2: Insert into TimescaleDB
    if mysql_data:
        insert_into_timescale(mysql_data)
    else:
        print("⚠️ No data found in MySQL. Migration skipped.")
