# Search Workflow

The basic local retrieval flow has four steps:

1. Prepare local notes or documents as markdown files.
2. Import the markdown folder into OpenViking with `ar import-local`.
3. Wait for OpenViking to finish indexing. `ar import-local` does this by default.
4. Ask questions with `ar search` or `ar research`.

A successful smoke test should return results under this scope:

```text
viking://resources/smoke-corpus
```

Run the smoke test:

```powershell
.\scripts\smoke_test.ps1
```

Run a manual search:

```powershell
ar search "What is the core purpose of the second phase?" --scope viking://resources/smoke-corpus --top-k 3 --format text --documents-only
```

For multi-question research, write the questions in YAML and run:

```powershell
ar research <questions.yaml> --output reports\research_draft.md
```
