import time

from EMC2101 import EMC2101
from machine import I2C, Pin, SoftI2C

# Constants
PIN_I2C0_SDA = Pin(4)
PIN_I2C0_SCL = Pin(5)
I2C0_FREQ = 400000
# I2C0_FREQ = 10000
DESIRED_SPEED = 100  # Set desired fan speed percentage (0 to 100)

# Initialize I2C bus (use SoftI2C, I2C threw EIO error)
i2c = I2C(0, scl=PIN_I2C0_SCL, sda=PIN_I2C0_SDA, freq=I2C0_FREQ)
# i2c = I2C(0, scl=PIN_I2C0_SCL, sda=PIN_I2C0_SDA)
print(f"I2C Bus Initialized! Devices found: {i2c.scan()}")

# Initialize fan controller
fan_controller = EMC2101(i2c)
print("Fan controller object created")

# Set fan speed
fan_controller.set_duty_cycle(DESIRED_SPEED)
actual_speed = fan_controller.get_duty_cycle()

print(f"Speed set to {DESIRED_SPEED}%")
print(f"Actual speed is {actual_speed}%")
print(f"Actual RPM is {fan_controller.get_fan_rpm()} RPM")

# Monitor fan speed
while True:
    time.sleep(5)
    print(f"Monitoring Fan:")
    print(f"  Actual speed is {fan_controller.get_duty_cycle()}%")
    print(f"  Actual RPM   is {fan_controller.get_fan_rpm()} RPM")
