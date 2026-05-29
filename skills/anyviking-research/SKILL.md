---
name: anyviking-research
description: Use the `ar` CLI to search public web sources with AnySearch, save them as markdown, import them into OpenViking, and search a known `viking://` scope. Use this when the user wants fresh web material made available to their own Agent through OpenViking retrieval.
---

# AnyViking Research

This Skill is a workflow guide for the `ar` CLI.

It does not search or index by itself. The actual work is done by the installed `ar` command.

## Start Here

1. If environment state is unclear, run `ar doctor`.
2. If the user only wants web results, read `references/commands.md`.
3. If the user wants data saved or imported, read `references/workflow.md`.
4. If a command fails, read `references/troubleshooting.md`.

## Choose The Command

- Use `ar search-web` to search only.
- Use `ar fetch-web` to save web results as local files.
- Use `ar sync` to save web results and import them into OpenViking.
- Use `ar import-local` when the user already has local markdown files.
- Use `ar search` when the user has a known `viking://` scope.

## Rules

- Keep generated files under `data/`, `reports/`, or `workspace/`.
- Do not commit `.env`, `config/ov.conf`, `config/ovcli.conf`, `data/`, `reports/`, or `workspace/`.
- Prefer `--documents-only` when the user wants source documents instead of OpenViking-generated summaries.
- If `ar` is not on PATH, try `.\.venv\Scripts\ar.exe`.

## Upstream References

- AnySearch: https://github.com/anysearch-ai/anysearch-skill
- OpenViking: https://github.com/volcengine/OpenViking
