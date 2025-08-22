"""Logging configuration for the API."""

import logging
import sys
from typing import Optional
from .config import get_settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """Setup logging configuration."""
    settings = get_settings()
    level = log_level or settings.LOG_LEVEL
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    ) 
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("ai_agents").setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
