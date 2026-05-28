# Architecture

AnyViking Research has three layers.

```text
AnySearch
  -> finds public web material

AnyViking Research
  -> normalizes search results
  -> writes raw JSON, markdown, and manifest files
  -> calls OpenViking import/search commands
  -> generates retrieval-based research drafts

OpenViking
  -> stores local resources
  -> builds semantic indexes
  -> returns `viking://` retrieval results
```

## Folder Roles

```text
src/anyviking_research/
  Application package.

src/anyviking_research/cli.py
  Implements the `ar` command.

src/anyviking_research/connectors/
  Upstream public-web search connectors.
  `anysearch.py` talks to AnySearch and converts API responses into normalized Python objects.

src/anyviking_research/retrievers/
  Downstream retrieval adapters.
  `openviking.py` calls OpenViking HTTP search endpoints and converts responses into SearchResult objects.

src/anyviking_research/workflows/
  Multi-step workflows.
  `fetch_web.py` writes AnySearch results to local files.
  `research.py` reads YAML questions and creates markdown/JSON research drafts.

tests/
  Unit tests for connector, workflow, CLI, retriever, and research logic.

config/
  OpenViking server and CLI config examples.
  Real local configs are git-ignored.

scripts/
  PowerShell helper scripts, especially OpenViking startup and smoke testing.

examples/
  Demo corpora and demo scripts.

docs/
  Learning notes, architecture notes, FAQ, installation notes, and run records.

data/
  Runtime web-search output. Ignored by git.

reports/
  Runtime research reports. Ignored by git.

workspace/
  OpenViking runtime workspace. Ignored by git.
```

## Main Commands

```powershell
ar search-web "OpenViking GitHub" --max-results 3
```

Searches AnySearch and prints web results.

```powershell
ar fetch-web "OpenViking GitHub" --max-results 3 --output data\web\openviking-github
```

Searches AnySearch and saves raw JSON, markdown files, and a manifest.

```powershell
ar sync "OpenViking GitHub" --max-results 3 --output data\web\openviking-github --to viking://resources/openviking-github
```

Runs the full upstream-to-downstream import path.

```powershell
ar search "What is OpenViking?" --scope viking://resources/openviking-github --format text --documents-only
```

Searches the indexed OpenViking corpus.

```powershell
ar research questions.yaml --output reports\draft.md
```

Generates a retrieval-based research draft.

## Why This Shape

The project keeps AnySearch and OpenViking separate:

- AnySearch is good at discovering public web material.
- OpenViking is good at storing local resources and retrieving them with stable `viking://` references.
- AnyViking Research is the workflow layer between them.

This keeps the first usable version CLI-first and easy to debug. MCP, skill packaging, OpenVikingBot, and Web UI can be added later as wrappers around the same tested workflow.
