import paho.mqtt.client as paho
import time
import json
import threading
import matplotlib.pyplot as plt
from queue import Queue
import numpy as np
from PIL import Image

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
		port: int = 8883
	):
        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.on_connect = on_connect
        # client.on_subscribe = on_subscribe
        self.client.on_message = on_message
        self.client.on_publish = on_publish

        self.client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(hive_mq_username, hive_mq_password)
        self.client.connect(hive_mq_cloud, port)

        self.client.subscribe("response/query/angles", qos=2)
        self.client.subscribe("response/query/coords", qos=2)
        self.client.subscribe("response/query/camera", qos=2)
        self.client.subscribe("response/control/angles", qos=2)
        self.client.subscribe("response/control/coords", qos=2)
        self.client.subscribe("response/control/gripper", qos=2)
        
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
        self.client.publish("control/angles", payload=payload, qos=2)
        response = self.wait_until_response_recieved("response/control/angles")
        if not response["success"]:
            print(f"error sending angles: \n{response['error_msg']}")
            return
        print("angles sent successfully")


    def send_coords(
		self,
  		coord_list: list[float] = [0.0] * 6,
    	speed: int = 50
	):
        assert(type(coord_list) == list)
        assert(type(speed) == int)

        payload = json.dumps({"args": {"coords": coord_list, "speed": speed}})
        self.client.publish("control/coords", payload=payload, qos=2)
        response = self.wait_until_response_recieved("response/control/coords")
        if not response["success"]:
            print(f"error sending coords: \n{response['error_msg']}")
            return
        print("coords sent successfully")

    def send_gripper_value(
		self,
  		value: int = 100,
    	speed: int = 50
	):
        assert(type(value) == int)
        assert(type(speed) == int)

        payload = json.dumps({"args": {"value": value, "speed": speed}})
        self.client.publish("control/gripper", payload=payload, qos=2)
        response = self.wait_until_response_recieved("response/control/gripper")
        if not response["success"]:
            print(f"error sending gripper value: \n{response['error_msg']}")
            return
        print("gripper value sent successfully")

    def get_angles(self):
        payload = json.dumps({"args": {}})
        self.client.publish("query/angles", payload=payload, qos=2)
        response = self.wait_until_response_recieved("response/query/angles")
        if not response["success"]:
            print("Error getting angles")
            return None
        array = np.array(response["angles"])
        return array

    def get_coords(self):
        payload = json.dumps({"args": {}})
        self.client.publish("query/coords", payload=payload, qos=2)
        response = self.wait_until_response_recieved("response/query/coords")
        if not response["success"]:
            print("Error getting coords")
            return None
        array = np.array(response["coords"])
        return array

    def get_camera(self):
        payload = json.dumps({"args": {}})
        self.client.publish("query/camera", payload=payload, qos=2)
        response = self.wait_until_response_recieved("response/query/camera")
        if not response["success"]:
            print(f"could not get image with error: \n{response['error_msg']}")
            return None
        array = np.array(response["image_pixels"])
        array_shape = tuple(response["image_shape"])
        array = array.reshape(array_shape)[:, :, ::-1]
        return array


if __name__ == "__main__":
    from my_secrets import HIVEMQ_HOST, HIVEMQ_PASSWORD, HIVEMQ_USERNAME
    client = CobotMQTTClient(HIVEMQ_USERNAME, HIVEMQ_PASSWORD, HIVEMQ_HOST)