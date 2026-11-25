from market_mcp.client import MarketMCPClient


STOCK_RESEARCH_TOOL_NAMES = {
    "get_stock_quote",
    "search_stocks",
    "get_stock_history",
    "get_top_gainers",
    "get_top_losers",
    "get_52week_high",
    "get_52week_low",
    "get_most_active_stocks",
    "get_corporate_actions",
    "get_company_profile",
    "get_shareholding_pattern",
    "get_bulk_deals",
    "get_nse_announcements",
    "get_board_meetings",
    "get_peer_comparison",
}


async def get_stock_research_tools():
    """
    Get the tools assigned to the Stock Research Agent.
    """

    client = MarketMCPClient()

    all_tools = await client.get_tools()

    stock_research_tools = [
        tool
        for tool in all_tools
        if tool.name in STOCK_RESEARCH_TOOL_NAMES
    ]

    return stock_research_tools