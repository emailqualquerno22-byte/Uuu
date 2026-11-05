#!/usr/bin/env python3
"""MCP server providing filesystem read/write/list tools.

Run with: python mcp_servers/filesystem_server.py
Transport: stdio (Model Context Protocol)
"""

from __future__ import annotations

import os
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)


def _resolve(path: str) -> Path:
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = Path(os.getcwd()) / p
    return p.resolve()


def _safe_path(path: str) -> Path:
    p = _resolve(path)
    allowed = [Path(os.getcwd()).resolve(), Path("/tmp").resolve()]
    for root in allowed:
        try:
            p.relative_to(root)
            return p
        except ValueError:
            continue
    raise ValueError(f"Path {path} is outside allowed roots")


async def _list_tools_handler(ctx, params) -> ListToolsResult:
    return ListToolsResult(
        tools=[
            Tool(
                name="read_file",
                description="Read the contents of a file at the given path. "
                "Returns the file contents as text.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Absolute or relative file path"},
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="write_file",
                description="Write text content to a file, creating parent directories as needed. "
                "Returns the number of bytes written.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to write"},
                        "content": {"type": "string", "description": "Text content to write"},
                    },
                    "required": ["path", "content"],
                },
            ),
            Tool(
                name="list_directory",
                description="List files and subdirectories in a directory.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"},
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="file_exists",
                description="Check whether a file or directory exists.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to check"},
                    },
                    "required": ["path"],
                },
            ),
        ]
    )


async def _call_tool_handler(ctx, params) -> CallToolResult:
    args = params.arguments or {}
    name = params.name
    try:
        if name == "read_file":
            p = _safe_path(args["path"])
            if not p.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"ERROR: file not found: {p}")]
                )
            return CallToolResult(
                content=[TextContent(type="text", text=p.read_text(encoding="utf-8", errors="replace"))]
            )

        elif name == "write_file":
            p = _safe_path(args["path"])
            p.parent.mkdir(parents=True, exist_ok=True)
            data = args["content"]
            if isinstance(data, str):
                data = data.encode("utf-8")
            p.write_bytes(data)
            return CallToolResult(
                content=[TextContent(type="text", text=f"OK: wrote {len(data)} bytes to {p}")]
            )

        elif name == "list_directory":
            p = _safe_path(args["path"])
            if not p.is_dir():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"ERROR: not a directory: {p}")]
                )
            entries = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            lines = []
            for e in entries:
                kind = "DIR " if e.is_dir() else "FILE"
                size = "" if e.is_dir() else f" ({e.stat().st_size} bytes)"
                lines.append(f"{kind} {e.name}{size}")
            return CallToolResult(
                content=[TextContent(type="text", text="\n".join(lines) or "(empty)")]
            )

        elif name == "file_exists":
            p = _safe_path(args["path"])
            return CallToolResult(
                content=[TextContent(type="text", text=f"exists={p.exists()} path={p}")]
            )

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
    "filesystem-server",
    on_list_tools=_list_tools_handler,
    on_call_tool=_call_tool_handler,
)


async def main() -> None:
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())