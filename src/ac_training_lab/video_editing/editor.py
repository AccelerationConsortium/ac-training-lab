import json
import subprocess
from pathlib import Path
from io import StringIO


class VideoProcessor:
    VIDEO_FPS = 30
    SPEEDUP_FACTOR = 16

    @staticmethod
    def download_youtube_video(video_id=None, url=None, format=None, output_file=None):
        """
        Downloads a YouTube video using yt-dlp.
        If `format` is specified, it will be passed to yt-dlp via --format.
        """

        if (video_id is None and url is None) or (
            video_id is not None and url is not None
        ):
            raise ValueError("Must specify either video_id or url (but not both)")

        if video_id is not None:
            url = f"https://www.youtube.com/watch?v={video_id}"

        # Construct yt-dlp command
        command = ["yt-dlp", url]
        if format:
            command.extend(["--format", format])
        if output_file:
            command.extend(["--output", output_file])

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("Download successful!")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("An error occurred while downloading:")
            print(e.stderr)

    @staticmethod
    def download_and_process_video(link):
        """
        1. Get v1 chunks
        2. Get timestamps for stale chunks
        3. ffmpeg add overlay
        4. Apply auto-editor with v1
        """
        file_path = Path(__file__).parent

        video_path = file_path / ".raw_video.mp4"
        VideoProcessor.download_youtube_video(
            url=link, format="bv", output_file=video_path
        )

        v1_path = file_path / ".v1_timeline.json"
        VideoProcessor._generate_v1(video_path, v1_path)

        overlayed_video_path = file_path / ".overlayed_video.mp4"
        VideoProcessor._edit_add_overlay(
            video_path=video_path,
            timeline_path=v1_path,
            output_path=overlayed_video_path,
        )

        edited_video_path = file_path / ".edited_video.mp4"
        VideoProcessor._edit_apply_speedup(
            video_path=overlayed_video_path,
            output_path=edited_video_path,
        )

    @staticmethod
    def _parse_json_from_text(text, outpath):
        json_start = text.find("{")

        if json_start != -1:
            json_text = text[json_start:]
            text_as_json = json.loads(json_text)

            with open(outpath, "w") as f:
                json.dump(text_as_json, f, indent=4)
        else:
            raise ValueError("Could not find JSON data in stdout.")

    @staticmethod
    def _frame_number_to_seconds(frame_number, fps):
        total_seconds = frame_number / fps
        return int(total_seconds)

    @staticmethod
    def _generate_v1(video_path, outpath):
        log_buffer = StringIO()

        process = subprocess.Popen(
            [
                "auto-editor",
                video_path,
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
            print(line, end="")
            log_buffer.write(line)

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)

        VideoProcessor._parse_json_from_text(log_buffer.getvalue(), outpath)

    @staticmethod
    def _edit_add_overlay(video_path, timeline_path, output_path):
        with open(timeline_path, "r") as f:
            timeline_data = json.load(f)

        chunks = timeline_data["chunks"]

        sped_up_timestamps = []

        for start, stop, speed in chunks:
            # Check if the speed is not 1 (normal speed)
            if speed != 1:
                sped_up_timestamps.append(
                    (
                        VideoProcessor._frame_number_to_seconds(
                            start, VideoProcessor.VIDEO_FPS
                        ),
                        VideoProcessor._frame_number_to_seconds(
                            stop, VideoProcessor.VIDEO_FPS
                        ),
                    )
                )

        # Build ffmpeg filter-complex
        filter_complex = ""
        for i, (start, stop) in enumerate(sped_up_timestamps):
            if i == 0:
                filter_complex += f"[0:v][1:v] overlay=0:0:enable='between(t,{start},{stop})' [v{i+1}]; "
            elif i == len(sped_up_timestamps) - 1:
                filter_complex += f"[v{i}][1:v] overlay=0:0:enable='between(t,{start},{stop}):' [v{i+1}]"
            else:
                filter_complex += f"[v{i}][1:v] overlay=0:0:enable='between(t,{start},{stop})' [v{i+1}]; "

        overlay_path = Path(__file__).parent / "overlay.png"
        overlay_output_path = Path(__file__).parent / "overlayed.mp4"

        process = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
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
                output_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in process.stdout:
            print(line, end="")

        process.wait()

    @staticmethod
    def _edit_apply_speedup(video_path, output_path):
        process = subprocess.Popen(
            [
                "auto-editor",
                video_path,
                "--edit",
                "motion:threshold=0.2",
                "--video-speed",
                "1",
                "--silent-speed",
                str(VideoProcessor.SPEEDUP_FACTOR),
                "--video-codec",
                "h264_nvenc",
                "--download-format",
                "bv",
                "--margin",
                "5sec",
                "--output-file",
                output_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in process.stdout:
            print(line, end="")

        process.wait()
