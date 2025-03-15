import os
from PIL import Image
from picamera2 import Picamera2


def test_camera_setup():
    picam2 = Picamera2()
    picam2.start()
    picam2.configure({})
    picam2.set_controls({"AfMode": "auto"})
    picam2.autofocus_cycle()
    config = picam2.create_still_configuration(transform="vflip")
    assert config == {}, "Expected empty config from dummy class"


def test_capture_file():
    picam2 = Picamera2()
    file_path = "test_image.jpeg"
    # Verify an image file is created
    picam2.capture_file(file_path)
    assert os.path.exists(file_path), "Expected image file to be created."

    # Verify the contents of the file form a valid image
    with open(file_path, "rb") as f:
        img = Image.open(f)
        assert img.size == (640, 480), "Expected a 640x480 image."
        assert img.mode == "RGB", "Expected the image to be in RGB mode."

    os.remove(file_path)
