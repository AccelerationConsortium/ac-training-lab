import paho.mqtt.client as paho
import json, io, base64
from queue import Queue
from PIL import Image


class CobotController:

    def __init__(
        self,
        hive_mq_username: str,
        hive_mq_password: str,
        hive_mq_cloud: str,
        port: int,
        cobot_id: str,
    ):
        self.publish_endpoint = cobot_id
        self.response_endpoint = cobot_id + "/response"
        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.tls_set()
        self.client.username_pw_set(hive_mq_username, hive_mq_password)
        self.client.connect(hive_mq_cloud, port)

        response_queue = Queue()

        def on_message(client, userdata, msg):
            payload_dict = json.loads(msg.payload)
            response_queue.put(payload_dict)

        self.response_queue = response_queue

        def on_connect(client, userdata, flags, rc, properties=None):
            print("Connection recieved")

        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.subscribe(self.response_endpoint, qos=2)
        self.client.loop_start()

    def handle_publish_and_response(self, payload):
        self.client.publish(self.publish_endpoint, payload=payload, qos=2)
        return self.response_queue.get(block=True)

    def send_angles(
        self,
        angle_list: list[float] = [0.0] * 6,
        speed: int = 50
    ):
        payload = json.dumps({"command": "control/angles",
                             "args": {"angles": angle_list, "speed": speed}})
        return self.handle_publish_and_response(payload)

    def send_coords(
        self,
        coord_list: list[float] = [0.0] * 6,
        speed: int = 50
    ):
        payload = json.dumps({"command": "control/coords",
                             "args": {"coords": coord_list, "speed": speed}})
        return self.handle_publish_and_response(payload)

    def send_gripper_value(
        self,
        value: int = 100,
        speed: int = 50
    ):
        payload = json.dumps({"command": "control/gripper",
                             "args": {"gripper_value": value, "speed": speed}})
        return self.handle_publish_and_response(payload)

    def get_angles(self):
        payload = json.dumps({"command": "query/angles", "args": {}})
        return self.handle_publish_and_response(payload)

    def get_coords(self):
        payload = json.dumps({"command": "query/coords", "args": {}})
        return self.handle_publish_and_response(payload)

    def get_gripper_value(self):
        payload = json.dumps({"command": "query/gripper", "args": {}})
        return self.handle_publish_and_response(payload)

    def get_camera(self, quality=100, save_path=None):
        payload = json.dumps({"command": "query/camera", "args": {"quality": quality}})
        response = self.handle_publish_and_response(payload)
        if not response["success"]:
            return response

        b64_bytes = base64.b64decode(response["image"])
        img_bytes = io.BytesIO(b64_bytes)
        img = Image.open(img_bytes)

        response["image"] = img
        if save_path is not None:
            img.save(save_path)

        return response

if __name__ == "__main__":
	from my_secrets import *
    
	cobot = CobotController(
        HIVEMQ_USERNAME,
        HIVEMQ_PASSWORD,
        HIVEMQ_HOST,
        PORT,
        DEVICE_ID
	)