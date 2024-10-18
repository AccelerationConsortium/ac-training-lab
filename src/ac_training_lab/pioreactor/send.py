import paho.mqtt.client as mqtt
import json
import lookhere
import time


"""
A simple script that publishes a message to a topic.

Useful for sending commands to the Pioreactor.

Author: Enrui (Edison) Lin
"""

# Define the MQTT broker details
broker = lookhere.broker
port = lookhere.port
topic = 'pioreactor/control'
username = lookhere.username
password = lookhere.password


broker = 'pio1.local'
port = 1883
username = 'pioreactor'
password = 'raspberry'

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic)

def publish_start_stirring():
    # Create the MQTT client
    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
    client.on_connect = on_connect
    # Connect to the broker
    client.connect(broker, port)

    # Create the JSON payload for starting stirring
    payload = {
        "command": "start_stirring"
    }

    # Convert the payload to a JSON string
    payload_str = json.dumps(payload)

    # Publish the message to the topic
    res = client.publish(topic, payload_str)
    print(f"res: {res}")
    print(f"Published command to start stirring")

    # Disconnect from the broker
    client.disconnect()


# Example usage
# publish_start_stirring()  # Set the RPM value to 200 or any value you want

payload = {
    "command": "stop_stirring",
    "reactor": "pio1",
    "experiment": "Edi"
}

payload = {
    "command": "start_stirring",
    "rpm": 300,
    "reactor": "pio1",
    "experiment": "Edi"
}

# payload = {
#     "command": "update_stirring_rpm",
#     "rpm": 1000
# }

# payload = {
#     "command": "set_led_intensity",
#     "brightness": 100
# }

payload = {
    "command": "set_temperature_automation",
    "automation": "only_record_temperature",
    "reactor": "pio1",
    "experiment": "Edi"
}

# payload = {
#     "command": "temp_update",
#     "settings": {
#         "$state": "disconnected"
#     },
#     "reactor": "pio1",
#     "experiment": "Edi"
# }

# payload = {
#     "command": "temp_update",
#     "settings": {
#         "target_temperature": 40
#     },
#     "reactor": "pio1",
#     "experiment": "Edi"
# }

# payload = {
#     "command": "set_temperature_automation",
#     "automation": "thermostat",
#     "temp": 40,
#     "reactor": "pio1",
#     "experiment": "Edi"
# }

payload_str = json.dumps(payload)


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    result = client.publish("pioreactor/Edi/temperature_automation/temperature", payload_str)
    print(f"Send `{payload_str}` to topic `{topic}`")


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()


if __name__ == '__main__':
    run()