import os

import subprocess
import requests

YT_API_KEY = os.getenv("YT_API_KEY")
CHANNEL_ID = "UCHBzCfYpGwoqygH9YNh9A6g"


def get_latest_video_id(device_name=None, playlist_id=None):

    if device_name is None and playlist_id is None:
        raise Exception("Must specify either device_name or playlist_id")

    if device_name is not None and playlist_id is not None:
        print("Both device_name and playlist_id entered.. device_name will be ignored.")

    if playlist_id is None:
        # Step 1: get all playlists from the channel (note that 'playlists' in url)
        url = "https://www.googleapis.com/youtube/v3/playlists"
        params = {
            "part": "snippet",
            "channelId": CHANNEL_ID,
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

    # Step 2: get the most recent video from the playlist
    # NOTE: (This grabs the video most recently *added* to the playlist)
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": 1,
        "key": YT_API_KEY,
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    items = res.json().get("items", [])

    if not items:
        return None

    return items[0]["snippet"]["resourceId"]["videoId"]


def download_youtube_live(video_id):
    url = f"https://www.youtube.com/live/{video_id}"
    try:
        result = subprocess.run(
            ["./yt-dlp", url], check=True, capture_output=True, text=True
        )
        print("Download successful!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("An error occurred while downloading:")
        print(e.stderr)


# Example usage
download_youtube_live("ktj2CUfRv0w")

if __name__ == "__main__":
    video_id = get_latest_video_id(device_name="Opentrons OT-2")
    download_youtube_live(video_id)
