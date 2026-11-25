from market_mcp.client import MarketMCPClient


MARKET_INTELLIGENCE_TOOL_NAMES = {
    "get_market_status",
    "get_fii_dii_data",
    "get_advances_declines",
    "get_index",
    "get_all_indices",
    "get_index_constituents",
    "get_index_history",
    "get_sector_performance",
    "get_market_news",
    "get_stock_news",
    "get_sector_news",
    "get_nse_announcements",
    "get_board_meetings",
    "get_bulk_deals",
    "get_corporate_actions",
}


async def get_market_intelligence_tools():
    """
    Get the tools assigned to the Market Intelligence Agent.
    """

    client = MarketMCPClient()

    all_tools = await client.get_tools()

    market_intelligence_tools = [
        tool
        for tool in all_tools
        if tool.name in MARKET_INTELLIGENCE_TOOL_NAMES
    ]

    return market_intelligence_tools