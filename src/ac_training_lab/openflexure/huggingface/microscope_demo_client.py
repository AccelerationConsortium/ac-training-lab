import base64
import io
import json
import os
import shutil
import time
from io import BytesIO
from queue import Queue

import paho.mqtt.client as mqtt
from PIL import Image


class MicroscopeDemo:
    def __init__(
        self,
        host,
        port,
        username,
        password,
        microscope,
        path_to_openflexure_stitching="OPTIONAL",
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.microscope = microscope
        self.path_to_openflexure_stitching = path_to_openflexure_stitching

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
                    print(f"Command printing error (program will continue) {e}")

        self.client.on_message = on_message

        self.client.connect(self.host, port=self.port, keepalive=60, bind_address="")

        self.client.loop_start()

        self.client.subscribe(self.microscope + "/return", qos=2)

    def scan_and_stitch(
        self, c1, c2, temp, ov=1200, foc=0, output="Downloads/stitched.jpeg"
    ):
        """takes a scan with the same inputs + 2 more and outputs a stitched
        image. output is the directory the stitched image will go to and temp is
        the temporary directory to stitch the image otherwise it works just like
        scan()"""
        command = json.dumps(
            {"command": "scan", "c1": c1, "c2": c2, "ov": ov, "foc": foc}
        )
        self.client.publish(
            self.microscope + "/command", payload=command, qos=2, retain=False
        )
        while self.receiveq.empty():
            time.sleep(0.05)
        image = self.receiveq.get()
        image_list = image["images"]
        if os.path.isdir(temp):
            shutil.rmtree(temp)
        os.makedirs(temp)
        for i in range(len(image_list)):
            image_bytes = base64.b64decode(image_list[i])
            with io.BytesIO(image_bytes) as buffer:
                img = Image.open(buffer)
                img.save(
                    temp + "/" + str(i) + ".jpeg",
                    format="JPEG",
                    exif=img.info.get("exif"),
                )
        os.system(
            "cd "
            + self.path_to_openflexure_stitching
            + " && python -m venv .venv && .\\.venv\\Scripts\\activate && openflexure-stitch "  # noqa: E501
            + temp
        )
        # edit the cd commands so it can find the stitching program on your
        # machine and make sure that openflexure-stitching is installed

        pos = len(temp)
        for char in ("/", "\\"):
            index = temp.rfind(char)
            if index != -1 and index < pos:
                pos = index
        result = temp[pos + 1 :] if pos < len(temp) else temp

        shutil.move(temp + "/" + result + "_stitched.jpg", output)

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

    def focus(self, amount="fast"):
        """focuses by different amounts: huge, fast, medium, fine, or any
        integer value"""
        command = json.dumps({"command": "focus", "amount": amount})
        self.client.publish(
            self.microscope + "/command", payload=command, qos=2, retain=False
        )
        while self.receiveq.empty():
            time.sleep(0.05)
        return self.receiveq.get()

    def get_pos(
        self,
    ):
        """returns a dictionary with x, y, and z coordinates eg.
        {'x':1,'y':2,'z':3}"""
        command = json.dumps({"command": "get_pos"})
        self.client.publish(
            self.microscope + "/command", payload=command, qos=2, retain=False
        )
        while self.receiveq.empty():
            time.sleep(0.05)
        pos = self.receiveq.get()
        return pos["pos"]

    def take_image(self):
        """returns an image object"""
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
