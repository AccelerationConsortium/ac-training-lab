import asyncio

from prefect import get_client


async def trigger_ot2():
    # This payload will be passed as parameters to main_flow
    params = {"R": 120, "Y": 50, "B": 80, "mix_well": "B2"}

    async with get_client() as client:
        dep = await client.read_deployment_by_name(
            "ot2-device-flow/ot2-device-deployment"
        )
        run = await client.create_flow_run_from_deployment(dep.id, parameters=params)
        print("Triggered OT-2 run:", run.id)


asyncio.run(trigger_ot2())
