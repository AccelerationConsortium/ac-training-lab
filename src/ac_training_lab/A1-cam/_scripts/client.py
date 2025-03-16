import json
import os
from PIL import Image
import paho.mqtt.client as mqtt
import wget
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


def on_message(client, userdata, msg):
    # received_message will be the AWS URI
    print(f"Received message: {msg.payload}")
    image_uri = msg.payload.decode("utf-8")
    data_queue.put(image_uri)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)

client.on_message = on_message

client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_HOST, MQTT_PORT)
client.subscribe(CAMERA_WRITE_TOPIC, qos=2)

client.loop_start()

msg = {"command": "capture_image"}
payload = json.dumps(msg)
client.publish(CAMERA_READ_TOPIC, payload, qos=2)
print(f"Published payload: {payload}")

client.loop_start()

while True:
    queue_timeout = 30
    data = data_queue.get(True, queue_timeout)
    image_uri = data["image_uri"]
    client.loop_stop()

    assert isinstance(image_uri, str), f"Expected string, got {type(image_uri)}"

    print(f"Received image URI: {image_uri}")

    try:
        # Download the image from the URI
        temp_file = wget.download(image_uri)
        print(f"\nDownloaded image to {temp_file}")

        # Open the downloaded image
        Image.open(temp_file).show()

        # remove the temp file
        os.remove(temp_file)
    except Exception as e:
        print(f"Error processing image: {e}")
