# filepath: c:\Users\bairdst4\Documents\GitHub\AccelerationConsortium\ac-training-lab\src\ac_training_lab\cobot280pi\_scripts\pose_2025_vial_jubilee.py
from gradio_client import Client, file

import os

HF_TOKEN = os.environ["HF_TOKEN"]

client = Client(
    "AccelerationConsortium/cobot280pi-gradio",
    hf_token=HF_TOKEN,
)

# Define all coordinates as an array for easier maintenance
coordinates = [
    # Format: [x, y, z, roll, pitch, yaw]
    [18.9, -119.2, 298.4, -89.6, 0.57, -86.12],
    [14.7, -106.7, 350.5, -89.74, -1.11, -85.69],
    [-16.0, -10.3, 341.7, -90.6, 3.81, -81.75],
    [-21.8, 10.0, 341.7, 87.8, -55.86, 101.86],
    [-17.2, -5.8, 341.8, -90.2, -1.06, -80.58],
    [3.7, -39.8, 375.4, -92.19, 4.11, -78.57],
    [68.2, -110.9, 343.6, -95.58, 11.91, -84.48],
    [75.2, -118.9, 313.5, -98.67, 22.39, -86.78],
    [73.9, -118.4, 313.8, -97.14, 19.87, -88.0],
    [34.1, -57.0, 337.3, -103.26, 15.1, -86.3],
]

# Execute movement sequence
for coord in coordinates:
    client.predict(
        user_id="sgbaird",
        x=coord[0],
        y=coord[1],
        z=coord[2],
        roll=coord[3],
        pitch=coord[4],
        yaw=coord[5],
        movement_speed=50,
        api_name="/control_coords",
    )
