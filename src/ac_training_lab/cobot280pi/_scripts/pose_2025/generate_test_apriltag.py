"""
Create a simplified AprilTag image for testing purposes
"""

import os

import cv2
import numpy as np


def create_apriltag_test_image():
    # Create a white background image
    img_size = (800, 600)
    img = np.ones((img_size[1], img_size[0], 3), dtype=np.uint8) * 255

    # Create a simulated AprilTag
    tag_size = 200

    # Position the tag in the center of the image
    center_x = img_size[0] // 2
    center_y = img_size[1] // 2

    # Draw the black outer square
    outer_x1 = center_x - tag_size // 2
    outer_y1 = center_y - tag_size // 2
    outer_x2 = center_x + tag_size // 2
    outer_y2 = center_y + tag_size // 2
    cv2.rectangle(img, (outer_x1, outer_y1), (outer_x2, outer_y2), (0, 0, 0), -1)

    # Draw a white inner square (with a margin)
    margin = tag_size // 10
    inner_x1 = outer_x1 + margin
    inner_y1 = outer_y1 + margin
    inner_x2 = outer_x2 - margin
    inner_y2 = outer_y2 - margin
    cv2.rectangle(img, (inner_x1, inner_y1), (inner_x2, inner_y2), (255, 255, 255), -1)

    # Create a grid pattern similar to AprilTag
    grid_size = 6  # 6x6 grid
    cell_size = (inner_x2 - inner_x1) // grid_size

    # Draw border cells (always black in AprilTags)
    for i in range(grid_size):
        for j in range(grid_size):
            # Draw black border
            if i == 0 or i == grid_size - 1 or j == 0 or j == grid_size - 1:
                cell_x1 = inner_x1 + i * cell_size
                cell_y1 = inner_y1 + j * cell_size
                cell_x2 = cell_x1 + cell_size
                cell_y2 = cell_y1 + cell_size
                cv2.rectangle(
                    img, (cell_x1, cell_y1), (cell_x2, cell_y2), (0, 0, 0), -1
                )

    # Draw a specific pattern in the middle (this one looks like AprilTag ID 0)
    cv2.rectangle(
        img,
        (inner_x1 + 2 * cell_size, inner_y1 + 2 * cell_size),
        (inner_x1 + 4 * cell_size, inner_y1 + 4 * cell_size),
        (0, 0, 0),
        -1,
    )

    # Add informative text
    cv2.putText(
        img,
        "Simulated AprilTag (tag36h11)",
        (center_x - 170, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2,
    )
    cv2.putText(
        img,
        "Tag ID: 0",
        (center_x - 50, center_y + tag_size // 2 + 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 0),
        2,
    )

    return img


def main():
    # Create test image
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(output_dir, "apriltag_test.jpg")

    # Generate the test image
    image = create_apriltag_test_image()

    # Save the image
    cv2.imwrite(output_path, image)

    print(f"Created test AprilTag image at: {output_path}")
    print(f"Now try running: python recognize_apriltag.py {output_path}")


if __name__ == "__main__":
    main()
