import paho.mqtt.client as mqtt
import boto3
import json
from datetime import datetime
import time

from picamera2 import Picamera2
from libcamera import controls, Transform

from my_secrets import (
    CAMERA_READ_ENDPOINT,
    CAMERA_WRITE_ENDPOINT,
    MQTT_PORT,
    MQTT_HOST,
    MQTT_PASSWORD,
    MQTT_USERNAME,
)

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("device.log")],
)
logger = logging.getLogger("device")

def on_message(client, userdata, message):
    data = json.loads(message.payload)
    command = data["command"]

    if command == "capture_image":
        logging.info(f"Received command: {command}")

        # only keeping one local copy at any given time called image.jpg
        file_path = "image.jpeg"

        logging.info("Begin autofocus")
        try:
            picam2.autofocus_cycle()
            logging.info("Successfully finished autofocus")
        except Exception as e:
            logging.error(f"Error autofocusing: {e}")
            return

        logging.info("Start image capture")
        try:
            picam2.capture_file(file_path)
            logging.info("Successfully capture image")
        except Exception as e:
            logging.error(f"Error capturing image: {e}")

        # make sure to setup S3 bucket with ACL and public access so that the link works publically
        # using the current timestamp as the unique object ID
        object_name = datetime.utcnow().strftime("%Y-%m-%d-%H:%M:%S") + ".jpeg"
        logging.info("Begin upload to S3")
        try:
            s3.upload_file(
                file_path, BUCKET_NAME, object_name, ExtraArgs={"ACL": "public-read"}
            )
            logging.info("Successfully uploaded to S3")
        except Exception as e:
            logging.error(f"Error uploading to S3: {e}")

        file_uri = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        logging.info("Begin MQTT publish")
        try:
            client.publish(CAMERA_WRITE_ENDPOINT, json.dumps({"image_url": file_uri}))
            logging.info(f"Published {file_uri} to {CAMERA_WRITE_ENDPOINT}")
        except Exception as e:
            logging.error(f"Error publishing {file_uri} to {CAMERA_WRITE_ENDPOINT}: {e}")

if __name__ == '__main__':
    # RPI Camera
    logging.info("Configuring camera")
    try:
        picam2 = Picamera2()
        picam2.set_controls({"AfMode": "auto"})
        # JPEG quality level (0 is worst, 95 is best)
        picam2.options["quality"] = 90
        config = picam2.create_still_configuration(transform=Transform(vflip=1))
        picam2.configure(config)
        picam2.start()
        logging.info("Successfully configured camera")
    except Exception as e:
        logging.error(f"Error configuring camera: {e}")
        exit(1)

    # AWS S3
    logging.info("Configuring AWS S3")
    try:
        BUCKET_NAME = "jwoo-picam-bucket"
        AWS_REGION = "us-east-1"
        s3 = boto3.client("s3", region_name=AWS_REGION)
        logging.info("Successfully configured AWS S3")
    except Exception as e:
        logging.error(f"Error configuring S3: {e}")
        exit(1)

    # MQTT
    logging.info("Configuring MQTT")
    try:
        client = mqtt.Client()
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
        client.on_message = on_message
        client.connect(MQTT_HOST, MQTT_PORT)
        client.subscribe(CAMERA_READ_ENDPOINT, qos=2)
        logging.info("Successfully configured MQTT")
        client.loop_forever()
    except Exception as e:
        logging.error(f"Error configuring MQTT: {e}")
        exit(1)
