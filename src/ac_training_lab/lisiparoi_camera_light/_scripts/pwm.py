import time

import RPi.GPIO as GPIO

print("Initializing PWM control...")
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(12, GPIO.OUT)

pwm = GPIO.PWM(12, 1000)  # Frequency of 1000 Hz
pwm.start(0)

print("Increasing brightness...")
# Gradually increase the brightness
for duty in range(0, 101, 5):
    pwm.ChangeDutyCycle(duty)
    if duty % 25 == 0:  # Print at milestone percentages
        print(f"Brightness: {duty}%")
    time.sleep(0.05)  # Shorter sleep time for smoother transitions

print("Decreasing brightness...")
# Gradually decrease the brightness
for duty in range(100, -1, -5):
    pwm.ChangeDutyCycle(duty)
    if duty % 25 == 0:  # Print at milestone percentages
        print(f"Brightness: {duty}%")
    time.sleep(0.05)  # Shorter sleep time for smoother transitions

print("Cleaning up...")
pwm.stop()
GPIO.cleanup()
print("PWM demonstration complete.")
