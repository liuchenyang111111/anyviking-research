# AnyViking Research Roadmap

AnyViking Research connects AnySearch upstream discovery with OpenViking downstream indexing and retrieval.

## Done

### v0.1 Local OpenViking wrapper

- Project-specific OpenViking config examples.
- `ar health`, `ar status`, `ar import-local`, `ar tree`, and `ar search`.
- JSON and text search output.
- `--documents-only` filtering for generated `.abstract.md` / `.overview.md` files.

### v0.2 Retrieval research workflow

- YAML question file input.
- Per-section OpenViking retrieval.
- Markdown research draft output.
- Optional JSON output.
- Citation statistics and quality warnings.

### v0.3 Demo corpus

- Small smoke corpus.
- Synthetic AI news corpus that is safe to keep in the repository.
- Demo scripts for search and research generation.

### v0.4 AnySearch upstream connector

- `AnySearchConnector` for `POST https://api.anysearch.com/v1/search`.
- Support for AnySearch `data.results` response shape.
- Optional `ANYSEARCH_API_KEY` environment variable.
- `ar search-web` for web-only search.
- `ar fetch-web` for raw JSON, markdown corpus, and manifest output.
- `ar sync` for AnySearch -> markdown -> OpenViking import.

### v0.5 End-to-end proof

Verified locally on 2026-05-28:

- OpenViking 0.3.17 health check passed.
- AnySearch returned live results for `OpenViking GitHub`.
- `ar sync` created markdown files and imported them into `viking://resources/openviking-github-sync`.
- `ar search` retrieved the imported web corpus from OpenViking.
- `ar research` generated `reports\openviking_github_sync_research.md` and JSON output.
- Unit tests passed.

## Next

### v0.6 Better research ergonomics

- Add topic presets for common research tasks.
- Add clearer progress output during long OpenViking imports.
- Add a command to create a starter YAML question file for a synced topic.

### v0.7 Optional LLM synthesis

- Add an optional summarization step that turns retrieved evidence into a stronger narrative draft.
- Keep citations grounded in `viking://` URIs.
- Make the LLM provider optional so search/indexing still works without it.

### v0.8 MCP / OpenVikingBot adapters

- Wrap the stable CLI workflow as an MCP tool if agents need direct tool calls.
- Consider OpenVikingBot integration after the CLI workflow remains stable.

### v0.9 Web UI, only if needed

- A small UI could show search, saved corpus, indexed resources, and generated reports.
- It is not required for the current CLI-first project.
