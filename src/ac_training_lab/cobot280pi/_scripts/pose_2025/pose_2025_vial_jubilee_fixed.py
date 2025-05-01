# filepath: c:\Users\bairdst4\Documents\GitHub\AccelerationConsortium\ac-training-lab\src\ac_training_lab\cobot280pi\_scripts\pose_2025_vial_jubilee_fixed.py
import time

from gradio_client import Client, file
import os

HF_TOKEN = os.environ["HF_TOKEN"]

client = Client(
    "AccelerationConsortium/cobot280pi-gradio",
    hf_token=HF_TOKEN,
)

# Define workflow sequence with separate steps for movement and gripper operations
# Each step is a dictionary with type, parameters, and description
workflow_sequence = [
    # Initial setup and approach
    {
        "type": "gripper",
        "value": 100,  # Open gripper (100=open, 0=closed)
        "description": "Open gripper completely",
    },
    {
        "type": "move",
        "coords": {
            "x": 18.9,
            "y": -119.2,
            "z": 298.4,
            "roll": -89.6,
            "pitch": 0.57,
            "yaw": -86.12,
        },
        "description": "Move to initial approach position",
    },
    # Pre-pickup position
    {
        "type": "move",
        "coords": {
            "x": 14.7,
            "y": -106.7,
            "z": 350.5,
            "roll": -89.74,
            "pitch": -1.11,
            "yaw": -85.69,
        },
        "description": "Move to pre-pickup position",
    },
    # Moving to placement area
    {
        "type": "move",
        "coords": {
            "x": -16.0,
            "y": -10.3,
            "z": 341.7,
            "roll": -90.6,
            "pitch": 3.81,
            "yaw": -81.75,
        },
        "description": "Move to placement area",
    },
    {
        "type": "gripper",
        "value": 0,  # Close gripper
        "description": "Close gripper to grab vial",
    },
    # Placement position
    {
        "type": "move",
        "coords": {
            "x": -21.8,
            "y": 10.0,
            "z": 341.7,
            "roll": 87.8,
            "pitch": -55.86,
            "yaw": 101.86,
        },
        "description": "Move to placement position",
    },
    {
        "type": "gripper",
        "value": 100,  # Open gripper
        "description": "Open gripper to release vial",
    },
    # Post-placement
    {
        "type": "move",
        "coords": {
            "x": -17.2,
            "y": -5.8,
            "z": 341.8,
            "roll": -90.2,
            "pitch": -1.06,
            "yaw": -80.58,
        },
        "description": "Move to post-placement position",
    },
    # Moving back
    {
        "type": "move",
        "coords": {
            "x": 3.7,
            "y": -39.8,
            "z": 375.4,
            "roll": -92.19,
            "pitch": 4.11,
            "yaw": -78.57,
        },
        "description": "Move back from placement area",
    },
    # Approaching pickup
    {
        "type": "move",
        "coords": {
            "x": 68.2,
            "y": -110.9,
            "z": 343.6,
            "roll": -95.58,
            "pitch": 11.91,
            "yaw": -84.48,
        },
        "description": "Approach pickup location",
    },
    # Vial pickup position
    {
        "type": "move",
        "coords": {
            "x": 75.2,
            "y": -118.9,
            "z": 313.5,
            "roll": -98.67,
            "pitch": 22.39,
            "yaw": -86.78,
        },
        "description": "Move to vial pickup position",
    },
    {
        "type": "gripper",
        "value": 0,  # Close gripper
        "description": "Close gripper to grab next vial",
    },
    # Post-pickup
    {
        "type": "move",
        "coords": {
            "x": 73.9,
            "y": -118.4,
            "z": 313.8,
            "roll": -97.14,
            "pitch": 19.87,
            "yaw": -88.0,
        },
        "description": "Move to post-pickup position",
    },
    # Return position
    {
        "type": "move",
        "coords": {
            "x": 34.1,
            "y": -57.0,
            "z": 337.3,
            "roll": -103.26,
            "pitch": 15.1,
            "yaw": -86.3,
        },
        "description": "Return to final position",
    },
]


def wait_for_user_confirmation(step_number, description):
    """Waits for user to press Enter before proceeding with the next step."""
    print(f"\n{'='*80}")
    print(f"STEP {step_number}: {description}")
    print(f"{'='*80}")
    input("Press Enter to execute this step or Ctrl+C to abort... ")


def move_robot_arm(coords):
    """Move the robot arm with proper error handling."""
    print(f"  Moving to coordinates: x={coords['x']}, y={coords['y']}, z={coords['z']}")
    client.predict(
        user_id="sgbaird",
        x=coords["x"],
        y=coords["y"],
        z=coords["z"],
        roll=coords["roll"],
        pitch=coords["pitch"],
        yaw=coords["yaw"],
        movement_speed=10,
        api_name="/control_coords",
    )


def set_gripper(value):
    """Set the gripper value with proper error handling."""
    print(f"  Setting gripper to {value} (0=closed, 100=open)")
    client.predict(
        user_id="sgbaird",
        gripper_value=value,
        movement_speed=10,
        api_name="/control_gripper",
    )


# Execute integrated workflow
print("\n" + "=" * 80)
print("VIAL JUBILEE WORKFLOW - INTERACTIVE MODE")
print("=" * 80)
print("\nThis script executes each step only after you confirm by pressing Enter.")
print("You can press Ctrl+C at any time to abort the workflow.")
print("\nStarting vial handling workflow...")

for i, step in enumerate(workflow_sequence):
    # Wait for user confirmation before proceeding
    wait_for_user_confirmation(i + 1, step["description"])

    # Execute the appropriate action based on step type
    if step["type"] == "move":
        move_robot_arm(step["coords"])
    elif step["type"] == "gripper":
        set_gripper(step["value"])

    print(f"  Step {i+1} completed.")
    time.sleep(1)  # Small pause between steps to ensure system stability

print("\n" + "=" * 80)
print("WORKFLOW COMPLETE!")
print("=" * 80)
