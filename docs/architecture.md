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

## Core Folders

```text
src/anyviking_research/
  Application package.

src/anyviking_research/cli.py
  Implements the `ar` command.

src/anyviking_research/connectors/
  Upstream public-web search connectors.

src/anyviking_research/retrievers/
  Downstream retrieval adapters.

src/anyviking_research/workflows/
  Multi-step workflows such as fetch and research.

tests/
  Unit tests for connector, workflow, CLI, retriever, and research logic.

config/
  OpenViking config examples. Real local configs are git-ignored.

scripts/
  Local helper scripts, especially startup and smoke testing.

examples/smoke_corpus/
  Minimal local demo corpus for import, search, and research.

skills/anyviking-research/
  Packaged skill instructions for agents that should drive the CLI.

docs/
  Core docs only: architecture, CLI reference, configuration, and development.
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

Searches an indexed OpenViking corpus.

```powershell
ar research examples\smoke_corpus\research_questions.yaml --output reports\smoke_corpus_research.md
```

Generates a retrieval-based research draft.

## Why This Shape

The project keeps AnySearch and OpenViking separate:

- AnySearch is good at discovering fresh public web material.
- OpenViking is good at storing local resources and retrieving them with stable `viking://` references.
- AnyViking Research is the workflow layer between them.

That makes the first usable version CLI-first and easy to debug. Skill packaging, MCP, bots, and Web UI can be added later as wrappers around the same tested workflow.
