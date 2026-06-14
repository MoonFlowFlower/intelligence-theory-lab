import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "artifacts" / "anti_lookup_generative_heldout_surface_protocol_001a_anchor_status_reconciliation_001a"
REPORT = ROOT / "docs" / "research" / "ANTI-LOOKUP-GENERATIVE-HELDOUT-SURFACE-PROTOCOL-001A-ANCHOR-STATUS-RECONCILIATION-001A.md"
ORIGINAL_REPORT = ROOT / "docs" / "research" / "ANTI-LOOKUP-GENERATIVE-HELDOUT-SURFACE-PROTOCOL-001A.md"
ORIGINAL_RESULT = ROOT / "artifacts" / "anti_lookup_generative_heldout_surface_protocol_001a" / "result.json"
TARGET_HASH = "cebb7812924dc6d00767308597886995e437ea2a"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_anchor_status_reconciliation_preserves_original_false_field_and_records_exact_hashes():
    readback = _load(TASK_DIR / "readback.json")
    result = _load(TASK_DIR / "result.json")
    original_result = _load(ORIGINAL_RESULT)
    original_report_text = ORIGINAL_REPORT.read_text(encoding="utf-8")

    assert "- Remote anchor performed: `False`" in original_report_text
    assert original_result["remote_anchor_performed"] is False
    assert readback["original_001a_result_remote_anchor_performed"] is False
    assert result["remote_anchor_performed_by_original_001a_report"] is False
    assert result["original_001a_remote_anchor_performed_false_preserved_as_historical_state"] is True
    assert result["original_001a_artifacts_rewritten"] is False

    assert readback["local_head"] == TARGET_HASH
    assert readback["remote_branch_hash"] == TARGET_HASH
    assert readback["local_tag_hash"] == TARGET_HASH
    assert readback["remote_tag_hash"] == TARGET_HASH
    assert readback["tag_type"] == "commit"
    assert readback["ahead_behind"] == "0\t0"
    assert readback["exact_match"] is True
    assert readback["final_clean_worktree"] is True
    assert result["exact_match"] is True
    assert result["anchor_status_reconciled"] is True
    assert result["protocol_boundary_anchored_after_original_report_generated"] is True


def test_report_and_result_keep_reconciliation_claim_ceiling_and_forbidden_paths_closed():
    report_text = REPORT.read_text(encoding="utf-8")
    result = _load(TASK_DIR / "result.json")

    assert "remote-anchor status reconciliation only" in report_text
    assert "historical/stale report state" in report_text
    assert "Current canonical anchor status" in report_text
    assert "does not prove mechanism validity" in report_text

    assert result["verdict"] == (
        "anti_lookup_generative_heldout_surface_protocol_001a_anchor_status_reconciliation_001a_pass"
    )
    assert result["stop_conditions_triggered"] == []
    assert result["candidate_code_created"] is False
    assert result["candidate_score_produced"] is False
    assert result["tournament_execution_attempted"] is False
    assert result["gate4_replacement_design_created"] is False
    assert result["gate4_repair_or_rerun_attempted"] is False
    assert result["runtime_or_mainline_path_created"] is False
    assert result["llm_rag_ui_companion_path_created"] is False
