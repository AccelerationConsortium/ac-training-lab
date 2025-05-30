# A1 Mini Overhead Toolhead Camera

This is intended to be run on a Raspberry Pi Zero 2W Raspberry Pi Camera
Module 3 running RPi OS Lite (bookworm).

## Bill of Materials

The following components are required for the equipment monitoring setup:

### Core Hardware
- [Raspberry Pi Zero 2W](https://pishop.ca/collections/raspberry-pi-zero/products/raspberry-pi-zero-2-w) - ~$24 CAD
- [MicroSD Card 32GB Class 10](https://pishop.ca/collections/micro-sd-cards/products/sandisk-ultra-microsdhc-card-32gb-class-10) - ~$15 CAD  
- [Heat Sink Kit for RPi Zero](https://pishop.ca/collections/cooling/products/heat-sink-kit-raspberry-pi-zero) - ~$6 CAD

### Camera Components  
- [Raspberry Pi Camera Module 3](https://pishop.ca/collections/camera/products/raspberry-pi-camera-module-3) - ~$35 CAD
- [Raspberry Pi Zero Camera Cable](https://pishop.ca/collections/camera/products/raspberry-pi-zero-camera-cable) - ~$8 CAD

### Power
- [USB-C Power Supply 5V 3A Official](https://pishop.ca/collections/power/products/raspberry-pi-15w-usb-c-power-supply) - ~$15 CAD
- Alternative: USB-C cable for power from computer/hub

### Mounting Hardware
**Option A:** Complete mount kit with all hardware included

**Option B:** DIY mounting solution (recommended):
- 3D Printable PiCam Mount (STL files - contact repository maintainer)
- [M2 x 8mm Screws (4x) + M2 Nuts (4x)](https://pishop.ca/collections/hardware/products/m2-screws-nuts-assortment) - ~$5 CAD
- [M2.5 x 12mm Screws (4x) + M2.5 Hex Standoffs (4x) + M2.5 Nuts (4x)](https://pishop.ca/collections/hardware/products/m2-5-screws-standoffs-nuts-kit) - ~$8 CAD

### Rod Clamp Assembly & Mounting
- Rod clamp assembly (for 8mm rod system) - contact supplier for compatibility
- 5/16" Hex Nut for secure rod mounting - available at hardware stores

### Tools Required
- Phillips head screwdriver
- 2.5mm hex key/Allen wrench

**Total estimated cost: ~$120-140 CAD** (excluding 3D printing and rod clamp assembly)

> **Note:** Links point to approximate product categories on PiShop.ca. Please verify exact part numbers and availability when ordering. The 5/16" hex nut specification is based on standard rod clamp requirements.

## Codebase

Optionally, update the system packages to the latest versions (`-y` flag is used to automatically answer "yes" to any installation prompts):
```bash
sudo apt update
sudo apt upgrade -y
```

Ensure that `git` is installed:
```bash
sudo apt-get install git -y
```

Clone the repository to your Raspberry Pi Zero 2W device via HTTPS (allows for `git pull` to work without needing to enter credentials each time):

```bash
git clone https://github.com/AccelerationConsortium/ac-training-lab.git
```

Navigate to the same directory as this README file:

```bash
cd /home/ac/ac-training-lab/src/ac_training_lab/a1_cam/
```

## Secrets

Make a copy of `my_secrets_example.py` called `my_secrets.py`:
```bash
cp my_secrets_example.py my_secrets.py
```

Fill in the necessary information. Keep in mind this will store the credentials in plain-text format, so try to keep your Pi login secure and restrict the access scope for the credentials as much as possible (e.g., topic filtering for MQTT and bucket policies for S3).

## Dependencies

If not already installed (not pre-installed on RPi OS Lite), install [`picamera2`](https://github.com/raspberrypi/picamera2) via:

```bash
sudo apt install python3-picamera2 --no-install-recommends
```

`libcamera` should be automatically installed after installing `picamera2`. Otherwise, one would use `sudo apt install -y python3-libcamera` (`libcamera` also does not come preinstalled on RPi OS Lite versions).

Also install [`FFmpeg`](https://github.com/FFmpeg/FFmpeg):

```bash
sudo apt install ffmpeg --no-install-recommends
```

Use the `venv` command to create a virtual environment to a new folder `venv` with the `--system-site-packages` flag so that it can use the `picamera2` and `libcamera` libraries and activate the environment via the following commands:

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

While one could use the built-in Python installation (this device is intended to be run via a single top-level script, the RPi device (in our case RPi Zero 2W) requires minimal setup (i.e., can easily be reflashed), and the RPi device is intended for a single purpose with a single set of requirements (i.e., a "point-and-shoot" camera)), the extra steps involved to make this work are as equally onerous as using a venv [[context](https://github.com/AccelerationConsortium/ac-training-lab/pull/178#issuecomment-2730490626)], hence we only include instructions assuming a venv.

Next, install the requirements via:

```bash
pip install -r requirements.txt
```

## "Local" (i.e., not RPi OS) OS Development

For local development (e.g., on your PC rather than the Raspberry Pi to make version control easier) with a dummy version of `picamera2` (very minimal mock package), while in the same folder as this README file, additionally run `pip install -e ./dummy_pkg/`. WARNING: do not install this on the Raspberry Pi for the toolhead camera -- the imports will overlap with the "real" system packages `picamera2` and `libcamera`.

## Running the Device

To start the device manually and ensure that it's functioning normally, run:

```bash
python3 device.py
```

To verify quickly that this script works, you can run `_scripts/client.py` locally (e.g., on your PC), ensuring that you have the same credentials in a `my_secrets.py` located in the `_scripts` directory as you do on the RPi. This script will request the latest image from the device and save it to your local machine.

## Automatic startup

To create the file, run nano (or other editor of choice):

```bash
sudo nano /etc/systemd/system/a1-cam.service
```

Copy the following code into the file (right click to paste), save it via `Ctrl+O` and `Enter` and exit via `Ctrl+X`:

```yaml
[Unit]
Description=Start picam device.py script
After=network-online.target
Wants=network-online.target

[Service]
# Launch the device script (adjust the path as needed)
WorkingDirectory=/home/ac/ac-training-lab/src/ac_training_lab/picam
# Best to specify the full path to the Python interpreter or use ExecSearchPath
ExecStart=/home/ac/ac-training-lab/src/ac_training_lab/picam/venv/bin/python3 device.py
# Restart whenever the script exits ('always' because sometimes it throws an error but still exits gracefully)
Restart=always
RestartSec=10

# Limit restart attempts to avoid a rapid infinite loop (e.g., up to max 9 times per day, assuming a StartLimitBurst of 3, 28800 seconds == 8 hours, "h" syntax wasn't working on RPi, so using seconds)
StartLimitInterval=3600
StartLimitBurst=3

# Allow up to 60 seconds for the script to start properly
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target
```

Run:
```
sudo systemctl daemon-reload
sudo systemctl enable a1-cam.service
sudo systemctl start a1-cam.service
```

Run:

```bash
sudo crontab -e
```

Add the following at the end of the crontab file:

```bash
#
# Restart at 2 am, local time (set up during flashing, or specified manually via e.g., `sudo timedatectl set-timezone America/New_York`)
0 2 * * * /sbin/shutdown -r now
```

You can manually start the service by running:

```bash
sudo systemctl start a1-cam.service
```

This command tells systemd to run your service immediately (as if it had been triggered at boot). To check its status, use:

```bash
sudo systemctl status a1-cam.service
```

To view any logs:

```bash
sudo journalctl -u a1-cam.service -f
```

Starting the service with `systemd` is recommended since it applies all the configured options (dependencies, restart behavior, etc.).

For more details, see the [systemctl(1)](https://www.freedesktop.org/software/systemd/man/systemctl.html) manual.


To stop the service (for example, while you work on fixing it / pulling new changes), run:

```bash
sudo systemctl stop a1-cam.service
```

This command stops the running instance of the service immediately. If you also want to prevent it from starting at boot until you've fixed it, you can disable it with:

```bash
sudo systemctl disable a1-cam.service
```

To get it to reflect the new changes, run:

```bash
sudo systemctl daemon-reload
```

You can list all available service unit files by running:

```bash
systemctl list-unit-files --type=service
```

This will display a list of service files along with their state (enabled, disabled, static, etc.). It shows unit files from all directories (such as `/etc/systemd/system`, `/usr/lib/systemd/system`, and `/run/systemd/system`).

For a list of all loaded (active or inactive) service units, you can use:

```bash
systemctl list-units --all --type=service
```

For more details on managing services, check out the [systemctl(1)](https://www.freedesktop.org/software/systemd/man/systemctl.html) manual [[transcript](https://chatgpt.com/share/67da116e-184c-8006-99b3-a49fc08eb1bb)].



<!-- While a virtual environment on RPi OS Lite will give you pip, this does not come preinstalled on the built-in Python on RPi OS Lite. To install pip, run:
```bash
sudo apt install python3-pip -y
```
> NOTE: The `-y` flag is used to automatically answer "yes" to any installation prompts. -->
