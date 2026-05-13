MQTT_HOST = "your-mqtt-host"
MQTT_PORT = 8883  # or 1883
MQTT_USERNAME = "your-username"
MQTT_PASSWORD = "your-password"
DEVICE_SERIAL = "your-device-serial"
CAMERA_READ_TOPIC = f"rpi-zero2w/still-camera/request/{DEVICE_SERIAL}"
CAMERA_WRITE_TOPIC = f"rpi-zero2w/still-camera/response/{DEVICE_SERIAL}"
BUCKET_NAME = "your-bucket-name"
AWS_REGION = "your-region"
AWS_ACCESS_KEY_ID = "your-aws-access-key-id"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-access-key"
IMAGE_QUALITY = (
    85  # JPEG quality (1-100). Lower = smaller file size. 85 gives ~2-3 MB images
)
