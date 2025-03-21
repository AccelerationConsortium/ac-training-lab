import subprocess

from my_secrets import STREAM_KEY, STREAM_URL


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


if __name__ == "__main__":
    p1, p2 = start_stream()
    try:
        # This will block until ffmpeg stops or the script is interrupted
        p2.wait()
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup: terminate both processes if still running
        p1.terminate()
        p2.terminate()
