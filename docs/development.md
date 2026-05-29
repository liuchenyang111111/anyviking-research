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

## Smoke Checks

Start OpenViking:

```powershell
.\scripts\start_openviking.ps1
```

Run the minimal local demo:

```powershell
.\scripts\smoke_test.ps1
```

Run a small research draft on the same corpus:

```powershell
ar research examples\smoke_corpus\research_questions.yaml --output reports\smoke_corpus_research.md --top-k 3
```

Run a low-volume live AnySearch sync:

```powershell
ar sync "OpenViking GitHub" --max-results 2 --output data\web\openviking-github --to viking://resources/openviking-github
```

## Skill Package

The repo includes a packaged skill under `skills/anyviking-research/`.
Keep the skill concise and move detailed command recipes or troubleshooting notes into `references/`.

## Release Checklist

1. Update `CHANGELOG.md`.
2. Update `README.md` and `docs/cli_reference.md` for command or workflow changes.
3. Run unit tests and compile checks.
4. Run `ar doctor`.
5. Run the smoke corpus demo.
6. Build the package:

```powershell
python -m build
```

7. Inspect the distribution:

```powershell
python -m twine check dist\*
```

8. Confirm no secrets or runtime artifacts are staged.
