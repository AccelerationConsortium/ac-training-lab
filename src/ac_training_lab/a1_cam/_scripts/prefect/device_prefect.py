import os
from datetime import datetime, timezone
from pathlib import Path

import boto3
from libcamera import Transform
from my_secrets import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    BUCKET_NAME,
)
from picamera2 import Picamera2
from prefect import flow


def _configure_picam2() -> Picamera2:
    picam2 = Picamera2()
    picam2.set_controls({"AfMode": "auto"})
    picam2.options["quality"] = 90
    config = picam2.create_still_configuration(transform=Transform(vflip=1))
    picam2.configure(config)
    picam2.start()
    return picam2


class A1CamCapture:
    def __init__(self):
        self.picam2 = _configure_picam2()
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )

    def _capture_image(self) -> str:
        """Instance helper: capture image and upload to S3, returning the object URL."""
        self.picam2.autofocus_cycle()
        self.picam2.capture_file("image.jpeg")
        object_name = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S") + ".jpeg"
        self.s3.upload_file("image.jpeg", BUCKET_NAME, object_name)
        uri = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        print(f"Uploaded image to {uri}")
        return uri

    def cleanup(self):
        self.picam2.stop()
        self.picam2.close()


@flow(description="Capture a Picamera2 image and upload it to S3.")
def capture_image() -> str:
    cam = A1CamCapture()
    try:
        return cam._capture_image()
    finally:
        cam.cleanup()


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[3]
    capture_image.from_source(
        source=str(repo_root),
        entrypoint="src/ac_training_lab/a1_cam/device_prefect.py:capture_image",
    ).deploy(
        name="capture-image",
        description=(
            "Capture a Picamera2 image and upload it to S3 using the configured "
            "bucket."
        ),
        work_pool_name=os.environ.get("PREFECT_WORK_POOL", "a1-cam-pool"),
    )
