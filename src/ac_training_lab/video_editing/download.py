import json
import os
from pathlib import Path

import pyotp
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from src.ac_training_lab.video_editing.my_secrets import EMAIL, PASSWORD, TOTP_SECRET

# Set up TOTP for 2FA
totp = pyotp.TOTP(TOTP_SECRET)

OUTPUT_DIR = Path(__file__).parent / "downloaded_videos"
PROCESSED_JSON = Path(__file__).parent / "processed.json"


def list_my_playlists(youtube):
    playlist_ids = []
    request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)

    while request:
        response = request.execute()
        for item in response.get("items", []):
            playlist_id = item["id"]
            title = item["snippet"]["title"]
            print(f"{title}: {playlist_id}")
            playlist_ids.append(playlist_id)

        request = youtube.playlists().list_next(request, response)

    return playlist_ids


def list_videos_in_playlist(youtube, playlist_id):
    video_ids = []
    request = youtube.playlistItems().list(
        part="snippet", playlistId=playlist_id, maxResults=50
    )

    while request:
        response = request.execute()
        for item in response["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            title = item["snippet"]["title"]
            print(f"  {title}: {video_id}")
            video_ids.append(video_id)

        request = youtube.playlistItems().list_next(request, response)

    return video_ids


def setup_youtube_client():
    credentials = Credentials(
        token=os.getenv("YOUTUBE_TOKEN"),
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        token_uri=os.getenv("YOUTUBE_TOKEN_URI"),
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],
    )
    return build("youtube", "v3", credentials=credentials)


def load_processed():
    if PROCESSED_JSON.exists():
        with open(PROCESSED_JSON, "r") as f:
            return json.load(f)
    return {}


def get_pending_downloads(youtube, processed_videos, downloaded_ids):
    all_videos = {}
    playlist_ids = list_my_playlists(youtube)
    for playlist_id in playlist_ids:
        video_ids = list_videos_in_playlist(youtube, playlist_id)
        all_videos[playlist_id] = [
            vid
            for vid in video_ids
            if vid not in processed_videos.get(playlist_id, [])
            and vid not in downloaded_ids
        ]
    return all_videos


def login_google(page):
    page.goto("https://accounts.google.com/")
    page.get_by_role("textbox", name="Email or phone").fill(EMAIL)
    page.get_by_role("button", name="Next").click()
    page.wait_for_selector('input[name="Passwd"]')
    page.get_by_role("textbox", name="Enter your password").fill(PASSWORD)
    page.get_by_role("button", name="Next").click()

    # TOTP if needed
    try:
        page.get_by_role(
            "link", name="Get a verification code from the Google Authenticator app"
        ).wait_for(timeout=5000)
    except PlaywrightTimeoutError:
        print("No TOTP prompt")
        return

    page.get_by_role(
        "link", name="Get a verification code from the Google Authenticator app"
    ).click()
    page.wait_for_selector('input[name="totpPin"]', timeout=5000)
    page.fill('input[name="totpPin"]', totp.now())
    page.get_by_role("button", name="Next").click()
    page.wait_for_url("https://myaccount.google.com/?pli=1", timeout=10000)


def download_video(page, video_id):
    try:
        print(f"Navigating to video {video_id}...")
        page.goto(f"https://studio.youtube.com/video/{video_id}/edit/", timeout=15000)
        page.get_by_role("button", name="Options").wait_for(timeout=5000)
        page.get_by_role("button", name="Options").click()
        print(f"Opened video {video_id} options.")

        page.get_by_role("menuitem", name="Download").wait_for(timeout=5000)
        with page.expect_download(timeout=10000) as download_info:
            page.get_by_role("menuitem", name="Download").click()
            print(f"Began downloading video {video_id}...")

        download = download_info.value
        OUTPUT_DIR.mkdir(exist_ok=True)
        file_path = OUTPUT_DIR / download.suggested_filename
        download.save_as(file_path)
        print(f"Downloaded: {file_path}")

    except Exception as e:
        print(f"Failed to download video {video_id}: {e}")


def main():
    youtube = setup_youtube_client()
    processed_videos = load_processed()
    downloaded_ids = set([f.stem for f in OUTPUT_DIR.glob("*.mp4")])

    pending = get_pending_downloads(youtube, processed_videos, downloaded_ids)
    print(f"Pending downloads: {sum(len(v) for v in pending.values())}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        login_google(page)

        for _, videos in pending.items():
            for video_id in videos:
                download_video(page, video_id)

        browser.close()


if __name__ == "__main__":
    main()
