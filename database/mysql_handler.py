import os
import mysql.connector
from dotenv import load_dotenv


class MySQLHandler:
    def __init__(self):
        # Load environment variables
        env_path = os.path.join(os.path.dirname(__file__), '../config/.env')
        load_dotenv(env_path)

        # Read MySQL credentials from .env
        self.host = os.getenv("MYSQL_HOST")
        self.port = os.getenv("MYSQL_PORT")
        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.database = os.getenv("MYSQL_DATABASE")

        # Ensure credentials are set
        if not all([self.host, self.port, self.user, self.password, self.database]):
            raise ValueError("MySQL credentials are missing. Check your .env file.")

        # Connect to MySQL
        self.conn = None
        self.connect()

    def connect(self):
        """
        Establish a MySQL database connection.
        """
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                port=int(self.port),
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print("✅ MySQL connection established successfully!")
        except mysql.connector.Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            self.conn = None

    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return the result.
        """
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"❌ MySQL query error: {e}")
            return None

    def execute_update(self, query, params=None):
        """
        Execute an INSERT, UPDATE, or DELETE query.
        """
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            print("✅ Query executed successfully!")
        except mysql.connector.Error as e:
            print(f"❌ Error executing update: {e}")
            self.conn.rollback()

    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("🔌 MySQL connection closed.")


# Example Usage
if __name__ == "__main__":
    db_handler = MySQLHandler()

    # Test Query
    result = db_handler.execute_query("SHOW TABLES;")
    print("Tables:", result)

    # Close Connection
    db_handler.close()
