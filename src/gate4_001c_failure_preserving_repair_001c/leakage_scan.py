from __future__ import annotations

import argparse
from pathlib import Path

from . import core


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    core.load_config(Path(args.config))
    bundle_path = Path(args.bundle)
    if not bundle_path.exists():
        raise SystemExit(f"missing bundle manifest: {bundle_path}")
    report, _ = core.build_leakage_report(core.repo_root())
    report["bundle_manifest"] = bundle_path.as_posix()
    core.write_json(Path(args.out), report)
    print(report["verdict"])


if __name__ == "__main__":
    main()
