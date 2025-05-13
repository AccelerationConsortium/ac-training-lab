"""
1. Get v1 chunks
2. Get timestamps for stale chunks
3. ffmpeg add overlay
4. Apply auto-editor with v1
"""

import json
import subprocess

from ac_training_lab.video_editing.yt_utils import download_youtube_video


def generate_v1(text):
    json_start = text.find("{")

    if json_start != -1:
        timeline_json_str = text[json_start:]
        timeline_data = json.loads(timeline_json_str)

        with open("v1.json", "w") as f:
            json.dump(timeline_data, f, indent=4)
    else:
        raise ValueError("Could not find JSON data in stdout.")


def frame_number_to_seconds(frame_number, fps):
    total_seconds = frame_number / fps
    return int(total_seconds)


link = "video.mp4"

# download_youtube_video(link=link, format="bv")

result = subprocess.run(
    [
        "auto-editor",
        link,
        "--edit",
        "motion:threshold=0.2",
        "--video-speed",
        "1",
        "--silent-speed",
        "5",
        "--video-codec",
        "h264_videotoolbox",
        "--download-format",
        "bv",
        "--margin",
        "5sec",
        "--export",
        "timeline:api=1",
    ],
    capture_output=True,
    text=True,
    check=True,
)

generate_v1(result.stdout)

with open("v1.json", "r") as f:
    timeline_data = json.load(f)

chunks = timeline_data["chunks"]

sped_up_timestamps = []

for start, stop, speed in chunks:
    # Check if the speed is not 1 (normal speed)
    if speed != 1:
        sped_up_timestamps.append(
            (frame_number_to_seconds(start, 30), frame_number_to_seconds(stop, 30))
        )

# Build ffmpeg filter-complex
filter_complex = ""
for i, (start, stop) in enumerate(sped_up_timestamps):