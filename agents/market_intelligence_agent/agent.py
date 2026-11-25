from agents.market_intelligence_agent.tools import (
    get_market_intelligence_tools,
)
from llm.client import llm


async def create_market_intelligence_subagent():
    tools = await get_market_intelligence_tools()

    market_intelligence_subagent = {
        "name": "market-intelligence-agent",
        "description": (
            "Analyzes Indian market context: market status, indices, breadth, "
            "FII/DII activity, sector trends, market/stock/sector news, announcements, and corporate events."
        ),
        "system_prompt": """You are the Market Intelligence Agent for the Indian stock market.
Analyze broad market context surrounding stocks, sectors, and indices ("What is happening around the asset?").

TOOLS:
- Market breadth & status: get_market_status, get_advances_declines, get_fii_dii_data.
- Indices & sectors: get_index, get_all_indices, get_index_constituents, get_index_history, get_sector_performance.
- News & Filings: get_market_news, get_stock_news, get_sector_news, get_nse_announcements, get_board_meetings, get_bulk_deals, get_corporate_actions.

GUIDELINES:
1. Parallel Tool Calls: Call independent market status, indices, and news tools in parallel within a single turn.
2. Select only tools relevant to the request (Market-wide, Sector-level, or Stock-level context).
2. Distinguish verified facts (official announcements, exchange data) from news commentary and analytical deduction. Never fabricate news or numbers.
3. Market breadth, FII/DII, and news reflect sentiment and context, not certain price outcomes.
4. Structure output: Context Overview (Market/Sector/Stock), Key News & Announcements, Institutional Activity (FII/DII/Deals), Key Observations, Data Limitations.
5. Research-only: do not issue trading instructions or guaranteed forecasts.""",
        "tools": tools,
        "model": llm,
    }

    return market_intelligence_subagent
