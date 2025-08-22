"""VectorStoreMemory is a memory implementation that uses a vector store for semantic retrieval.

It allows storing, retrieving, and searching vectors along with their metadata.
It provides methods to store, retrieve, search, and clear memory using a vector store.
"""

from ai_agents.memory.base import BaseMemory
from typing import Any, Dict, List, Optional


class VectorStoreMemory(BaseMemory):
    """VectorStoreMemory is a memory implementation that uses a vector store for semantic retrieval.

    It allows storing, retrieving, and searching vectors along with their metadata.
    It provides methods to store, retrieve, search, and clear memory using a vector store.
    """

    def __init__(
        self, embedding_model: str = "openai", store_path: str = "./vector_store"
    ):
        """Initialize VectorStoreMemory with embedding model and store path.

        Args:
            embedding_model (str): The model used for generating embeddings.
            store_path (str): Path to the vector store directory.
        """
        self.embedding_model = embedding_model
        self.store_path = store_path
        self.vectors: List[
            Dict[str, Any]
        ] = []  # In-memory store: [{"id": ..., "vector": ..., "meta": ...}]

    def store(self, key: str, value: Any) -> None:
        """Store a value in the vector store memory.

        Args:
            key (str): The key to store the value under.
            value (Any): The value to store, expected to be a dict with 'vector' and 'meta'.
        """
        # Assume value is a dict with 'vector' and 'meta'
        self.vectors.append({"id": key, **value})

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from the vector store memory.

        Args:
            key (str): The key to retrieve.
        """
        for item in self.vectors:
            if item["id"] == key:
                return item
        return None

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory for relevant items.

        Args:
            query (str): Search query
            limit (int): Max results to return
        """
        # Dummy search: return first N items (replace with real vector search in production)
        return self.vectors[:limit]

    def clear(self) -> None:
        """Clear all stored memory in the vector store."""
        self.vectors.clear()
