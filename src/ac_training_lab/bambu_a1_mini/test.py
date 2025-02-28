import paho.mqtt.client as mqtt
import time
import info
import json

BROKER = info.MQTT_BROKER
PORT = info.MQTT_PORT
TOPIC = info.MQTT_TOPIC_REQUEST
USERNAME = info.MQTT_USERNAME
PASSWORD = info.MQTT_PASSWORD

def on_connect(client, userdata, flags, rc):
    print("Connected to HiveMQ broker with result code " + str(rc))

client = mqtt.Client()
client.on_connect = on_connect
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()

client.connect(BROKER, PORT, 60)

# Sending 5 messages
for i in range(5):
    message = f"Hello MQTT {i+1}"
    client.publish(TOPIC, json.dumps({"message": message}))
    print(f"Sent: {message}")
    time.sleep(2)

client.disconnect()
