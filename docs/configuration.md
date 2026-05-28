# Configuration

AnyViking Research uses two kinds of configuration:

- OpenViking server and CLI configuration files under `config/`.
- Environment variables for optional upstream services such as AnySearch.

## OpenViking Server Config

Copy the example file:

```powershell
Copy-Item config\ov.conf.example config\ov.conf
```

Edit `config\ov.conf` and set your model provider credentials.

The important fields are:

```text
server.host      local server host, usually 127.0.0.1
server.port      local server port, usually 1933
storage.workspace local OpenViking workspace directory
embedding.*      embedding provider settings
vlm.*            VLM/provider settings used by OpenViking
```

`config\ov.conf` is ignored by git because it can contain API keys.

## OpenViking CLI Config

Copy the example file:

```powershell
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

The default points at:

```text
http://127.0.0.1:1933
```

Most project commands use `ar`, which finds the OpenViking executable and calls it for import/tree/status operations.

## AnySearch API Key

AnySearch may allow anonymous requests, but for stable usage set:

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

The key is read by `AnySearchConnector`. It is not written to output files.

## Local Runtime Directories

These paths are intentionally ignored by git:

```text
data/       web search output and manifests
reports/    generated research reports
workspace/  OpenViking local workspace
```

## Health Check

Run:

```powershell
ar doctor
```

Then start OpenViking if needed:

```powershell
.\scripts\start_openviking.ps1
```

Check service health:

```powershell
ar health
```
