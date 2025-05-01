"""
Visualization script for the robotic arm movement path in pose_2025_vial_jubilee.py
This script generates a 3D plot of the coordinates to help visualize the workflow.
"""

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Coordinates from pose_2025_vial_jubilee.py
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

# Extract x, y, z coordinates for plotting
x_coords = [point[0] for point in coordinates]
y_coords = [point[1] for point in coordinates]
z_coords = [point[2] for point in coordinates]

# Create a 3D plot
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection="3d")

# Plot the trajectory path
ax.plot(x_coords, y_coords, z_coords, "b-", linewidth=2, label="Robot Path")

# Plot the individual points
ax.scatter(
    x_coords,
    y_coords,
    z_coords,
    c=range(len(coordinates)),
    cmap="viridis",
    s=100,
    label="Movement Points",
)

# Add point labels for each position
for i, (x, y, z) in enumerate(zip(x_coords, y_coords, z_coords)):
    ax.text(x, y, z, f"  {i+1}", fontsize=12)

# Add a title and labels
ax.set_title("MyCobot 280 Vial Jubilee Workflow Visualization", fontsize=16)
ax.set_xlabel("X-axis (mm)", fontsize=12)
ax.set_ylabel("Y-axis (mm)", fontsize=12)
ax.set_zlabel("Z-axis (mm)", fontsize=12)

# Add a grid
ax.grid(True)

# Add a legend
ax.legend()

# Create a colorbar to show the sequence of movements
scatter = ax.scatter(
    x_coords, y_coords, z_coords, c=range(len(coordinates)), cmap="viridis", s=0
)
cbar = plt.colorbar(scatter, ax=ax, label="Movement Sequence")
cbar.set_ticks(range(len(coordinates)))
cbar.set_ticklabels([f"Position {i+1}" for i in range(len(coordinates))])

# Create a second view from the top (XY plane)
fig2, ax2 = plt.subplots(figsize=(10, 8))
scatter2 = ax2.scatter(
    x_coords, y_coords, c=range(len(coordinates)), cmap="viridis", s=100
)
ax2.plot(x_coords, y_coords, "b-", linewidth=2)

# Add point labels for each position
for i, (x, y) in enumerate(zip(x_coords, y_coords)):
    ax2.text(x, y, f"  {i+1}", fontsize=12)

ax2.set_title("Top-Down View (XY Plane)", fontsize=16)
ax2.set_xlabel("X-axis (mm)", fontsize=12)
ax2.set_ylabel("Y-axis (mm)", fontsize=12)
ax2.grid(True)

# Add a colorbar to the 2D plot
cbar2 = plt.colorbar(scatter2, ax=ax2, label="Movement Sequence")
cbar2.set_ticks(range(len(coordinates)))
cbar2.set_ticklabels([f"Position {i+1}" for i in range(len(coordinates))])

# Add annotations to explain workflow stages
ax.text(18.9, -119.2, 298.4, "  Starting Position", fontsize=10, color="red")
ax.text(75.2, -118.9, 313.5, "  Vial Pickup", fontsize=10, color="red")
ax.text(-21.8, 10.0, 341.7, "  Vial Placement", fontsize=10, color="red")

# Show the plots
plt.tight_layout()
plt.show()

# Uncomment to save the figures
# fig.savefig('vial_jubilee_3d_visualization.png', dpi=300, bbox_inches='tight')
# fig2.savefig('vial_jubilee_2d_visualization.png', dpi=300, bbox_inches='tight')

print("Visualization complete. Close the plot windows to continue.")
