from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EvolutionOutput:
    output_dir: Path
    summary_path: Path
    patterns_path: Path
    run_count: int
    successful_count: int


@dataclass
class PatternStats:
    runs: int = 0
    successes: int = 0
    query_counter: Counter[str] = field(default_factory=Counter)
    tag_counter: Counter[str] = field(default_factory=Counter)
    target_counter: Counter[str] = field(default_factory=Counter)
    content_type_counter: Counter[str] = field(default_factory=Counter)
    freshness_counter: Counter[str] = field(default_factory=Counter)
    language_counter: Counter[str] = field(default_factory=Counter)
    retrieval_checks: int = 0
    retrieval_passed: int = 0


def evolve_skill(
    log_path: str | Path = "data/run_logs/runs.jsonl",
    output_dir: str | Path = "data/skill_evolution",
) -> EvolutionOutput:
    records = read_run_log(log_path)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    summary = build_summary(records)
    summary_path = output_root / "summary.json"
    patterns_path = output_root / "generated_patterns.md"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    patterns_path.write_text(render_patterns(summary), encoding="utf-8")

    return EvolutionOutput(
        output_dir=output_root,
        summary_path=summary_path,
        patterns_path=patterns_path,
        run_count=summary["run_count"],
        successful_count=summary["successful_count"],
    )


def read_run_log(path: str | Path) -> list[dict[str, Any]]:
    log_path = Path(path)
    if not log_path.exists():
        raise FileNotFoundError(f"Run log does not exist: {log_path}")

    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_number}: {log_path}") from exc
        if isinstance(record, dict):
            records.append(record)
    return records


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    stats_by_tag: dict[str, PatternStats] = defaultdict(PatternStats)
    stats_by_case: dict[str, PatternStats] = defaultdict(PatternStats)
    total_checks = 0
    total_passed = 0
    successful_count = 0

    for record in records:
        if bool(record.get("success")):
            successful_count += 1
        checks = _int(record.get("retrieval_checks_count"), default=len(record.get("retrieval_checks") or []))
        passed = _int(record.get("retrieval_passed"), default=0)
        total_checks += checks
        total_passed += passed

        keys = _record_group_keys(record)
        for group_name, key in keys:
            stats = stats_by_tag[key] if group_name == "tag" else stats_by_case[key]
            _update_stats(stats, record)

    return {
        "run_count": len(records),
        "successful_count": successful_count,
        "success_rate": _rate(successful_count, len(records)),
        "retrieval_checks": total_checks,
        "retrieval_passed": total_passed,
        "retrieval_pass_rate": _rate(total_passed, total_checks),
        "patterns_by_tag": {
            key: _stats_to_dict(stats)
            for key, stats in sorted(stats_by_tag.items())
        },
        "patterns_by_case": {
            key: _stats_to_dict(stats)
            for key, stats in sorted(stats_by_case.items())
        },
    }


def render_patterns(summary: dict[str, Any]) -> str:
    lines = [
        "# Generated Skill Patterns",
        "",
        "These patterns are generated from local `run-case` logs. Review them before changing the main Skill.",
        "",
        "## Overall",
        "",
        f"- Runs: {summary['run_count']}",
        f"- Successful runs: {summary['successful_count']}",
        f"- Success rate: {summary['success_rate']:.2%}",
        f"- Retrieval checks: {summary['retrieval_passed']}/{summary['retrieval_checks']} passed",
        "",
        "## Patterns By Tag",
        "",
    ]

    patterns = summary.get("patterns_by_tag") or {}
    if not patterns:
        lines.append("- No tag patterns found.")
    for tag, data in patterns.items():
        lines.extend(_render_pattern_section(tag, data))

    lines.extend(["", "## Patterns By Case", ""])
    case_patterns = summary.get("patterns_by_case") or {}
    if not case_patterns:
        lines.append("- No case patterns found.")
    for case_id, data in case_patterns.items():
        lines.extend(_render_pattern_section(case_id, data))

    lines.extend(
        [
            "",
            "## Suggested Skill Update",
            "",
            "- Prefer `run-case` when the user has a repeatable forecast or research question.",
            "- Keep generated evidence under `data/cases/<case-id>/` and logs under `data/run_logs/`.",
            "- Use retrieval checks as a lightweight proof that imported OpenViking resources are searchable.",
            "- Do not automatically overwrite `SKILL.md`; copy reviewed patterns manually.",
            "",
        ]
    )
    return "\n".join(lines)


def _record_group_keys(record: dict[str, Any]) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    for tag in record.get("tags") or []:
        text = str(tag).strip()
        if text:
            keys.append(("tag", text))
    case_id = str(record.get("case_id") or "").strip()
    if case_id:
        keys.append(("case", case_id))
    return keys


def _update_stats(stats: PatternStats, record: dict[str, Any]) -> None:
    stats.runs += 1
    if bool(record.get("success")):
        stats.successes += 1

    for query in record.get("queries") or []:
        text = str(query).strip()
        if text:
            stats.query_counter[text] += 1

    for tag in record.get("tags") or []:
        text = str(tag).strip()
        if text:
            stats.tag_counter[text] += 1

    target_uri = str(record.get("target_uri") or "").strip()
    if target_uri:
        stats.target_counter[target_uri] += 1

    search = record.get("search") if isinstance(record.get("search"), dict) else {}
    for content_type in search.get("content_types") or []:
        text = str(content_type).strip()
        if text:
            stats.content_type_counter[text] += 1
    for field_name, counter in (
        ("freshness", stats.freshness_counter),
        ("language", stats.language_counter),
    ):
        text = str(search.get(field_name) or "").strip()
        if text:
            counter[text] += 1

    stats.retrieval_checks += _int(record.get("retrieval_checks_count"), default=len(record.get("retrieval_checks") or []))
    stats.retrieval_passed += _int(record.get("retrieval_passed"), default=0)


def _stats_to_dict(stats: PatternStats) -> dict[str, Any]:
    return {
        "runs": stats.runs,
        "successes": stats.successes,
        "success_rate": _rate(stats.successes, stats.runs),
        "top_queries": _top_items(stats.query_counter),
        "top_tags": _top_items(stats.tag_counter),
        "top_target_uris": _top_items(stats.target_counter),
        "content_types": _top_items(stats.content_type_counter),
        "freshness": _top_items(stats.freshness_counter),
        "languages": _top_items(stats.language_counter),
        "retrieval_checks": stats.retrieval_checks,
        "retrieval_passed": stats.retrieval_passed,
        "retrieval_pass_rate": _rate(stats.retrieval_passed, stats.retrieval_checks),
    }


def _render_pattern_section(name: str, data: dict[str, Any]) -> list[str]:
    lines = [
        f"### {name}",
        "",
        f"- Runs: {data['runs']}",
        f"- Success rate: {data['success_rate']:.2%}",
        f"- Retrieval checks: {data['retrieval_passed']}/{data['retrieval_checks']} passed",
    ]
    lines.extend(_render_items("Recommended queries", data.get("top_queries") or []))
    lines.extend(_render_items("Target URI patterns", data.get("top_target_uris") or []))
    lines.extend(_render_items("Content types", data.get("content_types") or []))
    lines.extend(_render_items("Freshness", data.get("freshness") or []))
    lines.extend(_render_items("Languages", data.get("languages") or []))
    lines.append("")
    return lines


def _render_items(title: str, items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return []
    lines = [f"- {title}:"]
    lines.extend(f"  - {item['value']} ({item['count']})" for item in items)
    return lines


def _top_items(counter: Counter[str], *, limit: int = 5) -> list[dict[str, Any]]:
    return [
        {"value": value, "count": count}
        for value, count in counter.most_common(limit)
    ]


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
