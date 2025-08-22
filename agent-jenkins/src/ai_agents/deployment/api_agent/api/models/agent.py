"""Agent-related Pydantic models."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Agent types."""
    SALES_ASSISTANT = "sales_assistant"
    CALCULATOR = "calculator"
    JENKINS_AGENT ="jenkinsagent"


class AgentInfo(BaseModel):
    """Basic agent information."""
    id: str = Field(..., description="Agent identifier")
    name: str = Field(..., description="Agent display name")
    type: AgentType = Field(..., description="Agent type")
    description: str = Field(..., description="Agent description")
    version: str = Field(default="1.0.0", description="Agent version")
    status: AgentStatus = Field(default=AgentStatus.IDLE, description="Current status")


class AgentConfig(BaseModel):
    """Agent configuration."""
    workflow: Dict[str, Any] = Field(..., description="Workflow configuration")
    state_schema: Optional[Dict[str, Any]] = Field(None, description="State schema")
    memory: Optional[Dict[str, Any]] = Field(None, description="Memory configuration")
    model: Optional[Dict[str, Any]] = Field(None, description="Model configuration")


class AgentDetailedInfo(AgentInfo):
    """Detailed agent information."""
    config: AgentConfig = Field(..., description="Agent configuration")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class AgentRunRequest(BaseModel):
    """Request to run an agent."""
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for the agent")
    config_override: Optional[Dict[str, Any]] = Field(None, description="Configuration overrides")
    timeout: Optional[int] = Field(None, description="Execution timeout in seconds")


class AgentRunResponse(BaseModel):
    """Response from agent execution."""
    run_id: str = Field(..., description="Unique run identifier")
    agent_id: str = Field(..., description="Agent identifier")
    status: AgentStatus = Field(..., description="Execution status")
    started_at: datetime = Field(..., description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Execution completion time")
    result: Optional[Dict[str, Any]] = Field(None, description="Execution result")
    error: Optional[str] = Field(None, description="Error message if failed")
    logs: List[str] = Field(default_factory=list, description="Execution logs")

 
class AgentStatusResponse(BaseModel):
    """Agent status response."""
    agent_id: str = Field(..., description="Agent identifier")
    run_id: Optional[str] = Field(None, description="Current or last run ID")
    status: AgentStatus = Field(..., description="Current status")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    current_run: Optional[AgentRunResponse] = Field(None, description="Current run details")


class AgentListResponse(BaseModel):
    """Response for listing agents."""
    agents: List[AgentInfo] = Field(..., description="List of available agents")
    total: int = Field(..., description="Total number of agents")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")
