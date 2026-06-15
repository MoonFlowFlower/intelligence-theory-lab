import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gate1_failed_graph_cache_reconciliation_001a.runner import (  # noqa: E402
    ARTIFACT_DIR_REL,
    CLAIM_CEILING,
    SELECTED_ITEM,
    run_reconciliation,
)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_queue_selects_only_gate1_graph_cache_reconciliation(tmp_path):
    result = run_reconciliation(repo_root=ROOT, output_dir=tmp_path)

    assert result["task_id"] == "GATE1-FAILED-GRAPH-CACHE-RECONCILIATION-001A"
    assert result["queue_id"] == "POST-FREEZE-GATE0-3-SEQUENTIAL-REPAIR-QUEUE-001A"
    assert result["max_queue_items_per_run"] == 1
    assert result["selected_items"] == [SELECTED_ITEM]
    assert result["selected_item_count"] == 1
    assert result["verdict"] == "gate1_failed_graph_cache_reconciliation_001a_preserve_failed_graph_cache_collapse"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["artifact_dir"] == ARTIFACT_DIR_REL
    assert result["current_layer"] == "engineering implementation / evidence-governance only"
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "no enabled path"
    assert result["downstream_authorization"] == {
        "gate1_pass": False,
        "gate3": False,
        "integrated_testbed": False,
        "gate4": False,
        "bridge": False,
        "admission": False,
        "runtime": False,
        "ego_mainline": False,
    }

    selected = _read_json(tmp_path / "selected_item.json")
    assert selected["selected_item"] == SELECTED_ITEM
    assert selected["not_selected_items"] == [
        "Gate3 baseline/ablation repair",
        "integrated Gate0-Gate3 testbed repair",
        "Gate4 work",
        "bridge/admission/runtime work",
        "unrelated files",
    ]


def test_reconciliation_preserves_failed_graph_cache_collapse_when_controls_match(tmp_path):
    run_reconciliation(repo_root=ROOT, output_dir=tmp_path)

    reconciliation = _read_json(tmp_path / "lineage_reconciliation.json")

    assert reconciliation["prior_lineage_result"]["package_verdict"] == "gate1_preflight_failed_graph_cache_collapse"
    assert reconciliation["prior_lineage_closeout"]["parent_gate1_package_verdict"] == "failed_graph_cache_collapse"
    assert reconciliation["gate1_001c_literal_pass_not_upgraded"] is True
    assert reconciliation["fair_controls_match_or_beat_candidate"] is True
    assert reconciliation["closure_preserved"] is True
    assert reconciliation["positive_gate1_inheritance_allowed"] is False
    assert set(reconciliation["graph_cache_family_controls_verified"]) >= {
        "count_table",
        "graph_lookup",
        "successor_map",
        "transition_table",
    }
    assert set(reconciliation["window_cache_controls_verified"]) >= {
        "hidden_state_cache",
        "prefix_cache",
        "longer_context_retrieval",
        "sequence_lookup",
        "nn_sequence",
    }
    assert reconciliation["source_artifact_hashes"]["prior_result_json"]
    assert reconciliation["source_artifact_hashes"]["prior_baseline_comparison_json"]
    assert reconciliation["code_path_hashes"]["gate1_preflight_runner_py"]
    assert reconciliation["code_path_hashes"]["gate1_preflight_core_py"]


def test_baseline_and_ablation_reports_are_computed_from_prior_callable_lineage(tmp_path):
    run_reconciliation(repo_root=ROOT, output_dir=tmp_path)

    baseline = _read_json(tmp_path / "baseline_comparison.json")
    ablation = _read_json(tmp_path / "ablation_report.json")

    assert baseline["producer_function"] == "build_baseline_reconciliation"
    assert baseline["prior_artifact"] == "artifacts/gate1_replay_consolidation_exec_taskcard_001/baseline_comparison.json"
    assert baseline["candidate_A_graph_cache_collapse_detected"] is True
    assert set(baseline["candidate_A_matched_by_graph_cache_family"]) >= {
        "graph_lookup",
        "transition_table",
        "successor_map",
        "count_table",
    }
    assert baseline["candidate_B_window_cache_controls_executed"] is True
    assert baseline["fair_control_match_blocks_positive_gate1_claim"] is True

    assert ablation["producer_function"] == "build_ablation_reconciliation"
    assert ablation["prior_artifact"] == "artifacts/gate1_replay_consolidation_exec_taskcard_001/ablation_report.json"
    assert ablation["all_required_ablation_variants_have_completed_ledger_runs"] is True
    assert ablation["real_ablation_rerun_evidence_verified"] is True
    assert set(ablation["verified_ablation_variant_prefixes"]) >= {
        "A_cand_salience_pe",
        "A_cand_reverse",
        "B_cand_salience_pe",
        "B_cand_reverse",
        "B_ctrl_shuffled_replay_B",
    }
    for record in ablation["ablation_variant_ledger_evidence"]:
        assert record["completed_for_all_seeds"] is True
        assert record["producer_function"] == "run_ledger_completed_run_id_check"
        assert record["seeds"] == [11, 13, 17, 19, 23]


def test_generated_artifact_set_and_claim_ceiling(tmp_path):
    result = run_reconciliation(repo_root=ROOT, output_dir=tmp_path)

    required = {
        "selected_item.json",
        "lineage_reconciliation.json",
        "baseline_comparison.json",
        "ablation_report.json",
        "result.json",
        "readback.json",
        "claim_ceiling.txt",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert _read_json(tmp_path / "result.json") == result
    assert _read_json(tmp_path / "readback.json")["artifact_files"] == sorted(required)
