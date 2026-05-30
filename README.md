[English](README.md) | [简体中文](README-ZH.md)

# AnyViking Research

AnyViking Research is a CLI bridge that turns public web results from AnySearch into local Markdown and imports them into OpenViking for downstream retrieval.

```text
AnySearch -> local markdown -> OpenViking -> viking:// retrieval
```

The current stage focuses on four things:

- search public web sources through AnySearch
- save raw JSON, markdown, and a manifest locally
- import saved material into OpenViking
- let your own Agent retrieve the indexed content through `anyviking search` or the OpenViking API/CLI

An optional Agent Skill is also included in [skills/anyviking-research](skills/anyviking-research) so an Agent can follow the same workflow with stable instructions.

## References

- [AnySearch Skill](https://github.com/anysearch-ai/anysearch-skill)
- [AnySearch docs](https://www.anysearch.com/docs)
- [OpenViking](https://github.com/volcengine/OpenViking)
- [OpenViking docs](https://docs.openviking.ai/)

## Requirements

- Python `3.12`
- A local OpenViking installation
- Optional `ANYSEARCH_API_KEY` for more stable AnySearch access

## Quick Start

Windows PowerShell:

```powershell
git clone https://github.com/liuchenyang111111/anyviking-research.git
cd anyviking-research
.\install.ps1
.\.venv\Scripts\anyviking.exe doctor
```

Linux / macOS:

```bash
git clone https://github.com/liuchenyang111111/anyviking-research.git
cd anyviking-research
./install.sh
source .venv/bin/activate
anyviking doctor
```

Install development dependencies:

```powershell
.\install.ps1 -Dev
```

```bash
./install.sh --dev
```

## Configure OpenViking

Copy the example config files:

```powershell
Copy-Item config\ov.conf.example config\ov.conf
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

```bash
cp config/ov.conf.example config/ov.conf
cp config/ovcli.conf.example config/ovcli.conf
```

Edit `config/ov.conf` with your own model-provider settings, then start OpenViking:

```powershell
.\scripts\start_openviking.ps1
```

```bash
./scripts/start_openviking.sh
```

Check the service:

```bash
anyviking health
```

## Configure AnySearch

If you have an AnySearch key:

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

```bash
export ANYSEARCH_API_KEY="your-key"
```

If you need to point to another compatible endpoint:

```powershell
$env:ANYSEARCH_API_URL = "https://your-endpoint.example"
```

```bash
export ANYSEARCH_API_URL="https://your-endpoint.example"
```

The CLI also respects `OPENVIKING_URL` for commands that talk directly to the OpenViking HTTP service.

## Main Commands

| Command | Purpose |
| --- | --- |
| `anyviking doctor` | Check local environment readiness |
| `anyviking health` | Check OpenViking health |
| `anyviking status` | Show OpenViking service status |
| `anyviking search-web` | Search public web sources through AnySearch |
| `anyviking fetch-web` | Save raw JSON, markdown, and a manifest locally |
| `anyviking sync` | Search, save, and import into OpenViking |
| `anyviking import-local` | Import an existing local file or folder |
| `anyviking tree` | Inspect a `viking://` resource tree |
| `anyviking search` | Search indexed OpenViking material |

Full command notes: [docs/cli_reference.md](docs/cli_reference.md)

## Typical Flow

Search only:

```bash
anyviking search-web "OpenViking GitHub" --max-results 3
```

Save search results locally:

```bash
anyviking fetch-web "OpenViking GitHub" --max-results 3 --output data/web/openviking-github
```

Save and import into OpenViking:

```bash
anyviking sync "OpenViking GitHub" --max-results 3 --output data/web/openviking-github --to viking://resources/openviking-github
```

Inspect the imported tree:

```bash
anyviking tree viking://resources/openviking-github -L 2
```

Retrieve indexed material:

```bash
anyviking search "What is OpenViking?" --scope viking://resources/openviking-github --top-k 3 --format text --documents-only
```

## Local Output

Runtime output stays local and is ignored by Git:

```text
data/       fetched AnySearch results and markdown files
workspace/  OpenViking local database, indexes, and logs
reports/    optional local generated output
config/ov.conf
config/ovcli.conf
.env
```

## How Agents Read The Imported Data

`viking://resources/...` is a virtual OpenViking URI, not a normal file path.

An Agent needs a tool to read it, for example:

```bash
anyviking search "your question" --scope viking://resources/your-topic --format json --documents-only
```

An Agent can also call the OpenViking API/CLI directly.

## Troubleshooting

- [docs/configuration.md](docs/configuration.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
- [docs/architecture.md](docs/architecture.md)

## Validation

```bash
python -m unittest discover -s tests
python -m compileall -q src tests
python -m build
python -m twine check dist/*
```

## License

AnyViking Research uses the MIT License. OpenViking remains a separate upstream dependency and follows its own license terms.
