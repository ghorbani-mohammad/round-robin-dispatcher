import threading
from typing import Dict, Any, Optional


class RequestCache:
    """
    Simple in-memory cache for storing request_ids.
    Thread-safe implementation for use in FastAPI background tasks.
    """

    def __init__(self):
        """Initialize the cache."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def get(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a request from cache.

        Args:
            request_id: The request ID to look up

        Returns:
            Request data if found, None otherwise
        """
        with self.lock:
            return self.cache.get(request_id)

    def set(self, request_id: str, data: Dict[str, Any]) -> None:
        """
        Store a request in cache.

        Args:
            request_id: The request ID
            data: The request data to store
        """
        with self.lock:
            self.cache[request_id] = data


# Global cache instance
request_cache = RequestCache()
