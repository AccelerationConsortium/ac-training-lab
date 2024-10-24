import time

from machine import UART, Pin

# Initialize UART interfaces
uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# Data to be sent
# txData = b"RS232 receive test...\r\n"
# print(f"Writing to uart0: {txData}")
# uart0.write(txData)
# time.sleep(0.1)

timeout = 10  # Timeout in seconds
start_time = time.time()

print("Starting UART communication...")

while True:
    current_time = time.time()
    if current_time - start_time > timeout:
        print("Timeout exceeded. Exiting...")
        break

    # Check for data on uart0
    if uart0.any() > 0:
        print("Data available on uart0")
    while uart0.any() > 0:  # Channel 0 is spontaneous and self-collecting
        rxData0 = uart0.read()
        print(f"rxData0: {rxData0}")
        print(rxData0)

    time.sleep(0.1)  # Add a small delay to avoid busy-waiting
