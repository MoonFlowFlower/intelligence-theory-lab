from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import core


def validate_artifact_dir(artifact_dir: Path) -> dict[str, Any]:
    parsed = []
    for path in sorted(artifact_dir.glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
        parsed.append(path.name)
    for path in sorted(artifact_dir.glob("*.jsonl")):
        line_count = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                json.loads(line)
                line_count += 1
        parsed.append(f"{path.name}:{line_count}")
    return {
        "task_id": core.TASK_ID,
        "artifact_dir": artifact_dir.as_posix(),
        "parse_status": "all_json_and_jsonl_parsed",
        "parsed": parsed,
        "parser": "json.loads",
        "claim_ceiling": core.CLAIM_CEILING,
        "non_evidence_statement": "JSON parsing verifies syntax only; it does not prove Gate4 or mechanism validity.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", required=True)
    args = parser.parse_args()
    artifact_dir = Path(args.artifact_dir)
    report = validate_artifact_dir(artifact_dir)
    core.write_json(artifact_dir / "json_parse_verification.json", report)
    print(report["parse_status"])


if __name__ == "__main__":
    main()
