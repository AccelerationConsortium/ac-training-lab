import paho.mqtt.client as mqtt
import info
import json
import bambulabs_api as bl
import time

"""
This script listens for messages on a specific MQTT topic and responds with the current status of the printer.

The printer status is retrieved using the BambuLabs API.

A seperate file named info.py is used to store the printer information and MQTT broker details.
It contains the following variables:
    - IP
    - SERIAL
    - ACCESS_CODE
    - MQTT_BROKER
    - MQTT_PORT
    - MQTT_USERNAME
    - MQTT_PASSWORD
    - MQTT_TOPIC_REQUEST
    - MQTT_TOPIC_RESPONSE
    
The bambulabs_api module is required and should be installed via pip. Virtual environment is recommended.

To run in background:
nohup python3 receive.py &
    
Author: Enrui (Edison) Lin
"""

BROKER = info.MQTT_BROKER
PORT = info.MQTT_PORT
TOPIC = info.MQTT_TOPIC_REQUEST
USERNAME = info.MQTT_USERNAME
PASSWORD = info.MQTT_PASSWORD

def on_connect(client, userdata, flags, rc):
    print("Connected to HiveMQ broker with result code " + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(f"Received message: {data}")
    
    # Retrieve printer status
    status = printer.get_state()
    bed_temperature = printer.get_bed_temperature()
    nozzle_temperature = printer.get_nozzle_temperature()
    
    # Prepare response payload
    response = {
        "status": status,
        "bed_temperature": bed_temperature,
        "nozzle_temperature": nozzle_temperature
    }
    
    # Publish the response
    client.publish(info.MQTT_TOPIC_RESPONSE, json.dumps(response))
    print(f"Sent response: {response}")

printer = bl.Printer(info.IP, info.ACCESS_CODE, info.SERIAL)
printer.connect()

time.sleep(5)

print("Connected to printer")
status = printer.get_state()
print(f"Printer status: {status}")
bed_temperature = printer.get_bed_temperature()
print(f"Bed temperature: {bed_temperature}")
nozzle_temperature = printer.get_nozzle_temperature()
print(f"Nozzle temperature: {nozzle_temperature}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()

client.connect(BROKER, PORT, 60)
client.loop_forever()  # Keep listening for messages

    