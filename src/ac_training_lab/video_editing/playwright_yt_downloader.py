"""
Playwright-based YouTube video downloader.

This module provides functionality to automatically download YouTube videos
by logging into a Google account and using YouTube's native download interface.
This is particularly useful for downloading private/unlisted videos from
owned channels that may not be accessible via yt-dlp.
"""

import os
import time
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubePlaywrightDownloader:
    """
    A class to automate YouTube video downloads using Playwright.
    
    This downloader logs into a Google account and uses YouTube's 
    native download functionality to download videos from owned channels.
    """
    
    def __init__(self, 
                 email: str, 
                 password: str, 
                 download_dir: Optional[str] = None,
                 headless: bool = True,
                 timeout: int = 30000):
        """
        Initialize the YouTube Playwright downloader.
        
        Args:
            email: Google account email
            password: Google account password
            download_dir: Directory to save downloads (defaults to current directory/downloads)
            headless: Whether to run browser in headless mode
            timeout: Default timeout for operations in milliseconds
        """
        self.email = email
        self.password = password
        self.download_dir = Path(download_dir) if download_dir else Path.cwd() / "downloads"
        self.headless = headless
        self.timeout = timeout
        
        # Ensure download directory exists
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Browser and page instances
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def start(self):
        """Start the Playwright browser."""
        self.playwright = sync_playwright().start()
        
        # Configure browser with download directory
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            downloads_path=str(self.download_dir)
        )
        
        # Create browser context with download settings
        context = self.browser.new_context(
            accept_downloads=True,
            locale='en-US'
        )
        
        self.page = context.new_page()
        
        # Set default timeout
        self.page.set_default_timeout(self.timeout)
        
        logger.info("Browser started successfully")
        
    def close(self):
        """Close the browser and cleanup."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed")
        
    def login_to_google(self) -> bool:
        """
        Log into Google account.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info("Logging into Google account...")
            
            # Navigate to Google sign-in
            self.page.goto("https://accounts.google.com/signin")
            
            # Enter email
            email_input = self.page.wait_for_selector('input[type="email"]')
            email_input.fill(self.email)
            self.page.click('button:has-text("Next")')
            
            # Wait for password field and enter password
            password_input = self.page.wait_for_selector('input[type="password"]', timeout=10000)
            password_input.fill(self.password)
            self.page.click('button:has-text("Next")')
            
            # Wait for successful login (redirect to account page or similar)
            self.page.wait_for_url("**/myaccount.google.com/**", timeout=30000)
            
            logger.info("Successfully logged into Google account")
            return True
            
        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout during Google login: {e}")
            return False
        except Exception as e:
            logger.error(f"Error during Google login: {e}")
            return False
    
    def navigate_to_youtube(self) -> bool:
        """
        Navigate to YouTube and ensure we're logged in.
        
        Returns:
            bool: True if successfully navigated and logged in
        """
        try:
            logger.info("Navigating to YouTube...")
            
            self.page.goto("https://www.youtube.com")
            
            # Check if we're logged in by looking for the user avatar
            try:
                self.page.wait_for_selector('button[aria-label*="Google Account"]', timeout=5000)
                logger.info("Successfully logged into YouTube")
                return True
            except PlaywrightTimeoutError:
                logger.warning("Not logged into YouTube, login may be required")
                return False
                
        except Exception as e:
            logger.error(f"Error navigating to YouTube: {e}")
            return False
    
    def navigate_to_video(self, video_id: str) -> bool:
        """
        Navigate to a specific YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            bool: True if successfully navigated to video
        """
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"Navigating to video: {video_url}")
            
            self.page.goto(video_url)
            
            # Wait for video to load
            self.page.wait_for_selector('video', timeout=15000)
            
            logger.info(f"Successfully navigated to video {video_id}")
            return True
            
        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout navigating to video {video_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error navigating to video {video_id}: {e}")
            return False
    
    def find_download_button(self) -> bool:
        """
        Find and click the download button on YouTube.
        
        This method looks for various possible selectors for the download button
        which may change over time as YouTube updates its interface.
        
        Returns:
            bool: True if download button found and clicked
        """
        try:
            logger.info("Looking for download button...")
            
            # Common selectors for YouTube download button
            download_selectors = [
                'button[aria-label*="Download"]',
                'button:has-text("Download")',
                '[data-tooltip-text*="Download"]',
                'yt-icon-button[aria-label*="Download"]',
                '.download-button',
                'button:has([d*="download"])',  # SVG path for download icon
            ]
            
            for selector in download_selectors:
                try:
                    # Look for the download button
                    download_button = self.page.wait_for_selector(selector, timeout=5000)
                    if download_button and download_button.is_visible():
                        logger.info(f"Found download button with selector: {selector}")
                        download_button.click()
                        
                        # Wait a moment for the download menu to appear
                        time.sleep(2)
                        return True
                        
                except PlaywrightTimeoutError:
                    continue
            
            # If no download button found, try the three-dot menu
            logger.info("Download button not found, trying three-dot menu...")
            return self._try_three_dot_menu()
            
        except Exception as e:
            logger.error(f"Error finding download button: {e}")
            return False
    
    def _try_three_dot_menu(self) -> bool:
        """
        Try to find download option in the three-dot menu.
        
        Returns:
            bool: True if download option found in menu
        """
        try:
            # Look for three-dot menu button
            menu_selectors = [
                'button[aria-label*="More actions"]',
                'button[aria-label*="More"]',
                '.ytp-more-button',
                'yt-icon-button[aria-label*="More"]',
            ]
            
            for selector in menu_selectors:
                try:
                    menu_button = self.page.wait_for_selector(selector, timeout=3000)
                    if menu_button and menu_button.is_visible():
                        logger.info(f"Found menu button with selector: {selector}")
                        menu_button.click()
                        
                        # Wait for menu to open
                        time.sleep(1)
                        
                        # Look for download option in menu
                        download_option = self.page.wait_for_selector(
                            'text="Download"', timeout=3000
                        )
                        if download_option:
                            download_option.click()
                            logger.info("Found and clicked download in menu")
                            return True
                            
                except PlaywrightTimeoutError:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error trying three-dot menu: {e}")
            return False
    
    def select_download_quality(self, preferred_quality: str = "720p") -> bool:
        """
        Select download quality from the quality selection menu.
        
        Args:
            preferred_quality: Preferred video quality (default: "720p")
            
        Returns:
            bool: True if quality selected successfully
        """
        try:
            logger.info(f"Selecting download quality: {preferred_quality}")
            
            # Wait for quality selection menu to appear
            time.sleep(2)
            
            # Look for quality options
            quality_selectors = [
                f'text="{preferred_quality}"',
                f'[aria-label*="{preferred_quality}"]',
                f'button:has-text("{preferred_quality}")',
            ]
            
            for selector in quality_selectors:
                try:
                    quality_option = self.page.wait_for_selector(selector, timeout=5000)
                    if quality_option and quality_option.is_visible():
                        quality_option.click()
                        logger.info(f"Selected quality: {preferred_quality}")
                        return True
                except PlaywrightTimeoutError:
                    continue
            
            # If preferred quality not found, try to select any available quality
            logger.warning(f"Preferred quality {preferred_quality} not found, selecting first available")
            
            # Look for any quality button and click the first one
            quality_buttons = self.page.query_selector_all('button[role="menuitem"]')
            if quality_buttons:
                quality_buttons[0].click()
                logger.info("Selected first available quality")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error selecting download quality: {e}")
            return False
    
    def wait_for_download_complete(self, timeout: int = 300) -> Optional[str]:
        """
        Wait for download to complete and return the downloaded file path.
        
        Args:
            timeout: Maximum time to wait for download in seconds
            
        Returns:
            Optional[str]: Path to downloaded file, or None if download failed
        """
        try:
            logger.info("Waiting for download to complete...")
            
            # Monitor downloads directory for new files
            initial_files = set(self.download_dir.glob('*'))
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                current_files = set(self.download_dir.glob('*'))
                new_files = current_files - initial_files
                
                # Check for completed downloads (not .crdownload or .tmp files)
                completed_files = [
                    f for f in new_files 
                    if not f.name.endswith(('.crdownload', '.tmp', '.part'))
                ]
                
                if completed_files:
                    downloaded_file = completed_files[0]
                    logger.info(f"Download completed: {downloaded_file}")
                    return str(downloaded_file)
                
                time.sleep(2)
            
            logger.error(f"Download timeout after {timeout} seconds")
            return None
            
        except Exception as e:
            logger.error(f"Error waiting for download: {e}")
            return None
    
    def download_video(self, 
                      video_id: str, 
                      quality: str = "720p",
                      max_wait_time: int = 300) -> Optional[str]:
        """
        Download a YouTube video by ID.
        
        Args:
            video_id: YouTube video ID
            quality: Preferred video quality
            max_wait_time: Maximum time to wait for download completion
            
        Returns:
            Optional[str]: Path to downloaded file, or None if download failed
        """
        logger.info(f"Starting download of video {video_id}")
        
        # Navigate to video
        if not self.navigate_to_video(video_id):
            return None
        
        # Find and click download button
        if not self.find_download_button():
            logger.error("Could not find download button")
            return None
        
        # Select quality
        if not self.select_download_quality(quality):
            logger.warning("Could not select quality, proceeding with default")
        
        # Wait for download to complete
        return self.wait_for_download_complete(max_wait_time)
    
    def download_videos_from_list(self, 
                                 video_ids: List[str],
                                 quality: str = "720p") -> Dict[str, Optional[str]]:
        """
        Download multiple videos from a list of video IDs.
        
        Args:
            video_ids: List of YouTube video IDs
            quality: Preferred video quality
            
        Returns:
            Dict[str, Optional[str]]: Mapping of video_id to downloaded file path
        """
        results = {}
        
        for video_id in video_ids:
            logger.info(f"Downloading video {video_id} ({len(results)+1}/{len(video_ids)})")
            
            try:
                downloaded_file = self.download_video(video_id, quality)
                results[video_id] = downloaded_file
                
                if downloaded_file:
                    logger.info(f"Successfully downloaded {video_id}: {downloaded_file}")
                else:
                    logger.error(f"Failed to download {video_id}")
                    
                # Wait between downloads to be respectful
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error downloading {video_id}: {e}")
                results[video_id] = None
        
        return results


def download_youtube_video_with_playwright(video_id: str, 
                                         email: str, 
                                         password: str,
                                         download_dir: Optional[str] = None,
                                         quality: str = "720p",
                                         headless: bool = True) -> Optional[str]:
    """
    Convenience function to download a single YouTube video.
    
    Args:
        video_id: YouTube video ID
        email: Google account email
        password: Google account password
        download_dir: Directory to save download
        quality: Video quality preference
        headless: Whether to run browser in headless mode
        
    Returns:
        Optional[str]: Path to downloaded file, or None if failed
    """
    with YouTubePlaywrightDownloader(
        email=email, 
        password=password, 
        download_dir=download_dir,
        headless=headless
    ) as downloader:
        
        # Login to Google
        if not downloader.login_to_google():
            logger.error("Failed to login to Google")
            return None
        
        # Navigate to YouTube
        if not downloader.navigate_to_youtube():
            logger.error("Failed to navigate to YouTube")
            return None
        
        # Download the video
        return downloader.download_video(video_id, quality)


if __name__ == "__main__":
    # Example usage
    import os
    
    # These should be set as environment variables for security
    email = os.getenv("GOOGLE_EMAIL")
    password = os.getenv("GOOGLE_PASSWORD")
    
    if not email or not password:
        print("Please set GOOGLE_EMAIL and GOOGLE_PASSWORD environment variables")
        exit(1)
    
    # Example video ID (replace with actual video)
    video_id = "dQw4w9WgXcQ"  # Never Gonna Give You Up
    
    downloaded_file = download_youtube_video_with_playwright(
        video_id=video_id,
        email=email,
        password=password,
        download_dir="./downloads",
        quality="720p",
        headless=False  # Set to True for production
    )
    
    if downloaded_file:
        print(f"Successfully downloaded: {downloaded_file}")
    else:
        print("Download failed")