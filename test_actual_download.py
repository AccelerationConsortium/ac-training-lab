#!/usr/bin/env python3
"""
Test script to actually attempt downloading a video using the Playwright downloader.

This script will try to use the real credentials to download the video from
ac-hardware-streams channel as requested by @sgbaird.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_actual_download():
    """Test actual video download with real credentials."""
    print("=" * 70)
    print("ACTUAL VIDEO DOWNLOAD TEST")
    print("=" * 70)
    print()
    
    # Get credentials
    email = os.getenv("GOOGLE_EMAIL")
    password = os.getenv("GOOGLE_PASSWORD")
    
    if not email or not password:
        print("❌ ERROR: Missing credentials")
        return False
    
    print("✅ Credentials available:")
    print(f"   Email: {email}")
    print(f"   Password: {'*' * len(password)} (length: {len(password)})")
    print()
    
    # Target video details from the comment
    video_id = "cIQkfIUeuSM"
    channel_id = "UCHBzCfYpGwoqygH9YNh9A6g"  # ac-hardware-streams
    
    print("🎯 Target video:")
    print(f"   Video ID: {video_id}")
    print(f"   Channel ID: {channel_id}")
    print(f"   Studio URL: https://studio.youtube.com/video/{video_id}/edit?c={channel_id}")
    print()
    
    # Try to import and use the Playwright downloader
    try:
        print("⚙️  Importing Playwright downloader...")
        
        # Add src directory to path
        src_path = Path(__file__).parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from ac_training_lab.video_editing.playwright_yt_downloader import download_youtube_video_with_playwright
        
        print("✅ Playwright downloader imported successfully")
        print()
        
        print("🚀 Starting video download...")
        print("   This will attempt to:")
        print("   1. Launch Playwright browser")
        print("   2. Login to Google with provided credentials")
        print("   3. Navigate to YouTube Studio")
        print("   4. Access the video page")
        print("   5. Find and click the three-dot ellipses menu")
        print("   6. Click the download option")
        print("   7. Wait for download completion")
        print()
        
        # Attempt the actual download
        downloaded_file = download_youtube_video_with_playwright(
            video_id=video_id,
            email=email,
            password=password,
            channel_id=channel_id,
            headless=False  # Set to False to see what's happening
        )
        
        if downloaded_file:
            print("🎉 SUCCESS!")
            print(f"   Downloaded file: {downloaded_file}")
            print(f"   File exists: {Path(downloaded_file).exists()}")
            
            # Check file size
            if Path(downloaded_file).exists():
                file_size = Path(downloaded_file).stat().st_size
                print(f"   File size: {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
            
            return True
        else:
            print("❌ DOWNLOAD FAILED")
            print("   Check the logs above for details")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Playwright may not be available in this environment")
        return False
    except Exception as e:
        print(f"💥 Download failed with exception: {e}")
        logger.exception("Download exception details:")
        return False

def main():
    """Main function."""
    print("Testing actual video download as requested by @sgbaird")
    print("This will attempt to download video cIQkfIUeuSM from ac-hardware-streams channel")
    print()
    
    try:
        success = test_actual_download()
        
        if success:
            print()
            print("✅ Download test completed successfully!")
            print("   The video has been downloaded using Playwright automation.")
            print("   The account has proper channel access and can download videos.")
        else:
            print()
            print("❌ Download test failed")
            print("   This could be due to:")
            print("   - Playwright not being available in this environment")
            print("   - Network connectivity issues")
            print("   - Authentication problems")
            print("   - Channel access issues")
            print("   - YouTube interface changes")
        
        return success
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)