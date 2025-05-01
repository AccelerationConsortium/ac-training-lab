# filepath: c:\Users\bairdst4\Documents\GitHub\AccelerationConsortium\ac-training-lab\src\ac_training_lab\cobot280pi\_scripts\pose_2025_vial_jubilee_integrated.py
import os
from gradio_client import Client, file

HF_TOKEN = os.environ["HF_TOKEN"]

client = Client(
    "AccelerationConsortium/cobot280pi-gradio",
    hf_token=HF_TOKEN,
)

# fmt: off
# Define integrated sequence with both coordinates and gripper states
# Format: [x, y, z, roll, pitch, yaw, gripper_value, description]
# gripper_value: 0-100 (0=closed, 100=open), None = no gripper change
workflow_sequence = [
    [18.9, -119.2, 298.4, -89.6, 0.57, -86.12, 100, "Initial approach with open gripper"],
    [14.7, -106.7, 350.5, -89.74, -1.11, -85.69, None, "Pre-pickup position"],
    [-16.0, -10.3, 341.7, -90.6, 3.81, -81.75, 0, "Moving to placement area"],
    [-21.8, 10.0, 341.7, 87.8, -55.86, 101.86, None, "Placement position - open gripper to release vial"],
    [-17.2, -5.8, 341.8, -90.2, -1.06, -80.58, None, "Post-placement"],
    [3.7, -39.8, 375.4, -92.19, 4.11, -78.57, None, "Moving back"],
    [68.2, -110.9, 343.6, -95.58, 11.91, -84.48, None, "Approaching pickup"],
    [75.2, -118.9, 313.5, -98.67, 22.39, -86.78, 0, "Vial pickup position - close gripper to grab vial"],
    [73.9, -118.4, 313.8, -97.14, 19.87, -88.0, None, "Post-pickup"],
    [34.1, -57.0, 337.3, -103.26, 15.1, -86.3, None, "Return position"],
]
# fmt: on

# Execute integrated workflow
print("Starting vial handling workflow...")

for i, step in enumerate(workflow_sequence):
    print(f"\nExecuting step {i+1}: {step[7]}")

    # Move to the position
    print(f"  Moving to coordinates: x={step[0]}, y={step[1]}, z={step[2]}")
    client.predict(
        user_id="sgbaird",
        x=step[0],
        y=step[1],
        z=step[2],
        roll=step[3],
        pitch=step[4],
        yaw=step[5],
        movement_speed=50,
        api_name="/control_coords",
    )

    # Handle gripper operation if specified
    if step[6] is not None:
        gripper_value = step[6]
        print(f"  Setting gripper to {gripper_value} (0=closed, 100=open)")
        client.predict(
            user_id="sgbaird",
            gripper_value=gripper_value,
            movement_speed=20,
            api_name="/control_gripper",
        )

print("\nWorkflow complete!")
