# https://www.prefect.io/blog/unveiling-interactive-workflows
# https://prefecthq.github.io/prefect-slack/
# https://github.com/PrefectHQ/interactive_workflow_examples

from prefect import flow, get_run_logger, settings, suspend_flow_run
from prefect.blocks.notifications import SlackWebhook
from prefect.context import get_run_context

slack_block = SlackWebhook.load("prefect-test")

MESSAGE = "This is an example of a human-in-the-loop flow using Prefect's interactive workflow features."  # noqa: E501


@flow(name="greet-slack-user-suspend", persist_result=True)  # persist result or not?
async def greet_user():
    logger = get_run_logger()

    message = str(MESSAGE)  # modify as needed
    flow_run = get_run_context().flow_run

    if flow_run and settings.PREFECT_UI_URL:
        flow_run_url = (
            f"{settings.PREFECT_UI_URL.value()}/flow-runs/flow-run/{flow_run.id}"
        )
        message += f"\n\nOpen the <{flow_run_url}|paused flow run>, click 'Resume', and then submit your name."  # noqa: E501

    await slack_block.notify(message)
    user = await suspend_flow_run(wait_for_input=str, timeout=120)

    msg_out = f"Hello, {user}!"
    logger.info(msg_out)

    return msg_out
