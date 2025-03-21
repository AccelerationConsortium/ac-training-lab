# https://mchrisgm.github.io/bambulabs_api/examples.html

from time import sleep
import bambulabs_api as bl

from my_secrets import IP, SERIAL, ACCESS_CODE

printer = bl.Printer(IP, ACCESS_CODE, SERIAL)

printer.connect()

sleep(2.0)

homing_success = printer.home_printer()

print(f"Homing success: {homing_success}")
