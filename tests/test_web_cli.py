import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from anyviking_research.cli import main
from anyviking_research.connectors.base import WebSearchResponse, WebSearchResult
from anyviking_research.retrievers.base import SearchResult


class FakeAnySearchConnector:
    last_init_kwargs: dict[str, object] | None = None

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        type(self).last_init_kwargs = kwargs

    def search(self, query: str, **kwargs) -> WebSearchResponse:
        return WebSearchResponse(
            query=query,
            provider="anysearch",
            results=[
                WebSearchResult(
                    title="Result",
                    url="https://example.com/result",
                    description="Description",
                    content="Content",
                    source="web",
                    score=0.7,
                )
            ],
            metadata={"request_id": "req_demo"},
        )


class WebCliTests(unittest.TestCase):
    def test_doctor_reports_json_checks(self) -> None:
        fake_checks = [
            {"name": "python", "ok": True, "required": True, "detail": "3.12"},
            {"name": "openviking-server", "ok": False, "required": False, "detail": "offline"},
        ]

        with patch("anyviking_research.cli._run_doctor", lambda url, timeout: fake_checks):
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["doctor", "--json"])

        data = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertFalse(data["ok"])
        self.assertEqual(data["checks"][0]["name"], "python")

    def test_doctor_fails_when_required_check_fails(self) -> None:
        fake_checks = [
            {"name": "python", "ok": False, "required": True, "detail": "3.11"},
        ]

        with patch("anyviking_research.cli._run_doctor", lambda url, timeout: fake_checks):
            with redirect_stdout(StringIO()):
                exit_code = main(["doctor"])

        self.assertEqual(exit_code, 2)

    def test_doctor_uses_openviking_url_from_environment(self) -> None:
        seen: dict[str, object] = {}

        def fake_run_doctor(url: str, timeout: float):
            seen["url"] = url
            return [{"name": "python", "ok": True, "required": True, "detail": "3.12"}]

        with patch.dict("os.environ", {"OPENVIKING_URL": "http://env-openviking:1933"}, clear=False):
            with patch("anyviking_research.cli._run_doctor", fake_run_doctor):
                with redirect_stdout(StringIO()):
                    exit_code = main(["doctor"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(seen["url"], "http://env-openviking:1933")

    def test_fetch_web_writes_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("anyviking_research.cli.AnySearchConnector", FakeAnySearchConnector):
                with redirect_stdout(StringIO()):
                    exit_code = main(
                        [
                            "fetch-web",
                            "demo query",
                            "--output",
                            temp_dir,
                            "--max-results",
                            "1",
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertTrue((Path(temp_dir) / "raw" / "anysearch_response.json").exists())
            self.assertTrue((Path(temp_dir) / "manifest.json").exists())
            self.assertEqual(len(list((Path(temp_dir) / "markdown").glob("*.md"))), 1)

    def test_search_web_uses_anysearch_url_from_environment(self) -> None:
        FakeAnySearchConnector.last_init_kwargs = None

        with patch.dict("os.environ", {"ANYSEARCH_API_URL": "https://env.anysearch.test"}, clear=False):
            with patch("anyviking_research.cli.AnySearchConnector", FakeAnySearchConnector):
                with redirect_stdout(StringIO()):
                    exit_code = main(["search-web", "demo query", "--format", "json"])

        self.assertEqual(exit_code, 0)
        self.assertIsNotNone(FakeAnySearchConnector.last_init_kwargs)
        self.assertEqual(
            FakeAnySearchConnector.last_init_kwargs["base_url"],
            "https://env.anysearch.test",
        )

    def test_sync_imports_markdown_directory(self) -> None:
        commands: list[list[str]] = []

        def fake_run_ov(arguments: list[str]) -> int:
            commands.append(arguments)
            return 0

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("anyviking_research.cli.AnySearchConnector", FakeAnySearchConnector):
                with patch("anyviking_research.cli._run_ov", fake_run_ov):
                    with redirect_stdout(StringIO()):
                        exit_code = main(
                            [
                                "sync",
                                "demo query",
                                "--output",
                                temp_dir,
                                "--to",
                                "viking://resources/demo",
                                "--max-results",
                                "1",
                            ]
                        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(commands[0][0], "add-resource")
        self.assertEqual(commands[0][2:], ["--to", "viking://resources/demo", "--wait"])
        self.assertTrue(commands[0][1].endswith("markdown"))
        self.assertEqual(commands[1], ["wait"])

    def test_sync_stops_when_no_markdown_files_are_created(self) -> None:
        class EmptyAnySearchConnector:
            def __init__(self, **kwargs) -> None:
                pass

            def search(self, query: str, **kwargs) -> WebSearchResponse:
                return WebSearchResponse(
                    query=query,
                    provider="anysearch",
                    results=[],
                )

        commands: list[list[str]] = []

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("anyviking_research.cli.AnySearchConnector", EmptyAnySearchConnector):
                with patch("anyviking_research.cli._run_ov", lambda arguments: commands.append(arguments) or 0):
                    with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                        exit_code = main(
                            [
                                "sync",
                                "empty query",
                                "--output",
                                temp_dir,
                                "--to",
                                "viking://resources/empty",
                            ]
                        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(commands, [])

    def test_run_case_can_skip_import_and_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_path = root / "case.yaml"
            output_dir = root / "case-output"
            log_path = root / "runs.jsonl"
            case_path.write_text(
                f"""
id: cli_case
title: CLI Case
question: Can the CLI run a case?
queries:
  - demo query
storage:
  output_dir: {output_dir.as_posix()}
  target_uri: viking://resources/cli-case
""".strip(),
                encoding="utf-8",
            )

            with patch("anyviking_research.cli.AnySearchConnector", FakeAnySearchConnector):
                with redirect_stdout(StringIO()):
                    exit_code = main(
                        [
                            "run-case",
                            str(case_path),
                            "--skip-import",
                            "--log",
                            str(log_path),
                        ]
                    )
            evidence_pack_exists = (output_dir / "evidence_pack.md").exists()
            log_exists = log_path.exists()

        self.assertEqual(exit_code, 0)
        self.assertTrue(evidence_pack_exists)
        self.assertTrue(log_exists)

    def test_run_case_runs_import_and_retrieval_checks(self) -> None:
        commands: list[list[str]] = []

        class FakeOpenVikingRetriever:
            def __init__(self, **kwargs) -> None:
                pass

            def search(self, query: str, scope: str | None = None, top_k: int = 5):
                return [
                    SearchResult(
                        title="Result",
                        uri="viking://resources/cli-case/result.md",
                        snippet="Snippet",
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
id: cli_case
title: CLI Case
question: Can the CLI run a case?
queries:
  - demo query
storage:
  output_dir: {output_dir.as_posix()}
  target_uri: viking://resources/cli-case
retrieval_checks:
  - query: What did it find?
    top_k: 1
""".strip(),
                encoding="utf-8",
            )

            with patch("anyviking_research.cli.AnySearchConnector", FakeAnySearchConnector):
                with patch("anyviking_research.cli.OpenVikingRetriever", FakeOpenVikingRetriever):
                    with patch("anyviking_research.cli._run_ov", lambda arguments: commands.append(arguments) or 0):
                        with redirect_stdout(StringIO()):
                            exit_code = main(
                                [
                                    "run-case",
                                    str(case_path),
                                    "--log",
                                    str(log_path),
                                ]
                            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(commands[0][0], "add-resource")
        self.assertEqual(commands[0][2:], ["--to", "viking://resources/cli-case", "--wait"])
        self.assertEqual(commands[1], ["wait"])

    def test_evolve_skill_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            log_path = root / "runs.jsonl"
            output_dir = root / "skill_evolution"
            log_path.write_text(
                json.dumps(
                    {
                        "case_id": "oracleproto_demo",
                        "queries": ["demo query"],
                        "search": {"freshness": "month", "language": "en", "content_types": ["web"]},
                        "tags": ["oracleproto"],
                        "target_uri": "viking://resources/forecast/oracleproto/demo",
                        "retrieval_checks": [{"passed": True}],
                        "retrieval_passed": 1,
                        "success": True,
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                exit_code = main(
                    [
                        "evolve-skill",
                        "--log",
                        str(log_path),
                        "--output",
                        str(output_dir),
                    ]
                )

            summary_exists = (output_dir / "summary.json").exists()
            patterns_exists = (output_dir / "generated_patterns.md").exists()

        self.assertEqual(exit_code, 0)
        self.assertTrue(summary_exists)
        self.assertTrue(patterns_exists)


if __name__ == "__main__":
    unittest.main()
