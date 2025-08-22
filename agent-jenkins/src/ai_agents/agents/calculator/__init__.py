"""CalculatorAgent implementation for simple mathematical operations."""

import os
from ai_agents.agents.workflow_agent import WorkflowAgent
from . import handlers
from langgraph.graph import StateGraph
from typing import Any, Dict, Optional


class CalculatorAgent(WorkflowAgent):
    """
    CalculatorAgent is a simple agent for mathematical calculations.
    
    It performs basic arithmetic operations without requiring OpenAI API.
    This agent demonstrates a simple workflow that can work offline.
    """

    default_config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

    def __init__(self, config: Dict[str, Any], config_path: Optional[str] = None):
        """
        Initializes a CalculatorAgent instance with the given configuration.

        Args:
            config (Dict[str, Any]): The configuration dictionary for the CalculatorAgent.
            config_path (Optional[str], optional): The path to the configuration file. Defaults to None.
        """
        self.default_config_path = config_path or self.default_config_path
        super().__init__(config)

    @property
    def handler_module(self):
        """
        Returns the handlers module for the calculator agent.

        Returns:
            module: The handlers module from ai_agents.agents.calculator.
        """
        return handlers

    @property
    def prompt_dir(self):
        """
        Returns the absolute path to the 'prompts' directory for the calculator agent.

        Returns:
            str: The absolute path to the 'calculator/prompts' directory.
        """
        return os.path.join(os.path.dirname(__file__), "prompts")

    def build_agent(self) -> StateGraph:
        """
        Build and return the workflow graph for the calculator agent.

        Returns:
            StateGraph: The agent's workflow graph implementation that defines its behavior
        """
        return self._build_workflow_graph(
            self.config, self.handler_module, self.prompt_dir
        )
