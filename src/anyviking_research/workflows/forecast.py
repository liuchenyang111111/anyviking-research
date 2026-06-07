from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

import httpx
import yaml

from anyviking_research.connectors.base import WebSearchResponse, WebSearchResult
from anyviking_research.retrievers.base import SearchResult
from anyviking_research.workflows.fetch_web import FetchWebOutput, write_web_search_output
from anyviking_research.workflows.run_case import (
    ForecastCase,
    ImportCallback,
    SearchCallback,
    _collect_case_results,
    _optional_string,
    _optional_string_list,
    _positive_int,
    load_case,
    write_evidence_pack,
)


@dataclass(frozen=True)
class ForecastAnswer:
    case_id: str
    answer: str
    source: str | None = None


@dataclass(frozen=True)
class LeakFilterDecision:
    url: str
    title: str
    published_at: str | None
    decision: str
    reason: str


@dataclass(frozen=True)
class PromptEvidence:
    uri: str
    title: str
    snippet: str
    score: float | None = None


@dataclass(frozen=True)
class PromptAssembly:
    retrieved: list[PromptEvidence]
    selected_for_prompt: list[PromptEvidence]
    truncation_reason: str | None


@dataclass(frozen=True)
class Prediction:
    predicted_answer: str
    probabilities: dict[str, float]
    rationale: str = ""


@dataclass(frozen=True)
class ForecastScore:
    correct: bool
    brier: float
    truth_probability: float


@dataclass(frozen=True)
class ForecastRunResult:
    case: ForecastCase
    baseline_mode: str
    answer: ForecastAnswer | None
    output: FetchWebOutput
    evidence_pack_path: Path
    run_dir: Path
    trajectory_path: Path
    prediction_path: Path
    prediction: Prediction
    score: ForecastScore | None
    leak_filter: list[LeakFilterDecision]
    prompt_assembly: PromptAssembly
    imported: bool
    import_exit_code: int | None
    success: bool


@dataclass(frozen=True)
class CandidateContext:
    candidate_dir: Path
    candidate_id: str | None
    prompt_notes: str | None
    strategy: dict[str, Any]
    additional_queries: list[str] = field(default_factory=list)


class Predictor(Protocol):
    def predict(
        self,
        *,
        case: ForecastCase,
        prompt: str,
        evidence: list[PromptEvidence],
    ) -> Prediction:
        ...


LeakAuditor = Callable[[WebSearchResult, str], LeakFilterDecision]


class OpenAICompatiblePredictor:
    """Small OpenAI-compatible chat-completions predictor."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 60.0,
        cache_dir: str | Path | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.cache_dir = Path(cache_dir) if cache_dir is not None else None

    def predict(
        self,
        *,
        case: ForecastCase,
        prompt: str,
        evidence: list[PromptEvidence],
    ) -> Prediction:
        request = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": read_forecast_system_prompt(),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        data = self._request_with_cache(request)
        content = _extract_message_content(data)
        parsed = json.loads(content)
        return normalize_prediction(parsed, case.options)

    def _request_with_cache(self, request: dict[str, Any]) -> dict[str, Any]:
        cache_path: Path | None = None
        if self.cache_dir is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256(
                json.dumps(request, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()
            cache_path = self.cache_dir / f"{digest}.json"
            if cache_path.exists():
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
                return cached.get("response", cached)

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(endpoint, json=request, headers=headers)
            response.raise_for_status()
            data = response.json()

        if cache_path is not None:
            cache_path.write_text(
                json.dumps({"request": request, "response": data}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        return data


def forecast_case(
    case_path: str | Path,
    *,
    connector: Any,
    predictor: Predictor,
    importer: ImportCallback | None = None,
    searcher: SearchCallback | None = None,
    answer_path: str | Path | None = None,
    run_root: str | Path = "data/runs",
    skip_import: bool = False,
    skip_score: bool = False,
    max_prompt_evidence: int = 6,
    fetched_at: datetime | None = None,
    leak_auditor: LeakAuditor | None = None,
    baseline_mode: str = "anyviking",
    baseline_group: str | None = None,
    candidate_dir: str | Path | None = None,
) -> ForecastRunResult:
    fetched_at = fetched_at or datetime.now(timezone.utc)
    if baseline_mode not in {"anyviking", "no-retrieval", "naive-search"}:
        raise ValueError("baseline_mode must be anyviking, no-retrieval, or naive-search")
    if baseline_group is None and candidate_dir is not None and baseline_mode == "anyviking":
        baseline_group = "anyviking_candidate"
    baseline_group = baseline_group or default_baseline_group(baseline_mode)
    case = load_case(case_path)
    candidate_context = load_candidate_context(candidate_dir) if candidate_dir is not None else None
    if candidate_context is not None and candidate_context.additional_queries:
        case = replace(
            case,
            queries=_merge_unique(case.queries, candidate_context.additional_queries),
        )
    if not case.options:
        raise ValueError("forecast cases must define options")
    if not case.question_type:
        raise ValueError("forecast cases must define question_type")

    answer = None if skip_score else load_answer(answer_path or default_answer_path(case_path), case.id)

    if baseline_mode == "no-retrieval":
        raw_response = WebSearchResponse(
            query=case.question,
            provider="none",
            results=[],
            metadata={"baseline_mode": baseline_mode},
        )
    elif baseline_mode == "naive-search":
        raw_response = _collect_naive_result(case, connector)
    else:
        raw_response = _collect_case_results(case, connector)
    filtered_response, leak_decisions = apply_leak_filter(
        raw_response,
        cutoff_date=case.cutoff_date,
        auditor=leak_auditor,
    )

    output = write_web_search_output(filtered_response, case.output_dir, fetched_at=fetched_at)
    evidence_pack_path = write_evidence_pack(case, filtered_response, output, fetched_at=fetched_at)

    imported = False
    import_exit_code: int | None = None
    if baseline_mode != "no-retrieval" and not skip_import and output.markdown_files:
        if importer is None:
            raise ValueError("importer is required unless skip_import is true")
        import_exit_code = importer(output.markdown_dir, case.target_uri)
        imported = import_exit_code == 0

    retrieved: list[SearchResult] = []
    if baseline_mode == "anyviking" and searcher is not None and (imported or skip_import):
        retrieval_queries = [check.query for check in case.retrieval_checks] or [case.question]
        for query in retrieval_queries:
            retrieved.extend(searcher(query, case.target_uri, max_prompt_evidence))
    if not retrieved:
        retrieved = _local_evidence_from_web(filtered_response)

    run_dir = _run_dir(run_root, case.id, fetched_at, baseline_group)
    run_dir.mkdir(parents=True, exist_ok=True)
    if hasattr(predictor, "cache_dir") and getattr(predictor, "cache_dir") is None:
        setattr(predictor, "cache_dir", run_dir / "llm_calls")

    prompt_assembly = assemble_prompt_evidence(retrieved, max_prompt_evidence=max_prompt_evidence)
    prompt = render_forecast_prompt(
        case,
        prompt_assembly.selected_for_prompt,
        candidate_notes=candidate_context.prompt_notes if candidate_context is not None else None,
    )
    prediction = predictor.predict(
        case=case,
        prompt=prompt,
        evidence=prompt_assembly.selected_for_prompt,
    )
    score = None if answer is None else score_prediction(prediction, answer.answer, case.options)

    prediction_path = run_dir / "prediction.json"
    prediction_path.write_text(
        json.dumps(
            {
                "case_id": case.id,
                "prediction": asdict(prediction),
                "score": asdict(score) if score is not None else None,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    trajectory_path = run_dir / "trajectory.json"
    trajectory = build_trajectory(
        case=case,
        split=_case_split(case_path),
        baseline_mode=baseline_mode,
        baseline_group=baseline_group,
        answer=answer,
        output=output,
        evidence_pack_path=evidence_pack_path,
        prediction=prediction,
        score=score,
        leak_filter=leak_decisions,
        prompt_assembly=prompt_assembly,
        candidate_context=candidate_context,
        imported=imported,
        import_exit_code=import_exit_code,
        fetched_at=fetched_at,
    )
    trajectory_path.write_text(json.dumps(trajectory, ensure_ascii=False, indent=2), encoding="utf-8")

    success = bool(prediction.predicted_answer)
    if baseline_mode != "no-retrieval":
        success = success and bool(output.markdown_files)
    if import_exit_code is not None:
        success = success and import_exit_code == 0

    return ForecastRunResult(
        case=case,
        baseline_mode=baseline_mode,
        answer=answer,
        output=output,
        evidence_pack_path=evidence_pack_path,
        run_dir=run_dir,
        trajectory_path=trajectory_path,
        prediction_path=prediction_path,
        prediction=prediction,
        score=score,
        leak_filter=leak_decisions,
        prompt_assembly=prompt_assembly,
        imported=imported,
        import_exit_code=import_exit_code,
        success=success,
    )


def default_answer_path(case_path: str | Path) -> Path:
    path = Path(case_path)
    return path.with_name(f"{path.stem}.answer.json")


def load_answer(path: str | Path, case_id: str) -> ForecastAnswer:
    answer_path = Path(path)
    if not answer_path.exists():
        raise FileNotFoundError(f"Answer file does not exist: {answer_path}")
    data = json.loads(answer_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("answer file must contain a JSON object")
    seen_case_id = str(data.get("case_id") or "").strip()
    if seen_case_id and seen_case_id != case_id:
        raise ValueError(f"answer case_id mismatch: expected {case_id}, got {seen_case_id}")
    answer = str(data.get("answer") or "").strip()
    if not answer:
        raise ValueError("answer file must contain a non-empty answer")
    return ForecastAnswer(
        case_id=case_id,
        answer=answer,
        source=str(data.get("source") or "").strip() or None,
    )


def load_candidate_context(path: str | Path) -> CandidateContext:
    root = Path(path)
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Candidate directory does not exist: {root}")

    candidate_id = None
    candidate_path = root / "candidate.json"
    if candidate_path.exists():
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        if isinstance(candidate, dict):
            candidate_id = str(candidate.get("candidate_id") or "").strip() or None

    prompt_notes = _read_optional_text(root / "prompt_patch.md")
    strategy_path = root / "strategy_patch.yaml"
    strategy: dict[str, Any] = {}
    if strategy_path.exists():
        parsed = yaml.safe_load(strategy_path.read_text(encoding="utf-8")) or {}
        if not isinstance(parsed, dict):
            raise ValueError(f"strategy_patch.yaml must contain a YAML object: {strategy_path}")
        strategy = parsed

    additional_queries = _strategy_queries(strategy)
    return CandidateContext(
        candidate_dir=root,
        candidate_id=candidate_id,
        prompt_notes=prompt_notes,
        strategy=strategy,
        additional_queries=additional_queries,
    )


def apply_leak_filter(
    response: WebSearchResponse,
    *,
    cutoff_date: str | None,
    auditor: LeakAuditor | None = None,
) -> tuple[WebSearchResponse, list[LeakFilterDecision]]:
    if not cutoff_date:
        return response, [
            LeakFilterDecision(
                url=result.url,
                title=result.title,
                published_at=result.published_at,
                decision="kept",
                reason="no cutoff_date configured",
            )
            for result in response.results
        ]

    decisions: list[LeakFilterDecision] = []
    kept: list[WebSearchResult] = []
    for result in response.results:
        published = _date_key(result.published_at)
        cutoff = _date_key(cutoff_date)
        if published and cutoff and published > cutoff:
            decisions.append(
                LeakFilterDecision(
                    url=result.url,
                    title=result.title,
                    published_at=result.published_at,
                    decision="dropped",
                    reason=f"published_at is after cutoff_date {cutoff_date}",
                )
            )
            continue

        if auditor is not None and (not published or _mentions_future_date(result, cutoff_date)):
            decision = auditor(result, cutoff_date)
            decisions.append(decision)
            if decision.decision == "kept":
                kept.append(result)
            continue

        decisions.append(
            LeakFilterDecision(
                url=result.url,
                title=result.title,
                published_at=result.published_at,
                decision="kept",
                reason="published_at is within cutoff",
            )
        )
        kept.append(result)

    return WebSearchResponse(
        query=response.query,
        provider=response.provider,
        results=kept,
        metadata={**response.metadata, "cutoff_date": cutoff_date, "leak_filter": "simple"},
    ), decisions


def _collect_naive_result(case: ForecastCase, connector: Any) -> WebSearchResponse:
    max_results = _positive_int(case.search.get("max_results"), default=5)
    return connector.search(
        case.question,
        max_results=max_results,
        domains=_optional_string_list(case.search.get("domains")),
        tags=_optional_string_list(case.search.get("tags")),
        content_types=_optional_string_list(case.search.get("content_types")),
        zone=_optional_string(case.search.get("zone")),
        language=_optional_string(case.search.get("language")),
        providers=_optional_string_list(case.search.get("providers")),
        freshness=_optional_string(case.search.get("freshness")),
        from_time=_optional_string(case.search.get("from_time")),
        to_time=_optional_string(case.search.get("to_time")) or case.cutoff_date,
    )


def assemble_prompt_evidence(
    results: list[SearchResult],
    *,
    max_prompt_evidence: int,
) -> PromptAssembly:
    retrieved = [
        PromptEvidence(
            uri=result.uri,
            title=result.title,
            snippet=result.snippet,
            score=result.score,
        )
        for result in results
    ]
    selected = retrieved[:max_prompt_evidence]
    truncation_reason = "context_window" if len(retrieved) > len(selected) else None
    return PromptAssembly(
        retrieved=retrieved,
        selected_for_prompt=selected,
        truncation_reason=truncation_reason,
    )


def render_forecast_prompt(
    case: ForecastCase,
    evidence: list[PromptEvidence],
    *,
    candidate_notes: str | None = None,
) -> str:
    options = "\n".join(f"- {option}" for option in case.options)
    evidence_lines = []
    for index, item in enumerate(evidence, start=1):
        evidence_lines.extend(
            [
                f"## Evidence {index}",
                f"- URI: {item.uri}",
                f"- Title: {item.title}",
                f"- Score: {item.score if item.score is not None else 'unknown'}",
                "",
                item.snippet or "(no snippet)",
                "",
            ]
        )
    evidence_block = "\n".join(evidence_lines).strip() or "(no evidence)"
    candidate_block = ""
    if candidate_notes:
        candidate_block = "\n\nCandidate workflow notes:\n" + candidate_notes.strip()
    template = _read_prompt_template()
    if template is not None:
        prompt = template.format(
            question_type=case.question_type,
            question=case.question,
            cutoff_date=case.cutoff_date or "(not set)",
            options=options,
            evidence=evidence_block,
        )
        return prompt + candidate_block
    return f"""Question type: {case.question_type}
Question: {case.question}
Cutoff date: {case.cutoff_date or "(not set)"}

Options:
{options}

Evidence:
{evidence_block}
{candidate_block}

Return JSON with exactly these keys:
- predicted_answer: one of the options
- probabilities: object whose keys are the options and whose values sum to 1
- rationale: short explanation grounded in the evidence
"""


def read_forecast_system_prompt() -> str:
    path = Path("skills/anyviking-research/prompts/forecast_system.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "You are a careful forecasting assistant. Return JSON only."


def _read_prompt_template() -> str | None:
    path = Path("skills/anyviking-research/prompts/forecast_user_template.md")
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def normalize_prediction(data: dict[str, Any], options: list[str]) -> Prediction:
    predicted_answer = str(data.get("predicted_answer") or "").strip()
    probabilities = _normalize_probabilities(data.get("probabilities"), options)
    if not predicted_answer:
        predicted_answer = max(probabilities, key=probabilities.get)
    if predicted_answer not in options:
        raise ValueError(f"predicted_answer must be one of {options}: {predicted_answer}")
    return Prediction(
        predicted_answer=predicted_answer,
        probabilities=probabilities,
        rationale=str(data.get("rationale") or "").strip(),
    )


def score_prediction(prediction: Prediction, truth: str, options: list[str]) -> ForecastScore:
    if truth not in options:
        raise ValueError(f"truth must be one of {options}: {truth}")
    truth_probability = prediction.probabilities.get(truth, 0.0)
    brier = sum(
        (prediction.probabilities.get(option, 0.0) - (1.0 if option == truth else 0.0)) ** 2
        for option in options
    )
    return ForecastScore(
        correct=prediction.predicted_answer == truth,
        brier=brier,
        truth_probability=truth_probability,
    )


def build_trajectory(
    *,
    case: ForecastCase,
    split: str,
    baseline_mode: str,
    baseline_group: str,
    answer: ForecastAnswer | None,
    output: FetchWebOutput,
    evidence_pack_path: Path,
    prediction: Prediction,
    score: ForecastScore | None,
    leak_filter: list[LeakFilterDecision],
    prompt_assembly: PromptAssembly,
    candidate_context: CandidateContext | None,
    imported: bool,
    import_exit_code: int | None,
    fetched_at: datetime,
) -> dict[str, Any]:
    failure_mode = infer_failure_mode(
        output_markdown_count=len(output.markdown_files),
        prompt_assembly=prompt_assembly,
        score=score,
        leak_filter=leak_filter,
    )
    return {
        "timestamp": fetched_at.isoformat(),
        "case_id": case.id,
        "split": split,
        "baseline_mode": baseline_mode,
        "baseline_group": baseline_group,
        "title": case.title,
        "question": case.question,
        "question_type": case.question_type,
        "options": case.options,
        "cutoff_date": case.cutoff_date,
        "queries": case.queries,
        "search": case.search,
        "target_uri": case.target_uri,
        "output_dir": str(output.output_dir),
        "markdown_dir": str(output.markdown_dir),
        "markdown_count": len(output.markdown_files),
        "evidence_pack": str(evidence_pack_path),
        "imported": imported,
        "import_exit_code": import_exit_code,
        "leak_filter": [asdict(decision) for decision in leak_filter],
        "prompt_assembly": {
            "retrieved": [asdict(item) for item in prompt_assembly.retrieved],
            "selected_for_prompt": [asdict(item) for item in prompt_assembly.selected_for_prompt],
            "truncation_reason": prompt_assembly.truncation_reason,
        },
        "candidate": _candidate_to_json(candidate_context),
        "prediction": asdict(prediction),
        "score": asdict(score) if score is not None else None,
        "answer_available": answer is not None,
        "failure_mode": failure_mode,
    }


def infer_failure_mode(
    *,
    output_markdown_count: int,
    prompt_assembly: PromptAssembly,
    score: ForecastScore | None,
    leak_filter: list[LeakFilterDecision],
) -> str | None:
    if output_markdown_count == 0:
        return "search_missed"
    if any(decision.decision == "dropped" for decision in leak_filter):
        return "leak_contaminated"
    if not prompt_assembly.retrieved:
        return "retrieval_missed"
    if prompt_assembly.truncation_reason:
        return "prompt_truncated"
    if score is not None and not score.correct:
        return "llm_misjudged"
    return None


def _normalize_probabilities(raw: Any, options: list[str]) -> dict[str, float]:
    if not isinstance(raw, dict):
        raise ValueError("probabilities must be an object")
    probabilities: dict[str, float] = {}
    for option in options:
        value = raw.get(option)
        try:
            probabilities[option] = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"missing or invalid probability for option {option}") from exc
    total = sum(probabilities.values())
    if total <= 0:
        raise ValueError("probabilities must sum to a positive value")
    return {option: value / total for option, value in probabilities.items()}


def _extract_message_content(data: dict[str, Any]) -> str:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError(f"LLM response did not include choices: {data}")
    first = choices[0]
    if not isinstance(first, dict):
        raise RuntimeError(f"LLM response included invalid choice: {data}")
    message = first.get("message")
    if not isinstance(message, dict):
        raise RuntimeError(f"LLM response did not include a message: {data}")
    content = str(message.get("content") or "").strip()
    if not content:
        raise RuntimeError(f"LLM response message was empty: {data}")
    return content


def _local_evidence_from_web(response: WebSearchResponse) -> list[SearchResult]:
    results: list[SearchResult] = []
    for result in response.results:
        snippet = result.content or result.description
        results.append(
            SearchResult(
                title=result.title,
                uri=result.url,
                snippet=snippet[:1200],
                score=result.score,
                source=result.source or response.provider,
            )
        )
    return results


def _run_dir(root: str | Path, case_id: str, timestamp: datetime, baseline_group: str) -> Path:
    stamp = timestamp.strftime("%Y%m%dT%H%M%SZ")
    safe_group = re.sub(r"[^A-Za-z0-9_.-]+", "-", baseline_group).strip("-") or "run"
    base = Path(root) / f"{stamp}-{case_id}-{safe_group}"
    if not base.exists():
        return base
    index = 2
    while True:
        candidate = Path(root) / f"{stamp}-{case_id}-{safe_group}-{index}"
        if not candidate.exists():
            return candidate
        index += 1


def _case_split(case_path: str | Path) -> str:
    parts = {part.lower() for part in Path(case_path).parts}
    if "eval" in parts:
        return "eval"
    return "train"


def default_baseline_group(baseline_mode: str) -> str:
    if baseline_mode == "no-retrieval":
        return "no_retrieval"
    if baseline_mode == "naive-search":
        return "naive_search"
    return "anyviking_baseline"


def _date_key(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"\d{4}-\d{2}-\d{2}", value)
    return match.group(0) if match else None


def _read_optional_text(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return text or None


def _strategy_queries(strategy: dict[str, Any]) -> list[str]:
    raw = strategy.get("additional_queries")
    if raw is None:
        raw = strategy.get("top_queries")
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if str(item).strip()]


def _merge_unique(first: list[str], second: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for item in [*first, *second]:
        key = item.strip()
        if key and key not in seen:
            seen.add(key)
            merged.append(key)
    return merged


def _candidate_to_json(candidate_context: CandidateContext | None) -> dict[str, Any] | None:
    if candidate_context is None:
        return None
    return {
        "candidate_dir": str(candidate_context.candidate_dir),
        "candidate_id": candidate_context.candidate_id,
        "additional_queries": candidate_context.additional_queries,
        "prompt_notes_applied": candidate_context.prompt_notes is not None,
    }


def _mentions_future_date(result: WebSearchResult, cutoff_date: str) -> bool:
    cutoff = _date_key(cutoff_date)
    if not cutoff:
        return False
    text = f"{result.title}\n{result.description}\n{result.content}"
    for year, month, day in re.findall(r"(\d{4})-(\d{2})-(\d{2})", text):
        if f"{year}-{month}-{day}" > cutoff:
            return True
    return False
