# Maps agent names to agent classes
from typing import Dict, Type
from ai_agents.agents.sales_assistant import SalesAgent
from ai_agents.agents.calculator import CalculatorAgent
from ai_agents.agents.jenkins_agent import JenkinsAgent

# from ai_agents.agents.dev_assistant import DevAssistantAgent  # Uncomment/add as needed

# Add more agent classes here as needed

# Registry that maps agent identifiers to agent classes
AGENT_REGISTRY: Dict[str, Type] = {
    "sales_assistant": SalesAgent,
    "calculator": CalculatorAgent,
    "jenkins_agent": JenkinsAgent
    # "dev_assistant": DevAssistantAgent,
    # "support_bot": SupportBotAgent,
}


def get_agent(agent_name: str, config_path: str = None):
    """
    Retrieve and instantiate the agent class for a given agent name.

    Args:
        agent_name (str): The identifier for the agent.
        config_path (str, optional): Path to the agent config file.

    Returns:
        An instantiated agent object.

    Raises:
        ValueError: If the agent name is not registered.
    """
    if agent_name not in AGENT_REGISTRY:
        raise ValueError(f"Agent '{agent_name}' is not registered.")
    agent_cls = AGENT_REGISTRY[agent_name]
    config = agent_cls.load_config(config_path)
    return agent_cls(config)
