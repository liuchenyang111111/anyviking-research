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
