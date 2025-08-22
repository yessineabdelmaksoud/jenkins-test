"""Configuration settings for the API."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Host to bind the server")
    PORT: int = Field(default=8000, description="Port to bind the server")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    # CORS settings
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"],
        description="Allowed hosts for CORS"
    )

    # API settings
    API_PREFIX: str = Field(default="/api", description="API prefix")

    # Agent settings
    AGENTS_CONFIG_DIR: str = Field(
        default="src/ai_agents/agents",
        description="Directory containing agent configurations"
    )

    # OpenAI API settings
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key for language model access"
    )

    # OpenRouter API settings (alternative to OpenAI)
    OPENROUTER_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenRouter API key for language model access"
    )

    OPENAI_API_BASE: Optional[str] = Field(
        default=None,
        description="Custom OpenAI API base URL"
    )

    OPENROUTER_BASE_URL: Optional[str] = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL"
    )

    # Jenkins settings
    JENKINS_URL: Optional[str] = Field(
        default=None,
        description="Jenkins server URL"
    )

    JENKINS_USER: Optional[str] = Field(
        default=None,
        description="Jenkins username for API access"
    )

    JENKINS_TOKEN: Optional[str] = Field(
        default=None,
        description="Jenkins API token"
    )

    JENKINS_SANITIZE_LOGS: str = Field(
        default="true",
        description="Enable log sanitization for security"
    )

    JENKINS_ENABLE_ADVANCED_PII: str = Field(
        default="false",
        description="Enable advanced PII detection"
    )

    # Email notification settings
    EMAIL_SENDER: Optional[str] = Field(
        default=None,
        description="Email address for sending notifications"
    )

    EMAIL_PASSWORD: Optional[str] = Field(
        default=None,
        description="Email password or app password"
    )

    EMAIL_TO: Optional[str] = Field(
        default=None,
        description="Default recipient email address"
    )

    SMTP_HOST: str = Field(
        default="smtp.gmail.com",
        description="SMTP server host"
    )

    SMTP_PORT: int = Field(
        default=587,
        description="SMTP server port"
    )

    # Slack notification settings
    SLACK_WEBHOOK_URL: Optional[str] = Field(
        default=None,
        description="Slack webhook URL for notifications"
    )

    # Execution settings
    MAX_EXECUTION_TIME: int = Field(
        default=300,
        description="Maximum execution time for agents in seconds"
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True
        # Allow extra fields to be more flexible with environment variables
        extra = "allow"

 
# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
