import json
from queue import Queue

import paho.mqtt.client as mqtt
from my_secrets import (
    CAMERA_READ_TOPIC,
    CAMERA_WRITE_TOPIC,
    MQTT_HOST,
    MQTT_PASSWORD,
    MQTT_PORT,
    MQTT_USERNAME,
)

sensor_data_queue: "Queue[dict]" = Queue()


def get_paho_client(
    sensor_data_topic, hostname, username, password=None, port=8883, tls=True
):
    client = mqtt.Client(protocol=mqtt.MQTTv5)  # create new instance

    def on_message(client, userdata, msg):
        sensor_data_queue.put(json.loads(msg.payload))

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc != 0:
            print("Connected with result code " + str(rc))
        client.subscribe(sensor_data_topic, qos=1)

    client.on_connect = on_connect
    client.on_message = on_message

    if tls:
        client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
    client.username_pw_set(username, password)
    client.connect(hostname, port)
    client.subscribe(sensor_data_topic, qos=2)

    return client


def send_and_receive(client, command_topic, msg, queue_timeout=60):
    client.publish(command_topic, msg, qos=2)
    client.loop_start()

    while True:
        sensor_data = sensor_data_queue.get(True, queue_timeout)
        client.loop_stop()
        return sensor_data


# Initialize the MQTT client
client = get_paho_client(
    CAMERA_WRITE_TOPIC, MQTT_HOST, MQTT_USERNAME, password=MQTT_PASSWORD, port=MQTT_PORT
)

# Publish a command message to trigger image capture and wait for the response
command_payload = json.dumps({"command": "capture_image"})
response = send_and_receive(
    client, CAMERA_READ_TOPIC, command_payload, queue_timeout=30
)

# Process the received message
if "image_url" in response:
    print("Received image URL:", response["image_url"])
elif "error" in response:
    print("Error received from device:")
    print("Error:", response.get("error"))
    print("Traceback:", response.get("traceback"))
else:
    print("Unknown message received:", response)

1 + 1
