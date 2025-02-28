import paho.mqtt.client as mqtt
import boto3
import json
from datetime import datetime

from picamera2 import Picamera2
from libcamera import controls, Transform

from my_secrets import (
    CAMERA_READ_ENDPOINT,
    CAMERA_WRITE_ENDPOINT,
    PORT,
    MQTT_HOST,
    MQTT_PASSWORD,
    MQTT_USERNAME,
)


def on_message(client, userdata, msg):
    data = json.loads(message.payload)

    if data["command"] == "capture_image":
        print(f"Received command: {command}")
        # only keeping one local copy at any given time called image.jpg
        file_path = "image.jpeg"

        print("begin autofocus")
        picam2.autofocus_cycle()
        print("finish autofocus")
        print("start capture")
        picam2.capture_file(file_path)
        print("finish capture")

        # using the current timestamp as the unique object ID
        object_name = datetime.utcnow().strftime("%Y-%m-%d-%H:%M:%S") + ".jpeg"
        # make sure to setup S3 bucket with ACL and public access so that the link works publically
        print("begin upload")
        s3.upload_file(
            file_path, BUCKET_NAME, object_name, ExtraArgs={"ACL": "public-read"}
        )
        print("finish upload")

        file_uri = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        client.publish(CAMERA_WRITE_ENDPOINT, json.dumps({"image_url": file_uri}))


# camera setup
picam2 = Picamera2()
picam2.set_controls({"AfMode": "auto"})
# JPEG quality level (0 is worst, 95 is best)
picam2.options["quality"] = 90
config = picam2.create_still_configuration(transform=Transform(vflip=1))
picam2.configure(config)
picam2.start()

BUCKET_NAME = "jwoo-picam-bucket"
AWS_REGION = "us-east-1"
s3 = boto3.client("s3", region_name=AWS_REGION)

# Initialize the MQTT Client
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

client.on_message = on_message
client.connect(MQTT_HOST, PORT)

client.subscribe(CAMERA_READ_ENDPOINT, qos=2)

client.loop_forever()
