from machine import Pin, I2C, reset
from bme680 import BME680_I2C
from netman import connectWiFi
from umqtt.simple import MQTTClient
import time
import json

# Configuration
SSID = 'Pixel 8'
PASSWORD = '123456789'
MQTT_BROKER = b'b6bdb89571144b3d8e5ca4bbe666ddb5.s1.eu.hivemq.cloud'
MQTT_PORT = 8883
MQTT_TOPIC = b"sensors/bme680/data"
MQTT_USER = b'Luthiraa'
MQTT_PASS = b'theboss1010'

# Initialize I2C and Sensor
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
bme = BME680_I2C(i2c)

def connect_to_wifi():
    """Connects to Wi-Fi, restarts on failure."""
    try:
        status = connectWiFi(SSID, PASSWORD, country='US', retries=5)
        print("Wi-Fi connected! IP:", status[0])
    except Exception as e:
        print(f"Wi-Fi error: {e}")
        time.sleep(5)
        reset()

def connect_to_mqtt():
    """Connects to MQTT broker, restarts on failure."""
    client = MQTTClient(
        client_id=b"pico_w",
        server=MQTT_BROKER,
        port=MQTT_PORT,
        user=MQTT_USER,
        password=MQTT_PASS,
        keepalive=60,
        ssl=True,
        ssl_params={'server_hostname': MQTT_BROKER}
    )
    try:
        client.connect()
        print("Connected to MQTT broker!")
        return client
    except Exception as e:
        print(f"MQTT error: {e}")
        time.sleep(5)
        reset()

def main():
    connect_to_wifi()
    mqtt_client = connect_to_mqtt()

    while True:
        try:
            # Create JSON payload
            payload = json.dumps({
                "temperature": round(bme.temperature, 2),
                "humidity": round(bme.humidity, 2),
                "pressure": round(bme.pressure, 2),
                "gas": round(bme.gas, 2)
            })

            mqtt_client.publish(MQTT_TOPIC, payload)
            print("Published:", payload)
            time.sleep(2)

        except Exception as e:
            print(f"Runtime error: {e}")
            time.sleep(5)
            reset()

if __name__ == "__main__":
    main()

