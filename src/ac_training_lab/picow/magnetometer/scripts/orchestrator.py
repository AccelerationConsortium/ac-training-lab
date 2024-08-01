import json
import re
import time

import matplotlib.pyplot as plt
import numpy as np
import paho.mqtt.client as mqtt

HIVEMQ_USERNAME = "sgbaird"
HIVEMQ_PASSWORD = "D.Pq5gYtejYbU#L"
HIVEMQ_HOST = "248cc294c37642359297f75b7b023374.s2.eu.hivemq.cloud"

# MQTT Configuration

PORT = 8883  # Replace with your broker's port
sensor_data_topic = (
    "magnetometer/picow/test-magnetometer/sensor_data"  # Replace with your topic
)
# CA_CERT = "hivemq-com-chain.der"  # Path to your CA certificate

averaging_window = 3  # Number of data points to include in the moving average
data = []

# Matplotlib setup
fig = plt.figure(figsize=(10, 8))
ax1 = fig.add_subplot(211, projection="3d")
ax2 = fig.add_subplot(212)
plt.ion()

point_color = "red"
line_base_color = np.array([0, 0, 1, 1])
start_time = time.time()


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc, properties=None):
    if rc != 0:
        print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(sensor_data_topic, qos=1)


def on_message(client, userdata, msg):
    global data
    payload = msg.payload.decode("utf-8")
    sensor_data = json.loads(payload)

    for entry in sensor_data:
        magx = entry["X"]
        magy = entry["Y"]
        magz = entry["Z"]

        net_magnitude = np.sqrt(magx**2 + magy**2 + magz**2)
        scaled_distance = 1 / np.sqrt(net_magnitude) if net_magnitude != 0 else 0

        current_time = time.time()
        elapsed_time = current_time - start_time

        data.append(
            (
                1 / np.sqrt(abs(magx)) if magx != 0 else 0,
                1 / np.sqrt(abs(magy)) if magy != 0 else 0,
                1 / np.sqrt(abs(magz)) if magz != 0 else 0,
                elapsed_time,
            )
        )

        # Print the received data for debugging
        print(f"Received data: X={magx}, Y={magy}, Z={magz}, Time={elapsed_time}")

        # Filter old data
        data = [(x, y, z, t) for x, y, z, t in data if elapsed_time - t <= 10]

        # Averaging
        xs, ys, zs, ts = zip(*data)
        if len(data) > averaging_window:
            xs = np.convolve(
                xs, np.ones(averaging_window) / averaging_window, mode="valid"
            )
            ys = np.convolve(
                ys, np.ones(averaging_window) / averaging_window, mode="valid"
            )
            zs = np.convolve(
                zs, np.ones(averaging_window) / averaging_window, mode="valid"
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
        distances = [np.sqrt(x**2 + y**2 + z**2) for x, y, z in zip(xs, ys, zs)]
        ax2.clear()
        ax2.plot(ts, distances, "-o", color="blue")
        ax2.set_ylim(0, 1.1)  # Set fixed y-axis limits
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Distance (rel. units)")
        ax2.set_title("Estimated Distance over Time")

        plt.pause(0.01)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
# client.tls_set(CA_CERT)
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
client.on_connect = on_connect
client.on_message = on_message

client.connect(HIVEMQ_HOST, PORT, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    plt.ioff()
    plt.show()
