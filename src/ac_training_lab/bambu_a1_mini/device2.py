import os
import sys
import traceback
import paho.mqtt.client as mqtt
import ssl
import logging
import time
import random
import json
from io import BytesIO
import time
import zipfile
import bambulabs_api as bl

from bambulabs_api import states_info

# Replace with your actual HiveMQ Cloud credentials and device ID
# (or import from your own my_secrets.py)
from my_secrets import (
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    RESPONSE_TOPIC,
    REQUEST_TOPIC,
    IP,
    ACCESS_CODE,
    SERIAL,
)

# Configure logging, useful when running `sudo journalctl -u a1-cam.service -f`,
# as described in README.
# Example log: 2025-03-18 15:00:00 - INFO - Starting camera setup...
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# create a logger with a custom name
logger = logging.getLogger("a1-cam")


input_dir = "/home/ac/Documents/GitHub/AccelerationConsortium/ac-training-lab/src/ac_training_lab/bambu_a1_mini/gcode/"  # noqa: E501


env = os.getenv("env", "debug")
plate = os.getenv("plate", "true").lower() == "true"


def create_zip_archive_in_memory(
    text_content: str, text_file_name: str = "file.txt"
) -> BytesIO:
    """
    Create a zip archive in memory

    Args:
        text_content (str): content of the text file
        text_file_name (str, optional): location of the text file.
            Defaults to 'file.txt'.

    Returns:
        io.BytesIO: zip archive in memory
    """
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(text_file_name, text_content)
    zip_buffer.seek(0)
    return zip_buffer


print("Starting bambulabs_api example")
print("Connecting to Bambulabs 3D printer")
print(f"IP: {IP}")
print(f"Serial: {SERIAL}")
print(f"Access Code: {ACCESS_CODE}")

# Create a new instance of the API
printer = bl.Printer(IP, ACCESS_CODE, SERIAL)

# Connect to the Bambulabs 3D printer
printer.connect()

time.sleep(5)


def read_temperature():
    # for demonstration
    return round(25 + random.uniform(-2.0, 2.0), 1)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(REQUEST_TOPIC, qos=1)
    else:
        print(f"Failed to connect. Return code={rc}")


def on_message(client, userdata, msg):
    # we permit a global var for sake of demo'ing pretend hardware
    # normally the "state" would be kept by the device itself (hence one would remove the following line)
    try:
        payload_str = msg.payload.decode().strip().lower()
        print(f"Received command on {msg.topic}: {payload_str}")

        if msg.topic == REQUEST_TOPIC:
            msg_dict = json.loads(payload_str)
            gcode_filename = msg_dict["gcode_filename"]
            initial_layer_speed = float(msg_dict["initial_layer_speed"])
            initial_layer_infill_speed = float(msg_dict["initial_layer_infill_speed"])
            bed_temp = float(msg_dict["bed_temperature"])
            nozzle_temp = float(msg_dict["nozzle_temperature"])
            fan_speed = float(msg_dict["fan_speed"])

            INPUT_FILE_PATH = os.path.join(input_dir, gcode_filename)
            UPLOAD_FILE_NAME = os.path.basename(INPUT_FILE_PATH)

            with open(INPUT_FILE_PATH, "r") as gcode_file:
                gcode = gcode_file.read()

            gcode = gcode.replace(
                "; nozzle_temperature = 220",
                f"; nozzle_temperature = {nozzle_temp}",
            )
            gcode = gcode.replace(
                "; nozzle_temperature_initial_layer = 220",
                f"; nozzle_temperature_initial_layer = {nozzle_temp}",
            )
            gcode = gcode.replace(
                "; textured_plate_temp = 65", f"; textured_plate_temp = {bed_temp}"
            )
            gcode = gcode.replace(
                "; textured_plate_temp_initial_layer = 65",
                f"; textured_plate_temp_initial_layer = {bed_temp}",
            )
            gcode = gcode.replace("M140 S65", f"M140 S{bed_temp}")
            gcode = gcode.replace("M190 S65", f"M190 S{bed_temp}")
            # to reduce wait time for low temp
            gcode = gcode.replace("M140 S61 ", f"M140 S{bed_temp}")
            gcode = gcode.replace("M190 S61", f"M190 S{bed_temp}")

            gcode = gcode.replace("M109 S220", f"M109 S{nozzle_temp}")
            gcode = gcode.replace("M104 S220", f"M109 S{nozzle_temp}")

            gcode_location = "Metadata/plate_1.gcode"
            io_file = create_zip_archive_in_memory(gcode, gcode_location)

            result = printer.upload_file(io_file, UPLOAD_FILE_NAME)
            if "226" not in result:
                print("Error Uploading File to Printer")

            else:
                print("Done Uploading/Sending Start Print Command")
                printer.start_print(UPLOAD_FILE_NAME, 1)
                print("Start Print Command Sent")

            # send message that print has been started
            payload = json.dumps(
                {
                    "printer_state": printer.get_state(),
                    "message": f"Print started with file {UPLOAD_FILE_NAME}",
                    "_input_msg": msg_dict,
                }
            )
            client.publish(RESPONSE_TOPIC, payload, qos=1)

            state = printer.get_state()

            while state not in [
                states_info.GcodeState.IDLE.name,
                states_info.GcodeState.FINISH.name,
                states_info.GcodeState.FAILED.name,
            ]:
                time.sleep(2)
                state = printer.get_state()
                print(f"Printer State: {state}")

            payload = json.dumps({"printer_state": state})
            client.publish(RESPONSE_TOPIC, payload, qos=1)

            # move command
            z_current_lowered = printer.gcode(
                "M17 Z0.4 ; lower z motor current to reduce impact"
            )
            z_moved_high = printer.gcode("G1 Z100.2 F600   ; Move Z very high up")
            z_backed_off = printer.gcode(
                "G1 Z98.2        ; Back off slightly to release pressure"
            )

            restore_z_current = printer.mqtt_client.send_gcode(
                "M17 R ; restore z current", gcode_check=False
            )

            abs_positioning_set = printer.gcode("G90")
            # final_xy_position_set = printer.gcode("G1 X-13 Y180 F3600  ; Final XY position")
            final_xy_position_set = printer.gcode(
                "G1 X15.25 Y154.75 F3600  ; Final XY position"
            )

    except Exception as e:
        client.publish(RESPONSE_TOPIC, json.dumps({"error": str(e)}))
        logger.error(f"Error: {e}")


print("Setting up MQTT Client")
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)

# enable TLS for secure connection
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
# set username and password
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

client.connect(MQTT_HOST, MQTT_PORT)
print("Connected to MQTT Client")
client.subscribe(REQUEST_TOPIC, qos=2)

# Attach callbacks
client.on_connect = on_connect
client.on_message = on_message

# Start the MQTT network loop in a separate thread
client.loop_start()
print("Waiting for commands...")

start_time = time.time()
try:
    # Keep the script running to handle incoming messages
    while True:
        elapsed = round(time.time() - start_time)
        print(f"Running... Elapsed: {elapsed}s")
        time.sleep(10)
        state = printer.get_state()
        bed_temperature = printer.get_bed_temperature()
        nozzle_temperature = printer.get_nozzle_temperature()
        data = {
            "printer_state": state,
            "elapsed_time": elapsed,
            "bed_temp": bed_temperature,
            "nozzle_temp": nozzle_temperature,
        }
        payload = json.dumps(data)
        client.publish(RESPONSE_TOPIC, payload, qos=1)

except Exception as e:
    error_trace = traceback.format_exception(*sys.exc_info())

    error_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
    error_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    error_client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
    error_client.connect(MQTT_HOST, MQTT_PORT)

    error_payload = json.dumps({"error": str(e), "traceback": error_trace})
    error_client.publish(RESPONSE_TOPIC, error_payload)
    logger.info("Error details published to MQTT.")

    error_client.disconnect()

    raise Exception(
        "An error occurred. Please check the MQTT topic for details."
    ) from e

finally:
    # Gracefully stop
    client.loop_stop()
    client.disconnect()
    logger.info("MQTT client disconnected.")
