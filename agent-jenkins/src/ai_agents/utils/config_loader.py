"""ConfigLoader is a utility for loading configuration files for AI agents.

It supports loading YAML files and provides methods to retrieve agent-specific configurations.
"""

import os
import yaml
from typing import Dict, Any
from dotenv import load_dotenv


def load_yaml_config(path: str) -> Dict[str, Any]:
    """
    Load a YAML config file from the specified path.

    Args:
        path (str): Path to the YAML file.

    Returns:
        dict: Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_env_vars() -> Dict[str, str]:
    """
    Load key environment variables used globally.

    Returns:
        dict: Environment settings.
    """
    load_dotenv()
    keys = ["OPENAI_API_KEY", "REDIS_HOST", "REDIS_PORT"]
    return {key: os.getenv(key, "") for key in keys}
