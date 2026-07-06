# Release Risk Notes

![stack](https://img.shields.io/badge/stack-Python-7c3aed?style=flat-square) ![python](https://img.shields.io/badge/python-3.11-0891b2?style=flat-square) ![license](https://img.shields.io/badge/license-MIT-b45309?style=flat-square) ![ci](https://img.shields.io/badge/ci-GitHub%20Actions-be185d?style=flat-square)

![Release Risk Notes cover](assets/readme-cover.svg)

Generate release risk notes and checklists from changelog or diff text.

## Use case

- quick local checks around release planning
- small CI jobs where a readable report is enough
- review workflows that need deterministic output
- examples based on `examples/release.txt`

## Local setup

```bash
git clone https://github.com/mertefekurt/release-risk-notes.git
cd release-risk-notes
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## CLI

```bash
release-risk-notes examples/release.txt
```

## Quality check

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
python -m release_risk_notes --help
```
