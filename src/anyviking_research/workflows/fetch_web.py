from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import yaml

from anyviking_research.connectors.base import WebSearchResponse, WebSearchResult


@dataclass(frozen=True)
class FetchWebOutput:
    """Files created from one upstream web search run."""

    output_dir: Path
    markdown_dir: Path
    raw_json_path: Path
    manifest_path: Path
    markdown_files: list[Path]


def default_output_dir(query: str, *, root: str | Path = "data/web") -> Path:
    return Path(root) / _slugify(query)


def write_web_search_output(
    response: WebSearchResponse,
    output_dir: str | Path,
    *,
    fetched_at: datetime | None = None,
) -> FetchWebOutput:
    fetched_at = fetched_at or datetime.now(timezone.utc)
    root = Path(output_dir)
    raw_dir = root / "raw"
    markdown_dir = root / "markdown"
    raw_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)

    raw_json_path = raw_dir / f"{response.provider}_response.json"
    raw_json_path.write_text(
        json.dumps(_response_to_jsonable(response), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    markdown_files = [
        _write_result_markdown(
            result,
            markdown_dir,
            index=index,
            query=response.query,
            provider=response.provider,
            fetched_at=fetched_at,
        )
        for index, result in enumerate(response.results, start=1)
        if result.url
    ]

    manifest = {
        "query": response.query,
        "provider": response.provider,
        "fetched_at": fetched_at.isoformat(),
        "result_count": len(response.results),
        "markdown_count": len(markdown_files),
        "raw_json_path": str(raw_json_path),
        "markdown_dir": str(markdown_dir),
        "metadata": response.metadata,
        "files": [str(path) for path in markdown_files],
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return FetchWebOutput(
        output_dir=root,
        markdown_dir=markdown_dir,
        raw_json_path=raw_json_path,
        manifest_path=manifest_path,
        markdown_files=markdown_files,
    )


def _write_result_markdown(
    result: WebSearchResult,
    markdown_dir: Path,
    *,
    index: int,
    query: str,
    provider: str,
    fetched_at: datetime,
) -> Path:
    title = _clean_text(result.title or result.url or f"result-{index}")
    filename = f"{index:03d}-{_slugify(title)}.md"
    path = markdown_dir / filename
    frontmatter = {
        "title": title,
        "source_url": result.url,
        "source": result.source,
        "provider": provider,
        "query": query,
        "fetched_at": fetched_at.isoformat(),
        "published_at": result.published_at,
        "score": result.score,
        "quality_score": result.quality_score,
        "source_domain": urlparse(result.url).netloc,
    }
    body = [
        "---",
        yaml.safe_dump(
            {key: value for key, value in frontmatter.items() if value is not None},
            allow_unicode=True,
            sort_keys=False,
        ).strip(),
        "---",
        "",
        f"# {title}",
        "",
        f"- Source URL: {result.url}",
        f"- Query: {query}",
        f"- Provider: {provider}",
        "",
    ]
    description = _clean_text(result.description)
    content = _clean_text(result.content)
    if description:
        body.extend(["## Description", "", description, ""])
    if content:
        body.extend(["## Content", "", content, ""])
    elif description:
        body.extend(["## Content", "", description, ""])
    body.append("")
    path.write_text("\n".join(body), encoding="utf-8")
    return path


def _response_to_jsonable(response: WebSearchResponse) -> dict[str, object]:
    return {
        "query": response.query,
        "provider": response.provider,
        "metadata": response.metadata,
        "results": [asdict(result) for result in response.results],
    }


def _slugify(value: str, *, max_length: int = 80) -> str:
    value = _clean_text(value).strip().lower()
    value = re.sub(r"[^\w\u4e00-\u9fff]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-")
    return (value[:max_length].strip("-") or "untitled")


def _clean_text(value: str) -> str:
    value = value.replace("\ufffd", "")
    return "".join(
        char for char in value if char in {"\n", "\t"} or ord(char) >= 32
    ).strip()
