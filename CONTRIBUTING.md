# Contributing

Thanks for helping improve AnyViking Research.

This project is small on purpose. Good changes usually make the CLI easier to install, run, test, or understand.

## Setup

```powershell
git clone https://github.com/liuchenyang111111/anyviking-research.git
cd anyviking-research
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .[dev,openviking] --no-build-isolation
```

## Before A Pull Request

Run:

```powershell
python -m unittest discover -s tests
python -m compileall -q src tests
ar doctor
```

If you changed AnySearch behavior, test with a low `--max-results` value.

If you changed OpenViking behavior, run a small local import/search check with your own corpus.

## Guidelines

- Keep `ar` stable and script-friendly.
- Keep AnySearch code in `connectors/`.
- Keep OpenViking retrieval code in `retrievers/`.
- Put simple multi-step file workflows in `workflows/`.
- Do not commit `.env`, real config files, `data/`, `reports/`, `workspace/`, generated corpora, roadmap notes, or changelog notes.

## Good PR Scope

- AnySearch connector fixes.
- OpenViking adapter fixes.
- CLI usability.
- Docs and Skill instructions.
- Tests and packaging.

Large wrappers such as Web UI, MCP, or VikingBot should start with an issue and design notes.
