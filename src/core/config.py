"""
Core configuration management for LinkedIn Outreach Automation.
Handles environment variables, settings validation, and configuration access.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field, validator
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Application Info
    app_name: str = Field(default="LinkedIn Outreach Automation", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    
    # LinkedIn Credentials
    linkedin_email: Optional[str] = Field(default=None, env="LINKEDIN_EMAIL")
    linkedin_password: Optional[str] = Field(default=None, env="LINKEDIN_PASSWORD")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///data/linkedin_outreach.db", env="DATABASE_URL")
    
    # Automation Limits
    max_connection_requests_per_day: int = Field(default=20, env="MAX_CONNECTION_REQUESTS_PER_DAY")
    max_messages_per_day: int = Field(default=15, env="MAX_MESSAGES_PER_DAY")
    delay_between_actions_min: int = Field(default=30, env="DELAY_BETWEEN_ACTIONS_MIN")
    delay_between_actions_max: int = Field(default=120, env="DELAY_BETWEEN_ACTIONS_MAX")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/linkedin_automation.log", env="LOG_FILE")
    
    # Security Settings
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    headless_browser: bool = Field(default=True, env="HEADLESS_BROWSER")
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @validator("max_connection_requests_per_day")
    def validate_connection_requests_limit(cls, v):
        """Validate connection requests limit."""
        if v < 1 or v > 100:
            raise ValueError("Daily connection requests must be between 1 and 100")
        return v
    
    @validator("max_messages_per_day")
    def validate_messages_limit(cls, v):
        """Validate messages limit."""
        if v < 1 or v > 50:
            raise ValueError("Daily messages must be between 1 and 50")
        return v

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


def load_settings() -> Settings:
    """Load and validate application settings."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Create and validate settings
    settings = Settings()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)
    
    return settings


# Global settings instance
settings = load_settings()