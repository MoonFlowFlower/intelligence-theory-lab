from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import verify_bundle, write_admission_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify standalone evidence-admission bundles from callable provenance."
    )
    parser.add_argument("bundle_path", help="Directory containing JSON/JSONL evidence bundle files.")
    parser.add_argument(
        "--out",
        required=True,
        help="Directory where verifier artifacts will be written.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional stable run id for reproducible tests/readbacks.",
    )
    args = parser.parse_args()

    decision = verify_bundle(Path(args.bundle_path), run_id=args.run_id)
    command = [
        "python",
        "-m",
        "evidence_admission_verifier_001a",
        args.bundle_path,
        "--out",
        args.out,
    ]
    if args.run_id is not None:
        command.extend(["--run-id", args.run_id])
    decision["verifier_command"] = " ".join(command)
    write_admission_artifacts(decision, Path(args.out))
    print(json.dumps({"canonical_decision": decision["canonical_decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
