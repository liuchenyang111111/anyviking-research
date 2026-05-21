from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import httpx

from ov_search_skill.retrievers.base import SearchResult
from ov_search_skill.retrievers.openviking import OpenVikingRetriever
from ov_search_skill.workflows.research import (
    ResearchReport,
    report_to_jsonable,
    run_research,
    write_markdown_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ov-search-skill",
        description="搜索 OpenViking 本地语料，并返回结构化结果。",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    health = subparsers.add_parser("health", help="检查 OpenViking 服务健康状态")
    health.add_argument(
        "--url",
        default="http://127.0.0.1:1933",
        help="OpenViking 服务地址",
    )
    health.add_argument("--timeout", type=float, default=10.0)

    status = subparsers.add_parser("status", help="查看 OpenViking 服务和队列状态")
    status.add_argument(
        "--json",
        action="store_true",
        help="用 JSON 输出 OpenViking status 原始信息",
    )

    tree = subparsers.add_parser("tree", help="查看 viking:// 资源树")
    tree.add_argument("uri", help="要查看的 viking:// URI")
    tree.add_argument("-L", "--depth", type=int, default=2, help="资源树展开层级")

    import_local = subparsers.add_parser("import-local", help="导入本地文件或文件夹")
    import_local.add_argument("path", help="本地文件或文件夹路径")
    import_local.add_argument(
        "--to",
        required=True,
        help="导入目标 URI，例如 viking://resources/my-corpus",
    )
    import_local.add_argument(
        "--no-resource-wait",
        action="store_true",
        help="不向 ov add-resource 传 --wait",
    )
    import_local.add_argument(
        "--no-queue-wait",
        action="store_true",
        help="导入后不执行 ov wait",
    )

    search = subparsers.add_parser("search", help="执行语义检索")
    search.add_argument("query", help="自然语言问题")
    search.add_argument(
        "--scope",
        default=None,
        help="可选 viking:// 检索范围，例如 viking://resources/smoke-corpus/",
    )
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument(
        "--url",
        default="http://127.0.0.1:1933",
        help="OpenViking 服务地址",
    )
    search.add_argument("--timeout", type=float, default=60.0)
    search.add_argument(
        "--mode",
        choices=("find", "search"),
        default="find",
        help="调用 OpenViking 的哪个检索端点",
    )
    search.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="输出格式。json 适合脚本和 AI Agent，text 适合人阅读。",
    )
    search.add_argument(
        "--documents-only",
        action="store_true",
        help="只返回原始文档，过滤 OpenViking 生成的 .abstract.md / .overview.md。",
    )

    research = subparsers.add_parser("research", help="按 YAML 问题列表生成检索型调研草稿")
    research.add_argument("config", help="调研问题 YAML 配置路径")
    research.add_argument(
        "--output",
        default="reports/research_draft.md",
        help="输出 markdown 文件路径",
    )
    research.add_argument("--top-k", type=int, default=5)
    research.add_argument(
        "--fetch-k",
        type=int,
        default=None,
        help="每个问题先向 OpenViking 拉取多少候选结果；过滤噪声较多时可以调大。",
    )
    research.add_argument(
        "--dedupe",
        choices=("section", "none"),
        default="section",
        help="去重策略。section 表示同一章节内同一 URI 只保留一次；none 表示保留原始结果。",
    )
    research.add_argument(
        "--no-citation-stats",
        action="store_true",
        help="不在报告和 JSON 中生成引用统计。",
    )
    research.add_argument(
        "--min-results-per-section",
        type=int,
        default=1,
        help="每个章节期望的最低结果数，低于该值时生成质量提示。",
    )
    research.add_argument(
        "--url",
        default="http://127.0.0.1:1933",
        help="OpenViking 服务地址",
    )
    research.add_argument("--timeout", type=float, default=60.0)
    research.add_argument(
        "--include-summaries",
        action="store_true",
        help="包含 OpenViking 自动生成的 .abstract.md / .overview.md。",
    )
    research.add_argument(
        "--keep-unhelpful",
        action="store_true",
        help="保留明显无效的检索结果，例如“抱歉，没有找到相关结果”。",
    )
    research.add_argument(
        "--json",
        action="store_true",
        help="同时在终端输出 JSON 摘要。",
    )
    research.add_argument(
        "--json-output",
        default=None,
        help="可选 JSON 输出文件路径，适合后续脚本或 Agent 读取。",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

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
            print(f"已生成检索型调研草稿：{output_path}")
            if json_output_path is not None:
                print(f"已生成 JSON 检索结果：{json_output_path}")
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


def _find_ov_executable() -> str | None:
    executable_name = "ov.exe" if os.name == "nt" else "ov"
    sibling = Path(sys.executable).resolve().parent / executable_name
    if sibling.exists():
        return str(sibling)

    found = shutil.which("ov")
    if found:
        return found

    return None


def _print_text_results(query: str, scope: str | None, results: list[SearchResult]) -> None:
    print(f"问题: {query}")
    print(f"范围: {scope or '(全部)'}")
    print(f"结果数: {len(results)}")
    for index, result in enumerate(results, start=1):
        print("")
        print(f"{index}. {result.title}")
        print(f"   URI: {result.uri}")
        if result.score is not None:
            print(f"   Score: {result.score:.4f}")
        if result.snippet:
            print(f"   摘要: {result.snippet}")


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
