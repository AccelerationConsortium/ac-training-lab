# import lookhere
import paho.mqtt.client as mqtt

# Define the MQTT settings
# broker = lookhere.broker
# port = lookhere.port
# username = lookhere.username
# password = lookhere.password

"""
A simple script that subscribes to a topic and prints the received messages.

Useful for debugging and testing the MQTT broker.

Author: Enrui (Edison) Lin
"""

broker = "pio1.local"
port = 1883
username = "pioreactor"
password = "raspberry"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("pioreactor/pio1/Edi/leds/intensity")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()} on topic {msg.topic}")

    payload = msg.payload.decode()
    if msg.topic == "pioreactor/pio1/Edi/temperature_automation":
        print("\n")
        print("Received temperature automation data")
        # Do something with the payload
        print(payload)
        print(payload["target_temperature"])


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username, password)
# client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
client.connect(broker, port, 60)

# Blocking call that processes network traffic,
# dispatches callbacks and handles reconnecting.
client.loop_forever()
