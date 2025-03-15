import os
from PIL import Image
import paho.mqtt.client as mqtt
import wget
from my_secrets import (
    CAMERA_READ_TOPIC,
    CLIENT_READ_ENDPOINT,
    HIVEMQ_HOST,
    HIVEMQ_PASSWORD,
    HIVEMQ_USERNAME,
    PORT,
)


def on_message(client, userdata, msg):
    # received_message will be the AWS URI
    received_message = msg.payload.decode("utf-8")
    print(f"Received message: {received_message}")
    print("Downloading image:")
    filename = wget.download(received_message)
    print(f"\nDownloaded to: {os.path.abspath(filename)}")

    # Open the image automatically (if it's an image)
    try:
        Image.open(filename).show()
    except Exception as e:
        print(f"Could not open file automatically: {e}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)

client.on_message = on_message

client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
client.connect(HIVEMQ_HOST, PORT)
client.subscribe(CLIENT_READ_ENDPOINT, qos=2)

command = "capture"
client.publish(CAMERA_READ_TOPIC, command)
print(f"Published command: {command}")

client.loop_forever()
