import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from queue import Queue
from time import sleep, time

import boto3
import paho.mqtt.client as mqtt
from libcamera import Transform
from my_secrets import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    BUCKET_NAME,
    CAMERA_READ_TOPIC,
    CAMERA_WRITE_TOPIC,
    MQTT_HOST,
    MQTT_PASSWORD,
    MQTT_PORT,
    MQTT_USERNAME,
)
from picamera2 import Picamera2

# Configure logging, useful when running `sudo journalctl -u a1-cam.service -f`,
# as described in README.
# Example log: 2025-03-18 15:00:00 - INFO - Starting camera setup...
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# create a logger with a custom name
logger = logging.getLogger("a1-cam")


command_queue: "Queue[dict]" = Queue()


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)
        command = data["command"]

        if command == "capture_image":
            file_path = "image.jpeg"

            picam2.autofocus_cycle()
            picam2.capture_file(file_path)

            object_name = (
                datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S") + ".jpeg"
            )

            s3.upload_file(file_path, BUCKET_NAME, object_name)

            file_uri = (
                f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
            )

            data = {
                "image_uri": file_uri,
                # "bucket": BUCKET_NAME,
                # "object_name": object_name,
                # "region": AWS_REGION,
            }
            payload = json.dumps(data)
            client.publish(CAMERA_WRITE_TOPIC, payload)
            logger.info(f"Published image URI: {file_uri}")
    except Exception as e:
        client.publish(CAMERA_WRITE_TOPIC, json.dumps({"error": str(e)}))
        logger.error(f"Error: {e}")


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc, properties=None):
    if rc != 0:
        print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(CAMERA_READ_TOPIC, qos=2)


try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)

    client.on_connect = on_connect
    client.on_message = on_message

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
    # set username and password
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    # connect to HiveMQ Cloud, usually on port 8883 for TLS
    client.connect(MQTT_HOST, MQTT_PORT)

    logger.info("Starting camera setup...")
    picam2 = Picamera2()
    picam2.set_controls({"AfMode": "auto"})
    picam2.options["quality"] = 90
    config = picam2.create_still_configuration(transform=Transform(vflip=1))
    picam2.configure(config)
    picam2.start()
    logger.info("Camera configured successfully.")

    logger.info("Setting up AWS S3...")
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
    logger.info("AWS S3 configured successfully.")

    logger.info("MQTT client connected successfully.")
    # Start the MQTT network loop in a separate thread
    client.loop_start()
    logger.info("Waiting for commands...")

    start_time = time()
    # Keep the script running to handle incoming messages
    while True:
        elapsed = round(time() - start_time)
        print(f"Running... Elapsed: {elapsed}s")
        sleep(5)

except Exception as e:
    error_trace = traceback.format_exception(*sys.exc_info())

    error_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
    error_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    error_client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
    error_client.connect(MQTT_HOST, MQTT_PORT)

    error_payload = json.dumps({"error": str(e), "traceback": error_trace})
    error_client.publish(CAMERA_WRITE_TOPIC, error_payload)
    logger.info("Error details published to MQTT.")

    error_client.disconnect()

    raise Exception(
        "An error occurred. Please check the MQTT topic for details."
    ) from e

finally:
    # Gracefully stop
    client.loop_stop()
    client.disconnect()
    logger.info("MQTT client disconnected.")
