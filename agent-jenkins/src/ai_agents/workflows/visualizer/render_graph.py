"""Render a workflow graph from a YAML configuration file.

This module provides a function to read a YAML file describing a workflow or a set of nodes and edges,
and generates a Graphviz Digraph object representing the workflow graph.
"""

import yaml
import graphviz


def render_graph_from_yaml(path):
    """
    Renders a workflow graph from a YAML configuration file.

    The function reads a YAML file describing a workflow or a set of nodes and edges,
    and generates a Graphviz Digraph object representing the workflow graph.
    The YAML file can have one of the following structures:
    1. Contains a "workflow" key with "nodes" (list of node dicts) and "edges" (list of edge dicts).
    2. Contains "nodes" (dict of node_name to node data) and optionally "edges" (list of edge dicts).
       If "edges" are not present, transitions defined in each node are used to create edges.
    Each node is rendered with its name and type (default: "function").
    Each edge connects nodes as specified in the configuration.

    Args:
        path (str): Path to the YAML configuration file.

    Returns:
        graphviz.Digraph: A Graphviz Digraph object representing the workflow graph.
    """
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    dot = graphviz.Digraph()

    if "workflow" in config:
        workflow = config["workflow"]
        nodes = workflow.get("nodes", [])
        for node in nodes:
            node_name = node["name"]
            node_type = node.get("type", "function")
            dot.node(node_name, label=f"{node_name}\n({node_type})")
        # Draw edges from workflow["edges"]
        for edge in workflow.get("edges", []):
            dot.edge(edge["from"], edge["to"])
    else:
        nodes = config.get("nodes", {})
        for node_name, data in nodes.items():
            node_type = data.get("type", "function")
            dot.node(node_name, label=f"{node_name}\n({node_type})")
        # Draw edges from config["edges"] if present, else fallback to transitions
        edges = config.get("edges")
        if edges:
            for edge in edges:
                dot.edge(edge["from"], edge["to"])
        else:
            for node_name, data in nodes.items():
                for target in data.get("transitions", {}).values():
                    dot.edge(node_name, target)
    return dot


# Place main block at the end so function is defined
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python render_graph.py <path_to_workflow_yaml>")
        exit(1)
    graph_path = sys.argv[1]
    graph = render_graph_from_yaml(graph_path)
    graph.render("workflow_graph", format="png", cleanup=True)
