from PIL import Image
from utils import setup_logger


# A dummy class for easier testing without physically having the cobot
class DummyCobot:
    def __init__(self):
        self.logger = setup_logger()

    def set_gripper_value(self, **kwargs):
        self.logger.info(f"tried to set gripper value with args {kwargs}")

    def send_angles(self, **kwargs):
        self.logger.info(f"tried to send angles with args {kwargs}")

    def send_coords(self, **kwargs):
        self.logger.info(f"tried to send coords with args {kwargs}")

    def sync_send_angles(self, **kwargs):
        self.logger.info(f"tried to sync send angles with args {kwargs}")

    def sync_send_coords(self, **kwargs):
        self.logger.info(f"tried to sync send coords with args {kwargs}")

    def is_gripper_moving(self, **kwargs):
        self.logger.info(f"tried to check if gripper is moving with args {kwargs}")
        return False  # Always return False for dummy (not moving)

    def release_all_servos(self, **kwargs):
        self.logger.info(f"tried to release all servos with args {kwargs}")

    def get_angles(self, **kwargs):
        self.logger.info(f"tried to get angles with args {kwargs}")
        return [0, 0, 0, 0, 0, 0]

    def get_coords(self, **kwargs):
        self.logger.info(f"tried to get coords with args {kwargs}")
        return [0, 0, 0, 0, 0, 0]

    def get_gripper_value(self, **kwargs):
        self.logger.info(f"tried to get gripper value with args {kwargs}")
        return 0

    def get_camera(self, **kwargs):
        self.logger.info(f"tried to get camera with args {kwargs}")
        return Image.new("RGB", (1920, 1080), color="black")
