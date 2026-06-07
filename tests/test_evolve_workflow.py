import json
import tempfile
import unittest
from pathlib import Path

from anyviking_research.workflows.evolve import (
    collect_trajectories,
    iterate_once,
    propose_candidate,
    publish_candidate,
    summarize_baselines,
    summarize_trajectories,
    validate_candidate,
    write_baseline_summary,
)


class EvolveWorkflowTests(unittest.TestCase):
    def test_summarize_excludes_eval_trajectories_from_propose_metrics(self) -> None:
        summary = summarize_trajectories(
            [
                {
                    "case_id": "train_case",
                    "split": "train",
                    "queries": ["train query"],
                    "target_uri": "viking://resources/train",
                    "score": {"correct": True, "brier": 0.1},
                    "failure_mode": None,
                },
                {
                    "case_id": "eval_case",
                    "split": "eval",
                    "queries": ["eval query"],
                    "target_uri": "viking://resources/eval",
                    "score": {"correct": False, "brier": 0.9},
                    "failure_mode": "llm_misjudged",
                },
            ]
        )

        self.assertEqual(summary["trajectory_count"], 1)
        self.assertEqual(summary["excluded_eval_count"], 1)
        self.assertEqual(summary["top_queries"][0]["value"], "train query")
        self.assertEqual(summary["accuracy"], 1.0)

    def test_summarize_baselines_uses_eval_trajectories_by_group(self) -> None:
        summary = summarize_baselines(
            [
                {
                    "case_id": "train_case",
                    "split": "train",
                    "baseline_group": "anyviking_candidate",
                    "score": {"correct": False, "brier": 0.9},
                },
                {
                    "case_id": "eval_case_1",
                    "split": "eval",
                    "baseline_group": "anyviking_baseline",
                    "score": {"correct": True, "brier": 0.4},
                },
                {
                    "case_id": "eval_case_2",
                    "split": "eval",
                    "baseline_group": "anyviking_baseline",
                    "score": {"correct": False, "brier": 0.6},
                },
                {
                    "case_id": "eval_case_3",
                    "split": "eval",
                    "baseline_group": "anyviking_candidate",
                    "score": {"correct": True, "brier": 0.3},
                },
            ]
        )

        self.assertNotIn("train_case", json.dumps(summary))
        self.assertEqual(summary["anyviking_baseline"]["case_count"], 2)
        self.assertEqual(summary["anyviking_baseline"]["accuracy"], 0.5)
        self.assertAlmostEqual(summary["anyviking_baseline"]["mean_brier"], 0.5)
        self.assertEqual(summary["anyviking_candidate"]["case_count"], 1)

    def test_write_baseline_summary_can_feed_validate_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runs = root / "runs"
            for index, (group, brier) in enumerate(
                [
                    ("no_retrieval", 0.8),
                    ("naive_search", 0.7),
                    ("anyviking_baseline", 0.4),
                    ("anyviking_candidate", 0.3),
                ],
                start=1,
            ):
                run_dir = runs / f"run-{index}"
                run_dir.mkdir(parents=True)
                (run_dir / "trajectory.json").write_text(
                    json.dumps(
                        {
                            "case_id": "eval_case",
                            "split": "eval",
                            "baseline_group": group,
                            "score": {"correct": True, "brier": brier},
                        }
                    ),
                    encoding="utf-8",
                )

            baseline_output = write_baseline_summary(runs, root / "baselines.json")
            candidate_dir = root / "candidate"
            candidate_dir.mkdir()
            (candidate_dir / "candidate.json").write_text(
                json.dumps({"candidate_id": "cand", "trajectory_count": 1, "summary": {}}),
                encoding="utf-8",
            )
            (candidate_dir / "learned_patch.md").write_text("learned", encoding="utf-8")
            (candidate_dir / "strategy_patch.yaml").write_text("version: 0.1.0\n", encoding="utf-8")

            validation = validate_candidate(candidate_dir, baseline_path=baseline_output.output_path)

        self.assertEqual(
            baseline_output.groups,
            ["anyviking_baseline", "anyviking_candidate", "naive_search", "no_retrieval"],
        )
        self.assertTrue(validation.passed)

    def test_collect_propose_validate_and_publish_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runs = root / "runs"
            run_dir = runs / "run-1"
            run_dir.mkdir(parents=True)
            trajectory = {
                "case_id": "train_case",
                "split": "train",
                "queries": ["train query"],
                "target_uri": "viking://resources/train",
                "score": {"correct": True, "brier": 0.2},
                "failure_mode": None,
            }
            (run_dir / "trajectory.json").write_text(json.dumps(trajectory), encoding="utf-8")

            collected = collect_trajectories(runs, root / "collected.json")
            candidate = propose_candidate(runs, root / "candidates")
            baseline_path = candidate.candidate_dir / "baselines.json"
            baseline_path.write_text(
                json.dumps(
                    {
                        "no_retrieval": {"mean_brier": 0.8},
                        "naive_search": {"mean_brier": 0.7},
                        "anyviking_baseline": {"mean_brier": 0.4},
                        "anyviking_candidate": {"mean_brier": 0.3},
                    }
                ),
                encoding="utf-8",
            )
            validation = validate_candidate(candidate.candidate_dir)
            skill_dir = root / "skill"
            published = publish_candidate(candidate.candidate_dir, skill_dir)

            candidate_json = json.loads(candidate.candidate_path.read_text(encoding="utf-8"))
            validation_json = json.loads(validation.validation_path.read_text(encoding="utf-8"))
            learned_exists = (skill_dir / "references" / "learned.md").exists()
            strategy_exists = (skill_dir / "references" / "strategy.yaml").exists()
            prompt_exists = (skill_dir / "prompts" / "forecast_notes.md").exists()

        self.assertEqual(collected.trajectory_count, 1)
        self.assertEqual(candidate.trajectory_count, 1)
        self.assertEqual(candidate_json["summary"]["top_queries"][0]["value"], "train query")
        self.assertTrue(validation.passed)
        self.assertTrue(validation_json["checks"]["candidate_not_worse"])
        self.assertTrue(published.published)
        self.assertTrue(learned_exists)
        self.assertTrue(strategy_exists)
        self.assertTrue(prompt_exists)

    def test_propose_uses_train_count_not_eval_count(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runs = root / "runs"
            run_dir = runs / "run-1"
            run_dir.mkdir(parents=True)
            (run_dir / "trajectory.json").write_text(
                json.dumps(
                    {
                        "case_id": "eval_case",
                        "split": "eval",
                        "queries": ["eval query"],
                        "score": {"correct": False, "brier": 0.9},
                    }
                ),
                encoding="utf-8",
            )

            candidate = propose_candidate(runs, root / "candidates")
            candidate_json = json.loads(candidate.candidate_path.read_text(encoding="utf-8"))
            validation = validate_candidate(candidate.candidate_dir)

        self.assertEqual(candidate.trajectory_count, 0)
        self.assertEqual(candidate_json["excluded_eval_count"], 1)
        self.assertFalse(validation.passed)

    def test_propose_candidate_dirs_do_not_collide(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runs = root / "runs"
            run_dir = runs / "run-1"
            run_dir.mkdir(parents=True)
            (run_dir / "trajectory.json").write_text(
                json.dumps(
                    {
                        "case_id": "train_case",
                        "split": "train",
                        "queries": ["train query"],
                        "score": {"correct": True, "brier": 0.2},
                    }
                ),
                encoding="utf-8",
            )

            first = propose_candidate(runs, root / "candidates")
            second = propose_candidate(runs, root / "candidates")

        self.assertNotEqual(first.candidate_dir, second.candidate_dir)
        self.assertTrue(second.candidate_dir.name.endswith("-2"))

    def test_validate_rejects_candidate_when_baseline_gets_worse(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate_dir = root / "candidate"
            candidate_dir.mkdir()
            (candidate_dir / "candidate.json").write_text(
                json.dumps({"candidate_id": "cand", "trajectory_count": 1, "summary": {}}),
                encoding="utf-8",
            )
            (candidate_dir / "learned_patch.md").write_text("learned", encoding="utf-8")
            (candidate_dir / "strategy_patch.yaml").write_text("version: 0.1.0\n", encoding="utf-8")
            (candidate_dir / "baselines.json").write_text(
                json.dumps(
                    {
                        "no_retrieval": {"mean_brier": 0.8},
                        "naive_search": {"mean_brier": 0.7},
                        "anyviking_baseline": {"mean_brier": 0.4},
                        "anyviking_candidate": {"mean_brier": 0.5},
                    }
                ),
                encoding="utf-8",
            )

            validation = validate_candidate(candidate_dir)
            validation_json = json.loads(validation.validation_path.read_text(encoding="utf-8"))

        self.assertFalse(validation.passed)
        self.assertFalse(validation_json["checks"]["candidate_not_worse"])

    def test_iterate_once_validates_and_optionally_publishes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runs = root / "runs"
            run_dir = runs / "run-1"
            run_dir.mkdir(parents=True)
            (run_dir / "trajectory.json").write_text(
                json.dumps(
                    {
                        "case_id": "train_case",
                        "split": "train",
                        "queries": ["train query"],
                        "target_uri": "viking://resources/train",
                        "score": {"correct": True, "brier": 0.2},
                    }
                ),
                encoding="utf-8",
            )
            baseline_path = root / "baselines.json"
            baseline_path.write_text(
                json.dumps(
                    {
                        "no_retrieval": {"mean_brier": 0.8},
                        "naive_search": {"mean_brier": 0.7},
                        "anyviking_baseline": {"mean_brier": 0.4},
                        "anyviking_candidate": {"mean_brier": 0.3},
                    }
                ),
                encoding="utf-8",
            )

            output = iterate_once(
                runs,
                root / "candidates",
                baseline_path=baseline_path,
                publish=True,
                skill_dir=root / "skill",
            )

            learned_exists = (root / "skill" / "references" / "learned.md").exists()

        self.assertTrue(output.validation.passed)
        self.assertIsNotNone(output.publish)
        self.assertTrue(learned_exists)


if __name__ == "__main__":
    unittest.main()
