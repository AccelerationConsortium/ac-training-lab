import threading
import io
import time
import queue
import json
import paho.mqtt.client as paho
from my_secrets import *
import base64
import cv2
import numpy as np
from PIL import Image
from utils import setup_logger, truncate_string
from pymycobot.mycobot import MyCobot

logger = setup_logger()

class CobotMQTTServer:
	def __init__(self, client, base_endpoint):
		self.client = client
		self.base_endpoint = base_endpoint
		self.mc = MyCobot("/dev/ttyAMA0", 1000000)
		logger.info("Cobot controller initialized")

		self.message_queue = queue.Queue()
		self.thread = threading.Thread(target=self.queue_thread)
		self.thread.daemon = True
		self.thread.start()
		logger.info("Listening for commands...")

	def queue_thread(self):
		while True:
			item = self.message_queue.get()
			self.handle_message(item)
			self.message_queue.task_done()


	def push_command(self, message):
		self.message_queue.put(message)
		
	def handle_message(self, message):
		split_topic = message.topic.split("/")
		response_topic = "/".join(split_topic[:2] + ["response"] + split_topic[2:])
		response_payload = {}

		try:
			payload = json.loads(message.payload)
		except Exception:
			response_payload["success"] = False
			response_payload["error_msg"] = f"could not parse payload: {truncate_string(message.payload)}"
			logger.critical(response_payload["error_msg"])
			self.client.publish(response_topic, payload=json.dumps(response_payload), qos=2)
			return

		logger.info(f"Processing task with parameters: \n\ttopic: {message.topic}\n\tjson_payload: {payload}")

		if message.topic == self.base_endpoint + 'control/angles':
			status = self.handle_control_angle(payload)
		elif message.topic == self.base_endpoint + 'control/coords':
			status = self.handle_control_coord(payload)
		elif message.topic == self.base_endpoint + "control/gripper":
			status = self.handle_control_gripper(payload)
		elif message.topic == self.base_endpoint + 'query/angles':
			status = self.handle_query_angle(payload)
		elif message.topic == self.base_endpoint + 'query/coords':
			status = self.handle_query_coord(payload)
		elif message.topic == self.base_endpoint + 'query/camera':
			status = self.handle_query_camera(payload)
		else:
			response_payload["success"] = False
			response_payload["error_msg"] = f"unknown topic {message.topic}"
			logger.critical(response_payload["error_msg"])
			self.client.publish(response_topic, payload=json.dumps(response_payload), qos=2)

			return

		response_payload = json.dumps(status)
		self.client.publish(response_topic, payload=response_payload, qos=2)
		logger.info(f"attempted publish on: \n\ttopic: {response_topic}\n\tpayload: {truncate_string(response_payload)}")
	
	def handle_control_gripper(self, payload):
		args = payload["args"]
		try:
			self.mc.set_gripper_value(**args)
			time.sleep(3)
			return {"success": True}
		except Exception as e:
			logger.critical("control gripper error: " + truncate_string(str(e)))
			return {"success": False, "error_msg": str(e)}

	def handle_control_angle(self, payload):
		args = payload["args"]
		try:
			self.mc.send_angles(**args)
			time.sleep(3)
			return {"success": True}
		except Exception as e:
			logger.critical("control angle error: " + truncate_string(str(e)))
			return {"success": False, "error_msg": str(e)}

	def handle_control_coord(self, payload):
		args = payload["args"]
		try:
			self.mc.send_coords(**args)
			time.sleep(3)
			return {"success": True}
		except Exception as e:
			logger.critical("control coords error: " + truncate_string(str(e)))
			return {"success": False, "error_msg": str(e)}

	def handle_query_angle(self, payload):
		args = payload["args"]
		try:
			angles = self.mc.get_angles()
			time.sleep(3)
			if angles is None or len(angles) < 6:
				raise Exception("could not read angle")
			return {"success": True, "angles": angles}
		except Exception as e:
			error_msg = str(e)
			logger.critical(error_msg)
			return {"success": False, "error_msg": truncate_string(error_msg)}

	def handle_query_coord(self, payload):
		args = payload["args"]
		try:
			coords = self.mc.get_coords()
			time.sleep(3)
			if coords is None or len(coords) < 6:
				raise Exception("could not read coord")
			return {"success": True, "coords": coords}
		except Exception as e:
			error_msg = str(e)
			logger.critical(error_msg)
			return {"success": False, "error_msg": truncate_string(error_msg)}

	def handle_query_camera(self, payload, quality=100):
		args = payload["args"]
		try:
			webcam = cv2.VideoCapture(0)
			_, frame = webcam.read()
			webcam.release()

			img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
			compressed_bytes = io.BytesIO()
			img.save(compressed_bytes, format="JPEG", quality=quality)
			compressed_bytes.seek(0)
			byte_str = compressed_bytes.read()

			byte_str_base64 = base64.b64encode(byte_str).decode('utf-8')

			return {
				"success": True,
				"img_bytes": byte_str_base64,
			}
		except Exception as e:
			logger.critical(f"error in camera query: {truncate_string(str(e))}")
			return {"success": False, "error_msg": str(e)}
			


def on_connect(client, userdata, flags, rc, properties=None):
	logger.info("Connection received with code %s." % rc)

def on_publish(client, userdata, mid, properties=None):
	logger.info("Successful publish.")

def on_message(client, userdata, msg):
	if "response" not in msg.topic:
		logger.info(f"Recieved message with: \n\ttopic: {msg.topic}\n\tqos: {msg.qos}\n\tpayload: {truncate_string(msg.payload)}")
		handler.push_command(msg)
	else:
		logger.info(f"recieved response on {msg.topic}")

if __name__ == "__main__":
	client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
	client.on_connect = on_connect
	client.on_message = on_message
	client.on_publish = on_publish

	client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
	client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
	client.connect(HIVEMQ_HOST, 8883)

	base_endpoint = f"cobot280pi/{COBOT_ID}/"
	client.subscribe(base_endpoint + "#", qos=2)

	handler = CobotMQTTServer(client, base_endpoint)
	client.loop_forever()