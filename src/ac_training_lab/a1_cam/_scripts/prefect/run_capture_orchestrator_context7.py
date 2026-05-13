import asyncio
from typing import Optional
from uuid import UUID

from prefect.client.orchestration import get_client
from prefect.deployments import run_deployment
from prefect.flow_runs import wait_for_flow_run


async def capture_image_async(deployment_identifier: str, timeout: int = 300) -> str:
    """Request image capture and get URI back.

    Accepts either a UUID string for `deployment_id` or a deployment name slug
    like "project/deployment" or "deployment-name/flow-name". Falls back to
    using the identifier as a deployment name if it isn't a valid UUID.
    """
    async with get_client() as client:
        # Try parsing as UUID; otherwise treat as a deployment name/slug
        deployment_id: Optional[UUID] = None
        try:
            deployment_id = UUID(deployment_identifier)
        except (ValueError, TypeError):
            deployment_id = None

        if deployment_id is not None:
            flow_run = await client.create_flow_run_from_deployment(
                deployment_id=deployment_id
            )
        else:
            # Fall back to the higher-level `run_deployment` helper which accepts
            # a deployment slug like "project/deployment". Run it in a thread
            # to avoid blocking the async loop.
            flow_run = await asyncio.to_thread(run_deployment, deployment_identifier)

        # Wait for completion
        await wait_for_flow_run(
            flow_run_id=flow_run.id,
            timeout=timeout,
        )

        # Read the flow run to get the state
        run = await client.read_flow_run(flow_run.id)

        # Get the result from the state (may raise if result persistence is disabled)
        if run.state.is_completed():
            # `result()` may be async in some versions — handle either case
            result = run.state.result()
            if asyncio.iscoroutine(result):
                result = await result
            return result
        else:
            raise RuntimeError(f"Flow run failed: {run.state.type}")


def capture_image(deployment_identifier: str, timeout: int = 300) -> str:
    """Synchronous wrapper."""
    return asyncio.run(capture_image_async(deployment_identifier, timeout))


if __name__ == "__main__":
    # Replace with either a deployment UUID or a deployment name slug
    deployment_identifier = "capture-image/capture-image"
    uri = capture_image(deployment_identifier)
    print(f"Image URI: {uri}")
