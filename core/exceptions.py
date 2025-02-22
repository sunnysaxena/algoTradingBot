class APIError(Exception):
    """Exception raised for errors in the broker API."""

    def __init__(self, message="Error communicating with broker API"):
        self.message = message
        super().__init__(self.message)


class DatabaseError(Exception):
    """Exception raised for database connection issues."""

    def __init__(self, message="Database connection failed"):
        self.message = message
        super().__init__(self.message)


class OrderExecutionError(Exception):
    """Exception raised when order execution fails."""

    def __init__(self, message="Order execution failed"):
        self.message = message
        super().__init__(self.message)
