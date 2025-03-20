import logging
import socket
import time

from libcamera import Transform
from my_secrets import YOUTUBE_STREAM_KEY, YOUTUBE_STREAM_URL
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

# Configure logging, useful when running `sudo journalctl -u a1-cam.service -f`,
# as described in README.
# Example log: 2025-03-18 15:00:00 - INFO - Starting camera setup...
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# create a logger with a custom name
logger = logging.getLogger("picam")


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


# Wait until internet is connected
logger.info("Checking for internet")
while not internet():
    internet()
logger.info("Internet connected")

# Initialize the Picamera2 object
logger.info("Initializing camera")
picam2 = Picamera2()

# Configure the camera for video capture (set resolution to 1280x720)
picam2.configure(
    picam2.create_video_configuration(
        main={"size": (1280, 720)}, transform=Transform(hflip=1, vflip=1)
    )
)

picam2.start()
logger.info("Camera started")

# Create the ffmpeg command for streaming
#
ffmpeg_cmd = [
    "-b:v 4M",
    "-f flv",  # Output format for RTMP stream
    "anullsrc=channel_layout=stereo:sample_rate=48000",
    f"{YOUTUBE_STREAM_URL}/{YOUTUBE_STREAM_KEY}",  # YouTube RTMP URL and stream key
]
ffmpeg_cmd = " ".join(ffmpeg_cmd)

# Initialize FfmpegOutput to handle streaming
ffmpeg_output = FfmpegOutput(ffmpeg_cmd, audio=True)
h264_encoder = H264Encoder(bitrate=4000000)

# Start the output stream
picam2.start_recording(encoder=h264_encoder, output=ffmpeg_output)
logger.info("Streaming started")

try:
    while True:
        logger.info("Streaming...")
        time.sleep(10)

except KeyboardInterrupt:
    logger.warning("Streaming stopped.")

except Exception as e:
    logger.error(f"An error occurred: {e}")

finally:
    # Stop the camera and preview
    picam2.stop_recording()
    picam2.stop()
    logger.info("Camera stopped.")
