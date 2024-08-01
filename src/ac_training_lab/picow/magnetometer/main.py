import asyncio
import json
import ssl
from collections import deque

import ntptime
from machine import I2C, Pin
from micropython_mlx90393 import mlx90393
from mqtt_as import MQTTClient, config
from my_secrets import HIVEMQ_HOST, HIVEMQ_PASSWORD, HIVEMQ_USERNAME, PASSWORD, SSID
from netman import connectWiFi
from sdl_utils import get_onboard_led, get_unique_id

connectWiFi(SSID, PASSWORD, country="US")

# Initialize onboard LED and sensor
onboard_led = get_onboard_led()
i2c = I2C(0, sda=Pin(4), scl=Pin(5))
mlx = mlx90393.MLX90393(i2c, address=0x18)

# # Generate a unique identifier for the Pico W
# pico_id = get_unique_id(write_to_file=True)

# Buffer for storing sensor data
queue = []
sensor_data_buffer = deque(queue, 100)  # Adjust maxlen as needed

# MQTT Topics
# data_topic = f"magnetometer/picow/{pico_id}/sensor_data"
data_topic = "magnetometer/picow/test-magnetometer/sensor_data"

# To validate certificates, a valid time is required
ntptime.timeout = 30  # type: ignore
ntptime.host = "pool.ntp.org"
ntptime.settime()

print("Obtaining CA Certificate")
# generated via https://colab.research.google.com/github/sparks-baird/self-driving-lab-demo/blob/main/notebooks/7.2.1-hivemq-openssl-certificate.ipynb # noqa: E501
with open("hivemq-com-chain.der", "rb") as f:
    cacert = f.read()
    f.close()

# Local configuration
config.update(
    {
        "ssid": SSID,
        "wifi_pw": PASSWORD,
        "server": HIVEMQ_HOST,
        "user": HIVEMQ_USERNAME,
        "password": HIVEMQ_PASSWORD,
        "ssl": True,
        "ssl_params": {
            "server_side": False,
            "key": None,
            "cert": None,
            "cert_reqs": ssl.CERT_REQUIRED,
            "cadata": cacert,
            "server_hostname": HIVEMQ_HOST,
        },
        "keepalive": 3600,
    }
)


async def sensor_data_acquisition():
    while True:
        magx, magy, magz = mlx.magnetic
        sensor_data_buffer.append((magx, magy, magz))
        await asyncio.sleep(0.1)  # Adjust based on the desired sampling rate


async def publish_sensor_data(client):
    while True:
        if sensor_data_buffer:
            # Create a batch of data points with rate limiting
            data_batch = []
            if sensor_data_buffer:
                magx, magy, magz = sensor_data_buffer.popleft()
                data_batch.append({"X": magx, "Y": magy, "Z": magz})

            # Convert the batch to JSON and publish
            data = json.dumps(data_batch)
            await client.publish(data_topic, data, qos=1)

            # Print the data batch
            print("Published data:", data)

        await asyncio.sleep(1)  # Ensure only one data point is sent per second


async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()


async def main(client):
    await client.connect()
    asyncio.create_task(sensor_data_acquisition())
    asyncio.create_task(publish_sensor_data(client))
    asyncio.create_task(up(client))

    while True:
        await asyncio.sleep(10)
        onboard_led.toggle()


# MQTT client initialization and main loop execution
config["queue_len"] = 1
MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = MQTTClient(config)
del cacert  # to free memory
try:
    asyncio.run(main(client))
finally:
    client.close()
