from market_mcp.client import MarketMCPClient


F_AND_O_ANALYSIS_TOOL_NAMES = {
    "get_option_chain",
    "get_pcr",
    "get_max_pain",
    "get_futures_data",
    "get_oi_data",
}


async def get_f_and_o_analysis_tools():
    """
    Get the tools assigned to the F&O Analysis Agent.
    """

    client = MarketMCPClient()

    all_tools = await client.get_tools()

    f_and_o_tools = [
        tool
        for tool in all_tools
        if tool.name in F_AND_O_ANALYSIS_TOOL_NAMES
    ]

    return f_and_o_tools