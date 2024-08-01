import ssl
import time

import ntptime
import uasyncio as asyncio
from EMC2101 import EMC2101
from machine import I2C, Pin, unique_id
from mqtt_as import MQTTClient, config
from my_secrets import HIVEMQ_HOST, HIVEMQ_PASSWORD, HIVEMQ_USERNAME, PASSWORD, SSID
from netman import connectWiFi
from ubinascii import hexlify

my_id = hexlify(unique_id()).decode()
print(f"\nPICO_ID: {my_id}\n")

PICO_ID = "test-fan"  # UPDATE THIS TO YOUR ID
print(f"Overriding PICO_ID to: {PICO_ID}")


# Constants
PIN_I2C0_SDA = Pin(4)
PIN_I2C0_SCL = Pin(5)
I2C0_FREQ = 400000

# Initialize I2C bus
i2c = I2C(0, scl=PIN_I2C0_SCL, sda=PIN_I2C0_SDA, freq=I2C0_FREQ)
print(f"I2C Bus Initialized! Devices found: {i2c.scan()}")

# Initialize fan controller
fan_controller = EMC2101(i2c)
print("Fan controller object created")

# WiFi and MQTT configuration
connectWiFi(SSID, PASSWORD, country="US")

# To validate certificates, a valid time is required
ntptime.timeout = 30  # type: ignore
ntptime.host = "pool.ntp.org"
ntptime.settime()

print("Obtaining CA Certificate")
with open("hivemq-com-chain.der", "rb") as f:
    cacert = f.read()
    f.close()

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

command_topic = f"fan-control/picow/{PICO_ID}/speed"
sensor_data_topic = f"fan-control/picow/{PICO_ID}/rpm"


async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        try:
            topic = topic.decode()
            msg = msg.decode()
            retained = str(retained)
            print((topic, msg, retained))

            if topic == command_topic:
                try:
                    speed = int(msg)
                    if 0 <= speed <= 100:
                        fan_controller.set_duty_cycle(speed)
                        print(f"Fan speed set to {speed}%")
                    else:
                        print("Speed out of range")
                except ValueError:
                    print("Invalid speed value")

                rpm = fan_controller.get_fan_rpm()
                print(f"Publish {rpm} RPM to {sensor_data_topic}")
                await client.publish(sensor_data_topic, f"{rpm}", qos=1)
        except Exception as e:
            print(e)


async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe(command_topic, 1)  # renew subscriptions


async def main(client):
    await client.connect()
    for coroutine in (up, messages):
        asyncio.create_task(coroutine(client))

    start_time = time.time()
    # must have the while True loop to keep the program running
    while True:
        await asyncio.sleep(5)
        rpm = fan_controller.get_fan_rpm()
        elapsed_time = round(time.time() - start_time)
        print(f"Elapsed: {elapsed_time}s, RPM: {rpm}")
        await client.publish(sensor_data_topic, f"{rpm}", qos=1)


config["queue_len"] = 2  # Use event interface with specified queue length
MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = MQTTClient(config)
del cacert  # to free memory
try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
