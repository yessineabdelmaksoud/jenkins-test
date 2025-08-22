"""ToolRegistry is a global registry for managing tools available to AI agents.

It allows for registering, retrieving, and listing tools by their names.
Tools must inherit from BaseTool and implement the required methods.
"""

from typing import Dict, Type
from .base import BaseTool
from .search import SearchTool


class ToolRegistry:
    """Global registry for available tools."""

    _tools: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> None:
        """
        Register a new tool class.

        Args:
            tool_class: The tool class to register
        """
        instance = tool_class()
        cls._tools[instance.name] = tool_class

    @classmethod
    def get_tool(cls, name: str) -> Type[BaseTool]:
        """
        Get a tool class by name.

        Args:
            name (str): The name of the tool

        Returns:
            Type[BaseTool]: The tool class

        Raises:
            KeyError: If tool is not found
        """
        if name not in cls._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return cls._tools[name]

    @classmethod
    def list_tools(cls) -> Dict[str, str]:
        """
        List all registered tools and their descriptions.

        Returns:
            dict: Mapping of tool names to descriptions
        """
        return {name: tool_cls().description for name, tool_cls in cls._tools.items()}


# Register built-in tools
ToolRegistry.register(SearchTool)
