# Command Recipes

## Health and Readiness

```powershell
ar doctor
```

```powershell
ar health
```

```powershell
ar status
```

## Public Web Search

Search only:

```powershell
ar search-web "AI search tools" --max-results 5
```

Search and save results locally:

```powershell
ar fetch-web "AI search tools" --max-results 5 --output data\web\ai-search-tools
```

Search and import into OpenViking:

```powershell
ar sync "AI search tools" --max-results 5 --output data\web\ai-search-tools --to viking://resources/ai-search-tools
```

## Local Corpus

Import a local folder:

```powershell
ar import-local .\examples\smoke_corpus --to viking://resources/smoke-corpus
```

Show the resource tree:

```powershell
ar tree viking://resources/smoke-corpus -L 2
```

Search a known scope:

```powershell
ar search "What is the core purpose of the second phase?" --scope viking://resources/smoke-corpus --top-k 3 --format text --documents-only
```

## Research Drafts

Generate markdown output:

```powershell
ar research examples\smoke_corpus\research_questions.yaml --output reports\smoke_corpus_research.md --top-k 3
```

Generate markdown plus JSON:

```powershell
ar research examples\smoke_corpus\research_questions.yaml --output reports\smoke_corpus_research.md --json-output reports\smoke_corpus_research.json --top-k 3
```
