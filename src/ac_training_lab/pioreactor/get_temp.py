import asyncio
import json

import lookhere
import paho.mqtt.client as mqtt

# import time


"""
This script demonstrates how to use the Paho MQTT client to
send and receive messages from a broker.

This script sends a request to the Pioreactor to get temperature readings,
and prints the received data.

This script makes the requests asynchronously using the asyncio library.

Author: Enrui (Edison) Lin
"""

BROKER = lookhere.broker
PORT = lookhere.port
REQUEST_TOPIC = "pioreactor/control"
RESPONSE_TOPIC = "pioreactor/temperature"
USERNAME = lookhere.username
PASSWORD = lookhere.password
REQUEST_INTERVAL = 60


# Define the MQTT Client class
class PioreactorMQTTClient:
    def __init__(self, broker, port, request_topic, response_topic):
        self.broker = broker
        self.port = port
        self.request_topic = request_topic
        self.response_topic = response_topic
        self.client = mqtt.Client()

        # Assign callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        """Connect to the MQTT broker and start the background loop."""
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
        self.client.connect(self.broker, self.port)
        self.client.loop_start()  # This starts the loop in a background thread
        print("Connected to MQTT broker")

    def disconnect(self):
        """Disconnect from the MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from MQTT broker")

    def on_connect(self, client, userdata, flags, rc):
        """Callback when the client connects to the broker."""
        if rc == 0:
            print("Connected successfully")
            self.client.subscribe(self.response_topic)
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, message):
        """Handle incoming messages."""
        payload = message.payload.decode("utf-8")
        try:
            data = json.loads(payload)
            print(f"Received temperature data: {data}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON payload received: {payload}")

    async def publish_temperature_request(
        self, experiment, filter_mod_N, lookback, reactor
    ):
        """Publish a temperature request to the request topic."""
        payload = {
            "command": "get_temperature_readings",
            "experiment": experiment,
            "filter_mod": filter_mod_N,
            "lookback": lookback,
            "reactor": reactor,
        }
        payload_str = json.dumps(payload)
        self.client.publish(self.request_topic, payload_str)
        print(f"Published request for temperature readings: {payload_str}")

    async def periodic_temperature_requests(
        self, experiment, filter_mod_N, lookback, interval, reactor
    ):
        """Asynchronously send temperature requests at regular intervals."""
        try:
            while True:
                await self.publish_temperature_request(
                    experiment, filter_mod_N, lookback, reactor
                )
                await asyncio.sleep(
                    interval
                )  # Use asyncio sleep to not block the event loop
        except asyncio.CancelledError:
            print("Periodic temperature request loop cancelled")


# Main function to run the MQTT client asynchronously
async def run_mqtt_client():
    # Initialize the client
    pioreactor_client = PioreactorMQTTClient(
        BROKER, PORT, REQUEST_TOPIC, RESPONSE_TOPIC
    )

    # Connect to the broker
    pioreactor_client.connect()

    # Start the periodic request function
    await pioreactor_client.periodic_temperature_requests(
        "Edi", 1, 10000000, REQUEST_INTERVAL, "pio1"
    )


if __name__ == "__main__":
    try:
        asyncio.run(run_mqtt_client())
    except KeyboardInterrupt:
        print("MQTT client stopped manually")
