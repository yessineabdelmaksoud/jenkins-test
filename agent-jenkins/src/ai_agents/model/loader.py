"""ModelLoader is a utility class for loading language models with configuration.

It supports different model types and configurations, allowing for flexible model initialization.
"""

from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models.base import BaseLanguageModel


class ModelLoader:
    """Utility class for loading language models with configuration."""

    @staticmethod
    def load_model(
        model_type: str, model_id: str, config: Optional[Dict[str, Any]] = None
    ) -> BaseLanguageModel:
        """
        Load a language model with the given configuration.

        Args:
            model_type (str): Type of model ("openai", "huggingface", etc.)
            model_id (str): Model identifier
            config (dict, optional): Model-specific configuration

        Returns:
            BaseLanguageModel: Configured language model

        Raises:
            ValueError: If model type is not supported
        """
        config = config or {}
        model_type = model_type.lower()

        if model_type == "openai":
            # Support for custom OpenAI API base
            openai_api_base = config.get("openai_api_base")
            kwargs = {
                "model": model_id,
                "temperature": config.get("temperature", 0.7),
                "max_tokens": config.get("max_tokens", 1000),
            }
            if openai_api_base:
                kwargs["base_url"] = openai_api_base
            return ChatOpenAI(**kwargs)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
