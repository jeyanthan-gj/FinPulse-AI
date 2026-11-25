
from market_mcp.client import MarketMCPClient


TECHNICAL_ANALYSIS_TOOL_NAMES = {
    "get_stock_quote",
    "get_stock_history",
    "get_index_history",
    "get_technical_indicators",
    "get_support_resistance",
    "detect_candlestick_patterns",
    "scan_patterns_bulk",
}


async def get_technical_analysis_tools():
    """
    Get the tools assigned to the Technical Analysis Agent.
    """

    client = MarketMCPClient()

    all_tools = await client.get_tools()

    technical_analysis_tools = [
        tool
        for tool in all_tools
        if tool.name in TECHNICAL_ANALYSIS_TOOL_NAMES
    ]

    return technical_analysis_tools