import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from anyviking_research.connectors.base import WebSearchResponse, WebSearchResult
from anyviking_research.retrievers.base import SearchResult
from anyviking_research.workflows.run_case import load_case, run_case


class FakeCaseConnector:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def search(self, query: str, **kwargs) -> WebSearchResponse:
        self.queries.append(query)
        return WebSearchResponse(
            query=query,
            provider="anysearch",
            results=[
                WebSearchResult(
                    title=f"Result for {query}",
                    url="https://example.com/shared",
                    description="Short description",
                    content=f"Content for {query}",
                    source="web",
                )
            ],
            metadata={"query": query},
        )


class RunCaseWorkflowTests(unittest.TestCase):
    def test_load_case_reads_minimal_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            case_path = Path(temp_dir) / "case.yaml"
            case_path.write_text(
                """
id: demo_case
title: Demo Case
question: Will this demo work?
queries:
  - demo query
storage:
  output_dir: data/cases/demo
  target_uri: viking://resources/demo
retrieval_checks:
  - query: What does the demo say?
    top_k: 2
""".strip(),
                encoding="utf-8",
            )

            case = load_case(case_path)

        self.assertEqual(case.id, "demo_case")
        self.assertEqual(case.queries, ["demo query"])
        self.assertEqual(case.target_uri, "viking://resources/demo")
        self.assertEqual(case.retrieval_checks[0].top_k, 2)

    def test_run_case_writes_outputs_log_and_calls_importer_and_searcher(self) -> None:
        imported: list[tuple[Path, str]] = []
        searched: list[tuple[str, str, int]] = []

        def importer(markdown_dir: Path, target_uri: str) -> int:
            imported.append((markdown_dir, target_uri))
            return 0

        def searcher(query: str, scope: str, top_k: int) -> list[SearchResult]:
            searched.append((query, scope, top_k))
            return [
                SearchResult(
                    title="Demo",
                    uri="viking://resources/demo/doc.md",
                    snippet="Demo snippet",
                    source="openviking",
                )
            ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_path = root / "case.yaml"
            output_dir = root / "case-output"
            log_path = root / "runs.jsonl"
            case_path.write_text(
                f"""
id: demo_case
title: Demo Case
question: Will this demo work?
queries:
  - demo query one
  - demo query two
search:
  max_results: 2
storage:
  output_dir: {output_dir.as_posix()}
  target_uri: viking://resources/demo
retrieval_checks:
  - query: What does the demo say?
    top_k: 2
tags:
  - demo
""".strip(),
                encoding="utf-8",
            )

            connector = FakeCaseConnector()
            result = run_case(
                case_path,
                connector=connector,
                importer=importer,
                searcher=searcher,
                log_path=log_path,
                fetched_at=datetime(2026, 6, 5, tzinfo=timezone.utc),
            )

            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            log_record = json.loads(log_path.read_text(encoding="utf-8").strip())
            evidence_pack_exists = (output_dir / "evidence_pack.md").exists()

        self.assertEqual(connector.queries, ["demo query one", "demo query two"])
        self.assertEqual(result.search_result_count, 1)
        self.assertEqual(result.markdown_count, 1)
        self.assertTrue(result.success)
        self.assertEqual(imported[0][1], "viking://resources/demo")
        self.assertEqual(searched[0], ("What does the demo say?", "viking://resources/demo", 2))
        self.assertEqual(manifest["markdown_count"], 1)
        self.assertEqual(log_record["case_id"], "demo_case")
        self.assertEqual(log_record["retrieval_passed"], 1)
        self.assertTrue(evidence_pack_exists)


if __name__ == "__main__":
    unittest.main()
