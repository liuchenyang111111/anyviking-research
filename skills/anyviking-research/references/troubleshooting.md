# Troubleshooting

## `OpenViking health check failed`

Meaning:

- the OpenViking server is not running, or
- the server is listening on a different host or port.

Try:

```powershell
.\scripts\start_openviking.ps1
```

Then:

```powershell
ar health
```

## `ar.exe not found`

Meaning:

- the package is not installed in the active virtual environment.

Try:

```powershell
python -m pip install -e .[openviking] --no-build-isolation
```

## AnySearch request failed

Meaning:

- network access is unavailable, or
- the request was rejected, or
- an API key is needed for stable access.

Try:

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

Then rerun `ar search-web` or `ar sync`.

## Search returns no useful results

Try one or more of these:

- widen `--scope`
- increase `--top-k`
- remove overly narrow filters
- run `ar tree <scope>` to verify the corpus was imported
- use `--documents-only` when generated summaries are noisy
