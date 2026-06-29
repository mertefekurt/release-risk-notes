from __future__ import annotations

import json
import re
from collections import Counter

from release_risk_notes.models import Finding, ReleaseReport

RULES = (
    (
        "database",
        "high",
        re.compile(r"\b(migration|schema|backfill|alter table|drop column)\b", re.I),
        "Confirm migration rollback, lock time, and backward compatibility.",
    ),
    (
        "auth",
        "high",
        re.compile(r"\b(auth|oauth|sso|jwt|session|permission|role)\b", re.I),
        "Run login, logout, permission, and token-expiry smoke tests.",
    ),
    (
        "billing",
        "high",
        re.compile(r"\b(billing|invoice|payment|checkout|subscription|refund)\b", re.I),
        "Verify payment flows, invoice generation, and customer-facing amounts.",
    ),
    (
        "dependency",
        "medium",
        re.compile(r"\b(dependency|dependencies|requirements|package-lock|poetry.lock)\b", re.I),
        "Review lockfile changes and scan for vulnerable or breaking upgrades.",
    ),
    (
        "infrastructure",
        "medium",
        re.compile(r"\b(terraform|kubernetes|helm|docker|deployment|redis|queue)\b", re.I),
        "Check rollout plan, health probes, capacity, and rollback commands.",
    ),
    (
        "observability",
        "low",
        re.compile(r"\b(metric|log|trace|alert|dashboard|monitor)\b", re.I),
        "Confirm alerts and dashboards cover the changed path.",
    ),
)
SEVERITY_SCORE = {"low": 1, "medium": 3, "high": 5}
FAIL_LEVELS = {"low": 1, "medium": 5, "high": 10}


def analyze_release(text: str) -> ReleaseReport:
    findings: list[Finding] = []
    for area, severity, pattern, checklist in RULES:
        matches = sorted(set(match.group(0).lower() for match in pattern.finditer(text)))
        for signal in matches:
            findings.append(
                Finding(area=area, severity=severity, signal=signal, checklist=checklist)
            )

    changed_files = tuple(_extract_changed_files(text))
    findings.extend(_path_findings(changed_files))
    deduped = _dedupe_findings(findings)
    score = sum(SEVERITY_SCORE[finding.severity] for finding in deduped)
    return ReleaseReport(
        risk_level=_risk_level(score),
        score=score,
        findings=tuple(deduped),
        changed_files=changed_files,
    )


def report_to_markdown(report: ReleaseReport) -> str:
    lines = [
        "# release-risk-notes report",
        "",
        f"Risk level: **{report.risk_level}**",
        f"Risk score: `{report.score}`",
        "",
        "## Findings",
        "",
    ]
    if report.findings:
        for finding in report.findings:
            lines.append(
                f"- **{finding.severity}** `{finding.area}` via `{finding.signal}`: "
                f"{finding.checklist}"
            )
    else:
        lines.append("- no release-risk signals found")

    lines.extend(["", "## Changed files", ""])
    if report.changed_files:
        lines.extend(f"- `{path}`" for path in report.changed_files)
    else:
        lines.append("- no diff file paths detected")

    lines.extend(["", "## Reviewer checklist", ""])
    checklist = sorted({finding.checklist for finding in report.findings})
    if checklist:
        lines.extend(f"- [ ] {item}" for item in checklist)
    else:
        lines.append("- [ ] Run the normal release smoke test.")
    return "\n".join(lines) + "\n"


def report_to_json(report: ReleaseReport) -> str:
    return json.dumps(
        {
            "risk_level": report.risk_level,
            "score": report.score,
            "changed_files": list(report.changed_files),
            "findings": [finding.__dict__ for finding in report.findings],
        },
        indent=2,
    ) + "\n"


def should_fail(report: ReleaseReport, fail_on: str) -> bool:
    return report.score >= FAIL_LEVELS[fail_on]


def _extract_changed_files(text: str) -> list[str]:
    files: list[str] = []
    for line in text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                files.append(parts[3].removeprefix("b/"))
        elif line.startswith("+++ b/"):
            files.append(line.removeprefix("+++ b/").strip())
    return sorted(set(files))


def _path_findings(paths: tuple[str, ...]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        lowered = path.casefold()
        if "migration" in lowered or lowered.endswith(".sql"):
            findings.append(
                Finding(
                    "database",
                    "high",
                    path,
                    "Confirm migration rollback, lock time, and backward compatibility.",
                )
            )
        if "auth" in lowered or "permission" in lowered:
            findings.append(
                Finding(
                    "auth",
                    "high",
                    path,
                    "Run login, logout, permission, and token-expiry smoke tests.",
                )
            )
    return findings


def _dedupe_findings(findings: list[Finding]) -> list[Finding]:
    unique: dict[tuple[str, str, str], Finding] = {}
    for finding in findings:
        key = (finding.area, finding.severity, finding.signal)
        unique[key] = finding
    return sorted(unique.values(), key=lambda item: (item.area, item.severity, item.signal))


def _risk_level(score: int) -> str:
    if score >= 10:
        return "high"
    if score >= 5:
        return "medium"
    return "low"


def area_counts(report: ReleaseReport) -> Counter[str]:
    return Counter(finding.area for finding in report.findings)

