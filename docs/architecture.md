# Architecture

AnyViking Research is intentionally small.

```text
AnySearch
  finds public web pages

AnyViking Research
  saves normalized results as local markdown
  imports those markdown files into OpenViking
  searches a known viking:// scope

OpenViking
  stores resources in its workspace
  builds indexes
  returns viking:// retrieval results
```

For upstream search behavior, read:

- [AnySearch Skill](https://github.com/anysearch-ai/anysearch-skill)
- [AnySearch docs](https://www.anysearch.com/docs)

For storage, resource paths, and retrieval behavior, read:

- [OpenViking](https://github.com/volcengine/OpenViking)
- [OpenViking docs](https://docs.openviking.ai/)

## Code Layout

```text
src/anyviking_research/cli.py
  The `ar` command.

src/anyviking_research/connectors/
  Upstream search connectors. Today this means AnySearch.

src/anyviking_research/workflows/
  Multi-step local workflows, such as writing web results to markdown.

src/anyviking_research/retrievers/
  Downstream retrieval adapters. Today this means OpenViking.
```

## Main Flow

```powershell
ar sync "OpenViking GitHub" --max-results 3 --output data\web\openviking-github --to viking://resources/openviking-github
```

Then query the imported scope:

```powershell
ar search "What is OpenViking?" --scope viking://resources/openviking-github --format text --documents-only
```

## What This Project Does Not Hide

The project does not reimplement AnySearch or OpenViking.

It keeps their jobs separate:

- AnySearch discovers sources.
- OpenViking stores and retrieves sources.
- This project connects them with a simple CLI.
