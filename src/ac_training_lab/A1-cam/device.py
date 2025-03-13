import json
import sys
import traceback
from datetime import datetime

import boto3
import paho.mqtt.client as mqtt
from libcamera import Transform
from my_secrets import (
    CAMERA_READ_TOPIC,
    CAMERA_WRITE_TOPIC,
    MQTT_HOST,
    MQTT_PASSWORD,
    MQTT_PORT,
    MQTT_USERNAME,
    BUCKET_NAME,
    AWS_REGION,
)
from picamera2 import Picamera2

try:

    print("Starting camera setup...")
    picam2 = Picamera2()
    picam2.set_controls({"AfMode": "auto"})
    picam2.options["quality"] = 90
    config = picam2.create_still_configuration(transform=Transform(vflip=1))
    picam2.configure(config)
    picam2.start()
    print("Camera configured successfully.")

    print("Setting up AWS S3...")
    s3 = boto3.client("s3", region_name=AWS_REGION)
    print("AWS S3 configured successfully.")

    print("Connecting to MQTT...")
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

    def on_message(client, userdata, message):
        data = json.loads(message.payload)
        command = data.get("command")

        if command == "capture_image":
            file_path = "image.jpeg"

            picam2.autofocus_cycle()
            picam2.capture_file(file_path)

            object_name = datetime.utcnow().strftime("%Y-%m-%d-%H:%M:%S") + ".jpeg"

            s3.upload_file(
                file_path, BUCKET_NAME, object_name, ExtraArgs={"ACL": "public-read"}
            )

            file_uri = (
                f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
            )

            client.publish(CAMERA_WRITE_TOPIC, json.dumps({"image_url": file_uri}))
            print(f"Published image URL: {file_uri}")

    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT)
    client.subscribe(CAMERA_READ_TOPIC, qos=2)
    print("MQTT connection successful. Entering main loop.")

    client.loop_forever()

except Exception as e:
    error_trace = traceback.format_exception(*sys.exc_info())

    error_client = mqtt.Client()
    error_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    error_client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
    error_client.connect(MQTT_HOST, MQTT_PORT)

    error_payload = json.dumps({"error": str(e), "traceback": error_trace})
    error_client.publish(CAMERA_WRITE_TOPIC, error_payload)
    print("Error details published to MQTT.")

    raise Exception(
        "An error occurred. Please check the MQTT topic for details."
    ) from e
