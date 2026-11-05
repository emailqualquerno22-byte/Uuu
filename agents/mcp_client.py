"""MCP (Model Context Protocol) client integration.

Allows the agent to discover and use tools from MCP servers.
Falls back gracefully if no MCP servers are configured.
"""
import json
import os
import subprocess
import sys
from typing import Any


class MCPClient:
    """Minimal MCP client that connects to servers via stdio."""

    def __init__(self, server_config: dict):
        self.config = server_config
        self.process = None
        self.tools = []
        self._request_id = 0

    def start(self) -> bool:
        cmd = self.config.get("command", "")
        args = self.config.get("args", [])
        env = dict(os.environ)
        env.update(self.config.get("env", {}))
        try:
            self.process = subprocess.Popen(
                [cmd] + args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1,
            )
            # initialize
            self._send({
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "kilo-agent", "version": "1.0.0"},
                },
            })
            resp = self._recv()
            if resp and "result" in resp:
                # send initialized
                self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
                self._load_tools()
                return True
        except Exception as e:
            print(f"MCP start failed for {self.config.get('name')}: {e}")
        return False

    def _send(self, msg: dict) -> None:
        if self.process and self.process.stdin:
            self.process.stdin.write(json.dumps(msg) + "\n")
            self.process.stdin.flush()

    def _recv(self) -> dict | None:
        if not self.process or not self.process.stdout:
            return None
        line = self.process.stdout.readline()
        if not line:
            return None
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return None

    def _load_tools(self) -> None:
        self._request_id += 1
        self._send({
            "jsonrpc": "2.0", "id": self._request_id, "method": "tools/list",
        })
        resp = self._recv()
        if resp and "result" in resp:
            self.tools = resp["result"].get("tools", [])

    def call_tool(self, name: str, arguments: dict) -> str:
        self._request_id += 1
        self._send({
            "jsonrpc": "2.0", "id": self._request_id, "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })
        resp = self._recv()
        if resp and "result" in resp:
            result = resp["result"]
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                if isinstance(content, list):
                    return "\n".join(
                        item.get("text", str(item)) if isinstance(item, dict) else str(item)
                        for item in content
                    )
                return str(content)
            return str(result)
        return f"ERROR: MCP tool '{name}' returned no result"

    def stop(self) -> None:
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass


def load_mcp_configs(config_path: str = "mcp_servers/config.json") -> list[MCPClient]:
    """Load MCP server configurations from a JSON file."""
    if not os.path.exists(config_path):
        return []
    try:
        with open(config_path, "r") as f:
            configs = json.load(f)
        clients = []
        # Support both dict-style {name: config} and list-style [{name: ..., ...}]
        if isinstance(configs, dict):
            items = [(name, cfg) for name, cfg in configs.items()]
        else:
            items = [(cfg.get("name", f"server-{i}"), cfg) for i, cfg in enumerate(configs)]
        for name, cfg in items:
            cfg = dict(cfg)  # copy
            cfg["name"] = name
            client = MCPClient(cfg)
            if client.start():
                clients.append(client)
                print(f"  MCP server connected: {name} ({len(client.tools)} tools)")
            else:
                print(f"  MCP server skipped: {name}")
        return clients
    except Exception as e:
        print(f"  MCP config load failed: {e}")
        return []


def mcp_tools_to_dict(clients: list[MCPClient]) -> list[dict]:
    """Convert all MCP tools to provider-compatible dicts."""
    tools = []
    for client in clients:
        for tool in client.tools:
            tools.append({
                "name": tool.get("name", "unknown"),
                "description": tool.get("description", ""),
                "input_schema": tool.get("inputSchema", {"type": "object", "properties": {}}),
            })
    return tools