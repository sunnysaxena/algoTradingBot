import requests
import logging
from utils.logger import get_logger

logger = get_logger(__name__)

class RequestHandler:
    def __init__(self, base_url, headers=None, timeout=10):
        """
        Initializes the request handler.

        :param base_url: Base URL for API requests.
        :param headers: Default headers for requests.
        :param timeout: Timeout for requests.
        """
        self.base_url = base_url
        self.headers = headers if headers else {}
        self.timeout = timeout

    def send_request(self, endpoint, method="GET", params=None, data=None, headers=None):
        """
        Sends an HTTP request and returns the response.

        :param endpoint: API endpoint (appended to base_url).
        :param method: HTTP method (GET, POST, PUT, DELETE).
        :param params: Query parameters.
        :param data: Request payload.
        :param headers: Custom headers (if any).
        :return: JSON response or error.
        """
        url = f"{self.base_url}{endpoint}"
        headers = headers or self.headers

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}

# Example Usage
if __name__ == "__main__":
    API_URL = "https://api.example.com"
    handler = RequestHandler(base_url=API_URL, headers={"Authorization": "Bearer YOUR_TOKEN"})

    response = handler.send_request("/market/data", method="GET", params={"symbol": "AAPL"})
    print(response)
