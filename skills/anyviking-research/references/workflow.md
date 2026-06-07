# Workflow Guide

Use the smallest command that satisfies the user request.

## Search Only

```text
search-web
```

Use this when the user only wants fresh web results.

## Save For Inspection

```text
fetch-web
```

Use this when the user wants markdown files before indexing.

## Save And Index

```text
sync
```

Use this when the user wants public web material available through OpenViking.

## Repeatable Collection Case

```text
run-case
```

Use this when the user wants a reusable YAML template for research or forecast-data collection. A case can define several queries, a target `viking://` URI, and retrieval checks.

## Scored Forecast Case

```text
forecast
```

Use this when a case has `question_type`, `options`, `cutoff_date`, and a matching `.answer.json` file. It writes `prediction.json`, `prompt.md`, and `trajectory.json` under `data/runs/`.

Use `--baseline-mode no-retrieval`, `--baseline-mode naive-search`, and `--baseline-mode anyviking` when comparing evidence strategies on eval cases.

Use `--candidate-dir data/evolution/candidates/<candidate-id>` to run a proposed candidate before publishing it. That run is recorded as `anyviking_candidate`.

## Improve From Run Logs, Lite

```text
evolve-skill
```

Use this after successful `run-case` runs. It generates reviewable workflow suggestions under `data/skill_evolution/` and does not automatically edit the main Skill.

## Improve From Forecast Trajectories

```text
evolve collect -> evolve propose -> evolve validate -> evolve publish
```

Use this after `forecast` has produced local trajectories. Propose from train trajectories only. Validate on eval summaries and publish only after review.

For validation, run eval forecasts for `no_retrieval`, `naive_search`, `anyviking_baseline`, and `anyviking_candidate`, then summarize them with `evolve baselines`.

## Existing Local Corpus

```text
import-local -> search
```

Use this when the user already has markdown or text files.

## Read From OpenViking

```text
search
```

Use this when the user or their Agent already knows the `viking://` scope.

## Important Point

`viking://` is a virtual OpenViking URI. An Agent needs a tool such as `anyviking search` or another OpenViking adapter to read it.
