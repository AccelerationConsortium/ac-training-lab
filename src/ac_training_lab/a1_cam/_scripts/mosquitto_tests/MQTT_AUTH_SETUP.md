# MQTT Authentication and ACL Setup Guide

## Overview

This guide documents how to configure MQTT broker authentication (username/password) and Access Control Lists (ACLs) for topic-level authorization. This setup is critical for securing multi-lab deployments where different users need restricted access to specific device topics.

## Configuration Files

### 1. Mosquitto Configuration (`mosquitto.conf`)

```conf
# Disable anonymous access
allow_anonymous false

# Password file for authentication
password_file /path/to/mosquitto_passwd

# ACL file for topic authorization
acl_file /path/to/mosquitto_acl

# Listener
listener 8883
certfile /path/to/cert.pem
keyfile /path/to/key.pem
cafile /path/to/ca.pem
```

### 2. Password File (`mosquitto_passwd`)

Create users with the `mosquitto_passwd` utility:

```bash
# Create password file with first user
mosquitto_passwd -c mosquitto_passwd device_user

# Add additional users (without -c flag)
mosquitto_passwd mosquitto_passwd client_user
mosquitto_passwd mosquitto_passwd admin_user
```

**Recommended Users:**
- **device_user**: For Raspberry Pi devices (read requests, write responses)
- **client_user**: For notebooks/orchestrators (write requests, read responses)
- **admin_user**: For debugging (full access)

### 3. ACL File (`mosquitto_acl`)

Define topic-level permissions:

```acl
# Device credentials - can read requests and write responses
user device_user
topic read rpi-zero2w/still-camera/+/request
topic write rpi-zero2w/still-camera/+/response

# Client credentials - can write requests and read responses
user client_user
topic write rpi-zero2w/still-camera/+/request
topic read rpi-zero2w/still-camera/+/response

# Admin user - full access for debugging
user admin
topic readwrite #
```

## Multi-Lab Deployment

For organizations with multiple labs (SDL0, SDL1, SDL2, etc.), you can:

### Option 1: Shared Credentials with Lab-Prefixed Device IDs

All labs use the same `device_user` and `client_user` credentials, but devices have lab-specific serials:

```
# Device serials
sdl0-cam-01  # SDL0 lab
sdl1-cam-01  # SDL1 lab
sdl2-cam-01  # SDL2 lab
```

ACL remains the same (uses wildcard `+`).

### Option 2: Lab-Specific Credentials

Create separate users per lab:

```acl
# SDL0 device
user sdl0_device
topic read rpi-zero2w/still-camera/sdl0-+/request
topic write rpi-zero2w/still-camera/sdl0-+/response

# SDL0 client
user sdl0_client
topic write rpi-zero2w/still-camera/sdl0-+/request
topic read rpi-zero2w/still-camera/sdl0-+/response

# SDL1 device
user sdl1_device
topic read rpi-zero2w/still-camera/sdl1-+/request
topic write rpi-zero2w/still-camera/sdl1-+/response

# SDL1 client
user sdl1_client
topic write rpi-zero2w/still-camera/sdl1-+/request
topic read rpi-zero2w/still-camera/sdl1-+/response
```

## Testing Authentication

### Test Scripts with Authentication

Updated test scripts are provided in `_scripts/`:

- `test_mqtt_device_auth.py` - Mock device with authentication
- `test_mqtt_client_auth.py` - Mock client with authentication
- `create_mosquitto_auth.py` - Generate password and ACL files

### Running Tests

1. **Generate auth files:**
   ```bash
   python3 _scripts/create_mosquitto_auth.py
   ```

2. **Start mosquitto with auth:**
   ```bash
   mosquitto -c mosquitto_auth.conf
   ```

3. **Start device (Terminal 1):**
   ```bash
   python3 _scripts/test_mqtt_device_auth.py
   ```

4. **Run client test (Terminal 2):**
   ```bash
   python3 _scripts/test_mqtt_client_auth.py
   ```

### Expected Output

**Device:**
```
✓ Device authenticated and connected
  Username: device_user
  Subscribing to: rpi-zero2w/still-camera/test-cam-01/request
✓ Subscription confirmed
```

**Client:**
```
✓ Client authenticated and connected
  Username: client_user
✓ Publish successful
✓ SUCCESS! Received response:
  Image URI: https://test-bucket.s3...
```

## Common Authentication Issues

### Issue: "Connection refused - bad username or password"

**Causes:**
- Incorrect username/password
- Password file not found
- Password file permissions incorrect

**Solution:**
```bash
# Verify password file exists
ls -la mosquitto_passwd

# Ensure mosquitto can read it
chmod 644 mosquitto_passwd

# Test credentials manually
mosquitto_sub -h localhost -p 1883 -u device_user -P device_password -t test/#
```

### Issue: "Not authorized to publish/subscribe"

**Causes:**
- ACL denies access to topic
- Topic pattern doesn't match ACL rule
- User not defined in ACL file

**Solution:**
```bash
# Check ACL file syntax
cat mosquitto_acl

# Verify topic matches pattern
# Topic: rpi-zero2w/still-camera/test-cam-01/request
# Pattern: rpi-zero2w/still-camera/+/request
# Match: ✓

# Test with wildcard subscription (if allowed)
mosquitto_sub -h localhost -p 1883 -u admin -P admin_password -t '#' -v
```

### Issue: Client ID conflicts

**Causes:**
- Two connections with same client_id
- Previous session not cleanly disconnected

**Solution:**
```python
# Use unique client IDs
client = mqtt.Client(client_id=f"device-{DEVICE_SERIAL}-{timestamp}")

# Or let broker generate
client = mqtt.Client(client_id="")
```

## Security Best Practices

1. **Use TLS encryption** for production (port 8883 with certificates)
2. **Rotate passwords** periodically (every 90 days)
3. **Minimum permissions**: Grant only necessary topic access
4. **Audit logs**: Monitor connection attempts and publish/subscribe patterns
5. **Separate credentials**: Different users for devices vs clients vs admins
6. **File permissions**:
   ```bash
   chmod 600 mosquitto_passwd  # Only mosquitto user can read
   chmod 644 mosquitto_acl     # World-readable is OK (no secrets)
   ```

## HiveMQ Cloud Configuration

If using HiveMQ Cloud instead of self-hosted mosquitto:

1. Create users in HiveMQ console
2. Configure ACL rules in "Access Management"
3. Topic patterns remain the same
4. Use TLS (port 8883) - required by HiveMQ Cloud
5. Enable client certificate auth for additional security (optional)

Example HiveMQ ACL:
```
User: device_user
Publish: rpi-zero2w/still-camera/${clientid}/response
Subscribe: rpi-zero2w/still-camera/${clientid}/request

User: client_user
Publish: rpi-zero2w/still-camera/+/request
Subscribe: rpi-zero2w/still-camera/+/response
```

Note: HiveMQ supports `${clientid}` substitution for dynamic topic restrictions.

## References

- [Mosquitto Authentication](https://mosquitto.org/man/mosquitto-conf-5.html)
- [MQTT Security Fundamentals](https://www.hivemq.com/mqtt-security-fundamentals/)
- [ACL Best Practices](https://cedalo.com/blog/mqtt-acl-access-control-list-best-practices/)
