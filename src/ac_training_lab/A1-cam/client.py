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


# Publish a command
def send_command(command):
    client.publish(CAMERA_READ_TOPIC, command)
    print(f"Sent command: {command}")


def receive_message(client, userdata, msg):
    # received_message will be the AWS URI
    received_message = msg.payload.decode("utf-8")
    print(f"Received message: {received_message}")
    print("Downloading image:")
    wget.download(received_message)


client = mqtt.Client()

client.on_message = receive_message

client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
client.connect(HIVEMQ_HOST, PORT)
client.subscribe(CLIENT_READ_ENDPOINT, qos=2)

# just request for one image, call more times to get more images
send_command("capture")

client.loop_forever()
