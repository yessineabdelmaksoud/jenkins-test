"""CLI for Running AI Agents."""

import argparse
import sys
from typing import Dict, Any
# from pathlib import Path
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ai_agents.agents.registry import get_agent
from ai_agents.utils.config_loader import load_env_vars
from ai_agents.utils.json_utils import load_json_string
from ai_agents.execution.runner import run_agent


def parse_args():
    """Parse command line arguments for the CLI.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Run an AI agent")
    parser.add_argument("agent", help="Name of the agent to run")
    parser.add_argument("--config", help="Path to agent config file")
    parser.add_argument("--input", help="Input data as JSON string")
    return parser.parse_args()


def main() -> Dict[str, Any]:
    """
    CLI entry point for running agents.

    Returns:
        dict: Agent execution results
    """
    args = parse_args()

    # Load environment variables
    env_vars = load_env_vars()
    if not env_vars.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is required")
        sys.exit(1)

    try:
        # Instantiate the agent using the registry
        agent = get_agent(args.agent, args.config)

        # Parse input data
        input_data = {}
        if args.input:
            input_data = load_json_string(args.input)

        # Execute agent using the shared runner
        results = run_agent(agent, input_data)
        return results
    except Exception as e:
        print(f"Error running agent: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    results = main()
    print(results)
