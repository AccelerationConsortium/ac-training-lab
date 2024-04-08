# Description

import asyncio
import json
import sys
from time import time

import ussl
from machine import PWM, Pin
from mqtt_as import MQTTClient, config
from my_secrets import HIVEMQ_HOST, HIVEMQ_PASSWORD, HIVEMQ_USERNAME, PASSWORD, SSID
from netman import connectWiFi
from robust_ntptime import set_ntptime
from sdl_utils import get_onboard_led, get_unique_id
from uio import StringIO

onboard_led = get_onboard_led()

connectWiFi(SSID, PASSWORD, country="US")
set_ntptime(host="time.google.com", retry_host="pool.ntp.org")
pico_id = get_unique_id(write_to_file=True)

print("Obtaining CA Certificate from file")
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
            "cert_reqs": ussl.CERT_REQUIRED,
            "cadata": cacert,
            "server_hostname": HIVEMQ_HOST,
        },
        "keepalive": 30,
    }
)

# Setup PWM
pwm = PWM(Pin(0))  # Use the appropriate GPIO pin
pwm.freq(50)  # 50 Hz frequency


def set_position(pulse_ms):
    duty = int((pulse_ms / 20.0) * 65535)
    pwm.duty_u16(duty)


# MQTT Topics
command_topic = f"digital-pipette/picow/{pico_id}/L16-R"  # Prefix for all topics
print(command_topic)


async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        try:
            topic = topic.decode()
            msg = msg.decode()
            retained = str(retained)
            print((topic, msg, retained))

            if topic == command_topic:
                # Parse the incoming message as JSON for actuator control
                incoming_dict = json.loads(msg)
                print(incoming_dict)
                position = incoming_dict["position"]
                print(position)

                # Set the position of the actuator
                set_position(position)

                # There's no feedback from the actuator, so better to just use a QoS on the orchestrator side
                # In the future, this could be a visual, audio, vibrational, or other kind of check

        except Exception as e:
            with StringIO() as f:
                sys.print_exception(e, f)
                print(f.getvalue())


async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe(command_topic, 1)  # renew subscriptions


async def main(client):
    await client.connect()
    for coroutine in (up, messages):
        asyncio.create_task(coroutine(client))

    start_time = time()
    # must have the while True loop to keep the program running
    while True:
        await asyncio.sleep(5)
        onboard_led.value(1)  # Turn the LED on
        await asyncio.sleep(0.5)  # Keep the LED on for 0.5 seconds
        onboard_led.value(0)  # Turn the LED off
        elapsed_time = round(time() - start_time)
        print(f"Elapsed: {elapsed_time}s")


config["queue_len"] = 1  # Use event interface with specified queue length
MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = MQTTClient(config)
try:
    asyncio.run(main(client))

# At the end of the main function, before closing the client
finally:
    pwm.deinit()  # Deinitialize PWM
    client.close()  # Prevent LmacRxBlk:1 errors
