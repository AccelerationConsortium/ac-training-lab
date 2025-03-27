import time

import RPi.GPIO as GPIO

# from picamera2 import Picamera2

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)


GPIO.output(12, GPIO.HIGH)
print("lights on")

# picam2 = Picamera2()
# picam2.configure(picam2.create_still_configuration())

# picam2.start()
time.sleep(5)
# picam2.capture_file('/home/ac/documents/light/test.jpg')
# picam2.close()

GPIO.output(12, GPIO.LOW)
print("lights off")
