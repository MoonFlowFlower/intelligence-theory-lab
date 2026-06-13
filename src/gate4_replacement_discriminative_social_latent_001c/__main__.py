from __future__ import annotations

import argparse
import json

from .core import ARTIFACT_DIR, execute_bounded_run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    run = execute_bounded_run(output_dir=args.output_dir or ARTIFACT_DIR, persist_artifacts=True)
    print(json.dumps(run["result"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
