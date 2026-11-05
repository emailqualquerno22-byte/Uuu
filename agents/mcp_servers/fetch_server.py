"""MCP fetch server — provides web fetch operations via Model Context Protocol.

Handles:
- fetch_url: fetch a URL and return the text content
"""
import json
import os
import sys
import re
import urllib.request
import urllib.error
from http import HTTPStatus


def handle_client(stdin, stdout):
    """Read JSON-RPC messages from stdin, respond via stdout."""
    request_id = 0
    while True:
        line = stdin.readline()
        if not line:
            break
        try:
            msg = json.loads(line.strip())
        except json.JSONDecodeError:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32600, "message": "Invalid JSON"},
            }
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()
            continue

        method = msg.get("method", "")
        req_id = msg.get("id")

        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "fetch-mcp", "version": "1.0.0"},
                },
            }
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()

        elif method == "initialized":
            pass

        elif method == "tools/list":
            tools = [
                {
                    "name": "fetch_url",
                    "description": "Fetch a URL and return text content",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"url": {"type": "string"}},
                        "required": ["url"],
                    },
                },
            ]
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": tools},
            }
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()

        elif method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = handle_tool(tool_name, arguments)
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result,
            }
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()

        else:
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method {method} not found"},
            }
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()


def handle_tool(name: str, args: dict) -> dict:
    """Execute the requested tool and return a JSON-serializable result."""
    url = args.get("url", "")
    try:
        if name == "fetch_url":
            if not url.startswith(("http://", "https://")):
                return {"error": "URL must start with http:// or https://"}
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                # try to get charset from headers
                charset = resp.headers.get_content_charset() or "utf-8"
                content = resp.read().decode(charset, errors="replace")
                # strip HTML tags (basic)
                text = re.sub(r"<[^>]+>", " ", content)
                text = re.sub(r"\s+", " ", text).strip()
                # limit size
                if len(text) > 5000:
                    text = text[:5000] + "... [truncated]"
                return {"content": text}

        return {"error": f"unknown fetch tool: {name}"}

    except Exception as e:
        return {"error": f"fetch failed: {type(e).__name__}: {e}"}


if __name__ == "__main__":
    handle_client(sys.stdin, sys.stdout)