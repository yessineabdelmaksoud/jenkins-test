"""Base Memory Class.

This module defines the abstract base class for agent memory implementations.

It provides methods for storing, retrieving, searching, and clearing memory.
Subclasses must implement these methods to provide specific memory functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseMemory(ABC):
    """Abstract base class for agent memory implementations."""

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        """
        Store a value in memory.

        Args:
            key (str): The key to store the value under
            value (Any): The value to store
        """
        pass

    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from memory.

        Args:
            key (str): The key to retrieve

        Returns:
            Optional[Any]: The stored value, or None if not found
        """
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search memory for relevant items.

        Args:
            query (str): Search query
            limit (int): Max results to return

        Returns:
            List[Dict]: List of matching items with their metadata
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all stored memory."""
        pass
