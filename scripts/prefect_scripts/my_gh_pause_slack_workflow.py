# https://www.prefect.io/blog/unveiling-interactive-workflows
# https://prefecthq.github.io/prefect-slack/
# https://github.com/PrefectHQ/interactive_workflow_examples

from prefect import flow, get_run_logger, pause_flow_run
from prefect.blocks.notifications import SlackWebhook

slack_block = SlackWebhook.load("help-us-humans")


@flow
def greet_user():
    logger = get_run_logger()

    user = pause_flow_run(wait_for_input=str)

    logger.info(f"Hello, {user}!")
