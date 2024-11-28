from bme680 import BME680_I2C  # Ensure you have the right import for the BME680 class
from machine import I2C, Pin  
from netman import connectWiFi
from umqtt.simple import MQTTClient
import time

# Wi-Fi and MQTT configuration
SSID = 'Pixel 8'  # Replace with your Wi-Fi SSID
PASSWORD = '123456789'  # Replace with your Wi-Fi password
MQTT_BROKER = 'b6bdb89571144b3d8e5ca4bbe666ddb5.s1.eu.hivemq.cloud'  # HiveMQ Cloud broker URL
MQTT_PORT = 8883  # Port for TLS
MQTT_TOPIC = "sensors/bme680/data"  # Replace with your desired MQTT topic

MQTT_USER = 'Luthiraa'  
MQTT_PASS = 'theboss1010'  

def connect_to_internet():
    try:
        status = connectWiFi(SSID, PASSWORD, country='US', retries=3)
        print("Connected to Wi-Fi successfully!")
        print("IP Address:", status[0])
    except RuntimeError as e:
        print(f"Failed to connect to Wi-Fi: {e}")
        raise

# Initialize I2C and BME680
i2c = I2C(1, scl=Pin(27), sda=Pin(26))
bme = BME680_I2C(i2c)

# MQTT setup with authentication and TLS
client = MQTTClient(
    client_id=b"kudzai_raspberrypi_picow",
    server=MQTT_BROKER,
    port=MQTT_PORT,
    user=MQTT_USER,
    password=MQTT_PASS,
    keepalive=60,  # Set to a shorter interval
    ssl=True,
    ssl_params={'server_hostname': MQTT_BROKER}
)
# Connect to MQTT broker
def connect_to_mqtt():
    try:
        client.connect()
        print("Connected to MQTT broker")
        print("Client ID:", client.client_id)  # Print client ID
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        raise

# Connect to Wi-Fi and MQTT
connect_to_internet()
connect_to_mqtt()

while True:
    # Read sensor data
    temperature = bme.temperature
    humidity = bme.humidity
    pressure = bme.pressure
    gas = bme.gas
    
    # Prepare data payload
    payload = (
        f"Temperature: {temperature:.2f} °C, "
        f"Humidity: {humidity:.2f} %, "
        f"Pressure: {pressure:.2f} hPa, "
        f"Gas: {gas:.2f} ohms"
    )
    
    # Print data to console
    print("--------------------------------------------------")
    print(payload)
    print("--------------------------------------------------")
    
    # Publish data to MQTT broker
    try:
        client.publish(MQTT_TOPIC, payload)
        print("Data published to MQTT topic:", MQTT_TOPIC)
    except Exception as e:
        print(f"Failed to publish data: {e}")
        client.connect()
    
    time.sleep(2)
