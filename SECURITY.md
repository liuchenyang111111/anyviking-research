# Security Policy

AnyViking Research is a local workflow tool that can read local files, write local corpus data, and call external APIs. Treat configuration and generated artifacts carefully.

## Supported Versions

Security fixes are currently made on the main development line while the project is in alpha.

## Reporting A Vulnerability

Please do not open public issues for secrets, credential leakage, or path traversal problems. Report privately to the project maintainer. If this repository is forked or transferred, update this file with the correct private contact path.

Include:

- A short description of the issue.
- Reproduction steps.
- Affected command or module.
- Whether credentials, local files, or generated reports may be exposed.

## Secret Handling

Never commit:

- `config/ov.conf`
- `config/ovcli.conf`
- `.env`
- API keys or bearer tokens
- generated `data/`, `workspace/`, or `reports/` contents

The repository includes `.example` config files only.

## Runtime Safety

- `ar fetch-web` and `ar sync` may store public web snippets locally.
- `ar import-local` sends local files to the local OpenViking service for indexing.
- `ar research` writes generated drafts under `reports/` by default.
- Review generated reports before sharing them, because they may contain source snippets.
