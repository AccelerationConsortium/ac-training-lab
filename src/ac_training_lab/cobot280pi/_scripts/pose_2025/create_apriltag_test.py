import cv2
import numpy as np

# Create a blank white image (higher resolution for better detection)
img_size = (1200, 800)
img = np.ones((img_size[1], img_size[0], 3), dtype=np.uint8) * 255


# Function to draw a simplified AprilTag
def draw_apriltag(img, center, tag_id=0):
    tag_size = 200
    margin = tag_size // 10

    # Draw outer black square
    outer_tl = (center[0] - tag_size // 2, center[1] - tag_size // 2)
    outer_br = (center[0] + tag_size // 2, center[1] + tag_size // 2)
    cv2.rectangle(img, outer_tl, outer_br, (0, 0, 0), -1)

    # Draw inner white square with margin
    inner_tl = (outer_tl[0] + margin, outer_tl[1] + margin)
    inner_br = (outer_br[0] - margin, outer_br[1] - margin)
    cv2.rectangle(img, inner_tl, inner_br, (255, 255, 255), -1)

    # Create a 6x6 binary pattern (simplified version of tag36h11)
    # A real AprilTag would have a specific pattern based on ID
    cell_size = (inner_br[0] - inner_tl[0]) // 6

    # Draw a pattern that resembles a tag36h11 tag
    # The corners are always black
    cv2.rectangle(
        img, inner_tl, (inner_tl[0] + cell_size, inner_tl[1] + cell_size), (0, 0, 0), -1
    )  # Top-left
    cv2.rectangle(
        img, (inner_br[0] - cell_size, inner_tl[1]), inner_br, (0, 0, 0), -1
    )  # Top-right
    cv2.rectangle(
        img, (inner_tl[0], inner_br[1] - cell_size), inner_br, (0, 0, 0), -1
    )  # Bottom-right
    cv2.rectangle(
        img, inner_tl, (inner_tl[0] + cell_size, inner_tl[1] + cell_size), (0, 0, 0), -1
    )  # Bottom-left

    # Draw a unique pattern based on tag_id (simplified)
    if tag_id == 0:
        # Pattern for tag ID 0
        cv2.rectangle(
            img,
            (inner_tl[0] + 2 * cell_size, inner_tl[1] + 2 * cell_size),
            (inner_tl[0] + 4 * cell_size, inner_tl[1] + 4 * cell_size),
            (0, 0, 0),
            -1,
        )
    elif tag_id == 1:
        # Pattern for tag ID 1
        cv2.rectangle(
            img,
            (inner_tl[0] + 1 * cell_size, inner_tl[1] + 2 * cell_size),
            (inner_tl[0] + 5 * cell_size, inner_tl[1] + 4 * cell_size),
            (0, 0, 0),
            -1,
        )

    # Add tag ID text below the tag
    cv2.putText(
        img,
        f"Tag ID: {tag_id}",
        (center[0] - 60, center[1] + tag_size // 2 + 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 0),
        2,
    )


# Draw multiple AprilTags
draw_apriltag(img, (img_size[0] // 4, img_size[1] // 2), tag_id=0)
draw_apriltag(img, (3 * img_size[0] // 4, img_size[1] // 2), tag_id=1)

# Add information text
cv2.putText(
    img,
    "Sample AprilTags for Testing",
    (img_size[0] // 2 - 200, 50),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.0,
    (0, 0, 255),
    2,
)
cv2.putText(
    img,
    "Tag Family: tag36h11 (simplified)",
    (img_size[0] // 2 - 200, 90),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0, 0, 0),
    2,
)

# Save the image
output_path = "c:/Users/bairdst4/Documents/GitHub/AccelerationConsortium/ac-training-lab/src/ac_training_lab/cobot280pi/_scripts/apriltag_test_image.jpg"
cv2.imwrite(output_path, img)
print(f"Created test AprilTag image at: {output_path}")
