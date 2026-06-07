# Command Recipes

## Check Readiness

```bash
anyviking doctor
```

```bash
anyviking health
```

## Search The Web

```bash
anyviking search-web "AI search tools" --max-results 5
```

## Save Web Results

```bash
anyviking fetch-web "AI search tools" --max-results 5 --output data/web/ai-search-tools
```

## Save And Import Into OpenViking

```bash
anyviking sync "AI search tools" --max-results 5 --output data/web/ai-search-tools --to viking://resources/ai-search-tools
```

## Run A Reusable Case

```bash
anyviking run-case cases/oracleproto/train/deepseek_v4.yaml
```

Save local outputs only:

```bash
anyviking run-case cases/oracleproto/train/deepseek_v4.yaml --skip-import
```

## Run A Scored Forecast Case

```bash
anyviking forecast cases/oracleproto/train/deepseek_v4.yaml --skip-import
```

Run comparison modes:

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

## Generate Forecast-Driven Evolution Candidate

```bash
anyviking evolve collect --runs data/runs
anyviking evolve propose --runs data/runs
anyviking evolve validate data/evolution/candidates/<candidate-id> --baseline data/evolution/candidates/<candidate-id>/baselines.json
```

## Import Existing Local Files

```bash
anyviking import-local ./path/to/corpus --to viking://resources/my-corpus
```

## Inspect A Resource Tree

```bash
anyviking tree viking://resources/my-corpus -L 2
```

## Search Indexed Data

```bash
anyviking search "What does this corpus say?" --scope viking://resources/my-corpus --top-k 5 --format text --documents-only
```
