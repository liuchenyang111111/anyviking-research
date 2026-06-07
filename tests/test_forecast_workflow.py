import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from anyviking_research.connectors.base import WebSearchResponse, WebSearchResult
from anyviking_research.retrievers.base import SearchResult
from anyviking_research.workflows.forecast import (
    Prediction,
    apply_leak_filter,
    forecast_case,
    normalize_prediction,
    score_prediction,
)


class FakeForecastConnector:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def search(self, query: str, **kwargs) -> WebSearchResponse:
        self.calls.append((query, kwargs))
        return WebSearchResponse(
            query=query,
            provider="anysearch",
            results=[
                WebSearchResult(
                    title="Before cutoff",
                    url="https://example.com/before",
                    description="Evidence before cutoff",
                    content="The roadmap was uncertain before the cutoff.",
                    source="web",
                    published_at="2026-02-01",
                ),
                WebSearchResult(
                    title="After cutoff",
                    url="https://example.com/after",
                    description="Late evidence",
                    content="This page is after the cutoff.",
                    source="web",
                    published_at="2026-05-01",
                ),
            ],
        )


class FakePredictor:
    def __init__(self) -> None:
        self.prompt = ""
        self.evidence_count = 0

    def predict(self, *, case, prompt, evidence):
        self.prompt = prompt
        self.evidence_count = len(evidence)
        return Prediction(
            predicted_answer="Yes",
            probabilities={"Yes": 0.8, "No": 0.2},
            rationale="The selected evidence leans yes.",
        )


class ForecastWorkflowTests(unittest.TestCase):
    def test_normalize_prediction_and_brier_score(self) -> None:
        prediction = normalize_prediction(
            {"probabilities": {"Yes": 2, "No": 1}, "rationale": "demo"},
            ["Yes", "No"],
        )
        score = score_prediction(prediction, "Yes", ["Yes", "No"])

        self.assertEqual(prediction.predicted_answer, "Yes")
        self.assertAlmostEqual(prediction.probabilities["Yes"], 2 / 3)
        self.assertTrue(score.correct)
        self.assertAlmostEqual(score.brier, (2 / 3 - 1) ** 2 + (1 / 3) ** 2)

    def test_leak_filter_drops_sources_after_cutoff(self) -> None:
        response = WebSearchResponse(
            query="demo",
            provider="anysearch",
            results=[
                WebSearchResult(title="old", url="https://example.com/old", published_at="2026-01-01"),
                WebSearchResult(title="late", url="https://example.com/late", published_at="2026-04-01"),
            ],
        )

        filtered, decisions = apply_leak_filter(response, cutoff_date="2026-03-01")

        self.assertEqual([result.url for result in filtered.results], ["https://example.com/old"])
        self.assertEqual([decision.decision for decision in decisions], ["kept", "dropped"])

    def test_forecast_case_writes_prediction_and_trajectory(self) -> None:
        imported: list[tuple[Path, str]] = []

        def importer(markdown_dir: Path, target_uri: str) -> int:
            imported.append((markdown_dir, target_uri))
            return 0

        def searcher(query: str, scope: str, top_k: int) -> list[SearchResult]:
            return [
                SearchResult(
                    title=f"Retrieved {index}",
                    uri=f"viking://resources/demo/{index}.md",
                    snippet=f"Snippet {index}",
                    score=1.0 / index,
                    source="openviking",
                )
                for index in range(1, 4)
            ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_path = root / "case.yaml"
            answer_path = root / "case.answer.json"
            output_dir = root / "case-output"
            run_root = root / "runs"
            case_path.write_text(
                f"""
id: demo_forecast
title: Demo Forecast
question_type: yes_no
question: Will the demo happen?
options:
  - Yes
  - No
cutoff_date: "2026-03-01"
queries:
  - demo forecast query
search:
  max_results: 2
storage:
  output_dir: {output_dir.as_posix()}
  target_uri: viking://resources/demo
retrieval_checks:
  - query: What evidence exists?
    top_k: 3
""".strip(),
                encoding="utf-8",
            )
            answer_path.write_text(
                json.dumps({"case_id": "demo_forecast", "answer": "Yes"}),
                encoding="utf-8",
            )

            connector = FakeForecastConnector()
            predictor = FakePredictor()
            result = forecast_case(
                case_path,
                connector=connector,
                predictor=predictor,
                importer=importer,
                searcher=searcher,
                run_root=run_root,
                fetched_at=datetime(2026, 6, 6, tzinfo=timezone.utc),
                max_prompt_evidence=2,
            )
            trajectory = json.loads(result.trajectory_path.read_text(encoding="utf-8"))
            prediction = json.loads(result.prediction_path.read_text(encoding="utf-8"))

        self.assertEqual(connector.calls[0][1]["to_time"], "2026-03-01")
        self.assertEqual(result.output.markdown_files[0].name, "001-before-cutoff.md")
        self.assertEqual(len(result.output.markdown_files), 1)
        self.assertEqual(imported[0][1], "viking://resources/demo")
        self.assertTrue(result.score.correct)
        self.assertAlmostEqual(result.score.brier, 0.08)
        self.assertEqual(predictor.evidence_count, 2)
        self.assertEqual(trajectory["prompt_assembly"]["truncation_reason"], "context_window")
        self.assertEqual(len(trajectory["prompt_assembly"]["selected_for_prompt"]), 2)
        self.assertEqual(prediction["prediction"]["predicted_answer"], "Yes")

    def test_forecast_baseline_modes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_path = root / "case.yaml"
            output_dir = root / "case-output"
            run_root = root / "runs"
            case_path.write_text(
                f"""
id: demo_forecast
title: Demo Forecast
question_type: yes_no
question: Will the demo happen?
options:
  - Yes
  - No
cutoff_date: "2026-03-01"
queries:
  - structured query
search:
  max_results: 2
storage:
  output_dir: {output_dir.as_posix()}
  target_uri: viking://resources/demo
""".strip(),
                encoding="utf-8",
            )
            case_path.with_name("case.answer.json").write_text(
                json.dumps({"case_id": "demo_forecast", "answer": "Yes"}),
                encoding="utf-8",
            )

            no_retrieval_connector = FakeForecastConnector()
            no_retrieval = forecast_case(
                case_path,
                connector=no_retrieval_connector,
                predictor=FakePredictor(),
                run_root=run_root,
                skip_import=True,
                fetched_at=datetime(2026, 6, 6, 0, 0, tzinfo=timezone.utc),
                baseline_mode="no-retrieval",
            )
            naive_connector = FakeForecastConnector()
            naive = forecast_case(
                case_path,
                connector=naive_connector,
                predictor=FakePredictor(),
                run_root=run_root,
                skip_import=True,
                fetched_at=datetime(2026, 6, 6, 0, 1, tzinfo=timezone.utc),
                baseline_mode="naive-search",
            )
            no_retrieval_trajectory = json.loads(no_retrieval.trajectory_path.read_text(encoding="utf-8"))
            naive_trajectory = json.loads(naive.trajectory_path.read_text(encoding="utf-8"))

        self.assertEqual(no_retrieval_connector.calls, [])
        self.assertEqual(naive_connector.calls[0][0], "Will the demo happen?")
        self.assertEqual(no_retrieval_trajectory["baseline_mode"], "no-retrieval")
        self.assertEqual(naive_trajectory["baseline_mode"], "naive-search")
        self.assertTrue(no_retrieval.success)
        self.assertTrue(naive.success)

    def test_forecast_applies_candidate_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_path = root / "case.yaml"
            output_dir = root / "case-output"
            run_root = root / "runs"
            candidate_dir = root / "candidate"
            candidate_dir.mkdir()
            (candidate_dir / "candidate.json").write_text(
                json.dumps({"candidate_id": "cand-demo"}),
                encoding="utf-8",
            )
            (candidate_dir / "strategy_patch.yaml").write_text(
                "additional_queries:\n  - candidate query\n",
                encoding="utf-8",
            )
            (candidate_dir / "prompt_patch.md").write_text(
                "Prefer official release notes before commentary.",
                encoding="utf-8",
            )
            case_path.write_text(
                f"""
id: demo_forecast
title: Demo Forecast
question_type: yes_no
question: Will the demo happen?
options:
  - Yes
  - No
cutoff_date: "2026-03-01"
queries:
  - original query
search:
  max_results: 2
storage:
  output_dir: {output_dir.as_posix()}
  target_uri: viking://resources/demo
""".strip(),
                encoding="utf-8",
            )
            case_path.with_name("case.answer.json").write_text(
                json.dumps({"case_id": "demo_forecast", "answer": "Yes"}),
                encoding="utf-8",
            )

            connector = FakeForecastConnector()
            predictor = FakePredictor()
            result = forecast_case(
                case_path,
                connector=connector,
                predictor=predictor,
                run_root=run_root,
                skip_import=True,
                fetched_at=datetime(2026, 6, 6, 0, 2, tzinfo=timezone.utc),
                candidate_dir=candidate_dir,
            )
            trajectory = json.loads(result.trajectory_path.read_text(encoding="utf-8"))

        self.assertEqual([call[0] for call in connector.calls], ["original query", "candidate query"])
        self.assertIn("Prefer official release notes", predictor.prompt)
        self.assertEqual(trajectory["baseline_group"], "anyviking_candidate")
        self.assertEqual(trajectory["candidate"]["candidate_id"], "cand-demo")
        self.assertEqual(trajectory["candidate"]["additional_queries"], ["candidate query"])

    def test_forecast_run_dirs_do_not_collide_for_same_second(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_path = root / "case.yaml"
            output_dir = root / "case-output"
            run_root = root / "runs"
            case_path.write_text(
                f"""
id: demo_forecast
title: Demo Forecast
question_type: yes_no
question: Will the demo happen?
options:
  - Yes
  - No
cutoff_date: "2026-03-01"
queries:
  - structured query
search:
  max_results: 2
storage:
  output_dir: {output_dir.as_posix()}
  target_uri: viking://resources/demo
""".strip(),
                encoding="utf-8",
            )
            case_path.with_name("case.answer.json").write_text(
                json.dumps({"case_id": "demo_forecast", "answer": "Yes"}),
                encoding="utf-8",
            )
            timestamp = datetime(2026, 6, 6, 0, 3, tzinfo=timezone.utc)

            first = forecast_case(
                case_path,
                connector=FakeForecastConnector(),
                predictor=FakePredictor(),
                run_root=run_root,
                skip_import=True,
                fetched_at=timestamp,
                baseline_mode="no-retrieval",
            )
            second = forecast_case(
                case_path,
                connector=FakeForecastConnector(),
                predictor=FakePredictor(),
                run_root=run_root,
                skip_import=True,
                fetched_at=timestamp,
                baseline_mode="no-retrieval",
            )
            first_exists = first.trajectory_path.exists()
            second_exists = second.trajectory_path.exists()

        self.assertNotEqual(first.run_dir, second.run_dir)
        self.assertTrue(first_exists)
        self.assertTrue(second_exists)


if __name__ == "__main__":
    unittest.main()
