# Agent Notes

This is a short repo-local note for maintainers and AI helpers.

The formal Skill package is:

```text
skills/anyviking-research/SKILL.md
```

## Project Job

Use this project as a bridge:

```text
AnySearch -> markdown files -> OpenViking -> viking:// retrieval
```

Do not treat it as a Web UI, hosted service, VikingBot replacement, or full report writer.

## Usual Commands

Check the environment:

```powershell
ar doctor
```

Search the web:

```powershell
ar search-web "AI search tools" --max-results 5
```

Save web results locally:

```powershell
ar fetch-web "AI search tools" --max-results 5 --output data\web\ai-search-tools
```

Save and import into OpenViking:

```powershell
ar sync "AI search tools" --max-results 5 --output data\web\ai-search-tools --to viking://resources/ai-search-tools
```

Search a known OpenViking scope:

```powershell
ar search "What does this corpus say?" --scope viking://resources/ai-search-tools --top-k 5 --format text --documents-only
```

## Keep Local

Do not commit `.env`, real config files, `data/`, `reports/`, `workspace/`, roadmap notes, changelog notes, or generated corpora.
