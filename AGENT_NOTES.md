# Agent Notes

This repo-local agent note is the lightweight version used inside the repository.
The only formal skill in this repo lives at `skills/anyviking-research/SKILL.md`.

## Use This Workflow For

- AnySearch public-web discovery.
- Saving web results as local markdown files.
- Importing local markdown into OpenViking.
- Searching a known `viking://` corpus.
- Generating a retrieval-backed draft with `ar research`.

## Core Commands

```powershell
ar doctor
```

```powershell
ar health
```

```powershell
ar search-web "AI search tools" --max-results 5
```

```powershell
ar fetch-web "AI search tools" --max-results 5 --output data\web\ai-search-tools
```

```powershell
ar sync "AI search tools" --max-results 5 --output data\web\ai-search-tools --to viking://resources/ai-search-tools
```

```powershell
ar import-local .\examples\smoke_corpus --to viking://resources/smoke-corpus
```

```powershell
ar search "What is the core purpose of the second phase?" --scope viking://resources/smoke-corpus --top-k 3 --format text --documents-only
```

```powershell
ar research examples\smoke_corpus\research_questions.yaml --output reports\smoke_corpus_research.md --top-k 3
```

## Notes

- Prefer `--scope` when the target corpus is known.
- Use `search-web` for search-only tasks.
- Use `fetch-web` or `sync` when the results should be saved and reused.
- Use the smoke corpus for the smallest local demo.
- Do not commit `.env`, `config/ov.conf`, `config/ovcli.conf`, `data/`, or `reports/`.
