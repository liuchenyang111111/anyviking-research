from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class SearchResult:
    """Normalized result returned by a retriever."""

    title: str
    uri: str
    snippet: str
    score: float | None = None
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Retriever(Protocol):
    """Small retrieval interface used by workflows and agents."""

    def search(
        self,
        query: str,
        scope: str | None = None,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Search a corpus and return normalized results."""
        ...
