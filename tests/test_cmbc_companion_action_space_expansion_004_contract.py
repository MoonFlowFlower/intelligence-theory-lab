import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "CMBC_COMPANION_ACTION_SPACE_EXPANSION_004_CONTRACT.md"
ARTIFACT_DIR = ROOT / "artifacts" / "cmbc_companion_action_space_expansion_004_contract"
MANIFEST = ARTIFACT_DIR / "contract_manifest.json"
CONTRACT = ARTIFACT_DIR / "action_space_expansion_004_contract.json"
STATUS = ARTIFACT_DIR / "CONTRACT_STATUS.md"
BOUNDARY_SCAN = ARTIFACT_DIR / "boundary_scan_report.md"


def test_action_space_expansion_004_contract_files_exist():
    assert DOC.exists()
    assert MANIFEST.exists()
    assert CONTRACT.exists()
    assert STATUS.exists()
    assert BOUNDARY_SCAN.exists()


def test_action_space_expansion_004_is_contract_only_and_lab_only():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["contract_id"] == "CMBC-COMPANION-ACTION-SPACE-EXPANSION-004-CONTRACT"
    assert manifest["verdict"] == "action_space_expansion_004_contract_ready"
    assert manifest["authorized_scope"] == "contract_only"
    assert manifest["execution_authorized"] is False
    assert manifest["implementation_authorized"] is False
    assert manifest["selector_patch_authorized"] is False
    assert manifest["threshold_change_authorized"] is False
    assert manifest["rag_baseline_weakening_authorized"] is False
    assert manifest["ego_migration"] == "no_go"
    assert manifest["real_companion_implementation"] == "not_authorized"
    assert manifest["proactive_messages"] == "not_authorized"
    assert manifest["llm_action_selection"] is False


def test_action_space_expansion_004_declares_expanded_anonymous_action_space_gates():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    gates = contract["minimum_future_execution_gates"]

    assert gates["candidate_action_count_min"] == 20
    assert gates["semantic_label_visible_to_selector"] is False
    assert gates["rendered_text_visible_to_selector"] is False
    assert gates["action_distribution_entropy_reported"] is True
    assert gates["dominant_action_rate_reported"] is True
    assert gates["label_permutation_change_rate"] == 0.0
    assert gates["effect_swap_change_rate_min"] == 0.8
    assert gates["rag_causal_probe_match_rate_max"] == 0.5
    assert gates["strong_heuristic_causal_probe_match_rate_max"] == 0.5
    assert gates["expanded_contextual_heuristic_causal_probe_match_rate_max"] == 0.5
    assert gates["behavior_only_replay_match_rate"] == 1.0
    assert gates["renderer_action_change_rate"] == 0.0


def test_action_space_expansion_004_preserves_required_probe_and_baseline_coverage():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert set(contract["required_probe_types"]) == {
        "label_permutation_invariance",
        "effect_perturbation_sensitivity",
        "same_text_different_causal_history",
        "supporting_prior_deletion",
        "outcome_perturbation",
        "feedback_admission_single_contradiction",
        "feedback_admission_repeated_feedback",
        "renderer_adversarial_isolation",
        "behavior_only_replay",
        "baseline_comparison",
    }
    assert contract["required_baselines"] == [
        "RAGSummaryMemoryBaseline",
        "StrongHumanLikeHeuristicBaseline",
        "ExpandedContextualHeuristicBaseline",
        "ExpandedActionFrequencyBaseline",
        "ExpandedActionNearestNeighborBaseline",
    ]


def test_action_space_expansion_004_forbids_label_shortcuts_and_product_claims():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    forbidden = set(contract["forbidden"])

    assert "semantic action labels exposed to selector" in forbidden
    assert "rendered text exposed to selector" in forbidden
    assert "LLM action selection" in forbidden
    assert "EGO integration" in forbidden
    assert "real companion implementation" in forbidden
    assert "real proactive messages" in forbidden
    assert "selector patch to pass" in forbidden
    assert "threshold change after seeing results" in forbidden
    assert "RAG baseline weakening" in forbidden
    assert contract["claim_ceiling"] == (
        "bounded action-space expansion contract readiness only; no execution evidence"
    )
