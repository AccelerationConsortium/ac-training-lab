# https://docs.prefect.io/latest/guides/creating-interactive-workflows/
from prefect import flow, get_run_logger, pause_flow_run
from prefect.input import RunInput


class UserInput(RunInput):
    name: str
    age: int

    # Imagine overridden methods here!
    def override_something(self, *args, **kwargs):
        super().override_something(*args, **kwargs)


@flow
async def greet_user():
    logger = get_run_logger()

    user = await pause_flow_run(wait_for_input=UserInput)

    logger.info(f"Hello, {user.name}!")
