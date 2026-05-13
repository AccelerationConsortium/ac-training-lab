# RPi Streaming Cameras for Equipment Monitoring

An example of equipment monitoring happening at the Acceleration Consortium is available at https://www.youtube.com/@ac-hardware-streams.

This is intended to be run on a Raspberry Pi Zero 2W Raspberry Pi Camera
Module 3 running [RPi OS Lite (bookworm, 64-bit)](https://www.raspberrypi.com/software/operating-systems/).

```{include} ../../docs/_snippets/network-setup-note.md
```

![image](https://github.com/user-attachments/assets/244cf2dd-34bb-4a6c-b78a-52ec8d7bd6dc)

![image](https://github.com/user-attachments/assets/73200d69-44a9-4e46-ad1e-44e7c9dface4)

## Bill of Materials

The following components are required for the equipment monitoring setup.

```{note}
There is a [standalone DigiKey cart](https://www.digikey.ca/short/pwmfm83t) available containing most (not all) of the required components, including the optionals of HDMI and USB-A port adapters
```

### Core Hardware
- [Raspberry Pi Zero 2W](https://www.pishop.ca/product/raspberry-pi-zero-2-w/) (or [Zero 2WH](https://www.digikey.ca/en/products/detail/raspberry-pi/SC0721/24627135)) - $21.50 CAD
- [MicroSD Card 32GB Class 10](https://www.pishop.ca/product/raspberry-pi-sd-card-32gb/) - $13.95 CAD
- [MicroSD Card Reader](https://www.pishop.ca/product/usb-2-0-keychain-micro-sd-card-reader/) - $2.95 CAD
- [Aluminum Heatsink for Raspberry Pi B+/2/3 (2-Pack)](https://www.pishop.ca/product/aluminum-heatsink-for-raspberry-pi-b2-2-pack/) - $2.45 CAD
  - Alternative: [Heat Sink Kit for RPi Zero](https://www.pishop.ca/product/dedicated-aluminum-heatsink-for-raspberry-pi-zero-series-zero-zero-2-w/) - $5.95 CAD **[OPTIONAL - better cooling]**
  - *Note: The cheaper heat sink is the default as it doesn't require additional hardware. The more expensive one provides better cooling.*

### Camera Components
- [Raspberry Pi Camera Module 3](https://www.pishop.ca/product/raspberry-pi-camera-module-3/) - $35.00 CAD
- [Raspberry Pi Zero Camera Cable](https://www.pishop.ca/product/raspberry-pi-zero-mini-camera-cable-38mm/) - $3.95 CAD **[OPTIONAL]**
  - *Note: The RPi Camera Module 3 comes with a long cable you can use, but you can replace it with this shorter cable for cleaner mounting*

### Power

- [Compact 2A Power Adapter with USB-A socket](https://www.digikey.ca/en/products/detail/globtek-inc/WR9HA2000USBFMR6B/8598255) - $16.65 CAD
- [USB-A male to Micro USB male cable (2m)](https://www.digikey.ca/en/products/detail/cvilux-usa/DH-20M50056/13177301) - $3.19 CAD
  - *Note: Pi Zero 2W uses micro USB for power, not USB-C*

- [USB-A extension cable (2m)](https://www.digikey.ca/en/products/detail/assmann-wsw-components/AK669-2-18-BLACK/2391690) - $5.54 CAD **[OPTIONAL]**

- [International Power Adapter](https://www.digikey.ca/en/products/detail/eaton-tripp-lite/UNIPLUGINT/4439442?gQT=1) - $33.93 CAD **[OPTIONAL, for international]**

### Optional Troubleshooting Items
These items are optional and don't factor into the final price shown. They're useful if you're unable to SSH into the machine:
- [Mini HDMI Plug to Standard HDMI Jack Adapter](https://www.pishop.ca/product/mini-hdmi-plug-to-standard-hdmi-jack-adapter/) - $3.45 CAD **[OPTIONAL]**
- [6FT High Speed HDMI Cable With Ethernet](https://www.pishop.ca/product/6ft-high-speed-hdmi-cable-with-ethernet-18gbps-28awg-gold-plated/) - $2.95 CAD **[OPTIONAL]**
- [USB OTG Host Cable - MicroB OTG male to A female](https://www.pishop.ca/product/usb-otg-host-cable-microb-otg-male-to-a-female/) - $3.45 CAD **[OPTIONAL]**
- [Wireless Keyboard and Mouse Combo with USB Dongle](https://a.co/d/dxV6WWj) - Amazon **[OPTIONAL]**
- External Monitor **[OPTIONAL]**
- *Note: These items provide a simple fix for situations where SSH access is unavailable*

### Mounting Hardware
**Option A:** Off-the-shelf mount kit
- [Pro Mini Camera Mount for Raspberry Pi Zero](https://www.pishop.ca/product/pro-mini-camera-mount-for-raspberry-pi-zero/) - $7.95 CAD
- *Note: Off-the-shelf mount works but might need to be secured so the two laser cut pieces don't wobble relative to each other*

**Option B:** DIY mounting solution (recommended):
- [3D Printable PiCam Mount](https://github.com/AccelerationConsortium/ac-training-lab/tree/main/src/ac_training_lab/picam/_design) (STL files in repository)
- **M2 Hardware (4 pieces needed):**
  - [M2 Nylon Hex Standoff Spacer Screw Nut Assortment Kit (150 Pieces)](https://www.pishop.ca/product/m2-nylon-hex-standoff-spacer-screw-nut-assortment-kit-160-pieces/) - $7.95 CAD - PiShop.ca
  - *Note: This kit contains 150+ pieces including screws, nuts, and standoffs. You only need 4 M2×12mm screws and 4 M2 nuts from this kit.*
- **M2.5 Hardware (4 pieces needed):**
  - [White Nylon Screw and Stand-off Set - M2.5 - 420 pieces](https://www.pishop.ca/product/white-nylon-screw-and-stand-off-set-m2-5-420-pieces/) - $18.95 CAD - PiShop.ca
  - *Note: This kit contains 420+ pieces including screws, nuts, and standoffs. You only need 4 M2.5×8mm screws, 4 M2.5 nuts, and 4 M2.5×8mm standoffs from this kit.*
- *Note: Assembly instructions available at [ThePiHut](https://thepihut.com/blogs/raspberry-pi-tutorials/pro-mini-camera-mount-assembly-guide)*

### Rod Clamp Assembly & Mounting
- [Camera Desk Mount Table Stand](https://www.primecables.ca/p-407778-cab-lsd01-1s-camera-desk-mount-table-stand) - Prime Cables (~$20-30 CAD)
- [1/4"-20 Hex Nut (7/16" hex driver required, or finger-tighten)](https://www.mcmaster.com/product/91078A029) - McMaster-Carr for secure rod mounting (~$5-10 CAD)

### Tools Required (separate from total cost)
- [Small Precision Screwdriver Set](https://www.mcmaster.com/product/52985A22) - McMaster-Carr (~$15-20 CAD)
- [2.5mm Hex Key/Allen Wrench](https://www.mcmaster.com/product/5984A23) - McMaster-Carr (~$10-15 CAD)
- [7/16" Hex Nut Driver Tool](https://www.mcmaster.com/7142A36/) - McMaster-Carr (~$5-10 CAD)

**Total estimated cost: 109-115 CAD** (as of 2025-05-31, excluding 3D printing, camera desk mount, hex nut, and tools)
**Tool costs: 30-45 CAD** (separate from main components, not included in total)

> **Note:** Most electronic components have verified working links to PiShop.ca. Hardware components like screws and nuts are available at local hardware stores or McMaster-Carr.

## Hardware Setup

Ensure you connect the camera cable properly. Follow these steps:

1. **Power off and disconnect your Raspberry Pi from any power source.**
2. Orient the camera ribbon cable so that the metal contacts face the connector on the Pi (with Pi Zero 2W lying flat on its back, metal contacts should be facing down)
3. Carefully insert the ribbon cable fully into the camera connector (with camera facing upside down, the metal contacts should be facing down as well)
4. Lock the connector latch to secure the cable.
5. Reconnect power and turn on your Raspberry Pi.

> **Safety Note:** Always disconnect power from your Raspberry Pi before attaching or removing the camera to prevent hardware damage.

The images below show the correct orientation and connection:

<img width="800" alt="image" src="https://github.com/user-attachments/assets/3447d543-afe4-49c7-978e-2383ca031973" />

<img width="800" alt="image" src="https://github.com/user-attachments/assets/c7e4afd4-7c6b-4d88-88a4-e2c6422b29fa" />

The following shows an assembled camera setup, without any mounting hardware:

<img width="800" alt="image" src="https://github.com/user-attachments/assets/e3f9e17e-1876-4ac6-9ecd-7747bae4a1ad" />

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

Navigate to the same directory as this README file. This assumes that your username is `ac`.

```bash
cd /home/ac/ac-training-lab/src/ac_training_lab/picam/
```

## Secrets

Make a copy of `my_secrets_example.py` called `my_secrets.py`:
```bash
cp my_secrets_example.py my_secrets.py
```

Fill in the necessary information (e.g., via `nano my_secrets.py`). Keep in mind this will store the credentials in plain-text format, so try to keep your Pi login secure and restrict the access scope for the credentials as much as possible.

### Required Configuration Variables

#### `LAMBDA_FUNCTION_URL`
The AWS Lambda Function URL for the YouTube streaming service. This Lambda function handles YouTube API authentication and stream management.

**Setup Steps:**
1. Deploy the [streamingLambda](https://github.com/AccelerationConsortium/streamingLambda) service to your AWS account
2. The deployment will provide you with a Function URL that looks like: `https://your-unique-id.lambda-url.region.on.aws/`
3. Use this URL as your `LAMBDA_FUNCTION_URL`

**Note:** The Lambda function requires YouTube API credentials to be set up in AWS (stored in S3). See the streamingLambda repository for detailed deployment instructions.

#### `CAM_NAME`
A descriptive name for this specific camera device. This appears in YouTube broadcast titles and helps identify individual cameras when you have multiple devices.

**Examples:** `"PiCam-01"`, `"LabCam-A"`, `"MainCamera"`

#### `WORKFLOW_NAME`
**CRITICAL:** This must be **unique** across all your streaming devices to prevent conflicts.

The workflow name is used to:
- Create and organize YouTube playlists
- Identify which streams to end/restart
- Group related video streams

**Requirements:**
- Must be unique across all devices (see [Issue #290](https://github.com/AccelerationConsortium/ac-dev-lab/issues/290))
- Keep it concise due to YouTube character limits
- Use descriptive names for your experimental setup or location

**Examples:** `"SDLT-Toronto-001"`, `"MyLab-Setup-A"`, `"AC-Synthesis-Bench"`

#### `PRIVACY_STATUS`
Controls the visibility of your YouTube live stream:
- `"private"` - Only you can view (requires YouTube account login)
- `"public"` - Anyone can find and view the stream
- `"unlisted"` - Anyone with the link can view, but it won't appear in search results

**Recommendation:**
- Use `"unlisted"` for lab monitoring. This provides controlled access while keeping streams discoverable by your team.
- If you use `"private"`, you must provide access by adding a Google account for each person.
- Each person added to the channel will be able to see all videos in the channel.
- With `"unlisted"`, you can share specific playlists or videos individually.

#### Camera Orientation Settings
- `CAMERA_VFLIP` - Set to `True` to flip the camera image vertically
- `CAMERA_HFLIP` - Set to `True` to flip the camera image horizontally

Adjust these based on your camera mounting orientation to ensure the video appears right-side-up.

### Related Resources
- [streamingLambda Repository](https://github.com/AccelerationConsortium/streamingLambda) - AWS Lambda service for YouTube streaming
- [Issue #290](https://github.com/AccelerationConsortium/ac-dev-lab/issues/290) - Workflow name uniqueness requirements
- [YouTube Hardware Streams](https://www.youtube.com/@ac-hardware-streams) - Example of equipment monitoring streams



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

Copy the following code into the file (right click to paste), save it via `Ctrl+O` and `Enter` and exit via `Ctrl+X`. This assumes that your username is `ac`.

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
# Restart at 5 am, 1 pm, and 9 pm, local time (set up during flashing, or specified manually via e.g., `sudo timedatectl set-timezone America/New_York`)
0 5,13,21 * * * /sbin/shutdown -r now
```

Manually start the service by running:

```bash
sudo systemctl start device.service
```

*Note: This is the end of the picam setup. On reboot, a livestream should automatically start.*

---

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

## Troubleshooting

If you get the error:

> Codec AVOption preset (Encoding preset) has not been used for any stream. The most likely reason is either wrong type (e.g. a video option with no video streams) or that it is a private option of some decoder which was not actually used for any stream.`

then follow these steps:

1. Run `rpicam-hello` (Trixie) or `libcamera-hello` (Bookworm) to check if the camera is detected and working.
2. Verify that the physical connections are correct according to the hardware setup instructions above.
3. Try swapping out the camera with a new one to help with debugging.
4. If the issue persists, try swapping out the Pi Zero 2W with a new one.
Related issue(s):
- https://github.com/AccelerationConsortium/ac-training-lab/issues/11
- https://github.com/AccelerationConsortium/ac-training-lab/issues/161
- https://github.com/AccelerationConsortium/ac-training-lab/issues/80


<!-- While a virtual environment on RPi OS Lite will give you pip, this does not come preinstalled on the built-in Python on RPi OS Lite. To install pip, run:
```bash
sudo apt install python3-pip -y
```
> NOTE: The `-y` flag is used to automatically answer "yes" to any installation prompts. -->
