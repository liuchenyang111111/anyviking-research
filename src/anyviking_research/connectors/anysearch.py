from __future__ import annotations

import os
from typing import Any

import httpx

from anyviking_research.connectors.base import WebSearchResponse, WebSearchResult


class AnySearchConnector:
    """Connector for the AnySearch public-web search API."""

    def __init__(
        self,
        *,
        base_url: str = "https://api.anysearch.com",
        api_key: str | None = None,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key if api_key is not None else os.environ.get("ANYSEARCH_API_KEY")
        self.timeout = timeout
        self.transport = transport

    def search(
        self,
        query: str,
        *,
        max_results: int = 10,
        domains: list[str] | None = None,
        tags: list[str] | None = None,
        content_types: list[str] | None = None,
        zone: str | None = None,
        language: str | None = None,
        providers: list[str] | None = None,
        freshness: str | None = None,
        from_time: str | None = None,
        to_time: str | None = None,
    ) -> WebSearchResponse:
        if not query.strip():
            raise ValueError("query must not be empty")
        if max_results <= 0 or max_results > 100:
            raise ValueError("max_results must be between 1 and 100")

        payload = _compact_dict(
            {
                "query": query,
                "max_results": max_results,
                "domains": domains,
                "tags": tags,
                "content_types": content_types,
                "zone": zone,
                "language": language,
                "providers": providers,
                "constraint": _compact_dict(
                    {
                        "freshness": freshness,
                        "from": from_time,
                        "to": to_time,
                    }
                ),
            }
        )
        if payload.get("constraint") == {}:
            payload.pop("constraint")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        endpoint = f"{self.base_url}/v1/search"
        try:
            with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
                response = client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text.strip()
            detail = f" Body: {body[:500]}" if body else ""
            raise RuntimeError(f"AnySearch request failed: {exc}.{detail}") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"AnySearch request failed: {exc}") from exc

        data = response.json()
        payload = data.get("data") if isinstance(data.get("data"), dict) else data
        raw_results = payload.get("results") or []
        if not isinstance(raw_results, list):
            raise RuntimeError(f"AnySearch returned invalid results payload: {data}")

        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        if "code" in data:
            metadata = {**metadata, "code": data.get("code")}
        if "message" in data:
            metadata = {**metadata, "message": data.get("message")}

        return WebSearchResponse(
            query=query,
            provider="anysearch",
            results=[self._to_result(item) for item in raw_results if isinstance(item, dict)],
            metadata=metadata,
        )

    @staticmethod
    def _to_result(item: dict[str, Any]) -> WebSearchResult:
        metadata = {
            key: value
            for key, value in item.items()
            if key
            not in {
                "title",
                "url",
                "description",
                "content",
                "source",
                "score",
                "quality_score",
                "published_at",
            }
        }
        return WebSearchResult(
            title=str(item.get("title") or item.get("url") or "(untitled)").strip(),
            url=str(item.get("url") or "").strip(),
            description=str(item.get("description") or "").strip(),
            content=str(item.get("content") or "").strip(),
            source=str(item.get("source") or "").strip() or None,
            score=_score(item.get("score")),
            quality_score=_score(item.get("quality_score")),
            published_at=str(item.get("published_at") or "").strip() or None,
            metadata=metadata,
        )


def _compact_dict(data: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if value is not None and value != [] and value != ""
    }


def _score(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
