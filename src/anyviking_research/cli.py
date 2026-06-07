from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import httpx

from anyviking_research.connectors.anysearch import AnySearchConnector
from anyviking_research.retrievers.base import SearchResult
from anyviking_research.retrievers.openviking import OpenVikingRetriever
from anyviking_research.workflows.fetch_web import (
    default_output_dir,
    write_web_search_output,
)
from anyviking_research.workflows.evolve_skill import evolve_skill
from anyviking_research.workflows.forecast import (
    OpenAICompatiblePredictor,
    forecast_case,
)
from anyviking_research.workflows.run_case import run_case

DEFAULT_OPENVIKING_URL = "http://127.0.0.1:1933"
DEFAULT_ANYSEARCH_URL = "https://api.anysearch.com"
DEFAULT_LLM_BASE_URL = "https://api.openai.com/v1"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anyviking",
        description=(
            "AnySearch upstream web discovery plus OpenViking downstream "
            "indexing and retrieval."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check local installation and runtime readiness")
    doctor.add_argument(
        "--url",
        default=_default_openviking_url(),
        help="OpenViking server URL",
    )
    doctor.add_argument("--timeout", type=float, default=5.0)
    doctor.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON",
    )

    health = subparsers.add_parser("health", help="Check the OpenViking server health")
    health.add_argument(
        "--url",
        default=_default_openviking_url(),
        help="OpenViking server URL",
    )
    health.add_argument("--timeout", type=float, default=10.0)

    status = subparsers.add_parser("status", help="Show OpenViking service and queue status")
    status.add_argument(
        "--json",
        action="store_true",
        help="Print raw OpenViking status as JSON",
    )

    tree = subparsers.add_parser("tree", help="Show a viking:// resource tree")
    tree.add_argument("uri", help="viking:// URI to inspect")
    tree.add_argument("-L", "--depth", type=int, default=2, help="Tree depth")

    import_local = subparsers.add_parser("import-local", help="Import a local file or folder")
    import_local.add_argument("path", help="Local file or folder path")
    import_local.add_argument(
        "--to",
        required=True,
        help="Target URI, for example viking://resources/my-corpus",
    )
    import_local.add_argument(
        "--no-resource-wait",
        action="store_true",
        help="Do not pass --wait to ov add-resource",
    )
    import_local.add_argument(
        "--no-queue-wait",
        action="store_true",
        help="Do not run ov wait after import",
    )

    search_web = subparsers.add_parser("search-web", help="Search the public web with AnySearch")
    _add_anysearch_arguments(search_web)
    search_web.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format. json is script-friendly; text is easier to read.",
    )

    fetch_web = subparsers.add_parser("fetch-web", help="Search with AnySearch and save markdown/json files")
    _add_anysearch_arguments(fetch_web)
    fetch_web.add_argument(
        "--output",
        default=None,
        help="Output directory. Default: data/web/<query-slug>",
    )

    sync = subparsers.add_parser("sync", help="Search the web, save markdown, and import it into OpenViking")
    _add_anysearch_arguments(sync)
    sync.add_argument(
        "--output",
        default=None,
        help="Output directory. Default: data/web/<query-slug>",
    )
    sync.add_argument(
        "--to",
        required=True,
        help="Target URI, for example viking://resources/my-topic",
    )
    sync.add_argument(
        "--no-resource-wait",
        action="store_true",
        help="Do not pass --wait to ov add-resource",
    )
    sync.add_argument(
        "--no-queue-wait",
        action="store_true",
        help="Do not run ov wait after import",
    )

    run_case_parser = subparsers.add_parser("run-case", help="Run a reusable YAML collection case")
    run_case_parser.add_argument("case", help="Path to a case YAML file")
    run_case_parser.add_argument(
        "--anysearch-url",
        default=_default_anysearch_url(),
        help="AnySearch API URL",
    )
    run_case_parser.add_argument(
        "--openviking-url",
        default=_default_openviking_url(),
        help="OpenViking server URL for retrieval checks",
    )
    run_case_parser.add_argument("--timeout", type=float, default=60.0)
    run_case_parser.add_argument(
        "--log",
        default="data/run_logs/runs.jsonl",
        help="JSONL run log path",
    )
    run_case_parser.add_argument(
        "--skip-import",
        action="store_true",
        help="Save local files only; do not import into OpenViking",
    )
    run_case_parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Do not run retrieval checks after import",
    )
    run_case_parser.add_argument(
        "--no-resource-wait",
        action="store_true",
        help="Do not pass --wait to ov add-resource",
    )
    run_case_parser.add_argument(
        "--no-queue-wait",
        action="store_true",
        help="Do not run ov wait after import",
    )
    run_case_parser.add_argument(
        "--mode",
        choices=("find", "search"),
        default="find",
        help="OpenViking retrieval endpoint to call for checks",
    )

    evolve_skill_parser = subparsers.add_parser(
        "evolve-skill",
        help="Generate skill-pattern suggestions from run logs",
    )
    evolve_skill_parser.add_argument(
        "--log",
        default="data/run_logs/runs.jsonl",
        help="JSONL run log path",
    )
    evolve_skill_parser.add_argument(
        "--output",
        default="data/skill_evolution",
        help="Output directory for generated suggestions",
    )

    forecast_parser = subparsers.add_parser("forecast", help="Run a forecast case and score the prediction")
    forecast_parser.add_argument("case", help="Path to a forecast case YAML file")
    forecast_parser.add_argument(
        "--answer",
        default=None,
        help="Answer JSON path. Default: <case>.answer.json",
    )
    forecast_parser.add_argument(
        "--anysearch-url",
        default=_default_anysearch_url(),
        help="AnySearch API URL",
    )
    forecast_parser.add_argument(
        "--openviking-url",
        default=_default_openviking_url(),
        help="OpenViking server URL for retrieval",
    )
    forecast_parser.add_argument("--timeout", type=float, default=60.0)
    forecast_parser.add_argument(
        "--llm-base-url",
        default=_default_llm_base_url(),
        help="OpenAI-compatible base URL",
    )
    forecast_parser.add_argument(
        "--llm-api-key",
        default=os.environ.get("ANYVIKING_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY"),
        help="LLM API key. Defaults to ANYVIKING_LLM_API_KEY or OPENAI_API_KEY.",
    )
    forecast_parser.add_argument(
        "--llm-model",
        default=os.environ.get("ANYVIKING_LLM_MODEL", "gpt-4o-mini"),
        help="OpenAI-compatible model name",
    )
    forecast_parser.add_argument(
        "--run-root",
        default="data/runs",
        help="Directory for trajectory and prediction files",
    )
    forecast_parser.add_argument(
        "--skip-import",
        action="store_true",
        help="Save files and forecast from local evidence only; do not import into OpenViking",
    )
    forecast_parser.add_argument(
        "--skip-score",
        action="store_true",
        help="Do not read the answer file or compute scores",
    )
    forecast_parser.add_argument(
        "--no-resource-wait",
        action="store_true",
        help="Do not pass --wait to ov add-resource",
    )
    forecast_parser.add_argument(
        "--no-queue-wait",
        action="store_true",
        help="Do not run ov wait after import",
    )
    forecast_parser.add_argument(
        "--mode",
        choices=("find", "search"),
        default="find",
        help="OpenViking retrieval endpoint to call",
    )
    forecast_parser.add_argument("--max-prompt-evidence", type=int, default=6)
    forecast_parser.add_argument(
        "--baseline-mode",
        choices=("anyviking", "no-retrieval", "naive-search"),
        default="anyviking",
        help="Forecast evaluation mode. anyviking uses case queries and OpenViking retrieval.",
    )
    forecast_parser.add_argument(
        "--baseline-group",
        default=None,
        help="Optional group name written to trajectory, for example anyviking_candidate.",
    )
    forecast_parser.add_argument(
        "--candidate-dir",
        default=None,
        help="Optional evolution candidate directory to apply before publishing.",
    )

    evolve = subparsers.add_parser("evolve", help="Manage forecast-driven skill evolution")
    evolve_subparsers = evolve.add_subparsers(dest="evolve_command", required=True)
    evolve_collect = evolve_subparsers.add_parser("collect", help="Collect forecast trajectories")
    evolve_collect.add_argument("--runs", default="data/runs", help="Run directory root")
    evolve_collect.add_argument("--output", default="data/evolution/collected.json")
    evolve_baselines = evolve_subparsers.add_parser("baselines", help="Write baseline metrics from eval trajectories")
    evolve_baselines.add_argument("--runs", default="data/runs", help="Run directory root")
    evolve_baselines.add_argument("--output", default="data/evolution/baselines.json")
    evolve_propose = evolve_subparsers.add_parser("propose", help="Generate a reviewable evolution candidate")
    evolve_propose.add_argument("--runs", default="data/runs", help="Run directory root")
    evolve_propose.add_argument("--output", default="data/evolution/candidates")
    evolve_validate = evolve_subparsers.add_parser("validate", help="Validate a candidate from summary data")
    evolve_validate.add_argument("candidate", help="Candidate directory")
    evolve_validate.add_argument("--output", default=None, help="Validation output path")
    evolve_validate.add_argument(
        "--baseline",
        default=None,
        help="Optional JSON with no_retrieval, naive_search, anyviking_baseline, and anyviking_candidate metrics",
    )
    evolve_publish = evolve_subparsers.add_parser("publish", help="Publish a validated candidate")
    evolve_publish.add_argument("candidate", help="Candidate directory")
    evolve_publish.add_argument("--skill-dir", default="skills/anyviking-research")
    evolve_run = evolve_subparsers.add_parser("run", help="Collect and propose from existing trajectories")
    evolve_run.add_argument("--runs", default="data/runs", help="Run directory root")
    evolve_run.add_argument("--output", default="data/evolution/candidates")
    evolve_iterate = evolve_subparsers.add_parser("iterate", help="Run one local propose/validate iteration")
    evolve_iterate.add_argument("--rounds", type=int, default=1)
    evolve_iterate.add_argument("--runs", default="data/runs", help="Run directory root")
    evolve_iterate.add_argument("--output", default="data/evolution/candidates")
    evolve_iterate.add_argument("--baseline", default=None, help="Optional baseline metrics JSON")
    evolve_iterate.add_argument("--publish", action="store_true", help="Publish when validation passes")
    evolve_iterate.add_argument("--skill-dir", default="skills/anyviking-research")

    search = subparsers.add_parser("search", help="Run semantic retrieval with OpenViking")
    search.add_argument("query", help="Natural-language question")
    search.add_argument(
        "--scope",
        default=None,
        help="Optional viking:// search scope, for example viking://resources/smoke-corpus/",
    )
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument(
        "--url",
        default=_default_openviking_url(),
        help="OpenViking server URL",
    )
    search.add_argument("--timeout", type=float, default=60.0)
    search.add_argument(
        "--mode",
        choices=("find", "search"),
        default="find",
        help="OpenViking retrieval endpoint to call",
    )
    search.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format. json is script-friendly; text is easier to read.",
    )
    search.add_argument(
        "--documents-only",
        action="store_true",
        help="Return original documents only; filter .abstract.md / .overview.md.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        checks = _run_doctor(args.url, timeout=args.timeout)
        if args.json:
            print(json.dumps({"ok": all(check["ok"] for check in checks), "checks": checks}, ensure_ascii=False, indent=2))
        else:
            _print_doctor(checks)
        return 0 if all(check["ok"] for check in checks if check["required"]) else 2

    if args.command == "health":
        try:
            with httpx.Client(timeout=args.timeout) as client:
                response = client.get(args.url.rstrip("/") + "/health")
                response.raise_for_status()
        except httpx.HTTPError as exc:
            print(f"OpenViking health check failed: {exc}", file=sys.stderr)
            return 2

        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "status":
        command = ["status"]
        if args.json:
            command.extend(["--output", "json"])
        return _run_ov(command)

    if args.command == "tree":
        if args.depth < 0:
            print("depth must be greater than or equal to 0", file=sys.stderr)
            return 2
        return _run_ov(["tree", args.uri, "-L", str(args.depth)])

    if args.command == "import-local":
        local_path = Path(args.path)
        if not local_path.exists():
            print(f"Local path does not exist: {local_path}", file=sys.stderr)
            return 2

        command = ["add-resource", str(local_path), "--to", args.to]
        if not args.no_resource_wait:
            command.append("--wait")

        exit_code = _run_ov(command)
        if exit_code != 0:
            return exit_code

        if not args.no_queue_wait:
            return _run_ov(["wait"])
        return 0

    if args.command == "search-web":
        try:
            response = _run_anysearch(args)
        except (RuntimeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

        if args.format == "json":
            print(json.dumps(_web_response_to_jsonable(response), ensure_ascii=False, indent=2))
        else:
            _print_web_results(response.query, response.results)
        return 0

    if args.command == "fetch-web":
        try:
            response = _run_anysearch(args)
            output = write_web_search_output(
                response,
                args.output or default_output_dir(args.query),
            )
        except (OSError, RuntimeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

        print(f"Saved AnySearch raw response: {output.raw_json_path}")
        print(f"Saved markdown corpus directory: {output.markdown_dir}")
        print(f"Saved fetch manifest: {output.manifest_path}")
        print(f"Markdown file count: {len(output.markdown_files)}")
        return 0

    if args.command == "sync":
        try:
            response = _run_anysearch(args)
            output = write_web_search_output(
                response,
                args.output or default_output_dir(args.query),
            )
        except (OSError, RuntimeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

        print(f"Saved markdown corpus directory: {output.markdown_dir}")
        if not output.markdown_files:
            print(
                "AnySearch returned no URL-backed results, so OpenViking import was skipped.",
                file=sys.stderr,
            )
            return 2

        command = ["add-resource", str(output.markdown_dir), "--to", args.to]
        if not args.no_resource_wait:
            command.append("--wait")

        exit_code = _run_ov(command)
        if exit_code != 0:
            return exit_code

        if not args.no_queue_wait:
            return _run_ov(["wait"])
        return 0

    if args.command == "run-case":
        connector = AnySearchConnector(
            base_url=args.anysearch_url,
            timeout=args.timeout,
        )

        def importer(markdown_dir: Path, target_uri: str) -> int:
            command = ["add-resource", str(markdown_dir), "--to", target_uri]
            if not args.no_resource_wait:
                command.append("--wait")
            exit_code = _run_ov(command)
            if exit_code != 0:
                return exit_code
            if not args.no_queue_wait:
                return _run_ov(["wait"])
            return 0

        retriever = OpenVikingRetriever(
            base_url=args.openviking_url,
            mode=args.mode,
            timeout=args.timeout,
        )

        def searcher(query: str, scope: str, top_k: int) -> list[SearchResult]:
            results = retriever.search(query, scope=scope, top_k=max(top_k * 5, top_k))
            return [result for result in results if not _is_generated_summary(result.uri)][:top_k]

        try:
            result = run_case(
                args.case,
                connector=connector,
                importer=None if args.skip_import else importer,
                searcher=None if args.skip_checks or args.skip_import else searcher,
                log_path=args.log,
                skip_import=args.skip_import,
                skip_checks=args.skip_checks or args.skip_import,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

        _print_case_result(result)
        return 0 if result.success else 2

    if args.command == "evolve-skill":
        try:
            output = evolve_skill(args.log, args.output)
        except (OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

        print(f"Read run log: {args.log}")
        print(f"Runs: {output.run_count}")
        print(f"Successful runs: {output.successful_count}")
        print(f"Summary: {output.summary_path}")
        print(f"Generated patterns: {output.patterns_path}")
        return 0

    if args.command == "forecast":
        if args.max_prompt_evidence <= 0:
            print("max-prompt-evidence must be greater than 0", file=sys.stderr)
            return 2
        if not args.skip_score and args.answer is not None and not Path(args.answer).exists():
            print(f"Answer file does not exist: {args.answer}", file=sys.stderr)
            return 2
        if not args.llm_api_key:
            print(
                "Missing LLM API key. Set ANYVIKING_LLM_API_KEY or OPENAI_API_KEY, "
                "or pass --llm-api-key.",
                file=sys.stderr,
            )
            return 2

        connector = AnySearchConnector(
            base_url=args.anysearch_url,
            timeout=args.timeout,
        )

        def importer(markdown_dir: Path, target_uri: str) -> int:
            command = ["add-resource", str(markdown_dir), "--to", target_uri]
            if not args.no_resource_wait:
                command.append("--wait")
            exit_code = _run_ov(command)
            if exit_code != 0:
                return exit_code
            if not args.no_queue_wait:
                return _run_ov(["wait"])
            return 0

        retriever = OpenVikingRetriever(
            base_url=args.openviking_url,
            mode=args.mode,
            timeout=args.timeout,
        )

        def searcher(query: str, scope: str, top_k: int) -> list[SearchResult]:
            results = retriever.search(query, scope=scope, top_k=max(top_k * 5, top_k))
            return [result for result in results if not _is_generated_summary(result.uri)][:top_k]

        predictor = OpenAICompatiblePredictor(
            base_url=args.llm_base_url,
            api_key=args.llm_api_key,
            model=args.llm_model,
            timeout=args.timeout,
        )
        try:
            result = forecast_case(
                args.case,
                connector=connector,
                predictor=predictor,
                importer=None if args.skip_import else importer,
                searcher=None if args.skip_import else searcher,
                answer_path=args.answer,
                run_root=args.run_root,
                skip_import=args.skip_import,
                skip_score=args.skip_score,
                max_prompt_evidence=args.max_prompt_evidence,
                baseline_mode=args.baseline_mode,
                baseline_group=args.baseline_group,
                candidate_dir=args.candidate_dir,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

        _print_forecast_result(result)
        return 0 if result.success else 2

    if args.command == "evolve":
        from anyviking_research.workflows.evolve import (
            collect_trajectories,
            iterate_once,
            propose_candidate,
            publish_candidate,
            validate_candidate,
            write_baseline_summary,
        )

        try:
            if args.evolve_command == "collect":
                output = collect_trajectories(args.runs, args.output)
                print(f"Collected trajectories: {output.trajectory_count}")
                print(f"Output: {output.output_path}")
                return 0
            if args.evolve_command == "baselines":
                output = write_baseline_summary(args.runs, args.output)
                print(f"Baseline groups: {', '.join(output.groups) if output.groups else '(none)'}")
                print(f"Output: {output.output_path}")
                return 0
            if args.evolve_command == "propose":
                output = propose_candidate(args.runs, args.output)
                print(f"Candidate: {output.candidate_dir}")
                print(f"Candidate summary: {output.candidate_path}")
                return 0
            if args.evolve_command == "validate":
                output = validate_candidate(args.candidate, args.output, baseline_path=args.baseline)
                print(f"Validation: {output.validation_path}")
                print(f"Passed: {output.passed}")
                return 0 if output.passed else 2
            if args.evolve_command == "publish":
                output = publish_candidate(args.candidate, args.skill_dir)
                print(f"Published: {output.published}")
                print(f"Skill dir: {output.skill_dir}")
                return 0 if output.published else 2
            if args.evolve_command == "run":
                output = propose_candidate(args.runs, args.output)
                print(f"Candidate: {output.candidate_dir}")
                print("Review and validate before publishing.")
                return 0
            if args.evolve_command == "iterate":
                if args.rounds != 1:
                    print("Only --rounds 1 is currently supported.", file=sys.stderr)
                    return 2
                output = iterate_once(
                    args.runs,
                    args.output,
                    baseline_path=args.baseline,
                    publish=args.publish,
                    skill_dir=args.skill_dir,
                )
                print(f"Candidate: {output.candidate.candidate_dir}")
                print(f"Validation: {output.validation.validation_path}")
                print(f"Passed: {output.validation.passed}")
                if output.publish is not None:
                    print(f"Published: {output.publish.published}")
                return 0 if output.validation.passed else 2
        except (OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

    if args.command == "search":
        retriever = OpenVikingRetriever(
            base_url=args.url,
            mode=args.mode,
            timeout=args.timeout,
        )
        try:
            fetch_k = max(args.top_k * 5, args.top_k) if args.documents_only else args.top_k
            results = retriever.search(args.query, scope=args.scope, top_k=fetch_k)
        except (RuntimeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

        if args.documents_only:
            results = [
                result for result in results if not _is_generated_summary(result.uri)
            ][: args.top_k]

        if args.format == "text":
            _print_text_results(args.query, args.scope, results)
        else:
            print(
                json.dumps(
                    {
                        "query": args.query,
                        "scope": args.scope,
                        "top_k": args.top_k,
                        "source": "openviking",
                        "documents_only": args.documents_only,
                        "result_count": len(results),
                        "results": [asdict(result) for result in results],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


def _run_ov(arguments: list[str]) -> int:
    executable = _find_ov_executable()
    if executable is None:
        print(
            "Could not find ov executable. Make sure OpenViking is installed in the current virtual environment.",
            file=sys.stderr,
        )
        return 2

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    completed = subprocess.run(
        [executable, *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="" if completed.stderr.endswith("\n") else "\n")
    return completed.returncode


def _run_doctor(base_url: str, *, timeout: float) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []

    checks.append(
        {
            "name": "python",
            "ok": sys.version_info >= (3, 12),
            "required": True,
            "detail": sys.version.split()[0],
        }
    )
    checks.append(
        {
            "name": "package",
            "ok": True,
            "required": True,
            "detail": _package_version("anyviking-research") or "editable/local",
        }
    )

    openviking_version = _package_version("openviking")
    checks.append(
        {
            "name": "openviking-package",
            "ok": openviking_version is not None,
            "required": True,
            "detail": openviking_version or "not installed",
        }
    )

    ov_executable = _find_ov_executable()
    checks.append(
        {
            "name": "ov-executable",
            "ok": ov_executable is not None,
            "required": True,
            "detail": ov_executable or "not found",
        }
    )

    config_path = Path("config/ov.conf")
    config_ok = config_path.exists()
    checks.append(
        {
            "name": "openviking-config",
            "ok": config_ok,
            "required": True,
            "detail": str(config_path) if config_ok else "missing config/ov.conf",
        }
    )

    anysearch_key_set = bool(os.environ.get("ANYSEARCH_API_KEY"))
    checks.append(
        {
            "name": "anysearch-api-key",
            "ok": anysearch_key_set,
            "required": False,
            "detail": "set" if anysearch_key_set else "not set; anonymous requests may still work",
        }
    )

    server_ok = False
    server_detail = "not checked"
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(base_url.rstrip("/") + "/health")
            response.raise_for_status()
            data = response.json()
            server_ok = bool(data.get("healthy") or data.get("status") == "ok")
            server_detail = json.dumps(data, ensure_ascii=False)
    except httpx.HTTPError as exc:
        server_detail = str(exc)
    checks.append(
        {
            "name": "openviking-server",
            "ok": server_ok,
            "required": False,
            "detail": server_detail,
        }
    )

    return checks


def _package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _print_doctor(checks: list[dict[str, object]]) -> None:
    print("AnyViking Research environment check")
    for check in checks:
        marker = "OK" if check["ok"] else ("WARN" if not check["required"] else "FAIL")
        print(f"- [{marker}] {check['name']}: {check['detail']}")


def _add_anysearch_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("query", help="Public web search query")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum result count")
    parser.add_argument(
        "--anysearch-url",
        default=_default_anysearch_url(),
        help="AnySearch API URL",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--domain",
        action="append",
        dest="domains",
        default=None,
        help="Restrict search to a domain. Can be passed multiple times.",
    )
    parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=None,
        help="Restrict search by AnySearch tag. Can be passed multiple times.",
    )
    parser.add_argument("--language", default=None, help="Language filter, for example zh or en")
    parser.add_argument("--zone", default=None, help="Regional search filter")
    parser.add_argument(
        "--provider",
        action="append",
        dest="providers",
        default=None,
        help="Restrict search provider. Can be passed multiple times.",
    )
    parser.add_argument(
        "--content-type",
        action="append",
        dest="content_types",
        default=None,
        help="Content type filter, for example web, news, or doc. Can be passed multiple times.",
    )
    parser.add_argument("--freshness", default=None, help="Freshness filter, for example day, week, month, or year")
    parser.add_argument("--from-time", default=None, help="Start time filter")
    parser.add_argument("--to-time", default=None, help="End time filter")


def _run_anysearch(args: argparse.Namespace):
    connector = AnySearchConnector(
        base_url=args.anysearch_url,
        timeout=args.timeout,
    )
    return connector.search(
        args.query,
        max_results=args.max_results,
        domains=args.domains,
        tags=args.tags,
        content_types=args.content_types,
        zone=args.zone,
        language=args.language,
        providers=args.providers,
        freshness=args.freshness,
        from_time=args.from_time,
        to_time=args.to_time,
    )


def _default_openviking_url() -> str:
    return os.environ.get("OPENVIKING_URL", DEFAULT_OPENVIKING_URL)


def _default_anysearch_url() -> str:
    return os.environ.get("ANYSEARCH_API_URL", DEFAULT_ANYSEARCH_URL)


def _default_llm_base_url() -> str:
    return os.environ.get("ANYVIKING_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or DEFAULT_LLM_BASE_URL


def _web_response_to_jsonable(response) -> dict[str, object]:
    return {
        "query": response.query,
        "provider": response.provider,
        "metadata": response.metadata,
        "result_count": len(response.results),
        "results": [asdict(result) for result in response.results],
    }


def _print_web_results(query: str, results) -> None:
    print(f"Query: {query}")
    print(f"Result count: {len(results)}")
    for index, result in enumerate(results, start=1):
        print("")
        print(f"{index}. {result.title}")
        print(f"   URL: {result.url}")
        if result.source:
            print(f"   Source: {result.source}")
        if result.score is not None:
            print(f"   Score: {result.score:.4f}")
        if result.description:
            print(f"   Description: {result.description}")
        elif result.content:
            preview = result.content.replace("\n", " ")[:240]
            print(f"   Content: {preview}")


def _print_case_result(result) -> None:
    print(f"Case: {result.case.id}")
    print(f"Title: {result.case.title}")
    print(f"Question: {result.case.question}")
    print(f"Search results: {result.search_result_count}")
    print(f"Markdown files: {result.markdown_count}")
    print(f"Markdown directory: {result.output.markdown_dir}")
    print(f"Evidence pack: {result.evidence_pack_path}")
    print(f"Target URI: {result.case.target_uri}")
    print(f"Imported: {result.imported}")
    if result.import_exit_code is not None:
        print(f"Import exit code: {result.import_exit_code}")
    if result.retrieval_checks:
        passed = sum(1 for check in result.retrieval_checks if check.passed)
        print(f"Retrieval checks: {passed}/{len(result.retrieval_checks)} passed")
    else:
        print("Retrieval checks: skipped")
    print(f"Run log: {result.log_path}")


def _print_forecast_result(result) -> None:
    print(f"Case: {result.case.id}")
    print(f"Question: {result.case.question}")
    print(f"Markdown files: {len(result.output.markdown_files)}")
    print(f"Target URI: {result.case.target_uri}")
    print(f"Imported: {result.imported}")
    print(f"Predicted answer: {result.prediction.predicted_answer}")
    print("Probabilities:")
    for option, probability in result.prediction.probabilities.items():
        print(f"- {option}: {probability:.4f}")
    if result.score is not None:
        print(f"Correct: {result.score.correct}")
        print(f"Brier: {result.score.brier:.4f}")
    else:
        print("Score: skipped")
    print(f"Trajectory: {result.trajectory_path}")


def _find_ov_executable() -> str | None:
    executable_name = "ov.exe" if os.name == "nt" else "ov"
    venv_root = Path(sys.executable).resolve().parent.parent

    candidates = [
        venv_root / "Lib" / "site-packages" / "openviking" / "bin" / executable_name,
        venv_root / "lib" / "site-packages" / "openviking" / "bin" / executable_name,
        Path(sys.executable).resolve().parent / executable_name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    found = shutil.which("ov")
    if found:
        return found

    return None


def _print_text_results(query: str, scope: str | None, results: list[SearchResult]) -> None:
    print(f"Query: {query}")
    print(f"Scope: {scope or '(all)'}")
    print(f"Result count: {len(results)}")
    for index, result in enumerate(results, start=1):
        print("")
        print(f"{index}. {result.title}")
        print(f"   URI: {result.uri}")
        if result.score is not None:
            print(f"   Score: {result.score:.4f}")
        if result.snippet:
            print(f"   Snippet: {result.snippet}")


def _is_generated_summary(uri: str) -> bool:
    tail = uri.rstrip("/").rsplit("/", 1)[-1].lower()
    return tail in {".abstract.md", ".overview.md"}


if __name__ == "__main__":
    raise SystemExit(main())
