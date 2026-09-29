"""
Configuration module for ULTRON AI Assistant
Handles loading environment variables and configuration settings
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env from the project folder (Projects\jarvis), no matter where you run from
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Config:
    """Configuration class for ULTRON"""

    def __init__(self):
        # Load NVIDIA API key from environment variable (never hardcode)
        self.nvidia_api_key: Optional[str] = os.getenv('NVIDIA_API_KEY')

        # Model configuration
        self.model_name: str = "nvidia/nemotron-3-super-120b-a12b"

        # Assistant configuration
        self.assistant_name: str = "ULTRON"
        self.user_name: str = "Gopal"

        # API endpoint
        self.api_base_url: str = "https://integrate.api.nvidia.com/v1"

        # Validate configuration on initialization
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate that required configuration is present"""
        if not self.nvidia_api_key:
            # Don't raise exception here to allow graceful degradation
            # In production, this should be handled appropriately
            pass

    def is_configured(self) -> bool:
        """Check if the API key is configured"""
        return bool(self.nvidia_api_key)

    def get_api_headers(self) -> dict:
        """Get headers for API requests"""
        if not self.nvidia_api_key:
            return {}
        return {
            "Authorization": f"Bearer {self.nvidia_api_key}",
            "Content-Type": "application/json"
        }


# Global config instance
config = Config()