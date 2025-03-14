#!/usr/bin/env python3
import json
import paho.mqtt.client as mqtt
from my_secrets import (
    CAMERA_READ_TOPIC,
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
)

# Initialize the MQTT client for the orchestrator
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

client.connect(MQTT_HOST, MQTT_PORT, 60)

# Publish a command message to trigger image capture
command_payload = json.dumps({"command": "capture_image"})

client.publish(CAMERA_READ_TOPIC, command_payload, qos=2)
print("Published capture command to", CAMERA_READ_TOPIC)

# Disconnect the client after publishing
client.disconnect()
