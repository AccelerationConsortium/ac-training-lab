"""
Video editing and YouTube utilities module.

This module provides utilities for YouTube video downloading and processing,
including both traditional yt-dlp methods and new Playwright-based automation.
"""

# Import main classes and functions for easy access
from .yt_utils import get_latest_video_id, download_youtube_live
from .playwright_yt_downloader import (
    YouTubePlaywrightDownloader,
    download_youtube_video_with_playwright
)
from .playwright_config import PlaywrightYTConfig, load_config
from .integrated_downloader import YouTubeDownloadManager

__all__ = [
    # Original yt-dlp functionality
    'get_latest_video_id',
    'download_youtube_live',
    
    # Playwright functionality
    'YouTubePlaywrightDownloader',
    'download_youtube_video_with_playwright',
    'PlaywrightYTConfig',
    'load_config',
    
    # Integrated functionality
    'YouTubeDownloadManager',
]