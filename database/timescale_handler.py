import os
import psycopg2
from dotenv import load_dotenv


class TimescaleDBHandler:
    def __init__(self):
        """
        Initialize TimescaleDB connection using credentials from the .env file.
        """
        env_path = os.path.join(os.path.dirname(__file__), '../config/.env')
        load_dotenv(env_path)

        self.host = os.getenv("TIMESCALEDB_HOST")
        self.port = os.getenv("TIMESCALEDB_PORT")
        self.user = os.getenv("TIMESCALEDB_USER")
        self.password = os.getenv("TIMESCALEDB_PASSWORD")
        self.database = os.getenv("TIMESCALEDB_DATABASE")

        if not all([self.host, self.port, self.user, self.password, self.database]):
            raise ValueError("❌ TimescaleDB credentials are missing. Check your .env file.")

        self.conn = None
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
        try:
            self.cursor.execute(query, params or ())
            result = self.cursor.fetchall()
            return result if result else []  # Ensures empty list instead of None
        except psycopg2.Error as e:
            print(f"❌ Query execution error: {e}")
            return []

    def execute_update(self, query, params=None):
        """Execute an INSERT, UPDATE, or DELETE query."""
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


# ✅ Fetch latest 10 records from nifty50_1m
if __name__ == "__main__":
    db_handler = TimescaleDBHandler()

    SCHEMA_NAME = 'sensex'
    TABLE_NAME = 'sensex_1m'
    query = f"""
        SELECT id, timestamp, open, high, low, close, volume 
        FROM {SCHEMA_NAME}.{TABLE_NAME} 
        ORDER BY timestamp DESC 
        LIMIT 10;
    """

    results = db_handler.execute_query(query)

    if results:
        print(f"\n📌 Latest 10 records from {TABLE_NAME}:")
        for row in results:
            print(row)
    else:
        print(f"\n⚠️ No data found in {TABLE_NAME}.")

    db_handler.close()
