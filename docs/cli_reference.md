# CLI Reference

The command is `ar`.

If your virtual environment is not active, use:

```powershell
.\.venv\Scripts\ar.exe doctor
```

## Check Environment

```powershell
ar doctor
```

Use JSON output when another tool or Agent needs to parse the result:

```powershell
ar doctor --json
```

## OpenViking Service

```powershell
ar health
```

```powershell
ar status
```

```powershell
ar status --json
```

## Import Local Files

```powershell
ar import-local .\path\to\corpus --to viking://resources/my-corpus
```

Show the resource tree:

```powershell
ar tree viking://resources/my-corpus -L 2
```

## Search Public Web

```powershell
ar search-web "query" --max-results 5
```

Useful filters:

```powershell
ar search-web "query" --domain github.com --language en --freshness week
```

## Save Web Results Locally

```powershell
ar fetch-web "query" --max-results 5 --output data\web\topic-name
```

This writes:

```text
data\web\topic-name\raw\anysearch_response.json
data\web\topic-name\markdown\*.md
data\web\topic-name\manifest.json
```

## Save And Import Into OpenViking

```powershell
ar sync "query" --max-results 5 --output data\web\topic-name --to viking://resources/topic-name
```

This is the main command for the project.

## Search Indexed Data

```powershell
ar search "question" --scope viking://resources/topic-name --top-k 5
```

Text output is easier for humans:

```powershell
ar search "question" --scope viking://resources/topic-name --format text --documents-only
```
