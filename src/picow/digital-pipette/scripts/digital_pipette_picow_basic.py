import utime
from machine import PWM, Pin

# Setup PWM
pwm = PWM(Pin(0))  # Use the appropriate GPIO pin
pwm.freq(50)  # 50 Hz frequency


def set_position(pulse_ms):
    duty = int((pulse_ms / 20.0) * 65535)
    pwm.duty_u16(duty)


# Example to set the actuator to different positions
set_position(1.1)  # Almost full retraction
utime.sleep(5)
set_position(1.5)  # Halfway
utime.sleep(5)
set_position(1.9)  # Almost full extension
utime.sleep(5)
set_position(1.1)  # Almost full retraction
utime.sleep(5)
set_position(1.5)  # Halfway
utime.sleep(5)

# Add your logic to set it to the desired intermediate positions

pwm.deinit()  # Deinitialize PWM
