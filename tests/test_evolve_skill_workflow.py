import json
import tempfile
import unittest
from pathlib import Path

from anyviking_research.workflows.evolve_skill import build_summary, evolve_skill


class EvolveSkillWorkflowTests(unittest.TestCase):
    def test_build_summary_groups_successful_patterns_by_tag_and_case(self) -> None:
        summary = build_summary(
            [
                {
                    "case_id": "oracleproto_demo",
                    "queries": ["demo query"],
                    "search": {"freshness": "month", "language": "en", "content_types": ["web", "news"]},
                    "tags": ["oracleproto", "forecast-data"],
                    "target_uri": "viking://resources/forecast/oracleproto/demo",
                    "retrieval_checks": [{"passed": True}],
                    "retrieval_passed": 1,
                    "success": True,
                },
                {
                    "case_id": "oracleproto_demo",
                    "queries": ["demo query"],
                    "search": {"freshness": "month", "language": "en", "content_types": ["web"]},
                    "tags": ["oracleproto"],
                    "target_uri": "viking://resources/forecast/oracleproto/demo",
                    "retrieval_checks": [],
                    "retrieval_passed": 0,
                    "success": False,
                },
            ]
        )

        self.assertEqual(summary["run_count"], 2)
        self.assertEqual(summary["successful_count"], 1)
        oracleproto = summary["patterns_by_tag"]["oracleproto"]
        self.assertEqual(oracleproto["runs"], 2)
        self.assertEqual(oracleproto["top_queries"][0]["value"], "demo query")
        self.assertEqual(oracleproto["content_types"][0]["value"], "web")
        self.assertEqual(summary["patterns_by_case"]["oracleproto_demo"]["retrieval_passed"], 1)

    def test_evolve_skill_writes_summary_and_markdown(self) -> None:
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

            output = evolve_skill(log_path, output_dir)
            summary = json.loads(output.summary_path.read_text(encoding="utf-8"))
            patterns = output.patterns_path.read_text(encoding="utf-8")

        self.assertEqual(output.run_count, 1)
        self.assertEqual(output.successful_count, 1)
        self.assertEqual(summary["patterns_by_tag"]["oracleproto"]["successes"], 1)
        self.assertIn("Generated Skill Patterns", patterns)
        self.assertIn("demo query", patterns)


if __name__ == "__main__":
    unittest.main()
