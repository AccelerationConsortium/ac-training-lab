# https://www.prefect.io/blog/unveiling-interactive-workflows
# https://prefecthq.github.io/prefect-slack/
# https://github.com/PrefectHQ/interactive_workflow_examples

from prefect.blocks.notifications import SlackWebhook

slack_block = SlackWebhook.load("help-us-humans")
