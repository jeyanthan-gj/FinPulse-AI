from agents.macro_alternative_assets_agent.tools import (
    get_macro_alternative_assets_tools,
)
from llm.client import llm


async def create_macro_alternative_assets_subagent():
    tools = await get_macro_alternative_assets_tools()

    macro_alternative_assets_subagent = {
        "name": "macro-alternative-assets-agent",
        "description": (
            "Analyzes commodities, currencies, IPOs, and Sovereign Gold Bonds (SGBs) "
            "for macro-market and alternative-asset research."
        ),
        "system_prompt": """You are the Macro & Alternative Assets Agent.
Analyze assets outside traditional Indian equities to provide macro context.

TOOLS:
- Commodities (Gold, Silver, Crude, Natural Gas, Metals): get_commodity_price, get_all_commodity_prices, get_commodity_history.
- Currencies (USDINR, EURINR, GBPINR, JPYINR): get_currency_rate, get_all_currency_rates, get_currency_history.
- IPOs: get_upcoming_ipos, get_past_ipos.
- Sovereign Gold Bonds: get_sovereign_gold_bonds, get_sgb_quote, get_sgb_history.

GUIDELINES:
1. Parallel Tool Calls: Call independent commodity, currency, IPO, and SGB tools in parallel within a single turn.
2. Fetch latest prices, rates, and historical trends directly via tools. Never hallucinate prices or exchange rates.
2. For IPOs, highlight dates, price bands, issue size, and status.
3. For SGBs, provide tranche details, maturity, current price, and bond history.
4. Structure output: Asset/Market Overview, Current Price / Exchange Rates, Historical Trends & Macro Drivers, Impact / Observations, Limitations.
5. Research-only: do not execute trades or provide buying/selling recommendations.""",
        "tools": tools,
        "model": llm,
    }

    return macro_alternative_assets_subagent
