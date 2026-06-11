import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser(prog="predictive_action_learning_contract_001c")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run-suite-external",
                       help="USER-SIDE: rerun frozen suite with RFC3161 anchoring (network)")
    p.add_argument("--suite-dir", required=True)
    p.add_argument("--tsa", action="append", default=None,
                   help="TSA URL (repeatable); default freetsa.org then digicert")
    p = sub.add_parser("verify-artifacts", help="OFFLINE: verify anchors + equality + gates")
    p.add_argument("--suite-dir", required=True)
    p.add_argument("--reference", default=None)
    p.add_argument("--tests-exit-code", type=int, required=True)
    p.add_argument("--tests-summary", default="")
    args = ap.parse_args()

    from . import driver
    if args.cmd == "run-suite-external":
        driver.run_suite_external(args.suite_dir, tsa_urls=args.tsa)
    else:
        ref = args.reference or driver.DEFAULT_REFERENCE
        res = driver.verify_artifacts(args.suite_dir, ref,
                                      args.tests_exit_code, args.tests_summary)
        print(json.dumps({k: res[k] for k in
                          ("implementation_verdict", "evidence_verdict",
                           "anchors_externally_valid", "anchors_signed_by_test_ca")},
                         indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
