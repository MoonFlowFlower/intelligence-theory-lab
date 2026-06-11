import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "process_intervention_hard_distribution_001a"
TASK_CARD = ROOT / "docs" / "codex" / "tasks" / "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001A.md"


REQUIRED_ARTIFACTS = {
    "hard_distribution_spec.json",
    "frozen_inputs.json",
    "distribution_shortcut_audit.json",
    "fair_control_budget_spec.json",
    "heldout_composition_manifest.json",
    "ablation_hook_manifest.json",
    "claim_ceiling.txt",
}

REQUIRED_FAIR_CONTROLS = {
    "online_count_statistic",
    "count_table",
    "graph_cache",
    "transition_table",
    "successor_map",
    "trace_only_replay",
    "behavior_only_replay",
    "summary_retrieval",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _case_key(case: dict) -> tuple[str, str, str]:
    return (
        case["observable_context"],
        case["intervention_condition"],
        case["action"],
    )


def test_required_hard_distribution_artifacts_exist_and_parse():
    assert TASK_CARD.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})

    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        parsed = _read_json(ARTIFACT_DIR / name)
        assert parsed["task_id"] == "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001A"

    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == (
        "bounded process-intervention hard-distribution readiness only"
    )


def test_distribution_breaks_context_intervention_action_shortcut():
    spec = _read_json(ARTIFACT_DIR / "hard_distribution_spec.json")
    audit = _read_json(ARTIFACT_DIR / "distribution_shortcut_audit.json")
    cases = spec["case_families"]

    outcomes_by_key: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    future_by_actual: dict[str, set[str]] = defaultdict(set)
    for case in cases:
        outcomes_by_key[_case_key(case)].add(case["outcome"])
        future_by_actual[case["actual_observation"]].add(case["future_behavior"])

    conflicting_keys = {key: values for key, values in outcomes_by_key.items() if len(values) > 1}
    ambiguous_actuals = {actual: values for actual, values in future_by_actual.items() if len(values) > 1}

    assert conflicting_keys
    assert ambiguous_actuals
    assert audit["context_intervention_action_uniquely_determines_outcome"] is False
    assert audit["deterministic_key_conflict_count"] == len(conflicting_keys)
    assert audit["future_behavior_directly_recoverable_from_actual_observation"] is False
    assert audit["scale_increased_without_structural_shortcut_removal"] is False


def test_distribution_contains_delays_partial_observability_and_counterfactual_pairs():
    spec = _read_json(ARTIFACT_DIR / "hard_distribution_spec.json")
    cases = spec["case_families"]

    assert any(case["delay_steps"] > 0 for case in cases)
    assert any(case["partial_observability"]["hidden_state_visible"] is False for case in cases)
    assert any(case["ambiguity_profile"]["immediate_observation_sufficient"] is False for case in cases)

    pairs = spec["counterfactual_action_pairs"]
    assert pairs
    for pair in pairs:
        assert pair["shared_observation_history"]
        assert len({branch["action"] for branch in pair["branches"]}) >= 2
        assert len({branch["required_belief_update"] for branch in pair["branches"]}) >= 2


def test_heldout_split_and_ablation_hooks_are_predeclared():
    heldout = _read_json(ARTIFACT_DIR / "heldout_composition_manifest.json")
    ablation = _read_json(ARTIFACT_DIR / "ablation_hook_manifest.json")

    support = {tuple(item) for item in heldout["support_intervention_compositions"]}
    heldout_items = {tuple(item) for item in heldout["heldout_intervention_compositions"]}

    assert support
    assert heldout_items
    assert support.isdisjoint(heldout_items)
    assert heldout["heldout_split_frozen_before_execution"] is True
    assert heldout["heldout_split_missing"] is False

    hooks = {hook["hook_id"]: hook for hook in ablation["ablation_hooks"]}
    assert "learning_freeze" in hooks
    assert "history_replacement" in hooks
    assert all(hook["predeclared"] is True for hook in hooks.values())
    assert all(hook["executes_in_this_task"] is False for hook in hooks.values())


def test_fair_controls_are_preserved_with_predeclared_budget_and_access():
    budget = _read_json(ARTIFACT_DIR / "fair_control_budget_spec.json")
    controls = {control["control_name"]: control for control in budget["fair_controls"]}

    assert REQUIRED_FAIR_CONTROLS.issubset(set(controls))
    assert budget["fair_controls_weakened_or_removed"] is False
    assert budget["thresholds_changed_to_force_pass"] is False
    for control_name in REQUIRED_FAIR_CONTROLS:
        control = controls[control_name]
        assert control["predeclared"] is True
        assert control["resource_budget_within_fair_access"] is True
        assert control["access_rules"]["may_use_observable_context"] is True
        assert control["access_rules"]["may_use_intervention_condition"] is True
        assert control["access_rules"]["may_use_action"] is True
        assert control["access_rules"]["may_use_future_outcomes"] is False
        assert control["access_rules"]["may_use_hidden_state_labels"] is False


def test_frozen_inputs_authorize_nothing_and_old_inputs_are_unchanged():
    frozen = _read_json(ARTIFACT_DIR / "frozen_inputs.json")

    assert frozen["freeze_before_any_execution"] is True
    assert frozen["execution_authorized"] is False
    assert frozen["old_001b_artifacts_edited"] is False
    assert all(value is False for value in frozen["authorization_flags"].values())

    for relative_path, expected_hash in frozen["frozen_input_sha256"].items():
        assert _sha256(ROOT / relative_path) == expected_hash


def test_acceptance_gate_status_and_claim_ceiling_are_bounded():
    spec = _read_json(ARTIFACT_DIR / "hard_distribution_spec.json")
    audit = _read_json(ARTIFACT_DIR / "distribution_shortcut_audit.json")
    frozen = _read_json(ARTIFACT_DIR / "frozen_inputs.json")

    assert spec["claim_ceiling"] == "bounded process-intervention hard-distribution readiness only"
    assert audit["acceptance_gate_status"]["deterministic_key_conflict_audit_confirms_shortcut_breaking_conflicts"] is True
    assert audit["acceptance_gate_status"]["heldout_intervention_composition_split_exists"] is True
    assert audit["acceptance_gate_status"]["delayed_effect_cases_exist"] is True
    assert audit["acceptance_gate_status"]["partial_observability_cases_exist"] is True
    assert audit["acceptance_gate_status"]["authorization_flags_all_false"] is True
    assert frozen["what_this_does_not_prove"] == [
        "mechanism validity",
        "theory validity",
        "theory falsity",
        "Gate1 readiness",
        "bridge readiness",
        "EGO readiness",
        "agency",
        "consciousness",
        "companion readiness",
        "model-class reset necessity",
    ]
