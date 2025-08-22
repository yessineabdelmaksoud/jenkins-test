"""Runner for AI Agents.

This module provides a shared runner function to execute AI agents with input data.
It handles the instantiation of agents, execution with input data, and error handling.
"""

from typing import Any, Dict, Optional


def run_agent(
    agent, input_data: Optional[Dict[str, Any]] = None, verbose: bool = False
) -> Dict[str, Any]:
    """
    Shared logic to run an agent with input data and handle errors.

    Args:
        agent: An instance of BaseAgent or compatible agent class
        input_data: Optional dictionary of input data for the agent
        verbose: If True, print detailed error messages
    Returns:
        Dictionary of results from the agent's workflow
    Raises:
        Exception: Propagates any exception from agent execution
    """
    input_data = input_data or {}
    try:
        result = agent.run(input_data)
        return result
    except Exception as e:
        if verbose:
            print(f"[Runner] Error running agent: {e}")
        raise
