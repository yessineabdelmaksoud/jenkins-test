"""Memory Factory Module.

This module provides a factory class to create memory backends based on configuration.
It supports different types of memory implementations such as Redis and Vector Store.
"""

from typing import Optional, Dict
from ai_agents.memory.redis_memory import RedisMemory
from ai_agents.memory.vector_store import VectorStoreMemory


class MemoryFactory:
    """
    Factory to create memory backends based on config.

    Supported types:
    - 'redis': uses Redis for key-value memory
    - 'vector': uses vector store for semantic retrieval
    """

    @staticmethod
    def create(memory_type: str, config: Optional[Dict] = None):
        """
        Creates a memory backend based on the provided type and configuration.

        Args:
            memory_type (str): The type of memory to create (e.g., 'redis', 'vector').
            config (Optional[Dict], optional): The configuration for the memory backend. Defaults to {}.

        Returns:
            The created memory backend instance.
        """
        config = config or {}

        if memory_type == "redis":
            return RedisMemory(
                host=config.get("host", "localhost"),
                port=config.get("port", 6379),
                db=config.get("db", 0),
                namespace=config.get("namespace", "agent"),
            )

        elif memory_type == "vector":
            return VectorStoreMemory(
                embedding_model=config.get("embedding_model", "openai"),
                store_path=config.get("store_path", "./vector_store"),
            )

        else:
            raise ValueError(f"Unsupported memory type: {memory_type}")
