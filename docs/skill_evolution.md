# Skill Evolution

AnyViking has two evolution paths.

## Lite Path

`evolve-skill` reads local `run-case` logs and generates simple workflow suggestions.

```bash
anyviking evolve-skill --log data/run_logs/runs.jsonl
```

Outputs:

```text
data/skill_evolution/summary.json
data/skill_evolution/generated_patterns.md
```

Use this after several successful `run-case` runs. It does not edit `SKILL.md`.

## Forecast-Driven Path

The fuller loop uses scored forecast trajectories:

```bash
anyviking forecast cases/oracleproto/train/deepseek_v4.yaml --skip-import
anyviking evolve collect --runs data/runs
anyviking evolve propose --runs data/runs
```

This creates a local candidate under:

```text
data/evolution/candidates/<candidate-id>/
```

Candidate files:

```text
candidate.json
learned_patch.md
strategy_patch.yaml
prompt_patch.md
notes.md
```

## Validation

For serious validation, run eval cases with four groups:

```text
no_retrieval
naive_search
anyviking_baseline
anyviking_candidate
```

Use the current Skill for the first three groups, then run the candidate as a real forecast input:

```bash
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode no-retrieval --skip-import
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode naive-search --skip-import
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode anyviking
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode anyviking --candidate-dir data/evolution/candidates/<candidate-id>
```

`--candidate-dir` applies the candidate prompt notes and strategy patch before prediction, and writes the run as `anyviking_candidate`.

Write summary metrics to:

```text
data/evolution/candidates/<candidate-id>/baselines.json
```

```bash
anyviking evolve baselines --runs data/runs --output data/evolution/candidates/<candidate-id>/baselines.json
```

Then validate:

```bash
anyviking evolve validate data/evolution/candidates/<candidate-id> --baseline data/evolution/candidates/<candidate-id>/baselines.json
```

The candidate must not be worse than the previous AnyViking baseline on mean Brier score. The AnyViking baseline must also be no worse than no-retrieval and naive-search baselines.

You can also run one local iteration from existing trajectories:

```bash
anyviking evolve iterate --runs data/runs --baseline data/evolution/baselines.json
```

Add `--publish` only after you are comfortable publishing a candidate that passes validation.

## Publish

Only publish after review:

```bash
anyviking evolve publish data/evolution/candidates/<candidate-id>
```

Publishing writes reviewed notes into:

```text
skills/anyviking-research/references/learned.md
skills/anyviking-research/references/strategy.yaml
skills/anyviking-research/prompts/forecast_notes.md
```

Generated data stays under `data/` and should not be committed.

## Eval Hygiene

Use `cases/oracleproto/train/` for proposing improvements. Use `cases/oracleproto/eval/` only for validation.

Rules:

- Propose must not read eval trajectories or answer files.
- During candidate review, look at eval summary metrics, not individual eval failure details.
- Rotate eval case ids over time and record reused ids in `cases/oracleproto/eval/_used.txt`.
