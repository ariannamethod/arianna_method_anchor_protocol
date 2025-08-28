"""Lightweight in-memory vector engine used for tests.

This replaces the old ``utils.vector_engine`` dependency and simply stores
added memories in a list. It provides an async ``add_memory`` method matching
previous behaviour expected by the rest of the codebase.
"""

from __future__ import annotations

from typing import Any, Dict, List


class IndianaVectorEngine:
    """Minimal stub vector engine.

    Memories are kept in ``memory`` for inspection during tests.
    """

    def __init__(self) -> None:
        self._memory: List[Dict[str, Any]] = []

    async def add_memory(self, kind: str, content: str, role: str | None = None) -> None:
        """Store a memory entry in-memory."""
        self._memory.append({"kind": kind, "content": content, "role": role})

    @property
    def memory(self) -> List[Dict[str, Any]]:
        """Return stored memories."""
        return self._memory
