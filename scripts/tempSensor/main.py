import time
import machine
import scripts.tempSensor.lib.adafruit_bme680 as adafruit_bme680

# Initialize I2C (using GPIO pins directly)
i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4))  # Use I2C0 on GPIO4 (SDA) and GPIO5 (SCL)

# Initialize BME680 sensor
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

# Adjust for temperature offset
temperature_offset = -5

while True:
    print("\nTemperature: %0.1f C" % (bme680.temperature + temperature_offset))
    print("Gas: %d ohm" % bme680.gas)
    print("Humidity: %0.1f %%" % bme680.relative_humidity)
    print("Pressure: %0.3f hPa" % bme680.pressure)
    print("Altitude = %0.2f meters" % bme680.altitude)
    time.sleep(1)
