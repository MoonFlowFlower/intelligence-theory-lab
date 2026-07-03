import json
from pathlib import Path

from src.fsp_pum_env.s3b_artifacts import write_materialized_leak_scan_report
from src.fsp_pum_env.trajectory_sets import (
    TrajectorySetSpec,
    load_frozen_design,
    write_trajectory_set_recipe,
)


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def test_materialized_leak_scan_regenerates_and_scans_recipe_records(tmp_path):
    design = load_frozen_design(FROZEN)
    spec = TrajectorySetSpec(
        set_id="unit_set",
        master_seed=design["population_and_data"]["env_master_seeds"][0],
        env_mode="base",
        partitions={"heldout": {"start_user_id": design["population_and_data"]["N_train_users"], "count": 1}},
        turns_per_user=3,
        logging_policy=design["population_and_data"]["log_parity_trajectory_policy"],
    )
    entry = write_trajectory_set_recipe(design, spec, tmp_path / "trajectory_sets", raw_size_limit_bytes=1)
    manifest_path = tmp_path / "s3a_trajectory_set_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
                "sets": [entry],
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report_path = tmp_path / "s3b_leak_scan_report.json"
    report = write_materialized_leak_scan_report(FROZEN, manifest_path, report_path)

    assert report["artifact"] == "s3b_leak_scan_report"
    assert report["passed"] is True
    assert report["scanned_files"] == []
    assert report["known_limitation"].startswith("Scanner is key/type-based")
    assert report["sets"] == [
        {
            "set_id": "unit_set",
            "records_scanned": entry["member_view_record_count"],
            "member_view_record_count": entry["member_view_record_count"],
            "expected_member_view_sha256": entry["member_view_sha256"],
            "regenerated_member_view_sha256": entry["member_view_sha256"],
            "sha256_verified": True,
            "findings": [],
        }
    ]
    assert json.loads(report_path.read_text(encoding="utf-8")) == report


def test_materialized_leak_scan_preserves_failure_artifact_on_sha_mismatch(tmp_path):
    design = load_frozen_design(FROZEN)
    spec = TrajectorySetSpec(
        set_id="bad_set",
        master_seed=design["population_and_data"]["env_master_seeds"][0],
        env_mode="base",
        partitions={"heldout": {"start_user_id": design["population_and_data"]["N_train_users"], "count": 1}},
        turns_per_user=2,
        logging_policy=design["population_and_data"]["log_parity_trajectory_policy"],
    )
    entry = write_trajectory_set_recipe(design, spec, tmp_path / "trajectory_sets", raw_size_limit_bytes=1)
    entry["member_view_sha256"] = "0" * 64
    manifest_path = tmp_path / "s3a_trajectory_set_manifest.json"
    manifest_path.write_text(json.dumps({"sets": [entry]}, sort_keys=True) + "\n", encoding="utf-8")
    report_path = tmp_path / "s3b_leak_scan_report.json"

    report = write_materialized_leak_scan_report(FROZEN, manifest_path, report_path)

    assert report["passed"] is False
    assert report["stop_condition"] == "member_view_sha256_mismatch"
    assert report["sets"][0]["sha256_verified"] is False
    assert report_path.exists()


def test_materialized_leak_scan_uses_canonical_train_then_heldout_partition_order(tmp_path):
    design = load_frozen_design(FROZEN)
    spec = TrajectorySetSpec(
        set_id="ordered_set",
        master_seed=design["population_and_data"]["env_master_seeds"][0],
        env_mode="base",
        partitions={
            "train": {"start_user_id": 0, "count": 1},
            "heldout": {"start_user_id": design["population_and_data"]["N_train_users"], "count": 1},
        },
        turns_per_user=2,
        logging_policy=design["population_and_data"]["log_parity_trajectory_policy"],
    )
    entry = write_trajectory_set_recipe(design, spec, tmp_path / "trajectory_sets", raw_size_limit_bytes=1)
    manifest_path = tmp_path / "s3a_trajectory_set_manifest.json"
    manifest_path.write_text(json.dumps({"sets": [entry]}, sort_keys=True) + "\n", encoding="utf-8")

    report = write_materialized_leak_scan_report(FROZEN, manifest_path, tmp_path / "report.json")

    assert report["passed"] is True
    assert report["sets"][0]["sha256_verified"] is True
    assert report["sets"][0]["records_scanned"] == 4
