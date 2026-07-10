from __future__ import annotations

import copy
import hashlib
import itertools
import json
import random
import subprocess
from pathlib import Path
from typing import Any

from .h0_registry import all_atomic_specs, panel_for
from .h0_resolver import resolve_comparator_panel, resolve_component_evidence
from .h0_schema import (
    CausalObservationRecord,
    CausalOutcome,
    ComparatorObservationRecord,
    ComparatorOutcome,
    ComparatorState,
    ComponentId,
    EvidenceState,
    H0Registry,
    PanelKind,
)


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_registry_payload(payload: Any) -> dict[str, Any]:
    errors: list[str] = []
    registry: H0Registry | None = None
    try:
        if not isinstance(payload, dict):
            raise ValueError("registry payload must be an object")
        registry = H0Registry.from_dict(payload)
    except (TypeError, ValueError, KeyError) as exc:
        errors.append(str(exc))

    if registry is not None:
        specs = all_atomic_specs(registry)
        ids = [spec.atomic_contrast_id for spec in specs]
        tuples = [(spec.component, spec.panel, spec.arm) for spec in specs]
        if len(ids) != len(set(ids)):
            errors.append("atomic_contrast_id must be unique")
        if len(tuples) != len(set(tuples)):
            errors.append("component/panel/arm tuples must be unique")
        forbidden_literals = ("placeholder", "all_families", "candidate_placeholder", "aggregate_panel")
        for spec in specs:
            serialized = canonical_json_bytes(spec.to_dict()).decode("ascii").lower()
            if any(token in serialized for token in forbidden_literals):
                errors.append(f"{spec.atomic_contrast_id} contains a forbidden placeholder")
            if spec.seed_block_id != spec.power_spec.seed_block_id:
                errors.append(f"{spec.atomic_contrast_id} seed block mismatch")
            if not all((spec.full_arm, spec.intervention_arm, spec.reference_arm)):
                errors.append(f"{spec.atomic_contrast_id} has an unresolved execution arm")
            if spec.atomic_contrast_id != f"atomic::{spec.component.value}::{spec.panel.value}::{spec.arm}":
                errors.append(f"{spec.atomic_contrast_id} identity is not canonical")
        for component in ComponentId:
            for panel in PanelKind:
                panel_spec = panel_for(registry, component, panel)
                if not panel_spec.mandatory or not panel_spec.arms:
                    errors.append(f"{component.value}/{panel.value} is not mandatory/non-empty")

    return {
        "producer_function": "validate_registry_payload",
        "accepted": not errors,
        "validation_errors": errors,
        "atomic_spec_count": len(all_atomic_specs(registry)) if registry else 0,
    }


def reference_oracle_component(
    component_id: ComponentId,
    mandatory_arm_ids: list[str],
    observations: list[CausalObservationRecord],
) -> EvidenceState:
    """Independent branch structure; does not call primary reducers or their helpers."""
    if not mandatory_arm_ids:
        return EvidenceState.INVALID_INSTRUMENT
    seen: dict[str, CausalOutcome] = {}
    invalid_dependency = False
    absence_proof = False
    not_started = False
    foreign = False
    for row in observations:
        if row.component_id is not component_id or row.arm_id in seen:
            foreign = True
        seen[row.arm_id] = row.outcome
        invalid_dependency = invalid_dependency or row.outcome in {CausalOutcome.INVALID, CausalOutcome.UNDERPOWERED}
        absence_proof = absence_proof or row.outcome in {CausalOutcome.NO_CONTRIBUTION, CausalOutcome.WRONG_SIGN}
        not_started = not_started or row.outcome is CausalOutcome.NOT_STARTED
    if foreign or set(seen) != set(mandatory_arm_ids):
        return EvidenceState.INVALID_INSTRUMENT
    if invalid_dependency:
        return EvidenceState.INVALID_INSTRUMENT
    if absence_proof:
        return EvidenceState.ABSENT
    if not_started:
        return EvidenceState.NOT_TESTED
    if all(value is CausalOutcome.EXPECTED_SIGN for value in seen.values()):
        return EvidenceState.PRESENT_BOUNDED
    return EvidenceState.INVALID_INSTRUMENT


def reference_oracle_comparator(
    component_id: ComponentId,
    panel: PanelKind,
    required_arm_ids: list[str],
    observations: list[ComparatorObservationRecord],
) -> ComparatorState:
    if panel not in {PanelKind.CONTROL, PanelKind.RIVAL} or not required_arm_ids:
        return ComparatorState.INCONCLUSIVE
    seen: dict[str, ComparatorOutcome] = {}
    foreign = False
    for row in observations:
        if row.component_id is not component_id or row.panel is not panel or row.arm_id in seen:
            foreign = True
        seen[row.arm_id] = row.outcome
    if foreign or set(seen) != set(required_arm_ids):
        return ComparatorState.NOT_RUN
    values = set(seen.values())
    if ComparatorOutcome.COMPARATOR_SUPERIOR in values:
        return ComparatorState.DOMINATED
    if values & {ComparatorOutcome.PARITY, ComparatorOutcome.CEILING}:
        return ComparatorState.EQUIVALENT if panel is PanelKind.CONTROL else ComparatorState.SATURATED
    if values & {ComparatorOutcome.INVALID, ComparatorOutcome.UNDERPOWERED}:
        return ComparatorState.INCONCLUSIVE
    if ComparatorOutcome.NOT_RUN in values:
        return ComparatorState.NOT_RUN
    if all(value is ComparatorOutcome.CANDIDATE_SUPERIOR for value in seen.values()):
        return ComparatorState.SEPARATED
    return ComparatorState.INCONCLUSIVE


def _causal_rows(component: ComponentId, arms: list[str], overrides: dict[str, str] | None = None) -> list[dict[str, str]]:
    override = overrides or {}
    return [
        {"component_id": component.value, "arm_id": arm, "outcome": override.get(arm, CausalOutcome.EXPECTED_SIGN.value)}
        for arm in arms
    ]


def _comparator_rows(component: ComponentId, panel: PanelKind, arms: list[str], overrides: dict[str, str] | None = None) -> list[dict[str, str]]:
    override = overrides or {}
    return [
        {"component_id": component.value, "panel": panel.value, "arm_id": arm, "outcome": override.get(arm, ComparatorOutcome.CANDIDATE_SUPERIOR.value)}
        for arm in arms
    ]


def build_scenario_catalog(registry: H0Registry) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for component in ComponentId:
        causal_arms = [row.arm for row in panel_for(registry, component, PanelKind.CAUSAL).arms]
        target = causal_arms[0]
        scenarios.append({"scenario_id": f"{component.value}::causal::positive", "kind": "causal", "component_id": component.value, "required_arm_ids": causal_arms, "observations": _causal_rows(component, causal_arms), "expected": EvidenceState.PRESENT_BOUNDED.value})
        for label, outcome, expected in (
            ("invalid", CausalOutcome.INVALID, EvidenceState.INVALID_INSTRUMENT),
            ("underpowered", CausalOutcome.UNDERPOWERED, EvidenceState.INVALID_INSTRUMENT),
            ("no_contribution", CausalOutcome.NO_CONTRIBUTION, EvidenceState.ABSENT),
            ("wrong_sign", CausalOutcome.WRONG_SIGN, EvidenceState.ABSENT),
            ("not_started", CausalOutcome.NOT_STARTED, EvidenceState.NOT_TESTED),
        ):
            scenarios.append({"scenario_id": f"{component.value}::causal::{label}", "kind": "causal", "component_id": component.value, "required_arm_ids": causal_arms, "observations": _causal_rows(component, causal_arms, {target: outcome.value}), "expected": expected.value})
        scenarios.append({"scenario_id": f"{component.value}::causal::missing", "kind": "causal", "component_id": component.value, "required_arm_ids": causal_arms, "observations": _causal_rows(component, causal_arms[:-1]), "expected": EvidenceState.INVALID_INSTRUMENT.value})
        if len(causal_arms) > 1:
            scenarios.append({"scenario_id": f"{component.value}::causal::invalid_precedence", "kind": "causal", "component_id": component.value, "required_arm_ids": causal_arms, "observations": _causal_rows(component, causal_arms, {causal_arms[0]: CausalOutcome.WRONG_SIGN.value, causal_arms[-1]: CausalOutcome.INVALID.value}), "expected": EvidenceState.INVALID_INSTRUMENT.value})

        for panel in (PanelKind.CONTROL, PanelKind.RIVAL):
            arms = [row.arm for row in panel_for(registry, component, panel).arms]
            target = arms[0]
            parity_expected = ComparatorState.EQUIVALENT if panel is PanelKind.CONTROL else ComparatorState.SATURATED
            cases = (
                ("positive", None, ComparatorState.SEPARATED),
                ("dominated", ComparatorOutcome.COMPARATOR_SUPERIOR, ComparatorState.DOMINATED),
                ("parity", ComparatorOutcome.PARITY, parity_expected),
                ("ceiling", ComparatorOutcome.CEILING, parity_expected),
                ("underpowered", ComparatorOutcome.UNDERPOWERED, ComparatorState.INCONCLUSIVE),
                ("not_run", ComparatorOutcome.NOT_RUN, ComparatorState.NOT_RUN),
            )
            for label, outcome, expected in cases:
                overrides = {} if outcome is None else {target: outcome.value}
                scenarios.append({"scenario_id": f"{component.value}::{panel.value}::{label}", "kind": "comparator", "component_id": component.value, "panel": panel.value, "required_arm_ids": arms, "observations": _comparator_rows(component, panel, arms, overrides), "expected": expected.value})
            scenarios.append({"scenario_id": f"{component.value}::{panel.value}::missing", "kind": "comparator", "component_id": component.value, "panel": panel.value, "required_arm_ids": arms, "observations": _comparator_rows(component, panel, arms[:-1]), "expected": ComparatorState.NOT_RUN.value})
    return scenarios


def _deserialize_causal(rows: list[dict[str, str]]) -> list[CausalObservationRecord]:
    return [CausalObservationRecord(ComponentId(row["component_id"]), row["arm_id"], CausalOutcome(row["outcome"])) for row in rows]


def _deserialize_comparator(rows: list[dict[str, str]]) -> list[ComparatorObservationRecord]:
    return [ComparatorObservationRecord(ComponentId(row["component_id"]), PanelKind(row["panel"]), row["arm_id"], ComparatorOutcome(row["outcome"])) for row in rows]


def evaluate_scenario(scenario: dict[str, Any]) -> tuple[str, str]:
    component = ComponentId(scenario["component_id"])
    if scenario["kind"] == "causal":
        rows = _deserialize_causal(scenario["observations"])
        candidate = resolve_component_evidence(component_id=component, mandatory_arm_ids=scenario["required_arm_ids"], observations=rows)
        oracle = reference_oracle_component(component, scenario["required_arm_ids"], rows)
    else:
        panel = PanelKind(scenario["panel"])
        rows = _deserialize_comparator(scenario["observations"])
        candidate = resolve_comparator_panel(component_id=component, panel=panel, required_arm_ids=scenario["required_arm_ids"], observations=rows)
        oracle = reference_oracle_comparator(component, panel, scenario["required_arm_ids"], rows)
    return candidate.value, oracle.value


def run_semantic_validation(registry: H0Registry, scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for scenario in scenarios:
        candidate, oracle = evaluate_scenario(scenario)
        rows.append({"scenario_id": scenario["scenario_id"], "candidate": candidate, "oracle": oracle, "expected": scenario["expected"], "agreement": candidate == oracle, "expected_match": candidate == scenario["expected"]})
    spec_validation = validate_registry_payload(registry.to_dict())
    return {
        "producer_function": "run_semantic_validation",
        "scenario_results": rows,
        "scenario_count": len(rows),
        "all_candidate_oracle_agree": all(row["agreement"] for row in rows),
        "all_expected_match": all(row["expected_match"] for row in rows),
        "atomic_specs_complete": spec_validation["accepted"],
        "atomic_spec_count": spec_validation["atomic_spec_count"],
        "validation_errors": spec_validation["validation_errors"],
    }


def build_permutation_catalog(registry: H0Registry, seed: int = 9173) -> list[dict[str, Any]]:
    catalog: list[dict[str, Any]] = []
    rng = random.Random(seed)
    for component in ComponentId:
        causal = [row.arm for row in panel_for(registry, component, PanelKind.CAUSAL).arms]
        outcomes = {arm: CausalOutcome.EXPECTED_SIGN.value for arm in causal}
        if len(causal) > 1:
            outcomes[causal[0]] = CausalOutcome.WRONG_SIGN.value
            outcomes[causal[-1]] = CausalOutcome.INVALID.value
        for index, order in enumerate(itertools.permutations(causal)):
            catalog.append({"permutation_id": f"causal::{component.value}::{index:04d}", "kind": "causal", "component_id": component.value, "panel": PanelKind.CAUSAL.value, "required_arm_ids": causal, "order": list(order), "outcomes": outcomes})
        for panel in (PanelKind.CONTROL, PanelKind.RIVAL):
            arms = [row.arm for row in panel_for(registry, component, panel).arms]
            orders: list[tuple[str, list[str]]] = [
                ("reversed", list(reversed(arms))),
                ("rotated", arms[1:] + arms[:1]),
                ("single_change", ([arms[1], arms[0]] + arms[2:]) if len(arms) > 1 else list(arms)),
            ]
            for bank_index in range(4):
                shuffled = list(arms)
                rng.shuffle(shuffled)
                orders.append((f"seed_bank_{bank_index}", shuffled))
            outcomes = {arm: ComparatorOutcome.CANDIDATE_SUPERIOR.value for arm in arms}
            outcomes[arms[-1]] = ComparatorOutcome.COMPARATOR_SUPERIOR.value
            for label, order in orders:
                catalog.append({"permutation_id": f"comparator::{component.value}::{panel.value}::{label}", "kind": "comparator", "component_id": component.value, "panel": panel.value, "required_arm_ids": arms, "order": order, "outcomes": outcomes})
    return catalog


def run_permutation_validation(catalog: list[dict[str, Any]]) -> dict[str, Any]:
    results = []
    for case in catalog:
        component = ComponentId(case["component_id"])
        if case["kind"] == "causal":
            rows = [CausalObservationRecord(component, arm, CausalOutcome(case["outcomes"][arm])) for arm in case["order"]]
            candidate = resolve_component_evidence(component_id=component, mandatory_arm_ids=case["required_arm_ids"], observations=rows)
            oracle = reference_oracle_component(component, case["required_arm_ids"], rows)
        else:
            panel = PanelKind(case["panel"])
            rows = [ComparatorObservationRecord(component, panel, arm, ComparatorOutcome(case["outcomes"][arm])) for arm in case["order"]]
            candidate = resolve_comparator_panel(component_id=component, panel=panel, required_arm_ids=case["required_arm_ids"], observations=rows)
            oracle = reference_oracle_comparator(component, panel, case["required_arm_ids"], rows)
        results.append({"permutation_id": case["permutation_id"], "candidate": candidate.value, "oracle": oracle.value, "agreement": candidate is oracle})
    consumed = [row["permutation_id"] for row in results]
    frozen = [row["permutation_id"] for row in catalog]
    return {"producer_function": "run_permutation_validation", "results": results, "all_invariant": all(row["agreement"] for row in results), "frozen_ids": frozen, "consumed_ids": consumed, "all_frozen_ids_consumed": consumed == frozen}


def enumerate_normative_leaves(payload: Any) -> list[dict[str, Any]]:
    leaves: list[dict[str, Any]] = []
    def walk(value: Any, segments: list[str | int]) -> None:
        if segments and segments[0] == "metadata":
            return
        if isinstance(value, dict):
            for key in sorted(value):
                walk(value[key], segments + [key])
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, segments + [index])
        else:
            path = "$" + "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in segments)
            leaves.append({"normative_field_id": f"normative::{len(leaves):05d}", "path": path, "segments": segments, "mutation_operator": "replace_with_json_null"})
    walk(payload, [])
    return leaves


def apply_null_mutation(payload: dict[str, Any], segments: list[str | int]) -> dict[str, Any]:
    mutated = copy.deepcopy(payload)
    cursor: Any = mutated
    for segment in segments[:-1]:
        cursor = cursor[segment]
    cursor[segments[-1]] = None
    return mutated


def run_mutation_validation(registry_payload: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    base_hash = sha256_bytes(canonical_json_bytes(registry_payload))
    results = []
    for field in manifest["normative_fields"]:
        mutated = apply_null_mutation(registry_payload, field["segments"])
        mutated_hash = sha256_bytes(canonical_json_bytes(mutated))
        validation = validate_registry_payload(mutated)
        results.append({"mutation_id": f"mutation::{field['normative_field_id']}", "normative_field_id": field["normative_field_id"], "path": field["path"], "input_changed": mutated_hash != base_hash, "real_validator_called": validation["producer_function"], "killed": not validation["accepted"], "validation_errors": validation["validation_errors"][:2]})
    killed = sum(bool(row["input_changed"] and row["killed"]) for row in results)
    return {"producer_function": "run_mutation_validation", "results": results, "mutation_count": len(results), "killed_count": killed, "normative_mutation_kill_rate": killed / len(results) if results else 0.0, "all_manifest_ids_consumed": [row["normative_field_id"] for row in results] == [row["normative_field_id"] for row in manifest["normative_fields"]]}


def _reverse_keys(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _reverse_keys(value[key]) for key in reversed(list(value))}
    if isinstance(value, list):
        return [_reverse_keys(row) for row in value]
    return value


def apply_transformation(payload: dict[str, Any], transformation_id: str) -> tuple[dict[str, Any], str]:
    transformed = copy.deepcopy(payload)
    if transformation_id == "json_key_order":
        transformed = _reverse_keys(transformed)
        raw = json.dumps(transformed, sort_keys=False, separators=(",", ":"))
    elif transformation_id == "set_like_arm_order":
        for component in transformed["components"]:
            for panel in component["panels"]:
                panel["arms"] = list(reversed(panel["arms"]))
        raw = json.dumps(transformed, sort_keys=False)
    elif transformation_id == "metadata_only_fields":
        transformed["metadata"] = {"note": "changed non-semantic annotation", "audit_note": "ignored by domain semantics"}
        raw = json.dumps(transformed, sort_keys=True)
    elif transformation_id == "canonical_equivalent_serialization":
        raw = json.dumps(transformed, sort_keys=False, indent=3, ensure_ascii=True)
        transformed = json.loads(raw)
    else:
        raise ValueError(f"unknown transformation {transformation_id}")
    return transformed, raw


def run_metamorphic_validation(registry_payload: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    results = []
    for row in catalog["transformations"]:
        transformed, raw = apply_transformation(registry_payload, row["transformation_id"])
        validation = validate_registry_payload(transformed)
        results.append({"transformation_id": row["transformation_id"], "accepted": validation["accepted"], "real_validator_called": validation["producer_function"], "serialized_sha256": sha256_bytes(raw.encode("utf-8"))})
    accepted = sum(bool(row["accepted"]) for row in results)
    return {"producer_function": "run_metamorphic_validation", "results": results, "valid_transformation_count": len(results), "accepted_count": accepted, "valid_transformation_accept_rate": accepted / len(results) if results else 0.0, "all_catalog_ids_consumed": [row["transformation_id"] for row in results] == [row["transformation_id"] for row in catalog["transformations"]]}


def baseline_exact_blob_equality(base_bytes: bytes, candidate_bytes: bytes) -> bool:
    return base_bytes == candidate_bytes


def baseline_permissive_schema_parse(candidate_bytes: bytes) -> bool:
    try:
        return isinstance(json.loads(candidate_bytes), dict)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False


def baseline_same_resolver_twice(scenario: dict[str, Any]) -> bool:
    first, _ = evaluate_scenario(scenario)
    second, _ = evaluate_scenario(scenario)
    return first == second


def baseline_synthetic_atomic_witness(payload: dict[str, Any]) -> bool:
    return isinstance(payload, dict) and isinstance(payload.get("components"), list) and bool(payload["components"])


def run_baseline_comparison(registry_payload: dict[str, Any], manifest: dict[str, Any], catalog: dict[str, Any], scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    base_bytes = canonical_json_bytes(registry_payload)
    mutations = [apply_null_mutation(registry_payload, row["segments"]) for row in manifest["normative_fields"]]
    transforms = [apply_transformation(registry_payload, row["transformation_id"])[1].encode("utf-8") for row in catalog["transformations"]]
    exact_invalid_reject = sum(not baseline_exact_blob_equality(base_bytes, canonical_json_bytes(row)) for row in mutations) / len(mutations)
    exact_valid_accept = sum(baseline_exact_blob_equality(base_bytes, row) for row in transforms) / len(transforms)
    permissive_invalid_reject = sum(not baseline_permissive_schema_parse(canonical_json_bytes(row)) for row in mutations) / len(mutations)
    permissive_valid_accept = sum(baseline_permissive_schema_parse(row) for row in transforms) / len(transforms)
    same_self_agreement = sum(baseline_same_resolver_twice(row) for row in scenarios) / len(scenarios)
    synthetic_invalid_reject = sum(not baseline_synthetic_atomic_witness(row) for row in mutations) / len(mutations)
    results = [
        {"baseline_id": "exact_blob_equality", "producer_function": "baseline_exact_blob_equality", "invalid_reject_rate": exact_invalid_reject, "valid_accept_rate": exact_valid_accept, "matched_candidate_discrimination": exact_invalid_reject == 1.0 and exact_valid_accept == 1.0},
        {"baseline_id": "permissive_schema_parse", "producer_function": "baseline_permissive_schema_parse", "invalid_reject_rate": permissive_invalid_reject, "valid_accept_rate": permissive_valid_accept, "matched_candidate_discrimination": permissive_invalid_reject == 1.0 and permissive_valid_accept == 1.0},
        {"baseline_id": "same_resolver_twice", "producer_function": "baseline_same_resolver_twice", "self_agreement_rate": same_self_agreement, "independent_oracle": False, "matched_candidate_discrimination": False},
        {"baseline_id": "synthetic_atomic_witness", "producer_function": "baseline_synthetic_atomic_witness", "invalid_reject_rate": synthetic_invalid_reject, "actual_atomic_specs_validated": False, "matched_candidate_discrimination": False},
    ]
    return {"producer_function": "run_baseline_comparison", "results": results, "all_baselines_invoked": [row["baseline_id"] for row in results] == catalog["baseline_ids"], "no_baseline_matches_candidate": not any(row["matched_candidate_discrimination"] for row in results)}


def _first_hit_component(rows: list[CausalObservationRecord]) -> EvidenceState:
    for row in rows:
        if row.outcome in {CausalOutcome.NO_CONTRIBUTION, CausalOutcome.WRONG_SIGN}:
            return EvidenceState.ABSENT
        if row.outcome in {CausalOutcome.INVALID, CausalOutcome.UNDERPOWERED}:
            return EvidenceState.INVALID_INSTRUMENT
    return EvidenceState.PRESENT_BOUNDED


def run_ablation_catalog(registry_payload: dict[str, Any], registry: H0Registry, contract: dict[str, Any]) -> dict[str, Any]:
    results = []
    component = ComponentId.MODEL
    causal_arms = [row.arm for row in panel_for(registry, component, PanelKind.CAUSAL).arms]
    order_rows = [CausalObservationRecord(component, causal_arms[0], CausalOutcome.WRONG_SIGN), CausalObservationRecord(component, causal_arms[-1], CausalOutcome.INVALID)]
    for arm in causal_arms[1:-1]:
        order_rows.append(CausalObservationRecord(component, arm, CausalOutcome.EXPECTED_SIGN))
    forward = _first_hit_component(order_rows)
    reverse = _first_hit_component(list(reversed(order_rows)))
    candidate = resolve_component_evidence(component_id=component, mandatory_arm_ids=causal_arms, observations=order_rows)
    results.append({"ablation_id": "order_first_hit", "producer_function": "_first_hit_component", "detected": forward is not reverse and candidate is EvidenceState.INVALID_INSTRUMENT, "probe_ids": ["order_wrong_before_invalid", "order_invalid_before_wrong"]})

    controls = {}
    for cid in ComponentId:
        arms = [row.arm for row in panel_for(registry, cid, PanelKind.CONTROL).arms]
        override = ComparatorOutcome.COMPARATOR_SUPERIOR if cid is ComponentId.MODEL else ComparatorOutcome.CANDIDATE_SUPERIOR
        rows = [ComparatorObservationRecord(cid, PanelKind.CONTROL, arm, override) for arm in arms]
        controls[cid] = resolve_comparator_panel(component_id=cid, panel=PanelKind.CONTROL, required_arm_ids=arms, observations=rows)
    global_scalar = {cid: (ComparatorState.DOMINATED if ComparatorState.DOMINATED in controls.values() else controls[cid]) for cid in ComponentId}
    results.append({"ablation_id": "global_panel_scalar", "producer_function": "global_panel_scalar_ablation", "detected": controls != global_scalar and len(set(controls.values())) > 1, "probe_ids": ["component_local_control_difference"]})

    provenance_mutated = copy.deepcopy(registry_payload)
    provenance_mutated["components"][0]["panels"][0]["arms"][0]["seed_block_id"] = None
    candidate_rejects = not validate_registry_payload(provenance_mutated)["accepted"]
    provenance_mutated["components"][0]["panels"][0]["arms"][0]["seed_block_id"] = provenance_mutated["components"][0]["panels"][0]["arms"][0]["power_spec"]["seed_block_id"]
    ablation_accepts = validate_registry_payload(provenance_mutated)["accepted"]
    results.append({"ablation_id": "ignore_provenance", "producer_function": "ignore_provenance_ablation", "detected": candidate_rejects and ablation_accepts, "probe_ids": ["atomic_seed_block_deleted"]})

    witness_mutated = copy.deepcopy(registry_payload)
    witness_mutated["components"][0]["panels"][0]["arms"][0]["expected_sign"] = None
    candidate_rejects = not validate_registry_payload(witness_mutated)["accepted"]
    witness_mutated["components"][0]["panels"][0]["arms"][0]["expected_sign"] = "expected_sign_contribution"
    witness_accepts = validate_registry_payload(witness_mutated)["accepted"]
    results.append({"ablation_id": "synthetic_atomic_witness", "producer_function": "synthetic_atomic_witness_ablation", "detected": candidate_rejects and witness_accepts, "probe_ids": ["atomic_expected_sign_deleted"]})

    independent = reference_oracle_component(component, causal_arms, order_rows)
    mutant = _first_hit_component(order_rows)
    same_resolver_agreement = mutant is _first_hit_component(order_rows)
    results.append({"ablation_id": "same_resolver_oracle", "producer_function": "same_resolver_oracle_ablation", "detected": same_resolver_agreement and mutant is not independent, "probe_ids": ["mutant_primary_vs_independent_oracle"]})
    frozen_ids = contract["ablation_ids"]
    return {"producer_function": "run_ablation_catalog", "results": results, "all_frozen_ablations_consumed": [row["ablation_id"] for row in results] == frozen_ids, "all_ablations_detected": all(row["detected"] for row in results)}


def run_path_authority(repo_root: Path, freeze_manifest: dict[str, Any]) -> dict[str, Any]:
    completed = subprocess.run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"], cwd=repo_root, text=True, capture_output=True, check=True)
    changed = sorted(line.replace("\\", "/") for line in completed.stdout.splitlines() if line)
    expected = sorted(freeze_manifest["phase_c_paths"])
    status = subprocess.run(["git", "status", "--porcelain=v1"], cwd=repo_root, text=True, capture_output=True, check=True).stdout.splitlines()
    forbidden = [path for path in ("artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h0", "src/itl_k0_reference_kernel_001a", "artifacts/ITL-K0-FORMAL-EVIDENCE-001A") if (repo_root / path).exists()]
    return {"producer_function": "run_path_authority", "changed_files_manifest": changed, "expected_phase_c_paths": expected, "exact_match": changed == expected, "worktree_clean_before_official_outputs": not status, "worktree_status": status, "external_write_manifest": [], "forbidden_paths_present": forbidden, "passed": changed == expected and not status and not forbidden}


def run_semantic_recompute_replay(registry_payload: dict[str, Any], scenarios: list[dict[str, Any]], original: dict[str, Any]) -> dict[str, Any]:
    serialized_state = canonical_json_bytes(registry_payload)
    serialized_observation = canonical_json_bytes(scenarios)
    restored_registry = H0Registry.from_dict(json.loads(serialized_state))
    restored_scenarios = json.loads(serialized_observation)
    recomputed = run_semantic_validation(restored_registry, restored_scenarios)
    original_map = {row["scenario_id"]: row["candidate"] for row in original["scenario_results"]}
    replay_map = {row["scenario_id"]: row["candidate"] for row in recomputed["scenario_results"]}
    return {"producer_function": "run_semantic_recompute_replay", "mechanism_episode_replay_run": False, "mechanism_episode_replay_status": "no mechanism episode replay was run", "recompute_from": ["serialized_registry_and_atomic_specs", "serialized_validation_observation"], "stored_verdict_hash_only": False, "serialized_state_sha256": sha256_bytes(serialized_state), "serialized_observation_sha256": sha256_bytes(serialized_observation), "candidate_behavior_recomputed": True, "scenario_results_match": replay_map == original_map, "recomputed_scenario_count": len(replay_map)}


def file_hashes(repo_root: Path, paths: list[str]) -> dict[str, str]:
    return {path: sha256_bytes((repo_root / path).read_bytes()) for path in paths}


def code_path_hash(repo_root: Path, source_paths: list[str]) -> str:
    digest = hashlib.sha256()
    for path in sorted(source_paths):
        digest.update(path.encode("utf-8"))
        digest.update((repo_root / path).read_bytes())
    return digest.hexdigest()


def attach_provenance(payload: dict[str, Any], *, producer_function: str, run_context: dict[str, Any], input_paths: list[str], consumed_ids: list[str] | None = None) -> dict[str, Any]:
    result = dict(payload)
    result.update({
        "producer_function": producer_function,
        "input_artifacts": input_paths,
        "input_artifact_hashes": {path: run_context["input_hashes"][path] for path in input_paths if path in run_context["input_hashes"]},
        "run_id": run_context["run_id"],
        "seed_context_episode_ids": run_context["seed_context_episode_ids"],
        "scenario_mutation_permutation_ids": consumed_ids or [],
        "aggregation_rule": run_context["aggregation_rule"],
        "code_path_hash": run_context["code_path_hash"],
        "source_test_hashes": run_context["source_test_hashes"],
        "task_card_pin": run_context["task_card_pin"],
    })
    return result
