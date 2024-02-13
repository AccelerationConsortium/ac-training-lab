from machine import Pin, unique_id
from ubinascii import hexlify


def get_unique_id(write_to_file=True):
    my_id = hexlify(unique_id()).decode()
    print(f"\nPICO_ID: {my_id}\n")

    if write_to_file:
        with open("pico_id.txt", "w") as f:
            f.write(my_id)

    return my_id


def get_onboard_led():
    try:
        onboard_led = Pin("LED", Pin.OUT)  # only works for Pico W
    except Exception as e:
        print(e)
        onboard_led = Pin(25, Pin.OUT)
    return onboard_led
