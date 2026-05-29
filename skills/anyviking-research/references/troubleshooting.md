# Troubleshooting

## `anyviking` Is Not Found

The package may not be installed in the active environment.

Try:

```powershell
.\.venv\Scripts\anyviking.exe doctor
```

```bash
.venv/bin/anyviking doctor
```

Or reinstall:

```bash
python -m pip install -e '.[openviking]' --no-build-isolation
```

## OpenViking Is Not Running

Try:

```powershell
.\scripts\start_openviking.ps1
anyviking health
```

```bash
./scripts/start_openviking.sh
anyviking health
```

## AnySearch Request Failed

Possible causes:

- network access is blocked
- the API rejected the request
- an API key is needed for stable access
- filters are too narrow

Set a key if you have one:

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

```bash
export ANYSEARCH_API_KEY="your-key"
```

## Search Results Look Weak

Try:

- increase `--max-results` for web search
- increase `--top-k` for OpenViking search
- remove narrow filters
- check the imported scope with `anyviking tree`
- use `--documents-only` to avoid generated summaries
