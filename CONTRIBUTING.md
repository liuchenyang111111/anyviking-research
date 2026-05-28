# Contributing

Thanks for helping improve AnyViking Research. This project is still early, so the most useful contributions are bug reports, small focused fixes, tests, and documentation that makes the workflow easier to reproduce.

## Development Setup

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

```powershell
python -m pip install -e .[dev,openviking] --no-build-isolation
```

## Before Opening A Pull Request

Run these checks:

```powershell
python -m unittest discover -s tests
```

```powershell
python -m compileall -q src tests
```

```powershell
ar doctor
```

For changes that touch OpenViking behavior, also run a local smoke test:

```powershell
.\scripts\smoke_test.ps1
```

For changes that touch AnySearch, use a low `--max-results` value and avoid committing files under `data/`.

## Coding Guidelines

- Keep the CLI stable and script-friendly.
- Prefer small modules with clear boundaries: connectors, retrievers, workflows, and CLI glue.
- Keep AnySearch as upstream discovery and OpenViking as downstream indexing/retrieval.
- Do not commit local runtime files, API keys, `data/`, `workspace/`, or generated reports.
- Add or update tests for behavior changes.
- Keep examples reproducible without private data.

## Commit Scope

Good pull requests usually fit one of these scopes:

- Connector improvements.
- OpenViking adapter fixes.
- Research workflow improvements.
- Documentation and examples.
- Tests and packaging.

Large changes such as Web UI, MCP, OpenVikingBot integration, or LLM synthesis should start with an issue and design notes.
