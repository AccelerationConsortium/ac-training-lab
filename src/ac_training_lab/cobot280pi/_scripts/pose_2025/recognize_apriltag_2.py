import os
import sys

import cv2
from pupil_apriltags import Detector

# Use the image path where we know the file exists
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "apriltag-field-image.webp")

print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {script_dir}")
print(f"Trying to load image from: {image_path}")

# Check if file exists
if not os.path.exists(image_path):
    print(f"Error: Image file does not exist at path: {image_path}")
    print("Files in directory:")
    for file in os.listdir(script_dir):
        print(f"  {file}")
    sys.exit(1)

# Load the image
try:
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: OpenCV failed to load image from: {image_path}")
        sys.exit(1)

    # Print image info for debugging
    print(f"Image shape: {img.shape}, dtype: {img.dtype}")

    # Convert to grayscale - the detector requires a grayscale image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print(f"Grayscale image shape: {gray.shape}")

    # Initialize the AprilTag detector with various parameters
    at_detector = Detector(
        families="tag36h11",
        nthreads=1,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=1,
        decode_sharpening=0.25,
        debug=0,
    )

    detections = at_detector.detect(
        gray, estimate_tag_pose=False, camera_params=None, tag_size=0.0
    )
    print(f"Detected {len(detections)} AprilTags in the image.")
except Exception as e:
    print(f"Error processing image: {e}")
    sys.exit(1)

# Visualize the results if tags are detected
try:
    if len(detections) > 0:
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

            # Print additional information
            print(f"Tag ID: {detection.tag_id}")
            print(f"Tag Family: {detection.tag_family}")
            print(f"Center: ({detection.center[0]:.2f}, {detection.center[1]:.2f})")
            print(f"Decision margin: {detection.decision_margin}")

        # Display the result
        cv2.imshow("AprilTag Detection", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No AprilTags detected in the image.")
