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
                 headless: bool = True,
                 timeout: int = 30000):
        """
        Initialize the YouTube Playwright downloader.
        
        Args:
            email: Google account email
            password: Google account password
            headless: Whether to run browser in headless mode
            timeout: Default timeout for operations in milliseconds
        """
        self.email = email
        self.password = password
        self.download_dir = Path.cwd() / "downloads"  # Use simple default directory
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
        Log into Google account with improved 2FA handling.
        
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
            
            # Handle various post-login scenarios
            logger.info("Checking login result...")
            
            # Try to detect successful login first
            try:
                # Check for immediate redirect to account page (no 2FA required)
                self.page.wait_for_url("**/myaccount.google.com/**", timeout=5000)
                logger.info("Successfully logged into Google account (direct login)")
                return True
            except PlaywrightTimeoutError:
                # Not immediately redirected, check for other scenarios
                pass
            
            # Check if we're on any Google authenticated page
            current_url = self.page.url
            if any(domain in current_url for domain in [
                "myaccount.google.com", 
                "accounts.google.com/ManageAccount",
                "accounts.google.com/b/0/ManageAccount"
            ]):
                logger.info("Successfully logged into Google account (authenticated page)")
                return True
            
            # Check for 2FA prompts or device verification
            try:
                # Look for various 2FA related elements
                two_fa_selectors = [
                    'div:has-text("2-Step Verification")',
                    'div:has-text("Verify it\'s you")',
                    'div:has-text("device verification")',
                    'div:has-text("verification code")',
                    'input[type="tel"]',  # Phone number input for verification
                    'div:has-text("Check your phone")',
                    'div:has-text("We sent a notification")'
                ]
                
                for selector in two_fa_selectors:
                    try:
                        element = self.page.wait_for_selector(selector, timeout=2000)
                        if element and element.is_visible():
                            logger.warning(f"2FA/verification prompt detected: {selector}")
                            # Since @sgbaird mentioned 2FA should be removed now, this might indicate
                            # the device verification is still required or there's a different issue
                            logger.error("2FA verification still required - account may need device verification completed")
                            return False
                    except PlaywrightTimeoutError:
                        continue
                        
            except Exception as e:
                logger.warning(f"Error checking for 2FA prompts: {e}")
            
            # Final attempt: wait a bit longer for any redirects
            try:
                self.page.wait_for_url("**/myaccount.google.com/**", timeout=10000)
                logger.info("Successfully logged into Google account (delayed redirect)")
                return True
            except PlaywrightTimeoutError:
                pass
            
            # Check if we ended up anywhere that suggests successful auth
            final_url = self.page.url
            if "accounts.google.com" in final_url and "signin" not in final_url:
                logger.info(f"Login appears successful - on authenticated Google page: {final_url}")
                return True
            
            logger.error(f"Login did not complete successfully. Final URL: {final_url}")
            return False
            
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
    
    def navigate_to_video(self, video_id: str, channel_id: str = None) -> bool:
        """
        Navigate to YouTube Studio for a specific video.
        
        Args:
            video_id: YouTube video ID
            channel_id: Channel ID (optional, can be included in URL)
            
        Returns:
            bool: True if successfully navigated to video
        """
        try:
            # Use YouTube Studio URL as suggested in the comment
            if channel_id:
                video_url = f"https://studio.youtube.com/video/{video_id}/edit?c={channel_id}"
            else:
                video_url = f"https://studio.youtube.com/video/{video_id}/edit"
            
            logger.info(f"Navigating to video in Studio: {video_url}")
            
            self.page.goto(video_url)
            
            # Wait for Studio page to load
            self.page.wait_for_selector('[data-testid="video-editor"]', timeout=15000)
            
            logger.info(f"Successfully navigated to video {video_id} in Studio")
            return True
            
        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout navigating to video {video_id} in Studio: {e}")
            return False
        except Exception as e:
            logger.error(f"Error navigating to video {video_id} in Studio: {e}")
            return False
    
    def find_download_button(self) -> bool:
        """
        Find and click the three-dot ellipses menu with download option in YouTube Studio.
        
        As suggested in the comment, look for the three vertical ellipses button
        that has a dropdown with a "download" option.
        
        Returns:
            bool: True if download button found and clicked
        """
        try:
            logger.info("Looking for three-dot ellipses menu...")
            
            # Look for three-dot ellipses menu button in YouTube Studio
            ellipses_selectors = [
                'button[aria-label*="More"]',
                'button[aria-label*="More actions"]', 
                'button:has-text("⋮")',  # Three vertical dots
                '[data-testid="three-dot-menu"]',
                'yt-icon-button[aria-label*="More"]',
                'button[title*="More"]'
            ]
            
            for selector in ellipses_selectors:
                try:
                    ellipses_button = self.page.wait_for_selector(selector, timeout=5000)
                    if ellipses_button and ellipses_button.is_visible():
                        logger.info(f"Found ellipses menu with selector: {selector}")
                        ellipses_button.click()
                        
                        # Wait for dropdown menu to appear
                        time.sleep(2)
                        
                        # Look for download option in the dropdown
                        download_selectors = [
                            'text="Download"',
                            'button:has-text("Download")',
                            '[aria-label*="Download"]'
                        ]
                        
                        for dl_selector in download_selectors:
                            try:
                                download_option = self.page.wait_for_selector(dl_selector, timeout=3000)
                                if download_option and download_option.is_visible():
                                    logger.info("Found download option in dropdown")
                                    download_option.click()
                                    return True
                            except PlaywrightTimeoutError:
                                continue
                                
                except PlaywrightTimeoutError:
                    continue
            
            logger.error("Could not find three-dot ellipses menu with download option")
            return False
            
        except Exception as e:
            logger.error(f"Error finding download button: {e}")
            return False
    
    
    def select_download_quality(self, preferred_quality: str = "720p") -> bool:
        """
        Select download quality if available (simplified for Studio interface).
        
        Args:
            preferred_quality: Preferred video quality (not used in Studio interface)
            
        Returns:
            bool: True (Studio interface handles quality automatically)
        """
        # In YouTube Studio, the download typically starts automatically
        # after clicking the download option, so we don't need quality selection
        logger.info("Using automatic quality selection in Studio interface")
        return True
    
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
                      channel_id: Optional[str] = None,
                      quality: str = "720p",
                      max_wait_time: int = 300) -> Optional[str]:
        """
        Download a YouTube video by ID using YouTube Studio.
        
        Args:
            video_id: YouTube video ID
            channel_id: YouTube channel ID (optional, helps with navigation)
            quality: Preferred video quality (not used in Studio interface)
            max_wait_time: Maximum time to wait for download completion
            
        Returns:
            Optional[str]: Path to downloaded file, or None if download failed
        """
        logger.info(f"Starting download of video {video_id}")
        
        # Navigate to video in Studio
        if not self.navigate_to_video(video_id, channel_id):
            return None
        
        # Find and click download button (three-dot menu)
        if not self.find_download_button():
            logger.error("Could not find download button")
            return None
        
        # Quality selection is automatic in Studio interface
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
                                         channel_id: Optional[str] = None,
                                         headless: bool = True) -> Optional[str]:
    """
    Convenience function to download a single YouTube video using Studio interface.
    
    Args:
        video_id: YouTube video ID
        email: Google account email
        password: Google account password
        channel_id: YouTube channel ID (optional, helps with navigation)
        headless: Whether to run browser in headless mode
        
    Returns:
        Optional[str]: Path to downloaded file, or None if failed
    """
    with YouTubePlaywrightDownloader(
        email=email, 
        password=password, 
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
        return downloader.download_video(video_id, channel_id)


if __name__ == "__main__":
    # Example usage with real credentials from environment
    import os
    
    # Get credentials from environment variables
    email = os.getenv("GOOGLE_EMAIL")
    password = os.getenv("GOOGLE_PASSWORD")
    
    if not email or not password:
        print("❌ ERROR: Please set GOOGLE_EMAIL and GOOGLE_PASSWORD environment variables")
        print("Example:")
        print("  export GOOGLE_EMAIL='your-email@gmail.com'")
        print("  export GOOGLE_PASSWORD='your-app-password'")
        exit(1)
    
    print("🚀 Starting YouTube Studio downloader...")
    print(f"   Email: {email}")
    print(f"   Password: {'*' * len(password)}")
    print()
    
    # Example: Download from ac-hardware-streams channel
    video_id = "cIQkfIUeuSM"  # Example video ID from the comment
    channel_id = "UCHBzCfYpGwoqygH9YNh9A6g"  # ac-hardware-streams channel
    
    print(f"Target video: https://studio.youtube.com/video/{video_id}/edit?c={channel_id}")
    print("Note: Account must have access to the channel to download videos")
    print()
    
    try:
        downloaded_file = download_youtube_video_with_playwright(
            video_id=video_id,
            email=email,
            password=password,
            channel_id=channel_id,
            headless=False  # Set to True for production
        )
        
        if downloaded_file:
            print(f"✅ Successfully downloaded: {downloaded_file}")
        else:
            print("❌ Download failed - check logs above for details")
            
    except Exception as e:
        print(f"💥 Download crashed: {e}")
        logger.error(f"Download failed with exception: {e}")