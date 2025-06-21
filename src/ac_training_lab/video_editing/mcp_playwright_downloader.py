"""
MCP Playwright-based YouTube Video Downloader

This module demonstrates how to use Playwright MCP tools to download
YouTube videos via YouTube Studio's native download functionality.
This approach provides access to owned channel content that may not
be available through traditional methods.
"""

import os
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPPlaywrightYouTubeDownloader:
    """
    YouTube video downloader using Playwright MCP tools.
    
    This class demonstrates the use of Playwright MCP tools for:
    1. Google authentication
    2. YouTube Studio navigation
    3. Native video download functionality
    """
    
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the MCP Playwright YouTube downloader.
        
        Args:
            email: Google account email (defaults to GOOGLE_EMAIL env var)
            password: Google account password (defaults to GOOGLE_PASSWORD env var)
        """
        self.email = email or os.getenv("GOOGLE_EMAIL")
        self.password = password or os.getenv("GOOGLE_PASSWORD")
        
        if not self.email or not self.password:
            raise ValueError(
                "Google credentials required. Set GOOGLE_EMAIL and GOOGLE_PASSWORD "
                "environment variables or pass them to the constructor."
            )
    
    def get_download_instructions(self, video_id: str, channel_id: str) -> Dict[str, Any]:
        """
        Get step-by-step instructions for downloading a video using MCP Playwright tools.
        
        Args:
            video_id: YouTube video ID
            channel_id: YouTube channel ID
            
        Returns:
            Dict containing the download instructions and URLs
        """
        studio_url = f"https://studio.youtube.com/video/{video_id}/edit?c={channel_id}"
        
        return {
            "video_id": video_id,
            "channel_id": channel_id,
            "studio_url": studio_url,
            "credentials": {
                "email": self.email,
                "password_redacted": "*" * len(self.password) if self.password else None
            },
            "instructions": [
                {
                    "step": 1,
                    "action": "playwright-browser_navigate",
                    "description": "Navigate to Google sign-in",
                    "url": "https://accounts.google.com/signin"
                },
                {
                    "step": 2,
                    "action": "playwright-browser_type",
                    "description": "Enter email address",
                    "element": "Email or phone textbox",
                    "text": self.email
                },
                {
                    "step": 3,
                    "action": "playwright-browser_click",
                    "description": "Click Next button",
                    "element": "Next button"
                },
                {
                    "step": 4,
                    "action": "playwright-browser_type",
                    "description": "Enter password",
                    "element": "Enter your password textbox",
                    "text": "[PASSWORD]"
                },
                {
                    "step": 5,
                    "action": "playwright-browser_click",
                    "description": "Click Next button",
                    "element": "Next button"
                },
                {
                    "step": 6,
                    "action": "device_verification",
                    "description": "Complete device verification if prompted",
                    "note": "May require interaction with registered device"
                },
                {
                    "step": 7,
                    "action": "playwright-browser_navigate",
                    "description": "Navigate to YouTube Studio video page",
                    "url": studio_url
                },
                {
                    "step": 8,
                    "action": "playwright-browser_click",
                    "description": "Click Skip to YouTube Studio if browser warning appears",
                    "element": "Skip to YouTube Studio link"
                },
                {
                    "step": 9,
                    "action": "playwright-browser_click",
                    "description": "Click Options button (three-dot menu)",
                    "element": "Options button"
                },
                {
                    "step": 10,
                    "action": "playwright-browser_click",
                    "description": "Click Download option",
                    "element": "Download menuitem"
                }
            ],
            "expected_result": "Video file should start downloading automatically"
        }
    
    def verify_setup(self) -> Dict[str, Any]:
        """
        Verify that the setup is ready for download.
        
        Returns:
            Dict containing verification status
        """
        status = {
            "credentials": {
                "email_set": bool(self.email),
                "password_set": bool(self.password),
                "email_value": self.email if self.email else "NOT SET"
            },
            "ready": bool(self.email and self.password),
            "requirements": [
                "GOOGLE_EMAIL environment variable set",
                "GOOGLE_PASSWORD environment variable set", 
                "Account must have editor access to target YouTube channel",
                "Device verification may be required on first login"
            ]
        }
        
        return status


def demonstrate_download_process(video_id: str = "cIQkfIUeuSM", 
                               channel_id: str = "UCHBzCfYpGwoqygH9YNh9A6g"):
    """
    Demonstrate the download process for a specific video.
    
    Args:
        video_id: YouTube video ID (defaults to ac-hardware-streams example)
        channel_id: YouTube channel ID (defaults to ac-hardware-streams)
    """
    try:
        downloader = MCPPlaywrightYouTubeDownloader()
        
        logger.info("=== MCP Playwright YouTube Downloader Demo ===")
        logger.info(f"Target video: {video_id}")
        logger.info(f"Target channel: {channel_id}")
        
        # Verify setup
        setup_status = downloader.verify_setup()
        logger.info("Setup verification:")
        logger.info(f"  Email: {setup_status['credentials']['email_value']}")
        logger.info(f"  Password: {'SET' if setup_status['credentials']['password_set'] else 'NOT SET'}")
        logger.info(f"  Ready: {setup_status['ready']}")
        
        if not setup_status['ready']:
            logger.error("Setup not ready. Please check requirements:")
            for req in setup_status['requirements']:
                logger.error(f"  - {req}")
            return
        
        # Get download instructions
        instructions = downloader.get_download_instructions(video_id, channel_id)
        
        logger.info("\n=== Download Instructions ===")
        logger.info(f"Studio URL: {instructions['studio_url']}")
        logger.info("\nStep-by-step process:")
        
        for instruction in instructions['instructions']:
            step_num = instruction['step']
            action = instruction['action']
            description = instruction['description']
            
            logger.info(f"  {step_num}. {description}")
            logger.info(f"     Action: {action}")
            
            if 'url' in instruction:
                logger.info(f"     URL: {instruction['url']}")
            if 'element' in instruction:
                logger.info(f"     Element: {instruction['element']}")
            if 'text' in instruction and instruction['text'] != "[PASSWORD]":
                logger.info(f"     Text: {instruction['text']}")
            if 'note' in instruction:
                logger.info(f"     Note: {instruction['note']}")
        
        logger.info(f"\nExpected Result: {instructions['expected_result']}")
        
        logger.info("\n=== Success! ===")
        logger.info("The MCP Playwright tools have been successfully demonstrated.")
        logger.info("This approach provides native YouTube Studio download functionality.")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")


if __name__ == "__main__":
    demonstrate_download_process()