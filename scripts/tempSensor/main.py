import json
import time

import mqtt_as
import uasyncio as asyncio
from bme680 import BME680_I2C
from machine import I2C, Pin, reset
from my_secrets import (
    MQTT_BROKER,
    MQTT_PASS,
    MQTT_PORT,
    MQTT_TOPIC,
    MQTT_USER,
    PASSWORD,
    SSID,
)

# configure mqtt_as settings
mqtt_as.config["ssid"] = SSID
mqtt_as.config["wifi_pw"] = PASSWORD
mqtt_as.config["server"] = MQTT_BROKER
mqtt_as.config["port"] = MQTT_PORT
mqtt_as.config["user"] = MQTT_USER
mqtt_as.config["password"] = MQTT_PASS
mqtt_as.config["client_id"] = "pico_w"
mqtt_as.config["ssl"] = True
mqtt_as.config["ssl_params"] = {"server_hostname": MQTT_BROKER}
mqtt_as.config["keepalive"] = 60
mqtt_as.config["clean"] = True

# init I2C and the BME680 sensor
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
bme = BME680_I2C(i2c)


async def pub_sensor_data(client):
    """Periodically publishes sensor data as a JSON payload."""
    while True:
        try:
            payload = json.dumps(
                {
                    "temperature": round(bme.temperature, 2),
                    "humidity": round(bme.humidity, 2),
                    "pressure": round(bme.pressure, 2),
                    "gas": round(bme.gas, 2),
                }
            )
            await client.publish(MQTT_TOPIC, payload)
            print("Published:", payload)
        except Exception as e:
            print("Runtime error:", e)
            time.sleep(5)
            reset()
        await asyncio.sleep(2)


async def main():
    client = mqtt_as.MQTTClient()
    await client.connect()
    print("Connected to MQTT broker!")

    # Start the sensor data publishing task
    asyncio.create_task(pub_sensor_data(client))

    # Keep the main loop running
    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
