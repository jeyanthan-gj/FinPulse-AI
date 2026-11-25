import asyncio

from agents.Stock_Research_Agent.tools import get_stock_research_tools


async def main():
    tools = await get_stock_research_tools()

    print(f"Stock Research tools: {len(tools)}")

    for tool in tools:
        print(f"- {tool.name}")


if __name__ == "__main__":
    asyncio.run(main())