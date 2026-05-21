import tempfile
import unittest
from pathlib import Path

from ov_search_skill.retrievers.base import SearchResult
from ov_search_skill.workflows.research import (
    ResearchQuestion,
    ResearchReport,
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


if __name__ == "__main__":
    unittest.main()
