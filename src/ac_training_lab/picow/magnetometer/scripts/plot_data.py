import re
import time

import matplotlib.pyplot as plt
import numpy as np
import serial

averaging_window = 5  # Number of data points to include in the moving average

try:
    with serial.Serial("COM14", 9600, timeout=1) as ser:
        data = []
        fig = plt.figure(figsize=(10, 8))

        # Create a 3D subplot for magnetic field visualization with inverse square root scaling
        ax1 = fig.add_subplot(211, projection="3d")

        # Create a 2D subplot for distance vs. time
        ax2 = fig.add_subplot(212)

        plt.ion()

        point_color = "red"
        line_base_color = np.array([0, 0, 1, 1])

        start_time = time.time()

        while True:
            try:
                line = ser.readline().decode("utf-8").strip()
                if not line:
                    continue

                match = re.match(r"X: (.*) uT, Y: (.*) uT, Z: (.*) uT", line)
                if match:
                    magx, magy, magz = map(float, match.groups())

                    net_magnitude = np.sqrt(magx**2 + magy**2 + magz**2)
                    scaled_distance = (
                        1 / np.sqrt(net_magnitude) if net_magnitude != 0 else 0
                    )

                    current_time = time.time()
                    elapsed_time = current_time - start_time

                    # Apply inverse square root scaling and append to data
                    data.append(
                        (
                            1 / np.sqrt(abs(magx)) if magx != 0 else 0,
                            1 / np.sqrt(abs(magy)) if magy != 0 else 0,
                            1 / np.sqrt(abs(magz)) if magz != 0 else 0,
                            elapsed_time,
                        )
                    )

                    # Filter old data
                    data = [
                        (x, y, z, t) for x, y, z, t in data if elapsed_time - t <= 10
                    ]

                    # Averaging
                    xs, ys, zs, ts = zip(*data)
                    if len(data) > averaging_window:
                        xs = np.convolve(
                            xs,
                            np.ones(averaging_window) / averaging_window,
                            mode="valid",
                        )
                        ys = np.convolve(
                            ys,
                            np.ones(averaging_window) / averaging_window,
                            mode="valid",
                        )
                        zs = np.convolve(
                            zs,
                            np.ones(averaging_window) / averaging_window,
                            mode="valid",
                        )
                        ts = ts[
                            -len(xs) :
                        ]  # Adjust time array to match the length of averaged arrays

                    # 3D plot updates with averaged values
                    ax1.clear()
                    ax1.scatter(xs, ys, zs, color=point_color, s=20)

                    for i in range(len(xs) - 1):
                        ax1.plot(
                            [xs[i], xs[i + 1]],
                            [ys[i], ys[i + 1]],
                            [zs[i], zs[i + 1]],
                            color=line_base_color,
                        )

                    # Calculate and average distance
                    distances = [
                        np.sqrt(x**2 + y**2 + z**2) for x, y, z in zip(xs, ys, zs)
                    ]
                    ax2.clear()
                    ax2.plot(ts, distances, "-o", color="blue")
                    ax2.set_ylim(0, 1.1)  # Set fixed y-axis limits
                    ax2.set_xlabel("Time (s)")
                    ax2.set_ylabel("Distance (rel. units)")
                    ax2.set_title("Estimated Distance over Time")

                    plt.pause(0.01)

            except serial.SerialTimeoutException:
                print("Serial timeout occurred, continuing...")
            except ValueError:
                print("Invalid data received, skipping...")

except serial.SerialException as e:
    print(f"Serial port error: {e}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")

finally:
    plt.ioff()
    plt.show()
