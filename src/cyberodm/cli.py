from __future__ import annotations
import argparse
from pathlib import Path
from .compute import compute
from .report import build as build_report

def main():
    parser = argparse.ArgumentParser(prog="cyberodm", description="Outcome-Driven Metrics for Cybersecurity")
    sub = parser.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("compute", help="Compute ODM scores, value, and OKR progress")
    s1.add_argument("--config", default="config.yml", help="Path to config.yml")

    s2 = sub.add_parser("report", help="Generate charts and executive ODM report")

    args = parser.parse_args()
    base = Path(".").resolve()

    if args.cmd == "compute":
        compute(base)
        print("Wrote:", base / "outputs" / "outcome_scores.csv")
        print("Wrote:", base / "outputs" / "okr_progress.csv")
        print("Wrote:", base / "outputs" / "value_realization.csv")
    elif args.cmd == "report":
        build_report(base)
        print("Wrote:", base / "outputs" / "report.md")
