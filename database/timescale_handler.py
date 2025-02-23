import os
import psycopg2
from dotenv import load_dotenv


class TimescaleDBHandler:
    def __init__(self):
        # Load environment variables
        env_path = os.path.join(os.path.dirname(__file__), '../config/.env')
        load_dotenv(env_path)

        # Read TimescaleDB credentials from .env
        self.host = os.getenv("TIMESCALEDB_HOST")
        self.port = os.getenv("TIMESCALEDB_PORT")
        self.user = os.getenv("TIMESCALEDB_USER")
        self.password = os.getenv("TIMESCALEDB_PASSWORD")
        self.database = os.getenv("TIMESCALEDB_DATABASE")

        # Ensure credentials are set
        if not all([self.host, self.port, self.user, self.password, self.database]):
            raise ValueError("TimescaleDB credentials are missing. Check your .env file.")

        # Connect to TimescaleDB
        self.conn = None
        self.connect()

    def connect(self):
        """
        Establish a connection to TimescaleDB.
        """
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=int(self.port),
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
            print("✅ TimescaleDB connection established successfully!")
        except psycopg2.Error as e:
            print(f"❌ Error connecting to TimescaleDB: {e}")
            self.conn = None

    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return the result.
        """
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"❌ TimescaleDB query error: {e}")
            return None

    def execute_update(self, query, params=None):
        """
        Execute an INSERT, UPDATE, or DELETE query.
        """
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            print("✅ Query executed successfully!")
        except psycopg2.Error as e:
            print(f"❌ Error executing update: {e}")
            self.conn.rollback()

    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("🔌 TimescaleDB connection closed.")


# Example Usage
if __name__ == "__main__":
    db_handler = TimescaleDBHandler()

    # Test Query
    result = db_handler.execute_query("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='fnodatabase';")
    print("Tables:", result)

    # Close Connection
    db_handler.close()
