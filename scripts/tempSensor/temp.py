from bme680 import *  # Ensure you have the right import for the BME680 class
from machine import I2C, Pin  
import time                  

# Initialize I2C on GPIO pins 27 (SCL) and 26 (SDA) for the Raspberry Pi Pico W
i2c = I2C(1, scl=Pin(27), sda=Pin(26))  

# Initialize the BME680 sensor over I2C
bme = BME680_I2C(i2c)

while True:
    print("--------------------------------------------------")
    print()
    print("Temperature: {:.2f} °C".format(bme.temperature))
    print("Humidity: {:.2f} %".format(bme.humidity))
    print("Pressure: {:.2f} hPa".format(bme.pressure))
    print("Gas: {:.2f} ohms".format(bme.gas))
    print()
    time.sleep(3)
