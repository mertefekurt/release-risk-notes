# Release Risk Notes

| Field | Value |
| --- | --- |
| Category | incident practice |
| Command | `release-risk-notes` |
| Inputs | `examples/release.txt` |

Generate release risk notes and checklists from changelog or diff text. The idea is simple: give Release Risk Notes the local file or fixture, get a readable result, and decide what needs attention before the next handoff.

## Cover

![Release Risk Notes cover](assets/readme-cover.svg)

## Run path

```bash
git clone https://github.com/mertefekurt/release-risk-notes.git
cd release-risk-notes
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
release-risk-notes examples/release.txt
```

## Repository notes

```text
.github/        CI workflow
examples/       sample inputs
src/            package source
tests/          test coverage
.gitignore      project file
pyproject.toml  package metadata
```
