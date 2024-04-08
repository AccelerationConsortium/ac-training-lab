"""
An example of a human-in-the-loop flow using Prefect's interactive workflow
features.

Included in the blog post:
https://www.prefect.io/blog/unveiling-interactive-workflows

SOURCE:
https://github.com/PrefectHQ/interactive_workflow_examples/blob/main/human_in_the_loop.py

LICENSE: Apache 2.0

See also
https://discourse.prefect.io/t/how-to-create-a-slack-webhook-url-for-the-slackwebhook-notification-block-incoming-webhook/2260 # noqa: E501
"""

import random
from enum import Enum

from prefect import flow, get_run_logger, settings, task
from prefect.blocks.notifications import SlackWebhook
from prefect.context import get_run_context
from prefect.engine import pause_flow_run

# Set the minimum confidence threshold, below which the model
# prompts for user input.
Confidence = int
MIN_CONFIDENCE: Confidence = 90

# An image of a pug.
# odosD, CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0>,
# via Wikimedia Commons"
PUGLY = "https://upload.wikimedia.org/wikipedia/commons/d/d7/Sad-pug.jpg"


class Animal(Enum):
    """Possible labels the model or a human can use"""

    PIG = "pig"
    DOG = "dog"


class GuessingClassifier:
    """
    An image classifier that returns a random label and confidence score
    """

    def classify(self, image) -> tuple[Animal, Confidence]:
        return random.choice(list(Animal)), random.randint(0, 100)


# Initialize the classifier so it can be used by the flow.
image_classifier = GuessingClassifier()

# A Block we'll use to notify our humans that we need help
slack_block = SlackWebhook.load("help-us-humans")


@task
async def classify(image) -> tuple[Animal, Confidence]:
    return image_classifier.classify(image)


@task
async def load_image(url: str) -> bytes:
    return b"fake image bytes"


MESSAGE = "Help us, humans! Please view <{image_url}|this image> and classify it."


@flow
async def classify_image(image_url: str = PUGLY):
    logger = get_run_logger()
    image = await load_image(image_url)
    label, confidence = await classify(image)

    if confidence < MIN_CONFIDENCE:
        message = MESSAGE.format(image_url=image_url)
        flow_run = get_run_context().flow_run

        if flow_run and settings.PREFECT_UI_URL:
            flow_run_url = (
                f"{settings.PREFECT_UI_URL.value()}/flow-runs/flow-run/{flow_run.id}"
            )
            message += f"\n\nAfter you view the image, open the <{flow_run_url}|paused flow run> and click Resume to classify the image."  # noqa: E501

        await slack_block.notify(message)

        label = await pause_flow_run(wait_for_input=Animal, timeout=60)

        if label == label:
            logger.info("The model was right!")
        else:
            logger.info("The model was wrong!")
    else:
        logger.info(
            f"The model was {confidence}% confident that the image was of a {label.value}!"  # noqa: E501
        )
