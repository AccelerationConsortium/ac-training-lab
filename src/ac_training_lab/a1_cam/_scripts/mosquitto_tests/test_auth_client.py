#!/usr/bin/env python3
"""Test MQTT client with authentication"""
import json
import sys
import time

import paho.mqtt.client as mqtt

DEVICE_SERIAL = "test-cam-01"
REQUEST_TOPIC = f"rpi-zero2w/still-camera/{DEVICE_SERIAL}/request"
RESPONSE_TOPIC = f"rpi-zero2w/still-camera/{DEVICE_SERIAL}/response"

response_received = False


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✓ Client connected successfully as 'client_user'")
        client.subscribe(RESPONSE_TOPIC, qos=1)
        print(f"✓ Subscribed to: {RESPONSE_TOPIC}")
    else:
        print(f"✗ Connection failed with code {rc}")
        if rc == 5:
            print("  Authentication failed - check username/password")


def on_message(client, userdata, msg):
    global response_received
    print(f"\n✓ Client received response on {msg.topic}")
    try:
        response = json.loads(msg.payload.decode())
        print(f"  Response: {response}")
        response_received = True
    except Exception as e:
        print(f"✗ Error processing message: {e}")


client = mqtt.Client(client_id="test-client")
client.username_pw_set("client_user", "client_pass")
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to broker at localhost:1883 as 'client_user'...")
client.connect("127.0.0.1", 1883, 60)
client.loop_start()

# Wait for connection
time.sleep(1)

# Send capture request
request = {"command": "capture", "timestamp": time.time()}

print(f"\n✓ Client publishing request to: {REQUEST_TOPIC}")
print(f"  Request: {request}")
result = client.publish(REQUEST_TOPIC, json.dumps(request), qos=1)
result.wait_for_publish()

# Wait for response
timeout = 5
print(f"\nWaiting up to {timeout}s for response...")
for i in range(timeout * 10):
    if response_received:
        print("\n✓ Test completed successfully!")
        sys.exit(0)
    time.sleep(0.1)

print("\n✗ No response received within timeout")
sys.exit(1)
