"""MCP filesystem server — provides filesystem operations via Model Context Protocol.

Commands are sent from the agent via MCP protocol. This server handles:
- read_file: read file contents
- write_file: write file contents  
- list_dir: list directory entries
- mkdir: create directory
- rm: remove file
"""
import json
import os
import sys
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
            # send error response
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
                    "capabilities": {"tools": {}],
                    "serverInfo": {"name": "filesystem-mcp", "version": "1.0.0"},
                },
            }
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()

        elif method == "initialized":
            # notification, no response needed
            pass

        elif method == "tools/list":
            tools = [
                {
                    "name": "read_file",
                    "description": "Read file contents",
                    "inputSchema": {
                        "type": "object", "properties": {"path": {"type": "string"}},
                        "required": ["path"],
                    },
                },
                {
                    "name": "write_file",
                    "description": "Write file contents",
                    "inputSchema": {
                        "type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                        "required": ["path", "content"],
                    },
                },
                {
                    "name": "list_dir",
                    "description": "List directory entries",
                    "inputSchema": {
                        "type": "object", "properties": {"path": {"type": "string", "default": "."}},
                        "required": [],
                    },
                },
                {
                    "name": "mkdir",
                    "description": "Create directory",
                    "inputSchema": {
                        "type": "object", "properties": {"path": {"type": "string"}},
                        "required": ["path"],
                    },
                },
                {
                    "name": "rm",
                    "description": "Remove file or empty directory",
                    "inputSchema": {
                        "type": "object", "properties": {"path": {"type": "string"}},
                        "required": ["path"],
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
    path = args.get("path", "")
    try:
        if name == "read_file":
            if not os.path.exists(path):
                return {"error": f"path not found: {path}"}
            with open(path, "r") as f:
                content = f.read()
            return {"content": content}

        elif name == "write_file":
            content = args.get("content", "")
            os.makedirs(os.path.dirname(os.path.abspath(path)) if os.path.dirname(path) else ".", exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return {"status": "ok", "message": f"Wrote {len(content)} bytes to {path}"}

        elif name == "list_dir":
            base = path or "."
            if not os.path.isdir(base):
                return {"error": f"not a directory: {base}"}
            entries = sorted(os.listdir(base))
            return {"entries": entries}

        elif name == "mkdir":
            os.makedirs(path, exist_ok=True)
            return {"status": "ok", "message": f"Created directory {path}"}

        elif name == "rm":
            if os.path.isfile(path):
                os.remove(path)
                return {"status": "ok", "message": f"Removed {path}"}
            elif os.path.isdir(path):
                import shutil
                shutil.rmtree(path)
                return {"status": "ok", "message": f"Removed directory {path}"}
            else:
                return {"error": f"path not found: {path}"}

        else:
            return {"error": f"unknown tool: {name}"}

    except Exception as e:
        return {"error": f"tool execution failed: {type(e).__name__}: {e}"}


if __name__ == "__main__":
    handle_client(sys.stdin, sys.stdout)