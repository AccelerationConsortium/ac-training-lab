import socket
import sys
import os
import wget

import time
from picamera2 import Picamera2, Preview
from picamera2.outputs import FfmpegOutput
from picamera2.encoders import H264Encoder

from libcamera import Transform

SCRIPT_URL = "https://raw.githubusercontent.com/AccelerationConsortium/ac-training-lab/refs/heads/jwoo-camera/src/ac_training_lab/picam/stream.py"


def stream(stream_key):
    # YouTube stream URL and stream key
    youtube_stream_url = "rtmp://a.rtmp.youtube.com/live2"

    # Initialize the Picamera2 object
    picam2 = Picamera2()

    # Configure the camera for video capture (set resolution to 1280x720)
    picam2.configure(
        picam2.create_video_configuration(main={"size": (1280, 720)}, transform=Transform(hflip=1, vflip=1))
    )  # Video configuration

    picam2.start_preview(Preview.QTGL)
    picam2.start()

    # Create the ffmpeg command for streaming
    ffmpeg_cmd = [
        "-b:v 4M",
        "-f flv",  # Output format for RTMP stream
        f"{youtube_stream_url}/{stream_key}",  # YouTube RTMP URL and stream key
    ]
    ffmpeg_cmd = " ".join(ffmpeg_cmd)

    # Initialize FfmpegOutput to handle streaming
    ffmpeg_output = FfmpegOutput(ffmpeg_cmd, audio=True)
    h264_encoder = H264Encoder(bitrate=4000000)

    # Start the output stream
    picam2.start_recording(encoder=h264_encoder, output=ffmpeg_output)

    try:
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        print("Streaming stopped.")

    finally:
        # Stop the camera and preview
        picam2.stop_recording()
        picam2.stop()


def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


def update_script():
    print("Updating script")
    os.remove(sys.argv[0])
    wget.download(SCRIPT_URL, out=sys.argv[0])
    print("Script updated successfully.")
    os.environ["SCRIPT_UPDATED"] = "1"
    os.execv(sys.executable, ["python3"] + sys.argv)


if __name__ == "__main__":
    # Wait until internet is connected
    print("Checking for internet")
    while not internet():
        internet()
    print("Internet connected")

    # Update this script
    if os.getenv("SCRIPT_UPDATED") != "1":
        update_script()

    # Check if a previous stream key exists
    try:
        with open(os.path.join(os.path.dirname(__file__), ".stream_key"), "r") as f:
            stream_key = f.read()
        print(f"Using saved stream key: {stream_key}")
    except FileNotFoundError:
        print("No previous stream key found. Exiting.")
        exit()

    stream(stream_key)
