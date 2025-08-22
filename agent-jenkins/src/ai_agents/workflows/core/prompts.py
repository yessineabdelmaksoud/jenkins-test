"""Prompt utilities for LangGraph workflows."""

import os
import string
from typing import Optional


def load_prompt_template(prompt_dir: str, handler_name: str) -> Optional[str]:
    """
    Load a prompt template file for a given handler from the specified directory.

    Returns the template string or None if not found.
    """
    template_path = os.path.join(prompt_dir, f"{handler_name}.tpl")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def render_prompt(template: str, state: dict) -> str:
    """Render a prompt template using the state dict (f-string style)."""
    return string.Template(template).safe_substitute(state)
