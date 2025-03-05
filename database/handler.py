import os
import asyncio
import logging
import threading
import influxdb_client
import websockets
from dotenv import load_dotenv

from mysql.connector.pooling import MySQLConnectionPool
from psycopg2.pool import SimpleConnectionPool
from influxdb_client.client.write_api import SYNCHRONOUS
from tenacity import retry, stop_after_attempt, wait_fixed
from utils.env_loader import load_env

# Load environment variables
load_dotenv(load_env())

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DatabaseHandler(object):
    _lock = threading.Lock()

    def __init__(self, db_config):
        """
        Initialize a database handler for MySQL, TimescaleDB, or InfluxDB.
        :param db_type: str -> "mysql", "timescaledb", or "influxdb"
        """
        if not isinstance(db_config, dict):
            raise ValueError("db_config should be a dictionary")

        self.db_type = db_config.get("type", "").lower()  # Extract db_type safely

        # print(f"🔍 Database Type Detected: {self.db_type}")  # Debugging line

        self.config = db_config  # Store full config for later use
        self.conn = None
        self.cursor = None
        self.pool = None

        if self.db_type == "mysql":
            self._init_mysql()
        elif self.db_type == "timescaledb":
            self._init_timescaledb()
        elif self.db_type == "influxdb":
            self._init_influxdb()
        else:
            raise ValueError("❌ Unsupported database type. Use 'mysql', 'timescaledb', or 'influxdb'.")

    def _init_mysql(self):
        """Initialize MySQL connection pool."""
        with self._lock:
            self.pool = MySQLConnectionPool(
                pool_name="mysql_pool",
                pool_size=5,
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE"),
            )
        logger.info("✅ MySQL connection pool initialized.")

    def _init_timescaledb(self):
        """Initialize TimescaleDB connection pool."""
        with self._lock:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                host=os.getenv("TIMESCALEDB_HOST"),
                user=os.getenv("TIMESCALEDB_USER"),
                password=os.getenv("TIMESCALEDB_PASSWORD"),
                database=os.getenv("TIMESCALEDB_DATABASE"),
            )
        logger.info("✅ TimescaleDB connection pool initialized.")

    def _init_influxdb(self):
        """Initialize InfluxDB client."""
        self.client = influxdb_client.InfluxDBClient(
            url=os.getenv("INFLUXDB_URL"),
            token=os.getenv("INFLUXDB_TOKEN"),
            org=os.getenv("INFLUXDB_ORG"),
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        logger.info("✅ InfluxDB client initialized.")

    def get_connection(self):
        """Retrieve a connection from the pool (MySQL & TimescaleDB only)."""
        if self.db_type == "mysql":
            self.conn = self.pool.get_connection()  # ✅ Use `get_connection()`
        elif self.db_type == "timescaledb":
            self.conn = self.pool.getconn()  # ✅ TimescaleDB uses `getconn()`
        self.cursor = self.conn.cursor()
        return self.conn

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def execute_query(self, query, params=None):
        """
        Execute SELECT queries asynchronously with retry logic.
        :param query: str -> SQL query
        :param params: tuple -> Query parameters
        """
        if self.db_type in ["mysql", "timescaledb"]:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, self._execute_query_sync, query, params)

    def _execute_query_sync(self, query, params=None):
        """Helper function to execute queries synchronously with retry logic."""
        self.get_connection()
        try:
            self.cursor.execute(query, params or ())
            results = self.cursor.fetchall()
            logger.info(f"✅ Query executed: {query}")
            return results if results else []
        except Exception as e:
            logger.error(f"❌ Query execution error: {e}")
            return []
        finally:
            self.close()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def execute_update(self, query, params=None):
        """
        Execute INSERT, UPDATE, or DELETE queries asynchronously with retry logic.
        :param query: str -> SQL query
        :param params: tuple -> Query parameters
        """
        if self.db_type in ["mysql", "timescaledb"]:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._execute_update_sync, query, params)

    def _execute_update_sync(self, query, params=None):
        """Helper function to execute update queries synchronously with retry logic."""
        self.get_connection()
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            logger.info(f"✅ Query executed: {query}")
        except Exception as e:
            logger.error(f"❌ Update error: {e}")
            self.conn.rollback()
        finally:
            self.close()

    def write_influx(self, bucket, measurement, tags, fields):
        """
        Write data to InfluxDB.
        :param bucket: str -> InfluxDB bucket name
        :param measurement: str -> Measurement name
        :param tags: dict -> Tags dictionary
        :param fields: dict -> Fields dictionary
        """
        if self.db_type != "influxdb":
            raise ValueError("❌ write_influx is only available for InfluxDB.")

        point = influxdb_client.Point(measurement).tag(tags).field(fields)
        self.write_api.write(bucket=bucket, org=os.getenv("INFLUXDB_ORG"), record=point)
        logger.info(f"✅ InfluxDB Write: {measurement} - {fields}")

    def close(self):
        """Release the connection back to the pool."""
        if self.db_type == "mysql" and self.conn:
            self.conn.close()  # ✅ Correct for MySQL
            self.conn = None
            self.cursor = None
        elif self.db_type == "timescaledb" and self.conn:
            self.pool.putconn(self.conn)  # ✅ Correct for TimescaleDB
            self.conn = None
            self.cursor = None

    def close_all(self):
        """Close all database connections."""
        if self.db_type == "mysql":
            self.pool = None  # MySQL pool does not support closeall()
            logger.info("🔌 MySQL connection pool cleared.")
        elif self.db_type == "timescaledb":
            self.pool.closeall()
            logger.info("🔌 TimescaleDB connection pool closed.")
        elif self.db_type == "influxdb":
            self.client.close()
            logger.info("🔌 InfluxDB client closed.")

    async def websocket_stream(self, uri):
        """WebSocket client for real-time market data."""
        try:
            async with websockets.connect(uri) as ws:
                while True:
                    message = await ws.recv()
                    logger.info(f"📡 Real-Time Data: {message}")
        except Exception as e:
            logger.error(f"❌ WebSocket Error: {e}")

# Example Usage
if __name__ == "__main__":
    async def main():

        """
        db_config = {
            "type": "mysql",
            "host": os.getenv("MYSQL_HOST"),
            "user": os.getenv("MYSQL_USER"),
            "password": os.getenv("MYSQL_PASSWORD"),
            "database": os.getenv("MYSQL_DATABASE"),
        }

        # MySQL Example
        mysql_handler = DatabaseHandler(db_config)
        results = await mysql_handler.execute_query("SELECT * FROM nifty50_1m LIMIT 5;")
        logger.info(results)
        mysql_handler.close_all()
        """

        # TimescaleDB Example
        tsdb_config = {
            "type": "timescaledb",
            "host": os.getenv("TIMESCALEDB_HOST"),
            "user": os.getenv("TIMESCALEDB_USER"),
            "password": os.getenv("TIMESCALEDB_PASSWORD"),
            "database": os.getenv("TIMESCALEDB_DATABASE"),
        }
        tsdb_handler = DatabaseHandler(tsdb_config)
        results = await tsdb_handler.execute_query("SELECT * FROM nifty50.nifty50_1d LIMIT 5;")
        logger.info(results)
        tsdb_handler.close_all()

        """
        # InfluxDB Example
        influx_config = {
            "type": "influxdb",
            "url": os.getenv("INFLUXDB_URL"),
            "token": os.getenv("INFLUXDB_TOKEN"),
            "org": os.getenv("INFLUXDB_ORG"),
        }
        influx_handler = DatabaseHandler(influx_config)
        influx_handler.write_influx("market_data", "ohlc", {"symbol": "NIFTY50"}, {"open": 100, "close": 102})
        influx_handler.close_all()

        # WebSocket Example (Standalone)
        ws_handler = DatabaseHandler(db_config)
        await ws_handler.websocket_stream("wss://your-websocket-url")
        """


    asyncio.run(main())
