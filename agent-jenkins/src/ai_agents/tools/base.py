"""BaseTool is an abstract base class for all tools that can be used by agents.

It defines the interface that all tools must implement, including methods for initialization,
execution, and metadata retrieval.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """Abstract base class for all tools that can be used by agents."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the tool with optional configuration.

        Args:
            config (dict, optional): Tool-specific configuration
        """
        self.config = config or {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the unique name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Returns a description of what the tool does."""
        pass

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool's functionality.

        Args:
            input_data (dict): Tool-specific input parameters

        Returns:
            dict: Tool execution results
        """
        pass
