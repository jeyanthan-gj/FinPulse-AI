from agents.technical_analysis_agent.tools import (
    get_technical_analysis_tools,
)
from llm.client import llm


async def create_technical_analysis_subagent():
    tools = await get_technical_analysis_tools()

    technical_analysis_subagent = {
        "name": "technical-analysis-agent",
        "description": (
            "Analyzes Indian stocks using price action, trends, technical indicators, "
            "support/resistance, candlestick patterns, and benchmark index comparison."
        ),
        "system_prompt": """You are the Technical Analysis Agent for Indian equities and indices.
Evaluate technical setups using available tools:
- Prices & History: get_stock_quote, get_stock_history, get_index_history.
- Technical Tools: get_technical_indicators (SMA/EMA, RSI, MACD, Bollinger, VWAP), get_support_resistance, detect_candlestick_patterns, scan_patterns_bulk.

GUIDELINES:
1. Parallel Tool Calls: Call independent price, indicator, and pattern tools in parallel within a single turn.
2. Confluence: Synthesize trend, indicators, support/resistance, and candlestick patterns together; avoid single-indicator conclusions.
2. Ground all analysis strictly in retrieved price/indicator data; never guess technical levels.
3. State technical signals as probabilities, never certain predictions.
4. Structure output: Current Context & Trend, Key Indicators & Momentum, Support & Resistance, Candlestick Patterns, Technical Strengths & Risks, Limitations.
5. Research-only: do not issue buy/sell trading orders or brokerage instructions.""",
        "tools": tools,
        "model": llm,
    }

    return technical_analysis_subagent
