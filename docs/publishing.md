# Publishing

This project uses source distributions and wheels built by `python -m build`.

Publishing is intentionally manual. The repository owner should publish to TestPyPI first, then publish the same version to PyPI from a version tag.

References:

- PyPI Trusted Publishing: https://docs.pypi.org/trusted-publishers/
- GitHub Action: https://github.com/pypa/gh-action-pypi-publish

## 1. Local Build Check

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

## 2. Configure Trusted Publishing

Create publishers on both TestPyPI and PyPI:

```text
Owner: liuchenyang111111
Repository: anyviking-research
Workflow: publish.yml
Environment for TestPyPI: testpypi
Environment for PyPI: pypi
```

Use the environments named in `.github/workflows/publish.yml`.

## 3. Publish To TestPyPI

Run the `publish` workflow manually with:

```text
target = testpypi
branch = main
```

Then test installation in a clean environment:

```bash
python -m venv .venv-testpypi
source .venv-testpypi/bin/activate
python -m pip install --upgrade pip
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ 'anyviking-research[openviking]'
anyviking --help
```

Windows uses:

```powershell
py -3.12 -m venv .venv-testpypi
.\.venv-testpypi\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ anyviking-research[openviking]
anyviking --help
```

## 4. Publish To PyPI

Create and push a version tag:

```bash
git tag v0.6.0
git push origin v0.6.0
```

Run the `publish` workflow manually from that tag with:

```text
target = pypi
ref = v0.6.0
```

The workflow refuses official PyPI publishing from a normal branch.

## 5. After Publishing

Verify the package:

```bash
python -m venv .venv-pypi-check
source .venv-pypi-check/bin/activate
python -m pip install --upgrade pip
python -m pip install 'anyviking-research[openviking]'
anyviking --help
```

Then update README install instructions if you want PyPI to become the recommended path.
