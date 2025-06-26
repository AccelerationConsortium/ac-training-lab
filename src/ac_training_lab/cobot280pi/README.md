# MyCobot 280 Pi

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AccelerationConsortium/ac-training-lab/blob/cobot-usage-docs/src/ac_training_lab/cobot280pi/gradio-client-demo.ipynb)

The general structure of the program is as follows;
- The cobot runs a python server which listens for commands from HiveMQ, and runs the appropriate Python API functions from [pymycobot](https://github.com/elephantrobotics/pymycobot/blob/main/docs/MyCobot_280_en.md).
- HuggingFace Spaces and the HuggingFace Python API (used in the Colab demo above) connect to HiveMQ and send commands to the appropriate topics, which the server is listening on.
- If you own a Cobot, you can follow the instructions below to set it up. Once completed, you also have the option of using the `CobotController` class as defined in `client.py`.

## Setup guide (if you own a cobot)
1. Power on the Cobot280 Pi and connect the micro HDMI cable to a monitor.
2. Connect the Cobot280 Pi to Wifi by clicking on the Wifi icon in the top right corner of the screen.
3. Open a terminal and type to the following command to upgrade system packages
```
sudo apt-get update && sudo apt-get upgrade -y
```
4. Install the required system dependencies with the following command
```
sudo apt-get install git
```
5. Clone the repository containing the code for the server run by the Cobot.
```
git clone https://github.com/AccelerationConsortium/ac-training-lab.git
```
7. Since we only need the files in the `ac-training-lab/src/ac_training_lab/cobot280pi/` directory, we move them out and delete the rest of the repository.
```
mv ac-training-lab/src/ac_training_lab/cobot280pi ./
rm -rf ./ac-training-lab
cd ./cobot280pi
```
8. Install the required python packages for running the server.
```
pip install -r requirements.txt
```
9. Create an account on [HiveMQ](https://www.hivemq.com/). Once you do, create a free serverless cluster. In the Overview > Connection details section, take note of the **URL** and **Port** parameters.
10. Then, in the Access Management section, create new credentials. Choose a **Username** and **Password** and take note of these parameters too. For the Permission dropdown, select **Publish and Subscribe**, and then Save your new credentials.
11. Create a file in the `ac-training-lab/src/ac_training_lab/cobot280pi/` directory named `my_secrets.py`. Paste the following contents into the file. Replace the <...> attributes with your own values as noted above. Make sure to keep these credentials secret!
```
HIVEMQ_USERNAME = "<HiveMQ credential username>"
HIVEMQ_PASSWORD = "<HiveMQ credential password>"
HIVEMQ_HOST = "<host URL from HiveMQ>"
DEVICE_PORT = <port from HiveMQ>
DEVICE_ENDPOINT = "cobot280pi/cobot1"
```
12. Run the server with the following command.
```
python device.py
```
13. Your server is now running! You can use the `CobotController` class from the `client.py` file to control your cobot. Initialize it with the same parameters as in your `my_secrets.py` file.
