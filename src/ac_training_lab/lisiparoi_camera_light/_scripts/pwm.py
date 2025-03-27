import time

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

pwm = GPIO.PWM(12, 1000)
pwm.start(0)

for duty in range(0, 101, 5):
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)

for duty in range(100, -1, -5):
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)

pwm.stop()
del pwm
GPIO.cleanup()
