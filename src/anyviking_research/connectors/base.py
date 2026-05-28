from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class WebSearchResult:
    """Normalized public-web search result."""

    title: str
    url: str
    description: str = ""
    content: str = ""
    source: str | None = None
    score: float | None = None
    quality_score: float | None = None
    published_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WebSearchResponse:
    """Normalized response returned by an upstream web search connector."""

    query: str
    provider: str
    results: list[WebSearchResult]
    metadata: dict[str, Any] = field(default_factory=dict)


class WebSearchConnector(Protocol):
    """Small interface for upstream public-web discovery."""

    def search(self, query: str, *, max_results: int = 10) -> WebSearchResponse:
        """Search the public web and return normalized results."""
        ...
