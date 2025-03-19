# A1 Mini Overhead Toolhead Camera

This is intended to be run on a Raspberry Pi Zero 2W with a Raspberry Pi Camera
Module 3.

## Secrets

Make a copy of `my_secrets_example.py` called `my_secrets.py` and
fill in the necessary information. Keep in mind this will store the credentials in plain-text format.

## Dependencies

If not already installed (not pre-installed on RPi OS Lite), install [`picamera2`](https://github.com/raspberrypi/picamera2) via:

```bash
sudo apt install python3-picamera2 --no-install-recommends
```

`libcamera` should be automatically installed after installing `picamera2`. Otherwise, one would use `sudo apt install -y python3-libcamera` (`libcamera` also does not come preinstalled on RPi OS Lite versions).

Optionally, you can use a virtual environment, but you will need to create it with the `--system-site-packages` flag via e.g., `python3 -m venv --system-site-packages venv` (installs to folder called "venv") followed by `source venv/bin/activate` so that it can use the `picamera2` and `libcamera` libraries. We are OK with *not* using a virtual environment because this device is intended to be run via a single top-level script, the RPi device (in our case RPi Zero 2W) requires minimal setup (i.e., can easily be reflashed), and the RPi device is intended for a single purpose with a single set of requirements (i.e., a "point-and-shoot" camera) [[context](https://github.com/AccelerationConsortium/ac-training-lab/pull/178#issuecomment-2730490626)].

While a virtual environment on RPi OS Lite will give you pip, this does not come preinstalled on the built-in Python on RPi OS Lite. To install pip, run:
```bash
sudo apt install python3-pip -y
```
> NOTE: The `-y` flag is used to automatically answer "yes" to any installation prompts.

While in the same folder as this README file (e.g., `cd ac-training-lab/src/ac_training_lab/a1_cam`), run:

```bash
pip install -r requirements.txt
```

## Non-RPi OS Development

For local development with a dummy version of picamera2 (very minimal mock package), while in the same folder as this README file, additionally run:

```bash
pip install -e ./dummy_pkg/ # WARNING: do not install this on the Raspberry Pi for the toolhead camera -- the imports will overlap with the "real" system packages `picamera2` and `libcamera`.
```

## Running the Device

To start the device manually, run:

```bash
python3 device.py
```