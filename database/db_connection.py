import mysql.connector
import influxdb
import psycopg2


class DatabaseConnection:
    """
    Handles connections to MySQL, InfluxDB, and TimescaleDB.
    """

    def __init__(self, config):
        """
        Initialize database connections based on the provided configuration.

        :param config: Dictionary containing database connection details.
        """
        self.config = config
        self.mysql_conn = None
        self.influx_client = None
        self.timescale_conn = None

    def connect_mysql(self):
        """
        Establish a connection to the MySQL database.
        """
        self.mysql_conn = mysql.connector.connect(
            host=self.config["mysql"]["host"],
            user=self.config["mysql"]["user"],
            password=self.config["mysql"]["password"],
            database=self.config["mysql"]["database"]
        )

    def connect_influxdb(self):
        """
        Establish a connection to the InfluxDB database.
        """
        self.influx_client = influxdb.InfluxDBClient(
            host=self.config["influxdb"]["host"],
            port=self.config["influxdb"]["port"],
            username=self.config["influxdb"]["user"],
            password=self.config["influxdb"]["password"],
            database=self.config["influxdb"]["database"]
        )

    def connect_timescaledb(self):
        """
        Establish a connection to the TimescaleDB database.
        """
        self.timescale_conn = psycopg2.connect(
            host=self.config["timescaledb"]["host"],
            user=self.config["timescaledb"]["user"],
            password=self.config["timescaledb"]["password"],
            database=self.config["timescaledb"]["database"]
        )

    def close_connections(self):
        """
        Close all active database connections.
        """
        if self.mysql_conn:
            self.mysql_conn.close()
        if self.influx_client:
            self.influx_client.close()
        if self.timescale_conn:
            self.timescale_conn.close()
