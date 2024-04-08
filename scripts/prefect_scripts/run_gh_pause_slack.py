import asyncio

from my_gh_pause_slack_workflow import greet_user


async def main():
    msg_out = await greet_user()
    print(msg_out)


if __name__ == "__main__":
    asyncio.run(main())

    1 + 1
