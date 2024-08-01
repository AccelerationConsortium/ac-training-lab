import network

# Initialize the WLAN interface
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Get the MAC address
mac_address = wlan.config("mac")

# Convert the MAC address to a readable format
mac_address_str = ":".join(["{:02x}".format(b) for b in mac_address])

print("MAC Address:", mac_address_str)
