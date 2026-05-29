# Development Guide

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev,openviking] --no-build-isolation
```

## Code Boundaries

Keep the layers separate:

```text
connectors/   calls upstream search APIs
workflows/    writes files and combines simple steps
retrievers/   calls downstream retrieval systems
cli.py        parses commands and prints user-facing output
```

Do not put OpenViking logic into AnySearch connectors.

Do not put AnySearch logic into OpenViking retrievers.

## Checks

Run these before committing:

```powershell
python -m unittest discover -s tests
python -m compileall -q src tests
```

Optional environment check:

```powershell
ar doctor
```

For a live AnySearch/OpenViking check, keep the result count low:

```powershell
ar sync "OpenViking GitHub" --max-results 2 --output data\web\openviking-github --to viking://resources/openviking-github
```

## Packaging

Build and inspect the package:

```powershell
python -m build
python -m twine check dist\*
```

Before publishing or committing, confirm that no secrets or runtime artifacts are staged.
