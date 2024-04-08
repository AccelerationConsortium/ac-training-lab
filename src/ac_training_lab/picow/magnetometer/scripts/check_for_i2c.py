import machine

# Create I2C object
i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4))

# Print out any addresses found
devices = i2c.scan()

if devices:
    for d in devices:
        print(hex(d))
