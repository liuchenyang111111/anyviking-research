# Project Context

This file is a short memory entry for the repository owner and AI helpers.

## Goal

Build a reusable CLI workflow that treats:

```text
AnySearch as the upstream discovery layer
OpenViking as the downstream indexing and retrieval layer
AnyViking Research as the workflow layer between them
```

## Current Shape

Repository path:

```text
D:\Github\anyviking-research
```

Current focus:

- Python package and `ar` CLI
- OpenViking health, import, tree, and search operations
- AnySearch upstream discovery
- Local markdown materialization and sync into OpenViking
- Retrieval-backed research drafts
- One minimal local demo corpus under `examples/smoke_corpus`
- One packaged agent skill under `skills/anyviking-research`

Not in scope yet:

- Web UI
- hosted service
- MCP server
- autonomous planner
- full LLM-written final reports
