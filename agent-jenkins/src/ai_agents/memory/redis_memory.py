"""Redis Memory Module.

This module implements a Redis-based memory backend for AI agents.
It provides methods to store, retrieve, search, and clear memory using Redis.
"""

import redis
from ai_agents.memory.base import BaseMemory
from typing import Any, Optional


class RedisMemory(BaseMemory):
    """RedisMemory class for managing agent memory using Redis.

    It provides methods to store, retrieve, search, and clear memory.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        namespace: str = "agent",
    ):
        """Initialize RedisMemory with connection parameters.

        Args:
            host (str): Redis server host.
            port (int): Redis server port
            db (int): Redis database index.
            namespace (str): Namespace for keys to avoid collisions.
        """
        self.namespace = namespace
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def _key(self, key: str) -> str:
        """Generate a namespaced key for Redis.

        Args:
            key (str): The original key.

        Returns:
            str: Namespaced key.
        """
        return f"{self.namespace}:{key}"

    def store(self, key: str, value: Any) -> None:
        """Store a value in Redis memory.

        Args:
            key (str): The key to store the value under.
            value (Any): The value to store.
        """
        self.client.set(self._key(key), value)

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from Redis memory.

        Args:
            key (str): The key to retrieve.
        """
        return self.client.get(self._key(key))

    def search(self, query: str, limit: int = 5):
        """Search for keys matching a query string.

        Args:
            query (str): The search query
            limit (int): Max results to return
            Returns:
        """
        # Simple search: return keys containing the query string
        pattern = f"*{query}*"
        keys = self.client.keys(self._key(pattern))
        results = []
        for k in keys[:limit]:
            results.append({"key": k, "value": self.client.get(k)})
        return results

    def clear(self) -> None:
        """Clear all stored memory in Redis."""
        keys = self.client.keys(self._key("*"))
        if keys:
            self.client.delete(*keys)
