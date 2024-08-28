"""

This script synchronizes time between an orchestrator and several motors using MQTT.
It retrieves the current NTP time from a server, publishes it to a specified MQTT topic,
and receives responses from the motors,
comparing the published and received times to calculate the difference.
The script handles MQTT connections, subscriptions, and message processing,
ensuring secure communication with TLS.
It periodically publishes the current NTP time and stopping after a specified duration.

"""


import os
import json
import threading
from time import time
import asyncio
import numpy as np
import pandas as pd
import ntplib
from queue import Queue, Empty
import paho.mqtt.client as paho
from my_secrets import (
    HIVEMQ_HOST,
    HIVEMQ_PASSWORD,
    HIVEMQ_USERNAME
)


username = HIVEMQ_USERNAME
password = HIVEMQ_PASSWORD
host = HIVEMQ_HOST
published_time = 0
received_time = 0

#Returns the current time of the npt servers
def get_ntp_time(server='time.google.com'):
    try:
        print("Creating NTP client")
        client=ntplib.NTPClient()
        print(f"Requesting time from server: {server}")
        response = client.request(server)
        print("Received response from server")
        ntp_time = round(response.tx_time)
        print(f"NTP time retrieved: {ntp_time}")
        return ntp_time
    except Exception as e:
        print("failed to connect to server")
        return None
    
publish_topic = 'time-sync/orchestrator'
motor1_topic = 'time-sync/motor1'
motor2_topic = 'time-sync/motor2'
subscribe_topics = [motor1_topic, motor2_topic]

def get_client_and_queue(
    subscribe_topic, host, username, password, port=8883, tls=True
):
    '''
    Set up the Client and queue as well as receive messages from the motors
    
    Parameters
    
    ----------
    subscribe_topic : list
        A list of the motor topics that the orchestrator receives messages from
    host: 
        
    host : str
        The hostname or IP address of the MQTT server to connect to.
    username : str
        The username to use for MQTT authentication.
    password : str, optional
        The password to use for MQTT authentication, by default None.
    port : int, optional
        The port number to connect to at the MQTT server, by default 8883.
    tls : bool, optional
        Whether to use TLS for the connection, by default True.

    '''
    client = paho.Client()  # create new instance
    queue = Queue()  # Create queue to store sensor data
    connected_event = threading.Event()  # event to wait for connection

    def on_message(client, userdata, msg):
        global received_time
        print(f"Received message on topic {msg.topic}: {msg.payload}")
        data = json.loads(msg.payload.decode())
        try:
            if "ntp_time" in data:
                received_time = data["ntp_time"]
            elif "received_time" in data:
                print("skip")
            else:
                raise KeyError (f"Neither 'ntp_time' nor 'received_time' found in the message : {data}")
            
        except KeyError as e:
            print(f"Error: {e}")
        queue.put(data)
        print(f"Queue contents after receiving message: {[item for item in queue.queue]}")
        #Finds the difference between the published time and the time recieved to find the difference
        diff = published_time - received_time
        print("PUBLISHED TIME")
        print(published_time)
        print("RECEIVED TIME")
        print(received_time)
        print(diff)

    def on_connect(client, userdata, flags, rc):
        #Subscribes to all topics in the list
        for i in range (len(subscribe_topics)):
            client.subscribe(subscribe_topics[i], qos=1)
        connected_event.set()
    client.on_connect = on_connect
    client.on_message = on_message
    # enable TLS for secure connection
    if tls:
        client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS_CLIENT) 
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883
    client.connect(host, port)
    # wait for connection to be established
    connected_event.wait(timeout=10.0)
    return client, queue

async def publish_ntp_time(client, topic):
    """
    Publish the current NTP time to the specified MQTT topic.

    Parameters
    ----------
    client : paho.Client
        The Paho MQTT client instance.
    topic : str
        The MQTT topic to publish the NTP time to.
    """
    global published_time
    current_time = get_ntp_time()  # Get the current time
    published_time = round(current_time)
    payload = json.dumps({"ntp_time": current_time})
    client.publish(topic, payload, qos=1, retain = False)
    print(f"Published NTP time: {current_time} to topic: {topic}")
async def publish_rec_time(client, topic):
    """
    Publish the NTP time received by the motors to the specified MQTT topic.

    Parameters
    ----------
    client : paho.Client
        The Paho MQTT client instance.
    topic : str
        The MQTT topic to publish the NTP time to.
    """
    global received_time
    payload = json.dumps({"received_time":received_time})
    client.publish(topic, payload, qos=1, retain = False)
async def main():
    client, queue = get_client_and_queue(subscribe_topics,host,username, password)
    client.loop_start()
    print("started")

    start_time = get_ntp_time()
    # must have the while True loop to keep the program running
    while True:
        await asyncio.sleep(5)
        elapsed_time = round(time() - start_time)
        await publish_ntp_time(client,publish_topic)
        await publish_rec_time(client, publish_topic)
        print(f"Elapsed: {elapsed_time}s")
        if elapsed_time >= 600:
            break
    print("stopped")
    client.loop_stop()
    client.disconnect()
if __name__ == "__main__":
    asyncio.run(main())
#need a method to indicate if it is time synced

