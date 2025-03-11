import os
import urllib.parse
import logging
import pymysql
import psycopg2
import sqlalchemy
import influxdb_client
from dotenv import load_dotenv
from psycopg2 import pool
from influxdb_client.client.write_api import SYNCHRONOUS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class DatabaseConnector:
    """Handles connections to MySQL, TimescaleDB, and InfluxDB."""

    def __init__(self):
        # Load MySQL credentials
        self.mysql_host = os.getenv("MYSQL_HOST", "127.0.0.1")
        self.mysql_port = os.getenv("MYSQL_PORT", "3306")
        self.mysql_user = urllib.parse.quote_plus(os.getenv("MYSQL_USER", "root"))
        self.mysql_password = urllib.parse.quote_plus(os.getenv("MYSQL_PASSWORD", "password"))
        self.mysql_db = os.getenv("MYSQL_DATABASE", "fnodatabase")

        # Load TimescaleDB credentials
        self.ts_host = os.getenv("TIMESCALEDB_HOST", "127.0.0.1")
        self.ts_port = os.getenv("TIMESCALEDB_PORT", "5432")
        self.ts_user = os.getenv("TIMESCALEDB_USER", "postgres")
        self.ts_password = os.getenv("TIMESCALEDB_PASSWORD", "password")
        self.ts_db = os.getenv("TIMESCALEDB_DATABASE", "trading_db")

        # Load InfluxDB credentials
        self.influx_url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
        self.influx_token = os.getenv("INFLUXDB_TOKEN", "my-token")
        self.influx_org = os.getenv("INFLUXDB_ORG", "my-org")
        self.influx_bucket = os.getenv("INFLUXDB_BUCKET", "trading")

        # Connection pools
        self.ts_pool = None

    def get_mysql_engine(self):
        """Return a SQLAlchemy engine for MySQL."""
        try:
            engine = sqlalchemy.create_engine(
                f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
            )
            logging.info("✅ MySQL connection established successfully!")
            return engine
        except Exception as e:
            logging.error(f"❌ MySQL connection error: {e}")
            return None

    def get_mysql_connection(self):
        """Return a raw PyMySQL connection for MySQL."""
        try:
            connection = pymysql.connect(
                host=self.mysql_host,
                user=self.mysql_user,
                password=self.mysql_password,
                database=self.mysql_db,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            logging.info("✅ Connected to MySQL (PyMySQL).")
            return connection
        except Exception as e:
            logging.error(f"❌ MySQL (PyMySQL) connection error: {e}")
            return None

    def get_timescale_connection(self):
        """Return a PostgreSQL connection for TimescaleDB."""
        try:
            connection = psycopg2.connect(
                host=self.ts_host,
                port=self.ts_port,
                user=self.ts_user,
                password=self.ts_password,
                database=self.ts_db
            )
            logging.info("✅ Connected to TimescaleDB.")
            return connection
        except Exception as e:
            logging.error(f"❌ TimescaleDB connection error: {e}")
            return None

    def get_timescale_pool(self):
        """Return a connection pool for TimescaleDB."""
        if not self.ts_pool:
            try:
                self.ts_pool = pool.SimpleConnectionPool(
                    1, 10,  # Min & Max connections
                    host=self.ts_host,
                    port=self.ts_port,
                    user=self.ts_user,
                    password=self.ts_password,
                    database=self.ts_db
                )
                logging.info("✅ TimescaleDB connection pool created.")
            except Exception as e:
                logging.error(f"❌ Failed to create TimescaleDB connection pool: {e}")
                self.ts_pool = None
        return self.ts_pool

    def get_influxdb_client(self):
        """Return an InfluxDB client."""
        try:
            client = influxdb_client.InfluxDBClient(
                url=self.influx_url,
                token=self.influx_token,
                org=self.influx_org
            )
            logging.info("✅ Connected to InfluxDB.")
            return client
        except Exception as e:
            logging.error(f"❌ InfluxDB connection error: {e}")
            return None

    def get_influx_write_api(self):
        """Return an InfluxDB write API."""
        client = self.get_influxdb_client()
        if client:
            return client.write_api(write_options=SYNCHRONOUS)
        return None

    def close_connections(self):
        """Close all database connections."""
        if self.ts_pool:
            self.ts_pool.closeall()
            logging.info("🔌 TimescaleDB connection pool closed.")

    def __del__(self):
        self.close_connections()


# Example usage
if __name__ == "__main__":
    db_connector = DatabaseConnector()

    # MySQL (SQLAlchemy)
    mysql_engine = db_connector.get_mysql_engine()

    # MySQL (PyMySQL)
    mysql_conn = db_connector.get_mysql_connection()
    if mysql_conn:
        mysql_conn.close()

    # TimescaleDB
    timescale_conn = db_connector.get_timescale_connection()
    if timescale_conn:
        timescale_conn.close()

    # InfluxDB
    influx_client = db_connector.get_influxdb_client()
    influx_write_api = db_connector.get_influx_write_api()
