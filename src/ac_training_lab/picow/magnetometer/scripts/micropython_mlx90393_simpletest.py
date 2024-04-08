# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya

import time

from machine import I2C, Pin
from micropython_mlx90393 import mlx90393

onboard_led = Pin("LED", Pin.OUT)

# https://chat.openai.com/share/04540787-58de-424b-b3a4-bf6a70dc1d66
i2c = I2C(0, sda=Pin(4), scl=Pin(5))  # Correct I2C pins for Pico W
mlx = mlx90393.MLX90393(i2c, address=0x18)  # address comes from check_for_i2c.py script

flash_interval = 3  # Flash the LED every 5 seconds
last_flash_time = time.time()

while True:
    magx, magy, magz = mlx.magnetic
    print(f"X: {magx} uT, Y: {magy} uT, Z: {magz} uT")

    current_time = time.time()
    if current_time - last_flash_time >= flash_interval:
        onboard_led.value(1)  # Toggle the LED on
        time.sleep(0.5)  # Keep the LED on for 0.5 seconds
        onboard_led.value(0)  # Toggle the LED off
        last_flash_time = current_time

    time.sleep(0.01)  # Short delay to prevent the loop from running too fast
