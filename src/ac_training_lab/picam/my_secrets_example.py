# AWS Lambda Function URL - Required for YouTube streaming
# This URL is obtained by deploying the streamingLambda service to AWS.
# See: https://github.com/AccelerationConsortium/streamingLambda
# The Lambda function handles YouTube API calls to create and manage live streams.
LAMBDA_FUNCTION_URL = "your_Lambda_function_url"

# Camera Name - Used for identifying this specific camera device
# This appears in the YouTube broadcast title alongside the workflow name and timestamp.
# Examples: "PiCam-01", "LabCam-A", "MainCamera"
CAM_NAME = "your_camera_name"

# Workflow Name - Used for organizing streams into playlists
# IMPORTANT: This must be UNIQUE across all devices to avoid conflicts.
# The workflow name is used to:
# - Create/find YouTube playlists
# - End streams for this specific workflow
# - Organize videos by experimental setup or location
# Keep it short (YouTube has character limits) and descriptive.
# Examples: "SDLT-Toronto-001", "MyLab-Setup-A", "AC-Synthesis-Bench"
# Related issue: https://github.com/AccelerationConsortium/ac-dev-lab/issues/290
WORKFLOW_NAME = "your_workflow_name"

# YouTube Privacy Status - Controls who can view the live stream
# Options: "private" (only you), "public" (anyone), "unlisted" (anyone with link)
# For lab monitoring, "unlisted" is often preferred for controlled sharing.
PRIVACY_STATUS = "private"  # "private", "public", or "unlisted"

# Camera orientation settings
# Set to True to flip the camera image vertically (rotate 180° around horizontal axis)
CAMERA_VFLIP = True
# Set to True to flip the camera image horizontally (mirror image)
CAMERA_HFLIP = True

# Camera rotation setting (for portrait mode streaming)
# Allowed options: 0, 90, 180, 270 (degrees, clockwise)
# Default: 0 (no rotation / landscape mode)
# Use 90 or 270 for portrait mode streaming
CAMERA_ROTATION = 0

# Stream resolution setting
# Allowed options for YouTube: "144p", "240p", "360p", "480p", "720p", "1080p"
# Resolution mappings:
#   "144p" = 256x144
#   "240p" = 426x240
#   "360p" = 640x360
#   "480p" = 854x480
#   "720p" = 1280x720
#   "1080p" = 1920x1080
# Default: "480p"
# Note: Pi Zero 2W can comfortably handle 480p at 15fps. 720p at 15fps is pushing it.
# For 1080p or higher frame rates, use a Pi 4B or Pi 5.
RESOLUTION = "480p"

# Stream frame rate setting (frames per second)
# Common values: 15, 24, 30
# Default: 15
# Note: Pi Zero 2W can comfortably handle 15fps at 480p.
# For higher frame rates or resolutions, use a Pi 4B or Pi 5.
FRAME_RATE = 15

# Timestamp overlay setting
# Set to True to display current date/time on the video stream
# Format: YYYY-MM-DD_HH-MM-SS (e.g., 2024-12-01_21-38-37)
# The timestamp appears in the top-left corner (white text with black background)
# Note: Enabling timestamp requires video re-encoding which increases CPU usage.
# Default: False
TIMESTAMP_OVERLAY = False
