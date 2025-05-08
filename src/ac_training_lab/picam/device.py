import subprocess

import requests
from my_secrets import (
    DEVICE_NAME,
    LAMBDA_FUNCTION_URL,
    PRIVACY_STATUS,
    STREAM_KEY,
    STREAM_URL,
)


def start_stream():
    """
    Starts the libcamera -> ffmpeg pipeline and returns two Popen objects:
      p1: libcamera-vid process
      p2: ffmpeg process
    """
    # First: libcamera-vid command
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
        # vertical/horizontal flips depend on the cam mount
        "--vflip",
        "--hflip",
        "-o",
        "-",  # Output to stdout (pipe)
    ]

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
        f"{STREAM_URL}/{STREAM_KEY}",
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


def call_lambda(action, device_name, privacy_status="private"):
    payload = {
        "action": action,
        "device_name": device_name,
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
    call_lambda("end", DEVICE_NAME)
    call_lambda("create", DEVICE_NAME, privacy_status=PRIVACY_STATUS)
    while True:
        print("Starting stream..")
        p1, p2 = start_stream()
        print("Stream started")
        try:
            # This will block until ffmpeg stops or the script is interrupted
            p2.wait()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
        finally:
            print("Terminating processes..")
            # Cleanup: terminate both processes if still running
            p1.terminate()
            p2.terminate()
            print("Processes terminated. Retrying..")
