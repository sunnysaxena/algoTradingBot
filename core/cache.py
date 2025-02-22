import time


class Cache:
    """
    A simple in-memory cache for storing frequently accessed data.
    """

    def __init__(self, expiration_time=60):
        """
        Initialize the cache with an expiration time.

        :param expiration_time: Time (in seconds) before cache items expire.
        """
        self.cache = {}
        self.expiration_time = expiration_time

    def set(self, key, value):
        """
        Store an item in the cache.

        :param key: Unique identifier for the cache item.
        :param value: Data to be stored in the cache.
        """
        self.cache[key] = (value, time.time())

    def get(self, key):
        """
        Retrieve an item from the cache.

        :param key: Unique identifier for the cache item.
        :return: Cached value or None if expired or not found.
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.expiration_time:
                return value
            else:
                del self.cache[key]  # Remove expired item
        return None

    def invalidate(self, key):
        """
        Remove an item from the cache.

        :param key: Unique identifier for the cache item.
        """
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """
        Clear all cache entries.
        """
        self.cache.clear()
