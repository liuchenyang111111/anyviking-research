from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ov_search_skill.retrievers.base import SearchResult
from ov_search_skill.retrievers.openviking import OpenVikingRetriever


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


def load_questions(config_path: str | Path) -> tuple[str, str, list[ResearchQuestion]]:
    path = Path(config_path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("research config must be a YAML mapping")

    title = str(data.get("topic_title") or data.get("title") or "OpenViking 检索调研草稿")
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
        heading = str(item.get("heading") or item.get("title") or f"问题 {index}")
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
    documents_only: bool = True,
    filter_unhelpful: bool = True,
    timeout: float = 60.0,
) -> ResearchReport:
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")
    if fetch_k is not None and fetch_k < top_k:
        raise ValueError("fetch_k must be greater than or equal to top_k")

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
        results = results[:top_k]
        results_by_id[question.id] = results

    return ResearchReport(
        title=title,
        scope=scope,
        questions=questions,
        results_by_id=results_by_id,
    )


def render_markdown(report: ResearchReport) -> str:
    lines: list[str] = [
        f"# {report.title}",
        "",
        "> 这是一份检索型调研草稿：它只整理 OpenViking 返回的相关资料，不直接生成最终分析结论。",
        "",
        "## 元信息",
        "",
        f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 检索范围：`{report.scope}`",
        f"- 问题数量：{len(report.questions)}",
        "",
        "## 检索结果",
        "",
    ]

    for index, question in enumerate(report.questions, start=1):
        results = report.results_by_id.get(question.id, [])
        lines.extend(
            [
                f"### {index}. {question.heading}",
                "",
                "**问题**",
                "",
                question.question,
                "",
                f"**Top {len(results)} 检索结果**",
                "",
            ]
        )

        if not results:
            lines.extend(["未检索到结果。", ""])
            continue

        for result_index, result in enumerate(results, start=1):
            score = f"{result.score:.4f}" if result.score is not None else "N/A"
            lines.extend(
                [
                    f"{result_index}. **{result.title}**",
                    f"   - URI：`{result.uri}`",
                    f"   - Score：{score}",
                ]
            )
            if result.snippet:
                lines.extend(
                    [
                        "   - 摘要：",
                        _indent_multiline(result.snippet, "     "),
                    ]
                )
            lines.append("")

    lines.extend(
        [
            "## 后续可做",
            "",
            "- 人工阅读上述 URI 对应原文，筛选真正可引用材料。",
            "- 在此基础上接入 LLM 或 OpenVikingBot，生成完整调研报告。",
            "- 对每节结果补充引用段落和最终结论。",
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
    }


def _indent_multiline(text: str, prefix: str) -> str:
    return "\n".join(prefix + line if line.strip() else prefix for line in text.splitlines())


def _is_generated_summary(uri: str) -> bool:
    tail = uri.rstrip("/").rsplit("/", 1)[-1].lower()
    return tail in {".abstract.md", ".overview.md"}


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

    normalized = text.replace(" ", "")
    unhelpful_markers = (
        "抱歉",
        "未找到相关",
        "没有找到相关",
        "无法给到相关内容",
        "无法回答",
        "无法为你提供",
        "无法提供",
        "暂未提供有效参考信息",
        "尚未录入具体",
    )
    return any(marker in normalized for marker in unhelpful_markers)
