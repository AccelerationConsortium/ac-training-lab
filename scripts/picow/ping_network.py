import time

import network
import urequests
from my_secrets import PASSWORD, SSID


# Function to connect to Wi-Fi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for connection
    max_attempts = 15
    attempt = 0
    while not wlan.isconnected() and attempt < max_attempts:
        print("Connecting to Wi-Fi...")
        time.sleep(1)
        attempt += 1

    if wlan.isconnected():
        print("Connected to Wi-Fi")
        print("Network config:", wlan.ifconfig())
    else:
        print("Failed to connect to Wi-Fi")

    return wlan.isconnected()


# Function to check internet access
def check_internet_access():
    try:
        response = urequests.get("http://www.google.com", timeout=15)
        if response.status_code == 200:
            print("Internet access is available")
            return True
        else:
            print("Failed to access the internet")
            return False
    except Exception as e:
        print("Error:", e)
        return False


# Connect to Wi-Fi
if connect_to_wifi(SSID, PASSWORD):
    # Check internet access
    check_internet_access()
else:
    print("Cannot check internet access without Wi-Fi connection")
