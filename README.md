# AnyViking Research

AnyViking Research is a CLI-first open-source research toolkit that connects public-web discovery with local semantic indexing.

```text
AnySearch -> discover public web sources
AnyViking Research -> normalize, materialize, import, search, and draft
OpenViking -> index local resources and return `viking://` citations
```

The project is the workflow layer between fresh web search and reusable local retrieval. It helps you collect sources, save them as local corpus files, index them with OpenViking, search them with stable resource URIs, and generate retrieval-backed research drafts.

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
| Minimal local demo | `examples/smoke_corpus` | implemented |
| Tests and CI | `tests/`, GitHub Actions | implemented |

## Project Maturity

This is an alpha-stage toolkit. The core CLI workflow is implemented and tested:

```text
AnySearch live query
-> markdown corpus output
-> OpenViking import
-> OpenViking semantic search
-> retrieval-backed research draft
```

It is not yet a Web UI, hosted service, MCP server, or autonomous research product. Those can be added later on top of the CLI foundation.

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

Search the public web:

```powershell
ar search-web "OpenViking GitHub" --max-results 3
```

Save web results as a local corpus:

```powershell
ar fetch-web "OpenViking GitHub" --max-results 3 --output data\web\openviking-github
```

Search the web and import it into OpenViking:

```powershell
ar sync "OpenViking GitHub" --max-results 3 --output data\web\openviking-github --to viking://resources/openviking-github
```

Search an indexed corpus:

```powershell
ar search "What is OpenViking?" --scope viking://resources/openviking-github --top-k 3 --format text --documents-only
```

Generate a research draft:

```powershell
ar research examples\smoke_corpus\research_questions.yaml --output reports\smoke_corpus_research.md
```

## Minimal Demo

Run the local smoke test:

```powershell
.\scripts\smoke_test.ps1
```

Run a small research draft on the same demo corpus:

```powershell
ar research examples\smoke_corpus\research_questions.yaml --output reports\smoke_corpus_research.md --top-k 3
```

## Packaged Skill

The formal agent skill is packaged under:

```text
skills/anyviking-research/
```

Use this folder when installing or sharing the skill. It contains:

```text
SKILL.md
agents/openai.yaml
references/commands.md
references/workflow.md
references/troubleshooting.md
```

The repository root also has `AGENT_NOTES.md` for maintainers and local AI helpers. It is not the formal skill entry point.

## Documentation

- [Architecture](docs/architecture.md)
- [CLI reference](docs/cli_reference.md)
- [Configuration](docs/configuration.md)
- [Development guide](docs/development.md)
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
examples/smoke_corpus/    minimal reproducible demo corpus
skills/anyviking-research/ packaged agent skill
docs/                     core user and developer documentation
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
