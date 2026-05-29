# CLI Reference

The command line entry point is `ar`.

## Environment Check

```powershell
ar doctor
```

Checks Python, package installation, OpenViking package, OpenViking executable, local config, optional AnySearch key, and OpenViking server health.

```powershell
ar doctor --json
```

Prints machine-readable check results.

## OpenViking Service

```powershell
ar health
```

Checks `http://127.0.0.1:1933/health` by default.

```powershell
ar status
```

Shows OpenViking service, queue, model, retrieval, and filesystem status.

```powershell
ar status --json
```

Prints raw OpenViking JSON status.

## Resource Management

```powershell
ar import-local <path> --to <viking-uri>
```

Imports a local file or folder into OpenViking.

```powershell
ar tree <viking-uri> -L 2
```

Shows a resource tree.

## AnySearch Upstream

```powershell
ar search-web "query" --max-results 5
```

Searches public web material with AnySearch and prints normalized results.

```powershell
ar search-web "query" --max-results 5 --format json
```

Prints normalized JSON.

Useful filters:

```powershell
ar search-web "query" --domain github.com --language en --freshness week
```

## Materialize Web Results

```powershell
ar fetch-web "query" --max-results 5 --output data\web\topic-name
```

Writes:

```text
data\web\topic-name\raw\anysearch_response.json
data\web\topic-name\markdown\*.md
data\web\topic-name\manifest.json
```

## Sync Web Results Into OpenViking

```powershell
ar sync "query" --max-results 5 --output data\web\topic-name --to viking://resources/topic-name
```

This is the full AnySearch -> markdown -> OpenViking import path.

## Search Indexed Corpus

```powershell
ar search "question" --scope viking://resources/topic-name --top-k 5
```

Default output is JSON.

```powershell
ar search "question" --scope viking://resources/topic-name --format text --documents-only
```

Text output is easier to read. `--documents-only` filters generated `.abstract.md` and `.overview.md` files.

## Research Drafts

```powershell
ar research examples\smoke_corpus\research_questions.yaml --output reports\smoke_corpus_research.md
```

The YAML file should include:

```yaml
topic_title: "Demo research"
ov_root_uri: "viking://resources/demo"
sections:
  - id: overview
    heading: "Overview"
    question: "What is this corpus about?"
```

Useful options:

```powershell
ar research questions.yaml --output reports\draft.md --json-output reports\draft.json
```

```powershell
ar research questions.yaml --output reports\draft.md --top-k 5 --fetch-k 20
```

```powershell
ar research questions.yaml --output reports\draft.md --dedupe section --min-results-per-section 2
```
