#!/usr/bin/env python3
"""Artifact-local validator for MECHANISM-FAMILY-TOURNAMENT-ENTRY-CRITERIA-001A."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "MECHANISM-FAMILY-TOURNAMENT-ENTRY-CRITERIA-001A"
ARTIFACT_DIR = Path(__file__).resolve().parent
RESULT_PATH = ARTIFACT_DIR / "tournament_entry_validation_results.json"

INPUT_FILES = {
    "candidate_family_registry": "candidate_family_registry.json",
    "shared_tournament_preflight_protocol": "shared_tournament_preflight_protocol.json",
    "family_baseline_matrix": "family_baseline_matrix.json",
    "family_ablation_matrix": "family_ablation_matrix.json",
    "family_transfer_counterfactual_matrix": "family_transfer_counterfactual_matrix.json",
    "closed_family_inheritance": "closed_family_inheritance.json",
    "tournament_entry_validation_rules": "tournament_entry_validation_rules.json",
    "malformed_positive_control_fixture": "malformed_positive_control_fixture.json"
}

REQUIRED_FAMILY_IDS = {
    "causal_world_model_control",
    "jepa_like_latent_prediction",
    "replay_consolidation_adaptation",
    "self_boundary_controllability_model",
    "viability_value_gated_prediction_action_loop",
    "social_latent_inference_without_partner_id_lookup"
}

ALLOWED_MECHANISM_LAYERS = {
    "causal_world_model_control",
    "latent_prediction_world_model",
    "replay_consolidation",
    "self_boundary_controllability",
    "viability_value_prediction_action",
    "social_latent_inference"
}

REQUIRED_FAMILY_FIELDS = [
    "family_id",
    "mechanism_layer",
    "bounded_mechanism_hypothesis",
    "intended_observable",
    "minimum_environment_requirements",
    "target_source_requirement",
    "strongest_cheap_baseline",
    "required_independent_baselines",
    "required_ablation",
    "leakage_risks",
    "shortcut_risks",
    "minimum_transfer_condition",
    "required_counterfactuals",
    "trace_requirements",
    "replay_requirements_if_applicable",
    "why_not_lookup_profile_table_shortcut",
    "entry_preflight_requirements",
    "exit_conditions",
    "claim_ceiling",
    "forbidden_interpretations"
]

REQUIRED_PROTOCOL_FIELDS = [
    "process_mode",
    "candidate_code_allowed_before_preflight",
    "required_baseline_classes",
    "required_leakage_positive_controls",
    "required_target_provenance_fields",
    "required_transfer_splits",
    "required_counterfactual_splits",
    "required_threshold_lock",
    "required_config_hash_lock",
    "required_source_pin",
    "required_code_path_hash",
    "family_kill_rule",
    "same_family_repair_policy",
    "admission_claim_forbidden",
    "mainline_claim_forbidden"
]

REQUIRED_TARGET_PROVENANCE_FIELDS = {
    "producer_function",
    "input_artifacts",
    "run_id",
    "seed_context_episode_ids",
    "aggregation_rule",
    "code_path_hash"
}

REQUIRED_RULE_IDS = {
    "fewer_than_three_candidate_families",
    "missing_strongest_cheap_baseline",
    "missing_ablation",
    "missing_transfer_condition",
    "missing_leakage_risk",
    "missing_target_provenance",
    "social_family_without_partner_id_lookup_baseline",
    "target_recoverable_from_static_label_formula",
    "candidate_code_before_baseline_preflight",
    "admission_or_readiness_claim_in_discovery_mode",
    "reopening_closed_family_without_new_problem_definition_and_stronger_baseline_separation"
}

SOCIAL_REQUIRED_BASELINES = {
    "partner_id_lookup",
    "anonymized_partner_key_lookup",
    "preference_table_reconstruction",
    "prior_trace_retrieval",
    "order_k_partner_history",
    "full_bundle_decoder"
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def current_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ARTIFACT_DIR.parents[1],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unavailable"


def as_nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0 and all(item not in ("", None) for item in value)


def validate_payload(
    registry: dict[str, Any],
    protocol: dict[str, Any],
    baseline_matrix: list[dict[str, Any]],
    ablation_matrix: list[dict[str, Any]],
    transfer_matrix: list[dict[str, Any]],
    closed_inheritance: dict[str, Any],
    rules: dict[str, Any]
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []

    if registry.get("task_id") != TASK_ID:
        errors.append("registry_task_id_mismatch")
    if registry.get("process_mode") != "discovery_mode":
        errors.append("registry_process_mode_not_discovery")
    if registry.get("candidate_code_authorized") is not False:
        errors.append("registry_candidate_code_authorized")
    if registry.get("gate4_replacement_design_authorized") is not False:
        errors.append("registry_gate4_design_authorized")
    if registry.get("winner_declared") is not False:
        errors.append("registry_declares_winner")
    if registry.get("preferred_family_declared") is not False:
        errors.append("registry_declares_preferred_family")

    families = registry.get("families")
    if not isinstance(families, list):
        errors.append("families_not_list")
        families = []
    if len(families) < 3:
        errors.append("fewer_than_three_candidate_families")

    family_ids: set[str] = set()
    for family in families:
        if not isinstance(family, dict):
            errors.append("family_not_object")
            continue
        family_id = family.get("family_id")
        if not isinstance(family_id, str) or not family_id:
            errors.append("family_missing_family_id")
            continue
        if family_id in family_ids:
            errors.append(f"duplicate_family_id:{family_id}")
        family_ids.add(family_id)

        for field in REQUIRED_FAMILY_FIELDS:
            if field not in family:
                errors.append(f"family_missing_field:{family_id}:{field}")

        if family.get("mechanism_layer") not in ALLOWED_MECHANISM_LAYERS:
            errors.append(f"family_invalid_mechanism_layer:{family_id}")
        for field in [
            "minimum_environment_requirements",
            "strongest_cheap_baseline",
            "required_independent_baselines",
            "required_ablation",
            "leakage_risks",
            "shortcut_risks",
            "minimum_transfer_condition",
            "required_counterfactuals",
            "trace_requirements",
            "entry_preflight_requirements",
            "exit_conditions",
            "forbidden_interpretations"
        ]:
            if field in family and not as_nonempty_list(family.get(field)):
                errors.append(f"family_empty_list:{family_id}:{field}")
        if not isinstance(family.get("claim_ceiling"), str) or "Gate4 readiness" not in family.get("claim_ceiling", ""):
            errors.append(f"family_claim_ceiling_missing_gate4_bound:{family_id}")

    missing_required_families = sorted(REQUIRED_FAMILY_IDS - family_ids)
    if missing_required_families:
        errors.append("missing_required_families:" + ",".join(missing_required_families))

    for field in REQUIRED_PROTOCOL_FIELDS:
        if field not in protocol:
            errors.append(f"protocol_missing_field:{field}")
    if protocol.get("process_mode") != "discovery_mode":
        errors.append("protocol_process_mode_not_discovery")
    if protocol.get("candidate_code_allowed_before_preflight") is not False:
        errors.append("protocol_allows_candidate_code_before_preflight")
    if protocol.get("admission_claim_forbidden") is not True:
        errors.append("protocol_admission_claim_not_forbidden")
    if protocol.get("mainline_claim_forbidden") is not True:
        errors.append("protocol_mainline_claim_not_forbidden")
    if protocol.get("readiness_claim_forbidden") is not True:
        errors.append("protocol_readiness_claim_not_forbidden")
    provenance_fields = set(protocol.get("required_target_provenance_fields", []))
    if not REQUIRED_TARGET_PROVENANCE_FIELDS.issubset(provenance_fields):
        errors.append("protocol_missing_target_provenance_fields")
    allowed_baseline_classes = set(protocol.get("required_baseline_classes", []))

    baseline_family_ids: set[str] = set()
    social_baselines: set[str] = set()
    for row in baseline_matrix if isinstance(baseline_matrix, list) else []:
        family_id = row.get("family_id")
        baseline_family_ids.add(family_id)
        if row.get("baseline_class") not in allowed_baseline_classes:
            errors.append(f"baseline_invalid_class:{family_id}:{row.get('baseline_id')}")
        if row.get("callable_required_in_future_preflight") is not True:
            errors.append(f"baseline_not_callable_required:{family_id}:{row.get('baseline_id')}")
        for field in [
            "family_id",
            "baseline_id",
            "baseline_class",
            "why_strong",
            "expected_shortcut_detected",
            "threshold_role",
            "failure_interpretation"
        ]:
            if not row.get(field):
                errors.append(f"baseline_missing_field:{family_id}:{field}")
        if family_id == "social_latent_inference_without_partner_id_lookup":
            social_baselines.add(row.get("baseline_id"))
    for family_id in family_ids:
        if family_id not in baseline_family_ids:
            errors.append(f"family_missing_baseline_matrix_row:{family_id}")
    if not SOCIAL_REQUIRED_BASELINES.issubset(social_baselines):
        errors.append("social_family_missing_required_shortcut_baselines")

    ablation_family_ids: set[str] = set()
    for row in ablation_matrix if isinstance(ablation_matrix, list) else []:
        family_id = row.get("family_id")
        ablation_family_ids.add(family_id)
        if row.get("callable_required_in_future_execution") is not True:
            errors.append(f"ablation_not_callable_required:{family_id}:{row.get('ablation_id')}")
        for field in [
            "family_id",
            "ablation_id",
            "ablated_component",
            "what_failure_would_mean",
            "what_success_would_not_prove"
        ]:
            if not row.get(field):
                errors.append(f"ablation_missing_field:{family_id}:{field}")
    for family_id in family_ids:
        if family_id not in ablation_family_ids:
            errors.append(f"family_missing_ablation_matrix_row:{family_id}")

    transfer_family_ids: set[str] = set()
    for row in transfer_matrix if isinstance(transfer_matrix, list) else []:
        family_id = row.get("family_id")
        transfer_family_ids.add(family_id)
        if row.get("split_required") is not True:
            errors.append(f"transfer_split_not_required:{family_id}")
        for field in [
            "family_id",
            "transfer_condition",
            "counterfactual_condition",
            "nuisance_variables",
            "target_variables",
            "leakage_risk_reduced"
        ]:
            if field in ("nuisance_variables", "target_variables"):
                if not as_nonempty_list(row.get(field)):
                    errors.append(f"transfer_missing_list:{family_id}:{field}")
            elif not row.get(field):
                errors.append(f"transfer_missing_field:{family_id}:{field}")
    for family_id in family_ids:
        if family_id not in transfer_family_ids:
            errors.append(f"family_missing_transfer_counterfactual_row:{family_id}")

    closure = closed_inheritance.get("current_generated_gate4_partner_id_lookup_family_closure", {})
    closed_family_inherited = (
        closure.get("best_faithful_baseline") == "partner_id_lookup_baseline"
        and closure.get("score") == 1.0
        and closure.get("threshold") == 0.8
        and closure.get("same_family_repair_allowed") is False
    )
    if not closed_family_inherited:
        errors.append("closed_family_negative_evidence_not_inherited")

    rule_ids = {
        row.get("rule_id")
        for row in rules.get("block_rules", [])
        if isinstance(row, dict)
    }
    missing_rule_ids = sorted(REQUIRED_RULE_IDS - rule_ids)
    if missing_rule_ids:
        errors.append("missing_validation_rules:" + ",".join(missing_rule_ids))

    summary = {
        "family_count": len(families),
        "baseline_row_count": len(baseline_matrix) if isinstance(baseline_matrix, list) else 0,
        "ablation_row_count": len(ablation_matrix) if isinstance(ablation_matrix, list) else 0,
        "transfer_counterfactual_row_count": len(transfer_matrix) if isinstance(transfer_matrix, list) else 0,
        "required_families_present": not missing_required_families,
        "required_family_ids_present": sorted(REQUIRED_FAMILY_IDS & family_ids),
        "missing_required_families": missing_required_families,
        "closed_family_inherited": closed_family_inherited,
        "candidate_code_authorized": registry.get("candidate_code_authorized") is True or protocol.get("candidate_code_allowed_before_preflight") is True,
        "admission_claim_authorized": protocol.get("admission_claim_forbidden") is not True,
        "mainline_claim_authorized": protocol.get("mainline_claim_forbidden") is not True
    }
    return errors, summary


def run_validation() -> dict[str, Any]:
    loaded = {
        key: load_json(ARTIFACT_DIR / filename)
        for key, filename in INPUT_FILES.items()
    }

    errors, summary = validate_payload(
        loaded["candidate_family_registry"],
        loaded["shared_tournament_preflight_protocol"],
        loaded["family_baseline_matrix"],
        loaded["family_ablation_matrix"],
        loaded["family_transfer_counterfactual_matrix"],
        loaded["closed_family_inheritance"],
        loaded["tournament_entry_validation_rules"]
    )

    fixture = loaded["malformed_positive_control_fixture"]
    fixture_errors, _fixture_summary = validate_payload(
        fixture["candidate_family_registry"],
        fixture["shared_tournament_preflight_protocol"],
        fixture["family_baseline_matrix"],
        fixture["family_ablation_matrix"],
        fixture["family_transfer_counterfactual_matrix"],
        fixture["closed_family_inheritance"],
        fixture["tournament_entry_validation_rules"]
    )
    invalid_fixture_failed_as_expected = len(fixture_errors) > 0
    if not invalid_fixture_failed_as_expected:
        errors.append("malformed_positive_control_did_not_fail")

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    final_verdict = "pass" if not errors and invalid_fixture_failed_as_expected else "block"
    inputs = [
        {
            "path": str((ARTIFACT_DIR / filename).relative_to(ARTIFACT_DIR.parents[1])).replace("\\", "/"),
            "sha256": sha256_file(ARTIFACT_DIR / filename)
        }
        for filename in INPUT_FILES.values()
    ]

    result = {
        "producer_function": "run_validation",
        "script_path": str(Path(__file__).relative_to(ARTIFACT_DIR.parents[1])).replace("\\", "/"),
        "inputs": inputs,
        "run_id": "mechanism_family_tournament_entry_criteria_001a_" + generated_at.replace("-", "").replace(":", "").replace("Z", "Z"),
        "current_head": current_head(),
        "code_path_hash": sha256_file(Path(__file__).resolve()),
        "generated_at_utc": generated_at,
        "family_count": summary["family_count"],
        "baseline_row_count": summary["baseline_row_count"],
        "ablation_row_count": summary["ablation_row_count"],
        "transfer_counterfactual_row_count": summary["transfer_counterfactual_row_count"],
        "required_families_present": summary["required_families_present"],
        "required_family_ids_present": summary["required_family_ids_present"],
        "missing_required_families": summary["missing_required_families"],
        "closed_family_inherited": summary["closed_family_inherited"],
        "invalid_fixture_failed_as_expected": invalid_fixture_failed_as_expected,
        "invalid_fixture_errors": fixture_errors,
        "candidate_code_authorized": summary["candidate_code_authorized"],
        "admission_claim_authorized": summary["admission_claim_authorized"],
        "mainline_claim_authorized": summary["mainline_claim_authorized"],
        "validation_errors": errors,
        "final_verdict": final_verdict
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    validation_result = run_validation()
    print(json.dumps({
        "final_verdict": validation_result["final_verdict"],
        "family_count": validation_result["family_count"],
        "baseline_row_count": validation_result["baseline_row_count"],
        "ablation_row_count": validation_result["ablation_row_count"],
        "transfer_counterfactual_row_count": validation_result["transfer_counterfactual_row_count"],
        "invalid_fixture_failed_as_expected": validation_result["invalid_fixture_failed_as_expected"],
        "validation_errors": validation_result["validation_errors"]
    }, indent=2, sort_keys=True))
    sys.exit(0 if validation_result["final_verdict"] == "pass" else 1)
