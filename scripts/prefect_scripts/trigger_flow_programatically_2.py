# https://docs.prefect.io/latest/api-ref/prefect/client/orchestration/?h=create_flow_run_from_deployment#prefect.client.orchestration.PrefectClient.create_flow_run_from_deployment
# https://docs.prefect.io/latest/api-ref/prefect/client/orchestration/?h=create_flow_run_from_deployment#prefect.client.orchestration.PrefectClient.create_flow_run

# CLI example:
# https://docs.prefect.io/latest/getting-started/quickstart/#step-4-make-your-code-schedulable

from prefect.client.orchestration import get_client

# from prefect.states import Scheduled

deployment_id = "7a7810f6-8d01-4a9b-aae2-e3c41b58756d"  # repo info deployment

parameters = {"repo_name": "prefect", "repo_owner": "PrefectHQ"}

with get_client() as client:
    deployment = client.read_deployment(deployment_id)
    flow_run = client.create_flow_run_from_deployment(
        deployment.id,
        parameters=parameters,
        # state=Scheduled(scheduled_time=scheduled_start_time),
        # tags=tags,
        # job_variables=job_vars,
    )
