from __future__ import annotations

import argparse
import json
from pathlib import Path

from .verifier import verify_bundle


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify synthetic Gate evidence-bundle provenance shape."
    )
    parser.add_argument("bundle_dir", help="Evidence-bundle directory to verify.")
    args = parser.parse_args()

    print(json.dumps(verify_bundle(Path(args.bundle_dir)), sort_keys=True))


if __name__ == "__main__":
    main()
