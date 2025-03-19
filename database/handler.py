import os
import asyncio
import logging
import threading
import asyncpg
import aiomysql
import pandas as pd
import influxdb_client
import redis.asyncio as redis
from dotenv import load_dotenv
from utils.env_loader import load_env
from influxdb_client.client.write_api import SYNCHRONOUS

# Load environment variables
load_dotenv(load_env())

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DatabaseHandler:
    _lock = threading.Lock()

    def __init__(self, db_config):
        if not isinstance(db_config, dict):
            raise ValueError("db_config should be a dictionary")

        self.db_type = db_config.get("type", "").lower()
        self.config = db_config
        self.pool = None
        self.client = None
        self.redis = None
        self._initialization_task = None

    async def _initialize_database(self):
        if self.db_type == "mysql" and self.pool is None:
            self.pool = await aiomysql.create_pool(
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                db=os.getenv("MYSQL_DATABASE"),
                minsize=1,
                maxsize=5
            )
            logger.info("✅ MySQL async connection pool initialized.")
        elif self.db_type == "timescaledb" and self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=os.getenv("TIMESCALEDB_HOST"),
                user=os.getenv("TIMESCALEDB_USER"),
                password=os.getenv("TIMESCALEDB_PASSWORD"),
                database=os.getenv("TIMESCALEDB_DATABASE"),
                min_size=1,
                max_size=5
            )
            logger.info("✅ TimescaleDB async connection pool initialized.")
        elif self.db_type == "influxdb" and self.client is None:
            self.client = influxdb_client.InfluxDBClient(
                url=os.getenv("INFLUXDB_URL"),
                token=os.getenv("INFLUXDB_TOKEN"),
                org=os.getenv("INFLUXDB_ORG"),
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            logger.info("✅ InfluxDB client initialized.")

    async def _ensure_initialized(self):
        if self._initialization_task is None:
            self._initialization_task = asyncio.create_task(self._initialize_database())
        await self._initialization_task
        self._initialization_task = None # Reset after completion

    async def _init_redis(self):
        if self.redis is None:
            self.redis = await redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
            logger.info("✅ Redis cache initialized.")

    async def execute_query(self, query, params=None):
        await self._ensure_initialized()
        if self.db_type == "timescaledb":
            async with self.pool.acquire() as conn:
                if params is None:
                    return await conn.fetch(query)
                else:
                    return await conn.fetch(query, *params)
        elif self.db_type == "mysql":
            async with self.pool.acquire() as conn:
                return await self._execute_mysql_query(conn, query, params)
        elif self.db_type == "influxdb" and self.client:
            query_api = self.client.query_api()
            tables = query_api.query(query=query)
            if tables and len(tables) > 0:
                return tables[0].records
            return []
        return None

    async def _execute_mysql_query(self, conn, query, params):
        async with conn.cursor() as cursor:
            await cursor.execute(query, params or ())
            return await cursor.fetchall()

    async def execute_update(self, query, params=None):
        await self._ensure_initialized()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(query, *params)
                logger.info(f"✅ Query executed: {query}")

    async def batch_insert(self, table, data):
        await self._ensure_initialized()
        if not data:
            return
        columns = data[0].keys()
        values_str = ", ".join([f"(${i + 1})" for i in range(len(columns))])
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES {values_str}"
        async with self.pool.acquire() as conn:
            await conn.executemany(query, [tuple(d.values()) for d in data])
            logger.info(f"✅ Batch inserted {len(data)} rows into {table}")

    async def fetch_historical_data(self, symbol, start_time, end_time, timeframe='1m', custom_table_name=None):
        """Fetch historical OHLC data from the database."""
        table = custom_table_name
        if not table:
            logger.warning(f"No table name provided for symbol '{symbol}' and timeframe '{timeframe}'.")
            return pd.DataFrame()

        await self._ensure_initialized()

        try:
            # Check cache first
            cache_key = f"{table}:{start_time}:{end_time}"
            await self._init_redis()
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                logger.info(f"✅ Retrieved data from cache for {table}")
                return pd.read_json(cached_data)

            # Build query based on database type
            if self.db_type == "timescaledb":
                query = f"""
                    SELECT timestamp, open, high, low, close, volume
                    FROM {table}
                    WHERE timestamp >= $1 AND timestamp <= $2
                    ORDER BY timestamp ASC
                """
                params = (start_time, end_time)
                data = await self.execute_query(query, params)
                if data:
                    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df.set_index('timestamp', inplace=True)
                    await self.redis.set(cache_key, df.to_json(), ex=300)
                    return df
                return pd.DataFrame()

            elif self.db_type == "mysql":
                query = f"""
                    SELECT timestamp, open, high, low, close, volume
                    FROM {table}
                    WHERE timestamp >= %s AND timestamp <= %s
                    ORDER BY timestamp ASC
                """
                params = (start_time, end_time)
                data = await self.execute_query(query, params)
                if data:
                    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df.set_index('timestamp', inplace=True)
                    await self.redis.set(cache_key, df.to_json(), ex=300)
                    return df
                return pd.DataFrame()

            elif self.db_type == "influxdb":
                query_api = self.client.query_api()
                query = f'''
                    from(bucket: "{self.config.get('bucket', 'default')}")
                    |> range(start: "{start_time}", stop: "{end_time}")
                    |> filter(fn: (r) => r._measurement == "{table}")
                    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                '''
                tables = query_api.query(query)
                if tables and len(tables) > 0:
                    df = tables[0].records
                    df = pd.DataFrame.from_records(df, columns=['_time', 'open', 'high', 'low', 'close', 'volume'])
                    df = df.rename(columns={'_time': 'timestamp'}).set_index('timestamp')
                    await self.redis.set(cache_key, df.to_json(), ex=300)
                    return df
                return pd.DataFrame()

            else:
                raise ValueError(f"Unsupported db_type: {self.db_type}")

        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return pd.DataFrame()

    def get_table_name(self, symbol, timeframe):
        """
        This method is no longer directly used for fetching historical data
        in this specific backtesting setup.
        """
        return None

    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("🔌 Database connection pool closed.")
        if self.redis:
            await self.redis.close()
            logger.info("🔌 Redis cache closed.")
        if self.client:
            self.client.close()
            logger.info("🔌 InfluxDB client closed.")

    async def cache_get(self, key):
        await self._init_redis()
        return await self.redis.get(key)

    async def cache_set(self, key, value, expire=300):
        await self._init_redis()
        await self.redis.set(key, value, ex=expire)