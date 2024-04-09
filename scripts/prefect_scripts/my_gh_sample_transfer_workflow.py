# https://www.prefect.io/blog/unveiling-interactive-workflows
# https://prefecthq.github.io/prefect-slack/
# https://github.com/PrefectHQ/interactive_workflow_examples

from prefect import flow, get_run_logger, pause_flow_run, settings
from prefect.blocks.notifications import SlackWebhook
from prefect.context import get_run_context
from prefect.input import RunInput

slack_block = SlackWebhook.load("prefect-test")

MESSAGE = "Please move sample <{sample_link}|{sample_name}> from <{source_link}|{source_name}> to <{destination_link}|{destination_name}>."  # noqa: E501


class UserInput(RunInput):
    github_username: str
    comments: str
    flag_for_review: bool


@flow(name="sample-transfer")  # persist result or not?
async def move_sample(
    sample_link: str,
    sample_name: str,
    source_link: str,
    source_name: str,
    destination_link: str,
    destination_name: str,
):
    logger = get_run_logger()

    message = MESSAGE.format(
        sample_link=sample_link,
        sample_name=sample_name,
        source_link=source_link,
        source_name=source_name,
        destination_link=destination_link,
        destination_name=destination_name,
    )
    flow_run = get_run_context().flow_run

    if flow_run and settings.PREFECT_UI_URL:
        flow_run_url = (
            f"{settings.PREFECT_UI_URL.value()}/flow-runs/flow-run/{flow_run.id}"
        )
        message += f"\n\nOpen the <{flow_run_url}|paused flow run>, click 'Resume', and follow the instructions."  # noqa: E501

    await slack_block.notify(message)
    user_input = await pause_flow_run(
        wait_for_input=UserInput.with_initial_data(
            description="Please provide your GitHub username, any comments, and whether this sample transfer should be flagged for review.",  # noqa: E501
            github_username="sgbaird",
            comments="",
            flag_for_review=False,
        ),
        timeout=300,
    )

    logger.info(f"🚀 Sample transfer initiated by {user_input.github_username}")
    logger.info(f"💬 Comments: {user_input.comments}")
    logger.info(f"🚩 Flagged for review: {user_input.flag_for_review}")

    return user_input
