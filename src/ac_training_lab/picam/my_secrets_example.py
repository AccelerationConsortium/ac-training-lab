LAMBDA_FUNCTION_URL = "your_Lambda_function_url"
CAM_NAME = "your_camera_name"
# IMPORTANT: WORKFLOW_NAME must be unique across all devices and streams!
# The AWS Lambda function uses this name to identify and manage broadcasts.
# Identical workflow names will cause conflicts where ending one stream
# may terminate others with the same name. Keep names short as the Lambda
# function may append additional characters during processing.
WORKFLOW_NAME = "your_workflow_name"
PRIVACY_STATUS = "private"  # "private", "public", or "unlisted"

# Camera orientation settings
# Set to True to flip the camera image vertically
CAMERA_VFLIP = True
# Set to True to flip the camera image horizontally
CAMERA_HFLIP = True
