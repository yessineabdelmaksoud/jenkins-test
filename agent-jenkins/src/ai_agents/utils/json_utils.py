"""JSON handling utilities for AI agents."""

import json
from typing import Any, Dict


def load_json_string(json_str: str) -> Dict[str, Any]:
    """
    Load a JSON string with support for both single and double quoted strings.

    Args:
        json_str (str): The JSON string to parse. Can use either single or double quotes.

    Returns:
        Dict[str, Any]: The parsed JSON data as a dictionary.

    Raises:
        json.JSONDecodeError: If the input string is not valid JSON even after quote conversion.
        ValueError: If the parsed JSON is not a dictionary.
    """
    try:
        # First try to parse as is
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # If fails, try replacing single quotes with double quotes
            fixed_json = json_str.replace("'", '"')
            data = json.loads(fixed_json)

        # Ensure the result is a dictionary
        if not isinstance(data, dict):
            raise ValueError("JSON input must be an object/dictionary")

        return data

    except json.JSONDecodeError as e:
        # Provide helpful error message with examples
        raise json.JSONDecodeError(
            f"Invalid JSON input. Please ensure your input is valid JSON. Examples:\n"
            f'  Using double quotes: {{"input_query": "your question"}}\n'
            f"  Using single quotes: {'input_query': 'your question'}\n"
            f"Your input was: {json_str}\n"
            f"JSON error: {str(e)}",
            e.doc,
            e.pos,
        )
    except ValueError as e:
        raise ValueError(f"{str(e)}. Your input was: {json_str}")
