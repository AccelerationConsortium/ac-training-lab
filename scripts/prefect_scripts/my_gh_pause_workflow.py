from prefect import flow, get_run_logger, pause_flow_run


@flow
def greet_user():
    logger = get_run_logger()

    user = pause_flow_run(wait_for_input=str, timeout=60)

    logger.info(f"Hello, {user}!")


if __name__ == "__main__":
    greet_user()
