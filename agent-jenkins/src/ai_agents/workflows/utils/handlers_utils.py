"""Utility functions for handling workflow handlers in AI agents.

This module provides functions to resolve handlers, wrap them with context, and manage prompts.
It is used to dynamically build and execute workflows in AI agents.
"""

from typing import Any, Callable, Optional
from ai_agents.workflows.utils.prompts_utils import render_prompt
import inspect


def resolve_handler(handler_name, local_handlers, core_handlers):
    """Try to get the handler from local_handlers, else from core_handlers."""
    handler_fn = getattr(local_handlers, handler_name, None)
    if handler_fn is None:
        handler_fn = getattr(core_handlers, handler_name)
    return handler_fn


def handler_with_context(
    state: dict,
    handler_fn: Callable,
    model: Optional[Any] = None,
    tools: Optional[Any] = None,
    memory: Optional[Any] = None,
    prompt_template: Optional[str] = None,
    prompt_constructor: Optional[Callable] = None,
    node_type: Optional[str] = None,
) -> Any:
    """
    Wraps a handler function, providing it with model, tools, memory, and a prompt.

    If a prompt_constructor is provided, it is called as prompt_constructor(state, prompt_template) and used to generate the prompt.
    Otherwise, if a prompt_template is provided, it is rendered with the state.
    The handler is called with the prompt if it accepts it, otherwise without.
    """
    prompt = None
    if prompt_constructor:
        prompt = prompt_constructor(state, prompt_template)
    elif prompt_template:
        prompt = render_prompt(prompt_template, state)

    # Build the argument dict, including node_type
    kwargs = {
        "state": state,
        "model": model,
        "tools": tools,
        "memory": memory,
        "prompt": prompt,
        "node_type": node_type,
    }

    # Inspect the handler's signature and filter kwargs
    sig = inspect.signature(handler_fn)
    accepted_args = set(sig.parameters.keys())
    # If handler accepts **kwargs, pass all
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        return handler_fn(**kwargs)
    # Otherwise, only pass accepted args
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in accepted_args}
    return handler_fn(**filtered_kwargs)


# Example usage:
# from ai_agents.workflows.utils.node_types_utils import get_node_type
# node_type = get_node_type(node)
# handler_with_context(..., node_type=node_type)
