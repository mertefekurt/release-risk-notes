import json

from release_risk_notes.analyzer import analyze_release, area_counts, report_to_markdown
from release_risk_notes.cli import main


def test_detects_database_and_billing_risk() -> None:
    report = analyze_release("Added checkout migration and invoice retry behavior.")

    areas = area_counts(report)
    assert areas["database"] >= 1
    assert areas["billing"] >= 1
    assert report.risk_level == "high"


def test_extracts_changed_files_from_diff() -> None:
    report = analyze_release(
        "diff --git a/app/auth/session.py b/app/auth/session.py\n"
        "+++ b/app/auth/session.py\n"
        "+ changed jwt behavior\n"
    )

    assert "app/auth/session.py" in report.changed_files
    assert any(finding.area == "auth" for finding in report.findings)


def test_markdown_contains_checklist() -> None:
    markdown = report_to_markdown(analyze_release("Updated OAuth session permissions."))

    assert "Reviewer checklist" in markdown
    assert "Run login, logout" in markdown


def test_low_risk_when_no_signals() -> None:
    report = analyze_release("Changed button copy on the settings page.")

    assert report.risk_level == "low"
    assert report.score == 0


def test_cli_outputs_json_and_exit_code(tmp_path, capsys) -> None:
    path = tmp_path / "release.txt"
    path.write_text("Database migration for billing invoices.", encoding="utf-8")

    exit_code = main([str(path), "--format", "json", "--fail-on", "medium"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 2
    assert payload["risk_level"] == "high"

