"""
Integration script for YouTube video downloading using both yt-dlp and Playwright methods.

This script combines the existing YouTube API functionality from yt_utils.py
with the new Playwright-based downloading capability.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

from .yt_utils import get_latest_video_id, download_youtube_live
from .playwright_yt_downloader import YouTubePlaywrightDownloader, download_youtube_video_with_playwright
from .playwright_config import load_config

logger = logging.getLogger(__name__)


class YouTubeDownloadManager:
    """
    Manager class that provides multiple download methods for YouTube videos.
    
    This class can use either:
    1. yt-dlp (existing method)
    2. Playwright automation (new method)
    """
    
    def __init__(self, 
                 use_playwright: bool = False,
                 config: Optional[Any] = None):
        """
        Initialize the download manager.
        
        Args:
            use_playwright: Whether to use Playwright method by default
            config: Configuration object, will load default if None
        """
        self.use_playwright = use_playwright
        self.config = config or load_config()
        
        # Validate configuration if using Playwright
        if self.use_playwright and not self.config.validate():
            raise ValueError("Invalid configuration for Playwright method")
    
    def get_latest_video_from_channel(self, 
                                    channel_id: Optional[str] = None,
                                    device_name: Optional[str] = None,
                                    playlist_id: Optional[str] = None) -> Optional[str]:
        """
        Get the latest video ID from a channel using the existing API method.
        
        Args:
            channel_id: YouTube channel ID
            device_name: Device name to filter playlists
            playlist_id: Specific playlist ID
            
        Returns:
            Optional[str]: Latest video ID or None if not found
        """
        try:
            channel_id = channel_id or self.config.default_channel_id
            return get_latest_video_id(
                channel_id=channel_id,
                device_name=device_name,
                playlist_id=playlist_id
            )
        except Exception as e:
            logger.error(f"Error getting latest video ID: {e}")
            return None
    
    def download_video_ytdlp(self, video_id: str) -> bool:
        """
        Download video using yt-dlp method (existing implementation).
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            bool: True if download successful
        """
        try:
            download_youtube_live(video_id)
            return True
        except Exception as e:
            logger.error(f"Error downloading with yt-dlp: {e}")
            return False
    
    def download_video_playwright(self, 
                                video_id: str,
                                channel_id: Optional[str] = None) -> Optional[str]:
        """
        Download video using Playwright method with YouTube Studio.
        
        Args:
            video_id: YouTube video ID
            channel_id: YouTube channel ID (optional, helps with navigation)
            
        Returns:
            Optional[str]: Path to downloaded file or None if failed
        """
        try:            
            return download_youtube_video_with_playwright(
                video_id=video_id,
                email=self.config.google_email,
                password=self.config.google_password,
                channel_id=channel_id,
                headless=self.config.headless
            )
        except Exception as e:
            logger.error(f"Error downloading with Playwright: {e}")
            return None
    
    def download_video(self, 
                      video_id: str,
                      method: Optional[str] = None,
                      channel_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Download video using specified or default method.
        
        Args:
            video_id: YouTube video ID
            method: Download method ('ytdlp' or 'playwright'), uses default if None
            channel_id: YouTube channel ID (only for Playwright method)
            
        Returns:
            Dict[str, Any]: Download result with status and file path
        """
        # Determine method
        use_playwright = method == 'playwright' if method else self.use_playwright
        
        result = {
            'video_id': video_id,
            'method': 'playwright' if use_playwright else 'ytdlp',
            'success': False,
            'file_path': None,
            'error': None
        }
        
        try:
            if use_playwright:
                file_path = self.download_video_playwright(video_id, channel_id)
                if file_path:
                    result['success'] = True
                    result['file_path'] = file_path
                else:
                    result['error'] = 'Playwright download failed'
            else:
                success = self.download_video_ytdlp(video_id)
                result['success'] = success
                if not success:
                    result['error'] = 'yt-dlp download failed'
                    
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error in download_video: {e}")
        
        return result
    
    def download_latest_from_channel(self, 
                                   channel_id: Optional[str] = None,
                                   device_name: Optional[str] = None,
                                   playlist_id: Optional[str] = None,
                                   method: Optional[str] = None) -> Dict[str, Any]:
        """
        Download the latest video from a channel.
        
        Args:
            channel_id: YouTube channel ID
            device_name: Device name to filter playlists
            playlist_id: Specific playlist ID
            method: Download method ('ytdlp' or 'playwright')
            
        Returns:
            Dict[str, Any]: Download result
        """
        # Get latest video ID
        video_id = self.get_latest_video_from_channel(
            channel_id=channel_id,
            device_name=device_name,
            playlist_id=playlist_id
        )
        
        if not video_id:
            return {
                'success': False,
                'error': 'Could not find latest video ID',
                'video_id': None
            }
        
        # Download the video
        return self.download_video(video_id, method, channel_id)
    
    def download_multiple_videos(self, 
                               video_ids: List[str],
                               method: Optional[str] = None,
                               channel_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Download multiple videos.
        
        Args:
            video_ids: List of YouTube video IDs
            method: Download method ('ytdlp' or 'playwright')
            channel_id: YouTube channel ID (for Playwright method)
            
        Returns:
            Dict[str, Dict[str, Any]]: Results for each video
        """
        results = {}
        
        for video_id in video_ids:
            logger.info(f"Downloading video {video_id} ({len(results)+1}/{len(video_ids)})")
            results[video_id] = self.download_video(video_id, method, channel_id)
        
        return results


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download YouTube videos using yt-dlp or Playwright')
    parser.add_argument('--video-id', help='Specific video ID to download')
    parser.add_argument('--channel-id', help='Channel ID to get latest video from')
    parser.add_argument('--device-name', help='Device name to filter playlists')
    parser.add_argument('--playlist-id', help='Specific playlist ID')
    parser.add_argument('--method', choices=['ytdlp', 'playwright'], 
                       help='Download method (default: ytdlp)')
    parser.add_argument('--use-playwright', action='store_true', 
                       help='Use Playwright by default')
    
    args = parser.parse_args()
    
    # Initialize download manager
    try:
        manager = YouTubeDownloadManager(use_playwright=args.use_playwright)
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set GOOGLE_EMAIL and GOOGLE_PASSWORD environment variables for Playwright")
        return 1
    
    # Download video
    if args.video_id:
        # Download specific video
        result = manager.download_video(
            video_id=args.video_id,
            method=args.method,
            channel_id=args.channel_id
        )
    else:
        # Download latest from channel
        result = manager.download_latest_from_channel(
            channel_id=args.channel_id,
            device_name=args.device_name,
            playlist_id=args.playlist_id,
            method=args.method
        )
    
    # Print result
    if result['success']:
        print(f"✓ Successfully downloaded video {result.get('video_id', 'unknown')}")
        if result.get('file_path'):
            print(f"  File: {result['file_path']}")
        print(f"  Method: {result.get('method', 'unknown')}")
    else:
        print(f"✗ Download failed: {result.get('error', 'Unknown error')}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())