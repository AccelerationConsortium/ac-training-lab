import os
import subprocess

import requests

from .totp_utils import get_totp_code_from_env

YT_API_KEY = os.getenv("YT_API_KEY")


def get_latest_video_id(channel_id, device_name=None, playlist_id=None):
    if device_name is None and playlist_id is None:
        raise Exception("Must specify either device_name or playlist_id")

    if device_name is not None and playlist_id is not None:
        print("Both device_name and playlist_id entered.. device_name will be ignored.")

    if playlist_id is None:
        # Step 1: get all playlists from the channel (note that 'playlists' in url)
        url = "https://www.googleapis.com/youtube/v3/playlists"
        params = {
            "part": "snippet",
            "channelId": channel_id,  # Fixed: was CHANNEL_ID (undefined variable)
            "maxResults": 1000,
            "key": YT_API_KEY,
        }
        res = requests.get(url, params=params)
        res.raise_for_status()
        playlists = res.json().get("items", [])

        for p in playlists:
            if device_name.lower() in p["snippet"]["title"].lower():
                playlist_id = p["id"]
                break

        if not playlist_id:
            raise Exception(f"No playlist found matching device name '{device_name}'")

    # Step 2: Use search API instead of playlistItems to get the most recent video by
    # publication date
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "maxResults": 1,
        "order": "date",  # This sorts by publication date (newest first)
        "type": "video",  # Only return videos
        "key": YT_API_KEY,
    }

    # If we have a playlist_id, we need to get videos from that specific playlist
    # Note: To properly filter by both channel and playlist, we need an additional step
    if playlist_id:
        # First get videos from the playlist
        playlist_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        playlist_params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": 10,  # Get several videos to ensure we find the latest
            "key": YT_API_KEY,
        }

        playlist_res = requests.get(playlist_url, params=playlist_params)
        playlist_res.raise_for_status()
        playlist_items = playlist_res.json().get("items", [])

        if not playlist_items:
            return None

        # Sort by publish date (newest first)
        sorted_items = sorted(
            playlist_items,
            key=lambda x: x["snippet"].get("publishedAt", ""),
            reverse=True,
        )

        # Return the newest video ID
        return sorted_items[0]["snippet"]["resourceId"]["videoId"]

    # If we're not filtering by playlist, just use the search API
    res = requests.get(url, params=params)
    res.raise_for_status()
    items = res.json().get("items", [])

    if not items:
        return None

    return items[0]["id"][
        "videoId"
    ]  # Note the different path to videoId for search results


def download_youtube_live(video_id):
    """
    Relies on ytdlp https://github.com/yt-dlp/yt-dlp
    """
    url = f"https://www.youtube.com/live/{video_id}"
    try:
        result = subprocess.run(
            ["yt-dlp", url], check=True, capture_output=True, text=True
        )
        print("Download successful!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("An error occurred while downloading:")
        print(e.stderr)


def get_current_totp_for_youtube():
    """
    Get current TOTP code for YouTube authentication if configured.
    
    This function provides TOTP support for YouTube workflows that may
    require 2FA authentication when used with playwright automation.
    
    Returns:
        TOTP code as string if secret is configured, None otherwise
    """
    return get_totp_code_from_env("YOUTUBE_TOTP_SECRET")


def download_youtube_with_totp(video_id, totp_code=None):
    """
    Enhanced YouTube download function with TOTP support.
    
    Args:
        video_id: YouTube video ID to download
        totp_code: Optional TOTP code for 2FA authentication
        
    Note:
        This function demonstrates how TOTP could be integrated into
        YouTube download workflows. The actual implementation would
        depend on the specific playwright automation needs.
    """
    if totp_code is None:
        totp_code = get_current_totp_for_youtube()
    
    if totp_code:
        print(f"TOTP code available for authentication: {totp_code}")
    
    # For now, fall back to standard download
    # In a real implementation, this would pass the TOTP code to playwright
    download_youtube_live(video_id)


if __name__ == "__main__":

    video_id = get_latest_video_id(
        channel_id="UCHBzCfYpGwoqygH9YNh9A6g", device_name="Opentrons OT-2"
    )
    download_youtube_live(video_id)
