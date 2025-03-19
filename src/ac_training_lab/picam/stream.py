import socket
import time

from libcamera import Transform
from my_secrets import YOUTUBE_STREAM_KEY, YOUTUBE_STREAM_URL
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput


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
print("Checking for internet")
while not internet():
    internet()
print("Internet connected")

# Initialize the Picamera2 object
picam2 = Picamera2()

# Configure the camera for video capture (set resolution to 1280x720)
picam2.configure(
    picam2.create_video_configuration(
        main={"size": (1280, 720)}, transform=Transform(hflip=1, vflip=1)
    )
)  # Video configuration

picam2.start_preview(Preview.QTGL)
picam2.start()

# Create the ffmpeg command for streaming
ffmpeg_cmd = [
    "-b:v 4M",
    "-f flv",  # Output format for RTMP stream
    f"{YOUTUBE_STREAM_URL}/{YOUTUBE_STREAM_KEY}",  # YouTube RTMP URL and stream key
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
