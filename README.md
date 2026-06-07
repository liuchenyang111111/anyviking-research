[English](README.md) | [简体中文](README-ZH.md)

# AnyViking Research

AnyViking Research is a CLI bridge that turns public web results from AnySearch into local Markdown and imports them into OpenViking for downstream retrieval.

```text
AnySearch -> local markdown -> OpenViking -> viking:// retrieval
```

The current stage focuses on these things:

- search public web sources through AnySearch
- save raw JSON, markdown, and a manifest locally
- import saved material into OpenViking
- let your own Agent retrieve the indexed content through `anyviking search` or the OpenViking API/CLI
- run reusable YAML cases for reproducible research or forecast-data collection tasks
- score OracleProto-style forecast cases with probability outputs and Brier scores
- generate reviewable Skill evolution candidates from local forecast trajectories

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
| `anyviking run-case` | Run a reusable YAML collection case |
| `anyviking forecast` | Run a scored forecast case with trajectory output |
| `anyviking evolve` | Collect trajectories, propose candidates, validate, and publish reviewed Skill updates |
| `anyviking evolve-skill` | Generate workflow suggestions from run logs |
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

## Reusable Cases

For repeatable technology-trend or forecast-data collection, use a YAML case:

```bash
anyviking run-case cases/oracleproto/train/deepseek_v4.yaml
```

This searches the configured queries, saves markdown, writes an `evidence_pack.md`, imports the material into OpenViking, and records a local run log under `data/run_logs/`.

Sample cases live in [cases](cases). More details: [docs/cases.md](docs/cases.md)

Run a scored forecast case:

```bash
anyviking forecast cases/oracleproto/train/deepseek_v4.yaml --skip-import
```

Run baseline comparisons:

```bash
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode no-retrieval --skip-import
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode naive-search --skip-import
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode anyviking
anyviking forecast cases/oracleproto/eval/apple_tv.yaml --baseline-mode anyviking --candidate-dir data/evolution/candidates/<candidate-id>
anyviking evolve baselines --runs data/runs --output data/evolution/candidates/<candidate-id>/baselines.json
```

Generate lightweight Skill improvement suggestions from successful case logs:

```bash
anyviking evolve-skill --log data/run_logs/runs.jsonl
```

This writes local outputs under `data/skill_evolution/`. More details: [docs/skill_evolution.md](docs/skill_evolution.md)

Generate a forecast-driven evolution candidate from trajectories:

```bash
anyviking evolve collect --runs data/runs
anyviking evolve propose --runs data/runs
anyviking evolve validate data/evolution/candidates/<candidate-id> --baseline data/evolution/candidates/<candidate-id>/baselines.json
```

## Forecast And Evolution Flow

The forecast loop is designed for reproducible checks, not one-off demos:

```text
OracleProto case
-> AnySearch collection
-> local markdown evidence
-> optional OpenViking import and retrieval
-> LLM probability forecast
-> answer scoring with Brier score
-> trajectory
-> reviewed Skill candidate
```

Use `train` cases to generate candidates. Use `eval` cases only to compare the current workflow and a candidate with the same LLM and the same case set.

The validation gate compares four groups:

```text
no_retrieval
naive_search
anyviking_baseline
anyviking_candidate
```

Generated candidates stay under `data/evolution/` until you review and publish them.

## Local Output

Runtime output stays local and is ignored by Git:

```text
data/       fetched AnySearch results and markdown files
workspace/  OpenViking local database, indexes, and logs
reports/    optional local generated output
data/run_logs/
data/runs/
data/evolution/
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
- [docs/cases.md](docs/cases.md)
- [docs/skill_evolution.md](docs/skill_evolution.md)
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
