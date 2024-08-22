# generate a jwt
# hive mq api to add this jwt to the list of tokens
# expire this token after a given timeframe with api

# mqtt to the microscope commands with attached credentials
# recieve returned mqtt/stored images

# recieve the payload
# execute the command
# return the images/store them etc

import base64
import json
import time
from io import BytesIO
from queue import Queue

import paho.mqtt.client as mqtt
from PIL import Image

# microscope1
# microscope2
# deltastagereflection
# deltastagetransmission


class MicroscopeDemo:
    def __init__(self, host, port, username, password, microscope):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.microscope = microscope

        self.client = mqtt.Client()
        self.client.tls_set()
        self.client.username_pw_set(self.username, self.password)

        self.receiveq = Queue()

        def on_message(client, userdata, message):
            received = json.loads(message.payload.decode("utf-8"))
            self.receiveq.put(received)
            if len(json.dumps(received)) <= 300:
                print(received)
            else:
                try:
                    print(json.dumps(received)[:300] + "...")
                except Exception as e:
                    print(f"Command printing error (program will continue): {e}")

        self.client.on_message = on_message

        self.client.connect(self.host, port=self.port, keepalive=60, bind_address="")

        self.client.loop_start()

        self.client.subscribe(self.microscope + "/return", qos=2)

    def scan_and_stitch(self, c1, c2, ov=1200, foc=0):  # WIP
        command = json.dumps(
            {"command": "scan_and_stitch", "c1": c1, "c2": c2, "ov": ov, "foc": foc}
        )
        self.client.publish(
            self.microscope + "/command", payload=command, qos=2, retain=False
        )
        while self.receiveq.empty():
            time.sleep(0.05)
        image = self.receiveq.get()
        image_string = image["image"]
        image_bytes = base64.b64decode(image_string)
        image_object = Image.open(BytesIO(image_bytes))
        return image_object

    def move(self, x, y, z=False, relative=False):
        """moves to given coordinates x, y (and z if it is set to any integer
        value, if it is set to False the z value wont change). If relative is
        True, then it will move relative to the current position instead of
        moving to the absolute coordinates"""
        command = json.dumps(
            {"command": "move", "x": x, "y": y, "z": z, "relative": relative}
        )
        self.client.publish(
            self.microscope + "/command", payload=command, qos=2, retain=False
        )
        while self.receiveq.empty():
            time.sleep(0.05)
        return self.receiveq.get()

    def scan(self, c1, c2, ov=1200, foc=0):
        """returns a list of image objects. Takes images to scan an entire area
        specified by two corners. you can input the corner coordinates as "x1
        y1", "x2, y2" or [x1, y1], [x2, y2]. ov refers to the overlap between
        the images (useful for stitching) and foc refers to how much the
        microscope should focus between images (0 to disable)"""
        command = json.dumps(
            {"command": "scan", "c1": c1, "c2": c2, "ov": ov, "foc": foc}
        )
        self.client.publish(
            self.microscope + "/command", payload=command, qos=2, retain=False
        )
        while self.receiveq.empty():
            time.sleep(0.05)
        image_l = self.receiveq.get()
        image_list = image_l["images"]
        for i in range(len(image_list)):
            image = image_list[i]
            image_bytes = base64.b64decode(image)
            image_object = Image.open(BytesIO(image_bytes))
            image_list[i] = image_object
        return image_list

    def focus(
        self, amount="fast"
    ):  # focuses by different amounts: huge, fast, medium, fine, or any integer value
        command = json.dumps({"command": "focus", "amount": amount})
        self.client.publish(
            self.microscope + "/command", payload=command, qos=2, retain=False
        )
        while self.receiveq.empty():
            time.sleep(0.05)
        return self.receiveq.get()

    def get_pos(
        self,
    ):  # returns a dictionary with x, y, and z coordinates eg. {'x':1,'y':2,'z':3}
        command = json.dumps({"command": "get_pos"})
        self.client.publish(
            self.microscope + "/command", payload=command, qos=2, retain=False
        )
        while self.receiveq.empty():
            time.sleep(0.05)
        pos = self.receiveq.get()
        return pos["pos"]

    def take_image(self):  # returns an image object
        command = json.dumps({"command": "take_image"})
        self.client.publish(
            self.microscope + "/command", payload=command, qos=2, retain=False
        )
        while self.receiveq.empty():
            time.sleep(0.05)
        image = self.receiveq.get()
        image_string = image["image"]
        image_bytes = base64.b64decode(image_string)
        image_object = Image.open(BytesIO(image_bytes))
        return image_object

    def end_connection(self):  # ends the connection
        self.client.loop_stop()
        self.client.disconnect()
