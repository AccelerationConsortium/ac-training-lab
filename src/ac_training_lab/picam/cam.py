import socket
import sys
import os
import subprocess

SCRIPT_URL="https://raw.githubusercontent.com/AccelerationConsortium/ac-training-lab/refs/heads/jwoo-camera/src/ac_training_lab/picam/cam.py"

def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False

def update_script():
    print("Updating script")
    os.remove(sys.argv[0])
    wget.download(SCRIPT_URL, out=sys.argv[0])
    print("Script updated successfully.")
    os.environ["SCRIPT_UPDATED"] = "1"
    os.execv(sys.executable, ['python3'] + sys.argv)

if __name__ == '__main__':
    # Wait until internet is connected
    print("Checking for internet")
    while not internet():    
        internet()
    print("Internet connected")

    # Update this script
    if os.getenv("SCRIPT_UPDATED") != "1":
        update_script()

    # Either use the previous stream key or input a new one
    # Check if a previous stream key exists
    try:
        with open(os.path.join(os.path.dirname(__file__), ".saved_key") "r") as f:
            previous_key = f.read()

    print("Previous stream key:", previous_key)
    print("Update? [y/n] (auto advancing in 5s)")


