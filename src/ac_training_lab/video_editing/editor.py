"""
1. Get v1 chunks
2. Get timestamps for stale chunks
3. ffmpeg add overlay
4. Apply auto-editor with v1
"""

import json
import subprocess
from pathlib import Path
from io import StringIO


from src.ac_training_lab.video_editing.yt_utils import download_youtube_video


def generate_v1(text, outpath):
    json_start = text.find("{")

    if json_start != -1:
        timeline_json_str = text[json_start:]
        timeline_data = json.loads(timeline_json_str)

        with open(outpath, "w") as f:
            json.dump(timeline_data, f, indent=4)
    else:
        raise ValueError("Could not find JSON data in stdout.")


def frame_number_to_seconds(frame_number, fps):
    total_seconds = frame_number / fps
    return int(total_seconds)


link = Path(__file__).parent / "video.mp4"

# link='https://www.youtube.com/live/Tbru5BiokmU?si=Sbmfu5dggSYLpnsp'
# outpath = Path(__file__).parent / 'video.mp4'
# download_youtube_video(url=link, format="bv", output_file = outpath)

log_buffer = StringIO()

process = subprocess.Popen(
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
        "h264_nvenc",
        "--download-format",
        "bv",
        "--margin",
        "5sec",
        "--export",
        "timeline:api=1",
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

for line in process.stdout:
    print(line, end="")  # Live output
    log_buffer.write(line)  # Capture output

process.wait()
if process.returncode != 0:
    raise subprocess.CalledProcessError(process.returncode, process.args)

# Use result.stdout equivalent
v1_path = Path(__file__).parent / "v1.json"
generate_v1(log_buffer.getvalue(), v1_path)
# generate_v1(result.stdout)


with open(v1_path, "r") as f:
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
    if i == 0:
        filter_complex += (
            f"[0:v][1:v] overlay=0:0:enable='between(t,{start},{stop})' [v{i+1}]; "
        )
    elif i == len(sped_up_timestamps) - 1:
        filter_complex += (
            f"[v{i}][1:v] overlay=0:0:enable='between(t,{start},{stop}):' [v{i+1}]"
        )
    else:
        filter_complex += (
            f"[v{i}][1:v] overlay=0:0:enable='between(t,{start},{stop})' [v{i+1}]; "
        )


overlay_path = Path(__file__).parent / "overlay.png"
overlay_output_path = Path(__file__).parent / "overlayed.mp4"

process = subprocess.Popen(
    [
        "ffmpeg",
        "-y",
        "-i",
        link,
        "-i",
        overlay_path,
        "-filter_complex",
        filter_complex,
        "-map",
        f"[v{len(sped_up_timestamps)}]",
        "-c:a",
        "copy",
        "-c:v",
        "h264_nvenc",
        overlay_output_path,
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

for line in process.stdout:
    print(line, end="")
    log_buffer.write(line)

process.wait()

edited_output_path = Path(__file__).parent / "edited.mp4"

process = subprocess.Popen(
    [
        "auto-editor",
        overlay_output_path,
        "--edit",
        "motion:threshold=0.2",
        "--video-speed",
        "1",
        "--silent-speed",
        "16",
        # "--video-codec",
        # "h264_nvenc",
        "--download-format",
        "bv",
        "--margin",
        "5sec",
        "--output-file",
        edited_output_path,
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

for line in process.stdout:
    print(line, end="")
    log_buffer.write(line)

process.wait()
