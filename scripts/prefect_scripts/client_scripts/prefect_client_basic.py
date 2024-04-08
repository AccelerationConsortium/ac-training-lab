import asyncio

from prefect import get_client


async def hello():
    async with get_client() as client:
        response = await client.hello()
        print(response.json())  # 👋


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(hello())
    loop.close()

    1 + 1
