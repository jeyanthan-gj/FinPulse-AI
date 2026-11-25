from market_mcp.client import MarketMCPClient


MACRO_ALTERNATIVE_ASSETS_TOOL_NAMES = {
    "get_commodity_price",
    "get_all_commodity_prices",
    "get_commodity_history",
    "get_currency_rate",
    "get_all_currency_rates",
    "get_currency_history",
    "get_upcoming_ipos",
    "get_past_ipos",
    "get_sovereign_gold_bonds",
    "get_sgb_quote",
    "get_sgb_history",
}


async def get_macro_alternative_assets_tools():
    """
    Get the tools assigned to the Macro & Alternative Assets Agent.
    """

    client = MarketMCPClient()

    all_tools = await client.get_tools()

    macro_alternative_assets_tools = [
        tool
        for tool in all_tools
        if tool.name in MACRO_ALTERNATIVE_ASSETS_TOOL_NAMES
    ]

    return macro_alternative_assets_tools