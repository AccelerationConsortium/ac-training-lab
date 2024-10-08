import requests
import json
from datetime import datetime
import paho.mqtt.client as mqtt
import json
import lookhere
import time

# --- PioReactor API Functions ---
def create_experiment(experiment, description="", mediaUsed="", organismUsed=""):
    url = "http://pioreactor.local/api/experiments"
    created_at = datetime.now().isoformat()
    
    payload = {
        "experiment": experiment,
        "created_at": created_at,
        "description": description,
        "mediaUsed": mediaUsed,
        "organismUsed": organismUsed
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
    url = f"http://pioreactor.local/api/experiments/{experiment}/workers"
    payload = {"pioreactor_unit": worker}
    headers = {"Content-Type": "application/json"}

    response = requests.put(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print(f"Worker {worker} assigned to experiment {experiment}.")
    else:
        print(f"Failed to assign worker {worker}. Status code: {response.status_code}")

def remove_worker_from_experiment(worker, experiment):
    url = f"http://pioreactor.local/api/experiments/{experiment}/workers/{worker}"
    headers = {"Content-Type": "application/json"}

    response = requests.delete(url, headers=headers)
    if response.status_code == 202:
        print(f"Worker {worker} removed from experiment {experiment}.")
    else:
        print(f"Failed to remove worker {worker}. Status code: {response.status_code}")

def start_stirring(worker, experiment):
    url = f"http://pioreactor.local/api/units/{worker}/jobs/run/job_name/stirring/experiments/{experiment}"
    headers = {"Content-Type": "application/json"}
    payload = {"env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"Stirring started for worker {worker}")
    else:
        print(f"Failed to start stirring. Status code: {response.status_code}")

def stop_stirring(worker, experiment):
    url = f"http://pioreactor.local/api/units/{worker}/jobs/update/job_name/stirring/experiments/{experiment}"
    headers = {"Content-Type": "application/json"}
    payload = {"settings" : {"$state": "disconnected"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"Stirring stopped for worker {worker}.")
    else:
        print(f"Failed to stop stirring. Status code: {response.status_code}")

def update_stirring_rpm(worker, experiment, rpm):
    url = f"http://pioreactor.local/api/units/{worker}/jobs/update/job_name/stirring/experiments/{experiment}"
    headers = {"Content-Type": "application/json"}
    payload = {"settings": {"target_rpm": rpm}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"Stirring RPM updated to {rpm} for worker {worker}.")
    else:
        print(f"Failed to update stirring RPM. Status code: {response.status_code}")

def set_led_intensity(worker, experiment, brightness_value):
    url = f"http://pioreactor.local/api/workers/{worker}/jobs/run/job_name/led_intensity/experiments/{experiment}"
    headers = {"Content-Type": "application/json"}
    payload = {"options": {"B": brightness_value, "source_of_event": "UI"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"LED intensity set to {brightness_value} for worker {worker}.")
    else:
        print(f"Failed to set LED intensity. Status code: {response.status_code}")

def get_temperature_readings(client, reactor, experiment, filter_mod, lookback):
    url = f"http://pioreactor.local/api/experiments/{experiment}/time_series/temperature_readings"
    params = {"filter_mod_N": filter_mod, "lookback": lookback}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print(f"Temperature readings retrieved for experiment {experiment}.")
        print(response.json())
        temperature_data = response.json()
        client.publish(f'pioreactor/{reactor}/temperature', json.dumps(temperature_data))
    else:
        print(f"Failed to retrieve temperature readings. Status code: {response.status_code}")

def get_experiments(client):
    url = "http://pioreactor.local/api/experiments"
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        experiments = response.json()
        client.publish('pioreactor/experiments', json.dumps(experiments))
    else:
        print(f"Failed to retrieve experiments. Status code: {response.status_code}")

def get_reactors(client, experiment):
    url = f"http://pioreactor.local/api/experiments/{experiment}/workers"
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        reactors = response.json()
        client.publish('pioreactor/reactors', json.dumps(reactors))
    else:
        print(f"Failed to retrieve reactors. Status code: {response.status_code}")

def get_reactor_stats(client, reactor):
    url = f"http://pioreactor.local/api/units/{reactor}/jobs/running"
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        stats = response.json()
        client.publish('pioreactor/stats', json.dumps(stats))
    else:
        print(f"Failed to retrieve reactor stats. Status code: {response.status_code}")

def get_task_status(task_id):
    # Construct the URL for getting the task status
    url = f"http://pioreactor.local/unit_api/task_results/{task_id}"
    
    # Set the headers
    headers = {
        "Content-Type": "application/json"
    }
    
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
    url = f"http://pioreactor.local/api/workers/assignments"
    
    # Set the headers
    headers = {
        "Content-Type": "application/json"
    }
    
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

    url2 = f"http://pioreactor.local/api/units/{reactor}/jobs/running"

    response2 = requests.get(url2, headers=headers)

    stats = response2.json()

    # print(stats)

    # task = stats.get("task_id", None)

    # if task is None:
    #     return None

    # response3 = get_task_status(task)

    # print(response3)

    running = []

    for item in stats:
        running.append(item["name"])

    # print(running)

    # running.remove("watchdog")
    running.remove("mqtt_to_db_streaming")
    running.remove("monitor")

    payload = {
        "experiment": experiment,
        "running": running
    }

    # print("Publishing worker")
    client.publish(f"pioreactor/{reactor}/worker", json.dumps(payload))

def set_temperature_automation(worker, experiment, automation_name, temp=None):
    # Construct the URL for the request
    url = f"http://pioreactor.local/api/workers/{worker}/jobs/run/job_name/temperature_automation/experiments/{experiment}"
    
    # Prepare the payload
    if automation_name == 'only_record_temperature':
        payload = {
            "args": [],
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {
                "automation_name": automation_name  # Set the desired automation name
            }
        }
    elif automation_name == 'thermostat':
        payload = {
            "args": [],
            "env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"},
            "options": {
                "automation_name": automation_name,  # Set the desired automation name
                "skip_first_run": 0,
                "target_temperature": temp  # Set the desired temperature value for the thermostat
            }
        }
    else:
        print(f"Invalid automation name: {automation_name}")
        return
    
    # Set the headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Send the PATCH request to set the automation
    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    
    # Check the response status code
    if response.status_code == 202:
        print(f"Automation '{automation_name}' set successfully on worker {worker} for experiment {experiment}!")
    else:
        print(f"Failed to set automation. Status code: {response.status_code}")
        print(f"Response: {response.text}")

def temp_update(worker, experiment, settings):
    # Construct the URL for the request
    url = f"http://pioreactor.local/api/workers/{worker}/jobs/update/job_name/temperature_automation/experiments/{experiment}"
    
    # Prepare the payload
    payload = {
        "args": [],
        "settings": settings
    }
    
    # Set the headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Send the PATCH request to set the automation
    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    
    # Check the response status code
    if response.status_code == 202:
        print(f"Automation settings updated successfully on worker {worker} for experiment {experiment}!")
    else:
        print(f"Failed to update automation settings. Status code: {response.status_code}")
        print(f"Response: {response.text}")

def temp_restart(worker, experiment, automation, temp=None):
    # Update automation to stop then start new automation
    print("Restarting temperature automation")
    temp_update(worker, experiment, {"$state": "disconnected"})
    time.sleep(3)
    set_temperature_automation(worker, experiment, automation, temp)

def stop_od_reading(reactor, experiment):
    url = f"http://pioreactor.local/api/workers/{reactor}/jobs/update/job_name/od_reading/experiments/{experiment}"
    headers = {"Content-Type": "application/json"}
    payload = {"settings" : {"$state": "disconnected"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"OD reading stopped for worker {reactor}.")
    else:
        print(f"Failed to stop OD reading. Status code: {response.status_code}")

def start_od_reading(reactor, experiment):
    url = f"http://pioreactor.local/api/workers/{reactor}/jobs/run/job_name/od_reading/experiments/{experiment}"
    headers = {"Content-Type": "application/json"}
    payload = {"env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"OD reading started for worker {reactor}")
    else:
        print(f"Failed to start OD reading. Status code: {response.status_code}")

def stop_growth_rate(reactor, experiment):
    url = f"http://pioreactor.local/api/workers/{reactor}/jobs/update/job_name/growth_rate_calculating/experiments/{experiment}"
    headers = {"Content-Type": "application/json"}
    payload = {"settings" : {"$state": "disconnected"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"Growth rate stopped for worker {reactor}.")
    else:
        print(f"Failed to stop growth rate. Status code: {response.status_code}")
    
def start_growth_rate(reactor, experiment):
    url = f"http://pioreactor.local/api/workers/{reactor}/jobs/run/job_name/growth_rate_calculating/experiments/{experiment}"
    headers = {"Content-Type": "application/json"}
    payload = {"env": {"EXPERIMENT": experiment, "JOB_SOURCE": "user"}}

    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print(f"Growth rate started for worker {reactor}")
    else:
        print(f"Failed to start growth rate. Status code: {response.status_code}")

# --- MQTT Functions ---
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe('pioreactor/control')

def on_message(client, userdata, msg):
    try:
        message = json.loads(msg.payload.decode('utf-8'))
        command = message.get('command')
        reactor = message.get('reactor')
        experiment = message.get('experiment')

        # Dispatch commands to respective functions
        if command == 'start_stirring':
            start_stirring(reactor, experiment)
            if message.get('rpm'):
                time.sleep(1)
                update_stirring_rpm(reactor, experiment, message['rpm'])
        elif command == 'stop_stirring':
            stop_stirring(reactor, experiment)
        elif command == 'update_stirring_rpm':
            update_stirring_rpm(reactor, experiment, message['rpm'])
        elif command == 'set_led_intensity':
            set_led_intensity(reactor, experiment, message['brightness'])
        elif command == 'get_temperature_readings':
            get_temperature_readings(client, reactor, experiment, message['filter_mod'], message['lookback'])
        elif command == 'get_experiments':
            get_experiments(client)
        elif command == 'get_reactors':
            get_reactors(client, experiment)
        elif command == 'get_reactor_stats':
            get_reactor_stats(client, reactor)
        elif command == 'get_worker':
            get_worker(client, reactor)
        elif command == 'set_temperature_automation':
            set_temperature_automation(reactor, experiment, message['automation'], message.get('temp'))
        elif command == 'temp_update':
            temp_update(reactor, experiment, message['settings'])
        elif command == 'temp_restart':
            temp_restart(reactor, experiment, message['automation'], message.get('temp', None))
        elif command == 'stop_od_reading':
            stop_od_reading(reactor, experiment)
        elif command == 'start_od_reading':
            start_od_reading(reactor, experiment)
        elif command == 'stop_growth_rate':
            stop_growth_rate(reactor, experiment)
        elif command == 'start_growth_rate':
            start_growth_rate(reactor, experiment)
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