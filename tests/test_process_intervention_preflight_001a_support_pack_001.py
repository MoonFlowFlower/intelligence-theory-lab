import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from negative_evidence_admission_gate_001a import evaluate_successor_task

TASK_CARD = (
    ROOT
    / "docs"
    / "codex"
    / "tasks"
    / "PROCESS-INTERVENTION-PREFLIGHT-001A-AMENDMENT-001-SUPPORT-PACK-001.md"
)
SUPPORT_PACK_DIR = (
    ROOT / "artifacts" / "process_intervention_preflight_001a_amendment_001_support_pack_001"
)
RERUN_DIR = (
    ROOT
    / "artifacts"
    / "process_intervention_preflight_001a_amendment_001_semantic_audit_rerun_001"
)

SUPPORT_CONTRACTS = [
    "amendment_001.md",
    "real_control_implementation_contract.md",
    "trace_commitment_contract.md",
    "match_metric_contract.md",
    "update_path_contract.md",
    "separation_statistic_contract.md",
    "state_accounting_contract.md",
    "resource_budget_contract.md",
    "environment_intervention_instantiation_contract.md",
    "memory_key_fidelity_contract.md",
    "behavior_probe_contract.md",
    "stage0_freeze_anchor_contract.md",
]

SUPPORT_PACK_ARTIFACTS = [
    "support_pack_result.json",
    "support_pack_matrix.json",
    "support_pack_gate_status.json",
    "support_pack_manifest.json",
    "claim_ceiling.txt",
]

RERUN_ARTIFACTS = [
    "semantic_audit_result.json",
    "semantic_audit_matrix.json",
    "false_pass_channel_findings.jsonl",
    "source_citation_map.json",
    "final_report.md",
    "claim_ceiling.txt",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(_read_text(path))


def test_support_pack_task_card_exists_and_locks_stop_rule():
    assert TASK_CARD.exists()
    text = _read_text(TASK_CARD)
    gate = evaluate_successor_task(text)
    assert gate["passed"] is True
    assert gate["failure_ids"] == []

    for phrase in [
        "PROCESS-INTERVENTION-PREFLIGHT-001A-AMENDMENT-001-SUPPORT-PACK-001",
        "executable-readiness support pack",
        "representational_gap_001b_failed_count_or_statistic_control_solved",
        "Fable / poisoning line = frozen",
        "negative evidence guard = sufficient",
        "semantic audit rerun count = one",
        "semantic_audit_blocked_missing_amendment_support_artifacts",
        "process_intervention_preflight_001a_framing_too_heavy_pivot_to_smaller_from_scratch_preflight",
        "do not continue patching contracts",
        "mechanism_implementation_authorized = false",
        "old_experiments_rerun = false",
    ]:
        assert phrase in text


def test_support_pack_reuses_existing_contract_sources_and_covers_13_categories():
    contract_root = ROOT / "docs" / "process_intervention_preflight_001a"
    for file_name in SUPPORT_CONTRACTS:
        assert (contract_root / file_name).exists(), file_name

    for artifact in SUPPORT_PACK_ARTIFACTS:
        assert (SUPPORT_PACK_DIR / artifact).exists(), artifact

    result = _read_json(SUPPORT_PACK_DIR / "support_pack_result.json")
    matrix = _read_json(SUPPORT_PACK_DIR / "support_pack_matrix.json")
    gate_status = _read_json(SUPPORT_PACK_DIR / "support_pack_gate_status.json")
    manifest = _read_json(SUPPORT_PACK_DIR / "support_pack_manifest.json")

    assert result["task_id"] == "PROCESS-INTERVENTION-PREFLIGHT-001A-AMENDMENT-001-SUPPORT-PACK-001"
    assert result["verdict"] == "support_pack_001_ready_for_single_semantic_audit_rerun"
    assert result["mechanism_evidence_claimed"] is False
    assert result["old_experiments_rerun"] is False
    assert result["fable_or_poisoning_line_expanded"] is False
    assert result["contract_source_policy"] == "reuse_existing_sources_no_duplicate_contract_tree"

    categories = {row["category_id"] for row in matrix["rows"]}
    assert categories == {f"A{i}" for i in range(1, 12)} | {
        "A12_AMENDMENT_ARTIFACTS",
        "A13_CONTRACT_TEST",
    }
    assert all(row["status"] == "present" for row in matrix["rows"])
    assert gate_status["missing_support_artifacts_blocker"] == "closed_for_rerun"
    assert gate_status["remaining_blocking_findings"] == []
    assert manifest["duplicates_contract_sources"] is False
    assert manifest["old_semantic_audit_preserved"] is True


def test_single_semantic_audit_rerun_records_pass_without_overwriting_old_audit():
    old_audit = (
        ROOT
        / "artifacts"
        / "process_intervention_preflight_001a_amendment_001_independent_semantic_audit"
        / "semantic_audit_result.json"
    )
    assert old_audit.exists()
    old_result = _read_json(old_audit)
    assert old_result["verdict"] == "semantic_audit_blocked_missing_amendment_support_artifacts"

    for artifact in RERUN_ARTIFACTS:
        assert (RERUN_DIR / artifact).exists(), artifact

    result = _read_json(RERUN_DIR / "semantic_audit_result.json")
    matrix = _read_json(RERUN_DIR / "semantic_audit_matrix.json")
    citations = _read_json(RERUN_DIR / "source_citation_map.json")
    report = _read_text(RERUN_DIR / "final_report.md")

    assert result["verdict"] == "semantic_audit_pass_support_pack_executable_readiness_only"
    assert result["semantic_pass"] is True
    assert result["missing_support_artifacts_blocker"] is False
    assert result["old_audit_overwritten"] is False
    assert result["mechanism_evidence_claimed"] is False
    assert result["next_allowed_task_if_any"] == (
        "PROCESS-INTERVENTION-PREFLIGHT-001B executable preflight authorization/execution path"
    )
    assert set(matrix["amendment_checks"]) == {f"A{i}" for i in range(1, 12)}
    assert matrix["support_pack_categories_present"] == 13
    assert citations["support_pack_task_card"] == str(TASK_CARD.relative_to(ROOT)).replace("\\", "/")
    assert "not mechanism evidence" in report
    assert "single semantic audit rerun" in report


def test_no_extra_semantic_audit_chain_or_forbidden_paths_created():
    rerun_dirs = sorted(
        path.name
        for path in (ROOT / "artifacts").glob(
            "process_intervention_preflight_001a_amendment_001_semantic_audit_rerun_*"
        )
        if path.is_dir()
    )
    assert rerun_dirs == ["process_intervention_preflight_001a_amendment_001_semantic_audit_rerun_001"]

    forbidden_paths = [
        "src/process_intervention_preflight_001a",
        "src/process_intervention_mechanism",
        "docs/codex/tasks/FABLE6-DATA-INTEGRITY-PREFLIGHT-001.md",
        "docs/codex/tasks/MODEL-POISONING-AUDIT-001B.md",
    ]
    for relative_path in forbidden_paths:
        assert not (ROOT / relative_path).exists(), relative_path


def test_support_pack_claim_ceiling_rejects_lexical_or_mechanism_overclaim():
    joined = "\n".join(
        [
            _read_text(TASK_CARD),
            _read_text(SUPPORT_PACK_DIR / "claim_ceiling.txt"),
            _read_text(RERUN_DIR / "claim_ceiling.txt"),
            _read_text(RERUN_DIR / "final_report.md"),
        ]
    )

    for phrase in [
        "lexical gate pass is not mechanism evidence",
        "not mechanism evidence",
        "not executable preflight success",
        "not EGO readiness",
        "not companion readiness",
        "not consciousness evidence",
    ]:
        assert phrase in joined

    forbidden_overclaims = [
        "proves mechanism success",
        "proves Fable causality",
        "authorizes EGO integration",
        "authorizes model-class reset",
    ]
    for phrase in forbidden_overclaims:
        assert phrase not in joined
