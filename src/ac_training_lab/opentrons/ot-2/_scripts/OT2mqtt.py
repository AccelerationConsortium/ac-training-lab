import json
from queue import Empty, Queue
from time import sleep

import opentrons.execute
import paho.mqtt.client as mqtt

protocol = opentrons.execute.get_protocol_api("2.16")

OT2_SERIAL = "OT2CEP20240218R04"
PICO_ID = "e66130100f895134"

# MQTT Broker Configuration
host = "248cc294c37642359297f75b7b023374.s2.eu.hivemq.cloud"
username = "sgbaird"
password = "D.Pq5gYtejYbU#L"
port = 8883

OT2_COMMAND_TOPIC = f"command/ot2/{OT2_SERIAL}/pipette"
OT2_STATUS_TOPIC = f"status/ot2/{OT2_SERIAL}/complete"
# SENSOR_COMMAND_TOPIC = f"command/picow/{PICO_ID}/as7341/read"
# SENSOR_DATA_TOPIC = f"color-mixing/picow/{PICO_ID}/as7341"

# Initialize MQTT client and sensor data queue
client = mqtt.Client()
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)  # type: ignore
client.username_pw_set(username, password)

command_queue = Queue()


# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code", rc)
    client.subscribe(OT2_COMMAND_TOPIC, qos=2)


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(f"Received message on topic {msg.topic}: {payload}")
    try:
        payload = json.loads(payload)
        if msg.topic == OT2_COMMAND_TOPIC:
            command_queue.put(payload)

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON payload: {e}")


client.on_connect = on_connect
client.on_message = on_message
client.connect(host, port)
client.loop_start()

print("MQTT client connected")

protocol.home()  # home to know MQTT cilent is connected
# Define labware and pipettes

# changed file path before nohup run
with open("ac_color_sensor_charging_port.json") as labware_file1:
    labware_def1 = json.load(labware_file1)
    tiprack_2 = protocol.load_labware_from_definition(labware_def1, 10)

with open("ac_6_tuberack_15000ul.json") as labware_file2:
    labware_def2 = json.load(labware_file2)
    reservoir = protocol.load_labware_from_definition(labware_def2, 3)

plate = protocol.load_labware(load_name="corning_96_wellplate_360ul_flat", location=1)

tiprack_1 = protocol.load_labware(load_name="opentrons_96_tiprack_300ul", location=9)

p300 = protocol.load_instrument(
    instrument_name="p300_single_gen2", mount="right", tip_racks=[tiprack_1]
)

p300.well_bottom_clearance.dispense = 8


print("Labwares loaded")


def mix_color(payload):
    R = payload["command"]["R"]
    Y = payload["command"]["Y"]
    B = payload["command"]["B"]
    mix_well = payload["command"]["well"]
    session_id = payload["session_id"]
    experiment_id = payload["experiment_id"]

    total = int(R + Y + B)
    if total <= 300:
        raise ValueError("The sum of the proportions must be smaller than 300")

    position = ["B1", "B2", "B3"]
    portion = {"B1": R, "B2": Y, "B3": B}
    # total_volume = 280
    red_volume = R  # int(portion["B1"] * total_volume)
    yellow_volume = Y  # int(portion["B2"] * total_volume)
    blue_volume = B  # int(portion["B3"] * total_volume)
    color_volume = {"B1": red_volume, "B2": yellow_volume, "B3": blue_volume}

    # To DO: start the mixing from the color with the smallest volume

    for pos in position:
        if float(portion[pos]) != 0.0:
            p300.pick_up_tip(tiprack_1[pos])
            p300.aspirate(color_volume[pos], reservoir[pos])
            p300.dispense(color_volume[pos], plate[mix_well])
            p300.default_speed = 100  # reduce pipette speed
            p300.blow_out(reservoir["A1"].top(z=-5))
            p300.default_speed = 400  # reset pipette speed
            p300.drop_tip(tiprack_1[pos])

    p300.pick_up_tip(tiprack_2["A2"])
    p300.move_to(plate[mix_well].top(z=3))

    # payloadtosent = json.dumps(payload)
    # print("Sending read command to sensor...")
    # client.publish(SENSOR_COMMAND_TOPIC, payloadtosent, qos=2)

    print("Sending status to HF...")

    payload = (
    f'{{"status": {{"sensor_status":"in_place"}}, '
    f'"experiment_id": "{experiment_id}", '
    f'"session_id": "{session_id}"}}'
)

    client.publish(OT2_STATUS_TOPIC, payload, qos=2)  # send a status message back to HF


def move_sensor_back(payload):
    results_status = payload["command"]["sensor_status"]
    session_id = payload["session_id"]
    experiment_id = payload["experiment_id"]

    p300.drop_tip(tiprack_2["A2"].top(z=-80))
    # protocol.home()

    payload = (
    f'{{"status": {{"sensor_status":"charging"}}, '
    f'"experiment_id": "{experiment_id}", '
    f'"session_id": "{session_id}"}}'
)
    client.publish(OT2_STATUS_TOPIC, payload, qos=2)  # send a status message back to HF

    if results_status == "sensor_timeout":
        protocol.home()


def handle_command(payload):

    if {"R", "Y", "B", "well"}.issubset(payload["command"].keys()):
        print(f"Handling mix command: {payload}")
        mix_color(payload)

    elif {"sensor_status"}.issubset(payload["command"].keys()):
        print("Sensor measure complete")
        move_sensor_back(payload)


print("OT-2 is waiting for command")
protocol.home()  # home to know OT-2 is ready


# Keep protocol active
while True:
    try:
        command = command_queue.get(timeout=1)
        print(f"Processing command from queue: {command}")

        if "command" in command and "experiment_id" in command:
            try:
                handle_command(command)
            except Exception as e:
                print(f"Error processing command: {e}")
    except Empty:

        print("No commands in queue. Waiting...")
    except Exception as e:

        print(f"Unexpected error in main loop: {e}")
    sleep(1)
