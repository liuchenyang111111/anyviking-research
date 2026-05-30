# Troubleshooting

## Quick Checks

Run this first:

```bash
anyviking doctor
```

If the command is not on `PATH`, use the virtual-environment executable:

```powershell
.\.venv\Scripts\anyviking.exe doctor
```

```bash
.venv/bin/anyviking doctor
```

## `anyviking` Is Not Found

Likely causes:

- The package was not installed.
- The virtual environment is not active.
- You installed an older version that still used the old `ar` command.

Fix:

```bash
python -m pip install -e '.[openviking]' --no-build-isolation
```

On Windows:

```powershell
python -m pip install -e .[openviking] --no-build-isolation
```

## OpenViking Package Or `ov` Is Missing

Install with the OpenViking extra:

```bash
python -m pip install -e '.[openviking]' --no-build-isolation
```

Then run:

```bash
anyviking doctor
```

## OpenViking Service Is Not Running

Start it:

```powershell
.\scripts\start_openviking.ps1
```

```bash
./scripts/start_openviking.sh
```

Then check:

```bash
anyviking health
```

## OpenViking Config Is Missing

Create local config files from templates:

```powershell
Copy-Item config\ov.conf.example config\ov.conf
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

```bash
cp config/ov.conf.example config/ov.conf
cp config/ovcli.conf.example config/ovcli.conf
```

Edit `config/ov.conf` and add your model-provider settings.

## AnySearch Request Failed

Common causes:

- Network access is blocked.
- Anonymous AnySearch requests are rate-limited.
- `ANYSEARCH_API_KEY` is missing or invalid.
- `ANYSEARCH_API_URL` points to the wrong endpoint.
- Filters such as `--domain`, `--language`, or `--freshness` are too narrow.

Set a key if you have one:

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

```bash
export ANYSEARCH_API_KEY="your-key"
```

Then test with a small request:

```bash
anyviking search-web "OpenViking GitHub" --max-results 3
```

If you use a custom AnySearch endpoint, verify that `ANYSEARCH_API_URL` is correct.

## Import Succeeded But Search Finds Nothing

Check the imported scope:

```bash
anyviking tree viking://resources/your-topic -L 2
```

Search with a larger result count:

```bash
anyviking search "question" --scope viking://resources/your-topic --top-k 10 --format text --documents-only
```

If this still fails, confirm that the markdown files were written under `data/` before import.

## Linux/macOS Script Permission Error

Run with `bash`:

```bash
bash ./install.sh
bash ./scripts/start_openviking.sh
```

Or make scripts executable:

```bash
chmod +x install.sh scripts/start_openviking.sh scripts/stop_openviking.sh
```

## PyPI Publishing Fails

Publishing requires one of these:

- PyPI/TestPyPI Trusted Publishing configured for this repository.
- A valid API token provided through the publishing environment.

Build locally first:

```bash
python -m build
python -m twine check dist/*
```

If local build and `twine check` pass, the remaining issue is usually publishing permissions or package-name ownership.
