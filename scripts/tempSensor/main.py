import time
import machine
import scripts.tempSensor.lib.adafruit_bme680 as adafruit_bme680

i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4))  

bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

temperature_offset = -5

while True:
    print("\nTemperature: %0.1f C" % (bme680.temperature + temperature_offset))
    print("Gas: %d ohm" % bme680.gas)
    print("Humidity: %0.1f %%" % bme680.relative_humidity)
    print("Pressure: %0.3f hPa" % bme680.pressure)
    print("Altitude = %0.2f meters" % bme680.altitude)
    time.sleep(1)
