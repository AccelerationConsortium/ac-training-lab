#!/usr/bin/env python3
"""
Mock camera device that listens for capture requests and responds with image URIs.
This simulates the Raspberry Pi camera device behavior.
"""
import json
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

# Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883
DEVICE_SERIAL = "test-cam-01"
CAMERA_READ_TOPIC = f"rpi-zero2w/still-camera/{DEVICE_SERIAL}/request"
CAMERA_WRITE_TOPIC = f"rpi-zero2w/still-camera/{DEVICE_SERIAL}/response"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✓ Device connected to MQTT broker")
        print(f"  Subscribing to: {CAMERA_READ_TOPIC}")
        client.subscribe(CAMERA_READ_TOPIC, qos=1)
    else:
        print(f"✗ Connection failed with code {rc}")


def on_message(client, userdata, msg):
    print(f"\n✓ Received message on topic: {msg.topic}")
    print(f"  Payload: {msg.payload.decode()}")

    try:
        data = json.loads(msg.payload)
        command = data.get("command")

        if command == "capture_image":
            print("  Processing capture_image command...")

            # Simulate image capture and S3 upload
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S")
            object_name = f"{timestamp}.jpeg"
            image_uri = f"https://test-bucket.s3.us-east-2.amazonaws.com/{object_name}"

            response = {
                "image_uri": image_uri,
                "timestamp": timestamp,
                "device_serial": DEVICE_SERIAL,
            }

            payload = json.dumps(response)
            print(f"  Publishing response to: {CAMERA_WRITE_TOPIC}")
            print(f"  Response: {payload}")

            result = client.publish(CAMERA_WRITE_TOPIC, payload, qos=1)
            print(f"  Publish result: {result.rc} (0=success)")
        else:
            print(f"  Unknown command: {command}")
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON decode error: {e}")
    except Exception as e:
        print(f"  ✗ Error processing message: {e}")


def main():
    print("=" * 60)
    print("Mock Camera Device Starting")
    print("=" * 60)
    print(f"MQTT Host: {MQTT_HOST}:{MQTT_PORT}")
    print(f"Device Serial: {DEVICE_SERIAL}")
    print(f"Request Topic: {CAMERA_READ_TOPIC}")
    print(f"Response Topic: {CAMERA_WRITE_TOPIC}")
    print()

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, client_id=f"device-{DEVICE_SERIAL}"
    )
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        print("Waiting for capture commands... (Ctrl+C to exit)")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client.disconnect()
        print("Device disconnected")


if __name__ == "__main__":
    main()
