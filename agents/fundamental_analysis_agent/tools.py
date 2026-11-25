from market_mcp.client import MarketMCPClient


FUNDAMENTAL_ANALYSIS_TOOL_NAMES = {
    "get_company_profile",
    "get_income_statement",
    "get_balance_sheet",
    "get_cash_flow",
    "get_key_ratios",
    "get_peer_comparison",
    "get_nse_financial_results",
    "screen_by_fundamentals",
}


async def get_fundamental_analysis_tools():
    """
    Get the tools assigned to the Fundamental Analysis Agent.
    """

    client = MarketMCPClient()

    all_tools = await client.get_tools()

    fundamental_tools = [
        tool
        for tool in all_tools
        if tool.name in FUNDAMENTAL_ANALYSIS_TOOL_NAMES
    ]

    return fundamental_tools