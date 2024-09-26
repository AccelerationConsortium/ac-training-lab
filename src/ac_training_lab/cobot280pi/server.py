from my_secrets import *
from utils import *

import cv2
import time, json, base64, io, sys, argparse
from PIL import Image
from queue import Queue
import paho.mqtt.client as paho
from pymycobot.mycobot import MyCobot

# cli args
parser = argparse.ArgumentParser()
parser.add_argument("--debug", "-d", action="store_true", help="runs in debug mode")

# Cobot action functions
def handle_control_gripper(args, cobot):
    logger.info(f"running command control/gripper with {args}")
    try:
        cobot.set_gripper_value(**args)
        return {"success": True}
    except Exception as e:
        logger.critical(f"control gripper error: {str(e)}")
        return {"success": False, "error_msg": str(e)}

def handle_control_angles(args, cobot):
    logger.info(f"running command control/angle with {args}")
    try:
        cobot.send_angles(**args)
        return {"success": True}
    except Exception as e:
        logger.critical(f"control angle error: {str(e)}")
        return {"success": False, "error_msg": str(e)}

def handle_control_coords(args, cobot):
    logger.info(f"running command control/coord with {args}")
    try:
        cobot.send_coords(**args)
        return {"success": True}
    except Exception as e:
        logger.critical(f"control coords error: {str(e)}")
        return {"success": False, "error_msg": str(e)}

def handle_query_angles(args, cobot):
    logger.info(f"running command query/angle with {args}")
    try:
        angles = cobot.get_angles()
        if angles is None or len(angles) < 6:
            raise Exception("could not read angle")
        return {"success": True, "angles": angles}
    except Exception as e:
        logger.critical(f"query angle error: {str(e)}")
        return {"success": False, "error_msg": str(e)}

def handle_query_coords(args, cobot):
    logger.info(f"running command query/coord with {args}")
    try:
        coords = cobot.get_coords()
        if coords is None or len(coords) < 6:
            raise Exception("could not read coord")
        return {"success": True, "coords": coords}
    except Exception as e:
        logger.critical(f"query coord error: {str(e)}")
        return {"success": False, "error_msg": str(e)}

def handle_query_gripper(args, cobot):
    logger.info(f"running command query/coord with {args}")
    try:
        gripper_pos = cobot.get_gripper_value()
        return {"success": True, "position": gripper_pos}
    except Exception as e:
        logger.critical(f"query gripper error: {str(e)}")
        return {"success": False, "error_msg": str(e)}

def handle_query_camera(args):
    logger.info(f"running command query/camera with {args}")
    try:
        webcam = cv2.VideoCapture(0)
        _, frame = webcam.read()
        webcam.release()

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        compressed_bytes = io.BytesIO()
        img.save(compressed_bytes, format="JPEG", quality=args["quality"])
        compressed_bytes.seek(0)
        byte_str = base64.b64encode(compressed_bytes.read()).decode("utf-8")
        return {"success": True, "image": byte_str}
    except Exception as e:
        logger.critical(f"query camera error: {str(e)}")
        return {"success": False, "error_msg": str(e)}


# MQTT Functions
def on_connect(client, userdata, flags, rc, properties=None):
    logger.info("Connection received with code %s." % rc)

def on_publish(client, userdata, mid, properties=None):
    logger.info("Successful publish.")

def handle_message(msg, cobot):
    # Parse payload to json dict
    try:
        payload_dict = json.loads(msg.payload)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    if "command" not in payload_dict:
        return {
            "success": False,
            "error": "'command' key should be in payload"
        }

    # Match to a command function
    cmd = payload_dict["command"]
    if cmd == "control/angles":
        return handle_control_angles(payload_dict["args"], cobot)
    elif cmd == "control/coords":
        return handle_control_coords(payload_dict["args"], cobot)
    elif cmd == "control/gripper":
        return handle_control_gripper(payload_dict["args"], cobot)
    elif cmd == "query/angles":
        return handle_query_angles(payload_dict["args"], cobot)
    elif cmd == "query/coords":
        return handle_query_coords(payload_dict["args"], cobot)
    elif cmd == "query/gripper":
        return handle_query_gripper(payload_dict["args"], cobot)
    elif cmd == "query/camera":
        return handle_query_camera(payload_dict["args"])
    else:
        return {
            "success": False,
            "error": "invalid command"
        }

if __name__ == "__main__":
    logger = setup_logger()
    task_queue = Queue()
    args = parser.parse_args()

    try:
        cobot = MyCobot("/dev/ttyAMA0", 1000000)
        logger.info("Cobot object initialized...")
    except Exception as e:
        logger.critical(f"could not initialize cobot with error {str(e)}")
        if not args.debug:
            logger.info("exiting...")
            sys.exit(1)
        else:
            cobot = None

    def on_message(client, userdata, msg):
        logger.info(
            f"Recieved message with: \n\ttopic: {msg.topic}\n\tqos: {msg.qos}\n\tpayload: {msg.payload}")
        task_queue.put(msg)

    client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish

    client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
    client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
    client.connect(HIVEMQ_HOST, DEVICE_PORT)
    client.subscribe(DEVICE_ENDPOINT, qos=2)
    client.loop_start()
    logger.info("Ready for tasks...")

    while True:
        msg = task_queue.get()  # blocks if queue is empty
        response_dict = handle_message(msg, cobot)
        client.publish(
            RESPONSE_ENDPOINT,
            qos=2,
            payload=json.dumps(response_dict)
        )
        time.sleep(3)
