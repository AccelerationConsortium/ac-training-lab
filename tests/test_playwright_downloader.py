"""
Tests for the Playwright YouTube downloader functionality.

Note: These tests focus on the structure and basic functionality.
Full integration tests would require valid credentials and network access.
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import our modules
from ac_training_lab.video_editing.playwright_yt_downloader import YouTubePlaywrightDownloader
from ac_training_lab.video_editing.playwright_config import PlaywrightYTConfig
from ac_training_lab.video_editing.integrated_downloader import YouTubeDownloadManager


class TestPlaywrightYTConfig:
    """Test the configuration class."""
    
    def test_config_initialization(self):
        """Test that configuration initializes with defaults."""
        config = PlaywrightYTConfig()
        
        # Test defaults
        assert config.page_timeout == 30000
        assert config.download_timeout == 300
        assert config.headless is True
        
    def test_config_validation_without_credentials(self):
        """Test that validation fails without credentials."""
        config = PlaywrightYTConfig()
        config.google_email = None
        config.google_password = None
        
        assert not config.validate()
        
    def test_config_validation_with_credentials(self):
        """Test that validation passes with credentials."""
        config = PlaywrightYTConfig()
        config.google_email = "test@example.com"
        config.google_password = "password"
        
        assert config.validate()
        
    def test_config_to_dict(self):
        """Test configuration dictionary conversion."""
        config = PlaywrightYTConfig()
        config.google_email = "test@example.com"
        config.google_password = "password"
        
        config_dict = config.to_dict()
        
        # Check that sensitive data is not included
        assert "google_email" not in config_dict
        assert "google_password" not in config_dict
        
        # Check that other fields are included
        assert "has_credentials" in config_dict
        assert config_dict["has_credentials"] is True


class TestYouTubePlaywrightDownloader:
    """Test the Playwright downloader class."""
    
    def test_downloader_initialization(self):
        """Test downloader initialization."""
        downloader = YouTubePlaywrightDownloader(
            email="test@example.com",
            password="password",
            headless=True
        )
        
        assert downloader.email == "test@example.com"
        assert downloader.password == "password"
        assert downloader.download_dir == Path.cwd() / "downloads"
        assert downloader.headless is True
        assert downloader.timeout == 30000
        
    def test_download_directory_creation(self):
        """Test that download directory is created automatically."""
        downloader = YouTubePlaywrightDownloader(
            email="test@example.com",
            password="password"
        )
        
        # Default downloads directory should be created
        assert downloader.download_dir.exists()
        assert downloader.download_dir.is_dir()
            
    @patch('ac_training_lab.video_editing.playwright_yt_downloader.sync_playwright')
    def test_context_manager(self, mock_playwright):
        """Test context manager functionality."""
        # Mock the playwright objects
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        downloader = YouTubePlaywrightDownloader(
            email="test@example.com",
            password="password"
        )
        
        # Test context manager
        with downloader:
            # Should have started browser
            assert mock_playwright_instance.chromium.launch.called
            assert mock_browser.new_context.called
            assert mock_context.new_page.called
            
        # Should have cleaned up
        assert mock_page.close.called
        assert mock_browser.close.called
        assert mock_playwright_instance.stop.called


class TestYouTubeDownloadManager:
    """Test the integrated download manager."""
    
    def test_manager_initialization_ytdlp(self):
        """Test manager initialization with yt-dlp."""
        manager = YouTubeDownloadManager(use_playwright=False)
        
        assert not manager.use_playwright
        assert manager.config is not None
        
    def test_manager_initialization_playwright_invalid_config(self):
        """Test manager initialization with invalid Playwright config."""
        # Create a config without credentials
        config = PlaywrightYTConfig()
        config.google_email = None
        config.google_password = None
        
        with pytest.raises(ValueError, match="Invalid configuration"):
            YouTubeDownloadManager(use_playwright=True, config=config)
            
    @patch('ac_training_lab.video_editing.integrated_downloader.get_latest_video_id')
    def test_get_latest_video_from_channel(self, mock_get_video_id):
        """Test getting latest video from channel."""
        mock_get_video_id.return_value = "test_video_id"
        
        manager = YouTubeDownloadManager(use_playwright=False)
        
        video_id = manager.get_latest_video_from_channel(
            channel_id="test_channel",
            device_name="test_device"
        )
        
        assert video_id == "test_video_id"
        mock_get_video_id.assert_called_once()
        
    @patch('ac_training_lab.video_editing.integrated_downloader.download_youtube_live')
    def test_download_video_ytdlp_success(self, mock_download):
        """Test successful video download with yt-dlp."""
        mock_download.return_value = None  # Successful download
        
        manager = YouTubeDownloadManager(use_playwright=False)
        
        result = manager.download_video("test_video_id", method="ytdlp")
        
        assert result['success'] is True
        assert result['method'] == 'ytdlp'
        assert result['video_id'] == 'test_video_id'
        assert result['error'] is None
        
    @patch('ac_training_lab.video_editing.integrated_downloader.download_youtube_live')
    def test_download_video_ytdlp_failure(self, mock_download):
        """Test failed video download with yt-dlp."""
        mock_download.side_effect = Exception("Download failed")
        
        manager = YouTubeDownloadManager(use_playwright=False)
        
        result = manager.download_video("test_video_id", method="ytdlp")
        
        assert result['success'] is False
        assert result['method'] == 'ytdlp'
        assert result['video_id'] == 'test_video_id'
        assert result['error'] is not None


class TestIntegrationScenarios:
    """Test integration scenarios."""
    
    def test_video_id_extraction_format(self):
        """Test that video ID formats are handled correctly."""
        # Test various video ID formats
        test_cases = [
            "dQw4w9WgXcQ",  # Standard 11-character ID
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Full URL
            "https://youtu.be/dQw4w9WgXcQ",  # Short URL
        ]
        
        for test_id in test_cases:
            # Extract just the ID part
            if "v=" in test_id:
                video_id = test_id.split("v=")[1].split("&")[0]
            elif "youtu.be/" in test_id:
                video_id = test_id.split("youtu.be/")[1].split("?")[0]
            else:
                video_id = test_id
                
            assert len(video_id) == 11  # YouTube video IDs are 11 characters
            assert video_id.isalnum() or any(c in video_id for c in ['-', '_'])


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])