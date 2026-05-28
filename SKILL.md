# AnyViking Research

Use this skill when an AI agent or developer needs a reproducible research workflow that uses AnySearch for upstream public-web discovery and OpenViking for downstream local indexing, search, and retrieval-backed research drafts.

## When To Use

Use this skill for:

- Searching local notes, markdown files, course materials, or previously collected news.
- Returning structured search results with `viking://` citations.
- Building a report or answer that should be grounded in local OpenViking resources.
- Demonstrating a local-corpus retrieval workflow without relying on live web search.
- Discovering public-web sources with AnySearch, saving them as markdown, then importing them into OpenViking.

Do not use this skill as the primary tool when:

- The user only needs fresh public web search and does not want to save or index results.
- OpenViking is not installed or cannot be started.
- The task requires a full web UI or autonomous research planner.

## Requirements

- Python 3.12 virtual environment.
- OpenViking 0.3.17 installed.
- OpenViking server running at `http://127.0.0.1:1933`.
- A configured OpenViking `ov.conf` with model provider credentials.

## Core Commands

Check server health:

```powershell
ar health
```

Show OpenViking status:

```powershell
ar status
```

Search the public web with AnySearch:

```powershell
ar search-web "AI search tools" --max-results 5
```

Save AnySearch results as raw JSON, markdown, and a manifest:

```powershell
ar fetch-web "AI search tools" --max-results 5 --output data\web\ai-search-tools
```

Search the web and import the saved markdown into OpenViking:

```powershell
ar sync "AI search tools" --max-results 5 --output data\web\ai-search-tools --to viking://resources/ai-search-tools
```

Import a local markdown folder:

```powershell
ar import-local .\examples\smoke_corpus --to viking://resources/smoke-corpus
```

Search a corpus:

```powershell
ar search "What is the core purpose of the second phase?" --scope viking://resources/smoke-corpus --top-k 3 --format text --documents-only
```

Run the synthetic corpus demo:

```powershell
.\examples\synthetic_ai_news\run_demo.ps1
```

Generate a retrieval-backed research draft:

```powershell
ar research examples\synthetic_ai_news\research_questions.yaml --output reports\synthetic_ai_news_research_draft.md --top-k 4
```

Write a JSON file for downstream automation:

```powershell
ar research examples\synthetic_ai_news\research_questions.yaml --output reports\synthetic_ai_news_research_draft.md --json-output reports\synthetic_ai_news_research_draft.json
```

Tune research quality checks:

```powershell
ar research examples\synthetic_ai_news\research_questions.yaml --output reports\synthetic_ai_news_research_draft.md --dedupe section --min-results-per-section 2
```

## Notes For Agents

- Prefer `--scope` whenever the target corpus is known.
- Use `search-web` for one-off public-web discovery.
- Use `fetch-web` when results should be inspected or curated before indexing.
- Use `sync` when results should go straight into OpenViking as a local corpus.
- Use JSON output for downstream automation.
- Use `--documents-only` when citations should point to original source documents rather than `.abstract.md` or `.overview.md`.
- Use `research` when the user needs a multi-question retrieval draft with `viking://` citations.
- Use `--json-output` when another script or agent needs structured research results.
- Use the default `--dedupe section` for cleaner reports; use `--dedupe none` only when debugging raw OpenViking output.
- Do not expose or commit API keys from `config/ov.conf`.
- Treat AnySearch as the upstream discovery layer and OpenViking as the downstream indexing and research layer.
