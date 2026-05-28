# Open Source Readiness

This document tracks the difference between a working demo and a maintainable open-source project.

## Already Present

- Python package under `src/anyviking_research`.
- CLI command `ar`.
- AnySearch connector.
- OpenViking retriever and import wrapper.
- Fetch and research workflows.
- Unit tests that do not require live services.
- CI workflow for tests and compile checks.
- Example corpora and PowerShell scripts.
- Runtime directories ignored by git.

## Added For Project Completeness

- `ar doctor` environment diagnostics.
- CLI reference documentation.
- Configuration documentation.
- Development guide.
- Contributing guide.
- Security policy.
- Package metadata, classifiers, optional dependencies, and typed package marker.
- Issue and pull request templates.

## Still Future Work

These are not required for the current CLI-first open-source foundation, but they would improve maturity:

- Real GitHub repository URLs in `pyproject.toml` after publishing location is known.
- More Linux/macOS smoke verification.
- Optional Docker Compose for OpenViking server.
- More robust live AnySearch integration tests gated behind an environment variable.
- Optional MCP adapter.
- Optional Web UI.
- Optional LLM synthesis layer with provider-agnostic configuration.

## Definition Of Done For This Stage

The project should be considered ready as an alpha open-source toolkit when:

- A new user can read the README and understand the purpose.
- A new user can install the package and run `ar doctor`.
- A developer can find CLI, configuration, and development docs.
- Tests pass without requiring OpenViking or AnySearch live services.
- A live local smoke test can demonstrate AnySearch -> OpenViking -> research when credentials and services are available.
