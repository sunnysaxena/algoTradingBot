import os
import asyncio
import logging
import threading
import asyncpg
import aiomysql
import redis.asyncio as redis
import influxdb_client
from dotenv import load_dotenv
from influxdb_client.client.write_api import SYNCHRONOUS
from utils.env_loader import load_env

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

        if self.db_type == "mysql":
            self._init_mysql()
        elif self.db_type == "timescaledb":
            self._init_timescaledb()
        elif self.db_type == "influxdb":
            self._init_influxdb()
        else:
            raise ValueError("❌ Unsupported database type. Use 'mysql', 'timescaledb', or 'influxdb'.")

    async def _init_mysql(self):
        self.pool = await aiomysql.create_pool(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            db=os.getenv("MYSQL_DATABASE"),
            minsize=1,
            maxsize=5
        )
        logger.info("✅ MySQL async connection pool initialized.")

    async def _init_timescaledb(self):
        self.pool = await asyncpg.create_pool(
            host=os.getenv("TIMESCALEDB_HOST"),
            user=os.getenv("TIMESCALEDB_USER"),
            password=os.getenv("TIMESCALEDB_PASSWORD"),
            database=os.getenv("TIMESCALEDB_DATABASE"),
            min_size=1,
            max_size=5
        )
        logger.info("✅ TimescaleDB async connection pool initialized.")

    def _init_influxdb(self):
        self.client = influxdb_client.InfluxDBClient(
            url=os.getenv("INFLUXDB_URL"),
            token=os.getenv("INFLUXDB_TOKEN"),
            org=os.getenv("INFLUXDB_ORG"),
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        logger.info("✅ InfluxDB client initialized.")

    async def _init_redis(self):
        self.redis = await redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
        logger.info("✅ Redis cache initialized.")

    async def execute_query(self, query, params=None):
        if self.db_type in ["mysql", "timescaledb"]:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *params) if self.db_type == "timescaledb" else await self._execute_mysql_query(conn, query, params)

    async def _execute_mysql_query(self, conn, query, params):
        async with conn.cursor() as cursor:
            await cursor.execute(query, params or ())
            return await cursor.fetchall()

    async def execute_update(self, query, params=None):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(query, *params)
                logger.info(f"✅ Query executed: {query}")

    async def batch_insert(self, table, data):
        if not data:
            return
        columns = data[0].keys()
        values_str = ", ".join([f"(${i+1})" for i in range(len(columns))])
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES {values_str}"
        async with self.pool.acquire() as conn:
            await conn.executemany(query, [tuple(d.values()) for d in data])
            logger.info(f"✅ Batch inserted {len(data)} rows into {table}")

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
        if not self.redis:
            await self._init_redis()
        return await self.redis.get(key)

    async def cache_set(self, key, value, expire=300):
        if not self.redis:
            await self._init_redis()
        await self.redis.set(key, value, ex=expire)
