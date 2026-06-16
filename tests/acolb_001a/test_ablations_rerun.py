from acolb_001a.ablations import run_ablations


def test_ablations_rerun_with_distinct_code_paths(tmp_path):
    report = run_ablations(output_dir=tmp_path)

    assert {row["ablation_id"] for row in report["ablations"]} == {"A1", "A2", "A3", "A4", "A5", "A6"}
    candidate_hash = report["candidate_code_path_hash"]
    for row in report["ablations"]:
        assert row["rerun"] is True
        assert row["code_path_hash"] != candidate_hash


def test_load_bearing_ablations_collapse_toward_floor(tmp_path):
    report = run_ablations(output_dir=tmp_path)
    by_id = {row["ablation_id"]: row for row in report["ablations"]}

    for ablation_id in ("A1", "A3", "A4"):
        assert by_id[ablation_id]["direction_ok"] is True
        assert by_id[ablation_id]["ood_score"] <= report["no_update_floor_score"] + 0.05
    assert by_id["A2"]["direction_ok"] is True
