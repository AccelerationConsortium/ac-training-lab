import asyncio
import json
import ssl
from collections import OrderedDict

import machine
import ntptime
import utime
from machine import unique_id
from mqtt_as import MQTTClient, config
from my_secrets import HIVEMQ_HOST, HIVEMQ_PASSWORD, HIVEMQ_USERNAME, PASSWORD, SSID
from netman import connectWiFi
from ubinascii import hexlify

# Set timezone offset; adjust as needed for daylight savings time changes
TIMEZONE_OFFSET = -5


def sync_time():
    """Synchronize time with NTP server."""
    try:
        ntptime.timeout = 10  # Shorter timeout for faster response
        ntptime.settime()
        return True
    except Exception as e:
        print(f"NTP sync error: {e}")
        return False


def get_local_time():
    """Get the current time adjusted for timezone."""
    return utime.localtime(utime.time() + TIMEZONE_OFFSET * 3600)


# Connect to Wi-Fi
connectWiFi(SSID, PASSWORD)

# Unique Pico W ID
my_id = hexlify(unique_id()).decode()

# MQTT topic
# Current scale model/pico id = FX-120i/e6613008e3659f2f
mqtt_topic = f"FX-120i/{my_id}"


# Initial NTP sync
if not sync_time():
    print("Initial time sync failed, resetting...")
    machine.reset()

# Obtain CA certificate
try:
    with open("hivemq-com-chain.der", "rb") as f:
        cacert = f.read()
except Exception as e:
    print(f"Certificate read error: {e}")
    machine.reset()

# Local configuration for MQTT
config.update(
    {
        "ssid": SSID,
        "wifi_pw": PASSWORD,
        "server": HIVEMQ_HOST,
        "user": HIVEMQ_USERNAME,
        "password": HIVEMQ_PASSWORD,
        "ssl": True,
        "ssl_params": {
            "cert_reqs": ssl.CERT_REQUIRED,
            "cadata": cacert,
            "server_hostname": HIVEMQ_HOST,
        },
        "keepalive": 60,
        "ping_interval": 5,
    }
)

# Initialize UART for scale data
uart = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5))


async def read_scale_data(client):
    last_publish = utime.time()  # Track the last time data was published
    sync_interval = 3600  # Sync every hour

    while True:
        try:
            # Periodic time sync
            if utime.time() - last_publish >= sync_interval:
                sync_time()

            uart.write(b"Q\r\n")  # Command to read data from the scale
            utime.sleep(0.1)

            if uart.any():  # Check if there is data available from the scale
                scale_data = uart.read().decode("utf-8").strip()
                if scale_data:
                    weight = scale_data.splitlines()[0].strip()
                    # Remove "ST," or "US," prefixes if they exist in the data
                    weight = weight.replace("ST,", "").replace("US,", "").strip()
                else:
                    weight = "0g"

                current = get_local_time()
                current_date = f"{current[0]:04}-{current[1]:02}-{current[2]:02}"
                current_time = f"{current[3]:02}:{current[4]:02}:{current[5]:02}"
                data = OrderedDict(
                    [
                        ("Current Weight", weight),
                        ("Date", current_date),
                        ("Time", current_time),
                    ]
                )

                message = json.dumps(data)
                print(f"Publishing scale data: {message}")
                await client.publish(mqtt_topic, message, qos=1)  # Publish data
                last_publish = utime.time()  # Update the last publish time

            await asyncio.sleep(1)

            # Reset if no successful publish for 5 minutes
            if utime.time() - last_publish > 300:
                print("No successful publish for 5 minutes, resetting...")
                sync_time()
                machine.reset()

        except Exception as e:
            print(f"Error in read_scale_data: {e}")
            await asyncio.sleep(5)


async def messages(client):
    async for topic, msg, retained in client.queue:
        print(f"Received message on topic {topic}: {msg.decode()}")


async def main(client):
    try:
        await client.connect()
        await asyncio.gather(messages(client), read_scale_data(client))
    except Exception as e:
        print(f"Main loop error: {e}")
        machine.reset()


# MQTT configuration
config["queue_len"] = 2
MQTTClient.DEBUG = True
client = MQTTClient(config)

# Start the main loop
asyncio.run(main(client))
