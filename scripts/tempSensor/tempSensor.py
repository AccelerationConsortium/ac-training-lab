from bme680 import *   
from machine import I2C, Pin  
import time                  

i2c = I2C(0, scl=Pin(5), sda=Pin(4))  

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

