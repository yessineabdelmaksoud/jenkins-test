# Batch runner for agents
"""
Batch runner for agents.

This module provides functionality to run an agent over a batch of input data dictionaries,
handling errors gracefully and optionally providing verbose output for debugging.

Functions:
    run_agent_batch(agent, batch_inputs, verbose=False):
        Executes the given agent on each input in batch_inputs.
        Collects results and error information for each run.
"""

from typing import Any, Dict, List
from ai_agents.execution.runner import run_agent


def run_agent_batch(
    agent, batch_inputs: List[Dict[str, Any]], verbose: bool = False
) -> List[Dict[str, Any]]:
    """
    Run an agent on a batch of input data.

    Args:
        agent: An instance of BaseAgent or compatible agent class
        batch_inputs: List of input data dictionaries
        verbose: If True, print detailed error messages for each run
    Returns:
        List of result dictionaries, one per input
    """
    results = []
    for idx, input_data in enumerate(batch_inputs):
        try:
            result = run_agent(agent, input_data, verbose=verbose)
            results.append(result)
        except Exception as e:
            if verbose:
                print(f"[BatchRunner] Error on item {idx}: {e}")
            results.append({"error": str(e), "input": input_data})
    return results
