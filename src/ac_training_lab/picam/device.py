import json
import subprocess

import requests
from my_secrets import (
    CAM_NAME,
    CAMERA_HFLIP,
    CAMERA_VFLIP,
    LAMBDA_FUNCTION_URL,
    PRIVACY_STATUS,
    WORKFLOW_NAME,
)


def start_stream(ffmpeg_url):
    """
    Starts the libcamera -> ffmpeg pipeline and returns two Popen objects:
      p1: libcamera-vid process
      p2: ffmpeg process
    """
    # First: libcamera-vid command with core parameters
    libcamera_cmd = [
        "libcamera-vid",
        "--inline",
        "--nopreview",
        "-t",
        "0",
        "--mode",
        "1536:864",  # A known 16:9 sensor mode
        "--width",
        "854",  # Scale width
        "--height",
        "480",  # Scale height
        "--framerate",
        "15",  # Frame rate
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
        # Copy the H.264 video directly
        "-c:v",
        "copy",
        # Encode audio as AAC
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-preset",
        "fast",
        "-strict",
        "experimental",
        # Output format is FLV, then final RTMP URL
        "-f",
        "flv",
        ffmpeg_url,
    ]

    # Start libcamera-vid, capturing its output in a pipe
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


if __name__ == "__main__":
    # End previous broadcast and start a new one via Lambda
    call_lambda("end", CAM_NAME, WORKFLOW_NAME)
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
        p1, p2 = start_stream(ffmpeg_url)
        print("Stream started")
        try:
            p2.wait()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
        finally:
            print("Terminating processes..")
            p1.terminate()
            p2.terminate()
            print("Processes terminated. Retrying..")
