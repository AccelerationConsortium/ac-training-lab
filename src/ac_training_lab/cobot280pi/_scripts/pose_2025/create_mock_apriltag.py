import cv2
import numpy as np

# Create a blank white image
img_size = (800, 600)
img = np.ones((img_size[1], img_size[0], 3), dtype=np.uint8) * 255

# Draw a mock AprilTag (simplified black square with white square inside)
tag_size = 150
tag_center = (img_size[0] // 3, img_size[1] // 2)

# Draw outer black square
outer_top_left = (tag_center[0] - tag_size // 2, tag_center[1] - tag_size // 2)
outer_bottom_right = (tag_center[0] + tag_size // 2, tag_center[1] + tag_size // 2)
cv2.rectangle(img, outer_top_left, outer_bottom_right, (0, 0, 0), -1)

# Draw inner white square
inner_size = tag_size // 2
inner_top_left = (tag_center[0] - inner_size // 2, tag_center[1] - inner_size // 2)
inner_bottom_right = (tag_center[0] + inner_size // 2, tag_center[1] + inner_size // 2)
cv2.rectangle(img, inner_top_left, inner_bottom_right, (255, 255, 255), -1)

# Draw a second mock AprilTag at a different position
tag_center2 = (img_size[0] * 2 // 3, img_size[1] // 2)

# Outer black square for second tag
outer_top_left2 = (tag_center2[0] - tag_size // 2, tag_center2[1] - tag_size // 2)
outer_bottom_right2 = (tag_center2[0] + tag_size // 2, tag_center2[1] + tag_size // 2)
cv2.rectangle(img, outer_top_left2, outer_bottom_right2, (0, 0, 0), -1)

# Inner white pattern for second tag - different pattern
inner_size2 = tag_size // 2
inner_top_left2 = (tag_center2[0] - inner_size2 // 2, tag_center2[1] - inner_size2 // 2)
inner_bottom_right2 = (
    tag_center2[0] + inner_size2 // 2,
    tag_center2[1] + inner_size2 // 2,
)
cv2.rectangle(img, inner_top_left2, inner_bottom_right2, (255, 255, 255), -1)

# Add some pattern inside the second tag
pattern_size = inner_size2 // 2
pattern_top_left = (
    tag_center2[0] - pattern_size // 2,
    tag_center2[1] - pattern_size // 2,
)
pattern_bottom_right = (
    tag_center2[0] + pattern_size // 2,
    tag_center2[1] + pattern_size // 2,
)
cv2.rectangle(img, pattern_top_left, pattern_bottom_right, (0, 0, 0), -1)

# Add text labels
cv2.putText(
    img,
    "Mock AprilTag 1",
    (tag_center[0] - 70, tag_center[1] + 100),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (0, 0, 0),
    2,
)
cv2.putText(
    img,
    "Mock AprilTag 2",
    (tag_center2[0] - 70, tag_center2[1] + 100),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (0, 0, 0),
    2,
)

# Add title
cv2.putText(
    img,
    "Test Image with Mock AprilTags",
    (img_size[0] // 2 - 150, 50),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0, 0, 255),
    2,
)

# Save the image
output_path = "c:/Users/bairdst4/Documents/GitHub/AccelerationConsortium/ac-training-lab/src/ac_training_lab/cobot280pi/_scripts/mock_apriltags.jpg"
cv2.imwrite(output_path, img)

print(f"Mock AprilTag test image created at: {output_path}")
