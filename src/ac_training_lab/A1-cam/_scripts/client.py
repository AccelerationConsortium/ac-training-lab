import json
import requests
from PIL import Image
import paho.mqtt.client as mqtt
import requests
from my_secrets import (
    CAMERA_READ_TOPIC,
    CAMERA_WRITE_TOPIC,
    MQTT_HOST,
    MQTT_PASSWORD,
    MQTT_USERNAME,
    MQTT_PORT,
)

from queue import Queue

data_queue: "Queue[dict]" = Queue()


def get_paho_client(
    sensor_data_topic, hostname, username, password=None, port=8883, tls=True
):

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5
    )  # create new instance

    def on_message(client, userdata, msg):
        # received_message will be the AWS URI
        print(f"Received payload: {msg.payload}")
        data = json.loads(msg.payload)
        print(f"Parsed data: {data}")
        data_queue.put(data)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc != 0:
            print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(sensor_data_topic, qos=2)

    client.on_connect = on_connect
    client.on_message = on_message

    # enable TLS for secure connection
    if tls:
        client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(hostname, port)
    client.subscribe(sensor_data_topic, qos=2)

    return client


def send_and_receive(client, command_topic, msg, queue_timeout=60):
    payload = json.dumps(msg)
    client.publish(command_topic, payload, qos=2)
    print(f"Published payload: {payload}")

    client.loop_start()

    while True:
        print("Waiting for data...")
        data = data_queue.get(True, queue_timeout)
        client.loop_stop()
        return data


client = get_paho_client(
    CAMERA_WRITE_TOPIC, MQTT_HOST, MQTT_USERNAME, password=MQTT_PASSWORD, port=MQTT_PORT
)

msg = {"command": "capture_image"}

try:
    data = send_and_receive(client, CAMERA_READ_TOPIC, msg, queue_timeout=30)

    image_uri = data["image_uri"]

    response = requests.get(image_uri)
    response.raise_for_status()
    with open("image.jpeg", "wb") as f:
        f.write(response.content)

    print("Opening image...")
    img = Image.open("image.jpeg")
    img.show()
finally:
    client.loop_stop()
    client.disconnect()
    print("Disconnected from MQTT broker")
