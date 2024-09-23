import paho.mqtt.client as paho
import time
import json
import threading
import matplotlib.pyplot as plt
from queue import Queue
import numpy as np
from PIL import Image
import io
import base64

response_queues = {}

def on_connect(client, userdata, flags, rc, properties=None):
	print("Connection recieved")

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
	print("mid: " + str(mid))

def on_message(client, userdata, msg):
	if msg.topic not in response_queues:
		response_queues[msg.topic] = Queue()
	response_queues[msg.topic].put(msg)

class CobotMQTTClient:
    
    def __init__(
		self,
		hive_mq_username: str,
		hive_mq_password: str,
		hive_mq_cloud: str,
        cobot_id: str,
		port: int = 8883
	):
        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_publish = on_publish

        self.client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(hive_mq_username, hive_mq_password)
        self.client.connect(hive_mq_cloud, port)

        self.base_endpoint = f"cobot280pi/{cobot_id}/"
        self.client.subscribe(self.base_endpoint + "response/query/angles", qos=2)
        self.client.subscribe(self.base_endpoint + "response/query/coords", qos=2)
        self.client.subscribe(self.base_endpoint + "response/query/camera", qos=2)
        self.client.subscribe(self.base_endpoint + "response/control/angles", qos=2)
        self.client.subscribe(self.base_endpoint + "response/control/coords", qos=2)
        self.client.subscribe(self.base_endpoint + "response/control/gripper", qos=2)
        
        self.client_loop_thread = threading.Thread(target=self.client.loop_forever)
        self.client_loop_thread.start()

    def wait_until_response_recieved(self, response_topic: str):
        while True:
            if response_topic not in response_queues:
                time.sleep(5)
                print("Waiting for response...")
                continue
            
            item = response_queues[response_topic].get()
            return json.loads(item.payload)
        
    def send_angles(
		self,
  		angle_list: list[float] = [0.0] * 6,
    	speed: int = 50
	):
        assert(type(angle_list) == list)
        assert(type(speed) == int)

        payload = json.dumps({"args": {"angles": angle_list, "speed": speed}})
        self.client.publish(self.base_endpoint + "control/angles", payload=payload, qos=2)
        response = self.wait_until_response_recieved(self.base_endpoint + "response/control/angles")
        return response

    def send_coords(
		self,
  		coord_list: list[float] = [0.0] * 6,
    	speed: int = 50
	):
        assert(type(coord_list) == list)
        assert(type(speed) == int)

        payload = json.dumps({"args": {"coords": coord_list, "speed": speed}})
        self.client.publish(self.base_endpoint + "control/coords", payload=payload, qos=2)
        response = self.wait_until_response_recieved(self.base_endpoint + "response/control/coords")
        return response

    def send_gripper_value(
		self,
  		value: int = 100,
    	speed: int = 50
	):
        assert(type(value) == int)
        assert(type(speed) == int)

        payload = json.dumps({"args": {"gripper_value": value, "speed": speed}})
        self.client.publish(self.base_endpoint + "control/gripper", payload=payload, qos=2)
        response = self.wait_until_response_recieved(self.base_endpoint + "response/control/gripper")
        return response

    def get_angles(self):
        payload = json.dumps({"args": {}})
        self.client.publish(self.base_endpoint + "query/angles", payload=payload, qos=2)
        response = self.wait_until_response_recieved(self.base_endpoint + "response/query/angles")
        return response

    def get_coords(self):
        payload = json.dumps({"args": {}})
        self.client.publish(self.base_endpoint + "query/coords", payload=payload, qos=2)
        response = self.wait_until_response_recieved(self.base_endpoint + "response/query/coords")
        return response

    def get_camera(self, save_path=None):
        payload = json.dumps({"args": {}})
        self.client.publish(self.base_endpoint + "query/camera", payload=payload, qos=2)
        response = self.wait_until_response_recieved(self.base_endpoint + "response/query/camera")
        if not response["success"]:
            return response

        b64_bytes = base64.b64decode(response["img_bytes"])
        img_bytes = io.BytesIO(b64_bytes)
        img = Image.open(img_bytes)

        response["image"] = img
        if save_path is not None:
            img.save(save_path)

        return response


if __name__ == "__main__":
    from my_secrets import HIVEMQ_HOST, HIVEMQ_PASSWORD, HIVEMQ_USERNAME, COBOT_ID
    client = CobotMQTTClient(HIVEMQ_USERNAME, HIVEMQ_PASSWORD, HIVEMQ_HOST, COBOT_ID)