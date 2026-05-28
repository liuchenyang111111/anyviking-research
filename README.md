# AnyViking Research

AnyViking Research is a CLI-first open-source research toolkit that connects public-web discovery with local semantic indexing.

```text
AnySearch -> discover public web sources
AnyViking Research -> normalize, materialize, import, search, and draft
OpenViking -> index local resources and return `viking://` citations
```

The project is designed for reproducible research workflows: collect sources, store them as local corpus files, index them with OpenViking, search them with stable resource URIs, and generate retrieval-backed research drafts.

## Why This Project Exists

Search and research workflows often split into two disconnected parts:

- public web search for fresh material;
- local indexing for reusable evidence, citations, and repeated analysis.

AnyViking Research is the workflow layer between them. It keeps AnySearch and OpenViking separate, but gives users one practical CLI for the full path.

## Current Capabilities

| Area | Command/API | Status |
| --- | --- | --- |
| Environment diagnostics | `ar doctor` | implemented |
| OpenViking health/status | `ar health`, `ar status` | implemented |
| Public web discovery | `ar search-web` | implemented with AnySearch |
| Web result materialization | `ar fetch-web` | raw JSON, markdown, manifest |
| Web-to-index sync | `ar sync` | AnySearch -> markdown -> OpenViking |
| Local corpus import | `ar import-local` | implemented |
| Resource inspection | `ar tree` | implemented |
| Semantic retrieval | `ar search` | JSON/text output |
| Research drafts | `ar research` | markdown and optional JSON |
| Reproducible examples | `examples/` | smoke and synthetic corpora |
| Tests and CI | `tests/`, GitHub Actions | unit tests without live services |

## Project Maturity

This is an alpha-stage open-source toolkit. The core CLI workflow is implemented and tested. Live local verification has successfully run:

```text
AnySearch live query
-> markdown corpus output
-> OpenViking import
-> OpenViking semantic search
-> retrieval-backed research draft
```

The project is not yet a hosted service, Web UI, autonomous planner, or full report-writing product. Those are future wrappers around the CLI foundation.

## Install

```powershell
cd D:\Github\anyviking-research
```

```powershell
py -3.12 -m venv .venv
```

```powershell
.\.venv\Scripts\Activate.ps1
```

```powershell
python -m pip install --upgrade pip setuptools wheel
```

For full local use with OpenViking:

```powershell
python -m pip install -e .[openviking] --no-build-isolation
```

For development:

```powershell
python -m pip install -e .[dev,openviking] --no-build-isolation
```

## Configure

Copy local config examples:

```powershell
Copy-Item config\ov.conf.example config\ov.conf
```

```powershell
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

Edit `config\ov.conf` and set your model provider credentials. Do not commit real config files.

Optionally set AnySearch API key:

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

Run diagnostics:

```powershell
ar doctor
```

## Start OpenViking

```powershell
.\scripts\start_openviking.ps1
```

```powershell
ar health
```

## Quick Workflow

Search public web results:

```powershell
ar search-web "OpenViking GitHub" --max-results 3
```

Save web results as a local corpus:

```powershell
ar fetch-web "OpenViking GitHub" --max-results 3 --output data\web\openviking-github
```

Import saved corpus into OpenViking:

```powershell
ar import-local data\web\openviking-github\markdown --to viking://resources/openviking-github
```

Or run the full sync in one command:

```powershell
ar sync "OpenViking GitHub" --max-results 3 --output data\web\openviking-github --to viking://resources/openviking-github
```

Search the indexed corpus:

```powershell
ar search "What is OpenViking?" --scope viking://resources/openviking-github --top-k 3 --format text --documents-only
```

Generate a research draft:

```powershell
ar research examples\synthetic_ai_news\research_questions.yaml --output reports\synthetic_ai_news_research_draft.md
```

## Reproducible Demo

The recommended demo uses project-owned synthetic markdown files:

```powershell
.\examples\synthetic_ai_news\run_demo.ps1
```

```powershell
.\examples\synthetic_ai_news\run_research.ps1
```

For a smaller smoke test:

```powershell
.\scripts\smoke_test.ps1
```

## Documentation

- [Architecture](docs/architecture.md)
- [CLI reference](docs/cli_reference.md)
- [Configuration](docs/configuration.md)
- [Development guide](docs/development.md)
- [Open-source readiness](docs/open_source_readiness.md)
- [Research workflow](docs/research_workflow.md)
- [FAQ](docs/faq.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## Repository Layout

```text
src/anyviking_research/
  cli.py                  command-line interface
  connectors/             upstream web discovery connectors
  retrievers/             downstream retrieval adapters
  workflows/              composed workflows such as fetch and research

tests/                    unit tests without live service requirements
config/                   example OpenViking config files
scripts/                  local helper scripts
examples/                 reproducible corpora and demos
docs/                     user and developer documentation
```

Runtime output is ignored by git:

```text
data/
reports/
workspace/
config/ov.conf
config/ovcli.conf
```

## Tests

```powershell
python -m unittest discover -s tests
```

```powershell
python -m compileall -q src tests
```

## License

AnyViking Research uses the MIT License. OpenViking is a separate upstream dependency; follow OpenViking's license terms when using it.
