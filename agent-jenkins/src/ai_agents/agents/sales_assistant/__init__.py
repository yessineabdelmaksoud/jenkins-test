"""SalesAgent implementation for LangGraph agents."""

import os
from ai_agents.agents.workflow_agent import WorkflowAgent
from . import handlers
from langgraph.graph import StateGraph
from typing import Any, Dict, Optional
 

class SalesAgent(WorkflowAgent):
    """
    SalesAgent is a LangGraph-based agent for sales-related tasks.

    It supports configurable workflows, tools, memory, and LLM model.
    The memory backend is available as self.memory and is passed to all handlers.
    """

    default_config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

    def __init__(self, config: Dict[str, Any], config_path: Optional[str] = None):
        """
        Initializes a SalesAgent instance with the given configuration and config path.

        Args:
            config (Dict[str, Any]): The configuration dictionary for the SalesAgent.
            config_path (Optional[str], optional): The path to the configuration file. Defaults to None.
        """
        self.default_config_path = config_path or self.default_config_path
        super().__init__(config)

    @property
    def handler_module(self):
        """
        Imports and returns the handlers module from the sales_assistant package.

        Returns:
            module: The handlers module from ai_agents.agents.sales_assistant.
        """
        return handlers

    @property
    def prompt_dir(self):
        """
        Returns the absolute path to the 'prompts' directory located within the 'sales_assistant' subfolder relative to the current file's directory.

        Returns:
            str: The absolute path to the 'sales_assistant/prompts' directory.
        """
        return os.path.join(os.path.dirname(__file__), "prompts")

    def build_agent(self) -> StateGraph:
        """
        Build and return the workflow graph for the sales agent.

        Returns:
            StateGraph: The agent's workflow graph implementation that defines its behavior
        """
        return self._build_workflow_graph(
            self.config, self.handler_module, self.prompt_dir
        )
