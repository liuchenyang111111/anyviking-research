from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import yaml

from anyviking_research.retrievers.base import SearchResult
from anyviking_research.retrievers.openviking import OpenVikingRetriever


@dataclass(frozen=True)
class ResearchQuestion:
    """One research section backed by one retrieval query."""

    id: str
    heading: str
    question: str


@dataclass(frozen=True)
class ResearchReport:
    """Research retrieval draft generated from configured questions."""

    title: str
    scope: str
    questions: list[ResearchQuestion]
    results_by_id: dict[str, list[SearchResult]]
    citation_stats: list[CitationStat] = field(default_factory=list)
    quality_warnings: list[QualityWarning] = field(default_factory=list)


@dataclass(frozen=True)
class CitationStat:
    """How often one cited document appears across research sections."""

    title: str
    uri: str
    count: int
    section_ids: list[str]
    section_headings: list[str]
    best_score: float | None = None


@dataclass(frozen=True)
class QualityWarning:
    """Lightweight quality signal for a retrieval draft."""

    code: str
    message: str
    section_id: str | None = None
    section_heading: str | None = None


DedupMode = Literal["section", "none"]


def load_questions(config_path: str | Path) -> tuple[str, str, list[ResearchQuestion]]:
    path = Path(config_path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("research config must be a YAML mapping")

    title = str(data.get("topic_title") or data.get("title") or "OpenViking retrieval research draft")
    scope = str(data.get("ov_root_uri") or data.get("scope") or "").strip()
    if not scope:
        raise ValueError("research config must define ov_root_uri or scope")

    raw_sections = data.get("sections")
    if not isinstance(raw_sections, list) or not raw_sections:
        raise ValueError("research config must define a non-empty sections list")

    questions: list[ResearchQuestion] = []
    for index, item in enumerate(raw_sections, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"section #{index} must be a mapping")

        question = str(item.get("question") or "").strip()
        if not question:
            raise ValueError(f"section #{index} must define question")

        section_id = str(item.get("id") or f"section-{index}")
        heading = str(item.get("heading") or item.get("title") or f"Question {index}")
        questions.append(
            ResearchQuestion(id=section_id, heading=heading, question=question)
        )

    return title, scope, questions


def run_research(
    config_path: str | Path,
    *,
    base_url: str = "http://127.0.0.1:1933",
    top_k: int = 5,
    fetch_k: int | None = None,
    dedupe: DedupMode = "section",
    include_citation_stats: bool = True,
    min_results_per_section: int = 1,
    documents_only: bool = True,
    filter_unhelpful: bool = True,
    timeout: float = 60.0,
) -> ResearchReport:
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")
    if fetch_k is not None and fetch_k < top_k:
        raise ValueError("fetch_k must be greater than or equal to top_k")
    if dedupe not in {"section", "none"}:
        raise ValueError("dedupe must be 'section' or 'none'")
    if min_results_per_section < 0:
        raise ValueError("min_results_per_section must be greater than or equal to 0")

    title, scope, questions = load_questions(config_path)
    retriever = OpenVikingRetriever(base_url=base_url, timeout=timeout)
    results_by_id: dict[str, list[SearchResult]] = {}
    candidate_limit = _candidate_limit(
        top_k,
        fetch_k=fetch_k,
        documents_only=documents_only,
        filter_unhelpful=filter_unhelpful,
    )

    for question in questions:
        results = retriever.search(question.question, scope=scope, top_k=candidate_limit)
        if documents_only:
            results = [
                result for result in results if not _is_generated_summary(result.uri)
            ]
        if filter_unhelpful:
            results = [
                result for result in results if not _is_unhelpful_result(result)
            ]
        if dedupe == "section":
            results = _dedupe_results_by_uri(results)
        results = results[:top_k]
        results_by_id[question.id] = results

    citation_stats = (
        _build_citation_stats(questions, results_by_id) if include_citation_stats else []
    )
    quality_warnings = _build_quality_warnings(
        questions,
        results_by_id,
        citation_stats,
        min_results_per_section=min_results_per_section,
    )

    return ResearchReport(
        title=title,
        scope=scope,
        questions=questions,
        results_by_id=results_by_id,
        citation_stats=citation_stats,
        quality_warnings=quality_warnings,
    )


def render_markdown(report: ResearchReport) -> str:
    lines: list[str] = [
        f"# {report.title}",
        "",
        "> This is a retrieval-based research draft. It organizes evidence returned by OpenViking; it is not a final analytical conclusion.",
        "",
        "## Metadata",
        "",
        f"- Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Search scope: `{report.scope}`",
        f"- Question count: {len(report.questions)}",
        "",
        "## Retrieval Results",
        "",
    ]

    for index, question in enumerate(report.questions, start=1):
        results = report.results_by_id.get(question.id, [])
        lines.extend(
            [
                f"### {index}. {question.heading}",
                "",
                "**Question**",
                "",
                question.question,
                "",
                f"**Top {len(results)} results**",
                "",
            ]
        )

        if not results:
            lines.extend(["No retrieval results found.", ""])
            continue

        for result_index, result in enumerate(results, start=1):
            score = f"{result.score:.4f}" if result.score is not None else "N/A"
            lines.extend(
                [
                    f"{result_index}. **{result.title}**",
                    f"   - URI: `{result.uri}`",
                    f"   - Score: {score}",
                ]
            )
            if result.snippet:
                lines.extend(
                    [
                        "   - Snippet:",
                        _indent_multiline(result.snippet, "     "),
                    ]
                )
            lines.append("")

    if report.citation_stats:
        lines.extend(
            [
                "## Citation Stats",
                "",
                "| Document | Hit count | Sections | Best score |",
                "| --- | ---: | --- | ---: |",
            ]
        )
        for stat in report.citation_stats:
            best_score = f"{stat.best_score:.4f}" if stat.best_score is not None else "N/A"
            sections = ", ".join(stat.section_headings)
            lines.append(
                "| "
                + " | ".join(
                    [
                        _escape_table_cell(f"{stat.title}<br>`{stat.uri}`"),
                        str(stat.count),
                        _escape_table_cell(sections),
                        best_score,
                    ]
                )
                + " |"
            )
        lines.append("")

    if report.quality_warnings:
        lines.extend(["## Quality Notes", ""])
        for warning in report.quality_warnings:
            lines.append(f"- `{warning.code}`: {warning.message}")
        lines.append("")

    lines.extend(
        [
            "## Suggested Next Steps",
            "",
            "- Read the cited `viking://` documents and decide which evidence is worth quoting.",
            "- Add interpretation, comparison, and final conclusions manually or with an optional LLM step.",
            "- Keep the final report grounded in the cited OpenViking resources.",
            "",
        ]
    )
    return "\n".join(lines)


def write_markdown_report(report: ResearchReport, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")
    return path


def report_to_jsonable(report: ResearchReport) -> dict[str, Any]:
    return {
        "title": report.title,
        "scope": report.scope,
        "question_count": len(report.questions),
        "sections": [
            {
                "id": question.id,
                "heading": question.heading,
                "question": question.question,
                "results": [result.__dict__ for result in report.results_by_id[question.id]],
            }
            for question in report.questions
        ],
        "citation_stats": [stat.__dict__ for stat in report.citation_stats],
        "quality_warnings": [
            warning.__dict__ for warning in report.quality_warnings
        ],
    }


def _indent_multiline(text: str, prefix: str) -> str:
    return "\n".join(prefix + line if line.strip() else prefix for line in text.splitlines())


def _is_generated_summary(uri: str) -> bool:
    tail = uri.rstrip("/").rsplit("/", 1)[-1].lower()
    return tail in {".abstract.md", ".overview.md"}


def _dedupe_results_by_uri(results: list[SearchResult]) -> list[SearchResult]:
    deduped: list[SearchResult] = []
    positions: dict[str, int] = {}
    for result in results:
        if result.uri not in positions:
            positions[result.uri] = len(deduped)
            deduped.append(result)
            continue

        existing_index = positions[result.uri]
        existing = deduped[existing_index]
        if _score_value(result.score) > _score_value(existing.score):
            deduped[existing_index] = result
    return deduped


def _build_citation_stats(
    questions: list[ResearchQuestion],
    results_by_id: dict[str, list[SearchResult]],
) -> list[CitationStat]:
    stats: dict[str, dict[str, Any]] = {}

    for question in questions:
        for result in results_by_id.get(question.id, []):
            if result.uri not in stats:
                stats[result.uri] = {
                    "title": result.title,
                    "uri": result.uri,
                    "count": 0,
                    "section_ids": [],
                    "section_headings": [],
                    "best_score": result.score,
                }

            item = stats[result.uri]
            item["count"] += 1
            if question.id not in item["section_ids"]:
                item["section_ids"].append(question.id)
                item["section_headings"].append(question.heading)
            if _score_value(result.score) > _score_value(item["best_score"]):
                item["best_score"] = result.score

    def sort_key(item: dict[str, Any]) -> tuple[int, float, str]:
        return (
            int(item["count"]),
            _score_value(item["best_score"]),
            str(item["title"]),
        )

    return [
        CitationStat(
            title=str(item["title"]),
            uri=str(item["uri"]),
            count=int(item["count"]),
            section_ids=list(item["section_ids"]),
            section_headings=list(item["section_headings"]),
            best_score=item["best_score"],
        )
        for item in sorted(stats.values(), key=sort_key, reverse=True)
        if item["uri"]
    ]


def _build_quality_warnings(
    questions: list[ResearchQuestion],
    results_by_id: dict[str, list[SearchResult]],
    citation_stats: list[CitationStat],
    *,
    min_results_per_section: int,
) -> list[QualityWarning]:
    warnings: list[QualityWarning] = []
    for question in questions:
        result_count = len(results_by_id.get(question.id, []))
        if result_count == 0:
            warnings.append(
                QualityWarning(
                    code="empty_section",
                    message=(
                        f"Section '{question.heading}' has no retrieval results. "
                        "Try changing the question or widening the search scope."
                    ),
                    section_id=question.id,
                    section_heading=question.heading,
                )
            )
        elif result_count < min_results_per_section:
            warnings.append(
                QualityWarning(
                    code="low_coverage",
                    message=(
                        f"Section '{question.heading}' has only {result_count} result(s), "
                        f"below the target of {min_results_per_section}."
                    ),
                    section_id=question.id,
                    section_heading=question.heading,
                )
            )

    if len(questions) >= 2:
        threshold = max(2, (len(questions) + 1) // 2)
        reused = [
            stat
            for stat in citation_stats
            if len(stat.section_ids) >= threshold
        ][:5]
        for stat in reused:
            warnings.append(
                QualityWarning(
                    code="high_reuse",
                    message=(
                        f"Document '{stat.title}' appears in {len(stat.section_ids)} sections. "
                        "Check whether the evidence is too concentrated."
                    ),
                )
            )

    return warnings


def _score_value(score: float | None) -> float:
    return float("-inf") if score is None else score


def _escape_table_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "<br>")


def _candidate_limit(
    top_k: int,
    *,
    fetch_k: int | None,
    documents_only: bool,
    filter_unhelpful: bool,
) -> int:
    if fetch_k is not None:
        return fetch_k
    if documents_only or filter_unhelpful:
        return max(top_k * 8, top_k)
    return top_k


def _is_unhelpful_result(result: SearchResult) -> bool:
    text = (result.snippet or "").strip()
    if not text:
        return True

    normalized = text.lower().replace(" ", "")
    unhelpful_markers = (
        "sorry",
        "no relevant result",
        "no relevant results",
        "cannot answer",
        "unable to answer",
        "unable to provide",
        "not found",
        "抱歉",
        "未找到相关",
        "没有找到相关",
        "无法回答",
        "无法提供",
        "暂未提供有效参考信息",
        "尚未录入具体",
    )
    return any(marker.lower().replace(" ", "") in normalized for marker in unhelpful_markers)
