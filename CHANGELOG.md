# Changelog

## 0.6.0

- Reframed the repository as a CLI-first open-source research toolkit rather than a small demo.
- Added `ar doctor` environment diagnostics.
- Added package metadata, optional dependencies, typed package marker, and source distribution manifest.
- Added CLI, configuration, development, security, contributing, and open-source readiness documentation.
- Added issue templates, pull request template, and package build checks in CI.
- Verified editable install, unit tests, compile checks, package build, and `twine check`.

## 0.5.0

- Renamed the project package and CLI to AnyViking Research / `anyviking_research` / `ar`.
- Added AnySearch upstream connector for public-web discovery.
- Added `ar search-web`, `ar fetch-web`, and `ar sync`.
- Added raw JSON, markdown, and manifest output for web search results.
- Added tests for AnySearch normalization, web-result materialization, and sync import orchestration.

## 0.4.0

- Added section-level research result deduplication.
- Added citation statistics to markdown and JSON research output.
- Added research quality warnings for empty, low-coverage, and highly reused evidence.
- Added `--dedupe`, `--no-citation-stats`, and `--min-results-per-section` CLI options.

## 0.3.1

- Streamlined documentation by merging demo run records and removing duplicated stage documents.
- Added `ROADMAP.md`.
- Added `--json-output` for `ar research`.
- Added GitHub Actions test workflow.
- Removed unused optional news dependencies from package metadata.
- Added project review and next-stage plan.

## 0.3.0

- Added open-source reproducible synthetic AI news corpus.
- Added synthetic corpus demo scripts and research questions.
- Updated README and docs to prioritize the synthetic demo for public reproduction.
- Verified synthetic research draft generation with 5 sections and 20 `viking://` citations.

## 0.2.0

- Added `ar research`.
- Added YAML-based multi-question retrieval workflow.
- Added markdown research draft rendering.
- Added filtering for OpenViking generated summaries and unhelpful placeholder answers.
- Added research workflow tests.

## 0.1.0

- Initialized the Python package and CLI.
- Added OpenViking health, status, import, tree, and search wrappers.
- Added smoke corpus and Windows PowerShell helper scripts.
- Added initial README, SKILL.md, architecture docs, and tests.
