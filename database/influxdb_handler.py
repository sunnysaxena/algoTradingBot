import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient


class InfluxDBHandler:
    def __init__(self):
        # Load the .env file explicitly from config/
        env_path = os.path.join(os.path.dirname(__file__), '../config/.env')
        load_dotenv(env_path)

        # Read InfluxDB credentials from .env
        self.url = os.getenv("INFLUXDB_URL")
        self.org = os.getenv("INFLUXDB_ORG")
        self.bucket = os.getenv("INFLUXDB_BUCKET")
        self.token = os.getenv("INFLUXDB_TOKEN")

        # Ensure credentials are set
        if not all([self.url, self.org, self.bucket, self.token]):
            raise ValueError("InfluxDB credentials are missing. Check your .env file.")

        # Create InfluxDB client
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)

    def query_data(self, query: str):
        """
        Execute an InfluxDB query.
        """
        try:
            query_api = self.client.query_api()
            result = query_api.query(query)
            return result
        except Exception as e:
            print(f"Error querying InfluxDB: {e}")
            return None

    def write_data(self, data):
        """
        Write data to InfluxDB.
        """
        try:
            write_api = self.client.write_api()
            write_api.write(bucket=self.bucket, org=self.org, record=data)
            print("Data written successfully to InfluxDB")
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")

    def close(self):
        """
        Close the InfluxDB connection.
        """
        self.client.close()
        print("InfluxDB connection closed.")


# Example Usage
if __name__ == "__main__":
    influx_handler = InfluxDBHandler()

    # Example Query (modify as needed)
    query = f'from(bucket: "{influx_handler.bucket}") |> range(start: -1h)'
    result = influx_handler.query_data(query)

    if result:
        for table in result:
            for record in table.records:
                print(record.values)

    # Close the connection
    influx_handler.close()
