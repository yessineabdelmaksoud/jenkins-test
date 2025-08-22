"""Transitions module for AI agent workflows.

This module defines the transition logic for moving between states in a workflow.
It includes a default transition handler and can be extended with custom transitions.
"""


def default_transition(output: dict):
    """Sample transition handler — assumes output contains 'next_node'."""
    return output.get("next_node", "end")
