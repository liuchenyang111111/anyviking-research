import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from anyviking_research.connectors.base import WebSearchResponse, WebSearchResult
from anyviking_research.workflows.fetch_web import (
    default_output_dir,
    write_web_search_output,
)


class FetchWebWorkflowTests(unittest.TestCase):
    def test_default_output_dir_slugifies_query(self) -> None:
        self.assertEqual(
            default_output_dir("AI Search: Tools?", root="data/web"),
            Path("data/web") / "ai-search-tools",
        )

    def test_write_web_search_output_creates_raw_markdown_and_manifest(self) -> None:
        response = WebSearchResponse(
            query="AI search tools",
            provider="anysearch",
            metadata={"request_id": "req_demo"},
            results=[
                WebSearchResult(
                    title="AI Search Tools",
                    url="https://example.com/ai-search",
                    description="A short description.",
                    content="A longer body.",
                    source="web",
                    score=0.8,
                    quality_score=0.9,
                    published_at="2026-05-01T00:00:00Z",
                )
            ],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output = write_web_search_output(
                response,
                temp_dir,
                fetched_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
            )

            raw = json.loads(output.raw_json_path.read_text(encoding="utf-8"))
            manifest = json.loads(output.manifest_path.read_text(encoding="utf-8"))
            markdown = output.markdown_files[0].read_text(encoding="utf-8")

        self.assertEqual(raw["query"], "AI search tools")
        self.assertEqual(raw["results"][0]["url"], "https://example.com/ai-search")
        self.assertEqual(manifest["markdown_count"], 1)
        self.assertIn("source_url: https://example.com/ai-search", markdown)
        self.assertIn("# AI Search Tools", markdown)
        self.assertIn("A longer body.", markdown)


if __name__ == "__main__":
    unittest.main()
