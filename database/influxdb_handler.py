from influxdb import InfluxDBClient


class InfluxDBHandler:
    """
    Handles InfluxDB operations including writing and querying data.
    """

    def __init__(self, config):
        """
        Initialize the InfluxDB client with connection settings.

        :param config: Dictionary containing InfluxDB connection details.
        """
        self.client = InfluxDBClient(
            host=config["host"],
            port=config["port"],
            username=config["user"],
            password=config["password"],
            database=config["database"]
        )

    def write_data(self, measurement, data):
        """
        Write data to an InfluxDB measurement.

        :param measurement: Name of the measurement.
        :param data: Dictionary containing field names and values.
        """
        json_body = [{"measurement": measurement, "fields": data}]
        self.client.write_points(json_body)

    def query_data(self, query):
        """
        Execute a query on InfluxDB.

        :param query: InfluxQL query string.
        :return: Query result.
        """
        return self.client.query(query)

    def close_connection(self):
        """
        Close the connection to InfluxDB.
        """
        self.client.close()
