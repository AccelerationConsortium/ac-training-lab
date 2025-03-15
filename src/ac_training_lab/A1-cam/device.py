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

# from queue import Queue

# image_uri_queue: "Queue[dict]" = Queue()


def get_paho_client(
    sensor_data_topic, hostname, username, password=None, port=8883, tls=True
):

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)

    def on_message(client, userdata, msg):
        data = json.loads(msg.payload)
        command = data["command"]

        if command == "capture_image":
            file_path = "image.jpeg"

            picam2.autofocus_cycle()
            picam2.capture_file(file_path)

            object_name = datetime.utcnow().strftime("%Y-%m-%d-%H:%M:%S") + ".jpeg"

            s3.upload_file(
                file_path,
                BUCKET_NAME,
                object_name,
                ExtraArgs={"ACL": "public-read"},
            )

            file_uri = (
                f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
            )

            client.publish(CAMERA_WRITE_TOPIC, json.dumps({"image_url": file_uri}))
            print(f"Published image URL: {file_uri}")
        else:
            client.publish(
                CAMERA_WRITE_TOPIC, json.dumps({"error": f"Invalid command: {command}"})
            )

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc != 0:
            print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(sensor_data_topic, qos=1)

    client.on_connect = on_connect
    client.on_message = on_message

    # enable TLS for secure connection
    if tls:
        client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(hostname, port)
    client.subscribe(CAMERA_READ_TOPIC, qos=2)

    return client


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

    client = get_paho_client(
        CAMERA_WRITE_TOPIC, MQTT_HOST, MQTT_USERNAME, password=MQTT_PASSWORD
    )
    print("MQTT client connected successfully.")
    print("Waiting for commands...")
    client.loop_forever()

except Exception as e:
    error_trace = traceback.format_exception(*sys.exc_info())

    error_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
    error_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    error_client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
    error_client.connect(MQTT_HOST, MQTT_PORT)

    error_payload = json.dumps({"error": str(e), "traceback": error_trace})
    error_client.publish(CAMERA_WRITE_TOPIC, error_payload)
    print("Error details published to MQTT.")

    raise Exception(
        "An error occurred. Please check the MQTT topic for details."
    ) from e
