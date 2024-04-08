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
    "Select the position value:", min_value=1.0, max_value=2.0, value=1.5
)

# Publish button
if st.button("Send Command"):
    if not pico_id or not HIVEMQ_HOST or not HIVEMQ_USERNAME or not HIVEMQ_PASSWORD:
        st.error("Please enter all required fields.")
    else:
        command_topic = f"digital-pipette/picow/{pico_id}/L16-R"
        client = mqtt.Client(paho.CallbackAPIVersion.VERSION1, protocol=paho.MQTTv5)
        client.tls_set()
        client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
        client.connect(HIVEMQ_HOST, PORT, 60)

        command = {"position": position}
        client.publish(command_topic, json.dumps(command), qos=1)
        client.disconnect()

        st.success(f"Command sent: {command} to topic {command_topic}")
