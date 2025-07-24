import time

from pymycobot.mycobot280 import MyCobot280

# Initialize cobot
print("Initializing MyCobot280...")
cobot = MyCobot280("/dev/ttyAMA0", 1000000)
print("Connected!")

# Test sync_send_angles
print("\nTesting sync_send_angles...")
try:
    degrees = [0, 0, 0, 0, 0, 0]
    speed = 50
    timeout = 15

    print(f"Moving to home position: {degrees}")
    start = time.time()
    cobot.sync_send_angles(degrees, speed, timeout)
    end = time.time()
    print(f"✓ Completed in {end-start:.2f} seconds")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test sync_send_coords
print("\nTesting sync_send_coords...")
try:
    coords = [200, 0, 300, 0, 0, 0]
    speed = 50
    mode = 0
    timeout = 15

    print(f"Moving to coordinates: {coords}")
    start = time.time()
    cobot.sync_send_coords(coords, speed, mode, timeout)
    end = time.time()
    print(f"✓ Completed in {end-start:.2f} seconds")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test get_angles
print("\nTesting get_angles...")
try:
    angles = cobot.get_angles()
    print(f"✓ Current angles: {angles}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test get_coords
print("\nTesting get_coords...")
try:
    coords = cobot.get_coords()
    print(f"✓ Current coords: {coords}")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\nDone!")
