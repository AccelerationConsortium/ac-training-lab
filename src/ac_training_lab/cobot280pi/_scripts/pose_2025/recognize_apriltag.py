# filepath: c:\Users\bairdst4\Documents\GitHub\AccelerationConsortium\ac-training-lab\src\ac_training_lab\cobot280pi\_scripts\recognize_apriltag.py
import argparse
import os

import cv2
import numpy as np
from chardet import detect
from pupil_apriltags import Detector


def detect_apriltags(image_path, visualize=True, output_path=None):
    """
    Detect AprilTags in an image and optionally visualize the results.

    Args:
        image_path (str): Path to the input image.
        visualize (bool): Whether to display the image with detection results.
        output_path (str): Path to save the visualization results (if None, won't save).

    Returns:
        list: List of detected AprilTag objects.
    """
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")

    # Print image info for debugging
    print(f"Image shape: {img.shape}, dtype: {img.dtype}")

    # Scale the image if it's very small
    min_dimension = min(img.shape[0], img.shape[1])
    if min_dimension < 300:
        scale_factor = 300 / min_dimension
        img = cv2.resize(img, (0, 0), fx=scale_factor, fy=scale_factor)
        print(f"Resized image to shape: {img.shape}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Initialize the AprilTag detector
    # Using modified parameters for better detection
    detector = Detector(
        families="tag36h11",  # Default tag family
        nthreads=1,  # Number of threads
        quad_decimate=1.0,  # Image decimation (1.0 = no decimation)
        quad_sigma=0.0,  # Gaussian blur (can try 0.8 if detection fails)
        refine_edges=1,  # Refine edges of detected quads
        decode_sharpening=0.25,  # Sharpening of decoded images
        debug=0,  # Debug level
    )

    # Detect tags
    detections = detector.detect(gray)
    print(f"Detected {len(detections)} AprilTags in the image.")

    if visualize or output_path:
        # Draw detection results on the image
        for detection in detections:
            # Extract corners and convert to integers
            corners = detection.corners.astype(int)

            # Draw the outline of the tag
            cv2.polylines(img, [corners.reshape((-1, 1, 2))], True, (0, 255, 0), 2)

            # Draw tag center
            center = (int(detection.center[0]), int(detection.center[1]))
            cv2.circle(img, center, 5, (0, 0, 255), -1)

            # Print tag ID
            text_position = (int(detection.center[0]), int(detection.center[1] - 20))
            cv2.putText(
                img,
                f"ID: {detection.tag_id}",
                text_position,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                2,
            )

            # Print tag family
            family_position = (int(detection.center[0]), int(detection.center[1] + 20))
            cv2.putText(
                img,
                f"{detection.tag_family}",
                family_position,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                2,
            )

            # Print additional information
            print(f"Tag ID: {detection.tag_id}")
            print(f"Tag Family: {detection.tag_family}")
            print(f"Center: ({detection.center[0]:.2f}, {detection.center[1]:.2f})")
            print(f"Corners: {detection.corners}")
            print(f"Homography: {detection.homography}")
            print(f"Pose R: {detection.pose_R}")
            print(f"Pose t: {detection.pose_t}")
            print(f"Decision margin: {detection.decision_margin}")
            print("------------------------------")

        # Save the visualization if output path is provided
        if output_path:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            cv2.imwrite(output_path, img)
            print(f"Result saved to {output_path}")

        # Display the result if visualize is True
        if visualize:
            cv2.imshow("AprilTag Detection", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    return detections


detect_apriltags(
    "c:/Users/bairdst4/Documents/GitHub/AccelerationConsortium/ac-training-lab/src/ac_training_lab/cobot280pi/_scripts/apriltag-field-image.webp",
    visualize=False,
    output_path="c:/Users/bairdst4/Documents/GitHub/AccelerationConsortium/ac-training-lab/src/ac_training_lab/cobot280pi/_scripts/apriltag_detection_result.jpg",
)
