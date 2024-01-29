from time import sleep

from machine import PWM, Pin

sg90 = PWM(Pin(0, mode=Pin.OUT))
sg90.freq(50)

# For a 2 ms pulse
duty_for_2ms = int(0.1 * 65535)  # Approximately 6553 for 10% duty cycle

while True:
    sg90.duty_u16(duty_for_2ms)
    sleep(1)
    # Adjust the duty cycle to the other position if needed
    # sg90.duty_u16(<other_duty_value>)
    # sleep(1)
