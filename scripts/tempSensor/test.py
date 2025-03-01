from bme680 import BME680_I2C  
from machine import I2C, Pin
from netman import connectWiFi
from umqtt.simple import MQTTClient
import json  
import time
from constants import WIFI_SSID, WIFI_PASSWORD, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, MQTT_USER, MQTT_PASSWORD


def connect_to_internet():
    try:
        status = connectWiFi(WIFI_SSID, WIFI_PASSWORD, country='US', retries=3)
        print("Connected to Wi-Fi successfully!")
        print("IP Address:", status[0])
    except RuntimeError as e:
        print(f"Failed to connect to Wi-Fi: {e}")
        raise

i2c = I2C(1, scl=Pin(27), sda=Pin(26))
bme = BME680_I2C(i2c)

client = MQTTClient(
    client_id=b"kudzai_raspberrypi_picow",
    server=MQTT_BROKER,
    port=MQTT_PORT,
    user=MQTT_USER,
    password=MQTT_PASSWORD,
    keepalive=60,  # Set to a shorter interval
    ssl=True,
    ssl_params={'server_hostname': MQTT_BROKER}
)

def connect_to_mqtt():
    try:
        client.connect()
        print("Connected to MQTT broker")
        print("Client ID:", client.client_id)  
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        raise

connect_to_internet()
connect_to_mqtt()

while True:
    temperature = bme.temperature
    humidity = bme.humidity
    pressure = bme.pressure
    gas = bme.gas
    payload = json.dumps({
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "gas": gas
    })
    print("oayload:", payload)
    
    try:
        client.publish(MQTT_TOPIC, payload)
        print("Data published to MQTT topic:", MQTT_TOPIC)
    except Exception as e:
        print(f"Failed to publish data: {e}")
        client.connect()
    
    time.sleep(2)
