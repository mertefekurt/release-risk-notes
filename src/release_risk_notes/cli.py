from __future__ import annotations

import argparse
import sys
from pathlib import Path

from release_risk_notes import __version__
from release_risk_notes.analyzer import (
    analyze_release,
    report_to_json,
    report_to_markdown,
    should_fail,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="release-risk-notes",
        description="Generate release risk notes from a changelog, PR summary, or git diff file.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="text file containing release notes or diff",
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--fail-on", choices=("low", "medium", "high"), default="high")
    parser.add_argument("--out", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.input is None:
        parser.print_help()
        return 0
    try:
        report = analyze_release(args.input.read_text(encoding="utf-8"))
        output = report_to_json(report) if args.format == "json" else report_to_markdown(report)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
    except OSError as exc:
        print(f"release-risk-notes: error: {exc}", file=sys.stderr)
        return 1
    return 2 if should_fail(report, args.fail_on) else 0
