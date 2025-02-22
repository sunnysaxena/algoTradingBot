class DatabaseOperations:
    """
    Handles CRUD (Create, Read, Update, Delete) operations for MySQL, InfluxDB, and TimescaleDB.
    """

    def __init__(self, db_connection):
        """
        Initialize with a database connection instance.

        :param db_connection: An instance of DatabaseConnection.
        """
        self.db_connection = db_connection

    def insert_mysql(self, table, data):
        """
        Insert data into a MySQL table.

        :param table: Name of the MySQL table.
        :param data: Dictionary containing column names and values.
        """
        conn = self.db_connection.mysql_conn
        cursor = conn.cursor()
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        cursor.close()

    def fetch_mysql(self, table, condition="1=1"):
        """
        Fetch data from a MySQL table.

        :param table: Name of the MySQL table.
        :param condition: SQL WHERE condition as a string.
        :return: List of tuples containing query results.
        """
        conn = self.db_connection.mysql_conn
        cursor = conn.cursor()
        query = f"SELECT * FROM {table} WHERE {condition}"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def insert_influxdb(self, measurement, data):
        """
        Insert data into an InfluxDB measurement.

        :param measurement: Name of the InfluxDB measurement.
        :param data: Dictionary containing field names and values.
        """
        client = self.db_connection.influx_client
        json_body = [{"measurement": measurement, "fields": data}]
        client.write_points(json_body)

    def fetch_influxdb(self, query):
        """
        Fetch data from InfluxDB.

        :param query: InfluxQL query string.
        :return: Query result.
        """
        client = self.db_connection.influx_client
        return client.query(query)

    def insert_timescaledb(self, table, data):
        """
        Insert data into a TimescaleDB table.

        :param table: Name of the TimescaleDB table.
        :param data: Dictionary containing column names and values.
        """
        conn = self.db_connection.timescale_conn
        cursor = conn.cursor()
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        cursor.close()

    def fetch_timescaledb(self, table, condition="1=1"):
        """
        Fetch data from a TimescaleDB table.

        :param table: Name of the TimescaleDB table.
        :param condition: SQL WHERE condition as a string.
        :return: List of tuples containing query results.
        """
        conn = self.db_connection.timescale_conn
        cursor = conn.cursor()
        query = f"SELECT * FROM {table} WHERE {condition}"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
