"""Utility functions for handling node types in AI agents' workflows."""

from ai_agents.workflows.core.node_types import NodeType


def get_node_type(node: dict) -> str:
    """
    Retrieves the type of a node from the given dictionary.

    Args:
        node (dict): The node dictionary containing node attributes.

    Returns:
        str: The value associated with the "type" key in the node dictionary.
             If "type" is not present, returns NodeType.FUNCTION as the default.
    """
    return node.get("type", NodeType.FUNCTION)
