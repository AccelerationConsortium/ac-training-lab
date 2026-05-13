#!/usr/bin/env python3
"""
Mock camera device with MQTT authentication.
Tests username/password authentication and topic ACL filters.
"""
import json
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

# Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_USERNAME = "device_user"
MQTT_PASSWORD = "device_password"
DEVICE_SERIAL = "test-cam-01"
CAMERA_READ_TOPIC = f"rpi-zero2w/still-camera/{DEVICE_SERIAL}/request"
CAMERA_WRITE_TOPIC = f"rpi-zero2w/still-camera/{DEVICE_SERIAL}/response"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✓ Device authenticated and connected")
        print(f"  Username: {MQTT_USERNAME}")
        print(f"  Subscribing to: {CAMERA_READ_TOPIC}")
        result = client.subscribe(CAMERA_READ_TOPIC, qos=1)
        print(f"  Subscribe result: {result}")
    else:
        error_messages = {
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorized",
        }
        print(f"✗ Connection failed: {error_messages.get(rc, f'Unknown error ({rc})')}")


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print(f"✓ Subscription confirmed (QoS: {granted_qos})")


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
            if result.rc == 0:
                print("  ✓ Publish successful")
            else:
                print(f"  ✗ Publish failed: {result.rc}")
        else:
            print(f"  Unknown command: {command}")
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON decode error: {e}")
    except Exception as e:
        print(f"  ✗ Error processing message: {e}")


def main():
    print("=" * 60)
    print("Mock Camera Device with Authentication")
    print("=" * 60)
    print(f"MQTT Host: {MQTT_HOST}:{MQTT_PORT}")
    print(f"Username: {MQTT_USERNAME}")
    print(f"Device Serial: {DEVICE_SERIAL}")
    print(f"Request Topic: {CAMERA_READ_TOPIC}")
    print(f"Response Topic: {CAMERA_WRITE_TOPIC}")
    print()

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, client_id=f"device-{DEVICE_SERIAL}"
    )
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    try:
        print("Connecting to broker...")
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        print("Waiting for capture commands... (Ctrl+C to exit)")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        client.disconnect()
        print("Device disconnected")


if __name__ == "__main__":
    main()
