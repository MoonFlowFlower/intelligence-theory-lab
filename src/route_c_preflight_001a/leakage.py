from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from . import provenance
from . import core


# Value offset used by the value-level decodable control. Large vs the unit
# confounder / 0.15 noise scale so a legal passive mean attacker decodes S
# without any answer key. NOT a threshold; it is the injected leak magnitude.
VALUE_LEAK_OFFSET = 5.0


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

# How each control is wired. gate_coupled controls drive a real fail-closed gate
# verdict; synthetic_detector_only controls only demonstrate that the key/name
# scanner fires on a planted token (NOT, by themselves, fail-closed safety
# evidence -- per the hostile audit, they are reported as synthetic-only).
CONTROL_TYPES = {
    "L1": "gate_coupled",
    "L2": "synthetic_detector_only",
    "L3": "synthetic_detector_only",
    "L4": "synthetic_detector_only",
    "L5": "gate_coupled",
    "L6": "synthetic_detector_only",
    "L7": "gate_coupled",
    "L8": "synthetic_detector_only",
    "L9": "gate_coupled_value_level",
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


def inject_observation_value_decodable_self_set(bundle: dict[str, Any], *, leak: float = VALUE_LEAK_OFFSET) -> dict[str, Any]:
    """L9 (value-level): leak S into passive handle_values, NOT into any key,
    label, name, schema alias, membership dict, or query field.

    Adds a fixed offset to the passive VALUES of the self channels. A legal
    passive mean/cross-episode attacker that reads only
    passive_rows[*].handle_values decodes S; the key/name scanner stays silent
    (there is no token to grep). This is the fail-able control the audit
    required: it must drive the value-level attacker family to ~1.0 and force
    blocked_by_observation_decodable_self_set.
    """
    copied = deepcopy(bundle)
    for episode in copied["episodes"]:
        truth = set(episode["truth_self_handles"])
        for view_key in ("legal", "interventional_legal"):
            for row in episode[view_key]["passive_rows"]:
                for handle in truth:
                    row["handle_values"][handle] = float(row["handle_values"][handle]) + leak
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
    """Key/name scanner. Detects planted answer keys/aliases by name. It is, by
    design, BLIND to value-level leakage (L9) -- that is caught by the attacker
    family + premise gate, not by name-grep."""
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


def _premise_gate_verdict(bundle: dict[str, Any], config: core.Config, run_id: str) -> dict[str, Any]:
    panel = core.run_baseline_panel(bundle, run_id=run_id)
    gate = core.non_identifiability_premise_gate(panel, config=config)
    return {
        "verdict": gate["verdict"],
        "family_max": panel["obs_only"]["family_max"]["value"],
        "family_max_attacker": panel["obs_only"]["family_max_attacker"],
        "value_level_family_max": panel["obs_only"]["value_level_family_max"],
    }


def _value_level_attacker_names() -> set[str]:
    return {name for name, _fn, value_level, _weak in core.PASSIVE_ATTACKER_FAMILY if value_level}


def run_leakage_positive_controls(
    *,
    bundle: dict[str, Any],
    config: core.Config,
    run_id: str,
    threshold_snapshot_hash: str | None = None,
) -> dict[str, Any]:
    if threshold_snapshot_hash is None:
        threshold_snapshot_hash = provenance.build_threshold_snapshot(config=config, config_type=core.Config)["snapshot_hash"]
    clean_scan = scan_bundle_for_leakage(bundle)

    key_controls = {
        "L1": inject_hidden_self_set_as_legal_field,
        "L2": inject_unpermuted_channel_ids,
        "L3": inject_action_label_alias,
        "L4": inject_query_label,
        "L5": inject_confounder_label,
        "L6": inject_intervention_return_shape_leak,
        "L7": inject_schema_only_attack,
        "L8": inject_oracle_formula_import,
    }
    control_results: dict[str, Any] = {}
    for control_id, injector in key_controls.items():
        injected = injector(bundle)
        scan = scan_bundle_for_leakage(injected)
        expected = CONTROL_CLASSES[control_id]
        fired = expected in scan["detected_classes"]
        gate_verdict = None
        if control_id in {"L1", "L5", "L7"}:
            gate = _premise_gate_verdict(injected, config, f"{run_id}-{control_id}-panel")
            gate_verdict = gate["verdict"]
            if control_id in {"L1", "L5"}:
                fired = fired and gate_verdict == "blocked_by_observation_decodable_self_set"
            if control_id == "L7":
                fired = fired and gate_verdict == "blocked_by_schema_alias_leakage"
        control_results[control_id] = {
            "control_type": CONTROL_TYPES[control_id],
            "value_level": False,
            "expected_class": expected,
            "detected_classes": scan["detected_classes"],
            "gate_verdict": gate_verdict,
            "fired": fired,
            "note": (
                "synthetic detector-only: proves the key/name scanner fires on the planted token; "
                "not, by itself, a fail-closed gate path"
                if CONTROL_TYPES[control_id] == "synthetic_detector_only"
                else "gate-coupled: drives a fail-closed premise/schema gate verdict"
            ),
        }

    # L9 value-level decodable control (gate-coupled; caught by the attacker
    # family, invisible to the key/name scanner).
    l9_injected = inject_observation_value_decodable_self_set(bundle)
    l9_scan = scan_bundle_for_leakage(l9_injected)  # expected: still clean (no token)
    l9_gate = _premise_gate_verdict(l9_injected, config, f"{run_id}-L9-panel")
    l9_decoded_by_value_level = l9_gate["family_max_attacker"] in _value_level_attacker_names()
    l9_fired = (
        l9_gate["verdict"] == "blocked_by_observation_decodable_self_set"
        and l9_decoded_by_value_level
        and l9_gate["value_level_family_max"] > config.premise_threshold
    )
    control_results["L9"] = {
        "control_type": CONTROL_TYPES["L9"],
        "value_level": True,
        "expected_class": "observation-value-decodable",
        "detected_classes": l9_scan["detected_classes"],
        "key_scanner_silent": l9_scan["verdict"] == "clean",
        "gate_verdict": l9_gate["verdict"],
        "family_max": l9_gate["family_max"],
        "family_max_attacker": l9_gate["family_max_attacker"],
        "value_level_family_max": l9_gate["value_level_family_max"],
        "decoded_by_value_level_attacker": l9_decoded_by_value_level,
        "fired": l9_fired,
        "note": "value-level leak in passive handle_values; decoded by a passive value attacker, not by name-grep",
    }

    all_controls_fired = all(row["fired"] for row in control_results.values())
    clean_is_clean = clean_scan["verdict"] == "clean"

    # Leakage fail-able self-check: replace L1's injector with a no-op so its
    # control cannot fire; the subsystem MUST then refuse to certify (block).
    def _noop_injector(b: dict[str, Any]) -> dict[str, Any]:
        return deepcopy(b)

    probe_injected = _noop_injector(bundle)
    probe_scan = scan_bundle_for_leakage(probe_injected)
    probe_fired = CONTROL_CLASSES["L1"] in probe_scan["detected_classes"]  # expected False
    probe_blocks = not probe_fired  # subsystem blocks because a control failed to fire
    failure_probe = {
        "description": "L1 injector replaced by no-op; control must fail to fire and force a block",
        "control_fired": probe_fired,
        "subsystem_blocks": probe_blocks,
        "blocking_verdict": None if probe_fired else "blocked_by_non_fail_able_control",
    }

    blocking_verdict = None if (clean_is_clean and all_controls_fired) else "blocked_by_non_fail_able_control"

    leakage_record = provenance.material_record(
        value=1.0 if (clean_is_clean and all_controls_fired) else 0.0,
        producer_function=run_leakage_positive_controls,
        inputs={
            "controls": sorted(control_results),
            "clean_verdict": clean_scan["verdict"],
            "config_hash": provenance.sha256_json(bundle["config"]),
        },
        run_id=run_id,
        seed="multi_seed",
        episode_ids=[e["episode_id"] for e in bundle["episodes"]],
        aggregation="all_controls_fired_and_clean_is_clean",
        threshold_used=None,
        threshold_snapshot_hash=threshold_snapshot_hash,
        subsystem="leakage",
        recompute_basis={"kind": "indicator", "predicate": bool(clean_is_clean and all_controls_fired)},
    )

    return {
        "producer_function": provenance.producer_name(run_leakage_positive_controls),
        "run_id": run_id,
        "clean_case": clean_scan,
        "control_results": control_results,
        "all_controls_fired": all_controls_fired,
        "clean_is_clean": clean_is_clean,
        "value_level_control": control_results["L9"],
        "failure_probe": failure_probe,
        "blocking_verdict": blocking_verdict,
        "provenance_record": leakage_record,
    }
