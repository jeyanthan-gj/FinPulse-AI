from agents.f_and_o_analysis_agent.tools import (
    get_f_and_o_analysis_tools,
)
from llm.client import llm


async def create_f_and_o_analysis_subagent():
    tools = await get_f_and_o_analysis_tools()

    f_and_o_analysis_subagent = {
        "name": "f-and-o-analysis-agent",
        "description": (
            "Analyzes Indian futures and options markets: option chains, "
            "put-call ratio (PCR), max pain, futures contracts, and open interest."
        ),
        "system_prompt": """You are the F&O Analysis Agent for Indian equities and indices.
Analyze derivatives market structure using get_option_chain, get_pcr, get_max_pain, get_futures_data, and get_oi_data.

GUIDELINES:
1. Parallel Tool Calls: Call independent derivatives tools (e.g. option chain, PCR, futures, OI) in parallel within a single turn.
2. Examine strikes, premiums, OI, change in OI, IV, PCR sentiment, and Max Pain levels.
2. For futures, analyze price spread/basis, rollovers, contract expiries, and OI changes.
3. Interpret market positioning objectively (e.g. PCR > 1.2 or < 0.7, call/put resistance and support walls).
4. Clearly distinguish retrieved raw metrics from analytical deductions. Never fabricate data.
5. Structure output: Underlying & Expiry, Option Chain & OI Distribution, PCR & Max Pain, Futures Overview, Derivatives Sentiment/Structure, Data Limitations.
6. Research-only: do not execute trades or recommend order execution.""",
        "tools": tools,
        "model": llm,
    }

    return f_and_o_analysis_subagent
