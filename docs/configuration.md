# Configuration

The repository only keeps example config files.

Real config files stay local:

```text
config/ov.conf
config/ovcli.conf
.env
```

## OpenViking

Copy the templates:

```powershell
Copy-Item config\ov.conf.example config\ov.conf
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

Edit `config\ov.conf` and set your own model provider credentials.

The important fields are:

```text
server.host
server.port
storage.workspace
embedding.*
vlm.*
```

`storage.workspace` is where OpenViking keeps its local database and indexes.

## AnySearch

AnySearch may work without a key, but a key is better for stable use:

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

The connector reads this value from the environment.

## Local Output

These folders are runtime output and are ignored by Git:

```text
data/
reports/
workspace/
```

`data/` stores fetched web material before import.

`workspace/` is OpenViking's local storage.

`reports/` is only for generated local output if a command writes there.
