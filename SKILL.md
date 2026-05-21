# OpenViking Search Skill

Use this skill when an AI agent or developer needs to search a local corpus that has already been imported into OpenViking, or needs a small reproducible workflow for importing local markdown into OpenViking.

## When To Use

Use this skill for:

- Searching local notes, markdown files, course materials, or previously collected news.
- Returning structured search results with `viking://` citations.
- Building a report or answer that should be grounded in local OpenViking resources.
- Demonstrating a local-corpus retrieval workflow without relying on live web search.

Do not use this skill as the primary tool when:

- The user only needs fresh public web search.
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
ov-search-skill health
```

Show OpenViking status:

```powershell
ov-search-skill status
```

Import a local markdown folder:

```powershell
ov-search-skill import-local .\examples\smoke_corpus --to viking://resources/smoke-corpus
```

Run the open-source reproducible synthetic corpus demo:

```powershell
.\examples\synthetic_ai_news\run_demo.ps1 -Question "为什么开源项目需要合成 demo 语料"
```

Search a corpus:

```powershell
ov-search-skill search "第二阶段重点做什么" --scope viking://resources/smoke-corpus --top-k 3
```

Return only original documents, filtering OpenViking generated summaries:

```powershell
ov-search-skill search "特朗普访华实际达成了哪些成果" --scope viking://resources/news-us-china-2026-05 --documents-only --format text
```

Generate a retrieval-backed research draft from a YAML question list:

```powershell
ov-search-skill research examples\news_us_china\research_questions.yaml --output reports\news_us_china_research_draft.md --top-k 5
```

For the synthetic corpus:

```powershell
ov-search-skill research examples\synthetic_ai_news\research_questions.yaml --output reports\synthetic_ai_news_research_draft.md --top-k 4
```

Write a JSON file for downstream automation:

```powershell
ov-search-skill research examples\synthetic_ai_news\research_questions.yaml --output reports\synthetic_ai_news_research_draft.md --json-output reports\synthetic_ai_news_research_draft.json
```

Tune research quality checks:

```powershell
ov-search-skill research examples\synthetic_ai_news\research_questions.yaml --output reports\synthetic_ai_news_research_draft.md --dedupe section --min-results-per-section 2
```

## Notes For Agents

- Prefer `--scope` whenever the target corpus is known.
- Use JSON output for downstream automation.
- Use `--documents-only` when citations should point to original source documents rather than `.abstract.md` or `.overview.md`.
- Use `research` when the user needs a multi-question retrieval draft with `viking://` citations.
- Use `--json-output` when another script or Agent needs structured research results.
- Use the default `--dedupe section` for cleaner reports; use `--dedupe none` only when debugging raw OpenViking output.
- Do not expose or commit API keys from `config/ov.conf`.
