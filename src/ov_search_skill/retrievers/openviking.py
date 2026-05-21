from __future__ import annotations

from typing import Any
from urllib.parse import unquote

import httpx

from ov_search_skill.retrievers.base import SearchResult


class OpenVikingRetriever:
    """Retriever backed by OpenViking's HTTP search API."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:1933",
        mode: str = "find",
        timeout: float = 60.0,
    ) -> None:
        if mode not in {"find", "search"}:
            raise ValueError("mode must be 'find' or 'search'")
        self.base_url = base_url.rstrip("/")
        self.mode = mode
        self.timeout = timeout

    def search(
        self,
        query: str,
        scope: str | None = None,
        top_k: int = 5,
    ) -> list[SearchResult]:
        if not query.strip():
            raise ValueError("query must not be empty")
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        payload: dict[str, Any] = {
            "query": query,
            "target_uri": scope or "",
            "limit": top_k,
        }
        endpoint = f"{self.base_url}/api/v1/search/{self.mode}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(endpoint, json=payload)
                response.raise_for_status()
        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Could not connect to OpenViking. Start openviking-server and "
                f"check {self.base_url}/health."
            ) from exc
        except httpx.HTTPStatusError as exc:
            body = exc.response.text.strip()
            detail = f" Body: {body[:500]}" if body else ""
            raise RuntimeError(f"OpenViking search request failed: {exc}.{detail}") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"OpenViking search request failed: {exc}") from exc

        data = response.json()
        if data.get("status") not in {None, "ok"}:
            raise RuntimeError(f"OpenViking returned non-ok response: {data}")

        result = data.get("result", data)
        contexts = self._flatten_contexts(result)
        return [self._to_search_result(ctx) for ctx in contexts[:top_k]]

    @staticmethod
    def _flatten_contexts(result: dict[str, Any]) -> list[dict[str, Any]]:
        contexts: list[dict[str, Any]] = []
        for group in ("resources", "memories", "skills"):
            items = result.get(group) or []
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        contexts.append({**item, "_group": group})

        contexts.sort(
            key=lambda item: item.get("score") if item.get("score") is not None else 0.0,
            reverse=True,
        )
        return contexts

    @staticmethod
    def _to_search_result(ctx: dict[str, Any]) -> SearchResult:
        uri = str(ctx.get("uri") or "")
        snippet = (
            str(ctx.get("abstract") or "").strip()
            or str(ctx.get("overview") or "").strip()
            or str(ctx.get("match_reason") or "").strip()
        )
        return SearchResult(
            title=OpenVikingRetriever._title_from_uri(uri),
            uri=uri,
            snippet=snippet,
            score=OpenVikingRetriever._score(ctx.get("score")),
            source="openviking",
            metadata={
                "context_type": ctx.get("context_type"),
                "level": ctx.get("level"),
                "category": ctx.get("category"),
                "match_reason": ctx.get("match_reason"),
                "group": ctx.get("_group"),
                "relations": ctx.get("relations") or [],
            },
        )

    @staticmethod
    def _title_from_uri(uri: str) -> str:
        if not uri:
            return "(untitled)"
        tail = uri.rstrip("/").rsplit("/", 1)[-1]
        tail = unquote(tail)
        if tail.endswith(".md"):
            tail = tail[:-3]
        return tail or uri

    @staticmethod
    def _score(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
