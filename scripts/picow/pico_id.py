from machine import unique_id
from ubinascii import hexlify

my_id = hexlify(unique_id()).decode()
print(f"\nPICO_ID: {my_id}\n")
