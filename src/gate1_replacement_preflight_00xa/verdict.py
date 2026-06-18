from __future__ import annotations

from copy import deepcopy

from .baselines import (
    DEGENERATE_BASELINE_IDS,
    FAIR_BASELINE_IDS,
    MANDATORY_BASELINE_IDS,
    PASSIVE_BASELINE_IDS,
)
from .readback import GENERATOR_SOURCE_PATH
from .metrics import CEILING_BAND_FLOOR, EQUIVALENCE_BAND, PARTIAL_INFERABILITY_MARGIN, TARGET_CEILING_MINIMUM


ALLOWED_VERDICTS = {
    "admissible_for_candidate_card_drafting_only",
    "rejected_metric_degenerate",
    "rejected_no_fair_signal",
    "rejected_answer_key_oracle_gap",
    "rejected_trivially_decodable",
    "rejected_baseline_saturated",
    "blocked_missing_partial_inferability_demonstration",
    "blocked_pending_canonical_readback",
    "blocked_missing_candidate_free_surface_spec",
    "blocked_candidate_authored_or_mutated_surface_spec",
}


def _synthetic_row(baseline_id: str, macro_f1: float) -> dict:
    return {
        "baseline_id": baseline_id,
        "producer_function": f"gate1_replacement_preflight_00xa.synthetic.{baseline_id}",
        "input_artifacts": ["synthetic_minimal_context"],
        "run_id": "minimal-valid-context",
        "seed_context_episode_ids": ["e1", "e2"],
        "aggregation_rule": "macro_f1_beta_1_over_binary_target",
        "code_path_hash": "a" * 64,
        "invoked": True,
        "independence_status": "independent_callable",
        "consumed_by_final_verdict": True,
        "metric": {"macro_f1": macro_f1},
        "applicability_status": "applicable",
    }


def minimal_valid_context(admissible_shape: bool = False) -> dict:
    fair_score = 0.78 if admissible_shape else 0.70
    oracle_score = 0.94 if admissible_shape else 0.94
    rows = {}
    for baseline_id in MANDATORY_BASELINE_IDS:
        if baseline_id in DEGENERATE_BASELINE_IDS or baseline_id == "size_only_sweep_0_to_N":
            score = 0.33
        elif baseline_id in PASSIVE_BASELINE_IDS:
            score = 0.62
        else:
            score = fair_score
        rows[baseline_id] = _synthetic_row(baseline_id, score)
    return {
        "source_pin_readback": {"all_present": True, "hash_conflicts": [], "consumed_by_final_verdict": True},
        "surface_spec_hash": {"ok": True, "verdict": "surface_spec_hash_verified", "consumed_by_final_verdict": True},
        "generator_provenance": {
            "generator_source_path": GENERATOR_SOURCE_PATH,
            "generator_source_hash": "b" * 64,
            "source_pin_sha256": "b" * 64,
            "source_pin_integrity": True,
            "generator_version_or_code_path_hash": "c" * 64,
            "producer_function": "gate1_replacement_preflight_00xa.spec_loader.build_candidate_free_surface_bundle",
            "fair_baseline_access": "same_candidate_free_visible_state_legal_channel_and_fixed_budget",
            "hidden_target_storage": "episode.hidden_target stored outside visible_state",
            "no_candidate_authored_truth": True,
            "candidate_authored_truth": False,
            "readback_channels": ["canonical_file_api_read_bytes", "canonical_source_pin_readback"],
            "self_readback_only": False,
            "consumed_by_final_verdict": True,
        },
        "baseline_rows_by_id": rows,
        "fair_baseline_ids": sorted(FAIR_BASELINE_IDS),
        "leakage": {
            "clean_scan": {"detected": []},
            "positive_control": {
                "detected_id": "leakage_positive_control_visible_answer_key_label",
                "detected": True,
                "removal_removes_detection": True,
                "consumed_by_final_verdict": True,
            },
            "consumed_by_final_verdict": True,
        },
        "replay": {
            "validation": {"valid": True, "errors": []},
            "consumed_by_final_verdict": True,
            "applicability": "applicable_serialized_state",
        },
        "ablation": {
            "rows": [
                {"ablation_id": "no_action", "invoked": True, "consumed_by_final_verdict": True},
                {"ablation_id": "no_transition", "invoked": True, "consumed_by_final_verdict": True},
                {"ablation_id": "no_legal_channel", "invoked": True, "consumed_by_final_verdict": True},
            ],
            "consumed_by_final_verdict": True,
        },
        "oracle": {
            "visible_channel_oracle": {"metric": {"macro_f1": oracle_score}, "budget_faithful": True, "legal_access_only": True},
            "answer_key_oracle": {"metric": {"macro_f1": oracle_score}, "diagnostic_only": True},
            "null_oracle": {"metric": {"macro_f1": 0.33}},
        },
        "partial_inferability": {
            "passive_family_macro_f1": 0.62,
            "random_or_matched_marginal_macro_f1": 0.33,
            "visible_channel_oracle_macro_f1": oracle_score,
            "residual_uncertainty_under_passive": True,
            "legal_channel_reduces_uncertainty": True,
            "fair_channel_has_signal": True,
            "consumed_by_final_verdict": True,
        },
        "adaptation_or_learning_claimed": False,
        "trained_learner": {"included": False},
    }


def validate_baseline_panel(context: dict) -> dict:
    rows = context.get("baseline_rows_by_id", {})
    errors = []
    for baseline_id in MANDATORY_BASELINE_IDS:
        row = rows.get(baseline_id)
        if row is None:
            errors.append(f"missing_required_baseline:{baseline_id}")
            continue
        if row.get("invoked") is not True:
            errors.append(f"baseline_not_invoked:{baseline_id}")
        if row.get("independence_status") != "independent_callable":
            errors.append(f"baseline_not_independent:{baseline_id}")
        if row.get("consumed_by_final_verdict") is not True:
            errors.append(f"baseline_not_consumed:{baseline_id}")
        if not row.get("producer_function") or not row.get("code_path_hash"):
            errors.append(f"baseline_missing_provenance:{baseline_id}")
    return {"valid": not errors, "errors": errors}


def validate_generator_provenance(generator_provenance: dict | None) -> dict:
    errors = []
    if not isinstance(generator_provenance, dict):
        return {
            "valid": False,
            "errors": ["generator_provenance_missing"],
            "producer_function": "gate1_replacement_preflight_00xa.verdict.validate_generator_provenance",
            "consumed_by_final_verdict": True,
        }

    required_fields = [
        "generator_source_path",
        "generator_source_hash",
        "source_pin_sha256",
        "generator_version_or_code_path_hash",
        "producer_function",
        "fair_baseline_access",
        "hidden_target_storage",
        "no_candidate_authored_truth",
        "readback_channels",
        "consumed_by_final_verdict",
    ]
    for field in required_fields:
        if not generator_provenance.get(field):
            errors.append(f"missing_required_generator_provenance:{field}")

    source_hash = generator_provenance.get("generator_source_hash")
    source_pin_hash = generator_provenance.get("source_pin_sha256")
    if not isinstance(source_hash, str) or len(source_hash) != 64:
        errors.append("invalid_generator_source_hash")
    if source_hash != source_pin_hash:
        errors.append("generator_source_hash_mismatch")
    if generator_provenance.get("source_pin_integrity") is not True:
        errors.append("generator_source_pin_integrity_false")
    if generator_provenance.get("generator_source_path") != GENERATOR_SOURCE_PATH:
        errors.append("generator_source_path_unexpected")
    if generator_provenance.get("self_readback_only") is True:
        errors.append("generator_provenance_self_readback_only")
    readback_channels = set(generator_provenance.get("readback_channels", []))
    if "canonical_source_pin_readback" not in readback_channels:
        errors.append("generator_source_pin_readback_missing")
    if "canonical_file_api_read_bytes" not in readback_channels:
        errors.append("generator_file_api_readback_missing")
    if generator_provenance.get("no_candidate_authored_truth") is not True:
        errors.append("candidate_authored_generator_truth")
    if generator_provenance.get("candidate_authored_truth") is True:
        errors.append("candidate_authored_generator_truth")
    if generator_provenance.get("consumed_by_final_verdict") is not True:
        errors.append("generator_provenance_not_consumed")

    return {
        "valid": not errors,
        "errors": errors,
        "producer_function": "gate1_replacement_preflight_00xa.verdict.validate_generator_provenance",
        "input_artifacts": ["generator_provenance.json", "source_readback.json"],
        "aggregation_rule": "fail_closed_if_generator_provenance_absent_unverifiable_self_readback_or_candidate_authored",
        "generator_source_path": generator_provenance.get("generator_source_path"),
        "generator_source_hash": generator_provenance.get("generator_source_hash"),
        "source_pin_sha256": generator_provenance.get("source_pin_sha256"),
        "consumed_by_final_verdict": True,
    }


def _trained_learner_invalid(context: dict) -> bool:
    if not context.get("adaptation_or_learning_claimed"):
        return False
    learner = context.get("trained_learner", {})
    return not (
        learner.get("included")
        and learner.get("ml_library_used")
        and learner.get("real_fit_evidence")
        and not learner.get("deterministic_stub")
    )


def _final(verdict: str, reason: str, context: dict, extra: dict | None = None) -> dict:
    payload = {
        "final_verdict": verdict,
        "allowed_verdict": verdict in ALLOWED_VERDICTS,
        "terminal_reason_id": reason,
        "producer_function": "gate1_replacement_preflight_00xa.verdict.derive_final_verdict",
        "input_artifacts": [
            "source_readback.json",
            "generator_provenance.json",
            "generator_provenance_gate.json",
            "baseline_results.jsonl",
            "partial_inferability.json",
            "oracle_results.json",
            "leakage_results.json",
            "replay_results.json",
            "ablation_results.json",
        ],
        "aggregation_rule": "ordered_fail_closed_verdict_derivation",
        "consumed_by_final_verdict": True,
        "claim_ceiling": "candidate-free preflight evidence bundle only",
    }
    if extra:
        payload.update(extra)
    return payload


def derive_final_verdict(context: dict) -> dict:
    surface = context.get("surface_spec_hash", {})
    if surface.get("verdict") == "blocked_missing_candidate_free_surface_spec":
        return _final("blocked_missing_candidate_free_surface_spec", "surface_spec_missing", context)
    if surface.get("verdict") == "blocked_candidate_authored_or_mutated_surface_spec" or surface.get("ok") is False:
        return _final("blocked_candidate_authored_or_mutated_surface_spec", "surface_spec_hash_mismatch_or_mutation", context)

    source = context.get("source_pin_readback", {})
    if not source.get("all_present") or source.get("hash_conflicts"):
        return _final("blocked_pending_canonical_readback", "source_pin_readback_conflict", context)

    generator_provenance_gate = validate_generator_provenance(context.get("generator_provenance"))
    generator_extra = {"generator_provenance_gate": generator_provenance_gate}
    if not generator_provenance_gate["valid"]:
        return _final(
            "blocked_pending_canonical_readback",
            "generator_provenance_missing_or_invalid",
            context,
            generator_extra,
        )

    baseline_validation = validate_baseline_panel(context)
    if not baseline_validation["valid"]:
        return _final(
            "blocked_pending_canonical_readback",
            "baseline_panel_invalid",
            context,
            {**generator_extra, "baseline_panel_errors": baseline_validation["errors"]},
        )

    if _trained_learner_invalid(context):
        return _final("blocked_pending_canonical_readback", "trained_learner_without_real_fit", context, generator_extra)

    leakage = context.get("leakage", {})
    positive = leakage.get("positive_control", {})
    if not positive.get("detected_id") or not positive.get("consumed_by_final_verdict"):
        return _final(
            "blocked_missing_partial_inferability_demonstration",
            "leakage_positive_control_absent_or_unconsumed",
            context,
            generator_extra,
        )
    if leakage.get("clean_scan", {}).get("detected"):
        return _final("blocked_pending_canonical_readback", "leakage_detected_on_clean_visible_path", context, generator_extra)

    replay = context.get("replay", {})
    if not replay.get("validation", {}).get("valid", False):
        return _final("blocked_pending_canonical_readback", "replay_invalid", context, generator_extra)

    ablation_rows = context.get("ablation", {}).get("rows", [])
    if not ablation_rows or any(not row.get("invoked") or not row.get("consumed_by_final_verdict") for row in ablation_rows):
        return _final("blocked_missing_partial_inferability_demonstration", "ablation_missing_or_unconsumed", context, generator_extra)

    rows = context["baseline_rows_by_id"]
    for baseline_id in DEGENERATE_BASELINE_IDS:
        if rows[baseline_id]["metric"]["macro_f1"] >= CEILING_BAND_FLOOR:
            return _final("rejected_metric_degenerate", "degenerate_predictor_reached_ceiling_band", context, generator_extra)
    if rows["size_only_sweep_0_to_N"]["metric"]["macro_f1"] >= CEILING_BAND_FLOOR:
        return _final("rejected_metric_degenerate", "size_only_sweep_reached_ceiling_band", context, generator_extra)

    partial = context.get("partial_inferability", {})
    passive_score = max(
        [partial.get("passive_family_macro_f1", 0.0)]
        + [rows[baseline_id]["metric"]["macro_f1"] for baseline_id in PASSIVE_BASELINE_IDS]
    )
    if passive_score >= CEILING_BAND_FLOOR:
        return _final("rejected_trivially_decodable", "passive_family_reached_ceiling_band", context, generator_extra)
    if partial.get("random_or_matched_marginal_macro_f1", 0.0) >= CEILING_BAND_FLOOR:
        return _final("rejected_no_fair_signal", "random_or_matched_marginal_reached_ceiling_band", context, generator_extra)

    visible_oracle = context["oracle"]["visible_channel_oracle"]["metric"]["macro_f1"]
    answer_key_oracle = context["oracle"]["answer_key_oracle"]["metric"]["macro_f1"]
    strongest_fair = max(rows[baseline_id]["metric"]["macro_f1"] for baseline_id in context["fair_baseline_ids"])
    if answer_key_oracle >= TARGET_CEILING_MINIMUM and visible_oracle < TARGET_CEILING_MINIMUM:
        return _final("rejected_answer_key_oracle_gap", "headroom_is_answer_key_only", context, generator_extra)
    if visible_oracle - passive_score < PARTIAL_INFERABILITY_MARGIN:
        return _final(
            "blocked_missing_partial_inferability_demonstration",
            "visible_channel_does_not_reduce_passive_uncertainty",
            context,
            generator_extra,
        )
    if strongest_fair >= visible_oracle - EQUIVALENCE_BAND:
        return _final(
            "rejected_baseline_saturated",
            "fair_baseline_ties_oracle_within_equivalence_band",
            context,
            {**generator_extra, "strongest_fair_macro_f1": strongest_fair, "visible_oracle_macro_f1": visible_oracle},
        )
    if visible_oracle < TARGET_CEILING_MINIMUM:
        return _final("rejected_no_fair_signal", "visible_channel_oracle_below_target_ceiling", context, generator_extra)
    return _final("admissible_for_candidate_card_drafting_only", "all_fail_closed_controls_clear", context, generator_extra)


def context_from_run(
    source_pin_readback: dict,
    surface_spec_hash: dict,
    generator_provenance: dict,
    baseline_rows: list[dict],
    leakage: dict,
    replay: dict,
    ablation: dict,
    oracle: dict,
    partial_inferability: dict,
) -> dict:
    return {
        "source_pin_readback": source_pin_readback,
        "surface_spec_hash": surface_spec_hash,
        "generator_provenance": generator_provenance,
        "baseline_rows_by_id": {row["baseline_id"]: deepcopy(row) for row in baseline_rows},
        "fair_baseline_ids": sorted(FAIR_BASELINE_IDS),
        "leakage": leakage,
        "replay": replay,
        "ablation": ablation,
        "oracle": oracle,
        "partial_inferability": partial_inferability,
        "adaptation_or_learning_claimed": False,
        "trained_learner": {"included": False, "reason": "no adaptation_or_learning_claim_in_preflight"},
    }
