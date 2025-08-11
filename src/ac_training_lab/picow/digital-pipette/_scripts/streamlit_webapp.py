"""This streamlit implementation is preferred over the gradio implementation

(EDIT: 2024-11-01 - Gradio offers easy remote API access, so in general starting
to prefer Gradio)
"""

import json

import paho.mqtt.client as mqtt
import streamlit as st

# Initialize Streamlit app
st.title("Actuator Control Panel")

# MQTT Configuration
HIVEMQ_HOST = st.text_input("Enter your HiveMQ host:", "", type="password")
HIVEMQ_USERNAME = st.text_input("Enter your HiveMQ username:", "")
HIVEMQ_PASSWORD = st.text_input("Enter your HiveMQ password:", "", type="password")
PORT = st.number_input(
    "Enter the port number:", min_value=1, max_value=65535, value=8883
)

# User input for the Pico ID
pico_id = st.text_input("Enter your Pico ID:", "", type="password")

# Slider for position value
position = st.slider(
    "Select the position value:", min_value=1.1, max_value=1.9, value=1.5
)


# singleton: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource
@st.cache_resource
def get_paho_client(hostname, username, password=None, port=8883, tls=True):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc != 0:
            print("Connected with result code " + str(rc))

    client.on_connect = on_connect

    # enable TLS for secure connection
    if tls:
        client.tls_set()
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(hostname, port)
    client.loop_start()  # Use a non-blocking loop

    return client


def send_command(client, pico_id, position):
    # Topic
    command_topic = f"digital-pipette/picow/{pico_id}/L16-R"

    # Create and send command
    command = {"position": position}

    try:
        result = client.publish(command_topic, json.dumps(command), qos=1)
        result.wait_for_publish()  # Ensure the message is sent
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            return f"Command sent: {command} to topic {command_topic}"
        else:
            return f"Failed to send command: {result.rc}"
    except Exception as e:
        return f"An error occurred: {e}"


# Publish button
if st.button("Send Command"):
    if not pico_id or not HIVEMQ_HOST or not HIVEMQ_USERNAME or not HIVEMQ_PASSWORD:
        st.error("Please enter all required fields.")
    else:
        client = get_paho_client(
            HIVEMQ_HOST,
            HIVEMQ_USERNAME,
            password=HIVEMQ_PASSWORD,
            port=int(PORT),
            tls=True,
        )
        success_msg = send_command(client, pico_id, position)
        st.success(success_msg)
