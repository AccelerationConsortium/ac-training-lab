# A1 Mini Overhead Toolhead Camera

This is intended to be run on a Raspberry Pi Zero 2W with a Raspberry Pi Camera
Module 3.

Make a copy of `my_secrets_example.py` called `my_secrets.py` and
fill in the necessary information. Keep in mind this will store the credentials in plain-text format.

`picamera2` via `sudo apt install python3-picamera2 --no-install-recommends` if not already installed (not pre-installed on RPi OS Lite). See https://github.com/raspberrypi/picamera2.

`libcamera` via `sudo apt install -y python3-libcamera` if not already installed, but probably handled already by `picamera2` installation. Also not preinstalled on RPi OS Lite versions.

```bash
cd ac-training-lab/src/ac_training_lab/A1-cam
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For local development with a dummy version of picamera2 (very minimal mock package), while in the same folder as this README file, additionally run:

```bash
pip install -e ./dummy_pkg/
```