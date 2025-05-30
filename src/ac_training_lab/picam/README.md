# RPi Zero 2W Streaming Cameras

This is intended to be run on a Raspberry Pi Zero 2W Raspberry Pi Camera
Module 3 running [RPi OS Lite (bookworm, 64-bit)](https://www.raspberrypi.com/software/operating-systems/).

## Bill of Materials

The following components are required for the equipment monitoring setup:

### Core Hardware
- [Raspberry Pi Zero 2W](https://www.pishop.ca/product/raspberry-pi-zero-2-w/) - ~$24 CAD
- MicroSD Card 32GB Class 10 - ~$15 CAD (available from electronics retailers)
- Heat Sink Kit for RPi Zero - ~$6 CAD (available from electronics retailers)

### Camera Components  
- [Raspberry Pi Camera Module 3](https://www.pishop.ca/product/raspberry-pi-camera-module-3/) - ~$35 CAD
- Raspberry Pi Zero Camera Cable - ~$8 CAD (available from electronics retailers)
  - *Note: The RPi Camera Module 3 comes with a long cable, but a shorter one might be desired for cleaner mounting*

### Power
- USB-C Power Supply 5V 3A Official - ~$15 CAD (available from electronics retailers)
- Alternative: USB-C cable for power from computer/hub

### Mounting Hardware
**Option A:** Off-the-shelf mount kit
- [Pro Mini Camera Mount for Raspberry Pi Zero](https://www.pishop.ca/product/pro-mini-camera-mount-for-raspberry-pi-zero/) - ~$25 CAD

**Option B:** DIY mounting solution (recommended):
- [3D Printable PiCam Mount](https://github.com/AccelerationConsortium/ac-training-lab/tree/main/src/ac_training_lab/picam/_design) (STL files in repository)
- M2 x 8mm Screws (4x) + M2 Nuts (4x) - ~$5 CAD (available from hardware stores)
- M2.5 x 12mm Screws (4x) + M2.5 Hex Standoffs (4x) + M2.5 Nuts (4x) - ~$8 CAD (available from hardware stores)

### Rod Clamp Assembly & Mounting
- [Camera Desk Mount Table Stand](https://www.primecables.ca/p-407778-cab-lsd01-1s-camera-desk-mount-table-stand) - Prime Cables
- [5/16" Hex Nut](https://www.mcmaster.com/91078A029/) - McMaster-Carr for secure rod mounting

### Tools Required
- [Small Precision Screwdriver](https://www.mcmaster.com/7845A36/) - McMaster-Carr
- [2.5mm Hex Key/Allen Wrench](https://www.mcmaster.com/7648A72/) - McMaster-Carr
- Hex nut tool with handle for tightening (recommended)

**Total estimated cost: ~$116-128 CAD** (excluding 3D printing, camera desk mount, and tools)

> **Note:** Electronic components are available from various retailers including PiShop.ca, electronics distributors, and online retailers. Specific product links are provided where verified to work. Hardware components like screws and nuts are available at local hardware stores.

## Codebase

Refresh the system's package list via:
```
sudo apt update
```

Optionally, upgrade the system packages to the latest versions via `sudo apt upgrade -y` (`-y` flag is used to automatically answer "yes" to any installation prompts)

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
cd /home/ac/ac-training-lab/src/ac_training_lab/picam/
```

## Secrets

Make a copy of `my_secrets_example.py` called `my_secrets.py`:
```bash
cp my_secrets_example.py my_secrets.py
```

Fill in the necessary information (e.g., via `nano my_secrets.py`). Keep in mind this will store the credentials in plain-text format, so try to keep your Pi login secure and restrict the access scope for the credentials as much as possible.

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

<!-- Next, install the requirements via:

```bash
pip install -r requirements.txt
``` -->

## "Local" (i.e., not RPi OS) OS Development

For local development (e.g., on your PC rather than the Raspberry Pi to make version control easier) with a dummy version of `picamera2` (very minimal mock package), while in the same folder as this README file, additionally run `pip install -e ./dummy_pkg/`. WARNING: do not install this on the Raspberry Pi for the toolhead camera -- the imports will overlap with the "real" system packages `picamera2` and `libcamera`.

## Running the Device

To start the device manually and ensure that it's functioning normally, run:

```bash
python3 device.py
```

## Automatic startup

To create the file, run nano (or other editor of choice):

```bash
sudo nano /etc/systemd/system/device.service
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
sudo systemctl enable device.service
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

Manually start the service by running:

```bash
sudo systemctl start device.service
```

This command tells systemd to run your service immediately (as if it had been triggered at boot). To check its status, use:

```bash
sudo systemctl status device.service
```

To view any logs:

```bash
sudo journalctl -u device.service -f
```

Starting the service with `systemd` is recommended since it applies all the configured options (dependencies, restart behavior, etc.).

For more details, see the [systemctl(1)](https://www.freedesktop.org/software/systemd/man/systemctl.html) manual.


To stop the service (for example, while you work on fixing it / pulling new changes), run:

```bash
sudo systemctl stop device.service
```

This command stops the running instance of the service immediately. If you also want to prevent it from starting at boot until you've fixed it, you can disable it with:

```bash
sudo systemctl disable device.service
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


Related issue(s):
- https://github.com/AccelerationConsortium/ac-training-lab/issues/11
- https://github.com/AccelerationConsortium/ac-training-lab/issues/161
- https://github.com/AccelerationConsortium/ac-training-lab/issues/80


<!-- While a virtual environment on RPi OS Lite will give you pip, this does not come preinstalled on the built-in Python on RPi OS Lite. To install pip, run:
```bash
sudo apt install python3-pip -y
```
> NOTE: The `-y` flag is used to automatically answer "yes" to any installation prompts. -->
