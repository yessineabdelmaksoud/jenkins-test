"""Base interface for all agent types in the system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from langgraph.graph import StateGraph
from langchain.agents import AgentExecutor
from ai_agents.utils.config_loader import load_yaml_config, load_env_vars


class AgentBase(ABC):
    """Base interface for all agent types.

    This class provides a common interface that all agent types must implement,
    regardless of their internal implementation (workflow-based, LangChain, custom).

    Attributes:
        default_config_path: Default path to the agent's configuration file.

    Methods:
        run: Executes the agent with the provided input data.
        build_agent: Creates and returns the agent's implementation.
        load_config: Loads agent configuration from a file.
    """

    default_config_path: Optional[str] = None

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with the provided input data.

        Args:
            input_data: Initial input state for the agent.

        Returns:
            The final state after agent execution.

        Raises:
            ValueError: If input_data is invalid or missing required fields.
        """
        pass

    @abstractmethod
    def build_agent(self) -> Union[StateGraph, AgentExecutor, Any]:
        """Build and return the agent implementation.

        Returns:
            The agent implementation - either a StateGraph, AgentExecutor, or custom type.
        """
        pass

    def build_model(self) -> Any:
        """Build the language model based on configuration.

        Returns:
            The configured language model instance.
        """
        model_cfg = self.config.get("model", {})
        if not model_cfg:
            return None

        from ai_agents.model.loader import ModelLoader

        config_dict = dict(model_cfg.get("config", {}))
        if "openai_api_key" not in config_dict:
            env_vars = load_env_vars()
            if env_vars.get("OPENAI_API_KEY"):
                config_dict["openai_api_key"] = env_vars["OPENAI_API_KEY"]

        return ModelLoader.load_model(
            model_type=model_cfg.get("type", "openai"),
            model_id=model_cfg.get("model_id", "gpt-3.5-turbo"),
            config=config_dict,
        )

    @classmethod
    def load_config(cls, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load agent configuration from a file.

        Args:
            config_path: Path to config file. Uses default_config_path if not provided.

        Returns:
            The loaded configuration dictionary.

        Raises:
            ValueError: If no config path is provided and no default exists.
            FileNotFoundError: If the config file does not exist.
        """
        path = config_path or cls.default_config_path
        if not path:
            raise ValueError("No config path provided and no default_config_path set")
        return load_yaml_config(path)
