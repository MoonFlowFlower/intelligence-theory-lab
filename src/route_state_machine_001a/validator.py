from __future__ import annotations

import hashlib
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import state_machine


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _relative_posix(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return _posix(path)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def code_path_hash() -> str:
    digest = hashlib.sha256()
    for path in sorted(
        [Path(__file__), Path(state_machine.__file__)],
        key=lambda item: item.as_posix(),
    ):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _new_error(code: str, message: str, **context: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"code": code, "message": message}
    if context:
        payload["context"] = context
    return payload


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)


def _string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_string_values(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_string_values(item))
        return strings
    return []


def _normalized_set(paths: list[str] | tuple[str, ...] | None) -> set[str]:
    return {_posix(path).strip().lstrip("./") for path in (paths or [])}


def _path_is_authorized(path: str, authorized_paths: list[str] | tuple[str, ...] | None) -> bool:
    normalized = _posix(path).strip().lstrip("./")
    for authorized in _normalized_set(authorized_paths):
        if normalized == authorized:
            return True
        if authorized.endswith("/") and normalized.startswith(authorized):
            return True
    return False


def is_roadmap_like_changed_file(path: str) -> bool:
    normalized = _posix(path).lower()
    if not normalized.startswith(("docs/", "src/", "tests/", "artifacts/")):
        return False
    basename = normalized.rsplit("/", 1)[-1]
    searchable = f"{normalized} {basename.replace('_', '-')}"
    return any(marker in searchable for marker in state_machine.ROADMAP_LIKE_MARKERS)


def _claim_ceiling_has_max(payload: Any) -> bool:
    return isinstance(payload, dict) and isinstance(payload.get("max"), str) and bool(payload["max"].strip())


def _source_readback_has_l014_or_equivalent(source_readback: Any) -> bool:
    strings = [item.strip() for item in _string_values(source_readback) if item.strip()]
    joined = "\n".join(strings)
    return "L-014" in joined or "L014" in joined


def _is_authorizing_value(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "authorized", "allow", "allowed"}
    return False


def validate_red_field_contract(contract_payload: Any) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if not isinstance(contract_payload, dict):
        errors.append(
            _new_error(
                "red_field_contract_not_object",
                "The committed Red-field contract must be a JSON object.",
            )
        )
        contract_payload = {}

    if contract_payload.get("task_id") != state_machine.K0_RED_FIELD_ADDENDUM_PIN["task_id"]:
        errors.append(
            _new_error(
                "red_field_contract_task_id_mismatch",
                "The Red-field contract task id must match the banked addendum pin.",
                expected=state_machine.K0_RED_FIELD_ADDENDUM_PIN["task_id"],
                actual=contract_payload.get("task_id"),
            )
        )

    axes = contract_payload.get("evidence_axes")
    axes = axes if isinstance(axes, dict) else {}
    expected_axes = {
        "evidence_state": list(state_machine.K0_RED_FIELD_EVIDENCE_STATES),
        "control_comparison_state": list(state_machine.K0_RED_FIELD_CONTROL_STATES),
        "comparison_state": list(state_machine.K0_RED_FIELD_RIVAL_STATES),
    }
    for field, expected in expected_axes.items():
        actual = axes.get(field)
        if actual != expected or not isinstance(actual, list) or len(actual) != len(set(actual)):
            errors.append(
                _new_error(
                    f"red_field_contract_{field}_invalid",
                    "Each Red-field axis must equal its frozen unique enum in frozen order.",
                    field=field,
                    expected=expected,
                    actual=actual,
                )
            )
    if "CONTROL_EQUIVALENT" in _string_values(axes.get("evidence_state")):
        errors.append(
            _new_error(
                "red_field_control_equivalent_in_evidence_state",
                "CONTROL_EQUIVALENT belongs only to the shortcut-control axis.",
            )
        )

    required_control_provenance = {
        "control_comparison_reason",
        "frozen_control_panel_id",
        "control_contrast_ids",
        "control_signed_margin",
        "control_confidence_interval",
        "control_equivalence_band",
        "control_equivalence_type",
    }
    required_rival_provenance = {
        "rival_comparison_reason",
        "frozen_rival_panel_id",
        "rival_contrast_ids",
        "rival_signed_margin",
        "rival_confidence_interval",
        "rival_equivalence_band",
        "rival_equivalence_type",
    }
    required_equivalence_types: set[Any] = {
        "CANDIDATE_PARITY",
        "ADMISSION_CEILING_SATURATION",
        "OWN_RULE_AMORTIZED_PARITY",
        "CONTROL_BETTER",
        None,
    }
    if set(axes.get("control_provenance_fields") or []) != required_control_provenance:
        errors.append(
            _new_error(
                "red_field_control_provenance_fields_invalid",
                "Control-axis provenance fields must equal the frozen set.",
            )
        )
    if set(axes.get("rival_provenance_fields") or []) != required_rival_provenance:
        errors.append(
            _new_error(
                "red_field_rival_provenance_fields_invalid",
                "Rival-axis provenance fields must equal the frozen set.",
            )
        )
    if set(axes.get("control_equivalence_type") or []) != required_equivalence_types:
        errors.append(
            _new_error(
                "red_field_control_equivalence_types_invalid",
                "Control equivalence types must equal the frozen set, including null.",
            )
        )

    semantic_rules = contract_payload.get("semantic_rules")
    semantic_rules = semantic_rules if isinstance(semantic_rules, dict) else {}
    required_semantics = {
        "absent_requires_valid_causal_ablation_failure": True,
        "causal_pass_shortcut_parity_mapping": "PRESENT_BOUNDED_PLUS_CONTROL_EQUIVALENT",
        "control_or_rival_run_underpowered_mapping": "STAR_INCONCLUSIVE",
        "control_tie_blocks_architectural_specialness": True,
        "strong_negative_can_satisfy_falsifier_collapse": True,
        "strong_negative_is_automatic_statistical_equivalence": False,
        "v_special_is_frozen_rival_panel_relative": True,
    }
    if any(semantic_rules.get(key) != value for key, value in required_semantics.items()):
        errors.append(
            _new_error(
                "red_field_semantic_rules_invalid",
                "Causal, shortcut, underpowered, strong-negative, and V_special semantics must remain frozen.",
            )
        )

    role_contract = contract_payload.get("arm_role_contract")
    role_contract = role_contract if isinstance(role_contract, dict) else {}
    assignments = role_contract.get("assignments")
    assignments = assignments if isinstance(assignments, list) else []
    role_rows = [row for row in assignments if isinstance(row, dict)]
    arm_ids = [row.get("arm_id") for row in role_rows]
    role_by_arm = {
        row.get("arm_id"): row.get("arm_role")
        for row in role_rows
        if isinstance(row.get("arm_id"), str)
    }
    if (
        role_contract.get("roles") != list(state_machine.K0_RED_FIELD_ARM_ROLES)
        or role_contract.get("one_role_per_arm_id") is not True
        or role_contract.get("ex_ante_assignment_required") is not True
        or len(role_rows) != len(assignments)
        or len(arm_ids) != len(set(arm_ids))
        or any(role not in state_machine.K0_RED_FIELD_ARM_ROLES for role in role_by_arm.values())
    ):
        errors.append(
            _new_error(
                "red_field_arm_role_overlap_or_invalid",
                "Every named arm must have exactly one frozen ex-ante role.",
            )
        )

    catalog = contract_payload.get("comparison_catalog")
    catalog = catalog if isinstance(catalog, dict) else {}
    evidence_catalog = set(catalog.get("evidence_contrast_ids") or [])
    control_catalog = set(catalog.get("control_comparison_ids") or [])
    rival_catalog = set(catalog.get("rival_comparison_ids") or [])
    integrity_catalog = set(contract_payload.get("integrity_dependency_catalog") or [])
    claim_catalog = set(contract_payload.get("claim_template_registry") or [])
    mappings = contract_payload.get("component_control_mapping")
    mappings = mappings if isinstance(mappings, list) else []
    mapping_rows = [row for row in mappings if isinstance(row, dict)]
    component_ids = [row.get("component_id") for row in mapping_rows]
    required_mapping_fields = {
        "component_id",
        "evidence_contrast_ids",
        "control_comparison_ids",
        "rival_comparison_ids",
        "integrity_dependency_ids",
        "claim_template_ids",
        "causal_arm_ids",
        "shortcut_control_arm_ids",
        "rival_arm_ids",
        "integrity_control_arm_ids",
    }
    if component_ids != list(state_machine.K0_RED_FIELD_COMPONENT_IDS):
        errors.append(
            _new_error(
                "red_field_component_mapping_set_invalid",
                "The component mapping must contain the six frozen components in frozen order.",
                actual=component_ids,
            )
        )

    role_fields = {
        "causal_arm_ids": "CAUSAL_ABLATION",
        "shortcut_control_arm_ids": "SHORTCUT_CONTROL",
        "rival_arm_ids": "RIVAL",
        "integrity_control_arm_ids": "INTEGRITY_CONTROL",
    }
    for row in mapping_rows:
        component_id = row.get("component_id")
        missing_fields = sorted(required_mapping_fields - set(row))
        empty_fields = sorted(
            field
            for field in required_mapping_fields - {"component_id"}
            if not isinstance(row.get(field), list) or not row.get(field)
        )
        unresolved = {
            "evidence_contrast_ids": sorted(set(row.get("evidence_contrast_ids") or []) - evidence_catalog),
            "control_comparison_ids": sorted(set(row.get("control_comparison_ids") or []) - control_catalog),
            "rival_comparison_ids": sorted(set(row.get("rival_comparison_ids") or []) - rival_catalog),
            "integrity_dependency_ids": sorted(set(row.get("integrity_dependency_ids") or []) - integrity_catalog),
            "claim_template_ids": sorted(set(row.get("claim_template_ids") or []) - claim_catalog),
        }
        role_errors = {
            field: sorted(
                arm
                for arm in row.get(field) or []
                if role_by_arm.get(arm) != expected_role
            )
            for field, expected_role in role_fields.items()
        }
        if missing_fields or empty_fields or any(unresolved.values()) or any(role_errors.values()):
            errors.append(
                _new_error(
                    "red_field_component_mapping_invalid",
                    "Every component must have resolved non-empty causal/control/rival/integrity mappings.",
                    component_id=component_id,
                    missing_fields=missing_fields,
                    empty_fields=empty_fields,
                    unresolved=unresolved,
                    role_errors=role_errors,
                )
            )

    mapping_by_component = {
        row.get("component_id"): row
        for row in mapping_rows
        if isinstance(row.get("component_id"), str)
    }
    required_component_arms = {
        "V_model": {
            "causal_arm_ids": {"planner_bypass", "checkpoint_swap", "prediction_counterfactual"},
            "shortcut_control_arm_ids": {
                "observation_only",
                "window_history",
                "exact_lookup",
                "nearest_neighbor",
                "graph_lookup",
                "transition_table",
                "successor_map",
                "count_table",
                "fsm_planner",
                "episodic_traversal",
                "candidate_own_rule_amortized",
            },
        },
        "V_online": {
            "causal_arm_ids": {"no_update", "shuffled_outcome"},
            "shortcut_control_arm_ids": {
                "candidate_own_rule_batched",
                "candidate_own_rule_amortized",
                "same_feedback_budget_table_history_learner",
            },
        },
        "V_replay": {
            "causal_arm_ids": {"matched_replay_off"},
            "shortcut_control_arm_ids": {
                "window_history",
                "episodic_traversal",
                "graph_lookup",
                "transition_table",
                "successor_map",
                "count_table",
                "fsm_planner",
                "matched_no_replay_amortized_learner",
            },
            "integrity_control_arm_ids": {"corrupted_replay_detector"},
        },
        "V_memory": {
            "causal_arm_ids": {"memory_read_off", "memory_zero", "source_deletion", "history_replacement"},
            "shortcut_control_arm_ids": {
                "recency",
                "summary",
                "rag",
                "exact_lookup",
                "nearest_neighbor",
                "window_history",
                "graph_lookup",
                "transition_table",
                "successor_map",
                "count_table",
                "fsm_planner",
                "episodic_traversal",
            },
        },
        "V_transfer": {
            "causal_arm_ids": {
                "fresh_init",
                "from_scratch",
                "checkpoint_only",
                "replay_reset",
                "memory_reset",
                "full_carryover",
            },
            "shortcut_control_arm_ids": {
                "equal_budget_persistent_history_carrier",
                "equal_budget_persistent_cache_carrier",
                "equal_budget_persistent_batched_carrier",
            },
        },
        "V_special": {
            "shortcut_control_arm_ids": {
                "observation_only",
                "window_history",
                "exact_lookup",
                "nearest_neighbor",
                "graph_lookup",
                "transition_table",
                "successor_map",
                "count_table",
                "fsm_planner",
                "episodic_traversal",
                "candidate_own_rule_amortized",
                "candidate_own_rule_batched",
                "same_feedback_budget_table_history_learner",
                "matched_no_replay_amortized_learner",
                "recency",
                "summary",
                "rag",
                "equal_budget_persistent_history_carrier",
                "equal_budget_persistent_cache_carrier",
                "equal_budget_persistent_batched_carrier",
            },
        },
    }
    for component_id, required_fields in required_component_arms.items():
        row = mapping_by_component.get(component_id, {})
        for field, required_arms in required_fields.items():
            actual_arms = set(row.get(field) or [])
            if not required_arms.issubset(actual_arms):
                errors.append(
                    _new_error(
                        "red_field_required_component_arm_missing",
                        "A frozen causal/control/integrity arm is missing from its component mapping.",
                        component_id=component_id,
                        mapping_field=field,
                        missing=sorted(required_arms - actual_arms),
                    )
                )
    graph_cache = set(state_machine.K0_RED_FIELD_GRAPH_CACHE_ARMS)
    for component_id in ("V_model", "V_replay", "V_memory", "V_special"):
        shortcuts = set(mapping_by_component.get(component_id, {}).get("shortcut_control_arm_ids") or [])
        if not graph_cache.issubset(shortcuts):
            errors.append(
                _new_error(
                    "red_field_graph_cache_mapping_missing",
                    "Every applicable component must include the full frozen graph/cache shortcut family.",
                    component_id=component_id,
                    missing=sorted(graph_cache - shortcuts),
                )
            )
        if "window_history" not in shortcuts:
            errors.append(
                _new_error(
                    "red_field_window_history_mapping_missing",
                    "Window-history must remain an explicit shortcut control.",
                    component_id=component_id,
                )
            )
    replay_mapping = mapping_by_component.get("V_replay", {})
    if (
        "matched_replay_off" not in (replay_mapping.get("causal_arm_ids") or [])
        or "corrupted_replay_detector" not in (replay_mapping.get("integrity_control_arm_ids") or [])
        or role_by_arm.get("matched_replay_off") != "CAUSAL_ABLATION"
        or role_by_arm.get("corrupted_replay_detector") != "INTEGRITY_CONTROL"
    ):
        errors.append(
            _new_error(
                "red_field_replay_causal_integrity_conflation",
                "Matched replay-off and corrupted-replay detection must be distinct causal and integrity controls.",
            )
        )

    signature = contract_payload.get("control_signature_contract")
    signature = signature if isinstance(signature, dict) else {}
    required_contrast_fields = {
        "contrast_id",
        "component_ids",
        "control_class",
        "family_ids",
        "protocol_ids",
        "full_arm_id",
        "intervention_arm_id",
        "reference_arm_id",
        "estimand_ids",
        "expected_effect",
        "success_signature",
        "failure_signature",
        "ambiguous_signature",
        "strong_negative_counts_as_success",
        "required_power_spec_id",
        "required_seed_block_id",
        "blast_radius_id",
        "verdict_mapping",
    }
    if (
        set(signature.get("future_required_artifacts") or [])
        != {"control_signature_contract.json", "control_signature_simulation.json"}
        or set(signature.get("candidate_independent_simulation_cases") or [])
        != {"parity", "strong_negative", "survival_positive", "boundary_failure"}
        or set(signature.get("required_contrast_fields") or []) != required_contrast_fields
        or signature.get("strong_negative_classification")
        != "FALSIFIER_COLLAPSE_SUCCESS_NOT_CONTROL_INACTIVE"
        or signature.get("strong_negative_is_statistical_equivalence") is not False
    ):
        errors.append(
            _new_error(
                "red_field_control_signature_contract_invalid",
                "Sign simulation, contrast fields, and strong-negative semantics must remain frozen.",
            )
        )

    determinism = contract_payload.get("determinism_contract")
    determinism = determinism if isinstance(determinism, dict) else {}
    required_rngs = {
        "python_random",
        "numpy",
        "torch_cpu",
        "torch_cuda",
        "environment",
        "action_tiebreak",
        "replay_sampler",
        "dataloader_worker",
    }
    required_compare_fields = {
        "predictions",
        "rankings",
        "actions",
        "state_hashes",
        "update_deltas",
        "checkpoint_hashes",
        "metrics",
    }
    required_platform_pins = {"os", "python", "numpy", "torch", "device", "cuda", "cudnn", "driver"}
    required_determinism_fields = {
        "seed_derivation_function",
        "rng_state_serialization_restore",
        "torch_deterministic_algorithms",
        "cudnn_benchmark_flag",
        "cudnn_deterministic_flag",
        "cpu_thread_count",
        "interop_thread_count",
    }
    if (
        determinism.get("exactness_mode") != "bit_exact_same_frozen_platform_backend_dependencies"
        or determinism.get("original_run_counts_as_recompute") is not False
        or determinism.get("fresh_processes_required") != 2
        or determinism.get("launcher_sets_pythonhashseed_before_interpreter_start") is not True
        or set(determinism.get("rng_registry") or []) != required_rngs
        or determinism.get("unregistered_rng_mapping") != "FAIL"
        or set(determinism.get("compare_fields") or []) != required_compare_fields
        or set(determinism.get("platform_pins") or []) != required_platform_pins
        or set(determinism.get("required_determinism_fields") or []) != required_determinism_fields
        or set(determinism.get("forbidden_rng_sources") or [])
        != {"time_based_seed", "undeclared_os_random", "implicit_global_rng"}
        or set(determinism.get("excluded_volatile_fields") or []) != {"timestamp", "pid", "wall_clock"}
        or determinism.get("process_isolation") != {"distinct_pid": True, "distinct_temp_dir": True}
        or determinism.get("mismatch_mapping") != "REPLAY_COMPUTATION_INTEGRITY_FAILED"
        or determinism.get("bit_exact_failure_mapping") != "INVALID_INSTRUMENT"
        or determinism.get("post_result_tolerance_replay_forbidden") is not True
    ):
        errors.append(
            _new_error(
                "red_field_determinism_contract_invalid",
                "The frozen bit-exact, RNG-registry, fresh-process x2, and mismatch contract is incomplete or drifted.",
            )
        )

    power = contract_payload.get("power_mde_equivalence_contract")
    power = power if isinstance(power, dict) else {}
    required_decision_fields = {
        "decision_kind",
        "alpha",
        "ci_method",
        "sidedness",
        "multiplicity_family",
        "multiplicity_correction",
        "target_power",
        "sesoi",
        "equivalence_margin",
        "variance_source",
        "fixed_seed_count",
        "computed_mde",
        "computed_power_at_sesoi",
        "pass_predicate",
        "underpowered_mapping",
    }
    required_equivalence_decisions = {
        "CONTROL_EQUIVALENT",
        "RIVAL_SATURATED",
        "no_interference",
        "retention_equivalence",
        "order_invariance",
    }
    if (
        set(power.get("future_required_sections") or []) != {"metrics", "estimands", "seed_blocks", "decision_specs"}
        or set(power.get("decision_kinds") or []) != {"superiority", "equivalence", "noninferiority", "collapse"}
        or set(power.get("decision_spec_required_fields") or []) != required_decision_fields
        or set(power.get("powered_equivalence_required_for") or []) != required_equivalence_decisions
        or power.get("not_rejecting_difference_is_equivalence") is not False
        or power.get("seed_policy") != "FIXED_COUNT_OR_EX_ANTE_SEQUENTIAL_MAX_N_ALPHA_SPENDING"
        or power.get("post_result_seed_addition_forbidden") is not True
        or power.get("unused_frozen_input_mapping") != "INVALID_INSTRUMENT"
        or power.get("underpowered_mapping") != "STAR_INCONCLUSIVE"
        or power.get("rival_panel_max_rule") != "FROZEN_MULTIPLICITY_OR_NESTED_RESAMPLING"
    ):
        errors.append(
            _new_error(
                "red_field_power_mde_equivalence_contract_invalid",
                "MDE, power, fixed-seed, multiplicity, and powered-equivalence rules must remain frozen.",
            )
        )

    blast_radius = contract_payload.get("integrity_blast_radius")
    blast_radius = blast_radius if isinstance(blast_radius, dict) else {}
    expected_blast_rules = {
        "shared_replay_recompute_engine_failure": "INVALIDATE_ALL_AND_ONLY_DEPENDENT_COMPONENTS_MAY_BE_GLOBAL",
        "one_arm_or_trace_recomputation_failure": "INVALIDATE_ONLY_DEPENDENT_ESTIMANDS_AND_COMPONENTS",
        "matched_replay_off_ties_full": "V_replay_ABSENT",
        "matched_no_replay_shortcut_learner_ties": "CONTROL_EQUIVALENT",
        "replay_reset_carrier_ties": "AFFECT_ONLY_MAPPED_V_transfer_REPLAY_CARRIER_PROPOSITION",
    }
    actual_blast_rules = {
        row.get("failure_class"): row.get("mapping")
        for row in blast_radius.get("rules") or []
        if isinstance(row, dict)
    }
    if (
        blast_radius.get("unconditional_replay_failure_global_propagation_forbidden") is not True
        or blast_radius.get("local_leakage_uses_frozen_dependency_matrix") is not True
        or actual_blast_rules != expected_blast_rules
        or set(blast_radius.get("required_machine_fields") or [])
        != {
            "integrity_gate_id",
            "gate_class",
            "affected_arms",
            "affected_estimands",
            "affected_components",
            "failure_action",
            "state_mapping",
            "resolver_function",
        }
    ):
        errors.append(
            _new_error(
                "red_field_integrity_blast_radius_invalid",
                "Replay/recompute failures must propagate through the frozen dependency-scoped blast-radius rules.",
            )
        )

    firewall = contract_payload.get("firewall_contract")
    firewall = firewall if isinstance(firewall, dict) else {}
    other = contract_payload.get("other_red_fields")
    other = other if isinstance(other, dict) else {}
    positive_control = other.get("positive_control_producer")
    positive_control = positive_control if isinstance(positive_control, dict) else {}
    capability_whitelist = firewall.get("capability_whitelist")
    capability_whitelist = capability_whitelist if isinstance(capability_whitelist, dict) else {}
    evaluator_only_fields = {"family_id", "split", "order", "latent_rule", "heldout_label"}
    if (
        firewall.get("interface_audit_required") is not True
        or firewall.get("trace_only_schema_required") is not True
        or not evaluator_only_fields.issubset(set(capability_whitelist.get("forbidden") or []))
        or set(other.get("evaluator_only_fields") or []) != evaluator_only_fields
        or other.get("uncertainty_before_calibration") != "TRACE_ONLY_CANNOT_SUPPORT_PRESENT_BOUNDED"
        or other.get("stop_condition_kind") != "CONTENT_BASED_NOT_ELAPSED_TIME"
        or positive_control
        != {
            "candidate_blind_review": True,
            "independent_bank_boundary": True,
            "independent_module": True,
            "k0r_may_be_sole_positive_control": False,
        }
    ):
        errors.append(
            _new_error(
                "red_field_other_required_fields_invalid",
                "Calibration, firewall, independent positive control, and content-based stop fields must remain frozen.",
            )
        )

    return {
        "producer_function": "validate_red_field_contract",
        "validation_errors": errors,
        "validation_warnings": warnings,
        "verdict": "pass" if not errors else "fail",
    }


def _extract_machine_claim_ceiling(card_text: str) -> Any:
    start_marker = "<!-- MACHINE_CLAIM_CEILING_BEGIN -->"
    end_marker = "<!-- MACHINE_CLAIM_CEILING_END -->"
    if card_text.count(start_marker) != 1 or card_text.count(end_marker) != 1:
        raise ValueError("machine claim-ceiling markers must each occur exactly once")
    block = card_text.split(start_marker, 1)[1].split(end_marker, 1)[0].strip()
    if not block.startswith("```json") or not block.endswith("```"):
        raise ValueError("machine claim-ceiling block must be a fenced JSON object")
    return json.loads(block[len("```json") : -len("```")].strip())


def validate_red_field_correction_contract(
    correction_payload: Any,
    base_contract_payload: Any,
    *,
    card_claim_ceiling: Any = None,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if not isinstance(correction_payload, dict):
        errors.append(
            _new_error(
                "red_field_correction_contract_not_object",
                "The committed Red-field correction contract must be a JSON object.",
            )
        )
        correction_payload = {}
    if not isinstance(base_contract_payload, dict):
        errors.append(
            _new_error(
                "red_field_correction_base_contract_not_object",
                "The pinned original Red-field contract must be available for cross-contract validation.",
            )
        )
        base_contract_payload = {}

    if correction_payload.get("task_id") != state_machine.K0_RED_FIELD_CORRECTION_PIN["task_id"]:
        errors.append(
            _new_error(
                "red_field_correction_task_id_mismatch",
                "The correction task id must match its committed-object pin.",
                expected=state_machine.K0_RED_FIELD_CORRECTION_PIN["task_id"],
                actual=correction_payload.get("task_id"),
            )
        )
    base_result = validate_red_field_contract(base_contract_payload)
    if base_result["validation_errors"]:
        errors.append(
            _new_error(
                "red_field_correction_base_contract_invalid",
                "The correction cannot enforce over an invalid original Red-field contract.",
                base_error_codes=[error["code"] for error in base_result["validation_errors"]],
            )
        )

    expected_overlay = {
        "base_contract_path": state_machine.K0_RED_FIELD_CONTRACT_PATH,
        "base_task_id": state_machine.K0_RED_FIELD_ADDENDUM_PIN["task_id"],
        "both_committed_object_gates_required": True,
        "non_conflicting_base_constraints_remain_binding": True,
        "precedence": "correction_controls_only_conflicting_terminal_formula_power_coverage_rng_and_claim_ceiling_fields",
    }
    if correction_payload.get("additive_overlay") != expected_overlay:
        errors.append(
            _new_error(
                "red_field_correction_overlay_invalid",
                "The correction must remain an additive overlay over the exact original contract.",
            )
        )

    # C1: the V_special mapping is exhaustive and never converts inconclusive to presence or absence.
    expected_v_special = {
        "ABSENT_if": [
            "any_referenced_component_ABSENT",
            "powered_shortcut_parity_or_saturation",
            "powered_rival_parity_or_saturation",
            "candidate_CONTROL_DOMINATED",
            "candidate_RIVAL_DOMINATED",
        ],
        "INVALID_INSTRUMENT_if": [
            "required_comparison_underpowered",
            "required_integrity_dependency_invalid",
            "any_referenced_component_INVALID_INSTRUMENT",
        ],
        "PRESENT_BOUNDED_requires": [
            "all_referenced_component_evidence_admissible_and_PRESENT_BOUNDED",
            "CONTROL_SEPARATED",
            "RIVAL_SEPARATED",
            "all_integrity_dependencies_valid",
        ],
        "inconclusive_maps_to_absent_or_present": False,
        "producer_function": "resolve_v_special_terminal_state",
    }
    if correction_payload.get("v_special_terminal_mapping") != expected_v_special:
        errors.append(
            _new_error(
                "red_field_correction_c1_v_special_invalid",
                "C1 V_special terminal semantics are incomplete or drifted.",
            )
        )

    # C2: derive granular causal contrasts from the pinned original arm/component map.
    base_mappings = base_contract_payload.get("component_control_mapping")
    base_mappings = base_mappings if isinstance(base_mappings, list) else []
    base_mapping_by_component = {
        row.get("component_id"): row
        for row in base_mappings
        if isinstance(row, dict) and isinstance(row.get("component_id"), str)
    }
    causal_components = list(state_machine.K0_RED_FIELD_COMPONENT_IDS[:-1])
    expected_contrast_catalog: list[dict[str, str]] = []
    for component_id in causal_components:
        for arm_id in base_mapping_by_component.get(component_id, {}).get("causal_arm_ids") or []:
            expected_contrast_catalog.append(
                {
                    "arm_id": arm_id,
                    "component_id": component_id,
                    "contrast_id": f"contrast_{arm_id}",
                }
            )
    contrast_catalog = correction_payload.get("causal_contrast_catalog")
    if contrast_catalog != expected_contrast_catalog:
        errors.append(
            _new_error(
                "red_field_correction_c2_contrast_catalog_invalid",
                "Every original causal arm must resolve to one frozen granular causal contrast.",
            )
        )
    contrast_ids = [row["contrast_id"] for row in expected_contrast_catalog]
    expected_formula_fields = {
        "component_id",
        "mandatory_causal_contrast_ids",
        "optional_causal_contrast_ids",
        "causal_aggregation_rule",
        "shortcut_panel_reduction_rule",
        "rival_panel_reduction_rule",
        "missing_arm_mapping",
        "invalid_dependency_precedence",
        "underpowered_precedence",
        "terminal_state_formula",
        "claim_emission_formula",
        "producer_function",
    }
    common_expected = {
        "causal_aggregation_rule": "AND_ALL_MANDATORY_CAUSAL_CONTRASTS_WITH_NO_POST_HOC_OPERATOR_SELECTION",
        "claim_emission_formula": "PRESENT_BOUNDED_ALWAYS_EMITS_ONLY_CANDIDATE_INTERNAL_CAUSAL_SIGNATURE;BOUNDED_CONTROL_NON_EQUIVALENCE_REQUIRES_CONTROL_SEPARATED;RIVAL_QUALIFIER_NEVER_ERASES_COMPONENT_EVIDENCE",
        "invalid_dependency_precedence": "INVALID_INSTRUMENT_BEFORE_ANY_EVIDENCE_OR_COMPARISON_TERMINAL",
        "missing_arm_mapping": "INVALID_INSTRUMENT",
        "optional_causal_contrast_ids": [],
        "producer_function": "resolve_component_terminal_state",
        "rival_panel_reduction_rule": "RIVAL_DOMINATED_IF_ANY_POWERED_RIVAL_SUPERIOR_ELSE_RIVAL_SATURATED_IF_ANY_POWERED_PARITY_OR_FROZEN_CEILING_SATURATION_ELSE_RIVAL_SEPARATED_IF_CANDIDATE_POWERED_SUPERIOR_TO_ALL_ELSE_RIVAL_INCONCLUSIVE",
        "shortcut_panel_reduction_rule": "CONTROL_DOMINATED_IF_ANY_POWERED_CONTROL_SUPERIOR_ELSE_CONTROL_EQUIVALENT_IF_ANY_POWERED_PARITY_OR_FROZEN_CEILING_SATURATION_ELSE_CONTROL_SEPARATED_IF_CANDIDATE_POWERED_SUPERIOR_TO_ALL_ELSE_CONTROL_INCONCLUSIVE",
        "terminal_state_formula": "INVALID_IF_MISSING_INVALID_OR_CAUSAL_UNDERPOWERED;PRESENT_BOUNDED_IF_ALL_MANDATORY_CAUSAL_EFFECTS;ABSENT_IF_ANY_MANDATORY_POWERED_NON_EFFECT;NOT_TESTED_IF_NO_REQUIRED_RUN_STARTED",
        "underpowered_precedence": "CAUSAL_TO_INVALID_INSTRUMENT_CONTROL_TO_CONTROL_INCONCLUSIVE_RIVAL_TO_RIVAL_INCONCLUSIVE_BEFORE_ABSENT_OR_SEPARATED",
    }
    formula_rows = correction_payload.get("component_verdict_formulas")
    formula_rows = formula_rows if isinstance(formula_rows, list) else []
    formula_error = [row.get("component_id") for row in formula_rows if isinstance(row, dict)] != list(
        state_machine.K0_RED_FIELD_COMPONENT_IDS
    )
    for row in formula_rows:
        if not isinstance(row, dict) or set(row) != expected_formula_fields:
            formula_error = True
            continue
        component_id = row["component_id"]
        expected_mandatory = (
            contrast_ids
            if component_id == "V_special"
            else [
                f"contrast_{arm_id}"
                for arm_id in base_mapping_by_component.get(component_id, {}).get("causal_arm_ids") or []
            ]
        )
        expected_row = dict(common_expected)
        expected_row.update(
            {
                "component_id": component_id,
                "mandatory_causal_contrast_ids": expected_mandatory,
            }
        )
        if component_id == "V_special":
            expected_row.update(
                {
                    "causal_aggregation_rule": "ALL_REFERENCED_COMPONENTS_PRESENT_BOUNDED",
                    "claim_emission_formula": "PANEL_RELATIVE_SPECIALNESS_ONLY_IF_PRESENT_BOUNDED_WITH_CONTROL_SEPARATED_AND_RIVAL_SEPARATED;NO_CLAIM_FOR_ABSENT_INVALID_INSTRUMENT_OR_NOT_TESTED",
                    "terminal_state_formula": "PRESENT_BOUNDED_IFF_ALL_REFERENCED_COMPONENTS_PRESENT_BOUNDED_AND_CONTROL_SEPARATED_AND_RIVAL_SEPARATED_AND_ALL_INTEGRITY_VALID;ABSENT_IF_ANY_REFERENCED_COMPONENT_ABSENT_OR_POWERED_CONTROL_EQUIVALENT_OR_CONTROL_DOMINATED_OR_RIVAL_SATURATED_OR_RIVAL_DOMINATED;INVALID_IF_REQUIRED_COMPARISON_UNDERPOWERED_OR_REQUIRED_INTEGRITY_OR_REFERENCED_COMPONENT_INVALID;NOT_TESTED_IF_REQUIRED_RUN_NOT_STARTED",
                }
            )
        if row != expected_row:
            formula_error = True
    if formula_error or len(formula_rows) != len(state_machine.K0_RED_FIELD_COMPONENT_IDS):
        errors.append(
            _new_error(
                "red_field_correction_c2_component_formulas_invalid",
                "C2 requires six exact, resolved, fail-closed component formula rows.",
            )
        )
    formula_contrast_refs = {
        contrast_id
        for row in formula_rows
        if isinstance(row, dict)
        for field in ("mandatory_causal_contrast_ids", "optional_causal_contrast_ids")
        for contrast_id in (row.get(field) or [])
    }
    if formula_contrast_refs != set(contrast_ids):
        errors.append(
            _new_error(
                "red_field_correction_c2_unused_or_unresolved_contrast",
                "Every correction contrast must be used and every formula reference must resolve.",
                unused=sorted(set(contrast_ids) - formula_contrast_refs),
                unresolved=sorted(formula_contrast_refs - set(contrast_ids)),
            )
        )

    # C3: superiority has its own terminal; CONTROL_BETTER is not an equivalence subtype.
    expected_terminal_schema = {
        "comparison_state": list(state_machine.K0_RED_FIELD_CORRECTED_RIVAL_STATES),
        "control_comparison_state": list(state_machine.K0_RED_FIELD_CORRECTED_CONTROL_STATES),
        "control_equivalence_type": list(state_machine.K0_RED_FIELD_CORRECTED_CONTROL_EQUIVALENCE_TYPES),
        "evidence_state": list(state_machine.K0_RED_FIELD_EVIDENCE_STATES),
        "fourth_verdict_axis_forbidden": True,
        "terminal_rules": {
            "candidate_powered_superiority": "STAR_SEPARATED",
            "control_or_rival_powered_superiority": "STAR_DOMINATED",
            "powered_parity_or_preregistered_ceiling_saturation": "CONTROL_EQUIVALENT_OR_RIVAL_SATURATED",
            "underpowered": "STAR_INCONCLUSIVE",
        },
    }
    terminal_schema = correction_payload.get("effective_terminal_schema")
    enum_unique = isinstance(terminal_schema, dict) and all(
        isinstance(terminal_schema.get(field), list)
        and len(terminal_schema[field]) == len({json.dumps(value) for value in terminal_schema[field]})
        for field in ("comparison_state", "control_comparison_state", "control_equivalence_type", "evidence_state")
    )
    if terminal_schema != expected_terminal_schema or not enum_unique:
        errors.append(
            _new_error(
                "red_field_correction_c3_terminal_schema_invalid",
                "C3 effective terminals, uniqueness, and superiority semantics are incomplete or drifted.",
            )
        )

    # C4: absence is a powered decision, never failure-to-reject.
    expected_absence = {
        "causal_underpowered_mapping": "INVALID_INSTRUMENT",
        "covered_causal_contrast_ids": contrast_ids,
        "failure_to_reject_effect_is_absence": False,
        "powered_absence_required_fields": [
            "valid_full_arm",
            "valid_intervention_arm",
            "frozen_equivalence_or_noninferiority_decision",
            "computed_power_at_sesoi",
            "target_power",
            "power_target_met",
        ],
        "powered_non_effect_required_for": [
            "every_causal_ablation_no_effect_mapping",
            "every_evidence_state_ABSENT_decision",
        ],
    }
    if correction_payload.get("causal_absence_contract") != expected_absence:
        errors.append(
            _new_error(
                "red_field_correction_c4_powered_absence_invalid",
                "C4 causal absence must be frozen, powered, and exhaustive over all causal contrasts.",
            )
        )

    # C5: coverage is closed over the pinned base assignments/mappings and both contrast catalogs.
    expected_coverage = {
        "all_arm_assignments_must_be_covered": True,
        "all_component_mapped_arms_must_be_covered": True,
        "all_contrast_ids_source": [
            "original_addendum.comparison_catalog",
            "correction.causal_contrast_catalog",
        ],
        "all_integrity_controls_must_have_detector_signatures": True,
        "arm_assignment_ids_source": "original_addendum.arm_role_contract.assignments[*].arm_id",
        "component_mapped_arm_ids_source": "original_addendum.component_control_mapping[*].*_arm_ids",
        "integrity_control_ids_source": "original_addendum.arm_role_contract.assignments[arm_role=INTEGRITY_CONTROL].arm_id",
        "orphan_arm_mapping": "INVALID_INSTRUMENT",
        "required_artifact": "control_signature_coverage_report.json",
        "required_report_fields": [
            "arm_id",
            "arm_role",
            "component_ids",
            "contrast_ids",
            "simulation_case_ids",
            "expected_sign_ids",
            "coverage_status",
            "producer_function",
            "input_hashes",
            "run_id",
            "aggregation_rule",
            "code_path_hash",
        ],
        "required_simulation_cases_per_contrast": [
            "parity",
            "strong_negative",
            "survival_positive",
            "boundary_failure",
        ],
        "unused_contrast_mapping": "INVALID_INSTRUMENT",
    }
    assignments = base_contract_payload.get("arm_role_contract", {}).get("assignments")
    assignments = assignments if isinstance(assignments, list) else []
    assigned_arm_ids = {
        row.get("arm_id") for row in assignments if isinstance(row, dict) and isinstance(row.get("arm_id"), str)
    }
    mapped_arm_ids = {
        arm_id
        for row in base_mappings
        if isinstance(row, dict)
        for field in ("causal_arm_ids", "shortcut_control_arm_ids", "rival_arm_ids", "integrity_control_arm_ids")
        for arm_id in (row.get(field) or [])
    }
    integrity_arm_ids = {
        row.get("arm_id")
        for row in assignments
        if isinstance(row, dict) and row.get("arm_role") == "INTEGRITY_CONTROL"
    }
    original_catalog = base_contract_payload.get("comparison_catalog")
    original_catalog = original_catalog if isinstance(original_catalog, dict) else {}
    original_contrast_ids = {
        contrast_id
        for values in original_catalog.values()
        if isinstance(values, list)
        for contrast_id in values
    }
    if (
        correction_payload.get("exhaustive_signature_coverage") != expected_coverage
        or not assigned_arm_ids
        or assigned_arm_ids != mapped_arm_ids
        or not integrity_arm_ids
        or not original_contrast_ids
        or not contrast_ids
    ):
        errors.append(
            _new_error(
                "red_field_correction_c5_exhaustive_coverage_invalid",
                "C5 must close coverage over every original assignment, mapped arm, integrity control, and contrast.",
                orphan_assignments=sorted(assigned_arm_ids - mapped_arm_ids),
                orphan_mappings=sorted(mapped_arm_ids - assigned_arm_ids),
            )
        )

    # C6: every source has restore evidence and two independent recomputes.
    expected_rng = {
        "distinct_fresh_process_recompute_records_required": 2,
        "distinct_pid_required": True,
        "distinct_temp_dir_required": True,
        "fresh_process_record_required_fields": [
            "process_index",
            "pid",
            "temp_dir_hash",
            "launcher_code_hash",
            "pythonhashseed_commitment",
            "serialized_state_hash",
            "observation_hash",
            "checkpoint_hash",
            "config_hash",
            "output_hash",
        ],
        "original_run_counts_as_recompute": False,
        "required_rng_source_ids_source": "original_addendum.determinism_contract.rng_registry",
        "rng_entry_required_fields": [
            "source_id",
            "library",
            "namespace",
            "seed_input_ids",
            "seed_derivation_function",
            "derived_seed_or_commitment",
            "device_id",
            "worker_id",
            "initial_state_hash",
            "serialized_state_hash",
            "restored_state_hash",
            "used_by_code_path_ids",
            "restore_verdict",
        ],
    }
    base_rng_sources = base_contract_payload.get("determinism_contract", {}).get("rng_registry")
    if (
        correction_payload.get("rng_evidence_contract") != expected_rng
        or not isinstance(base_rng_sources, list)
        or not base_rng_sources
        or len(base_rng_sources) != len(set(base_rng_sources))
    ):
        errors.append(
            _new_error(
                "red_field_correction_c6_rng_evidence_invalid",
                "C6 per-source RNG and distinct fresh-process evidence fields are incomplete or drifted.",
            )
        )

    # C7: future H0 must choose exactly one ex-ante seed design with callable power provenance.
    expected_power = {
        "computed_mde_power_required_fields": [
            "producer_function",
            "input_artifact_hashes",
            "run_id",
            "seed_block_id",
            "aggregation_rule",
            "code_path_hash",
        ],
        "exactly_one_seed_design_required": True,
        "fixed_seed_design_required_fields": ["fixed_seed_count", "frozen_seed_block_id"],
        "forbidden": [
            "null_fixed_count_plus_ambiguous_sequential_prose",
            "hand_written_computed_power_or_mde",
            "post_result_n_extension",
        ],
        "sequential_seed_design_required_fields": [
            "sequential_schedule_id",
            "analysis_looks",
            "max_n",
            "alpha_spending_rule",
            "stopping_predicate",
            "seed_release_order",
        ],
    }
    if correction_payload.get("power_design_provenance") != expected_power:
        errors.append(
            _new_error(
                "red_field_correction_c7_power_design_invalid",
                "C7 seed-design exclusivity and computed power/MDE provenance are incomplete or drifted.",
            )
        )

    # C8: the card and machine contract must carry the same exact single allowed claim and forbidden list.
    claim_ceiling = correction_payload.get("claim_ceiling")
    claim_unique = isinstance(claim_ceiling, dict) and all(
        isinstance(claim_ceiling.get(field), list)
        and len(claim_ceiling[field]) == len(set(claim_ceiling[field]))
        for field in ("allowed", "forbidden")
    )
    if (
        claim_ceiling != state_machine.K0_RED_FIELD_CORRECTION_CLAIM_CEILING
        or not claim_unique
        or (card_claim_ceiling is not None and card_claim_ceiling != claim_ceiling)
    ):
        errors.append(
            _new_error(
                "red_field_correction_c8_claim_ceiling_invalid",
                "C8 machine/card claim ceilings must exact-match the frozen allowed and forbidden lists.",
            )
        )

    return {
        "producer_function": "validate_red_field_correction_contract",
        "validation_errors": errors,
        "validation_warnings": warnings,
        "verdict": "pass" if not errors else "fail",
    }


def _git_output(repo_root: Path, *args: str, text: bool = True) -> str | bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=text,
        timeout=10,
    )
    return completed.stdout.strip() if text else completed.stdout


def _git_is_ancestor(repo_root: Path, ancestor: str, descendant: str = "HEAD") -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=repo_root,
        check=False,
        capture_output=True,
        timeout=10,
    )
    return completed.returncode == 0


def validate_red_field_addendum_repository(
    *,
    repo_root: Path,
    route_state_payload: Any,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    input_artifacts = [
        state_machine.K0_RED_FIELD_ADDENDUM_CARD_PATH,
        state_machine.K0_RED_FIELD_CONTRACT_PATH,
    ]
    if not isinstance(route_state_payload, dict):
        errors.append(
            _new_error(
                "red_field_route_state_missing",
                "The K0 route state is required for committed-object Red-field validation.",
            )
        )
        route_state_payload = {}
    pin = route_state_payload.get("red_field_addendum_pin")
    if pin != state_machine.K0_RED_FIELD_ADDENDUM_PIN:
        errors.append(
            _new_error(
                "red_field_addendum_pin_mismatch",
                "The serialized addendum pin must equal the frozen Phase A committed-object pin.",
                expected=state_machine.K0_RED_FIELD_ADDENDUM_PIN,
                actual=pin,
            )
        )
        pin = pin if isinstance(pin, dict) else {}

    bank_commit = pin.get("bank_commit")
    card_path = pin.get("card_path")
    contract_path = pin.get("contract_path")
    try:
        head = str(_git_output(repo_root, "rev-parse", "HEAD"))
    except (OSError, subprocess.SubprocessError) as exc:
        errors.append(
            _new_error(
                "red_field_git_readback_failed",
                "Git HEAD could not be read for the Red-field ancestry gate.",
                error=str(exc),
            )
        )
        head = ""

    if not isinstance(bank_commit, str) or not _git_is_ancestor(repo_root, bank_commit, head or "HEAD"):
        errors.append(
            _new_error(
                "red_field_bank_commit_not_ancestor",
                "The Phase A addendum bank commit must be an ancestor of the current Phase B validation HEAD.",
                bank_commit=bank_commit,
                validation_head=head,
            )
        )

    contract_payload: Any = None
    if isinstance(bank_commit, str) and isinstance(card_path, str) and isinstance(contract_path, str):
        try:
            actual_card_blob = str(_git_output(repo_root, "rev-parse", f"{bank_commit}:{card_path}"))
            actual_contract_blob = str(_git_output(repo_root, "rev-parse", f"{bank_commit}:{contract_path}"))
            contract_bytes = _git_output(repo_root, "cat-file", "blob", actual_contract_blob, text=False)
            assert isinstance(contract_bytes, bytes)
            actual_contract_sha256 = hashlib.sha256(contract_bytes).hexdigest()
            contract_payload = json.loads(contract_bytes.decode("utf-8"))
        except (AssertionError, UnicodeDecodeError, json.JSONDecodeError, OSError, subprocess.SubprocessError) as exc:
            errors.append(
                _new_error(
                    "red_field_committed_object_readback_failed",
                    "The Phase A card/contract committed objects could not be read and parsed.",
                    error=str(exc),
                )
            )
        else:
            actual = {
                "card_blob": actual_card_blob,
                "contract_blob": actual_contract_blob,
                "contract_sha256": actual_contract_sha256,
            }
            expected = {
                key: pin.get(key)
                for key in ("card_blob", "contract_blob", "contract_sha256")
            }
            if actual != expected:
                errors.append(
                    _new_error(
                        "red_field_committed_object_pin_drift",
                        "Committed card blob, contract blob, and contract SHA-256 must match the serialized pin.",
                        expected=expected,
                        actual=actual,
                    )
                )

    contract_result = validate_red_field_contract(contract_payload)
    errors.extend(contract_result["validation_errors"])
    warnings.extend(contract_result["validation_warnings"])
    return {
        "producer_function": "validate_red_field_addendum_repository",
        "input_artifacts": input_artifacts,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "verdict": "pass" if not errors else "fail",
    }


def validate_red_field_correction_repository(
    *,
    repo_root: Path,
    route_state_payload: Any,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    input_artifacts = [
        state_machine.K0_RED_FIELD_ADDENDUM_CARD_PATH,
        state_machine.K0_RED_FIELD_CONTRACT_PATH,
        state_machine.K0_RED_FIELD_CORRECTION_CARD_PATH,
        state_machine.K0_RED_FIELD_CORRECTION_CONTRACT_PATH,
    ]
    if not isinstance(route_state_payload, dict):
        errors.append(
            _new_error(
                "red_field_correction_route_state_missing",
                "The K0 route state is required for correction committed-object validation.",
            )
        )
        route_state_payload = {}

    if route_state_payload.get("red_field_addendum_pin") != state_machine.K0_RED_FIELD_ADDENDUM_PIN:
        errors.append(
            _new_error(
                "red_field_correction_original_addendum_pin_missing_or_drifted",
                "The correction cannot replace or remove the exact original Red-field addendum pin.",
            )
        )

    pin = route_state_payload.get("red_field_correction_pin")
    if pin != state_machine.K0_RED_FIELD_CORRECTION_PIN:
        errors.append(
            _new_error(
                "red_field_correction_pin_mismatch",
                "The serialized correction pin must equal the frozen Phase A committed-object pin.",
                expected=state_machine.K0_RED_FIELD_CORRECTION_PIN,
                actual=pin,
            )
        )
        pin = pin if isinstance(pin, dict) else {}

    bank_commit = pin.get("bank_commit")
    card_path = pin.get("card_path")
    contract_path = pin.get("contract_path")
    try:
        head = str(_git_output(repo_root, "rev-parse", "HEAD"))
    except (OSError, subprocess.SubprocessError) as exc:
        errors.append(
            _new_error(
                "red_field_correction_git_readback_failed",
                "Git HEAD could not be read for the correction ancestry gate.",
                error=str(exc),
            )
        )
        head = ""
    if not isinstance(bank_commit, str) or not _git_is_ancestor(repo_root, bank_commit, head or "HEAD"):
        errors.append(
            _new_error(
                "red_field_correction_bank_commit_not_ancestor",
                "The correction bank commit must be an ancestor of the Phase B validation HEAD.",
                bank_commit=bank_commit,
                validation_head=head,
            )
        )

    correction_payload: Any = None
    base_contract_payload: Any = None
    card_claim_ceiling: Any = None
    if isinstance(bank_commit, str) and isinstance(card_path, str) and isinstance(contract_path, str):
        try:
            actual_card_blob = str(_git_output(repo_root, "rev-parse", f"{bank_commit}:{card_path}"))
            actual_contract_blob = str(_git_output(repo_root, "rev-parse", f"{bank_commit}:{contract_path}"))
            card_bytes = _git_output(repo_root, "cat-file", "blob", actual_card_blob, text=False)
            contract_bytes = _git_output(repo_root, "cat-file", "blob", actual_contract_blob, text=False)
            base_contract_bytes = _git_output(
                repo_root,
                "cat-file",
                "blob",
                state_machine.K0_RED_FIELD_ADDENDUM_PIN["contract_blob"],
                text=False,
            )
            assert isinstance(card_bytes, bytes)
            assert isinstance(contract_bytes, bytes)
            assert isinstance(base_contract_bytes, bytes)
            actual_contract_sha256 = hashlib.sha256(contract_bytes).hexdigest()
            correction_payload = json.loads(contract_bytes.decode("utf-8"))
            base_contract_payload = json.loads(base_contract_bytes.decode("utf-8"))
            card_claim_ceiling = _extract_machine_claim_ceiling(card_bytes.decode("utf-8"))
        except (
            AssertionError,
            UnicodeDecodeError,
            ValueError,
            json.JSONDecodeError,
            OSError,
            subprocess.SubprocessError,
        ) as exc:
            errors.append(
                _new_error(
                    "red_field_correction_committed_object_readback_failed",
                    "The correction card/contract or original contract could not be read and parsed from committed objects.",
                    error=str(exc),
                )
            )
        else:
            actual = {
                "card_blob": actual_card_blob,
                "contract_blob": actual_contract_blob,
                "contract_sha256": actual_contract_sha256,
            }
            expected = {key: pin.get(key) for key in ("card_blob", "contract_blob", "contract_sha256")}
            if actual != expected:
                errors.append(
                    _new_error(
                        "red_field_correction_committed_object_pin_drift",
                        "Committed correction card/contract objects and SHA-256 must match the serialized pin.",
                        expected=expected,
                        actual=actual,
                    )
                )

    contract_result = validate_red_field_correction_contract(
        correction_payload,
        base_contract_payload,
        card_claim_ceiling=card_claim_ceiling,
    )
    errors.extend(contract_result["validation_errors"])
    warnings.extend(contract_result["validation_warnings"])
    return {
        "producer_function": "validate_red_field_correction_repository",
        "input_artifacts": input_artifacts,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "verdict": "pass" if not errors else "fail",
    }


def _forbidden_current_frontier_authorizations(
    *,
    program_state_payload: dict[str, Any],
    route_state_payload: dict[str, Any],
) -> list[str]:
    found: set[str] = set()

    authorizations = route_state_payload.get("authorizations")
    if isinstance(authorizations, dict):
        for key in state_machine.CURRENT_FRONTIER_FORBIDDEN_AUTHORIZATIONS:
            if _is_authorizing_value(authorizations.get(key)):
                found.add(key)

    route_allowed_actions = route_state_payload.get("allowed_next_actions")
    program_allowed_actions = program_state_payload.get("allowed_next_actions")
    for action in _string_values(route_allowed_actions) + _string_values(program_allowed_actions):
        normalized = action.lower().replace("-", "_")
        for token in state_machine.CURRENT_FRONTIER_FORBIDDEN_ACTION_TOKENS:
            if token in normalized:
                found.add(token)

    return sorted(found)


def validate_route_payload(
    *,
    route_id: str,
    state_payload: dict[str, Any] | None,
    closure_payload: dict[str, Any] | None,
    changed_files: list[str] | None = None,
    authorized_paths: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if not isinstance(state_payload, dict):
        errors.append(_new_error("missing_or_invalid_state_json", "state.json must be a JSON object."))
        state_payload = {}

    current_state = state_payload.get("current_state")
    if current_state not in state_machine.ROUTE_STATES:
        errors.append(
            _new_error(
                "invalid_current_state",
                "Route current_state is not in the frozen enum.",
                current_state=current_state,
                valid_states=list(state_machine.ROUTE_STATES),
            )
        )

    state_route_id = state_payload.get("route_id")
    if state_route_id and state_route_id != route_id:
        warnings.append(
            _new_error(
                "state_route_id_mismatch",
                "state.json route_id differs from directory route_id.",
                state_route_id=state_route_id,
                directory_route_id=route_id,
            )
        )

    if route_id == state_machine.K0_PARENT_ROUTE_ID:
        if current_state not in ("REGISTERED", "READY_TO_IMPLEMENT"):
            errors.append(
                _new_error(
                    "k0_parent_state_outside_authorized_contract",
                    "The K0 parent contract permits only REGISTERED or the separately carded READY_TO_IMPLEMENT boundary.",
                    current_state=current_state,
                )
            )
        if closure_payload is not None:
            errors.append(
                _new_error(
                    "k0_parent_has_unexpected_closure",
                    "The K0 parent must not have a closure packet at REGISTERED or READY_TO_IMPLEMENT.",
                )
            )

        authorizations = state_payload.get("authorizations")
        allowed_actions = state_payload.get("allowed_next_actions")
        source_readback = state_payload.get("source_readback")
        ledger_readback = source_readback.get("ledger") if isinstance(source_readback, dict) else None

        if current_state == "REGISTERED":
            if state_payload.get("implementation_authorized") is not False:
                errors.append(
                    _new_error(
                        "k0_registered_parent_implementation_not_explicitly_false",
                        "The registered K0 parent must set implementation_authorized to false.",
                    )
                )
            invalid_authorizations = [
                key
                for key in state_machine.K0_PARENT_REQUIRED_FALSE_AUTHORIZATIONS
                if not isinstance(authorizations, dict) or authorizations.get(key) is not False
            ]
            if invalid_authorizations:
                errors.append(
                    _new_error(
                        "k0_registered_parent_forbidden_authorization",
                        "Every registered K0 parent implementation, runtime, claim, and publication authorization must be explicit false.",
                        invalid_or_missing=invalid_authorizations,
                    )
                )
            if not isinstance(allowed_actions, list) or set(allowed_actions) != set(
                state_machine.K0_PARENT_ALLOWED_ACTIONS
            ):
                errors.append(
                    _new_error(
                        "k0_registered_parent_allowed_actions_mismatch",
                        "The registered K0 parent may only authorize child-card banking and route validation.",
                        expected=list(state_machine.K0_PARENT_ALLOWED_ACTIONS),
                        actual=allowed_actions,
                    )
                )
            expected_ledger_prefix = state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX
        else:
            if state_payload.get("implementation_authorized") is not True:
                errors.append(
                    _new_error(
                        "k0_ready_implementation_authorization_not_explicitly_true",
                        "READY_TO_IMPLEMENT must explicitly authorize only the frozen first-pair targets.",
                    )
                )
            if state_payload.get("phase") != state_machine.K0_READY_PHASE:
                errors.append(
                    _new_error(
                        "k0_ready_phase_mismatch",
                        "The READY_TO_IMPLEMENT boundary must use the frozen first-pair phase.",
                        expected=state_machine.K0_READY_PHASE,
                        actual=state_payload.get("phase"),
                    )
                )
            invalid_true_authorizations = [
                key
                for key in state_machine.K0_READY_REQUIRED_TRUE_AUTHORIZATIONS
                if not isinstance(authorizations, dict) or authorizations.get(key) is not True
            ]
            invalid_false_authorizations = [
                key
                for key in state_machine.K0_READY_REQUIRED_FALSE_AUTHORIZATIONS
                if not isinstance(authorizations, dict) or authorizations.get(key) is not False
            ]
            expected_authorization_keys = set(state_machine.K0_PARENT_REQUIRED_FALSE_AUTHORIZATIONS)
            actual_authorization_keys = set(authorizations) if isinstance(authorizations, dict) else set()
            if (
                invalid_true_authorizations
                or invalid_false_authorizations
                or actual_authorization_keys != expected_authorization_keys
            ):
                errors.append(
                    _new_error(
                        "k0_ready_authorizations_mismatch",
                        "READY_TO_IMPLEMENT may authorize Foundation and H0 only; every other authorization must remain explicit false.",
                        invalid_true=invalid_true_authorizations,
                        invalid_false=invalid_false_authorizations,
                        unexpected_or_missing_keys=sorted(actual_authorization_keys ^ expected_authorization_keys),
                    )
                )
            if allowed_actions != list(state_machine.K0_READY_ALLOWED_ACTIONS):
                errors.append(
                    _new_error(
                        "k0_ready_allowed_actions_mismatch",
                        "The READY_TO_IMPLEMENT boundary must expose only the frozen first-pair actions and validation.",
                        expected=list(state_machine.K0_READY_ALLOWED_ACTIONS),
                        actual=allowed_actions,
                    )
                )
            if state_payload.get("authorized_implementation_targets") != list(
                state_machine.K0_READY_AUTHORIZED_IMPLEMENTATION_TARGETS
            ):
                errors.append(
                    _new_error(
                        "k0_ready_implementation_targets_mismatch",
                        "The READY_TO_IMPLEMENT boundary must name exactly Foundation and H0 in frozen order.",
                        expected=list(state_machine.K0_READY_AUTHORIZED_IMPLEMENTATION_TARGETS),
                        actual=state_payload.get("authorized_implementation_targets"),
                    )
                )
            if state_payload.get("child_authorizations") != state_machine.K0_READY_CHILD_AUTHORIZATIONS:
                errors.append(
                    _new_error(
                        "k0_ready_child_authorizations_mismatch",
                        "The child authorization map must contain exactly two true and four false frozen child entries.",
                        expected=state_machine.K0_READY_CHILD_AUTHORIZATIONS,
                        actual=state_payload.get("child_authorizations"),
                    )
                )
            if not isinstance(source_readback, dict) or source_readback.get(
                "child_card_banks"
            ) != state_machine.K0_READY_CHILD_CARD_BANKS:
                errors.append(
                    _new_error(
                        "k0_ready_child_card_commit_pins_mismatch",
                        "The first-pair transition must pin the three frozen child-bank commits.",
                        expected=state_machine.K0_READY_CHILD_CARD_BANKS,
                        actual=source_readback.get("child_card_banks") if isinstance(source_readback, dict) else None,
                    )
                )
            if not isinstance(source_readback, dict) or source_readback.get("banked_card_objects") != list(
                state_machine.K0_READY_BANKED_CARD_OBJECTS
            ):
                errors.append(
                    _new_error(
                        "k0_ready_banked_card_object_readback_mismatch",
                        "The first-pair transition must carry the exact six-card commit/path/blob readback.",
                        expected=list(state_machine.K0_READY_BANKED_CARD_OBJECTS),
                        actual=source_readback.get("banked_card_objects") if isinstance(source_readback, dict) else None,
                    )
                )
            if not isinstance(source_readback, dict) or source_readback.get(
                "transition_card"
            ) != state_machine.K0_READY_TRANSITION_CARD_PATH:
                errors.append(
                    _new_error(
                        "k0_ready_transition_card_mismatch",
                        "The READY_TO_IMPLEMENT boundary must cite its separate bounded transition card.",
                        expected=state_machine.K0_READY_TRANSITION_CARD_PATH,
                        actual=source_readback.get("transition_card") if isinstance(source_readback, dict) else None,
                    )
                )
            red_field_pin = state_payload.get("red_field_addendum_pin")
            if red_field_pin is None:
                errors.append(
                    _new_error(
                        "k0_red_field_addendum_pin_missing",
                        "READY_TO_IMPLEMENT H0 authorization requires the banked Red-field addendum pin.",
                    )
                )
            elif red_field_pin != state_machine.K0_RED_FIELD_ADDENDUM_PIN:
                errors.append(
                    _new_error(
                        "k0_red_field_addendum_pin_mismatch",
                        "The Red-field addendum pin must equal the frozen Phase A committed-object pin.",
                        expected=state_machine.K0_RED_FIELD_ADDENDUM_PIN,
                        actual=red_field_pin,
                    )
                )
            red_field_correction_pin = state_payload.get("red_field_correction_pin")
            if red_field_correction_pin is None:
                errors.append(
                    _new_error(
                        "k0_red_field_correction_pin_missing",
                        "READY_TO_IMPLEMENT H0 authorization requires the banked Red-field correction pin.",
                    )
                )
            elif red_field_correction_pin != state_machine.K0_RED_FIELD_CORRECTION_PIN:
                errors.append(
                    _new_error(
                        "k0_red_field_correction_pin_mismatch",
                        "The Red-field correction pin must equal the frozen Phase A committed-object pin.",
                        expected=state_machine.K0_RED_FIELD_CORRECTION_PIN,
                        actual=red_field_correction_pin,
                    )
                )
            if (
                isinstance(state_payload.get("child_authorizations"), dict)
                and state_payload["child_authorizations"].get("ITL-K0-H0-H1-INSTRUMENT-001A:H0") is True
                and (
                    not isinstance(red_field_pin, dict)
                    or red_field_pin.get("red_field_gate_status") != "BANKED_AND_ENFORCED"
                    or not isinstance(red_field_correction_pin, dict)
                    or red_field_correction_pin.get("red_field_correction_gate_status")
                    != "BANKED_AND_ENFORCED"
                )
            ):
                errors.append(
                    _new_error(
                        "k0_h0_authorized_without_enforced_red_field_gate",
                        "H0 may remain true only when both exact Red-field gates are banked and enforced.",
                    )
                )
            expected_ledger_prefix = state_machine.K0_RED_FIELD_CORRECTION_LEDGER_ENTRY_PREFIX

        if not isinstance(ledger_readback, dict):
            errors.append(
                _new_error(
                    "k0_parent_ledger_declaration_missing",
                    "The K0 parent must declare its exact append-only ledger dependency.",
                )
            )
        else:
            if ledger_readback.get("path") != state_machine.K0_PARENT_LEDGER_PATH:
                errors.append(
                    _new_error(
                        "k0_parent_ledger_path_mismatch",
                        "The K0 parent ledger path must equal the frozen repo-relative path.",
                        expected=state_machine.K0_PARENT_LEDGER_PATH,
                        actual=ledger_readback.get("path"),
                    )
                )
            if ledger_readback.get("required_entry_prefix") != expected_ledger_prefix:
                errors.append(
                    _new_error(
                        "k0_parent_ledger_prefix_mismatch",
                        "The K0 parent ledger prefix must match its current frozen transition text.",
                        expected=expected_ledger_prefix,
                        actual=ledger_readback.get("required_entry_prefix"),
                    )
                )
            if current_state == "READY_TO_IMPLEMENT":
                expected_preserved_prefixes = [
                    state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX,
                    state_machine.K0_READY_LEDGER_ENTRY_PREFIX,
                    state_machine.K0_RED_FIELD_LEDGER_ENTRY_PREFIX,
                ]
                if ledger_readback.get("preserved_entry_prefixes") != expected_preserved_prefixes:
                    errors.append(
                        _new_error(
                            "k0_ready_preserved_ledger_prefix_mismatch",
                            "The corrected Red-field READY_TO_IMPLEMENT boundary must preserve L-020 through L-022.",
                            expected=expected_preserved_prefixes,
                            actual=ledger_readback.get("preserved_entry_prefixes"),
                        )
                    )
                if ledger_readback.get("preserved_entry_sha256") != state_machine.K0_RED_FIELD_PRESERVED_LEDGER_HASHES:
                    errors.append(
                        _new_error(
                            "k0_ready_preserved_ledger_hash_mismatch",
                            "The Red-field route must pin the exact full-line SHA-256 values for L-020 and L-021.",
                            expected=state_machine.K0_RED_FIELD_PRESERVED_LEDGER_HASHES,
                            actual=ledger_readback.get("preserved_entry_sha256"),
                        )
                    )

    if current_state == "CLOSURE_REVIEW_REQUIRED" and closure_payload is None:
        errors.append(
            _new_error(
                "closure_review_required_missing_closure_json",
                "CLOSURE_REVIEW_REQUIRED routes must include closure.json.",
            )
        )

    closure_type = None
    if closure_payload is not None:
        if not isinstance(closure_payload, dict):
            errors.append(_new_error("invalid_closure_json", "closure.json must be a JSON object."))
            closure_payload = {}

        closure_type = closure_payload.get("closure_type")
        if not closure_type:
            errors.append(_new_error("missing_closure_type", "closure.json must include closure_type."))
        elif closure_type not in state_machine.CLOSURE_TYPES:
            errors.append(
                _new_error(
                    "invalid_closure_type",
                    "closure_type is not in the frozen enum.",
                    closure_type=closure_type,
                    valid_closure_types=list(state_machine.CLOSURE_TYPES),
                )
            )

        if not _non_empty_string_list(closure_payload.get("allowed_next_actions")):
            errors.append(
                _new_error(
                    "missing_non_empty_allowed_next_actions",
                    "closure.json must include non-empty allowed_next_actions.",
                )
            )

        if not _non_empty_string_list(closure_payload.get("forbidden_next_actions")):
            errors.append(
                _new_error(
                    "missing_non_empty_forbidden_next_actions",
                    "closure.json must include non-empty forbidden_next_actions.",
                )
            )

        claim_ceiling = closure_payload.get("claim_ceiling")
        if not isinstance(claim_ceiling, dict) or not claim_ceiling.get("max"):
            errors.append(
                _new_error(
                    "missing_claim_ceiling_max",
                    "closure.json must include claim_ceiling.max.",
                )
            )

        evidence_status = closure_payload.get("evidence_status")
        if closure_type == "THEORY_PRESSURE":
            missing = [
                key
                for key in state_machine.REQUIRED_THEORY_PRESSURE_EVIDENCE
                if not isinstance(evidence_status, dict) or evidence_status.get(key) != "present"
            ]
            if missing:
                errors.append(
                    _new_error(
                        "theory_pressure_missing_required_evidence",
                        "THEORY_PRESSURE requires baseline, ablation, replay, and provenance marked present.",
                        missing_or_not_present=missing,
                    )
                )

        if closure_type == "INSTRUMENT_INVALID" and closure_payload.get("theory_pressure_authorized") is True:
            errors.append(
                _new_error(
                    "instrument_invalid_authorizes_theory_pressure",
                    "INSTRUMENT_INVALID closure cannot authorize theory pressure.",
                )
            )

        if closure_type == "ARTIFACT_ONLY" and closure_payload.get("mechanism_evidence_authorized") is True:
            errors.append(
                _new_error(
                    "artifact_only_authorizes_mechanism_evidence",
                    "ARTIFACT_ONLY closure cannot authorize mechanism evidence.",
                )
            )

        allowed_actions = closure_payload.get("allowed_next_actions")
        if closure_type == "IMPLEMENTATION_DEFECT" and isinstance(allowed_actions, list):
            normalized_actions = {str(action).strip() for action in allowed_actions}
            if "start_new_mechanism_route" in normalized_actions:
                errors.append(
                    _new_error(
                        "implementation_defect_allows_new_mechanism_route",
                        "IMPLEMENTATION_DEFECT cannot allow start_new_mechanism_route.",
                    )
                )

    if current_state == "CLOSURE_REVIEW_REQUIRED":
        blocked_changed_files = [
            _posix(path)
            for path in (changed_files or [])
            if is_roadmap_like_changed_file(path) and not _path_is_authorized(path, authorized_paths)
        ]
        if blocked_changed_files:
            errors.append(
                _new_error(
                    "unresolved_closure_with_roadmap_like_changed_file",
                    "Roadmap-like changed files are blocked while CLOSURE_REVIEW_REQUIRED is unresolved.",
                    changed_files=blocked_changed_files,
                )
            )

    return {
        "route_id": route_id,
        "current_state": current_state,
        "closure_type": closure_type,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "verdict": "pass" if not errors else "fail",
    }


def _parse_json_file(path: Path, errors: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append(_new_error("missing_state_json", "Route is missing state.json.", path=_posix(path)))
        return None
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        errors.append(_new_error("invalid_json", "JSON file could not be parsed.", path=_posix(path), error=str(exc)))
        return None
    if not isinstance(payload, dict):
        errors.append(_new_error("json_not_object", "JSON file must contain an object.", path=_posix(path)))
        return None
    return payload


def _route_input_artifacts(routes_dir: Path) -> list[str]:
    if not routes_dir.exists():
        return []
    artifacts: list[str] = []
    for path in sorted(routes_dir.glob("*/*")):
        if path.is_file():
            artifacts.append(path.relative_to(routes_dir).as_posix())
    return artifacts


def validate_k0_red_field_event(events_path: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    if not events_path.is_file():
        errors.append(
            _new_error(
                "k0_red_field_event_file_missing",
                "The K0 route events.jsonl file is required.",
                path=_posix(events_path),
            )
        )
    else:
        for line_number, line in enumerate(events_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    _new_error(
                        "k0_red_field_event_invalid_json",
                        "Every K0 route event line must be valid JSON.",
                        path=_posix(events_path),
                        line_number=line_number,
                        error=str(exc),
                    )
                )
                continue
            if not isinstance(payload, dict):
                errors.append(
                    _new_error(
                        "k0_red_field_event_not_object",
                        "Every K0 route event must be a JSON object.",
                        path=_posix(events_path),
                        line_number=line_number,
                    )
                )
                continue
            events.append(payload)

    matches = [event for event in events if event.get("event") == "red_field_addendum_banked_and_enforced"]
    if len(matches) != 1:
        errors.append(
            _new_error(
                "k0_red_field_event_missing_or_duplicate",
                "Exactly one Red-field bank/enforcement event must be appended.",
                match_count=len(matches),
                path=_posix(events_path),
            )
        )
    else:
        event = matches[0]
        if (
            event.get("route_id") != state_machine.K0_PARENT_ROUTE_ID
            or event.get("phase") != state_machine.K0_RED_FIELD_ADDENDUM_PHASE
            or event.get("current_state") != "READY_TO_IMPLEMENT"
            or event.get("red_field_addendum_pin") != state_machine.K0_RED_FIELD_ADDENDUM_PIN
            or event.get("foundation_authorized") is not True
            or event.get("h0_authorized_only_under_addendum") is not True
            or event.get("preserved_false_targets")
            != [
                "EGO-K0-REFERENCE-KERNEL-001A",
                "ITL-K0-H0-H1-INSTRUMENT-001A:H1",
                "K0-IMMUTABLE-FREEZE-001A",
                "ITL-K0-FORMAL-EVIDENCE-001A",
            ]
        ):
            errors.append(
                _new_error(
                    "k0_red_field_event_contract_mismatch",
                    "The Red-field route event must carry the exact state, phase, pin, and authorization boundary.",
                )
            )

    correction_matches = [
        event for event in events if event.get("event") == "red_field_semantic_correction_banked_and_enforced"
    ]
    if len(correction_matches) != 1:
        errors.append(
            _new_error(
                "k0_red_field_correction_event_missing_or_duplicate",
                "Exactly one Red-field semantic-correction bank/enforcement event must be appended.",
                match_count=len(correction_matches),
                path=_posix(events_path),
            )
        )
    else:
        event = correction_matches[0]
        if (
            event.get("route_id") != state_machine.K0_PARENT_ROUTE_ID
            or event.get("phase") != state_machine.K0_READY_PHASE
            or event.get("current_state") != "READY_TO_IMPLEMENT"
            or event.get("red_field_addendum_pin") != state_machine.K0_RED_FIELD_ADDENDUM_PIN
            or event.get("red_field_correction_pin") != state_machine.K0_RED_FIELD_CORRECTION_PIN
            or event.get("foundation_authorized") is not True
            or event.get("h0_authorized_only_under_both_red_gates") is not True
            or event.get("preserved_false_targets")
            != [
                "EGO-K0-REFERENCE-KERNEL-001A",
                "ITL-K0-H0-H1-INSTRUMENT-001A:H1",
                "K0-IMMUTABLE-FREEZE-001A",
                "ITL-K0-FORMAL-EVIDENCE-001A",
            ]
        ):
            errors.append(
                _new_error(
                    "k0_red_field_correction_event_contract_mismatch",
                    "The correction event must carry the exact phase, both pins, and preserved authorization boundary.",
                )
            )

    return {
        "producer_function": "validate_k0_red_field_event",
        "validation_errors": errors,
        "validation_warnings": [],
        "verdict": "pass" if not errors else "fail",
    }


def validate_routes_tree(
    *,
    routes_dir: Path,
    changed_files: list[str] | None = None,
    authorized_paths: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    route_results: list[dict[str, Any]] = []

    if not routes_dir.exists():
        errors.append(_new_error("missing_routes_dir", "Route artifact directory is missing.", path=_posix(routes_dir)))
        return {
            "producer_function": "validate_routes_tree",
            "route_count": 0,
            "routes": [],
            "input_artifacts": [],
            "changed_files": changed_files or [],
            "validation_errors": errors,
            "validation_warnings": warnings,
            "verdict": "fail",
        }

    route_dirs = sorted([path for path in routes_dir.iterdir() if path.is_dir()], key=lambda path: path.name)
    if not route_dirs:
        errors.append(_new_error("no_routes_found", "Route artifact directory contains no routes."))

    for route_dir in route_dirs:
        route_id = route_dir.name
        local_errors: list[dict[str, Any]] = []
        state_payload = _parse_json_file(route_dir / "state.json", local_errors)
        closure_path = route_dir / "closure.json"
        closure_payload: dict[str, Any] | None = None
        if closure_path.exists():
            try:
                loaded_closure = load_json(closure_path)
            except json.JSONDecodeError as exc:
                local_errors.append(
                    _new_error(
                        "invalid_json",
                        "JSON file could not be parsed.",
                        path=_posix(closure_path),
                        error=str(exc),
                    )
                )
            else:
                if isinstance(loaded_closure, dict):
                    closure_payload = loaded_closure
                else:
                    local_errors.append(
                        _new_error("json_not_object", "JSON file must contain an object.", path=_posix(closure_path))
                    )

        result = validate_route_payload(
            route_id=route_id,
            state_payload=state_payload,
            closure_payload=closure_payload,
            changed_files=changed_files,
            authorized_paths=authorized_paths,
        )
        if (
            route_id == state_machine.K0_PARENT_ROUTE_ID
            and isinstance(state_payload, dict)
            and state_payload.get("current_state") == "READY_TO_IMPLEMENT"
        ):
            event_result = validate_k0_red_field_event(route_dir / "events.jsonl")
            local_errors.extend(event_result["validation_errors"])
            result["validation_warnings"].extend(event_result["validation_warnings"])
        result["validation_errors"] = local_errors + result["validation_errors"]
        if result["validation_errors"]:
            result["verdict"] = "fail"
        route_results.append(result)

    for result in route_results:
        errors.extend(
            {
                **error,
                "route_id": result["route_id"],
            }
            for error in result["validation_errors"]
        )
        warnings.extend(
            {
                **warning,
                "route_id": result["route_id"],
            }
            for warning in result["validation_warnings"]
        )

    return {
        "producer_function": "validate_routes_tree",
        "route_count": len(route_dirs),
        "routes": route_results,
        "input_artifacts": _route_input_artifacts(routes_dir),
        "changed_files": [_posix(path) for path in (changed_files or [])],
        "validation_errors": errors,
        "validation_warnings": warnings,
        "verdict": "pass" if not errors else "fail",
    }


def _parse_program_state_file(path: Path, errors: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append(_new_error("missing_program_state_json", "Program state is missing.", path=_posix(path)))
        return None
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        errors.append(
            _new_error(
                "invalid_program_state_json",
                "program_state.json could not be parsed.",
                path=_posix(path),
                error=str(exc),
            )
        )
        return None
    if not isinstance(payload, dict):
        errors.append(
            _new_error("program_state_not_object", "program_state.json must contain an object.", path=_posix(path))
        )
        return None
    return payload


def validate_program_state(*, artifact_dir: Path, routes_dir: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    program_state_path = artifact_dir / state_machine.PROGRAM_STATE_FILENAME
    program_state_payload = _parse_program_state_file(program_state_path, errors)
    if program_state_payload is None:
        return {
            "producer_function": "validate_program_state",
            "input_artifacts": [],
            "current_frontier_route_id": None,
            "validation_errors": errors,
            "validation_warnings": warnings,
            "verdict": "fail",
        }

    current_frontier_route_id = program_state_payload.get("current_frontier_route_id")
    if not isinstance(current_frontier_route_id, str) or not current_frontier_route_id.strip():
        errors.append(
            _new_error(
                "missing_current_frontier_route_id",
                "program_state.json must include current_frontier_route_id.",
            )
        )
        current_frontier_route_id = None
    else:
        current_frontier_route_id = current_frontier_route_id.strip()

    if not _non_empty_string_list(program_state_payload.get("allowed_next_actions")):
        errors.append(
            _new_error(
                "program_state_missing_allowed_next_actions",
                "program_state.json must include non-empty allowed_next_actions.",
            )
        )

    if not _non_empty_string_list(program_state_payload.get("forbidden_next_actions")):
        errors.append(
            _new_error(
                "program_state_missing_forbidden_next_actions",
                "program_state.json must include non-empty forbidden_next_actions.",
            )
        )

    if not _claim_ceiling_has_max(program_state_payload.get("claim_ceiling")):
        errors.append(
            _new_error(
                "program_state_missing_claim_ceiling_max",
                "program_state.json must include claim_ceiling.max.",
            )
        )

    input_artifacts = [_relative_posix(program_state_path, artifact_dir.parent.parent)]

    if current_frontier_route_id:
        current_frontier_route_dir = routes_dir / current_frontier_route_id
        if not current_frontier_route_dir.exists():
            errors.append(
                _new_error(
                    "missing_current_frontier_route_directory",
                    "current_frontier_route_id must point to an existing route directory.",
                    current_frontier_route_id=current_frontier_route_id,
                    path=_posix(current_frontier_route_dir),
                )
            )
        else:
            route_state_errors: list[dict[str, Any]] = []
            route_state_payload = _parse_json_file(current_frontier_route_dir / "state.json", route_state_errors)
            errors.extend(route_state_errors)
            if route_state_payload is not None:
                input_artifacts.append(
                    _relative_posix(current_frontier_route_dir / "state.json", artifact_dir.parent.parent)
                )
                route_current_state = route_state_payload.get("current_state")
                source_readback = route_state_payload.get("source_readback")
                ledger_readback = source_readback.get("ledger") if isinstance(source_readback, dict) else None
                if (
                    current_frontier_route_id == state_machine.K0_PARENT_ROUTE_ID
                    and route_current_state == "READY_TO_IMPLEMENT"
                ):
                    program_k0_mismatches: dict[str, Any] = {}
                    expected_program_fields = {
                        "allowed_next_actions": list(state_machine.K0_READY_ALLOWED_ACTIONS),
                        "authorized_implementation_targets": list(
                            state_machine.K0_READY_AUTHORIZED_IMPLEMENTATION_TARGETS
                        ),
                        "child_authorizations": state_machine.K0_READY_CHILD_AUTHORIZATIONS,
                        "red_field_addendum_pin": state_machine.K0_RED_FIELD_ADDENDUM_PIN,
                        "red_field_correction_pin": state_machine.K0_RED_FIELD_CORRECTION_PIN,
                        "current_route_posture": "k0_dual_track_first_pair_ready_with_red_field_correction",
                    }
                    for field, expected in expected_program_fields.items():
                        if program_state_payload.get(field) != expected:
                            program_k0_mismatches[field] = {
                                "expected": expected,
                                "actual": program_state_payload.get(field),
                            }
                    if program_k0_mismatches:
                        errors.append(
                            _new_error(
                                "program_state_k0_red_field_boundary_mismatch",
                                "Program state must mirror the exact K0 Red-field authorization boundary.",
                                mismatches=program_k0_mismatches,
                            )
                        )
                if current_frontier_route_id == state_machine.K0_PARENT_ROUTE_ID and not isinstance(
                    ledger_readback, dict
                ):
                    errors.append(
                        _new_error(
                            "current_frontier_ledger_declaration_missing",
                            "The K0 parent current frontier must declare its exact append-only ledger dependency.",
                            current_frontier_route_id=current_frontier_route_id,
                        )
                    )
                if isinstance(ledger_readback, dict):
                    ledger_relative_path = ledger_readback.get("path")
                    required_entry_prefix = ledger_readback.get("required_entry_prefix")
                    expected_k0_ledger_prefix = (
                        state_machine.K0_RED_FIELD_CORRECTION_LEDGER_ENTRY_PREFIX
                        if route_current_state == "READY_TO_IMPLEMENT"
                        else state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX
                    )
                    if not isinstance(ledger_relative_path, str) or not ledger_relative_path.strip():
                        errors.append(
                            _new_error(
                                "current_frontier_ledger_path_missing",
                                "Declared current-frontier ledger readback must include a repo-relative path.",
                                current_frontier_route_id=current_frontier_route_id,
                            )
                        )
                    elif not isinstance(required_entry_prefix, str) or not required_entry_prefix.strip():
                        errors.append(
                            _new_error(
                                "current_frontier_ledger_entry_prefix_missing",
                                "Declared current-frontier ledger readback must include required_entry_prefix.",
                                current_frontier_route_id=current_frontier_route_id,
                            )
                        )
                    elif (
                        current_frontier_route_id == state_machine.K0_PARENT_ROUTE_ID
                        and (
                            ledger_relative_path != state_machine.K0_PARENT_LEDGER_PATH
                            or required_entry_prefix != expected_k0_ledger_prefix
                        )
                    ):
                        errors.append(
                            _new_error(
                                "current_frontier_k0_ledger_contract_mismatch",
                                "The K0 parent ledger declaration must match the frozen path and task-specific prefix.",
                                current_frontier_route_id=current_frontier_route_id,
                                expected_path=state_machine.K0_PARENT_LEDGER_PATH,
                                actual_path=ledger_relative_path,
                                expected_entry_prefix=expected_k0_ledger_prefix,
                                actual_entry_prefix=required_entry_prefix,
                            )
                        )
                    else:
                        repo_root = artifact_dir.parent.parent.resolve()
                        ledger_path = (repo_root / ledger_relative_path).resolve()
                        try:
                            ledger_path.relative_to(repo_root)
                        except ValueError:
                            errors.append(
                                _new_error(
                                    "current_frontier_ledger_path_outside_repo",
                                    "Declared ledger path must stay inside the repository.",
                                    current_frontier_route_id=current_frontier_route_id,
                                    path=_posix(ledger_path),
                                )
                            )
                        else:
                            input_artifacts.append(_relative_posix(ledger_path, repo_root))
                            if not ledger_path.is_file():
                                errors.append(
                                    _new_error(
                                        "current_frontier_ledger_missing",
                                        "Declared current-frontier ledger file is missing.",
                                        current_frontier_route_id=current_frontier_route_id,
                                        path=_posix(ledger_path),
                                    )
                                )
                            else:
                                ledger_lines = ledger_path.read_text(encoding="utf-8").splitlines()
                                matching_lines = [
                                    line for line in ledger_lines if line.startswith(required_entry_prefix)
                                ]
                                if not matching_lines:
                                    errors.append(
                                        _new_error(
                                            "current_frontier_ledger_entry_missing",
                                            "Declared current-frontier ledger entry prefix was not found.",
                                            current_frontier_route_id=current_frontier_route_id,
                                            required_entry_prefix=required_entry_prefix,
                                            path=_posix(ledger_path),
                                        )
                                    )
                                elif (
                                    current_frontier_route_id == state_machine.K0_PARENT_ROUTE_ID
                                    and len(matching_lines) != 1
                                ):
                                    errors.append(
                                        _new_error(
                                            "current_frontier_k0_ledger_entry_not_unique",
                                            "The frozen K0 parent ledger entry must occur exactly once.",
                                            current_frontier_route_id=current_frontier_route_id,
                                            required_entry_prefix=required_entry_prefix,
                                            match_count=len(matching_lines),
                                            path=_posix(ledger_path),
                                        )
                                    )
                                if (
                                    current_frontier_route_id == state_machine.K0_PARENT_ROUTE_ID
                                    and route_current_state == "READY_TO_IMPLEMENT"
                                ):
                                    preserved_prefixes = ledger_readback.get("preserved_entry_prefixes")
                                    expected_preserved_prefixes = [
                                        state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX,
                                        state_machine.K0_READY_LEDGER_ENTRY_PREFIX,
                                        state_machine.K0_RED_FIELD_LEDGER_ENTRY_PREFIX,
                                    ]
                                    if preserved_prefixes != expected_preserved_prefixes:
                                        errors.append(
                                            _new_error(
                                                "current_frontier_k0_preserved_ledger_contract_mismatch",
                                                "The corrected Red-field READY_TO_IMPLEMENT frontier must preserve L-020 through L-022.",
                                                expected=expected_preserved_prefixes,
                                                actual=preserved_prefixes,
                                            )
                                        )
                                    else:
                                        preserved_hashes = ledger_readback.get("preserved_entry_sha256")
                                        if preserved_hashes != state_machine.K0_RED_FIELD_PRESERVED_LEDGER_HASHES:
                                            errors.append(
                                                _new_error(
                                                    "current_frontier_k0_preserved_ledger_hash_contract_mismatch",
                                                    "The route state must pin the exact L-020/L-021 full-line hashes.",
                                                    expected=state_machine.K0_RED_FIELD_PRESERVED_LEDGER_HASHES,
                                                    actual=preserved_hashes,
                                                )
                                            )
                                        expected_hash_by_prefix = {
                                            state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX: state_machine.K0_PARENT_LEDGER_LINE_SHA256,
                                            state_machine.K0_READY_LEDGER_ENTRY_PREFIX: state_machine.K0_READY_LEDGER_LINE_SHA256,
                                            state_machine.K0_RED_FIELD_LEDGER_ENTRY_PREFIX: state_machine.K0_RED_FIELD_LEDGER_LINE_SHA256,
                                        }
                                        for preserved_prefix in preserved_prefixes:
                                            preserved_matches = [
                                                line for line in ledger_lines if line.startswith(preserved_prefix)
                                            ]
                                            if len(preserved_matches) != 1:
                                                errors.append(
                                                    _new_error(
                                                        "current_frontier_k0_preserved_ledger_entry_not_unique",
                                                        "Each preserved K0 ledger prefix must occur exactly once.",
                                                        required_entry_prefix=preserved_prefix,
                                                        match_count=len(preserved_matches),
                                                        path=_posix(ledger_path),
                                                    )
                                                )
                                            elif hashlib.sha256(
                                                preserved_matches[0].encode("utf-8")
                                            ).hexdigest() != expected_hash_by_prefix[preserved_prefix]:
                                                errors.append(
                                                    _new_error(
                                                        "current_frontier_k0_preserved_ledger_line_drift",
                                                        "A preserved K0 ledger line was rewritten after banking.",
                                                        required_entry_prefix=preserved_prefix,
                                                        expected_sha256=expected_hash_by_prefix[preserved_prefix],
                                                        actual_sha256=hashlib.sha256(
                                                            preserved_matches[0].encode("utf-8")
                                                        ).hexdigest(),
                                                        path=_posix(ledger_path),
                                                    )
                                                )
                current_state = route_current_state
                if current_state == "TOMBSTONED":
                    errors.append(
                        _new_error(
                            "current_frontier_route_tombstoned",
                            "current_frontier_route_id cannot point to a TOMBSTONED route.",
                            current_frontier_route_id=current_frontier_route_id,
                        )
                    )

                if current_state in ("REGISTERED", "READY_TO_IMPLEMENT"):
                    forbidden_authorizations = _forbidden_current_frontier_authorizations(
                        program_state_payload=program_state_payload,
                        route_state_payload=route_state_payload,
                    )
                    if forbidden_authorizations:
                        errors.append(
                            _new_error(
                                "registered_current_frontier_authorizes_forbidden_capability",
                                "REGISTERED current frontier cannot authorize mechanism validity, theory pressure, scoring, or experiment execution.",
                                current_frontier_route_id=current_frontier_route_id,
                                forbidden_authorizations=forbidden_authorizations,
                            )
                        )

                if (
                    current_frontier_route_id == state_machine.CURRENT_FRONTIER_ROUTE_ID
                    and not _source_readback_has_l014_or_equivalent(route_state_payload.get("source_readback"))
                ):
                    errors.append(
                        _new_error(
                            "n2_frontier_missing_l014_source_readback",
                            "N2-SBMC-ENV-REDESIGN-001A must cite L-014 or equivalent current ledger evidence in source_readback.",
                            current_frontier_route_id=current_frontier_route_id,
                        )
                    )

    return {
        "producer_function": "validate_program_state",
        "input_artifacts": sorted(set(input_artifacts)),
        "current_frontier_route_id": current_frontier_route_id,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "verdict": "pass" if not errors else "fail",
    }


def git_changed_files(repo_root: Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return []

    changed: list[str] = []
    for line in completed.stdout.splitlines():
        if not line:
            continue
        path_text = line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        changed.append(_posix(path_text))
    return changed


def build_validation_report(
    repo_root: str | Path,
    *,
    changed_files: list[str] | None = None,
    authorized_paths: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    effective_changed_files = git_changed_files(root) if changed_files is None else changed_files
    effective_authorized_paths = (
        list(state_machine.AUTHORIZED_TASK_PATHS) if authorized_paths is None else list(authorized_paths)
    )
    routes_dir = root / state_machine.TASK_ARTIFACT_DIR / "routes"
    route_tree = validate_routes_tree(
        routes_dir=routes_dir,
        changed_files=effective_changed_files,
        authorized_paths=effective_authorized_paths,
    )
    artifact_dir = root / state_machine.TASK_ARTIFACT_DIR
    program_state = validate_program_state(artifact_dir=artifact_dir, routes_dir=routes_dir)
    red_field_addendum = {
        "producer_function": "validate_red_field_addendum_repository",
        "input_artifacts": [],
        "validation_errors": [],
        "validation_warnings": [],
        "verdict": "not_applicable",
    }
    red_field_correction = {
        "producer_function": "validate_red_field_correction_repository",
        "input_artifacts": [],
        "validation_errors": [],
        "validation_warnings": [],
        "verdict": "not_applicable",
    }
    k0_state_path = routes_dir / state_machine.K0_PARENT_ROUTE_ID / "state.json"
    if k0_state_path.is_file():
        try:
            k0_state_payload = load_json(k0_state_path)
        except json.JSONDecodeError:
            k0_state_payload = None
        if isinstance(k0_state_payload, dict) and k0_state_payload.get("current_state") == "READY_TO_IMPLEMENT":
            red_field_addendum = validate_red_field_addendum_repository(
                repo_root=root,
                route_state_payload=k0_state_payload,
            )
            red_field_correction = validate_red_field_correction_repository(
                repo_root=root,
                route_state_payload=k0_state_payload,
            )
    input_artifacts = [
        f"{state_machine.TASK_ARTIFACT_DIR}/routes/{artifact}"
        for artifact in route_tree["input_artifacts"]
    ]
    input_artifacts.extend(program_state["input_artifacts"])
    input_artifacts.extend(red_field_addendum["input_artifacts"])
    input_artifacts.extend(red_field_correction["input_artifacts"])
    schema_dir = root / state_machine.TASK_ARTIFACT_DIR / "schemas"
    for schema in sorted(schema_dir.glob("*.schema.json")) if schema_dir.exists() else []:
        input_artifacts.append(_relative_posix(schema, root))

    validation_errors = (
        route_tree["validation_errors"]
        + program_state["validation_errors"]
        + red_field_addendum["validation_errors"]
        + red_field_correction["validation_errors"]
    )
    validation_warnings = (
        route_tree["validation_warnings"]
        + program_state["validation_warnings"]
        + red_field_addendum["validation_warnings"]
        + red_field_correction["validation_warnings"]
    )

    return {
        "task_id": state_machine.TASK_ID,
        "producer_function": "build_validation_report",
        "input_artifacts": sorted(set(input_artifacts)),
        "run_id": f"{state_machine.TASK_ID.lower()}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
        "aggregation_rule": "verdict is pass iff validate_routes_tree, validate_program_state, and applicable original-addendum and correction committed-object validators return zero validation_errors",
        "code_path_hash": code_path_hash(),
        "validation_errors": validation_errors,
        "validation_warnings": validation_warnings,
        "current_frontier_route_id": program_state["current_frontier_route_id"],
        "program_state_verdict": program_state["verdict"],
        "red_field_addendum_verdict": red_field_addendum["verdict"],
        "red_field_correction_verdict": red_field_correction["verdict"],
        "route_count": route_tree["route_count"],
        "routes": [
            {
                "route_id": result["route_id"],
                "current_state": result["current_state"],
                "closure_type": result["closure_type"],
                "verdict": result["verdict"],
            }
            for result in route_tree["routes"]
        ],
        "changed_files": route_tree["changed_files"],
        "authorized_paths": sorted(effective_authorized_paths),
        "claim_ceiling": "local route-governance validation only; no mechanism, theory, agency, autonomy, subjectivity, consciousness, EGO readiness, companion readiness, or mainline-effect claim",
        "verdict": "pass" if not validation_errors else "fail",
    }


def validation_report_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / state_machine.TASK_ARTIFACT_DIR / "validation_report.json"


def write_validation_report(repo_root: str | Path, report: dict[str, Any]) -> Path:
    path = validation_report_path(repo_root)
    write_json(path, report)
    return path


def build_status(repo_root: str | Path) -> dict[str, Any]:
    report = build_validation_report(repo_root)
    return {
        "task_id": state_machine.TASK_ID,
        "route_count": report["route_count"],
        "verdict": report["verdict"],
        "current_frontier_route_id": report["current_frontier_route_id"],
        "program_state_verdict": report["program_state_verdict"],
        "red_field_addendum_verdict": report["red_field_addendum_verdict"],
        "red_field_correction_verdict": report["red_field_correction_verdict"],
        "routes": report["routes"],
        "validation_error_count": len(report["validation_errors"]),
        "validation_warning_count": len(report["validation_warnings"]),
        "claim_ceiling": report["claim_ceiling"],
    }


def build_dashboard(repo_root: str | Path) -> dict[str, Any]:
    report = build_validation_report(repo_root)
    return {
        "task_id": state_machine.TASK_ID,
        "producer_function": "build_dashboard",
        "verdict": report["verdict"],
        "route_count": report["route_count"],
        "current_frontier_route_id": report["current_frontier_route_id"],
        "program_state_verdict": report["program_state_verdict"],
        "red_field_addendum_verdict": report["red_field_addendum_verdict"],
        "red_field_correction_verdict": report["red_field_correction_verdict"],
        "routes": report["routes"],
        "validation_error_codes": sorted({error["code"] for error in report["validation_errors"]}),
        "validation_warning_codes": sorted({warning["code"] for warning in report["validation_warnings"]}),
        "transition_command_status": "deferred_in_001a_first_local_version",
        "claim_ceiling": report["claim_ceiling"],
    }
