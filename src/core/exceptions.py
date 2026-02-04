"""
Core exceptions for LinkedIn Outreach Automation.
Defines custom exceptions with proper error handling and context.
"""

from typing import Any, Dict, Optional


class LinkedInAutomationError(Exception):
    """Base exception for all LinkedIn automation errors."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}
    
    def __str__(self) -> str:
        if self.context:
            return f"{self.message} | Context: {self.context}"
        return self.message


class AuthenticationError(LinkedInAutomationError):
    """Raised when LinkedIn authentication fails."""
    pass


class RateLimitError(LinkedInAutomationError):
    """Raised when LinkedIn rate limits are hit."""
    pass


class ProspectNotFoundError(LinkedInAutomationError):
    """Raised when a prospect is not found."""
    pass


class DatabaseError(LinkedInAutomationError):
    """Raised when database operations fail."""
    pass


class ConfigurationError(LinkedInAutomationError):
    """Raised when configuration is invalid or missing."""
    pass


class AutomationError(LinkedInAutomationError):
    """Raised when automation actions fail."""
    pass


class NetworkError(LinkedInAutomationError):
    """Raised when network operations fail."""
    pass


class ValidationError(LinkedInAutomationError):
    """Raised when data validation fails."""
    pass