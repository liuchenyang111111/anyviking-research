# Reusable Cases

Cases are YAML templates for reproducible collection tasks.

Use free-form commands when you only need a one-off import:

```bash
anyviking sync "AI coding agents latest developments" --to viking://resources/tech/ai-coding
```

Use a case when you want to repeat the same research setup:

```bash
anyviking run-case cases/oracleproto/train/deepseek_v4.yaml
```

## What A Case Does

`run-case` reads the YAML file, searches each query through AnySearch, deduplicates URL results, saves markdown under `data/cases/<case-id>/`, imports the markdown into OpenViking, and optionally runs retrieval checks against the target `viking://` URI.

`forecast` uses the same collection path, then asks an LLM to choose one option and score it against a separate `.answer.json` file. The answer file is only read after prediction.

It also writes:

```text
data/cases/<case-id>/raw/anysearch_response.json
data/cases/<case-id>/markdown/*.md
data/cases/<case-id>/manifest.json
data/cases/<case-id>/evidence_pack.md
data/run_logs/runs.jsonl
```

These outputs are local runtime files and are ignored by Git.

## Minimal Case Shape

```yaml
id: oracleproto_deepseek_v4
title: "OracleProto case: DeepSeek V4 release"
question_type: yes_no
question: Will DeepSeek release V4 in March 2026?
options:
  - Yes
  - No
cutoff_date: "2026-04-03"

queries:
  - DeepSeek V4 March 2026 release
  - DeepSeek V4 model announcement March 2026

search:
  max_results: 6
  freshness: month
  language: en
  content_types:
    - web
    - news

storage:
  output_dir: data/cases/oracleproto_deepseek_v4
  target_uri: viking://resources/forecast/oracleproto/deepseek-v4

retrieval_checks:
  - query: What public evidence discusses a possible DeepSeek V4 release in March 2026?
    top_k: 3
```

Copy one of the files in `cases/oracleproto/train/` and change the question, queries, and target URI for your own task.

## Forecast Scoring

Use `forecast` when the case has options and a matching answer file:

```bash
anyviking forecast cases/oracleproto/train/deepseek_v4.yaml --skip-import
```

The command writes:

```text
data/runs/<run-id>/prompt.md
data/runs/<run-id>/prediction.json
data/runs/<run-id>/trajectory.json
data/runs/<run-id>/llm_calls/*.json
```

The trajectory records the selected evidence that actually went into the prompt, not only the retrieval result list.

## Train And Eval

Use `cases/oracleproto/train/` to generate improvement candidates. Use `cases/oracleproto/eval/` only for validation. Do not inspect eval failures while proposing improvements.
