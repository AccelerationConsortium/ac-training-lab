import json
import shutil
import subprocess

import requests
from my_secrets import (
    CAM_NAME,
    CAMERA_HFLIP,
    CAMERA_ROTATION,
    CAMERA_VFLIP,
    FRAME_RATE,
    LAMBDA_FUNCTION_URL,
    PRIVACY_STATUS,
    RESOLUTION,
    TIMESTAMP_OVERLAY,
    WORKFLOW_NAME,
)

# Resolution mappings for YouTube-compatible resolutions
RESOLUTION_MAP = {
    "144p": (256, 144),
    "240p": (426, 240),
    "360p": (640, 360),
    "480p": (854, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
}


def get_camera_command():
    """
    Returns the available camera command.

    Uses 'rpicam-vid' on trixie or 'libcamera-vid' on bookworm.
    """
    if shutil.which("rpicam-vid"):
        return "rpicam-vid"
    elif shutil.which("libcamera-vid"):
        return "libcamera-vid"
    else:
        raise RuntimeError(
            "Neither 'rpicam-vid' nor 'libcamera-vid' command found on this system"
        )


def start_stream(
    ffmpeg_url, width=854, height=480, rotation=0, framerate=15, timestamp_overlay=False
):
    """
    Starts the libcamera -> ffmpeg pipeline and returns two Popen objects:
      p1: camera process (rpicam-vid or libcamera-vid)
      p2: ffmpeg process

    Args:
        ffmpeg_url: RTMP URL for streaming
        width: Output width in pixels (final output after rotation)
        height: Output height in pixels (final output after rotation)
        rotation: Rotation angle (0, 90, 180, 270 degrees clockwise)
        framerate: Frame rate in fps
        timestamp_overlay: Whether to show timestamp on video
    """
    # Get the available camera command
    camera_cmd = get_camera_command()

    # Camera always captures in landscape orientation using the full sensor.
    # For portrait output (90/270 rotation), we capture landscape and rotate in ffmpeg.
    # This preserves the full field of view instead of cropping.
    #
    # For 90/270 rotation, capture at height x width (landscape), then
    # rotate to width x height (portrait). For 0/180 rotation, capture at
    # width x height and output the same orientation.
    if rotation in (90, 270):
        # For portrait output, capture in landscape (swap dimensions for camera)
        # Camera captures height x width, then ffmpeg rotates to width x height
        cam_width, cam_height = height, width
    else:
        cam_width, cam_height = width, height

    # First: camera command with core parameters
    libcamera_cmd = [
        camera_cmd,
        "--inline",
        "--nopreview",
        "-t",
        "0",
        "--width",
        str(cam_width),  # Scale width
        "--height",
        str(cam_height),  # Scale height
        "--framerate",
        str(framerate),  # Frame rate
        "--codec",
        "h264",  # H.264 encoding
        "--bitrate",
        "1000000",  # ~1 Mbps video
    ]

    # Add flip parameters if needed
    if CAMERA_VFLIP:
        libcamera_cmd.extend(["--vflip"])
    if CAMERA_HFLIP:
        libcamera_cmd.extend(["--hflip"])

    # Add output parameters last
    libcamera_cmd.extend(["-o", "-"])  # Output to stdout (pipe)

    # Build video filter chain for ffmpeg
    video_filters = []

    # Add rotation filter if needed
    if rotation == 90:
        video_filters.append("transpose=1")  # 90 degrees clockwise
    elif rotation == 180:
        video_filters.append("hflip,vflip")  # 180 degrees
    elif rotation == 270:
        video_filters.append(
            "transpose=2"
        )  # 90 degrees counter-clockwise (270 clockwise)

    # Add timestamp overlay if enabled
    # Format: YYYY-MM-DD_HH-MM-SS. ffmpeg's localtime evaluates per-frame,
    # so the overlay updates once per second at typical framerates.
    if timestamp_overlay:
        # drawtext filter with white text, black background box, in top-left corner
        # fontsize scales with video height for consistent appearance
        if rotation in (90, 270):
            actual_height = width
        else:
            actual_height = height
        fontsize = max(16, actual_height // 20)
        # Note: In ffmpeg drawtext filter, special characters need escaping:
        # - The format separator after localtime uses \:
        # - Colons in the time display (H:M:S) also need escaping
        # - Using dashes instead of colons in time to avoid complex escaping issues
        timestamp_filter = (
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            f":fontsize={fontsize}"
            f":fontcolor=white"
            f":box=1:boxcolor=black@0.5:boxborderw=5"
            f":x=10:y=10"
            f":text='%{{localtime\\:%Y-%m-%d_%H-%M-%S}}'"
        )
        video_filters.append(timestamp_filter)

    # Second: ffmpeg command
    ffmpeg_cmd = [
        "ffmpeg",
        # Generate silent audio source
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=44100",
        # Handle timestamps/threading
        "-thread_queue_size",
        "1024",
        "-use_wallclock_as_timestamps",
        "1",
        # Read H.264 video from pipe
        "-i",
        "pipe:0",
    ]

    # Add video filter and encoding settings
    # Note: When filters are applied, libx264 encoding is required which increases
    # CPU usage compared to the original H.264 passthrough. This is unavoidable
    # since ffmpeg cannot apply filters without re-encoding the video stream.
    if video_filters:
        filter_chain = ",".join(video_filters)
        ffmpeg_cmd.extend(
            ["-vf", filter_chain, "-c:v", "libx264", "-preset", "ultrafast"]
        )
    else:
        ffmpeg_cmd.extend(["-c:v", "copy"])

    ffmpeg_cmd.extend(
        [
            # Encode audio as AAC
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-strict",
            "experimental",
            # Fix non-monotonous DTS warnings by enabling audio synchronization
            # and constant frame rate video output
            "-async",
            "1",
            "-vsync",
            "cfr",
            # Output format is FLV, then final RTMP URL
            "-f",
            "flv",
            ffmpeg_url,
        ]
    )

    # Start camera process, capturing its output in a pipe
    p1 = subprocess.Popen(
        libcamera_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    # Start ffmpeg, reading from p1's stdout
    p2 = subprocess.Popen(ffmpeg_cmd, stdin=p1.stdout, stderr=subprocess.STDOUT)

    # Close p1's stdout in the parent process
    p1.stdout.close()

    return p1, p2


def call_lambda(action, CAM_NAME, WORKFLOW_NAME, privacy_status="private"):
    payload = {
        "action": action,
        "cam_name": CAM_NAME,
        "workflow_name": WORKFLOW_NAME,
        "privacy_status": privacy_status,
    }
    print(f"Sending to Lambda: {payload}")
    try:

        response = requests.post(LAMBDA_FUNCTION_URL, json=payload)
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        response.raise_for_status()
        # Try to decode JSON, otherwise fall back to raw text
        try:
            result = response.json()
            if isinstance(result, dict) and "statusCode" in result and "body" in result:
                body = result["body"]
            else:
                body = result
        except ValueError:
            body = response.text

        print(f"Lambda '{action}' succeeded: {body}")
        return body

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error occurred: {e} - Response: {response.text}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to decode Lambda response: {e}")


def end_previous_broadcast():
    try:
        call_lambda("end", CAM_NAME, WORKFLOW_NAME)
    except RuntimeError as e:
        print(f"Could not end previous broadcast; continuing to create a new one: {e}")


if __name__ == "__main__":
    # Validate and get resolution
    if RESOLUTION not in RESOLUTION_MAP:
        raise ValueError(
            f"Invalid RESOLUTION '{RESOLUTION}'. "
            f"Allowed options: {list(RESOLUTION_MAP.keys())}"
        )
    width, height = RESOLUTION_MAP[RESOLUTION]

    # Validate rotation
    if CAMERA_ROTATION not in (0, 90, 180, 270):
        raise ValueError(
            f"Invalid CAMERA_ROTATION '{CAMERA_ROTATION}'. "
            f"Allowed options: 0, 90, 180, 270"
        )

    # Validate frame rate
    if not isinstance(FRAME_RATE, int) or FRAME_RATE <= 0:
        raise ValueError(
            f"Invalid FRAME_RATE '{FRAME_RATE}'. "
            f"Must be a positive integer (e.g., 15, 24, 30)"
        )

    # For 90/270 rotation, output is portrait (swapped dimensions)
    if CAMERA_ROTATION in (90, 270):
        output_width, output_height = height, width
        orientation = "portrait"
    else:
        output_width, output_height = width, height
        orientation = "landscape"

    print(
        f"Using resolution: {RESOLUTION} ({output_width}x{output_height} {orientation})"
    )
    print(f"Using rotation: {CAMERA_ROTATION} degrees")
    print(f"Using frame rate: {FRAME_RATE} fps")
    print(f"Timestamp overlay: {'enabled' if TIMESTAMP_OVERLAY else 'disabled'}")

    # End previous broadcast and start a new one via Lambda
    end_previous_broadcast()
    raw_body = call_lambda(
        "create", CAM_NAME, WORKFLOW_NAME, privacy_status=PRIVACY_STATUS
    )
    try:
        result = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        ffmpeg_url = result["result"]["ffmpeg_url"]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise RuntimeError(
            f"Cannot proceed: ffmpeg_url not found or response invalid → {e}"
        )

    print(f"Streaming to: {ffmpeg_url}")

    while True:
        print("Starting stream..")
        p1, p2 = start_stream(
            ffmpeg_url, width, height, CAMERA_ROTATION, FRAME_RATE, TIMESTAMP_OVERLAY
        )
        print("Stream started")
        interrupted = False
        try:
            p2.wait()
        except KeyboardInterrupt:
            print("Received interrupt signal, exiting...")
            interrupted = True
        except Exception as e:
            print(e)
        finally:
            print("Terminating processes..")
            p1.terminate()
            p2.terminate()
            print("Processes terminated.")
            if interrupted:
                break
            else:
                print("Retrying..")
