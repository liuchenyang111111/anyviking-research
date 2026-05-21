import json
import tempfile
import unittest
from pathlib import Path

from ov_search_skill.cli import _is_generated_summary, _write_json_report
from ov_search_skill.retrievers.base import SearchResult
from ov_search_skill.workflows.research import (
    ResearchQuestion,
    ResearchReport,
    _candidate_limit,
    _is_unhelpful_result,
)


class CliHelperTests(unittest.TestCase):
    def test_generated_summary_filter_matches_openviking_summary_files(self) -> None:
        self.assertTrue(_is_generated_summary("viking://resources/demo/.abstract.md"))
        self.assertTrue(_is_generated_summary("viking://resources/demo/.overview.md"))

    def test_generated_summary_filter_keeps_original_documents(self) -> None:
        self.assertFalse(_is_generated_summary("viking://resources/demo/article.md"))
        self.assertFalse(_is_generated_summary("viking://resources/demo/overview-notes.md"))

    def test_unhelpful_result_filter_catches_placeholder_answers(self) -> None:
        result = SearchResult(
            title="bad",
            uri="viking://resources/demo/bad.md",
            snippet="抱歉，没有找到相关的结果。",
        )

        self.assertTrue(_is_unhelpful_result(result))

    def test_unhelpful_result_filter_catches_cannot_answer_answers(self) -> None:
        result = SearchResult(
            title="bad",
            uri="viking://resources/demo/bad.md",
            snippet="您的问题我无法回答。",
        )

        self.assertTrue(_is_unhelpful_result(result))

    def test_unhelpful_result_filter_keeps_real_snippets(self) -> None:
        result = SearchResult(
            title="good",
            uri="viking://resources/demo/good.md",
            snippet="本文分析特朗普访华期间中美双方的贸易、科技与台湾议题。",
        )

        self.assertFalse(_is_unhelpful_result(result))

    def test_candidate_limit_fetches_more_when_filtering(self) -> None:
        self.assertEqual(
            _candidate_limit(
                5,
                fetch_k=None,
                documents_only=True,
                filter_unhelpful=True,
            ),
            40,
        )

    def test_candidate_limit_respects_explicit_fetch_k(self) -> None:
        self.assertEqual(
            _candidate_limit(
                5,
                fetch_k=12,
                documents_only=True,
                filter_unhelpful=True,
            ),
            12,
        )

    def test_write_json_report_creates_structured_file(self) -> None:
        question = ResearchQuestion(
            id="demo",
            heading="Demo",
            question="What is indexed?",
        )
        result = SearchResult(
            title="doc",
            uri="viking://resources/demo/doc.md",
            snippet="A useful result.",
            score=0.8,
        )
        report = ResearchReport(
            title="Demo Report",
            scope="viking://resources/demo",
            questions=[question],
            results_by_id={"demo": [result]},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "nested" / "report.json"
            written_path = _write_json_report(report, output_path)
            data = json.loads(written_path.read_text(encoding="utf-8"))

        self.assertEqual(data["title"], "Demo Report")
        self.assertEqual(data["sections"][0]["results"][0]["uri"], result.uri)


if __name__ == "__main__":
    unittest.main()
