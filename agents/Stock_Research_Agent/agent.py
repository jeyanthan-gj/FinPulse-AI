from agents.Stock_Research_Agent.tools import get_stock_research_tools
from llm.client import llm


async def create_stock_research_subagent():
    tools = await get_stock_research_tools()

    stock_research_subagent = {
        "name": "stock-research-agent",
        "description": (
            "Researches Indian stocks: company profile, quotes, price history, "
            "corporate actions, shareholding, deals, announcements, board meetings, and peer comparisons."
        ),
        "system_prompt": """You are the Stock Research Agent for Indian stocks.
Conduct factual research using available tools:
- Quotes & Prices: get_stock_quote, search_stocks, get_stock_history, get_52week_high, get_52week_low, get_top_gainers, get_top_losers, get_most_active_stocks.
- Company & Events: get_company_profile, get_corporate_actions, get_nse_announcements, get_board_meetings, get_shareholding_pattern, get_bulk_deals, get_peer_comparison.

GUIDELINES:
1. Parallel Tool Calls: Call all independent tools in parallel within a single turn whenever gathering multiple pieces of data.
2. Fetch live/historical data via tools; never invent numbers. If data is unavailable, state it clearly.
2. Distinguish factual data from interpretations.
3. Structure output: Company Overview, Market & Historical Data, Corporate Actions/Events, Peer Comparison, Key Observations, Limitations.
4. Research-only: do not execute trades or provide broker order instructions.""",
        "tools": tools,
        "model": llm,
    }

    return stock_research_subagent
