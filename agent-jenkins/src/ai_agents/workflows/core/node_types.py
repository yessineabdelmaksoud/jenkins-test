"""Node type definitions for LangGraph workflows."""

from enum import Enum


class NodeType(str, Enum):
    """Enumeration of possible node types in a workflow."""

    FUNCTION = "function"
    TOOL = "tool"
    DECISION = "decision"
    ENTRY = "entry"
    EXIT = "exit"
