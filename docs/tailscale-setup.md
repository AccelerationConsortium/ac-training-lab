# Tailscale Setup

[Tailscale](https://tailscale.com/) is a "mesh VPN" that allows secure access to devices across different networks. It simplifies remote access and management of devices.

The following covers [tailscale setup](#general-setup-instructions) for general-purpose machines (Linux, macOS, Windows, RPi OS) and SSH access, [setup for an OT-2 environment](#installing-and-auto-starting-tailscale-on-ot-2-opentrons) which requires special installation steps, and [instructions for remote desktop](#remote-desktop-on-windows) on Windows.

## General Setup Instructions

Follow the [Bookworm tailscale installation instructions](https://tailscale.com/kb/1174/install-debian-bookworm) (or follow the appropriate device instructions at https://tailscale.com/kb/1347/installation if not using bookworm). It's convenient to SSH into the device over the same WiFi network to make copy-pasting commands into the terminal easier (rather than trying to type them out).

You can see which RPi OS version you have (assuming you're using RPi OS) [by running](https://www.cyberciti.biz/faq/linux-command-print-raspberry-pi-os-version-on-raspberry-pi/) `hostnamectl` or using `cat /etc/os-release`. However, if you're using Ubuntu OS on your RPi, you'll [need to run](https://www.google.com/search?q=check+ubuntu+version) `lsb_release -a`.

On the device, [enable SSH](https://tailscale.com/kb/1193/tailscale-ssh), as mentioned in [How to SSH into a Raspberry Pi](https://tailscale.com/learn/how-to-ssh-into-a-raspberry-pi):
```
sudo tailscale up --ssh
```

Aside: You can check RPi serial number via `cat /proc/cpuinfo`, potentially useful for MQTT.

For VS Code / Tailscale Extension development, you'll probably want to disable incoming connections on your personal computer. If it's already installed on your computer, go to the corresponding icon on the toolbar and deselect it:

![image](https://github.com/user-attachments/assets/3e59525c-b2a4-44bd-8935-b685abc13ddb)

In the [machine tab of the tailscale admin console](https://login.tailscale.com/admin/machines), to be able to access devices managed by other users, follow the instructions mentioned in https://github.com/AccelerationConsortium/ac-training-lab/issues/184#issuecomment-2718880751:

Add:
```
	"tagOwners": {
		"tag:tailscale-ssh": ["autogroup:admin"],
	},
```
(or could be `["autogroup:member"]`, noting that members don't get to see the admin console)

Change `"dst":    ["autogroup:self"],` to e.g., `"dst":   ["tag:tailscale-ssh"],` (here it's showing `tailscale-ssh` as the tag, but you can use whatever tag name you'd like)

You also might want to ["disable key expiry"](https://tailscale.com/kb/1028/key-expiry) for the Raspberry Pi devices (see link for context about the security of doing so)

![image](https://github.com/user-attachments/assets/23ad57b6-e39f-4694-86ee-7c5d685c763f)

## VS Code Configuration

Also, consider updating the default SSH username in VS Code settings (Ctrl+,), since it will be your PC's username by default (which may not correspond to the username on the RPi).

Within the tailscale sidebar interface, I found it useful to try to connect to the terminal first, go through the prompts, then click the "Attach VS Code" button and follow any prompts again. I've had some issues (https://github.com/AccelerationConsortium/ac-training-lab/issues/184#issuecomment-2719179967) with getting VS Code errors when trying to go directly to "Attach VS Code" for a new device. If you click "details" while it's loading, you will likely find that it's waiting on you to authenticate by accessing a particular link.

Additional resources:
- https://www.reddit.com/r/Tailscale/comments/11c69q5/how_can_i_authenticate_a_headless_device/
- https://tailscale.com/kb/1174/install-debian-bookworm
- https://forums.raspberrypi.com/viewtopic.php?t=374609
- https://tailscale.com/kb/1265/vscode-extension
- https://tailscale.com/learn/how-to-ssh-into-a-raspberry-pi

---

## Installing and Auto-starting Tailscale on OT-2 (Opentrons)

**Note:** OT-2 runs a minimal [Buildroot-based system](https://github.com/Opentrons/buildroot) with a read-only root filesystem and limited network utilities. This guide works within those constraints.

 You'll use `vi` as the default editor because simpler editors like `nano` are typically not available on Buildroot systems.

### Download Static Tailscale Binary

On your computer, download the [static ARM binary](https://pkgs.tailscale.com/stable/#static) for Tailscale:

For current version of OT-2, you will use [Tailscale_1.82.0_arm.tgz](https://pkgs.tailscale.com/stable/tailscale_1.82.0_arm.tgz)


Send the file to the data directory on OT-2:

```bash
scp -i <your_ssh_key> -O tailscale_1.82.0_arm.tgz root@<ot2_ip>:/data/
```

SSH into OT-2 and run:

```bash
cd /data
tar -xzf tailscale_1.82.0_arm.tgz
```

This will extract two files: `tailscaled` and `tailscale`.

### Manually Start and Authenticate

With SSH into OT-2, run:

```
/data/tailscale_1.82.0_arm/tailscaled --tun=userspace-networking &
```
Then
```
/data/tailscale_1.82.0_arm/tailscale up --ssh
```

Since OT-2 does not have the required network driver for Tailsclae, you need to use [userspace-networking mode.
](https://tailscale.com/kb/1112/userspace-networking)

You will have an authentication link after running the code above. Open the given URL in a browser to authenticate the device to your Tailscale account.

This command`tailscale up --ssh `also enables SSH access over Tailscale.

Login to the Tailscale admin account. You should be able to see a new OT-2 shown in machines list. Assign the ACL tag `tailscale-SSH` for the new device.

You may also test the SSH before starting up the auto start script.

### Create Tailscale Startup Script

Create a script to start Tailscale.

```bash
vi /data/start_tailscale.sh
```

Press "i" to insert mode in vi.

Paste:

```sh
#!/bin/sh

if ! ps | grep '[t]ailscaled' > /dev/null; then
    echo "Starting tailscaled..." >> /tmp/tailscale-watch.log
    nohup /data/tailscale_1.82.0_arm/tailscaled --tun=userspace-networking > /tmp/tailscaled.log 2>&1 &
    sleep 5
    /data/tailscale_1.82.0_arm/tailscale up --ssh >> /tmp/tailscale-up.log 2>&1
else
    echo "tailscaled already running" >> /tmp/tailscale-watch.log
fi
```

Press ESC then ":wq" + Enter to save your edit.

Make it executable:

```bash
chmod +x /data/start_tailscale.sh
```

### Set Up Systemd Auto-Start

To make tailscaled start automatically at boot (even without SSH login), we will use a systemd service. Since `/etc/` is normally read-only on OT-2, we must temporarily remount it as writable.

SSH into your OT-2 and remount `/` as writable:

```bash
mount -o remount,rw /
```
> ⚠️ **Note on remounting `/` as writable:**
>
> Temporarily remounting `/` with `mount -o remount,rw /` is necessary to create the systemd service.
> However, keep in mind that modifying a normally read-only root filesystem may increase the risk of accidental system changes.
> Make sure to only modify what's necessary, and the system will automatically return to read-only after a reboot.

Create the systemd service file:

```bash
vi /etc/systemd/system/tailscale-autostart.service
```

Paste the following content:

```ini
[Unit]
Description=Start tailscaled on boot
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=/data/start_tailscale.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Enable the service and reload systemd:

```bash
systemctl daemon-reload
systemctl enable tailscale-autostart.service
```

Note that rebooting the OT-2 will automatically restore the default read-only state.

You can also manually start the service to test:

```bash
systemctl start tailscale-autostart.service
```

To verify:

```bash
/data/tailscale_1.82.0_arm/tailscale status
```

To check service logs:
```bash
systemctl status tailscale-autostart.service
```

Now, you can reboot OT-2 and see if the device on the admin page of Tailscale will become offline and then `Connected` again

### Summary of File Locations (OT-2)

| File | Purpose |
|------|---------|
| `/data/tailscale_1.82.0_arm/tailscaled` | Tailscale daemon |
| `/data/tailscale_1.82.0_arm/tailscale` | Tailscale CLI |
| `/data/start_tailscale.sh` | Startup script |
| `/etc/systemd/system/tailscale-autostart.service` | Systemd autostart service definition |

## Remote Desktop on Windows

Tailscale SSH isn't directly supported on Windows, and SSH on Windows machines can get a bit messy. However, you can still use Tailscale to set up remote desktop access. Note that you can only do this on Windows 10/11 Pro or Windows 10/11 Enterprise, not on Windows 10/11 Home.

[Install tailscale for Windows](https://tailscale.com/kb/1022/install-windows). We recommend using a private browser for the interactive login step if this is a non-personal device. You may need to copy the auto-opened URL to the private browser manually. Next, set up the "Remote Desktop Protocol" (RDP) [according to tailscale's documentation](https://tailscale.com/kb/1095/secure-rdp-windows).

Finally, [enable Remote Desktop on your device](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/remotepc/remote-desktop-allow-access):

<img src=https://github.com/user-attachments/assets/050746cd-a4ff-4bf4-ae4a-5ad1d74f05c1 width=400 alt="Screenshot of enabling Remote Desktop on Windows">

Then, on the device you're planning to use to access the remote device, use Windows' built-in remote desktop:

<img width=350 alt="Image" src="https://github.com/user-attachments/assets/d43c2633-439a-4bd1-a914-c029cdd2ab61" />

You'll enter your full domain:

<img width=350 alt="Image" src="https://github.com/user-attachments/assets/6b947cda-e357-4ca4-a776-08ee7d023cb5" />

Assuming you have access to the admin console, you can find full domain by clicking on the hostname of the corresponding machine within https://login.tailscale.com/admin/machines

This is of the form: `<hostname>.<tailnet-id>.ts.net`

Otherwise, as long as you know the hostname and tailnet ID, you can manually construct that full domain and enter it in. Then, you just need to log in as normal with the remote device's username and password.

_Based on https://github.com/AccelerationConsortium/ac-training-lab/issues/376_
