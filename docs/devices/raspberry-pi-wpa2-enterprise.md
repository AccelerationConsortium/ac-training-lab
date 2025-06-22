# Raspberry Pi WPA2-Enterprise WiFi Setup

This guide provides instructions for connecting Raspberry Pi devices to WPA2-Enterprise WiFi networks (commonly found in institutional environments). This setup is required for devices like the [picam](picam.md), [a1_cam](a1_cam.md), and other Raspberry Pi-based equipment in the AC Training Lab when operating on enterprise networks.

Consider running your devices in headless mode (e.g., Raspberry Pi OS Lite (bookworm)) in general, especially for any Raspberry Pi Zero 2W's that we have, to reduce the resources consumed by the OS.

Some considerations:

- Connecting to WPA2-Enterprise WiFi. After a lot of troubleshooting and debugging, I found a good way to get this working on bookworm:

## Connecting to WPA2-Enterprise WiFi

*following based on ChatGPT prompt, username redacted*

> Connect to a WPA2-Enterprise network on a headless Raspberry Pi Zero 2W running OS Lite (bookworm). I have access to the terminal already. It's on a WPA2-personal network at the moment, and I want to switch it to a WPA2-Enterprise network (specifically, University of Toronto wireless with SSID "UofT") ... How can I do this without exposing my password to the command line?

**1. Verify the Current Network Status:**

First, let's check the current status of your wireless interface (`wlan0`) to understand its state.

```bash
ip addr show wlan0
```

This command will display the IP address and connection status of `wlan0`.

**2. Install Necessary Packages:**

Ensure that `network-manager` and its associated tools are installed, as they provide utilities like `nmcli` and `nmtui` for network configuration.

```bash
sudo apt update
sudo apt install network-manager
```

Optionally, you can run `sudo apt upgrade` to upgrade all packages.

**3. Disable Conflicting Network Services:** [OPTIONAL]

To prevent conflicts, optionally disable other network management services such as `dhcpcd` (this may not apply to bookworm, but may help with earlier versions like buster). If you get `Failed to disable unit: Unit file dhcpcd.service does not exist.` you can ignore this.

```bash
sudo systemctl disable dhcpcd
sudo systemctl stop dhcpcd
```

**4. Enable and Start NetworkManager:**

Activate `NetworkManager` to manage network connections.

```bash
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager
```

**5. Configure the WPA2-Enterprise Connection Using `nmtui`:**

The `nmtui` (NetworkManager Text User Interface) tool provides an interactive way to set up network connections.

```bash
sudo nmtui
```

Within the `nmtui` interface:

- Select **"Edit a connection"**.
- Choose **"Add"**, then **"Wi-Fi"**.
- Set the **SSID** to "UofT".
- Under **"Wi-Fi Security"**, select **"WPA & WPA2 Enterprise"**.

![image](https://github.com/user-attachments/assets/1913a298-fdba-4f03-98af-5f8502231c19)

- For **"Authentication"**, choose **"Protected EAP (PEAP)"**.
- Enter your UTORid ("***") in the **"Username"** field.
- Enter the domain (in UofT's case, `radius.wireless.utoronto.ca` per their online instructions, NOTE: `.utoronto.ca` not `@utoronto.ca`)
- Leave **"Anonymous identity"** blank unless specified otherwise by the university's IT guidelines. If the interface requires you to enter something, try entering whatever you'd like (e.g., `anonymous`). Sometimes, it just needs *a* value
- For **"CA Certificate"**, if the university provides a specific certificate, specify its path. <!-- If not, select **"No CA certificate is required"**. -->
- Set **"Inner authentication"** to **"MSCHAPv2"**.
- Enter your UTORid password in the **"Password"** field.

**Note that users with sudo or root access can see the password again if they go digging.** I suggest changing your university password to something unique and specific to it (e.g., memorable password [generated via 1password](https://1password.com/password-generator)). You could also do something like make sure only you have root access and create a non-admin account that others on your team can SSH into, but some consideration might be required when trying to get the device to autostart a script.

![image](https://github.com/user-attachments/assets/8145bdf2-e903-4794-afbe-5a2a8020daae)

After configuring these settings, save and exit `nmtui`.

**6. Connect to the "UofT" Network:**

Attempt to establish the connection using `nmcli`.

```bash
sudo nmcli connection up UofT
```

If you are SSH'd into the device, it may close your connection. If all goes well, you should be able to connect after waiting a minute or so. Otherwise, if something catastrophic happens (i.e., it's unable to connect at all), then you'll need access to the device to manually follow these steps.

<!--- originally had `--ask` flag, but doesn't seem relevant anymore because root can still access password -->

**7. Verify the Connection:**

Check if `wlan0` has obtained an IP address and is connected to the "UofT" network.

```bash
ip addr show wlan0
```

You can also check (example output also shown):

```bash
sudo nmcli dev status
```

> ```shell
> DEVICE         TYPE      STATE                   CONNECTION 
> wlan0          wifi      connected               UofT
> ```

Alternatively, you can use `sudo nmtui` and "Activate Connection" to see which one is currently active (which will have a `*`); however, if you are SSH'd into your device over WiFi, you will need to have a keyboard and mouse directly connected to the device in order to switch it this way (since you have to manually "Deactivate" before you can activate the new one, at which point your SSH connection is already broken).

**Additional Considerations:**

- **CA Certificate:** While some institutions require a CA certificate for secure connections, others do not. If the University of Toronto does not mandate a specific CA certificate, you can configure the connection without it. However, using a CA certificate enhances security by validating the server's identity.

- **Consult University IT Support:** For institution-specific configurations or requirements, reach out to the University of Toronto's IT services or consult their support documentation.

By following these steps, you should be able to connect your Raspberry Pi Zero 2W to the "UofT" WPA2-Enterprise Wi-Fi network using your UTORid "***".

Rebooting the device should still connect to the one most recently chosen.

## Various resources during troubleshooting

Various resources during troubleshooting (see list in comment):
- https://www.reddit.com/r/raspberry_pi/comments/18n47zi/comment/mhq1wdq/

## Integration with AC Training Lab Devices

When setting up specific AC Training Lab devices that use Raspberry Pi hardware, refer to this documentation for the WiFi setup portion, then continue with the device-specific setup instructions:

- **[Picam](picam.md)**: Overhead camera system
- **[A1 Mini Camera](a1_cam.md)**: Toolhead camera for 3D printer monitoring
- **[Pioreactor](pioreactor.md)**: Automated bioreactor system

For these devices, complete the WPA2-Enterprise setup first, then proceed with the device-specific installation and configuration steps.