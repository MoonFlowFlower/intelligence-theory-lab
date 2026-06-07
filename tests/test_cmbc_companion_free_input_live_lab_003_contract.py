import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "CMBC_COMPANION_FREE_INPUT_LIVE_LAB_003_CONTRACT.md"
ARTIFACT_DIR = ROOT / "artifacts" / "cmbc_companion_free_input_live_lab_003_contract"
MANIFEST = ARTIFACT_DIR / "contract_manifest.json"
CONTRACT = ARTIFACT_DIR / "free_input_live_lab_003_contract.json"
STATUS = ARTIFACT_DIR / "CONTRACT_STATUS.md"


def test_free_input_live_lab_003_contract_files_exist():
    assert DOC.exists()
    assert MANIFEST.exists()
    assert CONTRACT.exists()
    assert STATUS.exists()


def test_contract_is_contract_only_and_lab_only():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["contract_id"] == "CMBC-COMPANION-FREE-INPUT-LIVE-LAB-003-CONTRACT"
    assert manifest["verdict"] == "free_input_live_lab_003_contract_ready"
    assert manifest["authorized_scope"] == "contract_only"
    assert manifest["execution_authorized"] is False
    assert manifest["implementation_authorized"] is False
    assert manifest["ego_migration"] == "no_go"
    assert manifest["real_companion_implementation"] == "not_authorized"
    assert manifest["proactive_messages"] == "not_authorized"
    assert manifest["llm_action_selection"] is False
    assert manifest["selector_patch_authorized"] is False
    assert manifest["threshold_change_authorized"] is False
    assert manifest["rag_baseline_weakening_authorized"] is False


def test_contract_requires_free_input_and_causal_probe_evidence():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert contract["minimum_execution_gates"]["free_input_turn_count_min"] == 20
    assert contract["minimum_execution_gates"]["causal_probe_case_count_min"] == 8
    assert contract["minimum_execution_gates"]["rag_causal_probe_match_rate_max"] == 0.5
    assert contract["minimum_execution_gates"]["strong_heuristic_causal_probe_match_rate_max"] == 0.5
    assert contract["minimum_execution_gates"]["renderer_action_change_rate"] == 0.0
    assert contract["minimum_execution_gates"]["behavior_only_replay_match_rate"] == 1.0
    assert contract["must_report_metrics"] == [
        "free_input_turn_count",
        "causal_probe_case_count",
        "rag_visible_action_match_rate",
        "rag_causal_probe_match_rate",
        "strong_heuristic_causal_probe_match_rate",
        "expanded_contextual_heuristic_causal_probe_match_rate",
        "renderer_action_change_rate",
        "behavior_only_replay_match_rate",
        "supporting_prior_deletion_effect",
        "outcome_perturbation_effect",
    ]


def test_contract_forbids_surface_or_product_claim_upgrade():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    forbidden = set(contract["forbidden"])

    assert "EGO integration" in forbidden
    assert "real companion agent" in forbidden
    assert "real proactive messages" in forbidden
    assert "LLM action selection" in forbidden
    assert "selector patch to pass" in forbidden
    assert "RAG baseline weakening" in forbidden
    assert "threshold change after seeing results" in forbidden
    assert "real companion readiness claim" in forbidden
    assert contract["claim_ceiling"] == (
        "bounded free-input offline/live-lab contract readiness only; no execution evidence"
    )
