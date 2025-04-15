import os

import cv2

# Print current working directory for reference
print(f"Current working directory: {os.getcwd()}")

# Try loading with absolute path
image_path = r"c:\Users\bairdst4\Documents\GitHub\AccelerationConsortium\ac-training-lab\src\ac_training_lab\cobot280pi\_scripts\apriltag-field-image.webp"
print(f"Trying to load image from: {image_path}")
img = cv2.imread(image_path)

if img is not None:
    print(f"Successfully loaded image with shape: {img.shape}")

    # Convert to grayscale and display some pixel values
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print(f"Grayscale image shape: {gray.shape}")
    print(f"First few pixels: {gray[0:5, 0:5]}")

    # Save a test version to verify we can write images
    cv2.imwrite("test_output.jpg", img)
    print("Successfully saved test image")
else:
    print("Failed to load image!")

    # Try listing the directory to see if the file exists
    directory = os.path.dirname(image_path)
    if os.path.exists(directory):
        print(f"Directory exists: {directory}")
        print("Files in directory:")
        for file in os.listdir(directory):
            print(f"  {file}")
    else:
        print(f"Directory does not exist: {directory}")
