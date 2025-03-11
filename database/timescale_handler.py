import os
import psycopg2
from dotenv import load_dotenv
from utils.env_loader import load_env


class TimescaleDBHandler:
    def __init__(self):
        """
        Initialize TimescaleDB connection using credentials from the .env file.
        """
        load_dotenv(load_env())

        self.host = os.getenv("TIMESCALEDB_HOST")
        self.port = os.getenv("TIMESCALEDB_PORT")
        self.user = os.getenv("TIMESCALEDB_USER")
        self.password = os.getenv("TIMESCALEDB_PASSWORD")
        self.database = os.getenv("TIMESCALEDB_DATABASE")

        if not all([self.host, self.port, self.user, self.password, self.database]):
            raise ValueError("❌ TimescaleDB credentials are missing. Check your .env file.")

        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Establish a connection to TimescaleDB."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=int(self.port),
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
            print("✅ Connected to TimescaleDB successfully!")
        except psycopg2.Error as e:
            print(f"❌ Connection error: {e}")
            self.conn = None

    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results."""
        if not self.conn:
            print("❌ No active database connection.")
            return []
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall() or []
        except psycopg2.Error as e:
            print(f"❌ Query execution error: {e}")
            return []

    def execute_update(self, query, params=None):
        """Execute an INSERT, UPDATE, or DELETE query."""
        if not self.conn:
            print("❌ No active database connection.")
            return
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            print("✅ Query executed successfully!")
        except psycopg2.Error as e:
            print(f"❌ Update error: {e}")
            self.conn.rollback()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("🔌 TimescaleDB connection closed.")

    def __enter__(self):
        """Enable context manager support."""
        if not self.conn:
            self.connect()
        if self.conn:
            return self
        raise ConnectionError("❌ Could not establish database connection.")

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure connection closes when exiting context manager."""
        self.close()
