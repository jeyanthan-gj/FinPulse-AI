import aiosqlite
from deepagents import create_deep_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from llm.client import llm

from agents.Stock_Research_Agent.agent import create_stock_research_subagent
from agents.fundamental_analysis_agent.agent import create_fundamental_analysis_subagent
from agents.technical_analysis_agent.agent import create_technical_analysis_subagent
from agents.stock_screening_agent.agent import create_stock_screening_subagent
from agents.f_and_o_analysis_agent.agent import create_f_and_o_analysis_subagent
from agents.mutual_fund_etf_agent.agent import create_mutual_fund_etf_subagent
from agents.market_intelligence_agent.agent import create_market_intelligence_subagent
from agents.macro_alternative_assets_agent.agent import create_macro_alternative_assets_subagent

DB_PATH = "market_research.db"


async def create_research_synthesis_supervisor():
    """
    Research Synthesis Supervisor: delegates specialized tasks to subagents
    and synthesizes results into clear, evidence-based research reports.
    Persists conversational state and checkpoints in SQLite database asynchronously.
    """
    specialist_subagents = [
        await create_stock_research_subagent(),
        await create_fundamental_analysis_subagent(),
        await create_technical_analysis_subagent(),
        await create_stock_screening_subagent(),
        await create_f_and_o_analysis_subagent(),
        await create_mutual_fund_etf_subagent(),
        await create_market_intelligence_subagent(),
        await create_macro_alternative_assets_subagent(),
    ]

    supervisor_prompt = """You are the Research Synthesis Supervisor for Indian Market Research AI.
Coordinate specialist subagents via task calls and synthesize findings into high-quality research reports.

SPECIALISTS:
- stock-research-agent: Company profile, quotes, historical prices, corporate actions, shareholding, announcements, bulk deals, board meetings, peer comparison.
- fundamental-analysis-agent: Financial statements (P&L, Balance Sheet, Cash Flow), key ratios, margins, growth, debt, valuation, fundamental screening.
- technical-analysis-agent: Price action, trends, indicators (RSI, MACD, MAs, Bollinger), support/resistance, candlestick patterns.
- stock-screening-agent: Filter stocks by price/volume, 52w high/low, gainers/losers, preset screens, fundamental criteria.
- f-and-o-analysis-agent: Derivatives, option chains, PCR, Max Pain, futures data, OI analysis.
- mutual-fund-etf-agent: MF discovery, NAV history, category ranking, SIP returns, comparison, ETF quotes/history.
- market-intelligence-agent: Market status/breadth, FII/DII activity, indices, sector performance, market/stock/sector news.
- macro-alternative-assets-agent: Commodities (Gold, Silver, Crude), currencies (USDINR), IPOs, SGBs.

DELEGATION GUIDELINES:
1. Selective Routing: Call only relevant subagents for the query. For mutual funds, invoke ONLY mutual-fund-etf-agent. Do not invoke market-intelligence-agent or equity agents unless specifically requested. Do not invoke all agents unnecessarily.
2. Sequential Workflows: If screening or discovery is required first, obtain candidate tickers before dispatching deep technical or fundamental tasks.
3. Parallel Tasks: Run independent specialist tasks in parallel within the same turn.
4. Minimal Focused Context: Pass only essential parameters (ticker, timeframe, specific focus) to subagents.

SYNTHESIS & REPORTING:
- Integrate findings logically; do not dump raw subagent outputs.
- Ground conclusions strictly in data retrieved by subagents. Never fabricate market numbers or predict guaranteed returns.
- Reconcile differences or explicitly state uncertainties and data limitations.
- Provide a structured response: Research Objective, Findings / Evidence, Key Risks, and Conclusion.
- Strictly research and analysis: never execute trades or provide broker order instructions."""

    conn = await aiosqlite.connect(DB_PATH)
    checkpointer = AsyncSqliteSaver(conn)
    await checkpointer.setup()

    research_synthesis_supervisor = create_deep_agent(
        model=llm,
        system_prompt=supervisor_prompt,
        subagents=specialist_subagents,
        checkpointer=checkpointer,
        name="research-synthesis-supervisor",
    )

    return research_synthesis_supervisor
