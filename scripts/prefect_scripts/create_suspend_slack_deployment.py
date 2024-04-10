from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/AccelerationConsortium/ac-training-lab.git",
        entrypoint="scripts/prefect_scripts/my_gh_suspend_slack_workflow.py:greet_user",
    ).deploy(
        name="suspend-workflow-deployment",
        work_pool_name="my-managed-pool",
        # cron="0 1 * * *",
    )
