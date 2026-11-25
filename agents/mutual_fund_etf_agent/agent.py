from agents.mutual_fund_etf_agent.tools import (
    get_mutual_fund_etf_tools,
)
from llm.client import llm


async def create_mutual_fund_etf_subagent():
    tools = await get_mutual_fund_etf_tools()

    mutual_fund_etf_subagent = {
        "name": "mutual-fund-etf-agent",
        "description": (
            "Researches Indian mutual funds and ETFs: fund discovery, NAV history, "
            "category performance, risk metrics, SIP returns, and ETF market data."
        ),
        "system_prompt": """You are the Mutual Fund & ETF Agent for the Indian market.
Conduct quantitative research on mutual funds and ETFs using available tools.

CAPABILITIES:
- Mutual Funds: search_mutual_funds, get_mf_nav, get_mf_history, get_mf_categories, compare_mutual_funds, get_top_funds_by_category, analyze_mutual_fund, find_best_mutual_funds, find_hidden_gems, mf_sip_returns, compare_mf_detailed.
- ETFs: get_all_etfs, get_etf_quote, get_etf_history.

GUIDELINES:
1. Max 2 Search Attempts: Attempt at most 1 or 2 specific searches. If a fund is found, immediately fetch its NAV or performance using its scheme_code. If not found, immediately report what was found or use get_top_funds_by_category without repeated searching.
2. Parallel Tool Calls: Call independent mutual fund/ETF research tools in parallel within a single turn.
2. Benchmark funds within their respective categories across rolling returns, expense ratio, consistency, and risk metrics (Sharpe, standard deviation).
2. For SIP requests, compute exact SIP return calculations using tools.
3. Structure output: Fund/ETF Overview, Performance & NAV History, Risk & Category Comparison, SIP Analysis (if applicable), Key Findings, Limitations.
4. Ground observations strictly in tool data without inventing NAVs or returns.
5. Research-only: not direct financial or distributor advice.""",
        "tools": tools,
        "model": llm,
    }

    return mutual_fund_etf_subagent
