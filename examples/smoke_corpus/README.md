# Smoke Corpus

This is the smallest local demo kept in the repository.

Use it when you want to verify that:

- OpenViking can import a local markdown folder
- `ar search` can retrieve `viking://` results
- `ar research` can generate a small retrieval-backed draft

## Quick Start

Run the scripted smoke test:

```powershell
.\scripts\smoke_test.ps1
```

Import the corpus manually:

```powershell
ar import-local .\examples\smoke_corpus --to viking://resources/smoke-corpus
```

Run a manual search:

```powershell
ar search "What is the core purpose of the second phase?" --scope viking://resources/smoke-corpus --top-k 3 --format text --documents-only
```

Generate a small research draft:

```powershell
ar research examples\smoke_corpus\research_questions.yaml --output reports\smoke_corpus_research.md --top-k 3
```
