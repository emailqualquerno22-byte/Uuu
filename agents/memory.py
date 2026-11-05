"""Memory management for the agent harness.

Implements session-level memory with compression and progressive disclosure.
Stores conversation history, tool results, and learned facts.
"""
import json
import os
import datetime
from typing import Any


class Memory:
    """Simple session memory with compression and persistence."""

    def __init__(self, persist_path: str | None = None):
        self.history: list[dict] = []
        self.facts: dict[str, Any] = {}
        self.persist_path = persist_path
        if persist_path and os.path.exists(persist_path):
            self._load()

    def add(self, role: str, content: str, **metadata) -> None:
        entry = {"role": role, "content": content, "timestamp": datetime.datetime.now().isoformat()}
        entry.update(metadata)
        self.history.append(entry)
        # keep only last 50 entries in active memory
        if len(self.history) > 50:
            self.history = self.history[-50:]

    def add_fact(self, key: str, value: Any) -> None:
        self.facts[key] = value

    def get_facts(self) -> str:
        if not self.facts:
            return ""
        return "Known facts:\n" + "\n".join(f"  {k}: {v}" for k, v in self.facts.items())

    def summarize(self) -> str:
        """Return a compressed summary of recent history."""
        if not self.history:
            return "(empty)"
        recent = self.history[-10:]
        lines = []
        for entry in recent:
            role = entry["role"]
            content = entry["content"]
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append(f"  [{role}] {content}")
        return "\n".join(lines)

    def save(self) -> None:
        if self.persist_path:
            os.makedirs(os.path.dirname(os.path.abspath(self.persist_path)), exist_ok=True)
            data = {"history": self.history, "facts": self.facts,
                    "saved": datetime.datetime.now().isoformat()}
            with open(self.persist_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

    def _load(self) -> None:
        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)
            self.history = data.get("history", [])
            self.facts = data.get("facts", {})
        except Exception:
            pass

    def clear(self) -> None:
        self.history = []
        self.facts = {}
        if self.persist_path and os.path.exists(self.persist_path):
            os.remove(self.persist_path)