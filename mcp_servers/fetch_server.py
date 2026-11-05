#!/usr/bin/env python3
"""MCP server providing web fetch and search tools.

Run with: python mcp_servers/fetch_server.py
Transport: stdio (Model Context Protocol)
"""

from __future__ import annotations

import json
import re
from typing import Any

import aiohttp
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

USER_AGENT = "KiloAgent/1.0 (+https://kilo.ai)"


async def _fetch_url(url: str, max_chars: int = 8000) -> str:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
        async with session.get(url, headers=headers, allow_redirects=True) as resp:
            resp.raise_for_status()
            ctype = resp.headers.get("Content-Type", "")
            raw = await resp.read()
            if "html" in ctype.lower() or "xml" in ctype.lower():
                text = _strip_html(raw.decode("utf-8", errors="replace"))
            else:
                text = raw.decode("utf-8", errors="replace")
            return text[:max_chars]


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<!--.*?-->", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _ddg_search(query: str, max_results: int) -> list[dict]:
    url = "https://html.duckduckgo.com/html/"
    try:
        r = requests.post(url, data={"q": query}, headers={"User-Agent": USER_AGENT}, timeout=15)
        r.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return [{"error": f"search request failed: {exc}"}]
    results = []
    for m in re.finditer(
        r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>',
        r.text,
        re.S,
    ):
        link, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        results.append({"title": title, "url": link})
        if len(results) >= max_results:
            break
    return results


async def _list_tools_handler(ctx, params) -> ListToolsResult:
    return ListToolsResult(
        tools=[
            Tool(
                name="web_fetch",
                description="Fetch a URL and return its content as readable text. "
                "HTML is stripped to plain text. Useful for reading web pages.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to fetch (http/https)"},
                        "max_chars": {"type": "integer", "description": "Max characters to return", "default": 8000},
                    },
                    "required": ["url"],
                },
            ),
            Tool(
                name="web_search",
                description="Search the web using DuckDuckGo and return a list of results "
                "(title, URL, snippet).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "max_results": {"type": "integer", "description": "Max results", "default": 5},
                    },
                    "required": ["query"],
                },
            ),
        ]
    )


async def _call_tool_handler(ctx, params) -> CallToolResult:
    args = params.arguments or {}
    name = params.name
    try:
        if name == "web_fetch":
            url = args["url"]
            max_chars = int(args.get("max_chars", 8000))
            text = await _fetch_url(url, max_chars)
            return CallToolResult(content=[TextContent(type="text", text=text)])

        elif name == "web_search":
            query = args["query"]
            max_results = int(args.get("max_results", 5))
            results = _ddg_search(query, max_results)
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(results, indent=2))])

        else:
            return CallToolResult(
                is_error=True,
                content=[TextContent(type="text", text=f"ERROR: unknown tool: {name}")],
            )

    except Exception as exc:  # noqa: BLE001
        return CallToolResult(
            is_error=True,
            content=[TextContent(type="text", text=f"ERROR: {type(exc).__name__}: {exc}")],
        )


app = Server(
    "fetch-server",
    on_list_tools=_list_tools_handler,
    on_call_tool=_call_tool_handler,
)


async def main() -> None:
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())