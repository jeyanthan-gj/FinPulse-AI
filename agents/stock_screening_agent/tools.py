
from market_mcp.client import MarketMCPClient


STOCK_SCREENING_TOOL_NAMES = {
    "screen_stocks",
    "screen_by_fundamentals",
    "run_preset_screen",
    "get_top_gainers",
    "get_top_losers",
    "get_most_active_stocks",
    "get_52week_high",
    "get_52week_low",
}


async def get_stock_screening_tools():
    """
    Get the tools assigned to the Stock Screening Agent.
    """

    client = MarketMCPClient()

    all_tools = await client.get_tools()

    stock_screening_tools = [
        tool
        for tool in all_tools
        if tool.name in STOCK_SCREENING_TOOL_NAMES
    ]

    return stock_screening_tools
