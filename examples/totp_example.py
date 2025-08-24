#!/usr/bin/env python3
"""
Example usage of pyotp functionality in AC Training Lab.

This script demonstrates how to use the TOTP functionality
for YouTube video downloading with 2FA authentication.
"""

import os
import sys

# Example of how to use the TOTP functionality
def example_basic_totp():
    """Example of basic TOTP operations."""
    print("=== Basic TOTP Example ===")
    
    try:
        from ac_training_lab.video_editing import (
            generate_totp_code,
            verify_totp_code,
            create_totp_provisioning_uri
        )
        
        # Generate a random secret for demonstration
        import pyotp
        secret = pyotp.random_base32()
        print(f"Generated secret: {secret}")
        
        # Generate TOTP code
        code = generate_totp_code(secret)
        print(f"Generated TOTP code: {code}")
        
        # Verify the code
        is_valid = verify_totp_code(secret, code)
        print(f"Code verification: {is_valid}")
        
        # Create provisioning URI
        uri = create_totp_provisioning_uri(secret, "user@example.com")
        print(f"Provisioning URI: {uri}")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure pyotp is installed: pip install pyotp")


def example_youtube_integration():
    """Example of YouTube integration with TOTP."""
    print("\n=== YouTube TOTP Integration Example ===")
    
    try:
        from ac_training_lab.video_editing import (
            get_current_totp_for_youtube,
            download_youtube_with_totp
        )
        
        # Get TOTP for YouTube (returns None if not configured)
        totp_code = get_current_totp_for_youtube()
        if totp_code:
            print(f"YouTube TOTP code: {totp_code}")
        else:
            print("No YouTube TOTP secret configured")
            print("Set YOUTUBE_TOTP_SECRET environment variable to enable")
        
        # Example of how download would work
        # Note: This won't actually download anything without proper setup
        print("Example download with TOTP support:")
        print("download_youtube_with_totp('video_id', totp_code)")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure the video_editing module is properly installed")


def example_environment_setup():
    """Example of setting up environment variables."""
    print("\n=== Environment Setup Example ===")
    
    print("To use TOTP with YouTube authentication:")
    print("1. Get your TOTP secret from your authenticator app")
    print("2. Set environment variable:")
    print("   export YOUTUBE_TOTP_SECRET='your_base32_secret_here'")
    print("3. Use the functions:")
    print("   from ac_training_lab.video_editing import get_current_totp_for_youtube")
    print("   code = get_current_totp_for_youtube()")
    print("   # Use code with playwright for 2FA authentication")


if __name__ == "__main__":
    print("AC Training Lab TOTP Functionality Examples")
    print("=" * 50)
    
    example_basic_totp()
    example_youtube_integration()
    example_environment_setup()
    
    print("\n" + "=" * 50)
    print("For more information, see docs/totp_usage.md")