import os

import cv2
import numpy as np

# Get the full path to the script and image
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "apriltag-field-image.webp")

print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {script_dir}")
print(f"Image path: {image_path}")
print(f"Image exists: {os.path.exists(image_path)}")

# Try to load the image using cv2.imread
img = cv2.imread(image_path)
if img is not None:
    print(f"Successfully loaded image with OpenCV: shape={img.shape}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print(f"Converted to grayscale: shape={gray.shape}")

    # Save a copy to verify we can process images
    cv2.imwrite(os.path.join(script_dir, "test_grayscale.jpg"), gray)
    print("Saved grayscale test image")
else:
    print("Failed to load image with OpenCV")

    # Try a different approach using binary read
    try:
        with open(image_path, "rb") as f:
            img_data = f.read()
            print(f"Read {len(img_data)} bytes from the image file")

            # Decode using cv2.imdecode
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is not None:
                print(f"Successfully loaded image with imdecode: shape={img.shape}")
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                print(f"Converted to grayscale: shape={gray.shape}")

                # Save a copy to verify we can process images
                cv2.imwrite(os.path.join(script_dir, "test_grayscale_2.jpg"), gray)
                print("Saved grayscale test image (method 2)")
            else:
                print("Failed to decode image with cv2.imdecode")
    except Exception as e:
        print(f"Error reading file: {e}")
