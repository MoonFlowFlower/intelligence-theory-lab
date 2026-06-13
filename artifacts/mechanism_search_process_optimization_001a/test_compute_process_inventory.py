import json
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
SCRIPT = ARTIFACT_DIR / "compute_process_inventory.py"
INVENTORY = ARTIFACT_DIR / "reviewed_task_inventory.json"
METRICS = ARTIFACT_DIR / "process_inventory_metrics.json"


def run_analyzer(*extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *extra_args],
        cwd=ARTIFACT_DIR,
        text=True,
        capture_output=True,
    )


def test_analyzer_generates_metrics_from_inventory():
    result = run_analyzer()
    assert result.returncode == 0, result.stderr
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    assert metrics["producer_function"] == "compute_process_inventory"
    assert metrics["input_path"].endswith("reviewed_task_inventory.json")
    assert metrics["invalid_fixture_failed_as_expected"] is True
    assert sum(metrics["category_counts"].values()) == len(inventory)
    assert metrics["downstream_decision_changed_count"] == sum(
        1 for row in inventory if row["downstream_decision_changed"]
    )
    assert metrics["cheap_baseline_issue_count"] == sum(
        1 for row in inventory if row["cheap_baseline_issue_present"]
    )
    assert metrics["same_family_repair_risk_count"] == sum(
        1 for row in inventory if row["same_family_repair_risk"]
    )


def test_analyzer_rejects_invalid_fixture_explicitly():
    result = run_analyzer("--validate-invalid-fixture-only")
    assert result.returncode != 0
    assert "invalid fixture rejected as expected" in result.stderr
