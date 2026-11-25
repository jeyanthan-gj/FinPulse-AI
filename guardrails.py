import re
from typing import Optional


# Exact canonical user intents (0-token, 0ms latency)
GREETINGS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "namaste",
    "hi there",
    "hello there",
    "hola",
}

GRATITUDE = {
    "thanks",
    "thank you",
    "thank u",
    "thx",
    "bye",
    "goodbye",
    "see you",
}

CAPABILITIES = {
    "help",
    "what can you do",
    "who are you",
    "capabilities",
    "what are your tools",
    "menu",
}

OFF_TOPIC_KEYWORDS = [
    "write a poem",
    "write me a story",
    "snake game",
    "capital of",
    "bake a cake",
    "recipe for",
    "translate to french",
]


class MarketGuardrails:
    """
    Zero-token guardrails engine aligned with Colang flows:
    Intercepts greetings, civilities, and off-topic requests
    before calling the multi-agent supervisor.
    """

    @staticmethod
    def check_input_rails(prompt: str) -> Optional[str]:
        if not prompt or not prompt.strip():
            return "Please provide a research question or stock symbol."

        clean = re.sub(r"[^\w\s]", "", prompt).strip().lower()

        # 1. Greeting Flow
        if clean in GREETINGS:
            return (
                "Hello! I am your Indian Market Research AI Assistant. "
                "I can help you analyze Indian stocks, financial fundamentals, "
                "technicals, option chains (PCR/OI), mutual funds, and commodities. "
                "Which asset or company would you like to research today?"
            )

        # 2. Gratitude / Farewell Flow
        if clean in GRATITUDE:
            return "You're welcome! Let me know whenever you need further research on Indian markets."

        # 3. Capabilities / Help Flow
        if clean in CAPABILITIES:
            return (
                "I am an enterprise Indian Market Research Assistant powered by Deep Agents + MCP.\n\n"
                "Available Capabilities:\n"
                "• Stock Research: Quotes, history, corporate actions, bulk deals, announcements\n"
                "• Fundamental Analysis: Balance sheets, P&L, cash flows, key valuation ratios\n"
                "• Technical Analysis: Moving averages, RSI, MACD, support/resistance, candlestick patterns\n"
                "• Derivatives (F&O): Live option chains, Put-Call Ratio (PCR), Max Pain, Futures\n"
                "• Mutual Funds & ETFs: NAV history, fund comparison, category ranking, SIP returns\n"
                "• Market Intelligence: FII/DII activity, index performance, sector trends, market news"
            )

        # 4. Off-Topic Flow
        for pattern in OFF_TOPIC_KEYWORDS:
            if pattern in clean:
                return (
                    "I am specialized strictly in Indian Financial Market Research. "
                    "I cannot assist with general coding, creative writing, or non-financial tasks. "
                    "Please ask a question related to Indian equities, derivatives, mutual funds, or commodities."
                )

        return None
