# Raspberry Pi WPA2-Enterprise WiFi Setup

This guide provides step-by-step instructions for connecting Raspberry Pi devices to institutional WiFi networks that use WPA2-Enterprise security (commonly found in universities and corporate environments). This setup is required for devices like the [picam](picam.md), [a1_cam](a1_cam.md), and other Raspberry Pi-based equipment in the AC Training Lab when operating on enterprise networks.

## Overview

WPA2-Enterprise networks use 802.1X authentication with various EAP (Extensible Authentication Protocol) methods instead of a simple shared password. Common EAP methods include:

- **PEAP-MSCHAPv2**: Most common in Windows/Active Directory environments
- **EAP-TLS**: Certificate-based authentication
- **EAP-TTLS**: Tunneled TLS authentication

This guide covers the most common scenario (PEAP-MSCHAPv2) but provides guidance for other methods.

## Prerequisites

- Raspberry Pi running Raspberry Pi OS (Lite or Desktop)
- SSH access to the Pi or physical access with keyboard/monitor
- Network credentials from your IT administrator:
  - Username and password
  - EAP method (e.g., PEAP, EAP-TLS, EAP-TTLS)
  - Phase 2 authentication method (for PEAP/EAP-TTLS)
  - CA certificate (if required)

## Method 1: Using wpa_supplicant Configuration File (Recommended)

### Step 1: Backup Current Configuration

```bash
sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.backup
```

### Step 2: Edit wpa_supplicant Configuration

```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

### Step 3: Add Enterprise Network Configuration

Add the following configuration to the file, replacing the placeholder values with your network details:

#### For PEAP-MSCHAPv2 (Most Common)

```bash
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid="YourNetworkName"
    key_mgmt=WPA-EAP
    eap=PEAP
    identity="your_username"
    password="your_password"
    phase2="auth=MSCHAPV2"
    # Uncomment and modify if you have a CA certificate
    # ca_cert="/etc/ssl/certs/your_ca_cert.pem"
    # Uncomment to disable certificate validation (less secure)
    # phase1="peapver=0 peaplabel=0"
}
```

#### For EAP-TLS (Certificate-based)

```bash
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid="YourNetworkName"
    key_mgmt=WPA-EAP
    eap=TLS
    identity="your_username"
    client_cert="/path/to/client_cert.pem"
    private_key="/path/to/private_key.pem"
    private_key_passwd="private_key_password"
    ca_cert="/path/to/ca_cert.pem"
}
```

#### For EAP-TTLS

```bash
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid="YourNetworkName"
    key_mgmt=WPA-EAP
    eap=TTLS
    identity="your_username"
    password="your_password"
    phase2="auth=MSCHAPV2"
    ca_cert="/path/to/ca_cert.pem"
}
```

### Step 4: Set Proper Permissions

```bash
sudo chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf
```

### Step 5: Restart Networking Services

```bash
sudo systemctl restart wpa_supplicant
sudo systemctl restart dhcpcd
```

Or reboot the system:

```bash
sudo reboot
```

## Method 2: Using raspi-config (Alternative)

### Step 1: Open raspi-config

```bash
sudo raspi-config
```

### Step 2: Navigate to Network Options

1. Select **System Options** or **Network Options** (depending on your version)
2. Select **Wireless LAN**

### Step 3: Enter Network Details

1. Enter the SSID (network name)
2. For the passphrase, you'll need to use a specific format for enterprise networks:

For PEAP-MSCHAPv2, use this format as the "passphrase":
```
"PEAP:your_username:your_password"
```

**Note**: This method has limitations and may not work with all enterprise configurations. The wpa_supplicant method is more reliable.

## Obtaining CA Certificates

If your network requires CA certificate validation:

### Download from IT Department

Contact your IT department for the CA certificate file (usually a .pem, .crt, or .cer file).

### Extract from Browser (Alternative)

1. On a computer connected to the network, open a web browser
2. Visit any HTTPS site
3. Click on the security icon and view certificate details
4. Export the root/intermediate certificate

### Install the Certificate

```bash
# Copy certificate to the Pi (example using scp)
scp ca_cert.pem pi@your_pi_ip:/home/pi/

# Move to system certificate directory
sudo cp ca_cert.pem /etc/ssl/certs/
sudo chmod 644 /etc/ssl/certs/ca_cert.pem
```

## Troubleshooting

### Check Connection Status

```bash
# Check if connected
ip addr show wlan0

# Check wpa_supplicant status
sudo wpa_cli status

# View detailed logs
sudo journalctl -u wpa_supplicant -f
```

### Common Issues and Solutions

#### Connection Timeout

- Verify credentials with IT department
- Check if the certificate is required
- Try disabling certificate validation temporarily (less secure):
  ```bash
  phase1="peapver=0 peaplabel=0"
  ```

#### Authentication Failure

- Double-check username and password
- Verify the correct EAP method with your IT department
- Check if domain is required (e.g., `username@domain.com` vs `domain\username`)

#### Certificate Issues

- Ensure CA certificate is in the correct format (PEM)
- Verify certificate path in configuration
- Check certificate permissions (should be readable by all users)

#### MAC Address Filtering

Some networks require device registration:
```bash
# Find your MAC address
ip link show wlan0
```
Contact IT to register this MAC address.

## Testing the Connection

### Basic Connectivity Test

```bash
# Test internet connectivity
ping -c 4 google.com

# Test DNS resolution
nslookup google.com

# Check IP assignment
ip route show
```

### Network Information

```bash
# View current connection details
iwconfig wlan0

# Show detailed wireless information
sudo iw dev wlan0 info
```

## Security Considerations

1. **Credential Storage**: The configuration file contains credentials in plain text. Ensure proper file permissions (600).

2. **Certificate Validation**: Always use CA certificate validation when possible. Disabling it makes your connection vulnerable to man-in-the-middle attacks.

3. **Regular Updates**: Keep your Raspberry Pi OS updated for the latest security patches.

4. **Backup Configuration**: Always backup working configurations before making changes.

## Integration with AC Training Lab Devices

When setting up specific AC Training Lab devices that use Raspberry Pi hardware, refer to this documentation for the WiFi setup portion, then continue with the device-specific setup instructions:

- **[Picam](picam.md)**: Overhead camera system
- **[A1 Mini Camera](a1_cam.md)**: Toolhead camera for 3D printer monitoring
- **[Pioreactor](pioreactor.md)**: Automated bioreactor system

For these devices, complete the WPA2-Enterprise setup first, then proceed with the device-specific installation and configuration steps.

## Additional Resources

- [Raspberry Pi Official Documentation](https://www.raspberrypi.org/documentation/configuration/wireless/)
- [wpa_supplicant Configuration Guide](https://w1.fi/cgit/hostap/plain/wpa_supplicant/wpa_supplicant.conf)
- [AC Training Lab Device Setup Guide](setup_iolt_devices.md)

## Support

If you encounter issues specific to your institution's network configuration, contact your local IT support team. For issues related to AC Training Lab devices, create an issue in the [AC Training Lab GitHub repository](https://github.com/AccelerationConsortium/ac-training-lab/issues).