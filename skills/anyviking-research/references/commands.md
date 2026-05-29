# Command Recipes

## Check Readiness

```powershell
ar doctor
```

```powershell
ar health
```

## Search The Web

```powershell
ar search-web "AI search tools" --max-results 5
```

## Save Web Results

```powershell
ar fetch-web "AI search tools" --max-results 5 --output data\web\ai-search-tools
```

## Save And Import Into OpenViking

```powershell
ar sync "AI search tools" --max-results 5 --output data\web\ai-search-tools --to viking://resources/ai-search-tools
```

## Import Existing Local Files

```powershell
ar import-local .\path\to\corpus --to viking://resources/my-corpus
```

## Inspect A Resource Tree

```powershell
ar tree viking://resources/my-corpus -L 2
```

## Search Indexed Data

```powershell
ar search "What does this corpus say?" --scope viking://resources/my-corpus --top-k 5 --format text --documents-only
```
