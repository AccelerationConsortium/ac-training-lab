import time
import numpy as np
from picamera2 import Picamera2, Preview

from picamera2.outputs import FfmpegOutput
from picamera2.encoders import H264Encoder, Quality


def stream(stream_key):
    # YouTube stream URL and stream key
    youtube_stream_url = "rtmp://a.rtmp.youtube.com/live2"

    # Initialize the Picamera2 object
    picam2 = Picamera2()

    # Configure the camera for video capture (set resolution to 1280x720)
    picam2.configure(
        picam2.create_video_configuration(main={"size": (1280, 720)})
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
