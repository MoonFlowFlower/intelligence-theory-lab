import json
from pathlib import Path


ARTIFACT_DIR = Path("artifacts/cmbc_companion_free_input_causal_probe_pack_003b")
TRANSCRIPT_PATH = Path(
    "artifacts/cmbc_companion_free_input_live_lab_003_execute/user_supplied_free_input_2026-06-07.jsonl"
)

REQUIRED_FILES = {
    "FREE_INPUT_CAUSAL_PROBE_PACK_003B_STATUS.md",
    "causal_probe_pack_003B.json",
    "causal_probe_pack_003B.md",
    "probe_anchor_audit.json",
    "probe_type_coverage_report.json",
    "probe_predeclaration_manifest.json",
    "boundary_scan_report.md",
}

REQUIRED_PROBE_TYPES = {
    "same_text_different_causal_history",
    "same_history_different_feedback_outcome",
    "supporting_prior_deletion",
    "predicted_outcome_perturbation",
    "feedback_admission_single_contradiction",
    "feedback_admission_repeated_feedback",
    "later_correction_context_narrowing",
    "renderer_adversarial_isolation",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_transcript_by_turn_id() -> dict[str, dict]:
    rows = {}
    with TRANSCRIPT_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                row = json.loads(line)
                rows[row["turn_id"]] = row
    return rows


def test_causal_probe_pack_003b_writes_required_artifacts():
    assert REQUIRED_FILES.issubset({path.name for path in ARTIFACT_DIR.iterdir()})


def test_causal_probe_pack_003b_covers_required_probe_types_and_counts():
    pack = load_json(ARTIFACT_DIR / "causal_probe_pack_003B.json")
    probe_types = {probe["probe_type"] for probe in pack["probes"]}

    assert pack["verdict"] == "causal_probe_pack_ready_for_003_reexecute"
    assert pack["causal_probe_case_count"] >= 8
    assert len(pack["probes"]) == pack["causal_probe_case_count"]
    assert REQUIRED_PROBE_TYPES.issubset(probe_types)
    assert set(pack["missing_required_probe_types"]) == set()


def test_causal_probe_pack_003b_anchors_every_probe_to_existing_human_turn():
    pack = load_json(ARTIFACT_DIR / "causal_probe_pack_003B.json")
    transcript_by_turn_id = load_transcript_by_turn_id()

    for probe in pack["probes"]:
        anchor_turn = probe["anchor_turn"]
        assert anchor_turn in transcript_by_turn_id
        assert probe["anchor_user_text"] == transcript_by_turn_id[anchor_turn]["free_input_text"]
        assert probe["source_anchor_is_existing_human_turn"] is True
        assert probe["new_user_turn_counted_as_free_input"] is False
        assert probe["post_result_selected"] is False


def test_causal_probe_pack_003b_boundary_flags_are_locked():
    pack = load_json(ARTIFACT_DIR / "causal_probe_pack_003B.json")
    manifest = load_json(ARTIFACT_DIR / "probe_predeclaration_manifest.json")

    for doc in (pack, manifest):
        assert doc["execution_authorized"] is False
        assert doc["implementation_authorized"] is False
        assert doc["selector_patched"] is False
        assert doc["thresholds_changed"] is False
        assert doc["rag_baseline_weakened"] is False
        assert doc["ego_migration"] == "no_go"
        assert doc["real_companion_implementation"] == "not_authorized"
        assert doc["proactive_messages"] == "not_authorized"
        assert doc["llm_action_selection"] is False


def test_causal_probe_pack_003b_audit_and_coverage_reports_match_pack():
    pack = load_json(ARTIFACT_DIR / "causal_probe_pack_003B.json")
    anchor_audit = load_json(ARTIFACT_DIR / "probe_anchor_audit.json")
    coverage = load_json(ARTIFACT_DIR / "probe_type_coverage_report.json")

    assert anchor_audit["all_anchors_valid"] is True
    assert anchor_audit["synthetic_user_turn_counted_as_free_input"] is False
    assert anchor_audit["invalid_anchor_turns"] == []
    assert coverage["all_required_probe_types_covered"] is True
    assert coverage["missing_required_probe_types"] == []
    assert coverage["causal_probe_case_count"] == pack["causal_probe_case_count"]
