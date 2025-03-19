import json
import logging
import os
import subprocess
import sys
import threading
import time
import zipfile
from io import BytesIO
from queue import Empty, Queue
from time import sleep

import bambulabs_api as bl
import paho.mqtt.client as mqtt

# set log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("mqtt_client.log"),
    ],
)
logger = logging.getLogger("bambu-mqtt-client")

# MQTT Broker Configuration
MQTT_BROKER = "248cc294c37642359297f75b7b023374.s2.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "sgbaird"
MQTT_PASSWORD = "D.Pq5gYtejYbU#L"

SERIAL = os.environ.get("BAMBU_SERIAL", "0309CA471800852")

REQUEST_TOPIC = f"bambu_a1_mini/request/{SERIAL}"
RESPONSE_TOPIC = f"bambu_a1_mini/response/{SERIAL}"

# Bambu Lab Printer Configuration
BAMBU_IP = "192.168.1.124"
BAMBU_SERIAL = "0309CA471800852"
BAMBU_ACCESS_CODE = "14011913"

# template file path
TEMPLATE_DIR = "/home/ac/bambu-printer-control/template"

# add global variable to track current template index
CURRENT_TEMPLATE_INDEX = 1
MAX_TEMPLATE_INDEX = 27


# add a function to get the next template index
def get_next_template_index():
    global CURRENT_TEMPLATE_INDEX

    # get current template index
    current_index = CURRENT_TEMPLATE_INDEX

    # update to the next template index
    CURRENT_TEMPLATE_INDEX = (CURRENT_TEMPLATE_INDEX % MAX_TEMPLATE_INDEX) + 1
    logger.info(
        f"template sequence updated: {current_index} -> {CURRENT_TEMPLATE_INDEX}"
    )

    # return current template index
    return current_index


client = mqtt.Client()
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

command_queue = Queue()


def create_zip_archive_in_memory(text_content, text_file_name="file.txt"):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(text_file_name, text_content)
    zip_buffer.seek(0)
    return zip_buffer


def load_gcode_template(template_name):
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    logger.info(f"load G-code template: {template_path}")

    try:
        with open(template_path, "r") as file:
            gcode = file.read()
        return gcode
    except Exception as e:
        logger.error(f"load G-code template failed: {e}")
        return None


# modify G-code template parameters
def modify_gcode_template(gcode, nozzle_temp, bed_temp, print_speed, fan_speed):
    """modify parameters in G-code template, including multiple temperature
    settings and print speed"""
    if not gcode:
        return None

    logger.info(
        f"modify G-code parameters: nozzle temperature={nozzle_temp}, bed temperature={bed_temp}, print speed={print_speed}, fan speed={fan_speed}"  # noqa E501
    )

    # replace nozzle temperature parameter (two places)
    # 1. regular layer nozzle temperature
    if "; nozzle_temperature = 220" in gcode:
        gcode = gcode.replace(
            "; nozzle_temperature = 220", f"; nozzle_temperature = {nozzle_temp}"
        )
        logger.info(f"Replaced nozzle temperature in comments: 220 -> {nozzle_temp}")
    else:
        logger.info("Could not find '; nozzle_temperature = 220' in G-code")

    # 2. initial layer nozzle temperature
    if "; nozzle_temperature_initial_layer = 220" in gcode:
        gcode = gcode.replace(
            "; nozzle_temperature_initial_layer = 220",
            f"; nozzle_temperature_initial_layer = {nozzle_temp}",
        )
        logger.info(
            f"Replaced initial layer nozzle temperature in comments: 220 -> {nozzle_temp}"  # noqa E501
        )
    else:
        logger.info(
            "Could not find '; nozzle_temperature_initial_layer = 220' in G-code"
        )

    # replace bed temperature parameter (two places)
    # 1. regular layer bed temperature
    if "; textured_plate_temp = 65" in gcode:
        gcode = gcode.replace(
            "; textured_plate_temp = 65", f"; textured_plate_temp = {bed_temp}"
        )
        logger.info(f"Replaced bed temperature in comments: 65 -> {bed_temp}")
    else:
        logger.info("Could not find '; textured_plate_temp = 65' in G-code")

    # 2. initial layer bed temperature
    if "; textured_plate_temp_initial_layer = 65" in gcode:
        gcode = gcode.replace(
            "; textured_plate_temp_initial_layer = 65",
            f"; textured_plate_temp_initial_layer = {bed_temp}",
        )
        logger.info(
            f"Replaced initial layer bed temperature in comments: 65 -> {bed_temp}"
        )
    else:
        logger.info(
            "Could not find '; textured_plate_temp_initial_layer = 65' in G-code"
        )

    # replace temperature settings in M commands
    if "M140 S65" in gcode:
        gcode = gcode.replace("M140 S65", f"M140 S{bed_temp}")  # bed temperature
        logger.info(f"Replaced bed temperature M command: M140 S65 -> M140 S{bed_temp}")
    else:
        logger.info("Could not find 'M140 S65' in G-code")

    if "M109 S200" in gcode:
        gcode = gcode.replace("M109 S200", f"M109 S{nozzle_temp}")  # nozzle temperature
        logger.info(
            f"Replaced nozzle temperature M command: M109 S200 -> M109 S{nozzle_temp}"
        )
    else:
        logger.info("Could not find 'M109 S200' in G-code")

    # NOTE: We no longer modify print speed in G-code
    # Print speed will be set directly via printer.set_print_speed_lvl() API call
    logger.info("Print speed will be set via API call, not in G-code")

    # replace fan setting parameter modify close_fan_the_first_x_layers
    # parameter, allow fan to be on in the first layer
    if "; close_fan_the_first_x_layers = 1" in gcode:
        gcode = gcode.replace(
            "; close_fan_the_first_x_layers = 1", "; close_fan_the_first_x_layers = 0"
        )
        logger.info("Modified fan setting to allow fan on first layer")
    else:
        logger.info("Could not find '; close_fan_the_first_x_layers = 1' in G-code")

    # calculate fan speed value (0-255)
    fan_value = int(fan_speed * 255 / 100)
    logger.info(f"Calculated fan value: {fan_value} (from {fan_speed}%)")

    # new method:
    m981_open_pos = gcode.find("M981 S1 P20000")
    if m981_open_pos != -1:
        logger.info("Found M981 S1 P20000 (open spaghetti detector) section")
        # Add M106 P1 Sn after M981 S1 P20000
        insert_pos = m981_open_pos + len("M981 S1_P20000")
        gcode = gcode[:insert_pos] + f"\nM106 P1 S{fan_value}" + gcode[insert_pos:]
        logger.info(
            f"Added fan control command after M106 P2 S0 in M981 S1 section: M106 P1 S{fan_value}"  # noqa E501
        )
    else:
        logger.info("Could not find M106 P2 S0 after spaghetti detector open command")

    # 2. Find M981 S0 P20000 section (close spaghetti detector)
    m981_close_pos = gcode.find("M981 S0 P20000")
    if m981_close_pos != -1:
        logger.info("Found M981 S0 P20000 (close spaghetti detector) section")
        # Add M106 P1 S0 after M981 S0 P20000
        insert_pos = m981_close_pos + len("M981 S0 P20000")
        gcode = gcode[:insert_pos] + "\nM106 P1 S0" + gcode[insert_pos:]
        logger.info("Added fan off command after M981 S0 section: M106 P1 S0")
    else:
        logger.info("Could not find M981 S0 P20000 (close spaghetti detector) section")

    # Verify temperature settings in G-code
    if f"M140 S{bed_temp}" in gcode:
        logger.info(f"Verified bed temperature in G-code: M140 S{bed_temp}")
    else:
        logger.warning("Could not verify bed temperature in G-code!")

    if f"M109 S{nozzle_temp}" in gcode:
        logger.info(f"Verified nozzle temperature in G-code: M109 S{nozzle_temp}")
    else:
        logger.warning("Could not verify nozzle temperature in G-code!")

    # Check for cooling commands
    if "M104 S0" in gcode:
        logger.info("Verified nozzle cooling command in G-code: M104 S0")
    else:
        logger.warning("Could not find nozzle cooling command (M104 S0) in G-code!")

    if "M140 S0" in gcode:
        logger.info("Verified bed cooling command in G-code: M140 S0")
    else:
        logger.warning("Could not find bed cooling command (M140 S0) in G-code!")

    return gcode


# handle connection
def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(REQUEST_TOPIC)
    logger.info(f"Subscribed to topic: {REQUEST_TOPIC}")

    # send initial status message
    send_status_message("Ready")


# send status message to response topic
def send_status_message(status, additional_data=None):
    message = {
        "status": status,
        "update_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    }

    if additional_data:
        message.update(additional_data)

    client.publish(RESPONSE_TOPIC, json.dumps(message))
    logger.info(f"Sent status message: {status}")


# handle received message
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    logger.info(f"Received message on topic {msg.topic}: {payload}")

    try:
        payload_data = json.loads(payload)

        # add command to queue, but not process immediately
        if isinstance(payload_data, dict):
            command_queue.put(payload_data)
            logger.info(f"Added command to queue: {payload_data}")

        # remove this directly processed code
        # if isinstance(payload_data, dict) and "command" in payload_data:
        #    command = payload_data["command"]
        #
        #    if command == "generate_gcode":
        #        handle_generate_gcode(payload_data)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        send_status_message("Error", {"error": f"JSON decode error: {str(e)}"})


# handle command
def handle_command(command):
    """process commands in the queue"""
    logger.info(f"processing command: {command}")

    if "command" not in command:
        logger.warning("command missing 'command' field")
        return

    cmd_type = command["command"]
    experiment_id = command.get("experiment_id", "unknown")

    logger.info(f"processing {cmd_type} command, experiment ID: {experiment_id}")

    # process command based on command type
    if cmd_type == "generate_gcode":
        handle_generate_gcode(command)
    elif cmd_type == "set_parameters":
        handle_set_parameters(command)
    elif cmd_type == "get_status":
        send_printer_status()
    elif cmd_type == "capture_image":
        # if receive manual capture command, also move nozzle to capture position
        logger.info("received manual capture command, move nozzle to capture position")
        post_print_processing("manual_capture")
    elif cmd_type == "reset_template":
        # process reset template sequence command
        start_index = command.get("start_index", 1)
        reset_template_sequence(start_index)
    else:
        logger.warning(f"unknown command type: {cmd_type}")


# handle generate G-code command
def handle_generate_gcode(payload_data):
    parameters = payload_data.get("parameters", {})
    nozzle_temp = parameters.get("nozzle_temp", 200)
    bed_temp = parameters.get("bed_temp", 60)
    print_speed = parameters.get("print_speed", 60)
    fan_speed = parameters.get("fan_speed", 100)

    # use get_next_template_index() to get current template index
    position = get_next_template_index()

    logger.info(
        f"generating G-code, parameters: nozzle={nozzle_temp}, bed={bed_temp}, speed={print_speed}, fan={fan_speed}, template index={position}"  # noqa E501
    )

    # send processing status
    send_status_message(
        "Processing",
        {
            "nozzle_temperature": nozzle_temp,
            "bed_temperature": bed_temp,
            "template_index": position,
        },
    )

    try:
        # select template file based on template index
        template_name = f"s{position}.gcode"

        # load template file
        gcode = load_gcode_template(template_name)
        if not gcode:
            raise Exception(f"failed to load template: {template_name}")

        # modify template parameters
        modified_gcode = modify_gcode_template(
            gcode, nozzle_temp, bed_temp, print_speed, fan_speed
        )
        if not modified_gcode:
            raise Exception("failed to modify G-code template")

        # send G-code to printer
        send_gcode_to_bambu(modified_gcode, f"print_template_{position}.gcode")

        # send completed status
        send_status_message(
            "Completed",
            {
                "nozzle_temperature": nozzle_temp,
                "bed_temperature": bed_temp,
                "template_index": position,
                "next_template_index": CURRENT_TEMPLATE_INDEX,
            },
        )

    except Exception as e:
        logger.error(f"error generating or sending G-code: {e}")
        send_status_message("Error", {"error": str(e)})


# handle set parameters command
def handle_set_parameters(payload_data):
    parameters = payload_data.get("parameters", {})
    nozzle_temp = parameters.get("nozzle_temp")
    bed_temp = parameters.get("bed_temp")
    print_speed = parameters.get("print_speed")
    fan_speed = parameters.get("fan_speed")

    logger.info(
        f"setting print parameters: nozzle={nozzle_temp}, bed={bed_temp}, speed={print_speed}, fan={fan_speed}"  # noqa E501
    )

    try:
        # connect to printer
        printer = bl.Printer(BAMBU_IP, BAMBU_ACCESS_CODE, BAMBU_SERIAL)
        connected = printer.connect()

        if not connected:
            raise Exception("failed to connect to printer")

        # set parameters
        if nozzle_temp is not None:
            printer.set_nozzle_temperature(nozzle_temp)
            logger.info(f"setting nozzle temperature: {nozzle_temp}")

        if bed_temp is not None:
            printer.set_bed_temperature(bed_temp)
            logger.info(f"setting bed temperature: {bed_temp}")

        if print_speed is not None:
            # convert percentage to speed level (1-5)
            # assume print_speed is 0-100 percentage
            speed_lvl = max(1, min(5, int(print_speed / 20)))
            printer.set_print_speed_lvl(speed_lvl)
            logger.info(
                f"setting print speed level: {speed_lvl} (original value: {print_speed}%)"  # noqa E501
            )

        if fan_speed is not None:
            # set fan speed
            # convert percentage to 0-255 value
            fan_value = int(fan_speed * 255 / 100)
            # send M106 command to control fan
            printer.send_gcode(f"M106 S{fan_value}")
            logger.info(f"setting fan speed: {fan_speed}% (M106 S{fan_value})")

        # send success status
        send_status_message(
            "Parameters_Set",
            {
                "nozzle_temperature": nozzle_temp,
                "bed_temperature": bed_temp,
                "print_speed": print_speed,
                "fan_speed": fan_speed,
            },
        )

    except Exception as e:
        logger.error(f"error setting print parameters: {e}")
        send_status_message("Error", {"error": str(e)})


# get and send printer status
def send_printer_status():
    try:
        # connect to printer
        printer = bl.Printer(BAMBU_IP, BAMBU_ACCESS_CODE, BAMBU_SERIAL)
        printer.connect()

        # get status
        status = printer.get_state()
        nozzle_temp = printer.get_nozzle_temperature()
        bed_temp = printer.get_bed_temperature()
        speed = printer.get_print_speed()

        # send status
        send_status_message(
            status,
            {
                "nozzle_temperature": nozzle_temp,
                "bed_temperature": bed_temp,
                "print_speed": speed,
            },
        )

    except Exception as e:
        logger.error(f"Error getting printer status: {e}")
        send_status_message("Error", {"error": str(e)})


# add a new function, for post-print processing
def post_print_processing(file_name):
    """post-print processing: directly send capture signal"""
    logger.info("starting post-print processing...")

    try:
        # wait for a while to ensure print is really completed
        time.sleep(30)  # wait 30 seconds

        # extract template index information
        template_index = None
        if "print_template_" in file_name:
            try:
                template_index = int(
                    file_name.replace("print_template_", "").replace(".gcode", "")
                )
            except Exception:
                pass

        # directly send capture signal to HF
        logger.info("sending capture signal to HF")
        capture_message = {
            "command": "capture_image",
            "auto_triggered": True,
            "print_job": file_name,
            "template_index": template_index,
            "next_template_index": CURRENT_TEMPLATE_INDEX,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        client.publish(RESPONSE_TOPIC, json.dumps(capture_message))
        logger.info("capture signal sent")

        # send status update
        status_data = {
            "photo_job": file_name,
            "photo_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        if template_index is not None:
            status_data["template_index"] = template_index
            status_data["next_template_index"] = CURRENT_TEMPLATE_INDEX

        send_status_message("Photo_Requested", status_data)

    except Exception as e:
        logger.error(f"error during post-print processing: {e}")
        send_status_message(
            "Error", {"error": f"error during post-print processing: {e}"}
        )


# modify send_gcode_to_bambu function, add post-print processing
def send_gcode_to_bambu(gcode, file_name="print_job.gcode"):
    logger.info(f"Sending G-code to Bambu printer: {file_name}")

    try:
        # save G-code to temporary file
        temp_gcode_path = os.path.join(TEMPLATE_DIR, "temp_print.gcode")
        with open(temp_gcode_path, "w") as f:
            f.write(gcode)

        logger.info(f"Saved G-code to temporary file: {temp_gcode_path}")

        # create a modified version of print.py, using our temporary file
        temp_print_script = os.path.join(TEMPLATE_DIR, "temp_print.py")

        # read original print.py content - from the same directory as mqtt.py,
        # not from template dir
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, "print.py"), "r") as f:
            print_script = f.read()

        # modify INPUT_FILE_PATH and UPLOAD_FILE_NAME
        print_script = print_script.replace(
            "INPUT_FILE_PATH = 's1.gcode'", "INPUT_FILE_PATH = 'temp_print.gcode'"
        )
        print_script = print_script.replace(
            "UPLOAD_FILE_NAME = 's1.gcode'", f"UPLOAD_FILE_NAME = '{file_name}'"
        )

        # Get print_speed from the calling context if available
        print_speed = 60  # Default value

        # Extract print_speed from the calling context if available
        import inspect

        frame = inspect.currentframe()
        try:
            while frame:
                if "print_speed" in frame.f_locals:
                    print_speed = frame.f_locals["print_speed"]
                    break
                frame = frame.f_back
        finally:
            del frame  # Avoid reference cycles

        # Convert print_speed (0-100) to speed level (1-4)
        # 0-25 -> 1, 26-50 -> 2, 51-75 -> 3, 76-100 -> 4
        speed_level = min(4, max(1, int(print_speed / 25) + 1))
        logger.info(
            f"Calculated print speed level: {speed_level} (from {print_speed}%)"
        )

        # save modified script
        with open(temp_print_script, "w") as f:
            f.write(print_script)

        logger.info(f"Created temporary print script: {temp_print_script}")

        # use subprocess to call modified print.py
        logger.info("Executing print script...")

        # switch to template directory and execute script
        current_dir = os.getcwd()
        os.chdir(TEMPLATE_DIR)

        # execute script and capture output
        process = subprocess.Popen(
            ["python", "temp_print.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # get output
        stdout, stderr = process.communicate()

        # switch back to original directory
        os.chdir(current_dir)

        # record output
        logger.info(f"Print script output:\n{stdout}")
        if stderr:
            logger.error(f"Print script errors:\n{stderr}")

        # check if successful
        if "Start Print Command Sent" in stdout:
            logger.info("Print started successfully")

            # After successful print start, set print speed using API
            try:
                # Connect to printer
                printer = bl.Printer(BAMBU_IP, BAMBU_ACCESS_CODE, BAMBU_SERIAL)
                connected = printer.connect()

                if connected:
                    # Set print speed level (1-4)
                    printer.set_print_speed_lvl(speed_level)
                    logger.info(
                        f"Successfully set print speed level to {speed_level} via API"
                    )
                else:
                    logger.error("Failed to connect to printer to set print speed")
            except Exception as e:
                logger.error(f"Error setting print speed: {e}")

            # parse printer status
            status_line = None
            for line in stdout.split("\n"):
                if "Printer status:" in line and "Bed temp:" in line:
                    status_line = line
                    break

            if status_line:
                # parse status line
                parts = status_line.split(",")
                status = parts[0].split(":")[1].strip()
                bed_temp = float(parts[1].split(":")[1].strip())
                nozzle_temp = float(parts[2].split(":")[1].strip())
                # speed = int(parts[3].split(":")[1].strip())

                # send status
                send_status_message(
                    "Printing",
                    {
                        "status": status,
                        "nozzle_temperature": nozzle_temp,
                        "bed_temperature": bed_temp,
                        "print_speed": speed_level,  # Use the speed level we set
                    },
                )

                # start a thread to execute post-print processing
                # using thread to avoid blocking main MQTT loop
                post_process_thread = threading.Thread(
                    target=post_print_processing, args=(file_name,)
                )
                # set as daemon thread, so it will exit when main program exits
                post_process_thread.daemon = True
                post_process_thread.start()
                logger.info("started post-print processing thread")

            else:
                # if cannot parse status, send a basic status
                send_status_message(
                    "Printing",
                    {
                        "status": "PRINTING",
                        "nozzle_temperature": 0,
                        "bed_temperature": 0,
                        "print_speed": speed_level,  # Use the speed level we set
                    },
                )
        else:
            logger.error("Failed to start print")
            send_status_message("Error", {"error": "Failed to start print"})

        # clean up temporary files
        try:
            os.remove(temp_gcode_path)
            os.remove(temp_print_script)
            logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {e}")

    except Exception as e:
        logger.error(f"Error sending G-code to printer: {e}")
        send_status_message("Error", {"error": str(e)})


# bind MQTT events
client.on_connect = on_connect
client.on_message = on_message


# main loop
def main():
    try:
        logger.info(f"Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_start()  # use non-blocking mode

        # Keep protocol active
        while True:
            try:
                command = command_queue.get(timeout=1)
                logger.info(f"Processing command from queue: {command}")

                if "command" in command:
                    try:
                        handle_command(command)
                    except Exception as e:
                        logger.error(f"Error processing command: {e}")
                else:
                    logger.info(f"Skipping command without required fields: {command}")
            except Empty:
                # queue is empty, continue loop
                pass
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")

            sleep(1)

    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        time.sleep(10)  # wait 10 seconds and retry
        main()


# add a function to reset template sequence
def reset_template_sequence(start_index=1):
    global CURRENT_TEMPLATE_INDEX

    old_index = CURRENT_TEMPLATE_INDEX
    CURRENT_TEMPLATE_INDEX = start_index
    logger.info(f"template sequence reset: {old_index} -> {CURRENT_TEMPLATE_INDEX}")

    send_status_message(
        "Template_Reset",
        {"old_template_index": old_index, "new_template_index": CURRENT_TEMPLATE_INDEX},
    )

    return CURRENT_TEMPLATE_INDEX


if __name__ == "__main__":
    main()
