from time import sleep

from lib.EMC2101 import EMC2101
from machine import Pin, SoftI2C, Timer

timer = Timer()

led = Pin("LED", Pin.OUT)


def blink(timer):
    led.toggle()


timer.init(freq=3, mode=Timer.PERIODIC, callback=blink)
sleep(5)

i2c = SoftI2C(scl=Pin((0)), sda=Pin(1))
controller = EMC2101(i2c)

controller.set_duty_cycle(int(percent[i]))


def set_stirring_percent(devices, percent):
    try:
        for i, dev in enumerate(devices):
            dev.set_duty_cycle(int(percent[i]))
    except IndexError:
        print("An incorrect number of stirring place speeds were specified")
        return

    return print(f"stirring speeds set to {percent}")


def set_stirring_rpm(rpm):
    controller.set_duty_cycle(30)
    sleep(5)
    a = controller.get_fan_rpm()
    b = controller.get_duty_cycle()

    duty_estimator = (b / a) * rpm

    if duty_estimator > 100:
        controller.set_duty_cycle(95)
        sleep(2)
        a = controller.get_fan_rpm()
        b = controller.get_duty_cycle()
    else:
        controller.set_duty_cycle(int(duty_estimator))
        sleep(2)
        a = controller.get_fan_rpm()
        b = controller.get_duty_cycle()

    while True:
        if a < rpm * 0.95:
            b += 2
            controller.set_duty_cycle(b)
            sleep(2)
            a = controller.get_fan_rpm()
            b = controller.get_duty_cycle()
        elif a > rpm * 1.05:
            b -= 2
            controller.set_duty_cycle(b)
            sleep(2)
            a = controller.get_fan_rpm()
            b = controller.get_duty_cycle()
        else:
            break

    return print(f"stirring speeds set to {rpm}")
