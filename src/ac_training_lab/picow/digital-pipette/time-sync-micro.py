"""
This script controls a servo motor and manages time synchronization
between a microcontroller and an orchestrator using MQTT.
It connects to Wi-Fi, obtains the current time using NTP,
and configures secure MQTT communication with HiveMQ using SSL certificates.
The script subscribes to a command topic to receive time synchronization commands,
adjusts the servo motor's angle based on the received time,
and checks for clock drift, making adjustments if necessary.
It periodically publishes the adjusted time back to the orchestrator
and attempts to resynchronize the system's clock every five minutes,
ensuring consistent time synchronization.
"""

import asyncio
import json
import ssl
import sys
from time import sleep, time

import ntptime
import urequests_2 as urequests

# Hardware
from machine import PWM, Pin

# MQTT
from mqtt_as import MQTTClient, config
from my_secrets import (
    CLUSTER_NAME,
    COLLECTION_NAME,
    COURSE_ID,
    DATA_API_KEY,
    DATABASE_NAME,
    ENDPOINT_BASE_URL,
    HIVEMQ_HOST,
    HIVEMQ_PASSWORD,
    HIVEMQ_USERNAME,
    PASSWORD,
    SSID,
)

# WiFi
from netman import connectWiFi
from uio import StringIO

# import csv# for MongoDB Data API


# Description: Receive commands from HiveMQ and send sensor data to HiveMQ

connectWiFi(SSID, PASSWORD, country="CA")

# To validate certificates, a valid time is required
ntptime.timeout = 5  # type: ignore
ntptime.host = "time.google.com"
received_time = "False"
sg90 = PWM(Pin(0, mode=Pin.OUT))
sg90.freq(50)
duty_for_2ms = int(0.08 * 65535)
try:
    ntptime.settime()
except Exception as e:
    print(f"{e} with {ntptime.host}. Trying again after 5 seconds")
    sleep(5)
    try:
        ntptime.settime()
    except Exception as e:
        print(f"{e} with {ntptime.host}. Trying again with pool.ntp.org")
        sleep(5)
        ntptime.host = "pool.ntp.org"
        ntptime.settime()

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
            "cert_reqs": ssl.CERT_REQUIRED,
            "cadata": cacert,
            "server_hostname": HIVEMQ_HOST,
        },
        "keepalive": 30,
    }
)


# MQTT Topics
command_topic = "time-sync/orchestrator"
micro_topic = "time-sync/motor1"
stored_data = []

print(f"Command topic: {command_topic}")
print(f"Sensor data topic: {micro_topic}")


def set_servo_angle(angle):
    # Convert the angle to duty cycle
    min_duty = 1638  # Corresponds to 0 degrees (1 ms pulse width)
    max_duty = 8192  # Corresponds to 180 degrees (2 ms pulse width)

    # Calculate the duty cycle for the given angle
    duty = int(min_duty + (max_duty - min_duty) * (angle / 180))
    servo.duty_u16(duty)


async def messages(client):
    global received_time  # Respond to incoming messages
    global duty_for_2ms
    async for topic, msg, retained in client.queue:
        try:
            topic = topic.decode()
            msg = msg.decode()
            retained = str(retained)
            print((topic, msg, retained))

            if topic == command_topic:
                data = json.loads(msg)
                time = data["ntp_time"]
                received_time = "True"
                sg90.duty_u16(duty_for_2ms)
                rtt = ntptime.time() - time
                adjusted_time = (
                    time + rtt
                )  # The orchestrators time once the message is received
                print(time)
                current_time = ntptime.time()
                drift = adjusted_time - current_time  # finding the clock drift (if any)
                print(current_time)
                if (
                    abs(drift) >= 1
                ):  # If the clock drift is significant(greater than 1 second)
                    ntptime.time(
                        time() + drift
                    )  # adjusts the internal clock to account for a drift
                stored_data.append(time)
                payload_json = json.dumps(
                    {"ntp_time": current_time}
                )  # convert current_time to a json string
                try:
                    await client.publish(
                        micro_topic, payload_json, qos=1, retain=False
                    )  # publishes ntp time for the orchestrator to read
                    print(
                        f"Message published to topic {sensor_data_topic}: {payload_json}"
                    )
                except Exception as e:
                    print(
                        f"Failed to publish message to topic {sensor_data_topic}: {e}"
                    )

        except Exception as e:
            with StringIO() as f:  # type: ignore
                sys.print_exception(e, f)  # type: ignore
                print(f.getvalue())  # type: ignore


async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe(command_topic, 1)  # renew subscriptions


async def main(client):
    global received_time
    global duty_for_2ms
    await client.connect()
    for coroutine in (up, messages):
        asyncio.create_task(coroutine(client))

    y = duty_for_2ms
    sync_interval = 300  # sync every 5 minutes
    start_time = 0
    sg90.duty_u16(duty_for_2ms)
    asyncio.sleep(1)
    y = y - 200
    sg90.duty_u16(y)
    # must have the while True loop to keep the program running
    while True:
        if received_time == "True":
            if start_time == 0:
                start_time = time()

            await asyncio.sleep(5)

            duty_for_2ms = duty_for_2ms - 100
            if duty_for_2ms == 0.075 * 65535:
                duty_for_2ms = 0.08 * 65535
            elapsed_time = round(time() - start_time)
            print(f"Elapsed: {elapsed_time}s")
            if elapsed_time > sync_interval:
                try:
                    ntptime.settime()
                    start_time = time()  # Reset start time after sync
                except Exception as e:
                    print(f"Failed to resyncrhonize time : {e}")
        else:
            x = 0
            await asyncio.sleep(5)
            elapsed_time = x + 5
            print(f"Elapsed before start: {elapsed_time}s")


config["queue_len"] = 20  # Specified queue length
MQTTClient.DEBUG = True  # Used to print diagnostic messages
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    client.close()
