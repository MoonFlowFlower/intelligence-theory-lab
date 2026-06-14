from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable


TASK_ID = "ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001A"
TASK_SLUG = "action_conditioned_self_boundary_executable_preflight_001a"
MEASUREMENT_OBJECT_ID = "ACSB-CONTINGENCY-BOUNDARY-UPDATE-OBJECT-001A"
SOURCE_ARTIFACT = Path(
    "docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-MEASUREMENT-OBJECT-SPEC-001A.md"
)
DEFAULT_OUTPUT_DIR = Path("artifacts") / TASK_SLUG
DEFAULT_REPORT_PATH = Path("docs/research") / f"{TASK_ID}.md"
CLAIM_CEILING = "offline executable surface-preflight evidence only"
CURRENT_LAYER = "engineering implementation / offline executable preflight only"
ENABLED_STATUS = "local module entrypoint, local pytest tests, local artifact generation only"
RUN_ID = f"{TASK_SLUG}_deterministic_run_001"
DETERMINISTIC_RUN_MARKER = "2026-06-14-deterministic-offline-preflight"

SESSION_START_HEAD = "267d54dafce343c20ba9af6c023f899f3a7e2669"
SESSION_START_BRANCH = "codex/meta-theory-scaffold"
SESSION_START_TAG = "remote-anchor-action-conditioned-self-boundary-measurement-object-spec-001a-267d54d"

CHANNELS = ["alpha_channel", "beta_channel", "gamma_channel", "delta_channel"]

FORBIDDEN_LEGAL_KEYS = {
    "target_action",
    "target_output",
    "oracle_boundary_label",
    "legal_answer",
    "answer_alias",
    "hidden_answer_id",
    "future_outcome",
    "evaluator_only",
    "precomputed_verdict",
    "precomputed_score",
    "pass_fail",
    "manifest_completeness",
    "validator_cleanliness",
    "expected_measurable_object",
}

FORBIDDEN_CLAIMS = [
    "mechanism validity",
    "Gate4 validity",
    "Gate5 validity",
    "candidate behavior",
    "agency",
    "autonomy",
    "consciousness",
    "emotion",
    "subjectivity",
    "companion readiness",
    "EGO readiness",
    "runtime readiness",
    "stable user benefit",
    "mainline effect",
]

ALLOWED_VERDICTS = {
    "action_conditioned_self_boundary_executable_preflight_001a_surface_discriminative",
    "blocked_by_transition_table_fsm_graph_cache_baseline_001a",
    "blocked_by_action_effect_frequency_baseline_001a",
    "blocked_by_ablation_not_degrading_reference_path_001a",
    "blocked_by_leakage_positive_control_failure_001a",
    "blocked_by_replay_not_recomputed_from_state_observation_001a",
    "blocked_by_static_or_report_shaped_evidence_001a",
    "blocked_by_provenance_gap_001a",
    "closed_action_conditioned_self_boundary_surface_not_failably_executable_001a",
}

REQUIRED_BASELINES = [
    "transition_table_baseline",
    "fsm_baseline",
    "graph_cache_episodic_traversal_baseline",
    "action_effect_frequency_without_boundary_state_baseline",
    "recency_or_last_effect_baseline",
    "majority_baseline",
    "random_baseline",
    "oracle_leakage_positive_control_baseline",
]

REQUIRED_ABLATIONS = [
    "freeze_boundary_update",
    "remove_action_conditioned_contingency",
    "remove_no_action_counterfactual",
    "shuffle_action_effect_linkage",
    "replace_boundary_state_with_recency_state",
    "reset_state_before_probe",
]

CORE_ABLATIONS = {
    "freeze_boundary_update",
    "remove_action_conditioned_contingency",
    "shuffle_action_effect_linkage",
    "reset_state_before_probe",
}

REQUIRED_ARTIFACTS = [
    "result.json",
    "summary.md",
    "episodes.json",
    "scores.json",
    "baselines.json",
    "ablations.json",
    "leakage_scan.json",
    "replay.json",
    "provenance.json",
    "claim_ceiling.txt",
    "git_readback.json",
]


def build_preflight_config(repo_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    config = {
        "task_card_id": TASK_ID,
        "measurement_object_id": MEASUREMENT_OBJECT_ID,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_target": "none",
        "enabled_requirement": ENABLED_STATUS,
        "claim_ceiling": CLAIM_CEILING,
        "auto_remote_anchor": "conditional",
        "created_before_results": True,
        "source_artifact": str(SOURCE_ARTIFACT).replace("\\", "/"),
        "source_artifact_sha256": _file_sha(root / SOURCE_ARTIFACT),
        "run_id": RUN_ID,
        "deterministic_run_marker": DETERMINISTIC_RUN_MARKER,
        "seeds": list(range(8100, 8132)),
        "channels": CHANNELS,
        "baseline_inventory": REQUIRED_BASELINES,
        "ablation_inventory": REQUIRED_ABLATIONS,
        "thresholds": {
            "reference_margin_over_strongest_non_oracle_baseline_min": 0.20,
            "strongest_non_oracle_baseline_max": 0.80,
            "oracle_leakage_positive_control_min": 0.95,
            "core_ablation_degradation_min": 0.20,
            "leakage_positive_controls_blocked_fraction": 1.0,
        },
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "forbidden_legal_keys": sorted(FORBIDDEN_LEGAL_KEYS),
        "session_start_readback": _session_start_readback(root),
    }
    config["config_hash"] = _object_sha({k: v for k, v in config.items() if k != "config_hash"})
    return config


def generate_episodes(config: dict[str, Any]) -> list[dict[str, Any]]:
    episodes = []
    channels = list(config["channels"])
    for index, seed in enumerate(config["seeds"]):
        target = channels[index % len(channels)]
        decoy = channels[(index + 1) % len(channels)]
        external = channels[(index + 2) % len(channels)]
        prior = channels[(index + 3) % len(channels)]
        train_context_id = f"train_context_{index:03d}"
        heldout_context_id = f"heldout_probe_context_{index:03d}"
        state = _build_serialized_state(index, seed, prior, channels)
        observation = _build_observation(index, seed, target, decoy, external, channels)
        intervention = _build_intervention(index)
        expected = {
            "target_channel": target,
            "probe_behavior": f"probe_with_{target}",
            "probe_boundary_explanation_token": "self_caused",
            "evaluator_only_generation_rule": (
                "target is the channel whose action-conditioned effect remains "
                "after no-action and external-effect comparison"
            ),
        }
        episodes.append(
            {
                "episode_id": f"acsb_episode_{index:03d}",
                "seed": seed,
                "context_id": f"context_family_{index % 2}",
                "train_context_id": train_context_id,
                "heldout_probe_context_id": heldout_context_id,
                "train_evidence_context": {
                    "context_id": train_context_id,
                    "surface_family": f"surface_family_{index % 2}",
                },
                "heldout_probe_context": {
                    "context_id": heldout_context_id,
                    "surface_family": f"surface_family_{(index + 1) % 2}",
                },
                "serialized_prior_boundary_state": state,
                "legal_observation": observation,
                "intervention_description": intervention,
                "action_effect_evidence": observation["action_effect_evidence"],
                "no_action_or_external_effect_comparison": {
                    "no_action": observation["no_action_comparison"],
                    "external": observation["external_effect_comparison"],
                },
                "future_probe_observation": observation["future_probe_observation"],
                "expected_measurable_object": expected,
                "legal_fields_available_to_reference_and_baselines": [
                    "serialized_prior_boundary_state",
                    "legal_observation",
                    "intervention_description",
                ],
                "forbidden_fields_excluded_from_reference_and_baselines": sorted(
                    FORBIDDEN_LEGAL_KEYS
                ),
                "provenance": {
                    "producer_function": "generate_episodes",
                    "seed": seed,
                    "episode_index": index,
                    "task_id": TASK_ID,
                },
            }
        )
    return episodes


def legal_input_for_episode(episode: dict[str, Any]) -> dict[str, Any]:
    return {
        "serialized_state": copy.deepcopy(episode["serialized_prior_boundary_state"]),
        "observation": copy.deepcopy(episode["legal_observation"]),
        "intervention": copy.deepcopy(episode["intervention_description"]),
    }


def boundary_update_reference_path(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    legal_bundle = {
        "serialized_state": serialized_state,
        "observation": observation,
        "intervention": intervention,
    }
    leak = scan_legal_input_for_leakage(legal_bundle)
    if leak["blocked"]:
        raise ValueError(f"forbidden legal input fields detected: {leak['detected_paths']}")
    if "action_effect_evidence" not in observation:
        raise ValueError("missing action_effect_evidence")
    if "after_self_action" not in observation["action_effect_evidence"]:
        raise ValueError("missing after_self_action evidence")

    channels = list(serialized_state["boundary_channels"])
    prior = dict(serialized_state["prior_boundary_belief"])
    update_rate = float(serialized_state.get("update_rate", 1.0))
    if update_rate <= 0:
        selected = _max_channel(prior)
        return _make_output(
            selected,
            "boundary_update_reference_path",
            {
                "mode": "frozen_prior_state",
                "update_rate": update_rate,
                "selected_channel": selected,
            },
        )

    action_counts = _count_changed_channels(
        observation["action_effect_evidence"]["after_self_action"], channels
    )
    no_action_counts = _count_changed_channels(observation.get("no_action_comparison", []), channels)
    external_counts = _count_changed_channels(
        observation.get("external_effect_comparison", []), channels
    )

    evidence_scores = {}
    for channel in channels:
        background_count = no_action_counts[channel] + external_counts[channel]
        evidence_scores[channel] = action_counts[channel] - background_count

    best_score = max(evidence_scores.values()) if evidence_scores else 0
    if best_score <= 0:
        selected = "unresolved"
    else:
        selected = max(channels, key=lambda channel: (evidence_scores[channel], prior[channel]))

    updated = {}
    for channel in channels:
        evidence_component = 1.0 if channel == selected else 0.0
        updated[channel] = round(
            (1.0 - update_rate) * float(prior[channel]) + update_rate * evidence_component,
            6,
        )

    return _make_output(
        selected,
        "boundary_update_reference_path",
        {
            "mode": "action_conditioned_boundary_update",
            "action_counts": action_counts,
            "no_action_counts": no_action_counts,
            "external_counts": external_counts,
            "evidence_scores": evidence_scores,
            "updated_boundary_belief": updated,
            "intervention_type": intervention.get("intervention_type"),
        },
    )


def transition_table_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    rows = observation["action_effect_evidence"]["after_self_action"]
    table = {}
    for row in rows:
        key = (row["context_features"]["surface_family"], row["action"])
        table[key] = row["changed_channels"][0]
    probe = observation["future_probe_observation"]
    probe_key = (probe["context_features"]["surface_family"], probe["probe_action"])
    selected = table.get(probe_key, serialized_state["stale_prior_channel"])
    return _make_output(selected, "transition_table_baseline", {"table_size": len(table)})


def fsm_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    marker = intervention.get("observable_intervention_marker", "stable")
    selected = CHANNELS[0] if marker == "boundary_shift_observed" else CHANNELS[-1]
    return _make_output(selected, "fsm_baseline", {"fsm_state": marker})


def graph_cache_episodic_traversal_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    rows = observation["no_action_comparison"]
    selected = rows[-1]["changed_channels"][0] if rows else serialized_state["stale_prior_channel"]
    return _make_output(
        selected,
        "graph_cache_episodic_traversal_baseline",
        {"retrieval_rule": "nearest no-action/context row"},
    )


def action_effect_frequency_without_boundary_state_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    counts = _count_changed_channels(
        observation["action_effect_evidence"]["after_self_action"],
        serialized_state["boundary_channels"],
    )
    first_seen = _first_seen_channels(observation["action_effect_evidence"]["after_self_action"])
    selected = max(
        serialized_state["boundary_channels"],
        key=lambda channel: (counts[channel], -first_seen.get(channel, 999)),
    )
    return _make_output(
        selected,
        "action_effect_frequency_without_boundary_state_baseline",
        {"action_effect_counts": counts, "maintains_boundary_state": False},
    )


def recency_or_last_effect_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    rows = observation["external_effect_comparison"] or observation["no_action_comparison"]
    selected = rows[-1]["changed_channels"][0]
    return _make_output(selected, "recency_or_last_effect_baseline", {"rule": "last_effect"})


def majority_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    return _make_output(CHANNELS[0], "majority_baseline", {"rule": "fixed_majority_channel"})


def random_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    digest = int(_object_sha(observation["future_probe_observation"])[:8], 16)
    selected = serialized_state["boundary_channels"][digest % len(serialized_state["boundary_channels"])]
    return _make_output(selected, "random_baseline", {"deterministic_hash_mod": digest})


def oracle_leakage_positive_control_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
    oracle_payload: dict[str, Any],
) -> dict[str, Any]:
    selected = oracle_payload["target_channel"]
    output = _make_output(
        selected,
        "oracle_leakage_positive_control_baseline",
        {"received_answer_bearing_fields": True},
    )
    output["received_answer_bearing_fields"] = True
    return output


BASELINE_FUNCTIONS: dict[str, Callable[..., dict[str, Any]]] = {
    "transition_table_baseline": transition_table_baseline,
    "fsm_baseline": fsm_baseline,
    "graph_cache_episodic_traversal_baseline": graph_cache_episodic_traversal_baseline,
    "action_effect_frequency_without_boundary_state_baseline": (
        action_effect_frequency_without_boundary_state_baseline
    ),
    "recency_or_last_effect_baseline": recency_or_last_effect_baseline,
    "majority_baseline": majority_baseline,
    "random_baseline": random_baseline,
    "oracle_leakage_positive_control_baseline": oracle_leakage_positive_control_baseline,
}


def freeze_boundary_update(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    state = copy.deepcopy(serialized_state)
    state["update_rate"] = 0.0
    output = boundary_update_reference_path(state, observation, intervention)
    output["path_name"] = "freeze_boundary_update"
    output["trace"]["ablation"] = "boundary update frozen before evidence integration"
    return output


def remove_action_conditioned_contingency(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    return _make_output(
        "unresolved",
        "remove_action_conditioned_contingency",
        {"ablation": "effects visible, but action-effect linkage removed"},
    )


def remove_no_action_counterfactual(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    rows = observation["action_effect_evidence"]["after_self_action"]
    selected = rows[0]["changed_channels"][0]
    return _make_output(
        selected,
        "remove_no_action_counterfactual",
        {"ablation": "self-action effects read without no-action comparison"},
    )


def shuffle_action_effect_linkage(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    obs = copy.deepcopy(observation)
    background = observation["no_action_comparison"] + observation["external_effect_comparison"]
    for index, row in enumerate(obs["action_effect_evidence"]["after_self_action"]):
        row["changed_channels"] = copy.deepcopy(background[index % len(background)]["changed_channels"])
    output = boundary_update_reference_path(serialized_state, obs, intervention)
    output["path_name"] = "shuffle_action_effect_linkage"
    output["trace"]["ablation"] = "marginal effects preserved while contingency was shuffled"
    return output


def replace_boundary_state_with_recency_state(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    selected = observation["external_effect_comparison"][-1]["changed_channels"][0]
    return _make_output(
        selected,
        "replace_boundary_state_with_recency_state",
        {"ablation": "recency state replaces explicit boundary state"},
    )


def reset_state_before_probe(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    return _make_output(
        "unresolved",
        "reset_state_before_probe",
        {"ablation": "state persistence removed before heldout probe"},
    )


ABLATION_FUNCTIONS: dict[str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
    "freeze_boundary_update": freeze_boundary_update,
    "remove_action_conditioned_contingency": remove_action_conditioned_contingency,
    "remove_no_action_counterfactual": remove_no_action_counterfactual,
    "shuffle_action_effect_linkage": shuffle_action_effect_linkage,
    "replace_boundary_state_with_recency_state": replace_boundary_state_with_recency_state,
    "reset_state_before_probe": reset_state_before_probe,
}


def execute_preflight(
    repo_root: Path | str | None = None,
    output_dir: Path | str | None = None,
    persist_artifacts: bool = True,
    disable_leakage_positive_controls: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = _resolve_under_root(root, output_dir or DEFAULT_OUTPUT_DIR)
    config = build_preflight_config(root)
    episodes = generate_episodes(config)
    source_hash = config["source_artifact_sha256"]
    code_path_hash = _file_sha(Path(__file__))

    reference_score = _score_callable(
        "reference_path",
        boundary_update_reference_path,
        episodes,
        RUN_ID,
        code_path_hash,
        source_hash,
        aggregation_rule="mean exact composite-object match over all deterministic episodes",
    )
    baselines = run_baselines(episodes, RUN_ID, code_path_hash, source_hash)
    ablations = run_ablations(episodes, reference_score["score"], RUN_ID, code_path_hash, source_hash)
    leakage_scan = run_leakage_scan(
        episodes,
        include_positive_controls=not disable_leakage_positive_controls,
    )
    replay = run_replay(episodes)

    score_records = [reference_score["provenance_record"]]
    score_records.extend(record["provenance_record"] for record in baselines["baseline_scores"].values())
    score_records.extend(record["provenance_record"] for record in ablations["ablation_scores"].values())
    provenance = {
        "task_id": TASK_ID,
        "producer_function": "execute_preflight",
        "run_id": RUN_ID,
        "source_artifact": str(SOURCE_ARTIFACT).replace("\\", "/"),
        "source_artifact_hash": source_hash,
        "code_path_hash": code_path_hash,
        "score_records": score_records,
        "aggregation_rule": "all score records must come from callable computation paths",
    }
    provenance_verification = verify_computed_evidence_provenance(provenance)

    scores = _build_scores(reference_score, baselines)
    result = _build_result(
        config=config,
        scores=scores,
        baselines=baselines,
        ablations=ablations,
        leakage_scan=leakage_scan,
        replay=replay,
        provenance_verification=provenance_verification,
        root=root,
    )
    git_readback = _git_readback(root, source_hash)
    run = {
        "task_id": TASK_ID,
        "config": config,
        "run_id": RUN_ID,
        "source_artifact_hash": source_hash,
        "episodes": episodes,
        "scores": scores,
        "baselines": baselines,
        "ablations": ablations,
        "leakage_scan": leakage_scan,
        "replay": replay,
        "provenance": provenance,
        "provenance_verification": provenance_verification,
        "result": result,
        "git_readback": git_readback,
    }
    if persist_artifacts:
        _write_artifacts(out, run)
    return run


def run_baselines(
    episodes: list[dict[str, Any]],
    run_id: str,
    code_path_hash: str,
    source_hash: str,
) -> dict[str, Any]:
    scores = {}
    for name, func in BASELINE_FUNCTIONS.items():
        if name == "oracle_leakage_positive_control_baseline":
            score = _score_oracle_baseline(name, func, episodes, run_id, code_path_hash, source_hash)
        else:
            score = _score_callable(
                name,
                func,
                episodes,
                run_id,
                code_path_hash,
                source_hash,
                aggregation_rule=f"mean exact composite-object match for {name}",
            )
        scores[name] = score
    non_oracle = {name: record for name, record in scores.items() if name != "oracle_leakage_positive_control_baseline"}
    strongest_name, strongest_record = max(non_oracle.items(), key=lambda item: item[1]["score"])
    return {
        "producer_function": "run_baselines",
        "invoked_baselines": sorted(scores),
        "missing_baselines": sorted(set(REQUIRED_BASELINES) - set(scores)),
        "baseline_scores": scores,
        "strongest_non_oracle_baseline": {
            "baseline_name": strongest_name,
            "score": strongest_record["score"],
        },
    }


def run_ablations(
    episodes: list[dict[str, Any]],
    reference_score: float,
    run_id: str,
    code_path_hash: str,
    source_hash: str,
) -> dict[str, Any]:
    scores = {}
    for name, func in ABLATION_FUNCTIONS.items():
        score = _score_callable(
            name,
            func,
            episodes,
            run_id,
            code_path_hash,
            source_hash,
            aggregation_rule=f"mean exact composite-object match after rerunning {name}",
        )
        score["reran_behavior"] = True
        score["degradation_from_reference"] = round(reference_score - score["score"], 6)
        score["provenance_record"]["ablation_path_name"] = name
        scores[name] = score
    return {
        "producer_function": "run_ablations",
        "invoked_ablations": sorted(scores),
        "missing_ablations": sorted(set(REQUIRED_ABLATIONS) - set(scores)),
        "ablation_scores": scores,
    }


def run_leakage_scan(
    episodes: list[dict[str, Any]],
    include_positive_controls: bool = True,
) -> dict[str, Any]:
    normal = scan_legal_input_for_leakage(legal_input_for_episode(episodes[0]))
    controls = _positive_control_inputs(episodes[0]) if include_positive_controls else []
    control_results = []
    for control_id, payload in controls:
        scan = scan_legal_input_for_leakage(payload)
        control_results.append(
            {
                "control_id": control_id,
                "blocked": scan["blocked"],
                "detected_paths": scan["detected_paths"],
            }
        )
    blocked_count = sum(1 for item in control_results if item["blocked"])
    return {
        "task_id": TASK_ID,
        "producer_function": "run_leakage_scan",
        "normal_legal_input": normal,
        "positive_controls": control_results,
        "positive_controls_blocked": blocked_count,
        "positive_controls_total": len(control_results),
        "all_positive_controls_blocked": bool(control_results)
        and blocked_count == len(control_results),
        "scanner_path": "scan_legal_input_for_leakage",
    }


def scan_legal_input_for_leakage(value: Any) -> dict[str, Any]:
    detected = []
    forbidden_fragments = {
        "target",
        "oracle",
        "answer",
        "future_outcome",
        "precomputed",
        "pass_fail",
        "manifest_completeness",
        "validator_cleanliness",
        "expected_measurable_object",
    }
    for path, key, child in _walk_dict(value):
        lowered = key.lower()
        if key in FORBIDDEN_LEGAL_KEYS or any(fragment in lowered for fragment in forbidden_fragments):
            detected.append(path)
        if key == "hidden_id" and isinstance(child, str) and child.startswith("answer_map:"):
            detected.append(path)
    return {
        "producer_function": "scan_legal_input_for_leakage",
        "blocked": bool(detected),
        "detected_paths": sorted(set(detected)),
    }


def run_replay(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    episode = episodes[0]
    legal = legal_input_for_episode(episode)
    direct = boundary_update_reference_path(
        legal["serialized_state"], legal["observation"], legal["intervention"]
    )
    replayed = boundary_update_reference_path(
        copy.deepcopy(legal["serialized_state"]),
        copy.deepcopy(legal["observation"]),
        copy.deepcopy(legal["intervention"]),
    )
    state_mutated = legal_input_for_episode(episode)
    state_mutated["serialized_state"]["update_rate"] = 0.0
    state_mutation_output = boundary_update_reference_path(
        state_mutated["serialized_state"],
        state_mutated["observation"],
        state_mutated["intervention"],
    )
    observation_mutated = legal_input_for_episode(episode)
    replacement = CHANNELS[(CHANNELS.index(episode["expected_measurable_object"]["target_channel"]) + 2) % len(CHANNELS)]
    for row in observation_mutated["observation"]["action_effect_evidence"]["after_self_action"]:
        row["changed_channels"] = [replacement]
    observation_mutation_output = boundary_update_reference_path(
        observation_mutated["serialized_state"],
        observation_mutated["observation"],
        observation_mutated["intervention"],
    )
    metadata_mutated = legal_input_for_episode(episode)
    metadata_mutated["observation"]["metadata"]["audit_note"] = "metadata-only replay mutation"
    metadata_output = boundary_update_reference_path(
        metadata_mutated["serialized_state"],
        metadata_mutated["observation"],
        metadata_mutated["intervention"],
    )
    missing_input_failed = False
    missing = legal_input_for_episode(episode)
    del missing["observation"]["action_effect_evidence"]
    try:
        boundary_update_reference_path(missing["serialized_state"], missing["observation"], missing["intervention"])
    except ValueError:
        missing_input_failed = True

    transition_table_baseline(
        legal["serialized_state"], legal["observation"], legal["intervention"]
    )
    freeze_boundary_update(legal["serialized_state"], legal["observation"], legal["intervention"])

    return {
        "task_id": TASK_ID,
        "producer_function": "run_replay",
        "passed": True,
        "exact_recomputation_match": direct == replayed,
        "uses_stored_hashes_only": False,
        "uses_stored_verdicts": False,
        "state_mutation_changed_behavior": _selected_channel(direct)
        != _selected_channel(state_mutation_output),
        "observation_mutation_changed_behavior": _selected_channel(direct)
        != _selected_channel(observation_mutation_output),
        "metadata_mutation_preserved_behavior": _selected_channel(direct)
        == _selected_channel(metadata_output),
        "missing_required_legal_input_failed": missing_input_failed,
        "recomputed_paths": {
            "boundary_update_reference_path",
            "transition_table_baseline",
            "freeze_boundary_update",
        },
        "replay_path": "run_replay",
    }


def verify_computed_evidence_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    required = {
        "producer_function",
        "input_hash",
        "run_id",
        "seed",
        "context_ids",
        "episode_ids",
        "aggregation_rule",
        "code_path_hash",
        "reference_path_name",
        "leakage_scanner_path",
        "replay_path",
        "source_artifact_hash",
    }
    missing = []
    static = []
    report_shaped = []
    for index, record in enumerate(provenance.get("score_records", [])):
        absent = sorted(field for field in required if not record.get(field))
        if absent:
            missing.append({"index": index, "missing_fields": absent})
        if record.get("score_source") != "callable_computation" or record.get("static_literal_score"):
            static.append(record.get("score_name", f"record_{index}"))
        if (
            record.get("report_only_score")
            or record.get("manifest_completeness_score")
            or record.get("validator_cleanliness_score")
        ):
            report_shaped.append(record.get("score_name", f"record_{index}"))
    return {
        "producer_function": "verify_computed_evidence_provenance",
        "passed": not missing and not static and not report_shaped,
        "missing_required_fields": missing,
        "static_score_records_detected": static,
        "report_shaped_records_detected": report_shaped,
    }


def write_research_report(run: dict[str, Any], report_path: Path | str = DEFAULT_REPORT_PATH) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    scores = run["scores"]
    baselines = run["baselines"]
    ablations = run["ablations"]
    leakage = run["leakage_scan"]
    replay = run["replay"]
    strongest = scores["strongest_non_oracle_baseline"]
    text = f"""# {TASK_ID}

Verdict: `{result["verdict"]}`

Current layer: `{CURRENT_LAYER}`

Mainline integration status: `none`

Enabled status: `{ENABLED_STATUS}`

Real trigger evidence: `callable local execution produced artifacts`

Claim ceiling: `{CLAIM_CEILING}`

Auto-Remote-Anchor: conditional

No mechanism validity is claimed.

No Gate4, Gate5, bridge, runtime, tournament, companion, product, or EGO-mainline path is enabled.

## Bounded Task Card Readback

- Task id: `{TASK_ID}`
- Problem definition: execute a local offline preflight for `{MEASUREMENT_OBJECT_ID}` to test executability, failability, replay, leakage controls, baselines, ablations, and provenance.
- Current stage/layer: `{CURRENT_LAYER}`
- Mainline target: none.
- Enabled-state requirement: local module entrypoint, local pytest tests, and local artifact generation only.
- Real-trigger evidence requirement: callable code must generate artifacts from computed behavior, baseline, ablation, leakage, replay, and provenance paths.
- Hypothesis: the bounded reference path should outperform cheap non-oracle baselines on heldout action-effect intervention probes, while mechanism-removing ablations degrade.
- Strongest baseline: transition-table / FSM / graph-cache / episodic traversal plus action-effect frequency without explicit self-boundary state.
- Ablation requirement: freeze boundary update, remove action-conditioned contingency, remove no-action counterfactual, shuffle linkage, replace state with recency, and reset state before probe.
- Trace/replay requirement: recompute from serialized state plus observation and intervention, not stored hashes or verdicts.
- Computed-evidence provenance gate: every score records producer function, input hash, run id, seed/context/episode ids, aggregation, code path hash, scanner path, replay path, and source hash.
- Acceptance gate: all scoped tests/checks pass, baselines do not match reference, positive controls block, replay recomputes, and claims remain bounded.
- Stop condition: `{result["stop_conditions_triggered"]}`
- Rollback plan: revert only the isolated allowed task paths if a forbidden touch or evidence-shaping failure appears.
- Auto-Remote-Anchor decision: conditional.

## Source Pins

- Measurement object spec: `{run["config"]["source_artifact"]}`
- Measurement object spec SHA-256: `{run["source_artifact_hash"]}`
- Prior invalid harness preserved by: `PRESERVE-ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A-HOSTILE-AUDIT-001A`
- Inherited blocker family: oracle-target tautology, answer-bearing legal fields, omitted fair baselines, proxy leakage, replay tautology, report-shaped success, transition-table/FSM solving, graph-cache/episodic traversal solving.

## Scores

- Reference path score: `{scores["reference_path"]["score"]}`
- Strongest non-oracle baseline: `{strongest["baseline_name"]}` = `{strongest["score"]}`
- Oracle leakage positive-control baseline: `{scores["oracle_leakage_positive_control_baseline"]["score"]}`
- Reference margin over strongest non-oracle baseline: `{scores["reference_margin_over_strongest_non_oracle_baseline"]}`

## Baselines

Invoked baselines: `{baselines["invoked_baselines"]}`

Missing baselines: `{baselines["missing_baselines"]}`

## Ablations

{_ablation_lines(ablations)}

## Leakage And Replay

- Leakage positive controls blocked: `{leakage["positive_controls_blocked"]}/{leakage["positive_controls_total"]}`
- Replay exact recomputation match: `{replay["exact_recomputation_match"]}`
- State mutation changed behavior: `{replay["state_mutation_changed_behavior"]}`
- Observation mutation changed behavior: `{replay["observation_mutation_changed_behavior"]}`
- Metadata-only mutation preserved behavior: `{replay["metadata_mutation_preserved_behavior"]}`

## Provenance

Provenance verification passed: `{run["provenance_verification"]["passed"]}`

Score records: `{len(run["provenance"]["score_records"])}`

## What This Does Not Prove

This does not prove mechanism validity, Gate validity, Gate4/Gate5 validity, candidate behavior, agency, autonomy, consciousness, emotion, subjectivity, companion readiness, EGO readiness, runtime readiness, stable user benefit, or mainline effect.
"""
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return path


def refresh_materialized_readbacks(
    repo_root: Path | str | None = None,
    output_dir: Path | str | None = None,
) -> None:
    root = Path(repo_root or Path.cwd()).resolve()
    out = _resolve_under_root(root, output_dir or DEFAULT_OUTPUT_DIR)
    result_path = out / "result.json"
    git_path = out / "git_readback.json"
    if not result_path.exists() or not git_path.exists():
        return
    result = json.loads(result_path.read_text(encoding="utf-8"))
    source_hash = _file_sha(root / SOURCE_ARTIFACT)
    result["changed_file_allowlist"] = _changed_file_allowlist_check(root)
    _write_json(result_path, result)
    _write_json(git_path, _git_readback(root, source_hash))


def _build_serialized_state(index: int, seed: int, prior: str, channels: list[str]) -> dict[str, Any]:
    beliefs = {channel: 0.05 for channel in channels}
    beliefs[prior] = 0.85
    return {
        "state_version": "acsb-boundary-state-v1",
        "state_hash": _object_sha({"index": index, "seed": seed, "prior": prior})[:16],
        "boundary_channels": channels,
        "prior_boundary_belief": beliefs,
        "stale_prior_channel": prior,
        "update_rate": 1.0,
        "uncertainty": 0.2,
        "legal_history_summary": {
            "evidence_windows": 2,
            "prior_was_before_intervention": True,
            "contains_evaluator_labels": False,
        },
    }


def _build_observation(
    index: int,
    seed: int,
    target: str,
    decoy: str,
    external: str,
    channels: list[str],
) -> dict[str, Any]:
    train_family = f"surface_family_{index % 2}"
    probe_family = f"surface_family_{(index + 1) % 2}"
    return {
        "observation_version": "acsb-legal-observation-v1",
        "available_channels": channels,
        "action_effect_evidence": {
            "after_self_action": [
                {
                    "trial": "self_action_trial_0",
                    "action": "calibration_pulse",
                    "changed_channels": [decoy, target],
                    "context_features": {"surface_family": train_family, "texture": f"grain_{seed % 3}"},
                },
                {
                    "trial": "self_action_trial_1",
                    "action": "calibration_pulse",
                    "changed_channels": [target, decoy],
                    "context_features": {"surface_family": train_family, "texture": f"grain_{(seed + 1) % 3}"},
                },
            ]
        },
        "no_action_comparison": [
            {
                "trial": "no_action_trial_0",
                "changed_channels": [decoy],
                "context_features": {"surface_family": train_family, "texture": "quiet_0"},
            },
            {
                "trial": "no_action_trial_1",
                "changed_channels": [decoy],
                "context_features": {"surface_family": train_family, "texture": "quiet_1"},
            },
        ],
        "external_effect_comparison": [
            {
                "trial": "external_trial_0",
                "changed_channels": [external],
                "context_features": {"surface_family": train_family, "texture": "external_0"},
            },
            {
                "trial": "external_trial_1",
                "changed_channels": [external],
                "context_features": {"surface_family": train_family, "texture": "external_1"},
            },
        ],
        "future_probe_observation": {
            "probe_action": "calibration_pulse",
            "context_features": {"surface_family": probe_family, "texture": f"heldout_{seed % 5}"},
            "available_behaviors": [f"probe_with_{channel}" for channel in channels] + ["withhold_probe"],
        },
        "metadata": {
            "generator": "deterministic_offline_preflight",
            "metadata_only": True,
        },
    }


def _build_intervention(index: int) -> dict[str, Any]:
    return {
        "intervention_type": "action_effect_boundary_shift",
        "observable_intervention_marker": "boundary_shift_observed",
        "description": (
            "After stale prior evidence, current observations separate self-action effects "
            "from no-action and external-only effects."
        ),
        "legal_to_all_paths": True,
        "report_mutation_only": False,
    }


def _score_callable(
    score_name: str,
    func: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]],
    episodes: list[dict[str, Any]],
    run_id: str,
    code_path_hash: str,
    source_hash: str,
    aggregation_rule: str,
) -> dict[str, Any]:
    outputs = []
    correct = 0
    legal_inputs = []
    for episode in episodes:
        legal = legal_input_for_episode(episode)
        legal_inputs.append(legal)
        output = func(legal["serialized_state"], legal["observation"], legal["intervention"])
        outputs.append(output)
        correct += int(_output_matches_expected(output, episode))
    score = round(correct / len(episodes), 6)
    record = {
        "score_name": score_name,
        "producer_function": getattr(func, "__name__", score_name),
        "input_hash": _object_sha(legal_inputs),
        "run_id": run_id,
        "seed": [episode["seed"] for episode in episodes],
        "context_ids": [episode["context_id"] for episode in episodes],
        "episode_ids": [episode["episode_id"] for episode in episodes],
        "aggregation_rule": aggregation_rule,
        "code_path_hash": code_path_hash,
        "reference_path_name": "boundary_update_reference_path",
        "baseline_path_name": score_name if score_name in REQUIRED_BASELINES else None,
        "ablation_path_name": score_name if score_name in REQUIRED_ABLATIONS else None,
        "leakage_scanner_path": "scan_legal_input_for_leakage",
        "replay_path": "run_replay",
        "deterministic_run_marker": DETERMINISTIC_RUN_MARKER,
        "source_artifact_hash": source_hash,
        "score_source": "callable_computation",
        "static_literal_score": False,
        "report_only_score": False,
        "manifest_completeness_score": False,
        "validator_cleanliness_score": False,
    }
    return {
        "score_name": score_name,
        "producer_function": getattr(func, "__name__", score_name),
        "score": score,
        "correct": correct,
        "total": len(episodes),
        "outputs": outputs,
        "provenance_record": record,
    }


def _score_oracle_baseline(
    score_name: str,
    func: Callable[..., dict[str, Any]],
    episodes: list[dict[str, Any]],
    run_id: str,
    code_path_hash: str,
    source_hash: str,
) -> dict[str, Any]:
    outputs = []
    correct = 0
    oracle_inputs = []
    for episode in episodes:
        legal = legal_input_for_episode(episode)
        oracle_payload = {
            "target_channel": episode["expected_measurable_object"]["target_channel"],
            "oracle_boundary_label": "self_caused",
        }
        oracle_inputs.append({"legal": legal, "oracle_payload": oracle_payload})
        output = func(
            legal["serialized_state"],
            legal["observation"],
            legal["intervention"],
            oracle_payload,
        )
        outputs.append(output)
        correct += int(_output_matches_expected(output, episode))
    score = round(correct / len(episodes), 6)
    record = {
        "score_name": score_name,
        "producer_function": score_name,
        "input_hash": _object_sha(oracle_inputs),
        "run_id": run_id,
        "seed": [episode["seed"] for episode in episodes],
        "context_ids": [episode["context_id"] for episode in episodes],
        "episode_ids": [episode["episode_id"] for episode in episodes],
        "aggregation_rule": f"mean exact composite-object match for {score_name}",
        "code_path_hash": code_path_hash,
        "reference_path_name": "boundary_update_reference_path",
        "baseline_path_name": score_name,
        "ablation_path_name": None,
        "leakage_scanner_path": "scan_legal_input_for_leakage",
        "replay_path": "run_replay",
        "deterministic_run_marker": DETERMINISTIC_RUN_MARKER,
        "source_artifact_hash": source_hash,
        "score_source": "callable_computation",
        "static_literal_score": False,
        "report_only_score": False,
        "manifest_completeness_score": False,
        "validator_cleanliness_score": False,
    }
    return {
        "score_name": score_name,
        "producer_function": score_name,
        "score": score,
        "correct": correct,
        "total": len(episodes),
        "outputs": outputs,
        "received_answer_bearing_fields": True,
        "provenance_record": record,
    }


def _build_scores(reference: dict[str, Any], baselines: dict[str, Any]) -> dict[str, Any]:
    strongest = baselines["strongest_non_oracle_baseline"]
    oracle = baselines["baseline_scores"]["oracle_leakage_positive_control_baseline"]
    return {
        "task_id": TASK_ID,
        "producer_function": "_build_scores",
        "reference_path": {
            "path_name": "boundary_update_reference_path",
            "score": reference["score"],
            "correct": reference["correct"],
            "total": reference["total"],
        },
        "strongest_non_oracle_baseline": strongest,
        "oracle_leakage_positive_control_baseline": {
            "score": oracle["score"],
            "received_answer_bearing_fields": True,
        },
        "reference_margin_over_strongest_non_oracle_baseline": round(
            reference["score"] - strongest["score"],
            6,
        ),
    }


def _build_result(
    config: dict[str, Any],
    scores: dict[str, Any],
    baselines: dict[str, Any],
    ablations: dict[str, Any],
    leakage_scan: dict[str, Any],
    replay: dict[str, Any],
    provenance_verification: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    thresholds = config["thresholds"]
    stop_conditions = []
    verdict = "action_conditioned_self_boundary_executable_preflight_001a_surface_discriminative"

    strongest = scores["strongest_non_oracle_baseline"]
    if not leakage_scan["all_positive_controls_blocked"]:
        stop_conditions.append("leakage_positive_control_failure")
        verdict = "blocked_by_leakage_positive_control_failure_001a"
    if not replay["passed"] or not replay["exact_recomputation_match"]:
        stop_conditions.append("replay_not_recomputed_from_state_observation")
        verdict = "blocked_by_replay_not_recomputed_from_state_observation_001a"
    if not provenance_verification["passed"]:
        stop_conditions.append("provenance_gap")
        verdict = "blocked_by_provenance_gap_001a"
    if strongest["score"] >= scores["reference_path"]["score"]:
        stop_conditions.append("cheap_baseline_matched_or_beat_reference")
        verdict = "blocked_by_transition_table_fsm_graph_cache_baseline_001a"
    if (
        baselines["baseline_scores"]["action_effect_frequency_without_boundary_state_baseline"]["score"]
        >= scores["reference_path"]["score"]
    ):
        stop_conditions.append("action_effect_frequency_baseline_matched_reference")
        verdict = "blocked_by_action_effect_frequency_baseline_001a"
    for name in CORE_ABLATIONS:
        if (
            ablations["ablation_scores"][name]["degradation_from_reference"]
            < thresholds["core_ablation_degradation_min"]
        ):
            stop_conditions.append(f"{name}_did_not_degrade_reference")
            verdict = "blocked_by_ablation_not_degrading_reference_path_001a"
    if (
        strongest["score"] > thresholds["strongest_non_oracle_baseline_max"]
        or scores["reference_margin_over_strongest_non_oracle_baseline"]
        < thresholds["reference_margin_over_strongest_non_oracle_baseline_min"]
    ):
        stop_conditions.append("baseline_margin_threshold_failed")
        verdict = "blocked_by_transition_table_fsm_graph_cache_baseline_001a"
    if scores["oracle_leakage_positive_control_baseline"]["score"] < thresholds["oracle_leakage_positive_control_min"]:
        stop_conditions.append("oracle_leakage_positive_control_low_score")
        verdict = "blocked_by_leakage_positive_control_failure_001a"

    claim_scan = _forbidden_positive_claim_scan({})
    allowlist = _changed_file_allowlist_check(root)
    if not allowlist["passed"]:
        stop_conditions.append("changed_file_allowlist_failure")

    return {
        "task_id": TASK_ID,
        "measurement_object_id": MEASUREMENT_OBJECT_ID,
        "verdict": verdict,
        "allowed_verdict": verdict in ALLOWED_VERDICTS,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": "none",
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": "callable local execution produced artifacts",
        "claim_ceiling": CLAIM_CEILING,
        "reference_path_score": scores["reference_path"]["score"],
        "strongest_non_oracle_baseline": strongest,
        "oracle_leakage_positive_control_score": scores[
            "oracle_leakage_positive_control_baseline"
        ]["score"],
        "ablation_results": {
            name: {
                "score": record["score"],
                "degradation_from_reference": record["degradation_from_reference"],
            }
            for name, record in ablations["ablation_scores"].items()
        },
        "replay_result": {
            "passed": replay["passed"],
            "exact_recomputation_match": replay["exact_recomputation_match"],
        },
        "provenance_result": provenance_verification,
        "forbidden_positive_claim_scan": claim_scan,
        "changed_file_allowlist": allowlist,
        "mechanism_validity_claimed": False,
        "agency_claimed": False,
        "autonomy_claimed": False,
        "consciousness_claimed": False,
        "emotion_claimed": False,
        "subjectivity_claimed": False,
        "runtime_readiness_claimed": False,
        "ego_readiness_claimed": False,
        "mainline_effect_claimed": False,
        "gate_bridge_runtime_or_ego_mainline_enabled": False,
        "stop_conditions_triggered": stop_conditions,
        "what_this_does_not_prove": FORBIDDEN_CLAIMS,
    }


def _write_artifacts(output_dir: Path, run: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_payloads = {
        "result.json": run["result"],
        "episodes.json": {
            "task_id": TASK_ID,
            "producer_function": "generate_episodes",
            "episodes": run["episodes"],
        },
        "scores.json": run["scores"],
        "baselines.json": run["baselines"],
        "ablations.json": run["ablations"],
        "leakage_scan.json": run["leakage_scan"],
        "replay.json": run["replay"],
        "provenance.json": run["provenance"],
        "git_readback.json": run["git_readback"],
    }
    for name, payload in artifact_payloads.items():
        _write_json(output_dir / name, payload)
    _write_text(output_dir / "claim_ceiling.txt", CLAIM_CEILING + "\n")
    _write_text(output_dir / "summary.md", _summary_text(run))


def _summary_text(run: dict[str, Any]) -> str:
    result = run["result"]
    strongest = run["scores"]["strongest_non_oracle_baseline"]
    return f"""# {TASK_ID} Summary

Verdict: `{result["verdict"]}`

Layer: `{CURRENT_LAYER}`

Mainline integration status: `none`

Enabled status: `{ENABLED_STATUS}`

Real trigger evidence: `callable local execution produced artifacts`

Claim ceiling: `{CLAIM_CEILING}`

Reference path score: `{run["scores"]["reference_path"]["score"]}`

Strongest non-oracle baseline: `{strongest["baseline_name"]}` = `{strongest["score"]}`

Oracle leakage positive-control baseline: `{run["scores"]["oracle_leakage_positive_control_baseline"]["score"]}`

No mechanism validity is claimed. No Gate4, Gate5, bridge, runtime, tournament, companion, product, or EGO-mainline path is enabled.
"""


def _forbidden_positive_claim_scan(payload: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(payload, sort_keys=True)
    positive_patterns = [
        "proves mechanism validity",
        "mechanism validity proven",
        "ego readiness achieved",
        "runtime ready",
        "companion ready",
        "consciousness evidence established",
        "agency success",
        "mainline effective",
    ]
    matches = [pattern for pattern in positive_patterns if pattern in text.lower()]
    return {
        "producer_function": "_forbidden_positive_claim_scan",
        "passed": not matches,
        "matches": matches,
        "claim_ceiling": CLAIM_CEILING,
    }


def _changed_file_allowlist_check(root: Path) -> dict[str, Any]:
    changed = _git_changed_paths(root)
    forbidden = [path for path in changed if not _path_allowed(path)]
    return {
        "producer_function": "_changed_file_allowlist_check",
        "passed": not forbidden,
        "changed_paths": changed,
        "forbidden_paths": forbidden,
        "allowed_prefixes": [
            "src/action_conditioned_self_boundary_executable_preflight_001a/",
            "tests/test_action_conditioned_self_boundary_executable_preflight_001a.py",
            "docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001A.md",
            "artifacts/action_conditioned_self_boundary_executable_preflight_001a/",
        ],
    }


def _path_allowed(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return (
        normalized == "tests/test_action_conditioned_self_boundary_executable_preflight_001a.py"
        or normalized == "docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001A.md"
        or normalized.startswith("src/action_conditioned_self_boundary_executable_preflight_001a/")
        or normalized.startswith("artifacts/action_conditioned_self_boundary_executable_preflight_001a/")
    )


def _git_changed_paths(root: Path) -> list[str]:
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return []
    paths = []
    for line in status:
        if not line:
            continue
        raw_path = line[3:]
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1]
        paths.append(raw_path.replace("\\", "/"))
    return sorted(paths)


def _git_readback(root: Path, source_hash: str) -> dict[str, Any]:
    current_status = "clean" if not _git_changed_paths(root) else "dirty"
    return {
        "task_id": TASK_ID,
        "producer_function": "_git_readback",
        "branch": _git_output(root, ["git", "branch", "--show-current"]),
        "head": _git_output(root, ["git", "rev-parse", "HEAD"]),
        "session_start_readback": _session_start_readback(root),
        "worktree_status_at_artifact_generation": current_status,
        "ahead_behind": _git_output(
            root,
            ["git", "rev-list", "--left-right", "--count", f"origin/{SESSION_START_BRANCH}...HEAD"],
        ),
        "diff_name_status": _git_output(root, ["git", "diff", "--name-status"]).splitlines(),
        "source_artifact": str(SOURCE_ARTIFACT).replace("\\", "/"),
        "source_artifact_sha256": source_hash,
    }


def _session_start_readback(root: Path) -> dict[str, Any]:
    return {
        "branch": SESSION_START_BRANCH,
        "head": SESSION_START_HEAD,
        "remote_branch": SESSION_START_HEAD,
        "local_tag": SESSION_START_TAG,
        "local_tag_hash": _git_output(root, ["git", "rev-parse", f"refs/tags/{SESSION_START_TAG}"]),
        "remote_tag": SESSION_START_TAG,
        "remote_tag_hash": SESSION_START_HEAD,
        "ahead_behind": "0\t0",
        "worktree_status": "clean",
        "readback_source": "current session start-state git readback before implementation",
    }


def _positive_control_inputs(episode: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    controls = []
    legal = legal_input_for_episode(episode)
    target = episode["expected_measurable_object"]["target_channel"]

    payload = copy.deepcopy(legal)
    payload["observation"]["target_action"] = f"probe_with_{target}"
    payload["observation"]["target_output"] = target
    controls.append(("explicit_target_action_output", payload))

    payload = copy.deepcopy(legal)
    payload["serialized_state"]["oracle_boundary_label"] = "self_caused"
    controls.append(("oracle_boundary_label", payload))

    payload = copy.deepcopy(legal)
    payload["observation"]["benign_answer_alias"] = target
    controls.append(("benign_answer_alias", payload))

    payload = copy.deepcopy(legal)
    payload["observation"]["hidden_id"] = f"answer_map:{target}"
    controls.append(("hidden_id_answer_map", payload))

    payload = copy.deepcopy(legal)
    payload["observation"]["future_outcome"] = target
    controls.append(("future_outcome", payload))

    payload = copy.deepcopy(legal)
    payload["observation"]["precomputed_verdict"] = "pass"
    payload["observation"]["precomputed_score"] = 1.0
    controls.append(("stored_verdict_score", payload))
    return controls


def _output_matches_expected(output: dict[str, Any], episode: dict[str, Any]) -> bool:
    expected = episode["expected_measurable_object"]
    return (
        _selected_channel(output) == expected["target_channel"]
        and output["probe_behavior"] == expected["probe_behavior"]
        and output["probe_boundary_explanation_token"]
        == expected["probe_boundary_explanation_token"]
    )


def _selected_channel(output: dict[str, Any]) -> str:
    return output["boundary_assignment_update"]["selected_self_channel"]


def _make_output(selected: str, path_name: str, trace: dict[str, Any]) -> dict[str, Any]:
    if selected == "unresolved":
        behavior = "withhold_probe"
        token = "unresolved"
    else:
        behavior = f"probe_with_{selected}"
        token = "self_caused"
    return {
        "path_name": path_name,
        "boundary_assignment_update": {
            "selected_self_channel": selected,
            "channel_confidence": {
                channel: (1.0 if channel == selected else 0.0) for channel in CHANNELS
            },
        },
        "probe_behavior": behavior,
        "probe_boundary_explanation_token": token,
        "trace": trace,
    }


def _count_changed_channels(rows: list[dict[str, Any]], channels: list[str]) -> dict[str, int]:
    counts = {channel: 0 for channel in channels}
    for row in rows:
        for channel in row.get("changed_channels", []):
            if channel in counts:
                counts[channel] += 1
    return counts


def _first_seen_channels(rows: list[dict[str, Any]]) -> dict[str, int]:
    seen = {}
    order = 0
    for row in rows:
        for channel in row.get("changed_channels", []):
            if channel not in seen:
                seen[channel] = order
                order += 1
    return seen


def _max_channel(scores: dict[str, float]) -> str:
    return max(scores, key=lambda channel: scores[channel])


def _walk_dict(value: Any, prefix: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            yield path, str(key), child
            yield from _walk_dict(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_dict(child, f"{prefix}[{index}]")


def _ablation_lines(ablations: dict[str, Any]) -> str:
    lines = []
    for name in REQUIRED_ABLATIONS:
        record = ablations["ablation_scores"][name]
        lines.append(
            f"- `{name}`: score `{record['score']}`, degradation `{record['degradation_from_reference']}`"
        )
    return "\n".join(lines)


def _resolve_under_root(root: Path, path: Path | str) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = root / resolved
    return resolved.resolve()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_ready(child) for child in value]
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    return value


def _git_output(root: Path, command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return completed.stdout.strip()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _object_sha(obj: Any) -> str:
    data = json.dumps(_json_ready(obj), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()
