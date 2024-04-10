from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/AccelerationConsortium/ac-training-lab.git",
        entrypoint="scripts/prefect_scripts/my_gh_sample_transfer_workflow.py:move_sample",  # noqa: E501
    ).deploy(
        name="sample-transfer-deployment",
        work_pool_name="my-managed-pool",
        # cron="0 1 * * *",
    )
