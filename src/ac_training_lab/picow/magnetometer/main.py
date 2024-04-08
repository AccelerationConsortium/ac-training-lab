import asyncio
import json
from collections import deque

from machine import I2C, Pin
from micropython_mlx90393 import mlx90393
from mqtt_as import MQTTClient, config
from sdl_utils import get_onboard_led, get_unique_id

# Initialize onboard LED and sensor
onboard_led = get_onboard_led()
i2c = I2C(0, sda=Pin(4), scl=Pin(5))
mlx = mlx90393.MLX90393(i2c, address=0x18)

# Generate a unique identifier for the Pico W
pico_id = get_unique_id(write_to_file=True)

# Buffer for storing sensor data
sensor_data_buffer = deque(
    maxlen=100
)  # Adjust maxlen as needed based on expected data rate and network delay

# MQTT Topics
data_topic = f"magnetometer/picow/{pico_id}/sensor_data"


async def sensor_data_acquisition():
    while True:
        magx, magy, magz = mlx.magnetic
        sensor_data_buffer.append((magx, magy, magz))
        await asyncio.sleep(0.1)  # Adjust based on the desired sampling rate


async def publish_sensor_data(client):
    while True:
        if sensor_data_buffer:
            # Create a batch of data points
            data_batch = []
            while sensor_data_buffer:
                magx, magy, magz = sensor_data_buffer.popleft()
                data_batch.append({"X": magx, "Y": magy, "Z": magz})

            # Convert the batch to JSON and publish
            data = json.dumps(data_batch)
            await client.publish(data_topic, data, qos=1)

        await asyncio.sleep(0.5)  # Adjust based on desired publishing frequency


async def main(client):
    await client.connect()
    asyncio.create_task(sensor_data_acquisition())
    asyncio.create_task(publish_sensor_data(client))

    while True:
        await asyncio.sleep(10)
        onboard_led.toggle()


# MQTT client initialization and main loop execution
config["queue_len"] = 1
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    client.close()
