import asyncio

from app.agents.research_agent import build_agent


async def main():
    agent = build_agent()

    result = await agent.run(
        user_msg=(
            "What controls are recommended "
            "for high-impact AI agents?"
        )
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())