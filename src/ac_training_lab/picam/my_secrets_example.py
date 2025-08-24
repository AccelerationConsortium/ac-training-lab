LAMBDA_FUNCTION_URL = "your_Lambda_function_url"

# NOTE: keep the combination of CAM_NAME and WORKFLOW_NAME to 71 characters or fewer to accommodate YouTube's title limit of 100 characters
# (29 characters are automatically appended due to https://github.com/AccelerationConsortium/streamingLambda/blob/main/chalicelib/ytb_api_utils.py)
CAM_NAME = "your_camera_name" # e.g., typical naming convention: cam-<id>, e.g., "cam-a1b2", with <id> as lower case. You can use https://1password.com/password-generator to generate a set of random characters, then manually take the first 4 characters and make them lowercase
WORKFLOW_NAME = "your_workflow_name" # typical naming convention: [device]-[workflow]-[lab] @ [organization], e.g., "OT2-HM-SDL2 @ AC" for an Opentrons OT2, hot melt workflow, as part of the Inorganic Chemistry Lab (SDL2) at the Acceleration Consortium

PRIVACY_STATUS = "private"  # "private", "public", or "unlisted"

# Camera orientation settings
# Set to True to flip the camera image vertically
CAMERA_VFLIP = True
# Set to True to flip the camera image horizontally
CAMERA_HFLIP = True
