import json
import time
from datetime import datetime, timedelta

import lookhere
import paho.mqtt.client as mqtt
import requests

"""
This script is used to interact with the PioReactor API to perform various
operations such as creating experiments, assigning workers to experiments,
starting/stopping stirring, setting LED intensity, etc.

lookhere.py contains the following variables:
- username: Username for the PioReactor
- password: Password for the PioReactor
- broker: MQTT broker address
- port: MQTT broker port
- username_pio: Username for the PioReactor
- password_pio: Password for the PioReactor
- port_pio: Port for the PioReactor
It should be placed in the same directory as this script.

Author: Enrui (Edison) Lin
"""


# This should reflect the domain_alias in the PioReactor Configuration
HTTP = "http://piobio.local/api"

automation_name = None
stirring_target_rpm = None
led_data = None


# --- PioReactor API Functions ---
def create_experiment(experiment, description="", mediaUsed="", organismUsed=""):
    url = f"{HTTP}/experiments"
    created_at = datetime.now().isoformat()

    payload = {
        "experiment": experiment,
        "created_at": created_at,
        "description": description,
        "mediaUsed": mediaUsed,
        "organismUsed": organismUsed,
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("Experiment created successfully!")
        return response.json()
    else:
        print(f"Failed to create experiment. Status code: {response.status_code}")
        return None


def assign_worker_to_experiment(worker, experiment):
    url = f"{HTTP}/experiments/{experiment}/workers"
    payload = {"pioreactor_unit": worker}
    headers = {"Content-Type": "application/json"}

    response = requests.put(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print(f"Worker {worker} assigned to experiment {experiment}.")
    else:
        print(f"Failed to assign worker {worker}. Status code: {response.status_code}")


def remove_worker_from_experiment(worker, experiment):
    url = f"{HTTP}/experiments/{experiment}/workers/{worker}"
    headers = {"Content-Type": "application/json"}

    response = requests.delete(url, headers=headers)
    if response.status_code == 202:
        print(f"Worker {worker} removed from experiment {experiment}.")
    else:
        print(f"Failed to remove worker {worker}. Status code: {response.status_code}")


def start_stirring(worker, experiment):
    url = f"{HTTP}/workers/{worker}/jobs/run/job_name/stirring/experiments/{experiment}"
    print(url)
    headers = {"Content-Type": "application/json"}
    payload = {"env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"Stirring started for worker {worker}")
    else:
        print(f"Failed to start stirring. Status code: {response.status_code}")


def stop_stirring(worker, experiment):
    url = f"{HTTP}/workers/{worker}/jobs/update/"
    f"job_name/stirring/experiments/{experiment}"
    headers = {"Content-Type": "application/json"}
    payload = {"settings": {"$state": "disconnected"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"Stirring stopped for worker {worker}.")
    else:
        print(f"Failed to stop stirring. Status code: {response.status_code}")


def update_stirring_rpm(worker, experiment, rpm):
    url = f"{HTTP}/workers/{worker}/jobs/update/"
    f"job_name/stirring/experiments/{experiment}"
    headers = {"Content-Type": "application/json"}
    payload = {"settings": {"target_rpm": rpm}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"Stirring RPM updated to {rpm} for worker {worker}.")
    else:
        print(f"Failed to update stirring RPM. Status code: {response.status_code}")


def set_led_intensity(worker, experiment, brightness_value, led):
    url = (
        f"{HTTP}/workers/{worker}/jobs/run/job_name/"
        f"led_intensity/experiments/{experiment}"
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
        "options": {led: brightness_value, "source_of_event": "UI"},
    }

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"LED intensity set to {brightness_value} for worker {worker}.")
    else:
        print(f"Failed to set LED intensity. Status code: {response.status_code}")


def get_temperature_readings(client, reactor, experiment, filter_mod, lookback):
    url = f"{HTTP}/experiments/{experiment}/time_series/temperature_readings"
    params = {"filter_mod_N": filter_mod, "lookback": lookback}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        print(f"Temperature readings retrieved for experiment {experiment}.")
        print(response.json())
        temperature_data = response.json()
        client.publish(
            f"pioreactor/{reactor}/temperature", json.dumps(temperature_data)
        )
    else:
        print(f"Failed to retrieve temp readings. Status code: {response.status_code}")


def get_experiments(client):
    url = f"{HTTP}/experiments"
    headers = {"Content-Type": "application/json"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        experiments = response.json()
        client.publish("pioreactor/experiments", json.dumps(experiments))
    else:
        print(f"Failed to retrieve experiments. Status code: {response.status_code}")


def get_reactors(client, experiment):
    url = f"{HTTP}/experiments/{experiment}/workers"
    headers = {"Content-Type": "application/json"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        reactors = response.json()
        client.publish("pioreactor/reactors", json.dumps(reactors))
    else:
        print(f"Failed to retrieve reactors. Status code: {response.status_code}")


def get_reactor_stats(client, reactor):
    url = f"{HTTP}/units/{reactor}/jobs/running"
    headers = {"Content-Type": "application/json"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        stats = response.json()
        client.publish("pioreactor/stats", json.dumps(stats))
    else:
        print(f"Failed to retrieve reactor stats. Status code: {response.status_code}")


def get_task_status(task_id):
    # Construct the URL for getting the task status
    url = f"{HTTP}://pioreactor.local/unit_api/task_results/{task_id}"

    # Set the headers
    headers = {"Content-Type": "application/json"}

    # Send the GET request to retrieve the task status
    response = requests.get(url, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        print("Task status retrieved successfully.")
        return response.json()  # Return the response data (task status)
    else:
        print(f"Failed to retrieve task status. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def get_worker(client, reactor):
    # Construct the URL for getting the worker
    url = f"{HTTP}/workers/assignments"

    # Set the headers
    headers = {"Content-Type": "application/json"}

    # Send the GET request to retrieve the worker
    response = requests.get(url, headers=headers)

    # print(response.text)

    if response.status_code == 200:
        print("Worker retrieved successfully.")
    else:
        print(f"Failed to retrieve worker. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

    data = response.json()

    experiment = None

    for e in data:
        if e["pioreactor_unit"] == reactor:
            experiment = e["experiment"]
            break

    if experiment is None:
        print(f"Failed to retrieve experiment for worker {reactor}")
        return None

    url2 = f"{HTTP}/units/{reactor}/jobs/running"

    response2 = requests.get(url2, headers=headers)

    stats = response2.json()

    # print(stats)

    # task = stats.get("task_id", None)

    # if task is None:
    #     return None

    # response3 = get_task_status(task)

    # print(response3)

    running = []

    print(stats)

    for item in stats:
        running.append(item["job_name"])

    url3 = f"{HTTP}/experiments"

    response3 = requests.get(url3, headers=headers)

    experiments = response3.json()

    exp_name = []

    for e in experiments:
        exp_name.append(e["experiment"])

    exp_name.remove(experiment)

    def on_connect(client, userdata, flags, rc):
        print(f"PIO connected with result code {rc}")
        client.subscribe(f"pioreactor/{reactor}/{experiment}/leds/intensity")

    def on_message(client, userdata, msg):
        global led_data
        led_data = json.loads(msg.payload.decode("utf-8"))
        # print(led_data)

    client_temp = mqtt.Client()

    client_temp.on_connect = on_connect
    client_temp.on_message = on_message

    client_temp.username_pw_set(lookhere.username_pio, lookhere.password_pio)

    client_temp.connect(reactor + ".local", lookhere.port_pio)

    client_temp.loop_start()

    # timeout = 5
    # start = time.time()

    # while len(led_data) < 5 and time.time() - start < timeout:
    #     time.sleep(1)

    time.sleep(1)

    client_temp.loop_stop()
    client_temp.disconnect()

    if "temperature_automation" in running:

        def on_connect(client, userdata, flags, rc):
            print(f"PIO connected with result code {rc}")
            client.subscribe(
                f"pioreactor/{reactor}/{experiment}/temperature_automation"
                "/automation_name"
            )

        def on_message(client, userdata, msg):
            global automation_name
            automation_name = msg.payload.decode("utf-8")
            print(automation_name)

        client_temp.on_connect = on_connect
        client_temp.on_message = on_message

        broker = reactor + ".local"

        client_temp.connect(broker, lookhere.port_pio)

        global automation_name
        client_temp.loop_start()
        time.sleep(1)
        # print(automation_name, "automation_name")
        client_temp.loop_stop()
        client_temp.disconnect()

    if "stirring" in running:

        def on_connect(client, userdata, flags, rc):
            print(f"PIO connected with result code {rc}")
            client.subscribe(f"pioreactor/{reactor}/{experiment}/stirring/target_rpm")

        def on_message(client, userdata, msg):
            global stirring_target_rpm
            stirring_target_rpm = msg.payload.decode("utf-8")
            print(stirring_target_rpm)

        client_temp.on_connect = on_connect
        client_temp.on_message = on_message

        broker = reactor + ".local"

        client_temp.connect(broker, lookhere.port_pio)

        global stirring_target_rpm
        client_temp.loop_start()
        time.sleep(1)
        # print(stirring_target_rpm, "stirring_target_rpm")
        # print(type(stirring_target_rpm))
        client_temp.loop_stop()
        client_temp.disconnect()

    print(running)

    # running.remove("watchdog")
    # running.remove("mqtt_to_db_streaming")
    running.remove("monitor")

    # print(experiment)

    payload = {
        "experiment": experiment,
        "running": running,
        "temperature_automation": automation_name,
        "stirring": (
            int(float(stirring_target_rpm)) if stirring_target_rpm is not None else None
        ),
        "leds": led_data if led_data is not None else None,
        "experiments": exp_name,
    }

    # print("Publishing worker")
    client.publish(f"pioreactor/{reactor}/worker", json.dumps(payload))


def set_temperature_automation(worker, experiment, automation_name, temp=None):
    # Construct the URL for the request
    url = (
        f"{HTTP}/workers/{worker}/jobs/run/job_name/temperature_automation/"
        f"experiments/{experiment}"
    )

    # Prepare the payload
    if automation_name == "only_record_temperature":
        payload = {
            "args": [],
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {
                "automation_name": automation_name  # Set the desired automation name
            },
        }
    elif automation_name == "thermostat":
        payload = {
            "args": [],
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {
                "automation_name": automation_name,  # Set the desired automation name
                "skip_first_run": 0,
                "target_temperature": temp,
            },
        }
    else:
        print(f"Invalid automation name: {automation_name}")
        return

    # Set the headers
    headers = {"Content-Type": "application/json"}

    # Send the PATCH request to set the automation
    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    # Check the response status code
    if response.status_code == 202:
        print(
            f"Automation '{automation_name}' set successfully on worker {worker}"
            f" for experiment {experiment}!"
        )
    else:
        print(f"Failed to set automation. Status code: {response.status_code}")
        print(f"Response: {response.text}")


def temp_update(worker, experiment, settings):
    # Construct the URL for the request
    url = (
        f"{HTTP}/workers/{worker}/jobs/update/job_name/temperature_automation/"
        f"experiments/{experiment}"
    )

    # Prepare the payload
    payload = {"settings": settings}

    # Set the headers
    headers = {"Content-Type": "application/json"}

    # Send the PATCH request to set the automation
    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    # Check the response status code
    if response.status_code == 202:
        print(
            f"Automation settings updated successfully on worker {worker} for "
            f"experiment {experiment}!"
        )
    else:
        print(
            f"Failed to update automation settings. Status code: {response.status_code}"
        )
        print(f"Response: {response.text}")


def temp_restart(worker, experiment, automation, temp=None):
    # Update automation to stop then start new automation
    print("Restarting temperature automation")
    temp_update(worker, experiment, {"$state": "disconnected"})
    time.sleep(3)
    set_temperature_automation(worker, experiment, automation, temp)


def stop_od_reading(reactor, experiment):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/update/job_name/od_reading/"
        f"experiments/{experiment}"
    )
    headers = {"Content-Type": "application/json"}
    payload = {"settings": {"$state": "disconnected"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"OD reading stopped for worker {reactor}.")
    else:
        print(f"Failed to stop OD reading. Status code: {response.status_code}")


def start_od_reading(reactor, experiment):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/run/job_name/"
        f"od_reading/experiments/{experiment}"
    )
    headers = {"Content-Type": "application/json"}
    payload = {"env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"OD reading started for worker {reactor}")
    else:
        print(f"Failed to start OD reading. Status code: {response.status_code}")


def stop_growth_rate(reactor, experiment):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/update/job_name/"
        f"growth_rate_calculating/experiments/{experiment}"
    )
    headers = {"Content-Type": "application/json"}
    payload = {"settings": {"$state": "disconnected"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"Growth rate stopped for worker {reactor}.")
    else:
        print(f"Failed to stop growth rate. Status code: {response.status_code}")


def start_growth_rate(reactor, experiment):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/run/job_name/growth_rate_calculating/"
        f"experiments/{experiment}"
    )
    headers = {"Content-Type": "application/json"}
    payload = {"env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"Growth rate started for worker {reactor}")
    else:
        print(f"Failed to start growth rate. Status code: {response.status_code}")


def get_readings(
    client,
    reactor,
    experiment,
    filter_mod,
    lookback,
    filter_mod2,
    lookback2,
    filter_mod3,
    lookback3,
    filter_mod4,
    lookback4,
    amount,
    amount2,
    amount3,
    amount4,
):
    # Get the experiment details
    url = f"{HTTP}/experiments/{experiment}"
    headers = {"Content-Type": "application/json"}

    response = requests.get(url, headers=headers)

    # print(response.json())

    hour = response.json().get("delta_hours", None)

    filter_mod2 = filter_mod2 + hour
    filter_mod3 = filter_mod3 + hour
    filter_mod4 = filter_mod4 + hour

    # print(amount2)

    # Get the temperature readings
    url = f"{HTTP}/experiments/{experiment}/time_series/temperature_readings"
    params = {"filter_mod_N": filter_mod, "lookback": lookback}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        print(f"Temperature readings retrieved for experiment {experiment}.")
    else:
        print(
            "Failed to retrieve temperature readings. "
            f"Status code: {response.status_code}"
        )

    # Get the OD readings
    url = f"{HTTP}/experiments/{experiment}/time_series/od_readings"
    params = {"filter_mod_N": filter_mod2, "lookback": lookback2}

    response2 = requests.get(url, params=params)
    if response2.status_code == 200:
        print(f"OD readings retrieved for experiment {experiment}.")
    else:
        print(f"Failed to retrieve OD readings. Status code: {response2.status_code}")

    # Get the noremalized OD readings
    url = f"{HTTP}/experiments/{experiment}/time_series/od_readings_filtered"
    params = {"filter_mod_N": filter_mod3, "lookback": lookback3}

    response3 = requests.get(url, params=params)
    if response3.status_code == 200:
        print(f"Normalized OD readings retrieved for experiment {experiment}.")
    else:
        print(
            "Failed to retrieve normalized OD readings. "
            f"Status code: {response3.status_code}"
        )

    # Get the growth rate readings
    url = f"{HTTP}/experiments/{experiment}/time_series/growth_rates"
    params = {"filter_mod_N": filter_mod4, "lookback": lookback4}

    response4 = requests.get(url, params=params)
    if response4.status_code == 200:
        print(f"Growth rate readings retrieved for experiment {experiment}.")
    else:
        print(
            "Failed to retrieve growth rate readings. "
            f"Status code: {response4.status_code}"
        )

    # Publish the readings to the MQTT topic
    # Readings are 4 minutes apart
    temp = response.json()
    temp = temp.get("data", [])

    if len(temp) != 0:
        temp = temp[0]
        if amount == "1 hour":
            lastTime = datetime.now()
            # lastTime = datetime.strptime(lastTime, "%Y-%m-%dT%H:%M:%S.%fZ")
            for i in range(len(temp), 0, -1):
                if datetime.strptime(
                    temp[i - 1].get("x"), "%Y-%m-%dT%H:%M:%S.%fZ"
                ) < lastTime - timedelta(hours=1):
                    temp = temp[i:]
                    break
        elif amount == "24 hours":
            lastTime = datetime.now()
            # lastTime = datetime.strptime(lastTime, "%Y-%m-%dT%H:%M:%S.%fZ")
            for i in range(len(temp), 0, -1):
                if datetime.strptime(
                    temp[i - 1].get("x"), "%Y-%m-%dT%H:%M:%S.%fZ"
                ) < lastTime - timedelta(hours=24):
                    temp = temp[i:]
                    break

    # Readings are 12 times a minute

    od = response2.json()
    od = od.get("data", [])

    if len(od) != 0:
        od = od[0]
        if amount2 == "1 hour":
            lastTime = datetime.now()
            # lastTime = datetime.strptime(lastTime, "%Y-%m-%dT%H:%M:%S.%fZ")
            for i in range(len(od), 0, -1):
                if datetime.strptime(
                    od[i - 1].get("x"), "%Y-%m-%dT%H:%M:%S.%fZ"
                ) < lastTime - timedelta(hours=1):
                    od = od[i:]
                    break
        elif amount2 == "24 hours":
            lastTime = datetime.now()
            # lastTime = datetime.strptime(lastTime, "%Y-%m-%dT%H:%M:%S.%fZ")
            for i in range(len(od), 0, -1):
                if datetime.strptime(
                    od[i - 1].get("x"), "%Y-%m-%dT%H:%M:%S.%fZ"
                ) < lastTime - timedelta(hours=24):
                    od = od[i:]
                    break

    # print(lastTime)

    norm_od = response3.json()
    norm_od = norm_od.get("data", [])

    if len(norm_od) != 0:
        norm_od = norm_od[0]
        if amount3 == "1 hour":
            lastTime = datetime.now()
            # lastTime = datetime.strptime(lastTime, "%Y-%m-%dT%H:%M:%S.%fZ")
            for i in range(len(norm_od), 0, -1):
                if datetime.strptime(
                    norm_od[i - 1].get("x"), "%Y-%m-%dT%H:%M:%S.%fZ"
                ) < lastTime - timedelta(hours=1):
                    norm_od = norm_od[i:]
                    break
        elif amount3 == "24 hours":
            lastTime = datetime.now()
            # lastTime = datetime.strptime(lastTime, "%Y-%m-%dT%H:%M:%S.%fZ")
            for i in range(len(norm_od), 0, -1):
                if datetime.strptime(
                    norm_od[i - 1].get("x"), "%Y-%m-%dT%H:%M:%S.%fZ"
                ) < lastTime - timedelta(hours=24):
                    norm_od = norm_od[i:]
                    break

    growth_rate = response4.json()
    growth_rate = growth_rate.get("data", [])
    if len(growth_rate) != 0:
        growth_rate = growth_rate[0]
        if amount4 == "1 hour":
            lastTime = datetime.now()
            # lastTime = datetime.strptime(lastTime, "%Y-%m-%dT%H:%M:%S.%fZ")
            for i in range(len(growth_rate), 0, -1):
                if datetime.strptime(
                    growth_rate[i - 1].get("x"), "%Y-%m-%dT%H:%M:%S.%fZ"
                ) < lastTime - timedelta(hours=1):
                    growth_rate = growth_rate[i:]
                    break
        elif amount4 == "24 hours":
            lastTime = datetime.now()
            # lastTime = datetime.strptime(lastTime, "%Y-%m-%dT%H:%M:%S.%fZ")
            for i in range(len(growth_rate), 0, -1):
                if datetime.strptime(
                    growth_rate[i - 1].get("x"), "%Y-%m-%dT%H:%M:%S.%fZ"
                ) < lastTime - timedelta(hours=24):
                    growth_rate = growth_rate[i:]
                    break

    readings = {
        "temperature": temp,
        "od": od,
        "normalized_od": norm_od,
        "growth_rate": growth_rate,
    }

    # print(temp)

    # print(len(od))

    client.publish(f"pioreactor/{reactor}/readings", json.dumps(readings))


def new_experiment(experiment, description="", mediaUsed="", organismUsed=""):
    url = f"{HTTP}/experiments"
    created_at = datetime.now().isoformat()

    payload = {
        "experiment": experiment,
        "created_at": created_at,
        "description": description,
        "mediaUsed": mediaUsed,
        "organismUsed": organismUsed,
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("Experiment created successfully!")
    else:
        print(f"Failed to create experiment. Status code: {response.status_code}")


def change_experiment(experiment, experiment_new, reactor):
    url = f"{HTTP}/experiments/{experiment}/workers/{reactor}"

    headers = {"Content-Type": "application/json"}

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print("Experiment changed successfully!")
    else:
        print(f"Failed to change experiment. Status code: {response.status_code}")
        return None

    url = f"{HTTP}/experiments/{experiment_new}/workers"

    payload = {"pioreactor_unit": reactor}

    response = requests.put(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print(f"Worker {reactor} assigned to experiment {experiment_new}.")
    else:
        print(f"Failed to assign worker {reactor}. Status code: {response.status_code}")

    set_led_intensity(reactor, experiment_new, 0, "A")


def delete_experiment(experiment):
    url = f"{HTTP}/experiments/{experiment}"

    headers = {"Content-Type": "application/json"}

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print("Experiment deleted successfully!")
    else:
        print(f"Failed to delete experiment. Status code: {response.status_code}")
        return None


def pump_add_media(reactor, experiment, volume=None, duration=None, continuous=False):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/run/job_name/add_media/experiments/{experiment}"
    )

    if volume is not None:
        payload = {
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {"ml": volume, "source_of_event": "UI"},
        }
    elif duration is not None:
        payload = {
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {"duration": duration, "source_of_event": "UI"},
        }
    elif continuous:
        # return # Don't think we should support this
        payload = {
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {"continuously": None, "source_of_event": "UI"},
        }
    else:
        print("Please provide either volume or duration.")
        return

    headers = {"Content-Type": "application/json"}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 202:
        print(f"Media added to reactor {reactor}.")
    else:
        print(f"Failed to add media. Status code: {response.status_code}")


def pump_remove_media(
    reactor, experiment, volume=None, duration=None, continuous=False
):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/run/job_name/"
        f"remove_waste/experiments/{experiment}"
    )

    if volume is not None:
        payload = {
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {"ml": volume, "source_of_event": "UI"},
        }
    elif duration is not None:
        payload = {
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {"duration": duration, "source_of_event": "UI"},
        }
    elif continuous:
        # return # Don't think we should support this
        payload = {
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {"continuously": None, "source_of_event": "UI"},
        }
    else:
        print("Please provide either volume or duration.")
        return

    headers = {"Content-Type": "application/json"}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 202:
        print(f"Media removed from reactor {reactor}.")
    else:
        print(f"Failed to remove media. Status code: {response.status_code}")


def add_alt_media(reactor, experiment, volume=None, duration=None, continuous=False):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/run/job_name/"
        f"add_alt_media/experiments/{experiment}"
    )

    if volume is not None:
        payload = {
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {"ml": volume, "source_of_event": "UI"},
        }
    elif duration is not None:
        payload = {
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {"duration": duration, "source_of_event": "UI"},
        }
    elif continuous:
        # return # Don't think we should support this
        payload = {
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {"continuously": None, "source_of_event": "UI"},
        }
    else:
        print("Please provide either volume or duration.")
        return

    headers = {"Content-Type": "application/json"}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 202:
        print(f"Media added to reactor {reactor}.")
    else:
        print(f"Failed to add media. Status code: {response.status_code}")


def circulate_media(reactor, experiment, duration):
    pump_add_media(reactor, experiment, continuous=True)
    pump_remove_media(reactor, experiment, continuous=True)

    time.sleep(duration)

    url = (
        f"{HTTP}/workers/{reactor}/jobs/stop/job_name/"
        f"add_media/experiments/{experiment}"
    )
    headers = {"Content-Type": "application/json"}

    response = requests.patch(url, headers=headers)

    if response.status_code == 202:
        print(f"Media circulated in reactor {reactor}.")
    else:
        print(f"Failed to circulate media. Status code: {response.status_code}")

    url = (
        f"{HTTP}/workers/{reactor}/jobs/stop/job_name/"
        f"remove_waste/experiments/{experiment}"
    )

    response = requests.patch(url, headers=headers)

    if response.status_code == 202:
        print(f"Media circulated in reactor {reactor}.")
    else:
        print(f"Failed to circulate media. Status code: {response.status_code}")

    # url = f"{HTTP}/workers/{reactor}/jobs/run/job_name/" \
    # "circulate_media/experiments/{experiment}"

    # payload = {
    #     "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
    #     "options": {"duration": duration, "source_of_event": "UI"}
    # }

    # headers = {"Content-Type": "application/json"}

    # response = requests.patch(url, headers=headers, data=json.dumps(payload))

    # if response.status_code == 202:
    #     print(f"Media circulated in reactor {reactor}.")
    # else:
    #     print(f"Failed to circulate media. Status code: {response.status_code}")


def circulate_alt_media(reactor, experiment, media, duration):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/run/job_name/"
        f"circulate_alt_media/experiments/{experiment}"
    )

    payload = {
        "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
        "options": {"duration": duration, "source_of_event": "UI", "media": media},
    }

    headers = {"Content-Type": "application/json"}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 202:
        print(f"Media circulated in reactor {reactor}.")
    else:
        print(f"Failed to circulate media. Status code: {response.status_code}")


def start_relay(reactor, experiment, relay):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/run/job_name/" f"relay/experiments/{experiment}"
    )

    payload = {
        "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
        "options": {},
    }

    headers = {"Content-Type": "application/json"}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 202:
        print(f"Relay {relay} started in reactor {reactor}.")
    else:
        print(f"Failed to start relay. Status code: {response.status_code}")


def stop_relay(reactor, experiment, relay):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/update/job_name/"
        f"relay/experiments/{experiment}"
    )

    payload = {
        "settings": {"$state": "disconnected"},
    }

    headers = {"Content-Type": "application/json"}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 202:
        print(f"Relay {relay} stopped in reactor {reactor}.")
    else:
        print(f"Failed to stop relay. Status code: {response.status_code}")


def relay_on(reactor, experiment, relay):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/update/job_name/"
        f"relay/experiments/{experiment}"
    )

    payload = {"settings": {"is_relay_on": 1}}

    headers = {"Content-Type": "application/json"}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 202:
        print(f"Relay {relay} turned on in reactor {reactor}.")
    else:
        print(f"Failed to turn on relay. Status code: {response.status_code}")


def relay_off(reactor, experiment, relay):
    url = (
        f"{HTTP}/workers/{reactor}/jobs/update/job_name/"
        f"relay/experiments/{experiment}"
    )

    payload = {"settings": {"is_relay_on": 0}}

    headers = {"Content-Type": "application/json"}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 202:
        print(f"Relay {relay} turned off in reactor {reactor}.")
    else:
        print(f"Failed to turn off relay. Status code: {response.status_code}")


# --- MQTT Functions ---
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("pioreactor/control")


def on_message(client, userdata, msg):
    try:
        message = json.loads(msg.payload.decode("utf-8"))
        command = message.get("command")
        reactor = message.get("reactor")
        experiment = message.get("experiment")

        # Dispatch commands to respective functions
        if command == "start_stirring":
            start_stirring(reactor, experiment)
            if message.get("rpm"):
                time.sleep(1)
                update_stirring_rpm(reactor, experiment, message["rpm"])
        elif command == "stop_stirring":
            stop_stirring(reactor, experiment)
        elif command == "update_stirring_rpm":
            update_stirring_rpm(reactor, experiment, message["rpm"])
        elif command == "set_led_intensity":
            set_led_intensity(
                reactor, experiment, message["brightness"], message["led"]
            )
        elif command == "get_temperature_readings":
            get_temperature_readings(
                client, reactor, experiment, message["filter_mod"], message["lookback"]
            )
        elif command == "get_experiments":
            get_experiments(client)
        elif command == "get_reactors":
            get_reactors(client, experiment)
        elif command == "get_reactor_stats":
            get_reactor_stats(client, reactor)
        elif command == "get_worker":
            get_worker(client, reactor)
        elif command == "set_temperature_automation":
            set_temperature_automation(
                reactor, experiment, message["automation"], message.get("temp")
            )
        elif command == "temp_update":
            temp_update(reactor, experiment, message["settings"])
        elif command == "temp_restart":
            temp_restart(
                reactor, experiment, message["automation"], message.get("temp", None)
            )
        elif command == "stop_od_reading":
            stop_od_reading(reactor, experiment)
        elif command == "start_od_reading":
            start_od_reading(reactor, experiment)
        elif command == "stop_growth_rate":
            stop_growth_rate(reactor, experiment)
        elif command == "start_growth_rate":
            start_growth_rate(reactor, experiment)
        elif command == "get_readings":
            get_readings(
                client,
                reactor,
                experiment,
                message["filter_mod"],
                message["lookback"],
                message["filter_mod2"],
                message["lookback2"],
                message["filter_mod3"],
                message["lookback3"],
                message["filter_mod4"],
                message["lookback4"],
                message["amount"],
                message["amount2"],
                message["amount3"],
                message["amount4"],
            )
        elif command == "new_experiment":
            new_experiment(
                message["experiment"],
                message.get("description", ""),
                message.get("mediaUsed", ""),
                message.get("organismUsed", ""),
            )
        elif command == "change_experiment":
            change_experiment(message["experiment"], message["experiment_new"], reactor)
        elif command == "delete_experiment":
            delete_experiment(message["experiment"])
        elif command == "pump_add_media":
            pump_add_media(
                reactor,
                experiment,
                message.get("volume"),
                message.get("duration"),
                message.get("continuous", False),
            )
        elif command == "pump_remove_media":
            pump_remove_media(
                reactor,
                experiment,
                message.get("volume"),
                message.get("duration"),
                message.get("continuous", False),
            )
        elif command == "add_alt_media":
            add_alt_media(
                reactor,
                experiment,
                message["media"],
                message.get("volume"),
                message.get("duration"),
                message.get("continuous", False),
            )
        elif command == "circulate_media":
            circulate_media(reactor, experiment, message["duration"])
        elif command == "circulate_alt_media":
            circulate_alt_media(
                reactor, experiment, message["media"], message["duration"]
            )
        elif command == "start_relay":
            start_relay(reactor, experiment, "a")
        elif command == "stop_relay":
            stop_relay(reactor, experiment, "a")
        elif command == "relay_off":
            relay_on(reactor, experiment, "a")
        elif command == "relay_on":
            relay_off(reactor, experiment, "a")
        else:
            print(f"Unknown command: {command}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode message: {e}")


def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")


# --- MQTT Client Setup ---
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
client.username_pw_set(lookhere.username, lookhere.password)
client.connect(lookhere.broker, lookhere.port)
client.loop_forever()
