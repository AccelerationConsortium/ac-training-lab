#!/usr/bin/env python3
"""Test MQTT device with authentication"""
import json
import time

import paho.mqtt.client as mqtt

DEVICE_SERIAL = "test-cam-01"
REQUEST_TOPIC = f"rpi-zero2w/still-camera/{DEVICE_SERIAL}/request"
RESPONSE_TOPIC = f"rpi-zero2w/still-camera/{DEVICE_SERIAL}/response"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✓ Device connected successfully as 'device_user'")
        client.subscribe(REQUEST_TOPIC, qos=1)
        print(f"✓ Subscribed to: {REQUEST_TOPIC}")
    else:
        print(f"✗ Connection failed with code {rc}")
        if rc == 5:
            print("  Authentication failed - check username/password")


def on_message(client, userdata, msg):
    print(f"\n✓ Device received request on {msg.topic}")
    try:
        request = json.loads(msg.payload.decode())
        print(f"  Request: {request}")

        # Send response
        response = {
            "status": "success",
            "timestamp": time.time(),
            "message": "Image captured",
            "s3_uri": f"s3://test-bucket/images/test-{int(time.time())}.jpg",
        }

        client.publish(RESPONSE_TOPIC, json.dumps(response), qos=1)
        print(f"✓ Device published response to: {RESPONSE_TOPIC}")
        print(f"  Response: {response}")
    except Exception as e:
        print(f"✗ Error processing message: {e}")


client = mqtt.Client(client_id="test-device")
client.username_pw_set("device_user", "device_pass")
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to broker at localhost:1883 as 'device_user'...")
client.connect("127.0.0.1", 1883, 60)

print("Device is ready and waiting for requests...")
client.loop_forever()
