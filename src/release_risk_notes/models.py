from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    area: str
    severity: str
    signal: str
    checklist: str


@dataclass(frozen=True)
class ReleaseReport:
    risk_level: str
    score: int
    findings: tuple[Finding, ...]
    changed_files: tuple[str, ...]

