import asyncio

from prefect import get_client


async def get_result(flow_id):
    async with get_client() as client:
        response = await client.hello()
        print(response.json())  # 👋
        result = (await client.read_flow_run(flow_id)).state.result()
        return result


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(get_result("bd33b4ee-7bf0-48e3-9629-23bdf121c107"))
    # PersistedResult(type='reference', artifact_type=None,
    # artifact_description=None, serializer_type='pickle',
    # storage_block_id=UUID('1e4ce198-a25a-4808-81db-65cb30d0cffb'),
    # storage_key='69b055e353b745249d493350b79e81e8')
    loop.close()

    1 + 1
