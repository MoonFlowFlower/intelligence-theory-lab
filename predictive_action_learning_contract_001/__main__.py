"""CLI for the bounded experiment. Documented in the suite README."""

import argparse
import json
import os
import sys


def main():
    ap = argparse.ArgumentParser(prog="predictive_action_learning_contract_001")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("--suite-dir", required=True)

    p = sub.add_parser("run")
    p.add_argument("--suite-dir", required=True)
    p.add_argument("--group", required=True,
                   choices=["core", "baselines", "ablations", "protocol", "perturbations"])

    p = sub.add_parser("run-single")
    p.add_argument("--suite-dir", required=True)
    p.add_argument("--spec-json", required=True)

    p = sub.add_parser("duplicates")
    p.add_argument("--suite-dir", required=True)

    p = sub.add_parser("finalize")
    p.add_argument("--suite-dir", required=True)
    p.add_argument("--tests-exit-code", type=int, required=True)
    p.add_argument("--tests-summary", default="")

    args = ap.parse_args()

    from . import suite as S
    from . import reporting as R

    if args.cmd == "init":
        S.write_config_artifact(args.suite_dir)
        R.write_readme(args.suite_dir)
        print(f"initialized {args.suite_dir}")
    elif args.cmd == "run":
        done = S.run_group(args.suite_dir, args.group)
        print(f"group {args.group}: {len(done)} runs: {done}")
    elif args.cmd == "run-single":
        rid = S.run_single_spec(args.suite_dir, args.spec_json)
        print(f"ran {rid}")
    elif args.cmd == "duplicates":
        ids = S.run_duplicates(args.suite_dir, os.getcwd())
        print(f"duplicates: {ids}")
    elif args.cmd == "finalize":
        res = R.finalize(args.suite_dir,
                         {"exit_code": args.tests_exit_code,
                          "summary": args.tests_summary})
        v = res["verdicts"]
        print(json.dumps({
            "implementation_verdict": v["implementation_verdict"],
            "evidence_verdict": v["evidence_verdict"],
            "failed_gates": v["failed_gates"],
            "stop_conditions_triggered": v["stop_conditions_triggered"],
        }, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
