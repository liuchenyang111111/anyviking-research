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
from anyviking_research.workflows.research import (
    ResearchReport,
    report_to_jsonable,
    run_research,
    write_markdown_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ar",
        description=(
            "AnySearch upstream web discovery plus OpenViking downstream "
            "indexing, retrieval, and research drafts."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check local installation and runtime readiness")
    doctor.add_argument(
        "--url",
        default="http://127.0.0.1:1933",
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
        default="http://127.0.0.1:1933",
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
        default="http://127.0.0.1:1933",
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

    research = subparsers.add_parser("research", help="Generate a retrieval-based research draft from YAML questions")
    research.add_argument("config", help="Research question YAML path")
    research.add_argument(
        "--output",
        default="reports/research_draft.md",
        help="Output markdown file path",
    )
    research.add_argument("--top-k", type=int, default=5)
    research.add_argument(
        "--fetch-k",
        type=int,
        default=None,
        help="Candidate results to fetch per question before filtering.",
    )
    research.add_argument(
        "--dedupe",
        choices=("section", "none"),
        default="section",
        help="Dedupe strategy. section keeps each URI once per section; none keeps raw results.",
    )
    research.add_argument(
        "--no-citation-stats",
        action="store_true",
        help="Do not include citation statistics in the report or JSON.",
    )
    research.add_argument(
        "--min-results-per-section",
        type=int,
        default=1,
        help="Minimum expected result count per section before adding quality notes.",
    )
    research.add_argument(
        "--url",
        default="http://127.0.0.1:1933",
        help="OpenViking server URL",
    )
    research.add_argument("--timeout", type=float, default=60.0)
    research.add_argument(
        "--include-summaries",
        action="store_true",
        help="Include OpenViking-generated .abstract.md / .overview.md files.",
    )
    research.add_argument(
        "--keep-unhelpful",
        action="store_true",
        help="Keep clearly unhelpful retrieval results.",
    )
    research.add_argument(
        "--json",
        action="store_true",
        help="Also print the JSON summary to the terminal.",
    )
    research.add_argument(
        "--json-output",
        default=None,
        help="Optional JSON output file path for scripts or agents.",
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

    if args.command == "research":
        try:
            report = run_research(
                args.config,
                base_url=args.url,
                top_k=args.top_k,
                fetch_k=args.fetch_k,
                dedupe=args.dedupe,
                include_citation_stats=not args.no_citation_stats,
                min_results_per_section=args.min_results_per_section,
                documents_only=not args.include_summaries,
                filter_unhelpful=not args.keep_unhelpful,
                timeout=args.timeout,
            )
            output_path = write_markdown_report(report, args.output)
            json_output_path = _write_json_report(report, args.json_output) if args.json_output else None
        except (OSError, RuntimeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

        if args.json:
            print(json.dumps(report_to_jsonable(report), ensure_ascii=False, indent=2))
        else:
            print(f"Generated retrieval research draft: {output_path}")
            if json_output_path is not None:
                print(f"Generated JSON retrieval results: {json_output_path}")
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
        default="https://api.anysearch.com",
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


def _write_json_report(report: ResearchReport, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report_to_jsonable(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    raise SystemExit(main())
