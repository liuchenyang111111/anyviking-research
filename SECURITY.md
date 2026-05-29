# Security Policy

AnyViking Research is a local CLI tool. It can read local files, write local corpus files, and call external APIs.

## Do Not Commit

- `.env`
- `config/ov.conf`
- `config/ovcli.conf`
- API keys
- bearer tokens
- `data/`
- `reports/`
- `workspace/`
- generated corpus files

Only `.example` config files belong in the repository.

## Runtime Notes

- `anyviking search-web` calls AnySearch.
- `anyviking fetch-web` and `anyviking sync` can save public web snippets locally.
- `anyviking sync` and `anyviking import-local` send local files to the local OpenViking service for indexing.
- `anyviking search` reads indexed OpenViking results from a known `viking://` scope.

Review generated local files before sharing them.

## Reporting A Vulnerability

Do not open public issues for secrets, credential leakage, or path traversal problems. Report privately to the maintainer. If this repository is forked or transferred, update this file with the correct contact path.
