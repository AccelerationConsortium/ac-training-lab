"""
Configuration for Playwright YouTube downloader.

This file contains lean configuration and credential management
for the Playwright YouTube downloader.
"""

import os
from typing import Optional, Dict, Any


class PlaywrightYTConfig:
    """Simplified configuration class for Playwright YouTube downloader."""
    
    def __init__(self):
        """Initialize configuration with environment variables and defaults."""
        
        # Credentials (should be set as environment variables)
        self.google_email = os.getenv("GOOGLE_EMAIL")
        self.google_password = os.getenv("GOOGLE_PASSWORD")
        
        # Browser settings
        self.headless = os.getenv("YT_HEADLESS", "true").lower() == "true"
        
        # Timeout settings (in milliseconds)
        self.page_timeout = int(os.getenv("YT_PAGE_TIMEOUT", "30000"))
        self.download_timeout = int(os.getenv("YT_DOWNLOAD_TIMEOUT", "300"))  # seconds
        
        # Channel settings
        self.default_channel_id = os.getenv("YT_CHANNEL_ID", "UCHBzCfYpGwoqygH9YNh9A6g")
        
        # Browser user agent
        self.user_agent = os.getenv("YT_USER_AGENT", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
    def validate(self) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            bool: True if configuration is valid
        """
        if not self.google_email:
            print("Error: GOOGLE_EMAIL environment variable not set")
            return False
            
        if not self.google_password:
            print("Error: GOOGLE_PASSWORD environment variable not set")
            return False
            
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict[str, Any]: Configuration as dictionary (excluding sensitive data)
        """
        return {
            "headless": self.headless,
            "page_timeout": self.page_timeout,
            "download_timeout": self.download_timeout,
            "default_channel_id": self.default_channel_id,
            "user_agent": self.user_agent,
            "has_credentials": bool(self.google_email and self.google_password)
        }


# Example environment variables setup (simplified)
EXAMPLE_ENV_VARS = """
# Copy these to your .env file or set as environment variables

# Required credentials
GOOGLE_EMAIL=your-email@gmail.com
GOOGLE_PASSWORD=your-app-password

# Optional settings
YT_HEADLESS=true
YT_PAGE_TIMEOUT=30000
YT_DOWNLOAD_TIMEOUT=300
YT_CHANNEL_ID=UCHBzCfYpGwoqygH9YNh9A6g

# Security note: Use App Passwords for Google accounts with 2FA enabled
# https://support.google.com/accounts/answer/185833
"""


def load_config() -> PlaywrightYTConfig:
    """
    Load configuration from environment variables.
    
    Returns:
        PlaywrightYTConfig: Loaded configuration
    """
    return PlaywrightYTConfig()


def print_example_env():
    """Print example environment variables."""
    print(EXAMPLE_ENV_VARS)


if __name__ == "__main__":
    # Test configuration loading
    config = load_config()
    
    print("Current configuration:")
    for key, value in config.to_dict().items():
        print(f"  {key}: {value}")
    
    if not config.validate():
        print("\nConfiguration validation failed!")
        print("\nExample environment variables:")
        print_example_env()
    else:
        print("\nConfiguration is valid!")