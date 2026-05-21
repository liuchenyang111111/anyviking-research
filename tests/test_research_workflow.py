import tempfile
import unittest
from pathlib import Path

from ov_search_skill.retrievers.base import SearchResult
from ov_search_skill.workflows.research import (
    ResearchQuestion,
    ResearchReport,
    _build_citation_stats,
    _build_quality_warnings,
    _dedupe_results_by_uri,
    load_questions,
    render_markdown,
    report_to_jsonable,
)


class ResearchWorkflowTests(unittest.TestCase):
    def test_load_questions_reads_minimal_yaml_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "questions.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        'topic_title: "测试调研"',
                        'ov_root_uri: "viking://resources/demo"',
                        "sections:",
                        "  - id: background",
                        '    heading: "背景"',
                        '    question: "请检索背景信息"',
                    ]
                ),
                encoding="utf-8",
            )

            title, scope, questions = load_questions(config_path)

        self.assertEqual(title, "测试调研")
        self.assertEqual(scope, "viking://resources/demo")
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].id, "background")
        self.assertEqual(questions[0].heading, "背景")
        self.assertEqual(questions[0].question, "请检索背景信息")

    def test_load_questions_rejects_missing_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "questions.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "sections:",
                        "  - id: background",
                        '    question: "请检索背景信息"',
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "ov_root_uri or scope"):
                load_questions(config_path)

    def test_render_markdown_includes_question_and_viking_uri(self) -> None:
        question = ResearchQuestion(
            id="background",
            heading="背景",
            question="请检索背景信息",
        )
        result = SearchResult(
            title="demo",
            uri="viking://resources/demo/doc.md",
            snippet="这是一条测试摘要。",
            score=0.9,
        )
        report = ResearchReport(
            title="测试调研",
            scope="viking://resources/demo",
            questions=[question],
            results_by_id={"background": [result]},
        )

        markdown = render_markdown(report)

        self.assertIn("# 测试调研", markdown)
        self.assertIn("### 1. 背景", markdown)
        self.assertIn("请检索背景信息", markdown)
        self.assertIn("viking://resources/demo/doc.md", markdown)

    def test_report_to_jsonable_keeps_structured_results(self) -> None:
        question = ResearchQuestion(
            id="background",
            heading="背景",
            question="请检索背景信息",
        )
        result = SearchResult(
            title="demo",
            uri="viking://resources/demo/doc.md",
            snippet="这是一条测试摘要。",
            score=0.9,
        )
        report = ResearchReport(
            title="测试调研",
            scope="viking://resources/demo",
            questions=[question],
            results_by_id={"background": [result]},
        )

        data = report_to_jsonable(report)

        self.assertEqual(data["title"], "测试调研")
        self.assertEqual(data["question_count"], 1)
        self.assertEqual(data["sections"][0]["results"][0]["uri"], result.uri)
        self.assertIn("citation_stats", data)
        self.assertIn("quality_warnings", data)

    def test_dedupe_results_by_uri_keeps_highest_scored_result(self) -> None:
        low_score = SearchResult(
            title="doc low",
            uri="viking://resources/demo/doc.md",
            snippet="low",
            score=0.2,
        )
        high_score = SearchResult(
            title="doc high",
            uri="viking://resources/demo/doc.md",
            snippet="high",
            score=0.8,
        )
        other = SearchResult(
            title="other",
            uri="viking://resources/demo/other.md",
            snippet="other",
            score=0.5,
        )

        results = _dedupe_results_by_uri([low_score, other, high_score])

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, "doc high")
        self.assertEqual(results[1].title, "other")

    def test_build_citation_stats_counts_reused_documents(self) -> None:
        questions = [
            ResearchQuestion(id="market", heading="市场", question="市场问题"),
            ResearchQuestion(id="roadmap", heading="路线", question="路线问题"),
        ]
        shared = SearchResult(
            title="shared",
            uri="viking://resources/demo/shared.md",
            snippet="shared",
            score=0.7,
        )
        stronger_shared = SearchResult(
            title="shared",
            uri="viking://resources/demo/shared.md",
            snippet="shared again",
            score=0.9,
        )
        unique = SearchResult(
            title="unique",
            uri="viking://resources/demo/unique.md",
            snippet="unique",
            score=0.5,
        )

        stats = _build_citation_stats(
            questions,
            {
                "market": [shared, unique],
                "roadmap": [stronger_shared],
            },
        )

        self.assertEqual(stats[0].uri, shared.uri)
        self.assertEqual(stats[0].count, 2)
        self.assertEqual(stats[0].section_headings, ["市场", "路线"])
        self.assertEqual(stats[0].best_score, 0.9)

    def test_build_quality_warnings_detects_low_coverage_and_high_reuse(self) -> None:
        questions = [
            ResearchQuestion(id="a", heading="A", question="A?"),
            ResearchQuestion(id="b", heading="B", question="B?"),
        ]
        shared = SearchResult(
            title="shared",
            uri="viking://resources/demo/shared.md",
            snippet="shared",
            score=0.8,
        )
        stats = _build_citation_stats(
            questions,
            {
                "a": [shared],
                "b": [shared],
            },
        )

        warnings = _build_quality_warnings(
            questions,
            {
                "a": [shared],
                "b": [shared],
            },
            stats,
            min_results_per_section=2,
        )

        codes = {warning.code for warning in warnings}
        self.assertIn("low_coverage", codes)
        self.assertIn("high_reuse", codes)

    def test_render_markdown_includes_citation_stats_and_quality_warnings(self) -> None:
        question = ResearchQuestion(id="a", heading="A", question="A?")
        result = SearchResult(
            title="doc",
            uri="viking://resources/demo/doc.md",
            snippet="doc",
            score=0.8,
        )
        stats = _build_citation_stats([question], {"a": [result]})
        warnings = _build_quality_warnings(
            [question],
            {"a": []},
            stats,
            min_results_per_section=1,
        )
        report = ResearchReport(
            title="测试调研",
            scope="viking://resources/demo",
            questions=[question],
            results_by_id={"a": [result]},
            citation_stats=stats,
            quality_warnings=warnings,
        )

        markdown = render_markdown(report)

        self.assertIn("## 引用统计", markdown)
        self.assertIn("## 质量提示", markdown)


if __name__ == "__main__":
    unittest.main()
