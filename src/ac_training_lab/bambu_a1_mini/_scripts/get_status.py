# https://mchrisgm.github.io/bambulabs_api/examples.html

from time import sleep

import bambulabs_api as bl
from my_secrets import ACCESS_CODE, IP, SERIAL

printer = bl.Printer(IP, ACCESS_CODE, SERIAL)

printer.connect()

sleep(2.0)

status = printer.get_state()
print(f"Printer status: {status}")

bed_temperature = printer.get_bed_temperature()
nozzle_temperature = printer.get_nozzle_temperature()
speed = printer.get_print_speed()
print(
    f"Printer status: {status}, Bed temp: {bed_temperature}, "
    f"Nozzle temp: {nozzle_temperature},"
    f"Print speed: {speed}"
)
