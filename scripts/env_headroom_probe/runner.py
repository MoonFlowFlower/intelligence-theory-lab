"""CLI for the Phase-A borrow-first environment headroom probe."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .adapters import ADAPTERS, record_digest
from .battery import run_battery, stable_digest
from .contract import build_prereg_contract

OFFICIAL_ENVS = {"POS_INTERNAL_ESTAR", "NEG_5A846D5_SCOUT"}


def _json_dump(data: Any) -> None:
    sys.stdout.write(json.dumps(data, indent=2, sort_keys=True) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["contract", "recompute"], default="contract")
    parser.add_argument("--env", default="UNIT_SYNTHETIC")
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--drop-graph-closure", action="store_true")
    parser.add_argument("--shuffle-o-y", action="store_true")
    parser.add_argument(
        "--phase-b-authorized",
        action="store_true",
        help="Required for registered controls/candidates; Phase A tests do not use it.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "contract":
        _json_dump(build_prereg_contract())
        return 0

    if args.env not in ADAPTERS:
        raise SystemExit(f"unknown env adapter: {args.env}")
    if args.env in OFFICIAL_ENVS and not args.phase_b_authorized:
        raise SystemExit(
            f"{args.env} is a registered control; official scoring requires --phase-b-authorized"
        )
    if args.env != "UNIT_SYNTHETIC" and not args.phase_b_authorized:
        raise SystemExit(
            "borrowed candidate/control recompute requires --phase-b-authorized after Claude Red-audit"
        )

    adapter = ADAPTERS[args.env]
    records = adapter.build_records(int(args.seed))
    battery = run_battery(
        records,
        seed=int(args.seed),
        include_graph_closure=not args.drop_graph_closure,
        shuffle_targets=bool(args.shuffle_o_y),
    )
    payload = {
        "producer_function": "runner.main",
        "mode": "recompute",
        "env": args.env,
        "adapter_source": adapter.source,
        "adapter_status": adapter.status,
        "record_digest": record_digest(records),
        "battery": battery,
    }
    payload["fresh_process_digest"] = stable_digest(payload)
    _json_dump(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
