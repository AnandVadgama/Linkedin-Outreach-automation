"""
Core package initialization.
"""

from .config import settings
from .exceptions import *
from .logging import configure_logging, get_logger

# Initialize logging on import
configure_logging()

__all__ = [
    "settings",
    "configure_logging",
    "get_logger",
    "LinkedInAutomationError",
    "AuthenticationError",
    "RateLimitError",
    "ProspectNotFoundError",
    "DatabaseError",
    "ConfigurationError",
    "AutomationError",
    "NetworkError",
    "ValidationError"
]