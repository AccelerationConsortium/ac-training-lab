#!/usr/bin/env python3
"""
Test client that sends capture requests and receives image URIs.
This simulates the notebook/orchestrator behavior.
"""
import json
import time
from queue import Empty, Queue

import paho.mqtt.client as mqtt

# Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883
DEVICE_SERIAL = "test-cam-01"
CAMERA_READ_TOPIC = f"rpi-zero2w/still-camera/{DEVICE_SERIAL}/request"
CAMERA_WRITE_TOPIC = f"rpi-zero2w/still-camera/{DEVICE_SERIAL}/response"

data_queue = Queue()


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✓ Client connected to MQTT broker")
        print(f"  Subscribing to: {CAMERA_WRITE_TOPIC}")
        client.subscribe(CAMERA_WRITE_TOPIC, qos=1)
    else:
        print(f"✗ Connection failed with code {rc}")


def on_message(client, userdata, msg):
    print(f"\n✓ Received response on topic: {msg.topic}")
    print(f"  Payload: {msg.payload.decode()}")

    try:
        data = json.loads(msg.payload)
        print(f"  Parsed data: {data}")
        data_queue.put(data)
        print(f"  Added to queue (queue size: {data_queue.qsize()})")
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON decode error: {e}")


def main():
    print("=" * 60)
    print("Test Camera Client Starting")
    print("=" * 60)
    print(f"MQTT Host: {MQTT_HOST}:{MQTT_PORT}")
    print(f"Device Serial: {DEVICE_SERIAL}")
    print(f"Request Topic: {CAMERA_READ_TOPIC}")
    print(f"Response Topic: {CAMERA_WRITE_TOPIC}")
    print()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="test-client")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        client.loop_start()

        # Give it a moment to connect
        time.sleep(1)

        # Send capture command
        msg = {"command": "capture_image"}
        payload = json.dumps(msg)
        print("Sending capture command...")
        print(f"  Topic: {CAMERA_READ_TOPIC}")
        print(f"  Payload: {payload}")

        result = client.publish(CAMERA_READ_TOPIC, payload, qos=1)
        print(f"  Publish result: {result.rc} (0=success)")

        # Wait for response
        print("\nWaiting for response (timeout: 10s)...")
        try:
            data = data_queue.get(True, 10)
            print("\n✓ SUCCESS! Received response:")
            print(f"  Image URI: {data.get('image_uri')}")
            print(f"  Timestamp: {data.get('timestamp')}")
            print(f"  Device: {data.get('device_serial')}")
        except Empty:
            print("\n✗ TIMEOUT: No response received after 10s")
            print("  Check that device is running and topics match")

    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        client.loop_stop()
        client.disconnect()
        print("\nClient disconnected")


if __name__ == "__main__":
    main()
