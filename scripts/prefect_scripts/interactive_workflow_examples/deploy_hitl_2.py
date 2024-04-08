from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/AccelerationConsortium/ac-training-lab.git",
        entrypoint=(
            "scripts/prefect_scripts/interactive_workflow_examples/"
            "human_in_the_loop_2.py:classify_image"
        ),
    ).deploy(name="human-in-the-loop", work_pool_name="my-managed-pool")

    1 + 1

# cron="0 1 * * *",
