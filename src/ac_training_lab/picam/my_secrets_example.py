LAMBDA_FUNCTION_URL = "your_Lambda_function_url"

# NOTE: the combination of CAM_NAME and WORKFLOW_NAME must be fewer than 67 characters to accommodate YouTube's title limit
# (33 characters are automatically appended due to https://github.com/AccelerationConsortium/streamingLambda/blob/32e1ce85664d5fca6f8c1bf21cd1e7e5df071040/chalicelib/ytb_api_utils.py#L100)
CAM_NAME = "your_camera_name" # e.g., "cam-a1b2"
WORKFLOW_NAME = "your_workflow_name" # typical naming convention: [device]-[workflow]-[lab], e.g., "OT2-HM-SDL2" for an Opentrons OT2, hot melt workflow, as part of the Inorganic Chemistry Lab (SDL2) at the Acceleration Consortium

PRIVACY_STATUS = "private"  # "private", "public", or "unlisted"

# Camera orientation settings
# Set to True to flip the camera image vertically
CAMERA_VFLIP = True
# Set to True to flip the camera image horizontally
CAMERA_HFLIP = True
