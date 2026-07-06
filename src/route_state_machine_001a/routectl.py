from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import validator


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))


def cmd_validate(args: argparse.Namespace) -> int:
    root = Path(args.root)
    report = validator.build_validation_report(root)
    output_path = validator.write_validation_report(root, report)
    payload = {
        "verdict": report["verdict"],
        "validation_error_count": len(report["validation_errors"]),
        "validation_warning_count": len(report["validation_warnings"]),
        "validation_report": str(output_path),
        "run_id": report["run_id"],
    }
    _print_json(payload)
    return 0 if report["verdict"] == "pass" else 1


def cmd_status(args: argparse.Namespace) -> int:
    status = validator.build_status(Path(args.root))
    lines = [
        f"task_id: {status['task_id']}",
        f"verdict: {status['verdict']}",
        f"route_count: {status['route_count']}",
        f"current_frontier_route_id: {status['current_frontier_route_id']}",
        f"program_state_verdict: {status['program_state_verdict']}",
        f"validation_errors: {status['validation_error_count']}",
        f"validation_warnings: {status['validation_warning_count']}",
        "routes:",
    ]
    for route in status["routes"]:
        lines.append(
            f"- {route['route_id']}: state={route['current_state']} closure={route['closure_type']} verdict={route['verdict']}"
        )
    lines.append(f"claim_ceiling: {status['claim_ceiling']}")
    print("\n".join(lines))
    return 0 if status["verdict"] == "pass" else 1


def cmd_dashboard(args: argparse.Namespace) -> int:
    dashboard = validator.build_dashboard(Path(args.root))
    _print_json(dashboard)
    return 0 if dashboard["verdict"] == "pass" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="routectl",
        description="ROUTE-STATE-MACHINE-001A local route-governance validator.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate route artifacts and write validation_report.json")
    validate_parser.add_argument("--root", default=".", help="repository root")
    validate_parser.set_defaults(func=cmd_validate)

    status_parser = subparsers.add_parser("status", help="print route status summary")
    status_parser.add_argument("--root", default=".", help="repository root")
    status_parser.set_defaults(func=cmd_status)

    dashboard_parser = subparsers.add_parser("dashboard", help="print machine-readable dashboard summary")
    dashboard_parser.add_argument("--root", default=".", help="repository root")
    dashboard_parser.set_defaults(func=cmd_dashboard)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
