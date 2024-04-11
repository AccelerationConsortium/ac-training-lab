from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/AccelerationConsortium/ac-training-lab.git",
        entrypoint="scripts/prefect_scripts/hello_world.py:hello_world",
    ).deploy(
        name="hello-world-deployment",
        work_pool_name="my-managed-pool",
        cron="0 1 * * *",  # Run every day at 1:00 AM
    )
