from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

from anyviking_research.connectors.base import WebSearchResponse, WebSearchResult
from anyviking_research.retrievers.base import SearchResult
from anyviking_research.workflows.fetch_web import FetchWebOutput, write_web_search_output


ImportCallback = Callable[[Path, str], int]
SearchCallback = Callable[[str, str, int], list[SearchResult]]


@dataclass(frozen=True)
class RetrievalCheck:
    query: str
    top_k: int = 3


@dataclass(frozen=True)
class ForecastCase:
    id: str
    title: str
    question: str
    queries: list[str]
    output_dir: Path
    target_uri: str
    question_type: str | None = None
    options: list[str] = field(default_factory=list)
    cutoff_date: str | None = None
    horizon: str | None = None
    search: dict[str, Any] = field(default_factory=dict)
    retrieval_checks: list[RetrievalCheck] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RetrievalCheckRun:
    query: str
    top_k: int
    result_count: int
    passed: bool


@dataclass(frozen=True)
class CaseRunResult:
    case: ForecastCase
    output: FetchWebOutput
    evidence_pack_path: Path
    log_path: Path
    search_result_count: int
    markdown_count: int
    imported: bool
    import_exit_code: int | None
    retrieval_checks: list[RetrievalCheckRun]
    success: bool


def load_case(path: str | Path) -> ForecastCase:
    case_path = Path(path)
    data = yaml.safe_load(case_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Case file must contain a YAML object: {case_path}")

    case_id = _required_string(data, "id")
    question = _required_string(data, "question")
    title = str(data.get("title") or case_id).strip()
    forecast = data.get("forecast") or {}
    if not isinstance(forecast, dict):
        raise ValueError("forecast must be a YAML object")
    queries = _string_list(data.get("queries"), field_name="queries")
    if not queries:
        raise ValueError("queries must contain at least one query")

    search = data.get("search") or {}
    if not isinstance(search, dict):
        raise ValueError("search must be a YAML object")

    storage = data.get("storage") or {}
    if not isinstance(storage, dict):
        raise ValueError("storage must be a YAML object")
    output_dir = Path(str(storage.get("output_dir") or f"data/cases/{case_id}"))
    target_uri = str(storage.get("target_uri") or "").strip()
    if not target_uri:
        raise ValueError("storage.target_uri is required")

    return ForecastCase(
        id=case_id,
        title=title,
        question=question,
        question_type=_optional_string(data.get("question_type") or forecast.get("question_type")),
        options=_string_list(data.get("options") or forecast.get("options") or [], field_name="options"),
        cutoff_date=_optional_string(data.get("cutoff_date") or data.get("as_of_date") or forecast.get("end_time")),
        horizon=str(data.get("horizon") or "").strip() or None,
        queries=queries,
        search=search,
        output_dir=output_dir,
        target_uri=target_uri,
        retrieval_checks=_parse_retrieval_checks(data.get("retrieval_checks") or []),
        tags=_string_list(data.get("tags") or [], field_name="tags"),
    )


def run_case(
    case_path: str | Path,
    *,
    connector: Any,
    importer: ImportCallback | None = None,
    searcher: SearchCallback | None = None,
    log_path: str | Path = "data/run_logs/runs.jsonl",
    skip_import: bool = False,
    skip_checks: bool = False,
    fetched_at: datetime | None = None,
) -> CaseRunResult:
    fetched_at = fetched_at or datetime.now(timezone.utc)
    case = load_case(case_path)
    response = _collect_case_results(case, connector)
    output = write_web_search_output(response, case.output_dir, fetched_at=fetched_at)
    evidence_pack_path = write_evidence_pack(case, response, output, fetched_at=fetched_at)

    imported = False
    import_exit_code: int | None = None
    if not skip_import and output.markdown_files:
        if importer is None:
            raise ValueError("importer is required unless skip_import is true")
        import_exit_code = importer(output.markdown_dir, case.target_uri)
        imported = import_exit_code == 0

    check_runs: list[RetrievalCheckRun] = []
    if not skip_checks and imported and case.retrieval_checks:
        if searcher is None:
            raise ValueError("searcher is required when retrieval checks are enabled")
        check_runs = [
            _run_retrieval_check(check, case.target_uri, searcher)
            for check in case.retrieval_checks
        ]

    success = bool(output.markdown_files)
    if import_exit_code is not None:
        success = success and import_exit_code == 0
    if check_runs:
        success = success and all(check.passed for check in check_runs)

    result = CaseRunResult(
        case=case,
        output=output,
        evidence_pack_path=evidence_pack_path,
        log_path=Path(log_path),
        search_result_count=len(response.results),
        markdown_count=len(output.markdown_files),
        imported=imported,
        import_exit_code=import_exit_code,
        retrieval_checks=check_runs,
        success=success,
    )
    append_run_log(result, log_path=log_path, timestamp=fetched_at)
    return result


def write_evidence_pack(
    case: ForecastCase,
    response: WebSearchResponse,
    output: FetchWebOutput,
    *,
    fetched_at: datetime,
) -> Path:
    path = output.output_dir / "evidence_pack.md"
    lines = [
        f"# {case.title}",
        "",
        f"- Case ID: `{case.id}`",
        f"- Question: {case.question}",
        f"- Horizon: {case.horizon or '(not set)'}",
        f"- Target URI: `{case.target_uri}`",
        f"- Fetched at: {fetched_at.isoformat()}",
        "",
        "## Search Queries",
        "",
        *[f"- {query}" for query in case.queries],
        "",
        "## Sources",
        "",
        "| # | Title | Source | URL |",
        "| --- | --- | --- | --- |",
    ]

    for index, result in enumerate(response.results, start=1):
        title = _markdown_cell(result.title or "(untitled)")
        source = _markdown_cell(result.source or "")
        url = result.url
        lines.append(f"| {index} | {title} | {source} | {url} |")

    lines.extend(
        [
            "",
            "## Retrieval Checks",
            "",
        ]
    )
    if case.retrieval_checks:
        lines.extend(f"- {check.query} (top_k={check.top_k})" for check in case.retrieval_checks)
    else:
        lines.append("- (none)")

    lines.extend(
        [
            "",
            "## Notes For Forecasting",
            "",
            "- Use this file as a source map, not as a final forecast.",
            "- Review the markdown files before making a prediction.",
            "- Add missing queries when an important angle is not covered.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def append_run_log(
    result: CaseRunResult,
    *,
    log_path: str | Path,
    timestamp: datetime,
) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": timestamp.isoformat(),
        "case_id": result.case.id,
        "title": result.case.title,
        "question": result.case.question,
        "horizon": result.case.horizon,
        "question_type": result.case.question_type,
        "options": result.case.options,
        "cutoff_date": result.case.cutoff_date,
        "queries": result.case.queries,
        "search": result.case.search,
        "tags": result.case.tags,
        "output_dir": str(result.output.output_dir),
        "target_uri": result.case.target_uri,
        "search_result_count": result.search_result_count,
        "markdown_count": result.markdown_count,
        "imported": result.imported,
        "import_exit_code": result.import_exit_code,
        "retrieval_checks": [asdict(check) for check in result.retrieval_checks],
        "retrieval_passed": sum(1 for check in result.retrieval_checks if check.passed),
        "success": result.success,
    }
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def _collect_case_results(case: ForecastCase, connector: Any) -> WebSearchResponse:
    max_results = _positive_int(case.search.get("max_results"), default=5)
    responses = [
        connector.search(
            query,
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
        for query in case.queries
    ]

    seen_urls: set[str] = set()
    results: list[WebSearchResult] = []
    for query, response in zip(case.queries, responses):
        for result in response.results:
            normalized_url = result.url.strip()
            if not normalized_url or normalized_url in seen_urls:
                continue
            seen_urls.add(normalized_url)
            metadata = {**result.metadata, "case_query": query}
            results.append(replace(result, metadata=metadata))

    return WebSearchResponse(
        query=case.question,
        provider=responses[0].provider if responses else "anysearch",
        results=results,
        metadata={
            "case_id": case.id,
            "title": case.title,
            "queries": case.queries,
            "response_count": len(responses),
            "search_metadata": [response.metadata for response in responses],
        },
    )


def _run_retrieval_check(
    check: RetrievalCheck,
    target_uri: str,
    searcher: SearchCallback,
) -> RetrievalCheckRun:
    results = searcher(check.query, target_uri, check.top_k)
    return RetrievalCheckRun(
        query=check.query,
        top_k=check.top_k,
        result_count=len(results),
        passed=bool(results),
    )


def _parse_retrieval_checks(raw: Any) -> list[RetrievalCheck]:
    if not isinstance(raw, list):
        raise ValueError("retrieval_checks must be a list")
    checks: list[RetrievalCheck] = []
    for item in raw:
        if isinstance(item, str):
            checks.append(RetrievalCheck(query=item.strip()))
            continue
        if isinstance(item, dict):
            query = str(item.get("query") or "").strip()
            if not query:
                raise ValueError("retrieval check query must not be empty")
            checks.append(RetrievalCheck(query=query, top_k=_positive_int(item.get("top_k"), default=3)))
            continue
        raise ValueError("retrieval_checks items must be strings or objects")
    return checks


def _required_string(data: dict[str, Any], key: str) -> str:
    value = str(data.get(key) or "").strip()
    if not value:
        raise ValueError(f"{key} is required")
    return value


def _string_list(value: Any, *, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    return [_scalar_to_string(item) for item in value if _scalar_to_string(item)]


def _optional_string(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _optional_string_list(value: Any) -> list[str] | None:
    if value is None:
        return None
    return _string_list(value, field_name="search list value")


def _positive_int(value: Any, *, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("expected a positive integer") from exc
    if parsed <= 0:
        raise ValueError("expected a positive integer")
    return parsed


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _scalar_to_string(value: Any) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return str(value).strip()
