import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from anyviking_research.cli import main
from anyviking_research.connectors.base import WebSearchResponse, WebSearchResult


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


if __name__ == "__main__":
    unittest.main()
