from __future__ import annotations

import json
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class CollectOutput:
    output_path: Path
    trajectory_count: int


@dataclass(frozen=True)
class CandidateOutput:
    candidate_dir: Path
    candidate_path: Path
    trajectory_count: int


@dataclass(frozen=True)
class ValidationOutput:
    validation_path: Path
    passed: bool


@dataclass(frozen=True)
class PublishOutput:
    skill_dir: Path
    published: bool
    files_written: list[Path]


@dataclass(frozen=True)
class IterateOutput:
    candidate: CandidateOutput
    validation: ValidationOutput
    publish: PublishOutput | None


@dataclass(frozen=True)
class BaselineOutput:
    output_path: Path
    groups: list[str]


def collect_trajectories(
    runs_root: str | Path = "data/runs",
    output_path: str | Path = "data/evolution/collected.json",
) -> CollectOutput:
    trajectories = read_trajectories(runs_root)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"trajectory_count": len(trajectories), "trajectories": trajectories}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return CollectOutput(output_path=output, trajectory_count=len(trajectories))


def write_baseline_summary(
    runs_root: str | Path = "data/runs",
    output_path: str | Path = "data/evolution/baselines.json",
) -> BaselineOutput:
    trajectories = read_trajectories(runs_root)
    summary = summarize_baselines(trajectories)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return BaselineOutput(output_path=output, groups=sorted(summary))


def propose_candidate(
    runs_root: str | Path = "data/runs",
    output_root: str | Path = "data/evolution/candidates",
) -> CandidateOutput:
    trajectories = read_trajectories(runs_root)
    candidate_id = _candidate_id()
    candidate_dir = _unique_candidate_dir(Path(output_root), candidate_id)
    candidate_id = candidate_dir.name
    candidate_dir.mkdir(parents=True, exist_ok=True)

    summary = summarize_trajectories(trajectories)
    train_trajectory_count = int(summary.get("trajectory_count") or 0)
    candidate = {
        "candidate_id": candidate_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "trajectory_count": train_trajectory_count,
        "excluded_eval_count": int(summary.get("excluded_eval_count") or 0),
        "summary": summary,
        "status": "proposed",
        "publish_gate": "validate before publish",
    }
    candidate_path = candidate_dir / "candidate.json"
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")
    (candidate_dir / "learned_patch.md").write_text(render_learned_patch(candidate_id, summary), encoding="utf-8")
    (candidate_dir / "strategy_patch.yaml").write_text(render_strategy_patch(summary), encoding="utf-8")
    (candidate_dir / "prompt_patch.md").write_text(render_prompt_patch(summary), encoding="utf-8")
    (candidate_dir / "notes.md").write_text(render_candidate_notes(candidate_id, summary), encoding="utf-8")
    return CandidateOutput(
        candidate_dir=candidate_dir,
        candidate_path=candidate_path,
        trajectory_count=train_trajectory_count,
    )


def validate_candidate(
    candidate_dir: str | Path,
    output_path: str | Path | None = None,
    baseline_path: str | Path | None = None,
) -> ValidationOutput:
    root = Path(candidate_dir)
    candidate_path = root / "candidate.json"
    if not candidate_path.exists():
        raise FileNotFoundError(f"candidate.json does not exist: {candidate_path}")
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    summary = candidate.get("summary") if isinstance(candidate.get("summary"), dict) else {}
    trajectory_count = int(candidate.get("trajectory_count") or 0)
    failed = int(summary.get("failed_count") or 0)
    baselines = _read_baselines(baseline_path or root / "baselines.json")
    passed = trajectory_count > 0 and (root / "learned_patch.md").exists() and (root / "strategy_patch.yaml").exists()
    if baselines:
        passed = passed and bool(baselines.get("comparison_passed", False))
    validation = {
        "candidate_id": candidate.get("candidate_id"),
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "trajectory_count": trajectory_count,
        "failed_count": failed,
        "checks": {
            "has_trajectories": trajectory_count > 0,
            "has_learned_patch": (root / "learned_patch.md").exists(),
            "has_strategy_patch": (root / "strategy_patch.yaml").exists(),
            "candidate_not_worse": baselines.get("candidate_not_worse") if baselines else "not checked",
            "anyviking_baseline_not_worse_than_no_retrieval": (
                baselines.get("anyviking_baseline_not_worse_than_no_retrieval") if baselines else "not checked"
            ),
            "anyviking_baseline_not_worse_than_naive_search": (
                baselines.get("anyviking_baseline_not_worse_than_naive_search") if baselines else "not checked"
            ),
            "comparison_passed": baselines.get("comparison_passed") if baselines else "not checked",
        },
        "baselines": baselines or {
            "required_groups": [
                "no_retrieval",
                "naive_search",
                "anyviking_baseline",
                "anyviking_candidate",
            ],
            "status": "not supplied",
        },
        "note": "This structural validation is the local gate. Run forecast baselines on eval cases before publishing important changes.",
    }
    output = Path(output_path) if output_path is not None else root / "validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    return ValidationOutput(validation_path=output, passed=passed)


def publish_candidate(
    candidate_dir: str | Path,
    skill_dir: str | Path = "skills/anyviking-research",
) -> PublishOutput:
    root = Path(candidate_dir)
    validation_path = root / "validation.json"
    if not validation_path.exists():
        raise FileNotFoundError(f"validation.json does not exist: {validation_path}")
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if not bool(validation.get("passed")):
        raise ValueError("candidate validation did not pass")

    skill_root = Path(skill_dir)
    references = skill_root / "references"
    prompts = skill_root / "prompts"
    references.mkdir(parents=True, exist_ok=True)
    prompts.mkdir(parents=True, exist_ok=True)

    files_written: list[Path] = []
    learned_patch = root / "learned_patch.md"
    if learned_patch.exists():
        learned = references / "learned.md"
        _append_file(learned, learned_patch.read_text(encoding="utf-8"))
        files_written.append(learned)

    strategy_patch = root / "strategy_patch.yaml"
    if strategy_patch.exists():
        strategy = references / "strategy.yaml"
        _merge_yaml_file(strategy, strategy_patch)
        files_written.append(strategy)

    prompt_patch = root / "prompt_patch.md"
    if prompt_patch.exists():
        prompt_target = prompts / "forecast_notes.md"
        _append_file(prompt_target, prompt_patch.read_text(encoding="utf-8"))
        files_written.append(prompt_target)

    _append_jsonl(
        Path("data/evolution/published_versions.jsonl"),
        {
            "candidate_dir": str(root),
            "published_at": datetime.now(timezone.utc).isoformat(),
            "files_written": [str(path) for path in files_written],
        },
    )
    return PublishOutput(skill_dir=skill_root, published=True, files_written=files_written)


def iterate_once(
    runs_root: str | Path = "data/runs",
    output_root: str | Path = "data/evolution/candidates",
    *,
    baseline_path: str | Path | None = None,
    publish: bool = False,
    skill_dir: str | Path = "skills/anyviking-research",
) -> IterateOutput:
    candidate = propose_candidate(runs_root, output_root)
    validation = validate_candidate(candidate.candidate_dir, baseline_path=baseline_path)
    publish_output = None
    if publish and validation.passed:
        publish_output = publish_candidate(candidate.candidate_dir, skill_dir)
    return IterateOutput(
        candidate=candidate,
        validation=validation,
        publish=publish_output,
    )


def read_trajectories(runs_root: str | Path) -> list[dict[str, Any]]:
    root = Path(runs_root)
    if not root.exists():
        return []
    trajectories: list[dict[str, Any]] = []
    for path in sorted(root.rglob("trajectory.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid trajectory JSON: {path}") from exc
        if isinstance(data, dict):
            trajectories.append({**data, "_path": str(path)})
    return trajectories


def summarize_trajectories(trajectories: list[dict[str, Any]]) -> dict[str, Any]:
    train_trajectories = [
        trajectory
        for trajectory in trajectories
        if str(trajectory.get("split") or "train") != "eval"
    ]
    failure_modes: Counter[str] = Counter()
    query_counter: Counter[str] = Counter()
    target_counter: Counter[str] = Counter()
    by_failure: dict[str, list[str]] = defaultdict(list)
    brier_scores: list[float] = []
    correct_count = 0

    for trajectory in train_trajectories:
        mode = str(trajectory.get("failure_mode") or "success").strip()
        failure_modes[mode] += 1
        by_failure[mode].append(str(trajectory.get("case_id") or "unknown"))
        for query in trajectory.get("queries") or []:
            query_counter[str(query)] += 1
        target_uri = str(trajectory.get("target_uri") or "")
        if target_uri:
            target_counter[target_uri] += 1
        score = trajectory.get("score") if isinstance(trajectory.get("score"), dict) else {}
        if score.get("correct") is True:
            correct_count += 1
        if score.get("brier") is not None:
            brier_scores.append(float(score["brier"]))

    return {
        "trajectory_count": len(train_trajectories),
        "excluded_eval_count": len(trajectories) - len(train_trajectories),
        "correct_count": correct_count,
        "failed_count": len(train_trajectories) - correct_count,
        "accuracy": correct_count / len(train_trajectories) if train_trajectories else 0.0,
        "mean_brier": sum(brier_scores) / len(brier_scores) if brier_scores else None,
        "failure_modes": [{"value": key, "count": value} for key, value in failure_modes.most_common()],
        "top_queries": [{"value": key, "count": value} for key, value in query_counter.most_common(10)],
        "top_target_uris": [{"value": key, "count": value} for key, value in target_counter.most_common(10)],
        "cases_by_failure_mode": dict(by_failure),
    }


def summarize_baselines(trajectories: list[dict[str, Any]]) -> dict[str, Any]:
    by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trajectory in trajectories:
        if str(trajectory.get("split") or "") != "eval":
            continue
        group = str(trajectory.get("baseline_group") or "").strip()
        if group:
            by_group[group].append(trajectory)

    return {
        group: _baseline_group_summary(items)
        for group, items in sorted(by_group.items())
    }


def render_learned_patch(candidate_id: str, summary: dict[str, Any]) -> str:
    lines = [
        f"## {candidate_id}: Forecast Workflow Notes",
        "",
        f"- added: {datetime.now(timezone.utc).date().isoformat()}",
        f"- evidence: {summary.get('trajectory_count', 0)} local forecast trajectories",
        "- last_useful: null",
        "- supersedes: null",
        "",
        "### Observations",
        "",
        f"- Accuracy: {summary.get('accuracy', 0.0):.2%}",
    ]
    mean_brier = summary.get("mean_brier")
    if mean_brier is not None:
        lines.append(f"- Mean Brier: {mean_brier:.4f}")
    for item in summary.get("failure_modes") or []:
        lines.append(f"- Failure mode `{item['value']}` appeared {item['count']} time(s).")
    if summary.get("top_queries"):
        lines.extend(["", "### Reusable Queries", ""])
        lines.extend(f"- {item['value']}" for item in summary["top_queries"][:5])
    lines.append("")
    return "\n".join(lines)


def render_strategy_patch(summary: dict[str, Any]) -> str:
    data = {
        "version": "0.1.0",
        "generated_from": "local_forecast_trajectories",
        "top_queries": [item["value"] for item in (summary.get("top_queries") or [])[:5]],
        "failure_modes": summary.get("failure_modes") or [],
    }
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def render_prompt_patch(summary: dict[str, Any]) -> str:
    lines = [
        "# Forecast Prompt Notes",
        "",
        "Use probability forecasts, cite evidence URIs, and explain uncertainty.",
        "When evidence is thin, keep probabilities conservative instead of forcing high confidence.",
        "",
    ]
    for item in summary.get("failure_modes") or []:
        if item["value"] != "success":
            lines.append(f"- Watch for `{item['value']}` when assembling evidence.")
    lines.append("")
    return "\n".join(lines)


def render_candidate_notes(candidate_id: str, summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# Candidate {candidate_id}",
            "",
            "Review this candidate before publishing.",
            "",
            f"- Trajectories: {summary.get('trajectory_count', 0)}",
            f"- Accuracy: {summary.get('accuracy', 0.0):.2%}",
            "- Propose should use train trajectories only. Validate on eval summaries without inspecting eval failures.",
            "- Validation here is structural. Serious releases should compare baseline and candidate on eval cases.",
            "",
        ]
    )


def _candidate_id() -> str:
    return "cand-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _unique_candidate_dir(output_root: Path, candidate_id: str) -> Path:
    candidate_dir = output_root / candidate_id
    if not candidate_dir.exists():
        return candidate_dir
    index = 2
    while True:
        next_dir = output_root / f"{candidate_id}-{index}"
        if not next_dir.exists():
            return next_dir
        index += 1


def _append_file(path: Path, content: str) -> None:
    prefix = "\n\n" if path.exists() and path.read_text(encoding="utf-8").strip() else ""
    with path.open("a", encoding="utf-8") as file:
        file.write(prefix + content.strip() + "\n")


def _merge_yaml_file(target: Path, patch: Path) -> None:
    if target.exists():
        backup = target.with_suffix(target.suffix + ".bak")
        shutil.copyfile(target, backup)
    target.write_text(patch.read_text(encoding="utf-8"), encoding="utf-8")


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_baselines(path: str | Path) -> dict[str, Any]:
    baseline_path = Path(path)
    if not baseline_path.exists():
        return {}
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"baseline file must contain a JSON object: {baseline_path}")
    required = {"no_retrieval", "naive_search", "anyviking_baseline", "anyviking_candidate"}
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"baseline file missing groups: {', '.join(missing)}")
    baseline_brier = _metric(data["anyviking_baseline"], "mean_brier")
    candidate_brier = _metric(data["anyviking_candidate"], "mean_brier")
    no_retrieval_brier = _metric(data["no_retrieval"], "mean_brier")
    naive_search_brier = _metric(data["naive_search"], "mean_brier")
    candidate_not_worse = _not_worse(candidate_brier, baseline_brier)
    anyviking_baseline_not_worse_than_no_retrieval = _not_worse(baseline_brier, no_retrieval_brier)
    anyviking_baseline_not_worse_than_naive_search = _not_worse(baseline_brier, naive_search_brier)
    comparison_passed = (
        candidate_not_worse
        and anyviking_baseline_not_worse_than_no_retrieval
        and anyviking_baseline_not_worse_than_naive_search
    )
    return {
        **data,
        "candidate_not_worse": candidate_not_worse,
        "anyviking_baseline_not_worse_than_no_retrieval": anyviking_baseline_not_worse_than_no_retrieval,
        "anyviking_baseline_not_worse_than_naive_search": anyviking_baseline_not_worse_than_naive_search,
        "comparison_passed": comparison_passed,
    }


def _baseline_group_summary(trajectories: list[dict[str, Any]]) -> dict[str, Any]:
    brier_scores: list[float] = []
    correct_count = 0
    for trajectory in trajectories:
        score = trajectory.get("score") if isinstance(trajectory.get("score"), dict) else {}
        if score.get("correct") is True:
            correct_count += 1
        if score.get("brier") is not None:
            brier_scores.append(float(score["brier"]))
    return {
        "case_count": len(trajectories),
        "accuracy": correct_count / len(trajectories) if trajectories else 0.0,
        "mean_brier": sum(brier_scores) / len(brier_scores) if brier_scores else None,
    }


def _metric(group: Any, key: str) -> float | None:
    if not isinstance(group, dict) or group.get(key) is None:
        return None
    return float(group[key])


def _not_worse(candidate: float | None, baseline: float | None) -> bool:
    return candidate is not None and baseline is not None and candidate <= baseline
