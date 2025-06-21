#!/usr/bin/env python3
"""
Test script for real Google login with the Playwright YouTube downloader.

This script uses real Google credentials from environment variables to test
the authentication flow. It will attempt to login and access YouTube Studio,
but is expected to fail when trying to access the video since the account
hasn't been added to the channel yet.
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ac_training_lab.video_editing.playwright_yt_downloader import YouTubePlaywrightDownloader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_real_google_login():
    """Test the complete login flow with real Google credentials."""
    
    print("=" * 70)
    print("REAL GOOGLE LOGIN TEST")
    print("=" * 70)
    print()
    
    # Get credentials from environment variables
    email = os.getenv("GOOGLE_EMAIL")
    password = os.getenv("GOOGLE_PASSWORD")
    
    if not email or not password:
        print("❌ ERROR: GOOGLE_EMAIL and GOOGLE_PASSWORD environment variables not found")
        print("Please ensure the credentials are set as environment secrets.")
        return False
    
    print(f"Using credentials:")
    print(f"  Email: {email}")
    print(f"  Password: {'*' * len(password)}")
    print()
    
    # Test parameters from the user's comment
    test_video_id = "cIQkfIUeuSM"
    test_channel_id = "UCHBzCfYpGwoqygH9YNh9A6g"  # ac-hardware-streams
    
    print(f"Test target:")
    print(f"  Video ID: {test_video_id}")
    print(f"  Channel ID: {test_channel_id}")
    print(f"  Studio URL: https://studio.youtube.com/video/{test_video_id}/edit?c={test_channel_id}")
    print()
    
    try:
        # Initialize downloader with real credentials
        with YouTubePlaywrightDownloader(
            email=email,
            password=password,
            headless=False  # Run visible so we can see what happens
        ) as downloader:
            
            print("STEP 1: Attempting Google Authentication")
            print("-" * 50)
            
            login_success = downloader.login_to_google()
            
            if login_success:
                print("✅ Google login successful!")
            else:
                print("❌ Google login failed")
                return False
            
            print()
            print("STEP 2: Navigating to YouTube")
            print("-" * 50)
            
            youtube_success = downloader.navigate_to_youtube()
            
            if youtube_success:
                print("✅ Successfully navigated to YouTube and confirmed login")
            else:
                print("❌ Failed to navigate to YouTube or confirm login")
                return False
            
            print()
            print("STEP 3: Attempting to Access YouTube Studio Video")
            print("-" * 50)
            print("NOTE: This is expected to fail since the account hasn't been added to the channel")
            
            studio_success = downloader.navigate_to_video(test_video_id, test_channel_id)
            
            if studio_success:
                print("✅ Successfully accessed YouTube Studio video")
                print("   This means the account has access to the channel!")
                
                # Try to find download button
                print()
                print("STEP 4: Looking for Download Button")
                print("-" * 50)
                
                download_button_found = downloader.find_download_button()
                
                if download_button_found:
                    print("✅ Found download button (three-dot menu)")
                    print("   Download process would start here")
                else:
                    print("❌ Could not find download button")
                
            else:
                print("❌ Failed to access YouTube Studio video")
                print("   This is expected - the account likely doesn't have channel access")
                print("   Error indicates authentication worked but authorization failed")
                
            print()
            print("=" * 70)
            print("TEST RESULTS SUMMARY")
            print("=" * 70)
            print(f"✅ Google Authentication:  {'✓' if login_success else '✗'}")
            print(f"✅ YouTube Navigation:     {'✓' if youtube_success else '✗'}")
            print(f"{'✅' if studio_success else '❌'} Studio Access:        {'✓' if studio_success else '✗'} (Expected to fail)")
            print()
            
            if login_success and youtube_success:
                print("🎉 SUCCESS: Authentication flow is working correctly!")
                print("   The Google login and YouTube navigation both work.")
                if not studio_success:
                    print("   Studio access failed as expected (account not added to channel).")
                print()
                print("NEXT STEPS:")
                print("1. Add the Google account to the ac-hardware-streams channel")
                print("2. Test again - studio access should then succeed")
                print("3. Video downloads will then be possible")
                return True
            else:
                print("❌ FAILURE: Authentication flow has issues")
                return False
                
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main function to run the real login test."""
    print("Starting Real Google Login Test...")
    print("This will use actual credentials and attempt to log in.")
    print("Browser will be visible so you can see the authentication process.")
    print()
    
    try:
        success = test_real_google_login()
        if success:
            print("\n✅ Real login test completed successfully!")
            print("The Playwright authentication system is working correctly.")
        else:
            print("\n❌ Real login test failed!")
            print("Check the logs above for details.")
        return success
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)