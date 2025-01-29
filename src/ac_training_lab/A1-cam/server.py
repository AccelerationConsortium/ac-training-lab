import paho.mqtt.client as mqtt
import boto3
from datetime import datetime

from picamera2 import Picamera2
from libcamera import controls, Transform

from my_secrets import (
    CAMERA_READ_ENDPOINT,
    CLIENT_READ_ENDPOINT,
    PORT,
    HIVEMQ_HOST,
    HIVEMQ_PASSWORD,
    HIVEMQ_USERNAME,
)


def on_message(client, userdata, msg):
    command = msg.payload.decode("utf-8")
    print(f"Received command: {command}")
    if command == "capture":
        print("Capturing image...")
        # only keeping one local copy at any given time called image.jpg
        file_path = "image.png"

        picam2.autofocus_cycle()
        picam2.capture_file(file_path)

        # using the current timestamp as the unique object ID
        object_name = datetime.utcnow().strftime("%Y-%m-%d-%H:%M:%S") + ".jpg"
        # make sure to setup S3 bucket with ACL and public access so that the link works publically
        s3.upload_file(
            file_path, BUCKET_NAME, object_name, ExtraArgs={"ACL": "public-read"}
        )

        file_uri = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        client.publish(CLIENT_READ_ENDPOINT, file_uri)


# camera setup
picam2 = Picamera2()
picam2.set_controls({"AfMode": "auto"})
picam2.options["compress_level"] = 0
config = picam2.create_still_configuration(transform=Transform(vflip=1))
picam2.configure(config)
picam2.start()

BUCKET_NAME = ""
AWS_REGION = ""
s3 = boto3.client("s3", region_name=AWS_REGION)

# Initialize the MQTT Client
client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
client.on_message = on_message

client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
client.connect(HIVEMQ_HOST, PORT)
client.subscribe(CAMERA_READ_ENDPOINT, qos=2)
client.loop_forever()
