# https://docs.prefect.io/latest/concepts/deployments/?h=run#running-a-deployed-flow-from-within-python-flow-code

from prefect.deployments import run_deployment

name = "repo-info/my-first-deployment"  # can also be deployment ID
parameters = parameters = {"repo_name": "prefect", "repo_owner": "PrefectHQ"}

print("Running deployment")
# https://docs.prefect.io/latest/concepts/deployments/#running-a-deployed-flow-from-within-python-flow-code
# timeout=0 to return immediately
flow_run = run_deployment(name=name, parameters=parameters)

# set persist_result=True in the flow definition so the result is not None NOTE:
# Can't run locally because "Path ... does not exist"
# (https://prefect-community.slack.com/archives/C04DZJC94DC/p1712593387928839?thread_ts=1712256264.613129&cid=C04DZJC94DC) # noqa: E501
print(flow_run.state.result(fetch=True))


1 + 1
# from prefect.cli.deployment import run

# if __name__ == "__main__":
#     run()
