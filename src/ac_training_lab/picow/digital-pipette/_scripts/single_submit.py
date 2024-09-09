"""This streamlit implementation is preferred over the gradio implementation"""

import json

import paho.mqtt.client as mqtt

# MQTT Configuration
HIVEMQ_HOST = ""
HIVEMQ_USERNAME = ""
HIVEMQ_PASSWORD = ""
PORT = 8883

# User input for the Pico ID
pico_id = ""

# Slider for position value
position = 1.35


def send_command(client, pico_id, position):
    # Topic
    command_topic = f"digital-pipette/picow/{pico_id}/L16-R"

    # Create and send command
    command = {"position": position}
    client.publish(command_topic, json.dumps(command), qos=1)

    return f"Command sent: {command} to topic {command_topic}"


# Initialize MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
client.tls_set()
client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
client.connect(HIVEMQ_HOST, PORT, 60)

success_msg = send_command(client, pico_id, position)

client.disconnect()
