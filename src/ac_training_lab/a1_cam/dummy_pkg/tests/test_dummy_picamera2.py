import os

from picamera2 import Picamera2
from PIL import Image

# Get the directory of this test file
TEST_DIR = os.path.dirname(os.path.abspath(__file__))


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
    # Write test image to the same folder as this test file
    file_path = os.path.join(TEST_DIR, "test_image.jpeg")

    # Verify an image file is created
    picam2.capture_file(file_path)
    assert os.path.exists(file_path), "Expected image file to be created."

    # Verify the contents of the file form a valid image
    with open(file_path, "rb") as f:
        img = Image.open(f)
        assert img.size == (640, 480), "Expected a 640x480 image."
        assert img.mode == "RGB", "Expected the image to be in RGB mode."

    os.remove(file_path)


if __name__ == "__main__":
    test_camera_setup()
    test_capture_file()
    print("All tests passed.")
