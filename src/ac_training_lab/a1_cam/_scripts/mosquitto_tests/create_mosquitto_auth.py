#!/usr/bin/env python3
"""
Create mosquitto authentication files for testing.
Generates password and ACL files with proper format.
"""
import base64
import hashlib
import os


def generate_password_hash(password):
    """Generate mosquitto-compatible password hash (SHA512-PBKDF2)"""
    # For simplicity, we'll use basic SHA512 hash
    # Mosquitto also supports plaintext with $6$ prefix for SHA512
    salt = os.urandom(12)
    password_hash = hashlib.pbkdf2_hmac("sha512", password.encode(), salt, 101)

    # Mosquitto format: $6$salt$hash (base64 encoded)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(password_hash).decode("ascii")

    return f"$6${salt_b64}${hash_b64}"


# Create password file
print("Creating /tmp/mosquitto_passwd...")
with open("/tmp/mosquitto_passwd", "w") as f:
    f.write(f"device_user:{generate_password_hash('device_password')}\n")
    f.write(f"client_user:{generate_password_hash('client_password')}\n")
print("✓ Password file created")

# Create ACL file
print("\nCreating /tmp/mosquitto_acl...")
acl_content = """# ACL (Access Control List) for mosquitto broker
# Format: user <username>
#         topic [read|write|readwrite] <topic>

# Device user can read requests and write responses
user device_user
topic read rpi-zero2w/still-camera/+/request
topic write rpi-zero2w/still-camera/+/response

# Client user can write requests and read responses
user client_user
topic write rpi-zero2w/still-camera/+/request
topic read rpi-zero2w/still-camera/+/response

# Admin user has full access (for debugging)
user admin
topic readwrite #
"""

with open("/tmp/mosquitto_acl", "w") as f:
    f.write(acl_content)
print("✓ ACL file created")

print("\n" + "=" * 60)
print("Authentication Configuration Created")
print("=" * 60)
print("\nUsers:")
print("  device_user / device_password - Device credentials")
print("  client_user / client_password - Client credentials")
print("\nTopic Filters:")
print("  device_user: read requests, write responses")
print("  client_user: write requests, read responses")
