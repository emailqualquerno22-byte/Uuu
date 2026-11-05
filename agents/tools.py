"""Tool registry for the agent harness.

Provides a unified interface for tool calling across providers.
Tools are registered with name, description, input schema, and a callable.
"""
import os
import subprocess
import datetime
import json
import urllib.request
import urllib.error
from typing import Any, Callable, Optional


class Tool:
    def __init__(self, name: str, description: str, fn: Callable, input_schema: dict = None):
        self.name = name
        self.description = description
        self.fn = fn
        self.input_schema = input_schema or {"type": "object", "properties": {}}

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    def __call__(self, **kwargs) -> str:
        try:
            result = self.fn(**kwargs)
            return str(result) if result is not None else "OK"
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"


def _read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def _write_file(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return f"Wrote {len(content)} bytes to {path}"


def _shell(cmd: str) -> str:
    try:
        result = subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.STDOUT, timeout=60
        )
        return result
    except subprocess.TimeoutExpired:
        return "ERROR: command timed out after 60s"
    except Exception as e:
        return f"ERROR: {e}"


def _web_fetch(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            # crude HTML tag strip
            import re
            text = re.sub(r"<[^>]+>", " ", content)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:4000]
    except Exception as e:
        return f"ERROR: {e}"


def _date_now() -> str:
    return datetime.datetime.now().isoformat()


def _list_dir(path: str = ".") -> str:
    try:
        entries = sorted(os.listdir(path))
        return "\n".join(entries)
    except Exception as e:
        return f"ERROR: {e}"


def _grep(pattern: str, path: str = ".") -> str:
    try:
        result = subprocess.check_output(
            ["grep", "-rn", pattern, path], text=True, stderr=subprocess.STDOUT, timeout=30
        )
        return result[:4000]
    except subprocess.CalledProcessError as e:
        return e.output if e.output else "no matches"
    except Exception as e:
        return f"ERROR: {e}"


TOOL_REGISTRY: dict[str, Tool] = {
    "read_file": Tool(
        "read_file",
        "Read the contents of a file from the filesystem.",
        _read_file,
        {"type": "object", "properties": {"path": {"type": "string", "description": "File path to read"}},
         "required": ["path"]},
    ),
    "write_file": Tool(
        "write_file",
        "Write content to a file on the filesystem. Creates parent directories as needed.",
        _write_file,
        {"type": "object", "properties": {"path": {"type": "string", "description": "File path to write"},
                                          "content": {"type": "string", "description": "Content to write"}},
         "required": ["path", "content"]},
    ),
    "shell": Tool(
        "shell",
        "Execute a shell command and return its output. Use for running scripts, git, curl, etc.",
        _shell,
        {"type": "object", "properties": {"cmd": {"type": "string", "description": "Shell command to execute"}},
         "required": ["cmd"]},
    ),
    "web_fetch": Tool(
        "web_fetch",
        "Fetch a URL and return the text content (HTML stripped).",
        _web_fetch,
        {"type": "object", "properties": {"url": {"type": "string", "description": "URL to fetch"}},
         "required": ["url"]},
    ),
    "date": Tool(
        "date",
        "Return the current date and time in ISO format.",
        _date_now,
        {"type": "object", "properties": {}},
    ),
    "list_dir": Tool(
        "list_dir",
        "List files and directories at a given path.",
        _list_dir,
        {"type": "object", "properties": {"path": {"type": "string", "description": "Directory path (default: current dir)"}},
         "required": []},
    ),
    "grep": Tool(
        "grep",
        "Search for a pattern in files under a directory. Returns matching lines with file names.",
        _grep,
        {"type": "object", "properties": {"pattern": {"type": "string", "description": "Regex pattern to search"},
                                          "path": {"type": "string", "description": "Directory to search (default: .)"}},
         "required": ["pattern"]},
    ),
}


def get_tools_for_provider(provider: str) -> list[dict]:
    """Return tool definitions formatted for the given provider."""
    if provider == "anthropic":
        return [t.to_dict() for t in TOOL_REGISTRY.values()]
    elif provider == "openai":
        return [
            {"type": "function", "function": {
                "name": t.name, "description": t.description,
                "parameters": t.input_schema}}
            for t in TOOL_REGISTRY.values()
        ]
    elif provider == "ollama":
        # Ollama uses a different tool format
        return [
            {"type": "function", "function": {
                "name": t.name, "description": t.description,
                "parameters": t.input_schema}}
            for t in TOOL_REGISTRY.values()
        ]
    return []


def execute_tool(name: str, **kwargs) -> str:
    tool = TOOL_REGISTRY.get(name)
    if not tool:
        return f"ERROR: unknown tool '{name}'"
    return tool(**kwargs)