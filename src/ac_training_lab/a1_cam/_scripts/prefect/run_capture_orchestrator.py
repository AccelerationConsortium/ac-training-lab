"""Async orchestrator that triggers a deployment and returns its result.

This uses `run_deployment` (async) to create and execute the flow run, then
reads the flow run via the Prefect client and calls `aresult()` on the final
state to retrieve the flow return value.

Usage:
    python scripts/run_capture_orchestrator.py [deployment-name]

Defaults to `capture-image/capture-image`.
"""

import asyncio
import sys

from prefect.client.orchestration import get_client
from prefect.deployments import run_deployment

# WARNING: These have not been working. This is trying to get the returned
# result without making an S3 bucket just for passing a string around. See
# src/ac_training_lab/a1_cam/_scripts/prefect/copilot-logs.md.


async def run_and_get(deployment_name: str = "capture-image/capture-image") -> object:
    # Trigger the deployment and wait (the function awaits completion by default)
    flow_run = await run_deployment(name=deployment_name)

    # Read the flow run and get its final state/result
    async with get_client() as client:
        fr = await client.read_flow_run(flow_run.id)
        state = fr.state
        result = await state.aresult(raise_on_failure=True)
        print("Flow result:", result)
        return result


if __name__ == "__main__":
    dep = sys.argv[1] if len(sys.argv) > 1 else "capture-image/capture-image"
    asyncio.run(run_and_get(dep))
