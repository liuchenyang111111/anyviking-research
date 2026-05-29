# Project Context

This is a short memory entry for the repository owner and AI helpers.

## Goal

Build a small CLI bridge:

```text
AnySearch -> local markdown -> OpenViking -> viking:// retrieval
```

The project should help users put fresh web material into OpenViking. Their own Agent can then read the indexed data with `ar search` or another OpenViking adapter.

## Current Shape

Current focus:

- Python package and `ar` CLI.
- AnySearch public-web discovery.
- Markdown materialization under `data/`.
- Sync into OpenViking resources.
- Search against a known `viking://` scope.
- Packaged Agent Skill under `skills/anyviking-research`.

Not in public repo scope:

- bundled example corpus
- generated reports
- roadmap/changelog notes
- Web UI
- hosted service
- MCP server
- VikingBot
- autonomous planner
- full report generation
