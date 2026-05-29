---
name: anyviking-research
description: Coordinate AnySearch public-web discovery with OpenViking local indexing and retrieval through the `ar` CLI. Use when Codex needs to search the web, save results as markdown, import local corpus files into OpenViking, search a known `viking://` scope, or generate a retrieval-backed research draft.
---

# AnyViking Research

Use this skill when the task should run through the `ar` CLI instead of ad hoc shell commands.

## Prerequisites

- Use a Python 3.12 environment where `ar` is installed.
- Expect OpenViking to be available at `http://127.0.0.1:1933`.
- Treat AnySearch as optional for search-only or sync workflows.

## Start Here

1. Run `ar doctor` when environment state is unclear.
2. If the user only wants public-web discovery, read `references/commands.md`.
3. If the user wants to index or research, read `references/workflow.md`.
4. If a command fails, read `references/troubleshooting.md`.

## Working Rules

- Prefer `ar search-web` for search-only tasks.
- Prefer `ar fetch-web` when results should be inspected before indexing.
- Prefer `ar sync` when web results should go straight into OpenViking.
- Prefer `ar import-local` when the corpus already exists on disk.
- Prefer `ar search` for one question against a known scope.
- Prefer `ar research` for multi-question retrieval drafts.
- Prefer `--documents-only` when citations should point to source documents instead of generated summaries.
- Keep runtime output in `data/`, `reports/`, or `workspace/`; do not treat those as source files.
- Do not commit `.env`, `config/ov.conf`, or `config/ovcli.conf`.

## Local Demo

For the smallest reproducible demo, use `examples/smoke_corpus` and `.\scripts\smoke_test.ps1`.
