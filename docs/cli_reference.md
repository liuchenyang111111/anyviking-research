# CLI Reference

The main command is `anyviking`.

If your virtual environment is not active, use:

```powershell
.\.venv\Scripts\anyviking.exe doctor
```

```bash
.venv/bin/anyviking doctor
```

## Check Environment

```bash
anyviking doctor
```

Use JSON output when another tool or Agent needs to parse the result:

```bash
anyviking doctor --json
```

## OpenViking Service

```bash
anyviking health
```

```bash
anyviking status
```

```bash
anyviking status --json
```

## Import Local Files

```bash
anyviking import-local ./path/to/corpus --to viking://resources/my-corpus
```

Show the resource tree:

```bash
anyviking tree viking://resources/my-corpus -L 2
```

## Search Public Web

```bash
anyviking search-web "query" --max-results 5
```

Useful filters:

```bash
anyviking search-web "query" --domain github.com --language en --freshness week
```

## Save Web Results Locally

```bash
anyviking fetch-web "query" --max-results 5 --output data/web/topic-name
```

This writes:

```text
data/web/topic-name/raw/anysearch_response.json
data/web/topic-name/markdown/*.md
data/web/topic-name/manifest.json
```

## Save And Import Into OpenViking

```bash
anyviking sync "query" --max-results 5 --output data/web/topic-name --to viking://resources/topic-name
```

This is the main command for the project.

## Search Indexed Data

```bash
anyviking search "question" --scope viking://resources/topic-name --top-k 5
```

Text output is easier for humans:

```bash
anyviking search "question" --scope viking://resources/topic-name --format text --documents-only
```
