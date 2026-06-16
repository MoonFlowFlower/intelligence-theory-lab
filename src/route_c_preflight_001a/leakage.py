from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from . import provenance
from . import core


CONTROL_CLASSES = {
    "L1": "self-set-in-legal",
    "L2": "identity-not-permuted",
    "L3": "action-label-alias",
    "L4": "answer-in-query",
    "L5": "confounder-in-legal",
    "L6": "api-effect-label",
    "L7": "schema-only-positive-control",
    "L8": "oracle-reachable",
}


def _map_legal(bundle: dict[str, Any], mutator: Callable[[dict[str, Any], dict[str, Any]], None]) -> dict[str, Any]:
    copied = deepcopy(bundle)
    for episode in copied["episodes"]:
        mutator(episode, episode["legal"])
        mutator(episode, episode["interventional_legal"])
    return copied


def inject_hidden_self_set_as_legal_field(bundle: dict[str, Any]) -> dict[str, Any]:
    def mutate(episode: dict[str, Any], legal: dict[str, Any]) -> None:
        truth = set(episode["truth_self_handles"])
        legal["leaked_self_membership_by_handle"] = {handle: handle in truth for handle in legal["handles"]}

    return _map_legal(bundle, mutate)


def inject_unpermuted_channel_ids(bundle: dict[str, Any]) -> dict[str, Any]:
    def mutate(_episode: dict[str, Any], legal: dict[str, Any]) -> None:
        legal["original_index_by_handle"] = {handle: index for index, handle in enumerate(legal["handles"])}

    return _map_legal(bundle, mutate)


def inject_action_label_alias(bundle: dict[str, Any]) -> dict[str, Any]:
    copied = deepcopy(bundle)
    for episode in copied["episodes"]:
        truth = set(episode["truth_self_handles"])
        for row in episode["interventional_legal"]["intervention_log"]:
            row["metadata"]["action_label_alias"] = "target_self_channel" if row["target_handle"] in truth else "target_other_channel"
    return copied


def inject_query_label(bundle: dict[str, Any]) -> dict[str, Any]:
    def mutate(episode: dict[str, Any], legal: dict[str, Any]) -> None:
        legal["query"]["answer_handles"] = list(episode["truth_self_handles"])

    return _map_legal(bundle, mutate)


def inject_confounder_label(bundle: dict[str, Any]) -> dict[str, Any]:
    def mutate(episode: dict[str, Any], legal: dict[str, Any]) -> None:
        truth = set(episode["truth_self_handles"])
        legal["confounder_self_membership_by_handle"] = {handle: handle in truth for handle in legal["handles"]}

    return _map_legal(bundle, mutate)


def inject_intervention_return_shape_leak(bundle: dict[str, Any]) -> dict[str, Any]:
    copied = deepcopy(bundle)
    for episode in copied["episodes"]:
        truth = set(episode["truth_self_handles"])
        for row in episode["interventional_legal"]["intervention_log"]:
            row["metadata"]["responded_channel_flag"] = row["target_handle"] in truth
            row["metadata"]["effect_size_label"] = "self_effect" if row["target_handle"] in truth else "no_effect"
    return copied


def inject_schema_only_attack(bundle: dict[str, Any]) -> dict[str, Any]:
    def mutate(episode: dict[str, Any], legal: dict[str, Any]) -> None:
        truth = set(episode["truth_self_handles"])
        legal["schema_alias_by_handle"] = {
            handle: f"self_{index}" if handle in truth else f"other_{index}"
            for index, handle in enumerate(legal["handles"])
        }

    return _map_legal(bundle, mutate)


def inject_oracle_formula_import(bundle: dict[str, Any]) -> dict[str, Any]:
    copied = deepcopy(bundle)
    copied["legal_function_scan"] = {
        "module": "legal_consumer",
        "source": "def illegal_reader(hidden):\n    return hidden.self_set_original\n",
    }
    return copied


def _detect_from_legal(legal: dict[str, Any], hits: set[str]) -> None:
    if "leaked_self_membership_by_handle" in legal:
        hits.add("self-set-in-legal")
    if "original_index_by_handle" in legal:
        hits.add("identity-not-permuted")
    if "answer_handles" in legal.get("query", {}):
        hits.add("answer-in-query")
    if "confounder_self_membership_by_handle" in legal:
        hits.add("confounder-in-legal")
    aliases = legal.get("schema_alias_by_handle", {})
    if any("self" in str(alias).lower() or "target" in str(alias).lower() for alias in aliases.values()):
        hits.add("schema-only-positive-control")
    for row in legal.get("intervention_log", []):
        metadata = row.get("metadata", {})
        if "action_label_alias" in metadata:
            hits.add("action-label-alias")
        if "responded_channel_flag" in metadata or "effect_size_label" in metadata:
            hits.add("api-effect-label")


def scan_bundle_for_leakage(bundle: dict[str, Any]) -> dict[str, Any]:
    hits: set[str] = set()
    for episode in bundle["episodes"]:
        _detect_from_legal(episode["legal"], hits)
        _detect_from_legal(episode["interventional_legal"], hits)
    source = bundle.get("legal_function_scan", {}).get("source", "")
    if any(token in source for token in ("self_set_original", "truth_self_handles", "confounder", "gain")):
        hits.add("oracle-reachable")
    return {
        "producer_function": provenance.producer_name(scan_bundle_for_leakage),
        "detected_classes": sorted(hits),
        "verdict": "clean" if not hits else "blocked",
    }


def run_leakage_positive_controls(*, bundle: dict[str, Any], config: core.Config, run_id: str) -> dict[str, Any]:
    clean_scan = scan_bundle_for_leakage(bundle)
    controls = {
        "L1": inject_hidden_self_set_as_legal_field,
        "L2": inject_unpermuted_channel_ids,
        "L3": inject_action_label_alias,
        "L4": inject_query_label,
        "L5": inject_confounder_label,
        "L6": inject_intervention_return_shape_leak,
        "L7": inject_schema_only_attack,
        "L8": inject_oracle_formula_import,
    }
    control_results = {}
    for control_id, injector in controls.items():
        injected = injector(bundle)
        scan = scan_bundle_for_leakage(injected)
        expected = CONTROL_CLASSES[control_id]
        fired = expected in scan["detected_classes"]
        gate_verdict = None
        if control_id in {"L1", "L5", "L7"}:
            panel = core.run_baseline_panel(injected, run_id=f"{run_id}-{control_id}-panel")
            gate_verdict = core.non_identifiability_premise_gate(panel, config=config)["verdict"]
            if control_id == "L1":
                fired = fired and gate_verdict == "blocked_by_observation_decodable_self_set"
            if control_id == "L7":
                fired = fired and gate_verdict == "blocked_by_schema_alias_leakage"
        control_results[control_id] = {
            "expected_class": expected,
            "detected_classes": scan["detected_classes"],
            "gate_verdict": gate_verdict,
            "fired": fired,
        }
    return {
        "producer_function": provenance.producer_name(run_leakage_positive_controls),
        "run_id": run_id,
        "clean_case": clean_scan,
        "control_results": control_results,
        "all_controls_fired": all(row["fired"] for row in control_results.values()),
        "blocking_verdict": None
        if clean_scan["verdict"] == "clean" and all(row["fired"] for row in control_results.values())
        else "blocked_by_non_fail_able_control",
    }
