import time

from gradio_client import Client
from prefect import flow, task
from prefect.flow_runs import pause_flow_run

GRADIO_ENDPOINT = "AccelerationConsortium/PioReactor_gradio"  # Hardcoded endpoint


def get_status():
    client = Client(GRADIO_ENDPOINT)
    result = client.predict(
        exp="Hello!!", api_name="/get_status_default"  # Replace with actual experiment
    )
    return result


@task
def start_stirring(rpm: int, experiment: str):
    client = Client(GRADIO_ENDPOINT)
    result = client.predict(
        rpm=rpm, experiment=experiment, state="start", api_name="/stirring_default"
    )
    return result


@task
def stop_stirring(experiment: str):
    client = Client(GRADIO_ENDPOINT)
    result = client.predict(
        rpm=0, experiment=experiment, state="stop", api_name="/stirring_default"
    )
    return result


@task
def update_stirring(rpm: int, experiment: str):
    client = Client(GRADIO_ENDPOINT)
    result = client.predict(
        rpm=rpm, experiment=experiment, state="update", api_name="/stirring_default"
    )
    return result


@flow
def stirring_control(
    rpm: int = 500, stop: bool = False, start: bool = False, update: bool = False
):
    status = get_status()
    experiment = status[0]  # Extract experiment name from the response
    rpm_value = rpm  # Example RPM value
    if start:
        start_stirring(rpm_value, experiment)
    if update:
        update_stirring(rpm_value, experiment)
    if stop:
        stop_stirring(experiment)


@task
def waiting_time(wait: int):
    time.sleep(wait)


@flow
def intermediary_flow(wait: int = 5):
    stirring_control(start=True)
    stirring_control(update=True, rpm=1000)
    waiting_time(wait)
    stirring_control(stop=True)


@flow
def user_stop_stirring():
    stirring_control(start=True)
    stirring_control(update=True, rpm=1000)
    pause_flow_run(wait_for_input=bool)
    stirring_control(stop=True)


if __name__ == "__main__":
    # stirring_control()
    stirring_control.deploy(
        name="Stop Stirring",
        work_pool_name="docker-pool",
        parameters={"stop": True},
        image="edisonlinx5o/gradio_client:latest",
        push=False,
    )
    stirring_control.deploy(
        name="Start Stirring",
        work_pool_name="docker-pool",
        parameters={"start": True},
        image="edisonlinx5o/gradio_client:latest",
        push=False,
    )
    stirring_control.deploy(
        name="Stirring Control",
        work_pool_name="docker-pool",
        parameters={"update": True, "rpm": 500},
        image="edisonlinx5o/gradio_client:latest",
        push=False,
    )
    intermediary_flow.deploy(
        name="Stirring Control Flow",
        work_pool_name="docker-pool",
        image="edisonlinx5o/gradio_client:latest",
        push=False,
    )
    user_stop_stirring.deploy(
        name="User Controlled Stirring",
        work_pool_name="docker-pool",
        image="edisonlinx5o/gradio_client:latest",
        push=False,
    )
