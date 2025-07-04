"""
Tests for YouTube utilities with TOTP integration.
"""

import os
import pytest
import pyotp

from ac_training_lab.video_editing.yt_utils import (
    get_current_totp_for_youtube,
    download_youtube_with_totp,
)


def test_get_current_totp_for_youtube():
    """Test getting TOTP code for YouTube authentication."""
    test_secret = pyotp.random_base32()
    env_var = "YOUTUBE_TOTP_SECRET"
    
    # Test with no env var set
    result = get_current_totp_for_youtube()
    assert result is None
    
    # Test with env var set
    os.environ[env_var] = test_secret
    try:
        result = get_current_totp_for_youtube()
        assert result is not None
        assert len(result) == 6
        assert result.isdigit()
    finally:
        if env_var in os.environ:
            del os.environ[env_var]


def test_download_youtube_with_totp_mock(monkeypatch):
    """Test YouTube download with TOTP (mocked subprocess to avoid actual download)."""
    # Mock subprocess.run to avoid actual download
    def mock_run(*args, **kwargs):
        class MockResult:
            stdout = "Mock download successful"
        return MockResult()
    
    monkeypatch.setattr("ac_training_lab.video_editing.yt_utils.subprocess.run", mock_run)
    
    # Test download with explicit TOTP code
    # This should not raise an exception
    download_youtube_with_totp("test_video_id", "123456")
    
    # Test download with TOTP from environment
    test_secret = pyotp.random_base32()
    env_var = "YOUTUBE_TOTP_SECRET"
    
    os.environ[env_var] = test_secret
    try:
        download_youtube_with_totp("test_video_id")
    finally:
        if env_var in os.environ:
            del os.environ[env_var]


def test_youtube_totp_integration():
    """Test integration between YouTube utils and TOTP functionality."""
    # This test verifies that the TOTP functionality is properly integrated
    # with the YouTube utilities without requiring actual YouTube API calls
    
    test_secret = pyotp.random_base32()
    env_var = "YOUTUBE_TOTP_SECRET"
    
    # Set up environment
    os.environ[env_var] = test_secret
    
    try:
        # Get TOTP code
        totp_code = get_current_totp_for_youtube()
        
        # Verify we got a valid TOTP code
        assert totp_code is not None
        assert len(totp_code) == 6
        assert totp_code.isdigit()
        
    finally:
        if env_var in os.environ:
            del os.environ[env_var]