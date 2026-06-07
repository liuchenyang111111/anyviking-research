# CLI Reference

The main command is `anyviking`.

If your virtual environment is not active, use:

```powershell
.\.venv\Scripts\anyviking.exe doctor
```

```bash
.venv/bin/anyviking doctor
```

## Check Environment

```bash
anyviking doctor
```

Set a default OpenViking HTTP endpoint through the environment if you do not want to repeat `--url`:

```bash
export OPENVIKING_URL="http://127.0.0.1:1933"
```

Use JSON output when another tool or Agent needs to parse the result:

```bash
anyviking doctor --json
```

## OpenViking Service

```bash
anyviking health
```

```bash
anyviking status
```

```bash
anyviking status --json
```

## Import Local Files

```bash
anyviking import-local ./path/to/corpus --to viking://resources/my-corpus
```

Show the resource tree:

```bash
anyviking tree viking://resources/my-corpus -L 2
```

## Search Public Web

```bash
anyviking search-web "query" --max-results 5
```

Set a default AnySearch-compatible endpoint through the environment if needed:

```bash
export ANYSEARCH_API_URL="https://your-endpoint.example"
```

Useful filters:

```bash
anyviking search-web "query" --domain github.com --language en --freshness week
```

## Save Web Results Locally

```bash
anyviking fetch-web "query" --max-results 5 --output data/web/topic-name
```

This writes:

```text
data/web/topic-name/raw/anysearch_response.json
data/web/topic-name/markdown/*.md
data/web/topic-name/manifest.json
```

## Save And Import Into OpenViking

```bash
anyviking sync "query" --max-results 5 --output data/web/topic-name --to viking://resources/topic-name
```

This is the main command for the project.

## Run A Reusable Case

```bash
anyviking run-case cases/oracleproto/train/deepseek_v4.yaml
```

Use this when a task should be reproducible. A case can define multiple search queries, a local output directory, a target `viking://` URI, and retrieval checks.

Save local files only:

```bash
anyviking run-case cases/oracleproto/train/deepseek_v4.yaml --skip-import
```

Skip retrieval checks after import:

```bash
anyviking run-case cases/oracleproto/train/deepseek_v4.yaml --skip-checks
```

## Run A Forecast Case

Use this when a case has options, a cutoff date, and a matching `.answer.json` file:

```bash
anyviking forecast cases/oracleproto/train/deepseek_v4.yaml --skip-import
```

Configure an OpenAI-compatible LLM through the environment:

```bash
export ANYVIKING_LLM_API_KEY="..."
export ANYVIKING_LLM_MODEL="gpt-4o-mini"
export ANYVIKING_LLM_BASE_URL="https://api.openai.com/v1"
```

`forecast` writes `prediction.json`, `prompt.md`, `trajectory.json`, and cached LLM calls under `data/runs/<run-id>/`.

Run baselines for comparison:

```bash
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode no-retrieval --skip-import
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode naive-search --skip-import
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode anyviking
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode anyviking --candidate-dir data/evolution/candidates/<candidate-id>
anyviking evolve baselines --runs data/runs --output data/evolution/candidates/<candidate-id>/baselines.json
```

## Generate Skill Suggestions

```bash
anyviking evolve-skill --log data/run_logs/runs.jsonl
```

This reads local run logs and writes:

```text
data/skill_evolution/summary.json
data/skill_evolution/generated_patterns.md
```

## Forecast-Driven Skill Evolution

After running forecast cases:

```bash
anyviking evolve collect --runs data/runs
anyviking evolve propose --runs data/runs
```

Validate a generated candidate before publishing:

```bash
anyviking evolve validate data/evolution/candidates/<candidate-id> --baseline data/evolution/candidates/<candidate-id>/baselines.json
anyviking evolve publish data/evolution/candidates/<candidate-id>
```

Publishing appends learned notes and strategy files under `skills/anyviking-research/`. Keep generated `data/evolution/` files local.

## Search Indexed Data

```bash
anyviking search "question" --scope viking://resources/topic-name --top-k 5
```

Text output is easier for humans:

```bash
anyviking search "question" --scope viking://resources/topic-name --format text --documents-only
```
