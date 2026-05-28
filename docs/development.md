# Development Guide

This guide is for contributors working on the codebase.

## Architecture Boundaries

```text
connectors/   upstream discovery APIs such as AnySearch
retrievers/   downstream retrieval backends such as OpenViking
workflows/    multi-step operations composed from connectors/retrievers
cli.py        command-line argument parsing and user-facing output
```

Keep connector code independent from OpenViking. Keep retriever code independent from AnySearch. Workflows are where they meet.

## Local Setup

```powershell
py -3.12 -m venv .venv
```

```powershell
.\.venv\Scripts\Activate.ps1
```

```powershell
python -m pip install -e .[dev,openviking] --no-build-isolation
```

## Test Commands

```powershell
python -m unittest discover -s tests
```

```powershell
python -m compileall -q src tests
```

```powershell
ar doctor
```

## Live Smoke Tests

Start OpenViking:

```powershell
.\scripts\start_openviking.ps1
```

Run the local smoke corpus:

```powershell
.\scripts\smoke_test.ps1
```

Run the synthetic corpus research workflow:

```powershell
.\examples\synthetic_ai_news\run_research.ps1
```

Run a low-volume live AnySearch sync:

```powershell
ar sync "OpenViking GitHub" --max-results 2 --output data\web\openviking-github --to viking://resources/openviking-github
```

## Release Checklist

1. Update `CHANGELOG.md`.
2. Update `README.md` and `docs/cli_reference.md` for new commands.
3. Run unit tests and compile checks.
4. Run `ar doctor`.
5. Run one local OpenViking smoke test.
6. Build the package:

```powershell
python -m build
```

7. Inspect the distribution:

```powershell
python -m twine check dist\*
```

8. Confirm no secrets or runtime artifacts are staged.
