import time
import numpy as np
from picamera2 import Picamera2, Preview
from picamera2.outputs import FfmpegOutput

# YouTube stream URL and stream key
youtube_stream_url = "rtmp://a.rtmp.youtube.com/live2"
stream_key = "YOUR_STREAM_KEY"  # Replace with your YouTube stream key

# Initialize the Picamera2 object
picam2 = Picamera2()

# Configure the camera for video capture (set resolution to 1280x720)
picam2.configure(picam2.create_video_configuration())  # Video configuration
picam2.start()

# Start the preview window
picam2.start_preview(Preview.QTGL)  # Use OpenGL for hardware-accelerated preview (QTGL)

# Create the ffmpeg command for streaming
ffmpeg_cmd = [
    'ffmpeg',
    '-re',  # Read input at native frame rate
    '-f', 'rawvideo',  # Input video format
    '-pix_fmt', 'yuv420p',  # Pixel format (common for raw video)
    '-s', '1280x720',  # Set the resolution (same as camera resolution)
    '-i', '-',  # Input will come from stdin (pipe)
    '-vcodec', 'libx264',  # Use H.264 codec for video compression
    '-framerate', '30',  # Set frame rate (same as camera capture rate)
    '-f', 'flv',  # Output format for RTMP stream
    f'{youtube_stream_url}/{stream_key}'  # YouTube RTMP URL and stream key
]

# Initialize FfmpegOutput to handle streaming
ffmpeg_output = FfmpegOutput(ffmpeg_cmd)

# Start the output stream
picam2.start_recording(ffmpeg_output)

try:
    while True:
        # Continuously capture and send frames
        time.sleep(1 / 30)  # Sleep to maintain 30 FPS capture rate

except KeyboardInterrupt:
    print("Streaming stopped.")

finally:
    # Stop the camera and preview
    picam2.stop_recording()
    picam2.stop_preview()
    picam2.stop()

