# Playwright YouTube Downloader

This module provides an alternative method for downloading YouTube videos using Playwright browser automation. This is particularly useful for downloading private or unlisted videos from owned channels that may not be accessible via traditional methods like yt-dlp.

## Features

- **Browser Automation**: Uses Playwright to automate a real browser session
- **Google Account Login**: Automatically logs into a Google account to access owned videos
- **Native YouTube Interface**: Uses YouTube's built-in download functionality
- **Quality Selection**: Supports selecting video quality (720p, 1080p, etc.)
- **Multiple Videos**: Can download multiple videos in sequence
- **Integration**: Integrates with existing yt-dlp functionality
- **Flexible Configuration**: Environment variable based configuration

## Installation

Install the required dependencies:

```bash
pip install playwright requests
playwright install chromium
```

## Configuration

Set up your credentials and preferences using environment variables:

```bash
# Required credentials
export GOOGLE_EMAIL="your-email@gmail.com"
export GOOGLE_PASSWORD="your-app-password"

# Optional settings
export YT_DOWNLOAD_DIR="./downloads"
export YT_DEFAULT_QUALITY="720p"
export YT_HEADLESS="true"
export YT_PAGE_TIMEOUT="30000"
export YT_DOWNLOAD_TIMEOUT="300"
export YT_CHANNEL_ID="UCHBzCfYpGwoqygH9YNh9A6g"
```

### Security Notes

- **Use App Passwords**: For Google accounts with 2FA enabled, generate and use an App Password instead of your regular password
- **Environment Variables**: Store credentials in environment variables, not in code
- **Restricted Scope**: Use an account with minimal necessary permissions

## Usage

### Basic Usage

```python
from ac_training_lab.video_editing.playwright_yt_downloader import download_youtube_video_with_playwright

# Download a single video
downloaded_file = download_youtube_video_with_playwright(
    video_id="dQw4w9WgXcQ",
    email="your-email@gmail.com",
    password="your-app-password",
    download_dir="./downloads",
    quality="720p",
    headless=True
)

if downloaded_file:
    print(f"Downloaded: {downloaded_file}")
```

### Advanced Usage

```python
from ac_training_lab.video_editing.playwright_yt_downloader import YouTubePlaywrightDownloader

# Use the downloader class for more control
with YouTubePlaywrightDownloader(
    email="your-email@gmail.com",
    password="your-app-password",
    download_dir="./downloads",
    headless=False  # Show browser for debugging
) as downloader:
    
    # Login once
    if downloader.login_to_google():
        downloader.navigate_to_youtube()
        
        # Download multiple videos
        video_ids = ["video1", "video2", "video3"]
        results = downloader.download_videos_from_list(video_ids, quality="1080p")
        
        for video_id, file_path in results.items():
            if file_path:
                print(f"✓ {video_id}: {file_path}")
            else:
                print(f"✗ {video_id}: Failed")
```

### Integrated Downloader

The integrated downloader provides a unified interface for both yt-dlp and Playwright methods:

```python
from ac_training_lab.video_editing.integrated_downloader import YouTubeDownloadManager

# Initialize with Playwright as default
manager = YouTubeDownloadManager(use_playwright=True)

# Download latest video from channel
result = manager.download_latest_from_channel(
    channel_id="UCHBzCfYpGwoqygH9YNh9A6g",
    device_name="Opentrons OT-2",
    method="playwright",  # or "ytdlp"
    quality="720p"
)

if result['success']:
    print(f"Downloaded: {result['file_path']}")
else:
    print(f"Failed: {result['error']}")
```

### Command Line Usage

```bash
# Download specific video with Playwright
python -m ac_training_lab.video_editing.integrated_downloader \
    --video-id dQw4w9WgXcQ \
    --method playwright \
    --quality 720p

# Download latest from channel with yt-dlp
python -m ac_training_lab.video_editing.integrated_downloader \
    --channel-id UCHBzCfYpGwoqygH9YNh9A6g \
    --device-name "Opentrons OT-2" \
    --method ytdlp

# Use Playwright by default
python -m ac_training_lab.video_editing.integrated_downloader \
    --use-playwright \
    --channel-id UCHBzCfYpGwoqygH9YNh9A6g
```

## How It Works

1. **Browser Launch**: Starts a Chromium browser instance with download settings
2. **Google Login**: Navigates to Google sign-in and enters credentials
3. **YouTube Navigation**: Goes to YouTube and verifies login status
4. **Video Access**: Navigates to specific video pages
5. **Download Trigger**: Finds and clicks the download button in YouTube's interface
6. **Quality Selection**: Chooses the preferred video quality
7. **Download Monitoring**: Waits for download completion and returns file path

## Browser Selectors

The downloader uses multiple fallback selectors to find YouTube's download interface elements, as these can change over time:

- Download buttons: `button[aria-label*="Download"]`, `button:has-text("Download")`, etc.
- Three-dot menus: `button[aria-label*="More actions"]`, `yt-icon-button[aria-label*="More"]`, etc.
- Quality options: Text-based and aria-label selectors

## Error Handling

The system includes comprehensive error handling for:

- **Authentication failures**: Invalid credentials, 2FA requirements
- **Network timeouts**: Configurable timeout values
- **Element not found**: Multiple selector fallbacks
- **Download failures**: File system and browser download issues

## Troubleshooting

### Common Issues

1. **Login Failed**
   - Check credentials are correct
   - Use App Password for 2FA accounts
   - Verify account access to target videos

2. **Download Button Not Found**
   - Video may not have download option
   - Account may not have permission
   - YouTube interface may have changed

3. **Download Timeout**
   - Increase `YT_DOWNLOAD_TIMEOUT`
   - Check network connection
   - Try lower quality setting

4. **Browser Issues**
   - Run `playwright install chromium`
   - Try with `headless=False` for debugging
   - Check browser console logs

### Debug Mode

Run with visible browser for debugging:

```python
downloaded_file = download_youtube_video_with_playwright(
    video_id="your_video_id",
    email="your-email@gmail.com",
    password="your-password",
    headless=False  # Show browser
)
```

## Comparison: yt-dlp vs Playwright

| Feature | yt-dlp | Playwright |
|---------|--------|------------|
| Speed | Fast | Slower |
| Resource Usage | Low | Higher |
| Private Videos | Limited | Full access with login |
| Owned Channel Videos | May fail | Full access |
| YouTube Updates | May break | More resilient |
| Quality Options | Many | YouTube's options |
| Batch Downloads | Efficient | Sequential |
| Browser Required | No | Yes |

## When to Use Each Method

**Use yt-dlp when:**
- Downloading public videos
- Batch processing many videos
- Resource efficiency is important
- No authentication required

**Use Playwright when:**
- Downloading private/unlisted videos
- Need access to owned channel content
- yt-dlp fails due to YouTube restrictions
- Want to use YouTube's native interface

## Contributing

To extend the functionality:

1. Add new selector patterns for UI changes
2. Implement additional quality options
3. Add support for playlists
4. Improve error handling and retry logic

## Security Considerations

- Never hardcode credentials in source code
- Use environment variables or secure credential stores
- Consider using service accounts for automation
- Regularly rotate passwords and App Passwords
- Monitor for unusual account activity

## License

This module is part of the ac-training-lab project and follows the same license terms.