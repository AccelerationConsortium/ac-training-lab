import json
import os
import subprocess
import sys
import time
import traceback
from queue import Empty, Queue

import paho.mqtt.client as mqtt
from my_secrets import (
    MQTT_BROKER,
    MQTT_PASSWORD,
    MQTT_PORT,
    MQTT_USERNAME,
    REQUEST_TOPIC,
    RESPONSE_TOPIC,
)

command_queue = Queue()
client = mqtt.Client()
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

TEMPLATE_DIR = "/home/ac/ac-training-lab/src/ac_training_lab/bambu_a1_mini/gcode"
CURRENT_TEMPLATE_INDEX = 1
MAX_TEMPLATE_INDEX = 27


def send_status_message(status, additional_data=None):
    message = {"status": status, "update_time": time.strftime("%Y-%m-%d %H:%M:%S")}
    if additional_data:
        message.update(additional_data)
    client.publish(RESPONSE_TOPIC, json.dumps(message))
    print(f"Status message sent: {status}")


def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe(REQUEST_TOPIC)
    send_status_message("Ready")


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode("utf-8"))
    command_queue.put(payload)
    print(f"Command queued: {payload}")


def get_next_template_index():
    global CURRENT_TEMPLATE_INDEX
    current_index = CURRENT_TEMPLATE_INDEX
    CURRENT_TEMPLATE_INDEX = (CURRENT_TEMPLATE_INDEX % MAX_TEMPLATE_INDEX) + 1
    print(f"Template index updated: {current_index} -> {CURRENT_TEMPLATE_INDEX}")
    return current_index


def load_gcode_template(template_name):
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    with open(template_path, "r") as file:
        return file.read()


def modify_gcode_template(gcode, nozzle_temp, bed_temp, print_speed, fan_speed):
    gcode = gcode.replace(
        "; nozzle_temperature = 220", f"; nozzle_temperature = {nozzle_temp}"
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
    #to reduce wait time for low temp
    gcode = gcode.replace("M140 S61 ", f"M140 S{bed_temp}") 
    gcode = gcode.replace("M190 S61", f"M190 S{bed_temp}")  

    gcode = gcode.replace("M109 S220", f"M109 S{nozzle_temp}")
    gcode = gcode.replace("M104 S220", f"M109 S{nozzle_temp}")
    
    return gcode


def send_gcode_to_printer(gcode, file_name="print_job.gcode"):
    temp_gcode_path = os.path.join(TEMPLATE_DIR, "temp_print.gcode")
    with open(temp_gcode_path, "w") as f:
        f.write(gcode)
    subprocess.run(["python", "print.py", temp_gcode_path])


def handle_generate_gcode(command):
    params = command.get("parameters", {})
    position = get_next_template_index()
    send_status_message("Processing", params)
    template_name = f"s{position}.gcode"
    gcode = load_gcode_template(template_name)
    modified_gcode = modify_gcode_template(
        gcode,
        params.get("nozzle_temp", 200),
        params.get("bed_temp", 60),
        params.get("print_speed", 60),
        params.get("fan_speed", 100),
    )
    send_gcode_to_printer(modified_gcode, f"print_template_{position}.gcode")
    send_status_message("Completed", params)


def handle_command(command):
    cmd_type = command.get("command")
    print(f"Processing command: {cmd_type}")

    if cmd_type == "generate_gcode":
        handle_generate_gcode(command)
    elif cmd_type == "set_parameters":
        print(f"Setting parameters: {command.get('parameters', {})}")
    elif cmd_type == "get_status":
        print("Fetching printer status")
    elif cmd_type == "capture_image":
        print("Manual capture command received")
    else:
        print(f"Unknown command: {cmd_type}")


try:
    print(f"Connecting to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.on_connect = on_connect
    client.on_message = on_message

    client.loop_start()
    print("MQTT connection established, starting main loop...")

    while True:
        try:
            command = command_queue.get(timeout=1)
            handle_command(command)
        except Empty:
            continue

except Exception as e:
    error_trace = traceback.format_exception(*sys.exc_info())
    print(f"Error encountered: {e}\n{''.join(error_trace)}")

    try:
        error_client = mqtt.Client()
        error_client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
        error_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        error_client.connect(MQTT_BROKER, MQTT_PORT)

        error_payload = json.dumps({"error": str(e), "traceback": error_trace})
        error_client.publish(RESPONSE_TOPIC, error_payload)
        print("Published detailed error info to MQTT")

    except Exception as mqtt_error:
        print(f"Failed to publish error details to MQTT: {mqtt_error}")

    raise e
