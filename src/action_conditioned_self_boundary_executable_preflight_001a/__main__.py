from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runner import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REPORT_PATH,
    execute_preflight,
    refresh_materialized_readbacks,
    write_research_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001A"
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    args = parser.parse_args()

    run = execute_preflight(
        repo_root=Path(args.repo_root),
        output_dir=Path(args.output_dir),
        persist_artifacts=True,
    )
    report_path = write_research_report(run, Path(args.report_path))
    refresh_materialized_readbacks(Path(args.repo_root), Path(args.output_dir))
    print(
        json.dumps(
            {
                "verdict": run["result"]["verdict"],
                "artifact_dir": str(Path(args.output_dir)),
                "report_path": str(report_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
