# Workflow Guide

## Choose the Smallest Useful Path

If the user only wants fresh results from the web:

```text
search-web
```

If the user wants web results saved as reusable local files:

```text
fetch-web
```

If the user wants web results indexed in OpenViking right away:

```text
sync
```

If the user already has markdown files locally:

```text
import-local -> search
```

If the user wants a multi-question draft:

```text
import-local or sync -> research
```

## Recommended Local Demo

Use the smallest repo-owned corpus first:

1. `.\scripts\smoke_test.ps1`
2. `ar research examples\smoke_corpus\research_questions.yaml --output reports\smoke_corpus_research.md --top-k 3`

This demo avoids live AnySearch dependency and keeps the validation loop short.
