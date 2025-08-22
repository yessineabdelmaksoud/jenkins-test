"""Graph utilities for building and compiling LangGraph workflows from YAML configurations.

This module provides functions to load workflow configurations from YAML files and build
LangGraph workflow graphs based on those configurations.
"""

import yaml
from typing import Any, Dict
from langgraph.graph import StateGraph
from ai_agents.workflows.core.node_types import NodeType
from ai_agents.workflows.utils.handlers_utils import handler_with_context
from ai_agents.workflows.core.transitions import default_transition


def load_workflow_from_yaml(path: str) -> Dict[str, Any]:
    """
    Load a workflow configuration from a YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed configuration as a dictionary.
    """
    with open(path, "r") as f:
        return yaml.safe_load(f)


def build_graph_from_config(config: Dict[str, Any]) -> Any:
    """
    Build and compile a LangGraph workflow graph from a config dictionary.

    Args:
        config: Workflow configuration dictionary.

    Returns:
        The compiled workflow graph.
    """
    graph = StateGraph()
    nodes = config.get("nodes", {})
    entry_point = config.get("entry_point", "start")

    for node_name, node_data in nodes.items():
        NodeType(node_data.get("type"))
        func_path = node_data.get("function")
        transitions = node_data.get("transitions", {})

        # Import function dynamically
        module_path, func_name = func_path.rsplit(".", 1)
        mod = __import__(module_path, fromlist=[func_name])
        func = getattr(mod, func_name)

        # Use handler_with_context for all nodes
        def node_callable(input_data, func=func):
            return handler_with_context(input_data, func)

        graph.add_node(
            node_name,
            node_callable,
            transitions=transitions if transitions else default_transition,
        )

    graph.set_entry_point(entry_point)
    return graph.compile()
