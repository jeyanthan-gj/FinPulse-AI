from market_mcp.client import MarketMCPClient


MUTUAL_FUND_ETF_TOOL_NAMES = {
    "search_mutual_funds",
    "get_mf_nav",
    "get_mf_history",
    "get_mf_categories",
    "compare_mutual_funds",
    "get_top_funds_by_category",
    "analyze_mutual_fund",
    "find_best_mutual_funds",
    "find_hidden_gems",
    "mf_sip_returns",
    "compare_mf_detailed",
    "get_all_etfs",
    "get_etf_quote",
    "get_etf_history",
}


async def get_mutual_fund_etf_tools():
    """
    Get the tools assigned to the Mutual Fund & ETF Agent.
    """

    client = MarketMCPClient()

    all_tools = await client.get_tools()

    mutual_fund_etf_tools = [
        tool
        for tool in all_tools
        if tool.name in MUTUAL_FUND_ETF_TOOL_NAMES
    ]

    return mutual_fund_etf_tools