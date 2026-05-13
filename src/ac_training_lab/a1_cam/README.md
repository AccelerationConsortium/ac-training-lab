# A1 Mini Overhead Toolhead Camera

This is intended to be run on a Raspberry Pi Zero 2W Raspberry Pi Camera
Module 3 running RPi OS Lite (bookworm).

```{include} ../../docs/_snippets/network-setup-note.md
```

## Architecture Overview

The A1 Mini camera system uses a hybrid approach for image transfer:

1. **MQTT** - Used to send capture commands to the device and receive image URIs back
2. **AWS S3** - Used to store the actual image files (avoids MQTT payload size limitations)

This architecture follows the recommendations from [ac-microcourses data logging tutorial](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.5-data-logging.html#additional-resources) which suggests uploading files to cloud storage and storing URIs in your database rather than embedding large binary data.

## AWS S3 Setup

### 1. Create an AWS Account

If you don't have an AWS account, create one at [aws.amazon.com](https://aws.amazon.com/). AWS offers a free tier that includes 5 GB of S3 storage for 12 months.

### 2. Create an S3 Bucket

Follow the official AWS documentation to create an S3 bucket:
- [Creating a bucket (AWS Console)](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html)
- [Tutorial: Creating your first S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html)

**Recommended bucket configuration settings** (based on [Issue #159](https://github.com/AccelerationConsortium/ac-dev-lab/issues/159#issuecomment-2725422824)):

![S3 Bucket Settings](https://github.com/user-attachments/assets/f155f371-9c1c-4702-9530-89615026da80)

Key considerations:
- **Region**: Choose a region close to your devices for lower latency (e.g., `us-east-2`)
- **Bucket name**: Must be globally unique (e.g., `rpi-zero2w-toolhead-camera`)
- **Object Ownership**: ACLs disabled (recommended)
- **Block Public Access settings**:
  - For enhanced security, keep "Block all public access" enabled (recommended)
  - If you need to access images from external systems, use IAM-based access controls or generate signed URLs rather than making the bucket public
  - Only uncheck public access if you fully understand the security implications and need publicly accessible URLs (as shown in the screenshot)

![S3 Public Access Settings](https://github.com/user-attachments/assets/fb694a7f-4dc0-4baf-a603-01bfa74d3165)

- **Bucket Versioning**: Can be left disabled by default. Enable if you want to keep multiple versions of files (less applicable when uploading timestamped images as this camera does)
- **Default encryption**: Enable Server-side encryption with Amazon S3 managed keys (SSE-S3)

**Optional: Enable Public Read Access**

> **⚠️ Security Warning**: Enabling public read access means anyone with knowledge of your object URLs can download images from your bucket. This may lead to unintended data exposure and unexpected AWS data transfer charges. Only enable this if you specifically need publicly accessible URLs and understand these implications.

If you unchecked "Block all public access" and want to allow public read access to images (useful for accessing images directly via URL without authentication), add the following bucket policy:

1. Go to your bucket → **Permissions** tab → **Bucket policy**
2. Click **Edit** and paste the following policy (replace `your-bucket-name` with your actual bucket name):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicRead",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

3. Click **Save changes**

This policy allows anyone to read (download) objects from your bucket via their public URLs. The IAM user credentials are still required for uploading and deleting objects. **Note**: Anyone who knows or guesses your object URLs can access them without authentication.

### 3. Create IAM Credentials

Create AWS IAM credentials with S3 access permissions. Follow the official guide:
- [Creating an IAM user in your AWS account](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html)
- [Managing access keys for IAM users](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)

**Detailed step-by-step instructions**:

1. **Navigate to IAM**:
   - In the AWS Console, search for "IAM" in the top search bar or go to the Services menu → Security, Identity, & Compliance → IAM

2. **Create a new user**:
   - In the left sidebar, click **Users**
   - Click the **Create user** button (orange button in top right)
   - Enter a user name (e.g., `a1-cam-user`)
   - Click **Next**

3. **Set permissions**:
   - Select **Attach policies directly**
   - **Do not** select any AWS managed policies (we'll add a custom policy next)
   - Click **Next**
   - Review and click **Create user**

4. **Add custom inline policy**:
   - After creating the user, click on the user name to open the user details
   - Click on the **Add permissions** dropdown → **Create inline policy**
   - Click on the **JSON** tab
   - Replace the default policy with the following (based on [Issue #159](https://github.com/AccelerationConsortium/ac-dev-lab/issues/159#issuecomment-2725490350)):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ListObjectsInBucket",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name"
            ]
        },
        {
            "Sid": "AllObjectActions",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

   - Replace `your-bucket-name` with your actual bucket name (e.g., `rpi-zero2w-toolhead-camera`)
   - Click **Next**
   - Enter a policy name (e.g., `a1-cam-s3-access`)
   - Click **Create policy**

5. **Create access keys**:
   - Still on the user details page, click the **Security credentials** tab
   - Scroll down to **Access keys** section
   - Click **Create access key**
   - Select **Application running outside AWS** as the use case
   - Click **Next**
   - (Optional) Add a description tag (e.g., "A1 Mini Camera Raspberry Pi")
   - Click **Create access key**
   - **IMPORTANT**: You'll see your `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` displayed
   - Click **Download .csv file** or copy both values immediately - they will only be shown once!
   - Save these credentials securely in a password manager
   - Click **Done**

**Security best practices**:
- Revoke credentials immediately if compromised
- Never commit credentials to version control

The a1_cam device generates URLs like:
```
https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}
```

If you need to configure additional bucket policies, see:
- [Using bucket policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-policies.html)
- [Bucket policy examples](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-bucket-policies.html)

## boto3 Setup

The device uses [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html), the AWS SDK for Python, to upload images to S3.

### Installation

boto3 is included in the device `requirements.txt` and will be installed when you follow the dependency installation instructions below.

### Configuration

The device code explicitly passes AWS credentials to boto3 from the `my_secrets.py` file. This approach keeps all credentials in one place and avoids the need to configure `~/.aws/credentials` on the Raspberry Pi.

Add the following to your `my_secrets.py` file (see Secrets section below for creating this file):

```python
AWS_ACCESS_KEY_ID = "your-aws-access-key-id"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-access-key"
AWS_REGION = "us-east-2"  # or your chosen region
BUCKET_NAME = "rpi-zero2w-toolhead-camera"  # or your bucket name
IMAGE_QUALITY = 85  # JPEG quality (1-100). Lower = smaller file size. 85 gives ~2-3 MB images
```

**Image quality settings**:
- `IMAGE_QUALITY` controls JPEG compression (1-100 scale)
- Default of 85 produces ~2-3 MB images (down from ~35 MB at quality 90)
- Lower values reduce file size but may decrease image clarity
- Recommended range: 75-90 depending on your needs

The device.py code passes these credentials directly to boto3.client():
```python
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
```

**Security considerations**:
- The `my_secrets.py` file stores credentials in plaintext. Ensure proper file permissions: `chmod 600 my_secrets.py`
- Keep your Raspberry Pi login credentials secure and use SSH key authentication
- Consider restricting SSH access and using fail2ban or similar tools
- While boto3 also supports reading credentials from `~/.aws/credentials` or environment variables, this implementation explicitly passes them to keep all device secrets centralized in `my_secrets.py`

### Additional Resources

- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [boto3 S3 Guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3.html)
- [boto3 S3 Examples](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-examples.html)

## MQTT Setup

The A1 Mini camera uses MQTT for hardware-software communication. For comprehensive MQTT setup instructions, refer to the AC Microcourses documentation:

- [Hardware-Software Communication](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.4-hardware-software-communication.html)
- [Onboard LED & Temperature Tutorial](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.4.1-onboard-led-temp.html)

### MQTT Credentials

The device requires MQTT connection details in the `my_secrets.py` file (see Secrets section below for setup):

- `MQTT_HOST` - Your MQTT broker host (e.g., HiveMQ Cloud)
- `MQTT_PORT` - Usually 8883 for TLS-encrypted connections
- `MQTT_USERNAME` - Your MQTT username
- `MQTT_PASSWORD` - Your MQTT password
- `DEVICE_SERIAL` - A unique identifier for this camera device
- `CAMERA_READ_TOPIC` - Topic for receiving capture commands (e.g., `rpi-zero2w/still-camera/request/{DEVICE_SERIAL}`)
- `CAMERA_WRITE_TOPIC` - Topic for publishing image URIs (e.g., `rpi-zero2w/still-camera/response/{DEVICE_SERIAL}`)

### MQTT Library

The device uses [paho-mqtt](https://pypi.org/project/paho-mqtt/), the standard Python MQTT client library. It's included in the device `requirements.txt`.

## Quick Setup (Automated)

For a streamlined setup process, use the provided `setup.sh` script:

```bash
bash setup.sh
```

This script automates all the steps described in the sections below. **Note**: If this script and README diverge, README is authoritative. See the [Codebase](#codebase), [Secrets](#secrets), and [Dependencies](#dependencies) sections for manual step-by-step instructions.

## Codebase

Update the system package list via:
```bash
sudo apt update
```

Optionally, upgrade the upgrade-able packages to the latest versions (`-y` flag is used to automatically answer "yes" to any installation prompts):
```
sudo apt upgrade -y
```

Ensure that `git` is installed:
```bash
sudo apt-get install git -y
```

Clone the repository to your Raspberry Pi Zero 2W device via HTTPS (allows for `git pull` to work without needing to enter credentials each time):

```bash
git clone https://github.com/AccelerationConsortium/ac-dev-lab.git
```

Navigate to the same directory as this README file:

```bash
cd /home/ac/ac-dev-lab/src/ac_training_lab/a1_cam/
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

While one could use the built-in Python installation (this device is intended to be run via a single top-level script, the RPi device (in our case RPi Zero 2W) requires minimal setup (i.e., can easily be reflashed), and the RPi device is intended for a single purpose with a single set of requirements (i.e., a "point-and-shoot" camera)), the extra steps involved to make this work are as equally onerous as using a venv [[context](https://github.com/AccelerationConsortium/ac-dev-lab/pull/178#issuecomment-2730490626)], hence we only include instructions assuming a venv.

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

### Testing the Camera

To verify the camera is working, you have two options:

**Option 1: Jupyter Notebook (Recommended)**

Use the provided `test_camera.ipynb` notebook to interactively test the camera:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AccelerationConsortium/ac-dev-lab/blob/main/src/ac_training_lab/a1_cam/test_camera.ipynb)

The notebook allows you to:
- Configure your MQTT credentials
- Send a capture command
- Download and display the captured image

**Option 2: Python Script**

Run `_scripts/client.py` locally (e.g., on your PC), ensuring you have the same credentials in a `my_secrets.py` located in the `_scripts` directory as you do on the RPi. This script will request the latest image from the device and save it to your local machine.

## Workflow Example

Here's how the complete image capture workflow operates:

1. **Setup**: Configure AWS S3 bucket and credentials, set up MQTT broker
2. **Image capture request**: Orchestrator sends `{"command": "capture_image"}` via MQTT to `CAMERA_READ_TOPIC`
3. **Device captures**: Raspberry Pi takes a photo using the camera
4. **Upload to S3**: Device uploads image to S3 bucket using boto3
5. **Respond with URI**: Device publishes S3 URI back to orchestrator via MQTT on `CAMERA_WRITE_TOPIC`
6. **Access image**: Orchestrator can download image from S3 or store URI in database

For implementation details, see [Issue #159](https://github.com/AccelerationConsortium/ac-dev-lab/issues/159).

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
WorkingDirectory=/home/ac/ac-dev-lab/src/ac_training_lab/a1_cam
# Best to specify the full path to the Python interpreter or use ExecSearchPath
ExecStart=/home/ac/ac-dev-lab/src/ac_training_lab/a1_cam/venv/bin/python3 device.py
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

You can manually start the service by running:

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



<!-- While a virtual environment on RPi OS Lite will give you pip, this does not come preinstalled on the built-in Python on RPi OS Lite. To install pip, run:
```bash
sudo apt install python3-pip -y
```
> NOTE: The `-y` flag is used to automatically answer "yes" to any installation prompts. -->
