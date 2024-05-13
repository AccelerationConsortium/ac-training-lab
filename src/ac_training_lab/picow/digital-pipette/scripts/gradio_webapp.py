"""Streamlit implementation is preferred over this gradio implementation"""

import json

import gradio as gr
import paho.mqtt.client as mqtt

# Configuration
HIVEMQ_HOST = "248cc294c37642359297f75b7b023374.s2.eu.hivemq.cloud"
HIVEMQ_USERNAME = "sgbaird"
HIVEMQ_PASSWORD = "D.Pq5gYtejYbU#L"
PORT = 8883  # default port for MQTT over TLS

# Initialize MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
client.tls_set()
client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
client.connect(HIVEMQ_HOST, PORT, 60)


def send_command(pico_id, position):
    # Topic
    command_topic = f"digital-pipette/picow/{pico_id}/L16-R"

    # Create and send command
    command = {"position": position}
    client.publish(command_topic, json.dumps(command), qos=1)
    client.disconnect()

    return f"Command sent: {command} to topic {command_topic}"


# Gradio interface
iface = gr.Interface(
    fn=send_command,
    inputs=[
        gr.Textbox(label="Pico ID"),
        gr.Slider(minimum=0, maximum=2000, step=10, label="Position Value"),
    ],
    outputs="text",
    title="Actuator Control Panel",
    description="Enter your Pico ID and select the position value to control the actuator.",
)

iface.launch()
