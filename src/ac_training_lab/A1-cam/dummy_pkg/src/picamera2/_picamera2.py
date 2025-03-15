import logging
from PIL import Image


class Picamera2:
    def set_controls(self, controls):
        logging.info(f"Mock: Setting controls: {controls}")

    def create_still_configuration(self, transform):
        logging.info(f"Mock: Creating still configuration with transform: {transform}")
        return {}

    def configure(self, config):
        logging.info(f"Mock: Configuring camera with config: {config}")

    def start(self):
        logging.info("Mock: Starting camera")

    def autofocus_cycle(self):
        logging.info("Mock: Performing autofocus cycle")

    def capture_file(self, file_path):
        logging.info(f"Mock: Capturing image to file: {file_path}")
        with open(file_path, "wb") as f:
            dummy_image = Image.new("RGB", (640, 480), color="black")
            dummy_image.save(f, "JPEG")
