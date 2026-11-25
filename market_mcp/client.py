import asyncio
import json
import os

from langchain_core.tools import StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient


MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")


def _sanitize_tool(tool: StructuredTool) -> StructuredTool:
    """
    Wraps an MCP tool to ensure that empty content (like [] or {})
    is converted to a valid JSON string ('[]' or '{}').
    This prevents providers like Groq/OpenAI from throwing 400 Bad Request:
    'for role:tool content must be a non-empty string or array'.
    """
    orig_coro = tool.coroutine

    async def _safe_coroutine(*args, **kwargs):
        res = await orig_coro(*args, **kwargs)
        if isinstance(res, tuple) and len(res) == 2:
            content, artifact = res
            if not content:
                # If content is empty list/dict, stringify artifact or default to '[]'
                if artifact and isinstance(artifact, dict) and "structured_content" in artifact:
                    content = json.dumps(artifact["structured_content"].get("result", []))
                else:
                    content = "[]"
            elif isinstance(content, (dict, list)):
                content = json.dumps(content)
            elif not isinstance(content, str):
                content = str(content)
            return content, artifact

        if res is None or res == [] or res == {}:
            return "[]"
        if isinstance(res, (dict, list)):
            return json.dumps(res)
        return str(res)

    return StructuredTool(
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
        coroutine=_safe_coroutine,
        response_format=getattr(tool, "response_format", "content_and_artifact"),
    )


class MarketMCPClient:
    """
    Reusable MCP client for the Indian Market MCP server.

    Caches loaded tools and shares a single client instance
    so all agents avoid redundant network round-trips.
    """

    _instance = None
    _cached_tools = None
    _lock = asyncio.Lock()

    def __new__(cls, url: str = MCP_URL):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.url = url
            cls._instance.client = MultiServerMCPClient(
                {
                    "indian_market": {
                        "url": url,
                        "transport": "streamable_http",
                    }
                }
            )
        return cls._instance

    async def get_tools(self):
        """
        Load all available MCP tools as LangChain tools with thread-safe caching
        and content sanitization.
        """
        if self._cached_tools is not None:
            return self._cached_tools

        async with self._lock:
            if self._cached_tools is None:
                raw_tools = await self.client.get_tools()
                self._cached_tools = [_sanitize_tool(t) for t in raw_tools]

        return self._cached_tools
