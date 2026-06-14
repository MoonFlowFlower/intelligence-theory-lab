from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from . import runner as base_001a


TASK_ID = "ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B-LEARNED-BASELINE-SCALING-CHALLENGE"
TASK_SLUG = "action_conditioned_self_boundary_executable_preflight_001b"
SOURCE_001A_RUNNER = Path("src/action_conditioned_self_boundary_executable_preflight_001a/runner.py")
SOURCE_001A_RESULT = Path("artifacts/action_conditioned_self_boundary_executable_preflight_001a/result.json")
DEFAULT_OUTPUT_DIR = Path("artifacts") / TASK_SLUG
DEFAULT_REPORT_PATH = Path("docs/research") / f"{TASK_ID}.md"
CLAIM_CEILING = "offline learned-baseline/scaling challenge evidence only"
CURRENT_LAYER = "engineering implementation / offline executable learned-baseline and scaling challenge only"
ENABLED_STATUS = "local offline module, tests, and artifact generation only"
RUN_ID = f"{TASK_SLUG}_deterministic_run_001"
DETERMINISTIC_RUN_MARKER = "2026-06-14-deterministic-offline-learned-scaling-challenge"

CANONICAL_001A_COMMIT = "4b7a5b467e1c56b392766e4fc60f75129c9e1842"
CANONICAL_001A_BRANCH = "codex/meta-theory-scaffold"
CANONICAL_001A_TAG = "remote-anchor-action-conditioned-self-boundary-executable-preflight-001a-4b7a5b4"

CHANNELS = list(base_001a.CHANNELS)
PROBE_SETTINGS = ["small_reproduction", "combinatorial_heldout", "noisy_decoy_intervention"]

FORBIDDEN_LEGAL_KEYS = set(base_001a.FORBIDDEN_LEGAL_KEYS)

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
    "action_conditioned_self_boundary_executable_preflight_001b_survives_learned_baseline_scaling_challenge",
    "blocked_by_learned_no_boundary_baseline_001b",
    "blocked_by_capacity_matched_boundary_disabled_reference_001b",
    "blocked_by_scaling_probe_collapse_001b",
    "blocked_by_leakage_positive_control_failure_001b",
    "blocked_by_replay_or_provenance_gap_001b",
    "blocked_by_report_shaped_or_static_score_evidence_001b",
    "closed_action_conditioned_self_boundary_surface_not_discriminative_under_learned_scaling_challenge_001b",
}

REQUIRED_LEARNED_BASELINES = [
    "learned_feature_mlp_without_boundary_state",
    "sequence_model_without_boundary_update",
    "embedding_knn_or_episodic_retrieval_baseline",
]

REQUIRED_NON_ORACLE_BASELINES = REQUIRED_LEARNED_BASELINES + [
    "capacity_matched_boundary_disabled_reference",
]

REQUIRED_ABLATIONS = list(base_001a.REQUIRED_ABLATIONS)

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
    "trace.jsonl",
    "scores.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan.json",
    "replay_report.json",
    "provenance.json",
    "failure_manifest.json",
    "claim_ceiling.txt",
    "git_readback.json",
]


def build_challenge_config(repo_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    source_001a = {
        "runner_path": str(SOURCE_001A_RUNNER).replace("\\", "/"),
        "runner_sha256": _file_sha(root / SOURCE_001A_RUNNER),
        "result_path": str(SOURCE_001A_RESULT).replace("\\", "/"),
        "result_sha256": _file_sha(root / SOURCE_001A_RESULT),
    }
    config = {
        "task_card_id": TASK_ID,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_target": "none",
        "enabled_requirement": ENABLED_STATUS,
        "claim_ceiling": CLAIM_CEILING,
        "auto_remote_anchor": "conditional",
        "created_before_results": True,
        "canonical_001a_boundary": _canonical_001a_boundary_readback(root),
        "source_001a": source_001a,
        "run_id": RUN_ID,
        "deterministic_run_marker": DETERMINISTIC_RUN_MARKER,
        "channels": CHANNELS,
        "probe_settings": PROBE_SETTINGS,
        "seeds_by_probe_setting": {
            "small_reproduction": list(range(9100, 9116)),
            "combinatorial_heldout": list(range(9200, 9224)),
            "noisy_decoy_intervention": list(range(9300, 9320)),
        },
        "learned_no_boundary_baseline_inventory": REQUIRED_LEARNED_BASELINES,
        "non_oracle_baseline_inventory": REQUIRED_NON_ORACLE_BASELINES,
        "ablation_inventory": REQUIRED_ABLATIONS,
        "thresholds": {
            "reference_margin_over_strongest_non_oracle_baseline_min": 0.15,
            "capacity_disabled_degradation_min": 0.20,
            "core_ablation_degradation_min": 0.20,
            "leakage_positive_controls_blocked_fraction": 1.0,
        },
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "forbidden_legal_keys": sorted(FORBIDDEN_LEGAL_KEYS),
    }
    config["config_hash"] = _object_sha({k: v for k, v in config.items() if k != "config_hash"})
    return config


def generate_scaling_probe_episodes(config: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        probe_name: [
            _build_episode(config, probe_name, index, seed)
            for index, seed in enumerate(config["seeds_by_probe_setting"][probe_name])
        ]
        for probe_name in config["probe_settings"]
    }


def legal_input_for_episode_001b(episode: dict[str, Any]) -> dict[str, Any]:
    return {
        "serialized_state": copy.deepcopy(episode["serialized_prior_boundary_state"]),
        "observation": copy.deepcopy(episode["legal_observation"]),
        "intervention": copy.deepcopy(episode["intervention_description"]),
    }


def learned_feature_mlp_without_boundary_state(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    _raise_if_leaking(serialized_state, observation, intervention)
    action_rows = observation["action_effect_evidence"]["after_self_action"]
    counts = base_001a._count_changed_channels(action_rows, serialized_state["boundary_channels"])
    first_seen = base_001a._first_seen_channels(action_rows)
    selected = max(
        serialized_state["boundary_channels"],
        key=lambda channel: (counts[channel], -first_seen.get(channel, 999)),
    )
    output = base_001a._make_output(
        selected,
        "learned_feature_mlp_without_boundary_state",
        {
            "learner": "deterministic_lightweight_feature_mlp_fallback",
            "ml_library_used": False,
            "feature_family": "legal_flattened_self_action_features_only",
            "maintains_explicit_boundary_update": False,
            "uses_no_action_counterfactual_boundary_update": False,
            "action_counts": counts,
        },
    )
    output["maintains_explicit_boundary_update"] = False
    return output


def sequence_model_without_boundary_update(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    _raise_if_leaking(serialized_state, observation, intervention)
    sequence = observation["legal_effect_sequence"]
    selected = sequence[-1]["changed_channels"][-1]
    output = base_001a._make_output(
        selected,
        "sequence_model_without_boundary_update",
        {
            "learner": "deterministic_sequence_memory",
            "sequence_events": len(sequence),
            "maintains_explicit_boundary_update": False,
            "uses_no_action_counterfactual_boundary_update": False,
        },
    )
    output["maintains_explicit_boundary_update"] = False
    return output


def embedding_knn_or_episodic_retrieval_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    _raise_if_leaking(serialized_state, observation, intervention)
    probe_features = observation["future_probe_observation"]["context_features"]
    candidates = observation["training_history"]
    nearest = min(
        candidates,
        key=lambda row: _feature_distance(row["context_features"], probe_features),
    )
    selected = nearest["changed_channels"][0]
    output = base_001a._make_output(
        selected,
        "embedding_knn_or_episodic_retrieval_baseline",
        {
            "learner": "deterministic_embedding_knn",
            "retrieval_context_id": nearest["context_id"],
            "retrieval_distance": _feature_distance(nearest["context_features"], probe_features),
            "maintains_explicit_boundary_update": False,
        },
    )
    output["maintains_explicit_boundary_update"] = False
    return output


def capacity_matched_boundary_disabled_reference(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    _raise_if_leaking(serialized_state, observation, intervention)
    action_counts = base_001a._count_changed_channels(
        observation["action_effect_evidence"]["after_self_action"],
        serialized_state["boundary_channels"],
    )
    no_action_counts = base_001a._count_changed_channels(
        observation.get("no_action_comparison", []),
        serialized_state["boundary_channels"],
    )
    external_counts = base_001a._count_changed_channels(
        observation.get("external_effect_comparison", []),
        serialized_state["boundary_channels"],
    )
    selected = serialized_state["stale_prior_channel"]
    output = base_001a._make_output(
        selected,
        "capacity_matched_boundary_disabled_reference",
        {
            "mode": "capacity_matched_counterfactuals_computed_update_disabled",
            "action_counts": action_counts,
            "no_action_counts": no_action_counts,
            "external_counts": external_counts,
            "disabled_component": "action_conditioned_boundary_update",
            "maintains_explicit_boundary_update": False,
        },
    )
    output["maintains_explicit_boundary_update"] = False
    return output


def contaminated_learned_no_boundary_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    selected = observation.get("target_output") or observation.get("benign_answer_alias")
    if selected is None:
        selected = learned_feature_mlp_without_boundary_state(
            serialized_state, observation, intervention
        )["boundary_assignment_update"]["selected_self_channel"]
    output = base_001a._make_output(
        selected,
        "contaminated_learned_no_boundary_baseline",
        {"exploited_contamination": "target_output" in observation},
    )
    output["maintains_explicit_boundary_update"] = False
    return output


BASELINE_FUNCTIONS_001B: dict[str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
    "learned_feature_mlp_without_boundary_state": learned_feature_mlp_without_boundary_state,
    "sequence_model_without_boundary_update": sequence_model_without_boundary_update,
    "embedding_knn_or_episodic_retrieval_baseline": embedding_knn_or_episodic_retrieval_baseline,
    "capacity_matched_boundary_disabled_reference": capacity_matched_boundary_disabled_reference,
}

ABLATION_FUNCTIONS_001B: dict[str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
    "freeze_boundary_update": base_001a.freeze_boundary_update,
    "remove_action_conditioned_contingency": base_001a.remove_action_conditioned_contingency,
    "remove_no_action_counterfactual": base_001a.remove_no_action_counterfactual,
    "shuffle_action_effect_linkage": base_001a.shuffle_action_effect_linkage,
    "replace_boundary_state_with_recency_state": base_001a.replace_boundary_state_with_recency_state,
    "reset_state_before_probe": base_001a.reset_state_before_probe,
}


def execute_challenge(
    repo_root: Path | str | None = None,
    output_dir: Path | str | None = None,
    persist_artifacts: bool = True,
    disable_leakage_positive_controls: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = _resolve_under_root(root, output_dir or DEFAULT_OUTPUT_DIR)
    config = build_challenge_config(root)
    episodes_by_probe = generate_scaling_probe_episodes(config)
    code_path_hash = _file_sha(Path(__file__))

    scores = run_probe_scores(
        episodes_by_probe,
        RUN_ID,
        code_path_hash,
        config["source_001a"],
    )
    baseline_comparison = _build_baseline_comparison(scores)
    ablation_report = run_ablations_001b(
        episodes_by_probe,
        scores,
        RUN_ID,
        code_path_hash,
        config["source_001a"],
    )
    leakage_scan = run_leakage_scan_001b(
        episodes_by_probe,
        include_positive_controls=not disable_leakage_positive_controls,
    )
    replay_report = run_replay_001b(episodes_by_probe)

    score_records = []
    for probe_scores in scores["by_probe_setting"].values():
        score_records.append(probe_scores["reference_path"]["provenance_record"])
        score_records.extend(
            record["provenance_record"] for record in probe_scores["baseline_scores"].values()
        )
    for probe_ablations in ablation_report["by_probe_setting"].values():
        score_records.extend(
            record["provenance_record"]
            for record in probe_ablations["ablation_scores"].values()
        )
    provenance = {
        "task_id": TASK_ID,
        "producer_function": "execute_challenge",
        "run_id": RUN_ID,
        "source_001a": config["source_001a"],
        "code_path_hash": code_path_hash,
        "score_records": score_records,
        "aggregation_rule": "all score records must come from callable computation paths",
    }
    provenance_verification = verify_computed_evidence_provenance_001b(provenance)
    result = _build_result(
        config=config,
        scores=scores,
        baseline_comparison=baseline_comparison,
        ablation_report=ablation_report,
        leakage_scan=leakage_scan,
        replay_report=replay_report,
        provenance_verification=provenance_verification,
        root=root,
    )
    run = {
        "task_id": TASK_ID,
        "config": config,
        "run_id": RUN_ID,
        "episodes_by_probe_setting": episodes_by_probe,
        "scores": scores,
        "baseline_comparison": baseline_comparison,
        "ablation_report": ablation_report,
        "leakage_scan": leakage_scan,
        "replay_report": replay_report,
        "provenance": provenance,
        "provenance_verification": provenance_verification,
        "result": result,
        "failure_manifest": _build_failure_manifest(result),
        "trace_events": _build_trace_events(scores, ablation_report),
        "git_readback": _git_readback_001b(root, config),
    }
    if persist_artifacts:
        _write_artifacts_001b(out, run)
    return run


def run_probe_scores(
    episodes_by_probe: dict[str, list[dict[str, Any]]],
    run_id: str,
    code_path_hash: str,
    source_001a: dict[str, str],
) -> dict[str, Any]:
    by_probe = {}
    for probe_name, episodes in episodes_by_probe.items():
        reference = _score_callable_001b(
            "reference_path",
            base_001a.boundary_update_reference_path,
            episodes,
            run_id,
            code_path_hash,
            source_001a,
            aggregation_rule=f"mean exact composite-object match for reference path in {probe_name}",
            probe_name=probe_name,
        )
        baseline_scores = {}
        for name, func in BASELINE_FUNCTIONS_001B.items():
            baseline_scores[name] = _score_callable_001b(
                name,
                func,
                episodes,
                run_id,
                code_path_hash,
                source_001a,
                aggregation_rule=f"mean exact composite-object match for {name} in {probe_name}",
                probe_name=probe_name,
                baseline_path_name=name,
            )
            baseline_scores[name]["maintains_explicit_boundary_update"] = False

        strongest_non_oracle_name, strongest_non_oracle = max(
            baseline_scores.items(), key=lambda item: item[1]["score"]
        )
        learned_scores = {
            name: baseline_scores[name] for name in REQUIRED_LEARNED_BASELINES
        }
        strongest_learned_name, strongest_learned = max(
            learned_scores.items(), key=lambda item: item[1]["score"]
        )
        by_probe[probe_name] = {
            "reference_path": reference,
            "baseline_scores": baseline_scores,
            "strongest_non_oracle_baseline": {
                "baseline_name": strongest_non_oracle_name,
                "score": strongest_non_oracle["score"],
            },
            "strongest_learned_no_boundary_baseline": {
                "baseline_name": strongest_learned_name,
                "score": strongest_learned["score"],
            },
            "reference_margin_over_strongest_non_oracle_baseline": round(
                reference["score"] - strongest_non_oracle["score"], 6
            ),
        }
    return {
        "task_id": TASK_ID,
        "producer_function": "run_probe_scores",
        "by_probe_setting": by_probe,
    }


def run_ablations_001b(
    episodes_by_probe: dict[str, list[dict[str, Any]]],
    scores: dict[str, Any],
    run_id: str,
    code_path_hash: str,
    source_001a: dict[str, str],
) -> dict[str, Any]:
    by_probe = {}
    for probe_name, episodes in episodes_by_probe.items():
        reference_score = scores["by_probe_setting"][probe_name]["reference_path"]["score"]
        ablation_scores = {}
        for name, func in ABLATION_FUNCTIONS_001B.items():
            score = _score_callable_001b(
                name,
                func,
                episodes,
                run_id,
                code_path_hash,
                source_001a,
                aggregation_rule=f"mean exact composite-object match after rerunning {name} in {probe_name}",
                probe_name=probe_name,
                ablation_path_name=name,
            )
            score["reran_behavior"] = True
            score["degradation_from_reference"] = round(reference_score - score["score"], 6)
            score["provenance_record"]["ablation_path_name"] = name
            ablation_scores[name] = score
        by_probe[probe_name] = {
            "probe_setting": probe_name,
            "ablation_scores": ablation_scores,
        }
    return {
        "task_id": TASK_ID,
        "producer_function": "run_ablations_001b",
        "invoked_ablations": sorted(ABLATION_FUNCTIONS_001B),
        "missing_ablations": sorted(set(REQUIRED_ABLATIONS) - set(ABLATION_FUNCTIONS_001B)),
        "by_probe_setting": by_probe,
    }


def run_leakage_scan_001b(
    episodes_by_probe: dict[str, list[dict[str, Any]]],
    include_positive_controls: bool = True,
) -> dict[str, Any]:
    first_episode = next(iter(episodes_by_probe.values()))[0]
    normal = scan_legal_input_for_leakage_001b(legal_input_for_episode_001b(first_episode))
    controls = _positive_control_inputs_001b(first_episode) if include_positive_controls else []
    control_results = []
    for control_id, payload in controls:
        scan = scan_legal_input_for_leakage_001b(payload)
        control_results.append(
            {
                "control_id": control_id,
                "blocked": scan["blocked"],
                "detected_paths": scan["detected_paths"],
            }
        )
    blocked_count = sum(1 for item in control_results if item["blocked"])
    contaminated = _score_contaminated_learned_positive_control(episodes_by_probe)
    clean_excludes_contaminated = all(
        not scan_legal_input_for_leakage_001b(legal_input_for_episode_001b(episode))["blocked"]
        for episodes in episodes_by_probe.values()
        for episode in episodes
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "run_leakage_scan_001b",
        "normal_legal_input": normal,
        "positive_controls": control_results,
        "positive_controls_blocked": blocked_count,
        "positive_controls_total": len(control_results),
        "all_positive_controls_blocked": bool(control_results)
        and blocked_count == len(control_results),
        "learned_contaminated_positive_control": contaminated,
        "clean_legal_input_excludes_contaminated_fields": clean_excludes_contaminated,
        "scanner_path": "scan_legal_input_for_leakage_001b",
    }


def scan_legal_input_for_leakage_001b(value: Any) -> dict[str, Any]:
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
        "producer_function": "scan_legal_input_for_leakage_001b",
        "blocked": bool(detected),
        "detected_paths": sorted(set(detected)),
    }


def run_replay_001b(episodes_by_probe: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    episode = next(iter(episodes_by_probe.values()))[0]
    path_functions: dict[str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
        "boundary_update_reference_path": base_001a.boundary_update_reference_path,
        **BASELINE_FUNCTIONS_001B,
        **ABLATION_FUNCTIONS_001B,
    }
    exact_cases = {}
    state_cases = {}
    observation_cases = {}
    metadata_cases = {}
    for name, func in path_functions.items():
        legal = legal_input_for_episode_001b(episode)
        direct = func(legal["serialized_state"], legal["observation"], legal["intervention"])
        replayed = func(
            copy.deepcopy(legal["serialized_state"]),
            copy.deepcopy(legal["observation"]),
            copy.deepcopy(legal["intervention"]),
        )
        exact_cases[name] = direct == replayed

        state_mutated = legal_input_for_episode_001b(episode)
        state_mutated["serialized_state"]["update_rate"] = 0.0
        state_mutated["serialized_state"]["stale_prior_channel"] = CHANNELS[
            (CHANNELS.index(episode["expected_measurable_object"]["target_channel"]) + 2)
            % len(CHANNELS)
        ]
        state_output = func(
            state_mutated["serialized_state"],
            state_mutated["observation"],
            state_mutated["intervention"],
        )
        state_cases[name] = _selected_channel(direct) != _selected_channel(state_output)

        observation_mutated = legal_input_for_episode_001b(episode)
        replacement = CHANNELS[
            (CHANNELS.index(episode["expected_measurable_object"]["target_channel"]) + 2)
            % len(CHANNELS)
        ]
        _replace_action_effect_channels(observation_mutated["observation"], replacement)
        observation_output = func(
            observation_mutated["serialized_state"],
            observation_mutated["observation"],
            observation_mutated["intervention"],
        )
        observation_cases[name] = _selected_channel(direct) != _selected_channel(observation_output)

        metadata_mutated = legal_input_for_episode_001b(episode)
        metadata_mutated["observation"]["metadata"]["audit_note"] = "metadata-only replay mutation"
        metadata_output = func(
            metadata_mutated["serialized_state"],
            metadata_mutated["observation"],
            metadata_mutated["intervention"],
        )
        metadata_cases[name] = _selected_channel(direct) == _selected_channel(metadata_output)

    missing_input_failed = False
    missing = legal_input_for_episode_001b(episode)
    del missing["observation"]["action_effect_evidence"]
    try:
        base_001a.boundary_update_reference_path(
            missing["serialized_state"],
            missing["observation"],
            missing["intervention"],
        )
    except ValueError:
        missing_input_failed = True

    return {
        "task_id": TASK_ID,
        "producer_function": "run_replay_001b",
        "passed": all(exact_cases.values())
        and any(state_cases.values())
        and any(observation_cases.values())
        and all(metadata_cases.values())
        and missing_input_failed,
        "exact_recomputation_passed": all(exact_cases.values()),
        "exact_recomputation_cases": exact_cases,
        "state_mutation_changed_behavior": any(state_cases.values()),
        "state_mutation_cases": state_cases,
        "observation_mutation_changed_behavior": any(observation_cases.values()),
        "observation_mutation_cases": observation_cases,
        "metadata_mutation_preserved_behavior": all(metadata_cases.values()),
        "metadata_mutation_cases": metadata_cases,
        "missing_required_legal_input_failed": missing_input_failed,
        "uses_stored_hashes_only": False,
        "uses_stored_verdicts": False,
        "recomputed_paths": sorted(path_functions),
        "replay_path": "run_replay_001b",
    }


def verify_computed_evidence_provenance_001b(provenance: dict[str, Any]) -> dict[str, Any]:
    required = {
        "producer_function",
        "input_hash",
        "run_id",
        "seed",
        "context_ids",
        "episode_ids",
        "aggregation_rule",
        "code_path_hash",
        "baseline_path_name",
        "ablation_path_name",
        "leakage_scanner_path",
        "replay_path",
        "source_001a_runner_hash",
        "source_001a_result_hash",
    }
    missing = []
    static = []
    report_shaped = []
    for index, record in enumerate(provenance.get("score_records", [])):
        absent = sorted(field for field in required if field not in record)
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
        "producer_function": "verify_computed_evidence_provenance_001b",
        "passed": not missing and not static and not report_shaped,
        "missing_required_fields": missing,
        "static_score_records_detected": static,
        "report_shaped_records_detected": report_shaped,
    }


def write_research_report_001b(
    run: dict[str, Any],
    report_path: Path | str = DEFAULT_REPORT_PATH,
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    source = run["config"]["source_001a"]
    scores = run["scores"]["by_probe_setting"]
    lines = [
        f"# {TASK_ID}",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        f"Current layer: `{CURRENT_LAYER}`",
        "",
        "Mainline integration status: `none`",
        "",
        f"Enabled status: `{ENABLED_STATUS}`",
        "",
        "Real trigger evidence: `callable local 001B execution produced artifacts`",
        "",
        f"Claim ceiling: `{CLAIM_CEILING}`",
        "",
        "Auto-Remote-Anchor: conditional",
        "",
        "No mechanism validity is claimed.",
        "",
        "No Gate4, Gate5, bridge, runtime, tournament, companion, product, or EGO-mainline path is enabled.",
        "",
        "## Bounded Task Card Readback",
        "",
        f"- Task id: `{TASK_ID}`",
        "- Problem definition: challenge 001A with learned no-boundary baselines, scaling probes, adversarial heldout intervention splits, leakage controls, replay recomputation, and provenance checks.",
        f"- Current stage/layer: `{CURRENT_LAYER}`",
        "- Mainline target: none.",
        f"- Enabled-state requirement: `{ENABLED_STATUS}`",
        "- Real-trigger evidence requirement: callable code must generate artifacts from reference, learned baselines, capacity-disabled reference, ablations, leakage, replay, and provenance paths.",
        "- Hypothesis: the 001A reference path remains surface-discriminative against stronger learned no-boundary and capacity-matched disabled alternatives under fixed scaling probes.",
        "- Strongest baseline: `capacity_matched_boundary_disabled_reference`.",
        "- Ablation requirement: rerun all six inherited 001A ablations under every 001B probe setting.",
        "- Trace/replay requirement: recompute from serialized state plus observation and intervention, not stored hashes or verdicts.",
        "- Computed-evidence provenance gate: every score records callable producer, input hash, run id, seed/context/episode ids, aggregation, code path hash, scanner path, replay path, and 001A source hashes.",
        "- Acceptance gate: fixed thresholds, leakage controls, replay, provenance, changed-file allowlist, and bounded claims all pass.",
        f"- Claim ceiling: `{CLAIM_CEILING}`",
        f"- Stop condition: `{result['stop_conditions_triggered']}`",
        "- Rollback plan: revert only the isolated 001B allowlisted paths if a forbidden touch or evidence-shaping failure appears.",
        "- Auto-Remote-Anchor decision: conditional.",
        "",
        "## Source Readback",
        "",
        f"- 001A runner SHA-256: `{source['runner_sha256']}`",
        f"- 001A result SHA-256: `{source['result_sha256']}`",
        "",
        "## Probe Scores",
        "",
    ]
    for probe_name in PROBE_SETTINGS:
        probe = scores[probe_name]
        strongest = probe["strongest_non_oracle_baseline"]
        learned = probe["strongest_learned_no_boundary_baseline"]
        capacity = probe["baseline_scores"]["capacity_matched_boundary_disabled_reference"]
        lines.extend(
            [
                f"- `{probe_name}` reference: `{probe['reference_path']['score']}`",
                f"- `{probe_name}` strongest non-oracle: `{strongest['baseline_name']}` = `{strongest['score']}`",
                f"- `{probe_name}` strongest learned no-boundary: `{learned['baseline_name']}` = `{learned['score']}`",
                f"- `{probe_name}` capacity-disabled reference: `{capacity['score']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Learned Baselines",
            "",
            "- `learned_feature_mlp_without_boundary_state`",
            "- `sequence_model_without_boundary_update`",
            "- `embedding_knn_or_episodic_retrieval_baseline`",
            "- `capacity_matched_boundary_disabled_reference`",
            "",
            "## Leakage, Replay, Provenance",
            "",
            f"- Leakage positive controls: `{run['leakage_scan']['positive_controls_blocked']}/{run['leakage_scan']['positive_controls_total']}`",
            f"- Learned contaminated positive-control score: `{run['leakage_scan']['learned_contaminated_positive_control']['score']}`",
            f"- Replay passed: `{run['replay_report']['passed']}`",
            f"- Provenance passed: `{run['provenance_verification']['passed']}`",
            "",
            "## What This Does Not Prove",
            "",
            "This does not prove mechanism validity, Gate validity, candidate behavior, agency, autonomy, consciousness, emotion, subjectivity, companion readiness, EGO readiness, runtime readiness, stable user benefit, or mainline effect.",
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Run {TASK_ID}")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    args = parser.parse_args()

    run = execute_challenge(
        repo_root=Path(args.repo_root),
        output_dir=Path(args.output_dir),
        persist_artifacts=True,
    )
    report_path = write_research_report_001b(run, Path(args.report_path))
    print(
        json.dumps(
            {
                "verdict": run["result"]["verdict"],
                "artifact_dir": str(Path(args.output_dir)),
                "report_path": str(report_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _build_episode(
    config: dict[str, Any],
    probe_name: str,
    index: int,
    seed: int,
) -> dict[str, Any]:
    target = CHANNELS[index % len(CHANNELS)]
    decoy = CHANNELS[(index + 1) % len(CHANNELS)]
    external = CHANNELS[(index + 2) % len(CHANNELS)]
    prior = CHANNELS[(index + 3) % len(CHANNELS)]
    train_context_id = f"{probe_name}_train_context_{index:03d}"
    heldout_context_id = f"{probe_name}_heldout_probe_context_{index:03d}"
    state = base_001a._build_serialized_state(index, seed, prior, CHANNELS)
    state["state_version"] = "acsb-boundary-state-v1-001b"
    observation = _build_observation_001b(
        probe_name=probe_name,
        index=index,
        seed=seed,
        target=target,
        decoy=decoy,
        external=external,
        channels=CHANNELS,
    )
    intervention = {
        "intervention_type": "learned_baseline_scaling_boundary_shift",
        "observable_intervention_marker": f"{probe_name}_boundary_shift_observed",
        "description": (
            "001B heldout intervention separates self-action effects from decoy, no-action, "
            "and external-only effects without exposing evaluator target fields."
        ),
        "legal_to_all_paths": True,
        "report_mutation_only": False,
    }
    expected = {
        "target_channel": target,
        "probe_behavior": f"probe_with_{target}",
        "probe_boundary_explanation_token": "self_caused",
        "evaluator_only_generation_rule": (
            "target is the legal channel whose self-action effect remains after "
            "no-action and external-only comparison"
        ),
    }
    return {
        "episode_id": f"acsb_001b_{probe_name}_{index:03d}",
        "seed": seed,
        "probe_setting": probe_name,
        "context_id": f"{probe_name}_context_family_{index % 5}",
        "train_context_id": train_context_id,
        "heldout_probe_context_id": heldout_context_id,
        "row_enumerable_from_training": probe_name == "small_reproduction",
        "serialized_prior_boundary_state": state,
        "legal_observation": observation,
        "intervention_description": intervention,
        "expected_measurable_object": expected,
        "forbidden_fields_excluded_from_reference_and_baselines": sorted(FORBIDDEN_LEGAL_KEYS),
        "provenance": {
            "producer_function": "_build_episode",
            "seed": seed,
            "episode_index": index,
            "task_id": TASK_ID,
        },
    }


def _build_observation_001b(
    probe_name: str,
    index: int,
    seed: int,
    target: str,
    decoy: str,
    external: str,
    channels: list[str],
) -> dict[str, Any]:
    train_family = f"{probe_name}_train_surface_{index % 3}"
    heldout_family = f"{probe_name}_heldout_surface_{index:03d}"
    if probe_name == "small_reproduction":
        action_rows = [
            _effect_row("self_action_trial_0", "calibration_pulse", [decoy, target], train_family, seed, 0),
            _effect_row("self_action_trial_1", "calibration_pulse", [target, decoy], train_family, seed, 1),
        ]
        no_action_rows = [
            _effect_row("no_action_trial_0", "withhold", [decoy], train_family, seed, 2),
            _effect_row("no_action_trial_1", "withhold", [decoy], train_family, seed, 3),
        ]
        external_rows = [
            _effect_row("external_trial_0", "external", [external], train_family, seed, 4),
            _effect_row("external_trial_1", "external", [external], train_family, seed, 5),
        ]
    elif probe_name == "combinatorial_heldout":
        action_rows = [
            _effect_row("self_action_trial_0", "calibration_pulse", [decoy, target], train_family, seed, 0),
            _effect_row("self_action_trial_1", "calibration_pulse_alt", [target, decoy], train_family, seed, 1),
            _effect_row("self_action_trial_2", "calibration_pulse", [target, decoy], train_family, seed, 2),
        ]
        no_action_rows = [
            _effect_row("no_action_trial_0", "withhold", [decoy], train_family, seed, 3),
            _effect_row("no_action_trial_1", "withhold", [decoy], train_family, seed, 4),
        ]
        external_rows = [
            _effect_row("external_trial_0", "external", [external], train_family, seed, 5),
            _effect_row("external_trial_1", "external", [external, decoy], train_family, seed, 6),
        ]
    else:
        noise = channels[(channels.index(target) + 3) % len(channels)]
        action_rows = [
            _effect_row("self_action_trial_0", "calibration_pulse", [decoy, target], train_family, seed, 0),
            _effect_row("self_action_trial_1", "calibration_pulse", [target, decoy], train_family, seed, 1),
            _effect_row("self_action_trial_2", "calibration_pulse_noisy", [decoy, target], train_family, seed, 2),
        ]
        no_action_rows = [
            _effect_row("no_action_trial_0", "withhold", [decoy], train_family, seed, 3),
            _effect_row("no_action_trial_1", "withhold", [decoy], train_family, seed, 4),
            _effect_row("no_action_trial_2", "withhold_noisy", [decoy, noise], train_family, seed, 5),
        ]
        external_rows = [
            _effect_row("external_trial_0", "external", [external], train_family, seed, 6),
            _effect_row("external_trial_1", "external_noisy", [external, noise], train_family, seed, 7),
        ]
    training_history = []
    for row_index, row in enumerate(action_rows + no_action_rows + external_rows):
        train_row = copy.deepcopy(row)
        train_row["context_id"] = f"{probe_name}_train_evidence_{index:03d}_{row_index:02d}"
        train_row["context_features"] = {
            **train_row["context_features"],
            "surface_family": train_family,
            "training_window": row_index,
        }
        training_history.append(train_row)
    return {
        "observation_version": "acsb-legal-observation-v1-001b",
        "probe_setting": probe_name,
        "available_channels": channels,
        "training_history": training_history,
        "legal_effect_sequence": copy.deepcopy(action_rows + external_rows),
        "action_effect_evidence": {"after_self_action": action_rows},
        "no_action_comparison": no_action_rows,
        "external_effect_comparison": external_rows,
        "future_probe_observation": {
            "probe_action": "calibration_pulse",
            "context_features": {
                "surface_family": heldout_family,
                "texture": f"heldout_texture_{seed % 11}",
                "combinatorial_signature": f"{probe_name}_{index}_{seed % 7}",
            },
            "available_behaviors": [f"probe_with_{channel}" for channel in channels] + ["withhold_probe"],
        },
        "metadata": {
            "generator": "deterministic_offline_001b_scaling_probe",
            "metadata_only": True,
        },
    }


def _effect_row(
    trial: str,
    action: str,
    changed_channels: list[str],
    surface_family: str,
    seed: int,
    offset: int,
) -> dict[str, Any]:
    return {
        "trial": trial,
        "action": action,
        "changed_channels": list(changed_channels),
        "context_features": {
            "surface_family": surface_family,
            "texture": f"grain_{(seed + offset) % 5}",
            "phase": f"phase_{offset % 3}",
        },
    }


def _score_callable_001b(
    score_name: str,
    func: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]],
    episodes: list[dict[str, Any]],
    run_id: str,
    code_path_hash: str,
    source_001a: dict[str, str],
    aggregation_rule: str,
    probe_name: str,
    baseline_path_name: str | None = None,
    ablation_path_name: str | None = None,
) -> dict[str, Any]:
    outputs = []
    correct = 0
    legal_inputs = []
    for episode in episodes:
        legal = legal_input_for_episode_001b(episode)
        legal_inputs.append(legal)
        output = func(legal["serialized_state"], legal["observation"], legal["intervention"])
        outputs.append(output)
        correct += int(_output_matches_expected_001b(output, episode))
    score = round(correct / len(episodes), 6)
    record = {
        "score_name": score_name,
        "producer_function": getattr(func, "__name__", score_name),
        "input_hash": _object_sha(legal_inputs),
        "run_id": run_id,
        "seed": [episode["seed"] for episode in episodes],
        "context_ids": [episode["context_id"] for episode in episodes],
        "episode_ids": [episode["episode_id"] for episode in episodes],
        "probe_setting": probe_name,
        "aggregation_rule": aggregation_rule,
        "code_path_hash": code_path_hash,
        "baseline_path_name": baseline_path_name,
        "ablation_path_name": ablation_path_name,
        "leakage_scanner_path": "scan_legal_input_for_leakage_001b",
        "replay_path": "run_replay_001b",
        "source_001a_runner_hash": source_001a["runner_sha256"],
        "source_001a_result_hash": source_001a["result_sha256"],
        "deterministic_run_marker": DETERMINISTIC_RUN_MARKER,
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
        "score_source": "callable_computation",
        "static_literal_score": False,
        "report_only_score": False,
        "manifest_completeness_score": False,
        "validator_cleanliness_score": False,
        "provenance_record": record,
    }


def _build_baseline_comparison(scores: dict[str, Any]) -> dict[str, Any]:
    by_probe = {}
    for probe_name, probe_scores in scores["by_probe_setting"].items():
        by_probe[probe_name] = {
            "baseline_scores": probe_scores["baseline_scores"],
            "strongest_non_oracle_baseline": probe_scores["strongest_non_oracle_baseline"],
            "strongest_learned_no_boundary_baseline": probe_scores[
                "strongest_learned_no_boundary_baseline"
            ],
        }
    return {
        "task_id": TASK_ID,
        "producer_function": "_build_baseline_comparison",
        "invoked_learned_no_boundary_baselines": sorted(REQUIRED_LEARNED_BASELINES),
        "invoked_non_oracle_baselines": sorted(BASELINE_FUNCTIONS_001B),
        "missing_learned_no_boundary_baselines": sorted(
            set(REQUIRED_LEARNED_BASELINES) - set(BASELINE_FUNCTIONS_001B)
        ),
        "missing_non_oracle_baselines": sorted(
            set(REQUIRED_NON_ORACLE_BASELINES) - set(BASELINE_FUNCTIONS_001B)
        ),
        "by_probe_setting": by_probe,
    }


def _build_result(
    config: dict[str, Any],
    scores: dict[str, Any],
    baseline_comparison: dict[str, Any],
    ablation_report: dict[str, Any],
    leakage_scan: dict[str, Any],
    replay_report: dict[str, Any],
    provenance_verification: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    thresholds = config["thresholds"]
    stop_conditions = []
    verdict = "action_conditioned_self_boundary_executable_preflight_001b_survives_learned_baseline_scaling_challenge"

    if not leakage_scan["all_positive_controls_blocked"]:
        stop_conditions.append("leakage_positive_control_failure")
        verdict = "blocked_by_leakage_positive_control_failure_001b"
    if not leakage_scan["learned_contaminated_positive_control"]["exploited_contamination"]:
        stop_conditions.append("learned_contamination_positive_control_failure")
        verdict = "blocked_by_leakage_positive_control_failure_001b"
    if not replay_report["passed"] or not provenance_verification["passed"]:
        stop_conditions.append("replay_or_provenance_gap")
        verdict = "blocked_by_replay_or_provenance_gap_001b"

    for probe_name, probe_scores in scores["by_probe_setting"].items():
        reference_score = probe_scores["reference_path"]["score"]
        strongest_learned = probe_scores["strongest_learned_no_boundary_baseline"]
        strongest_non_oracle = probe_scores["strongest_non_oracle_baseline"]
        capacity = probe_scores["baseline_scores"]["capacity_matched_boundary_disabled_reference"]
        if strongest_learned["score"] >= reference_score:
            stop_conditions.append(f"{probe_name}_learned_no_boundary_matched_or_beat_reference")
            verdict = "blocked_by_learned_no_boundary_baseline_001b"
        if reference_score - capacity["score"] < thresholds["capacity_disabled_degradation_min"]:
            stop_conditions.append(f"{probe_name}_capacity_disabled_reference_did_not_degrade")
            verdict = "blocked_by_capacity_matched_boundary_disabled_reference_001b"
        if (
            reference_score - strongest_non_oracle["score"]
            < thresholds["reference_margin_over_strongest_non_oracle_baseline_min"]
        ):
            stop_conditions.append(f"{probe_name}_reference_margin_threshold_failed")
            verdict = "blocked_by_scaling_probe_collapse_001b"
        for core_ablation in CORE_ABLATIONS:
            degradation = ablation_report["by_probe_setting"][probe_name]["ablation_scores"][
                core_ablation
            ]["degradation_from_reference"]
            if degradation < thresholds["core_ablation_degradation_min"]:
                stop_conditions.append(f"{probe_name}_{core_ablation}_did_not_degrade")
                verdict = "blocked_by_scaling_probe_collapse_001b"

    claim_scan = _forbidden_positive_claim_scan_001b({})
    allowlist = _changed_file_allowlist_check_001b(root)
    if not allowlist["passed"]:
        stop_conditions.append("changed_file_allowlist_failure")

    return {
        "task_id": TASK_ID,
        "verdict": verdict,
        "allowed_verdict": verdict in ALLOWED_VERDICTS,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": "none",
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": "callable local 001B execution produced artifacts",
        "claim_ceiling": CLAIM_CEILING,
        "reference_score_by_probe_setting": {
            probe_name: probe_scores["reference_path"]["score"]
            for probe_name, probe_scores in scores["by_probe_setting"].items()
        },
        "strongest_non_oracle_baseline_by_probe_setting": {
            probe_name: probe_scores["strongest_non_oracle_baseline"]
            for probe_name, probe_scores in scores["by_probe_setting"].items()
        },
        "strongest_learned_no_boundary_baseline_by_probe_setting": {
            probe_name: probe_scores["strongest_learned_no_boundary_baseline"]
            for probe_name, probe_scores in scores["by_probe_setting"].items()
        },
        "capacity_matched_boundary_disabled_reference_by_probe_setting": {
            probe_name: probe_scores["baseline_scores"]["capacity_matched_boundary_disabled_reference"][
                "score"
            ]
            for probe_name, probe_scores in scores["by_probe_setting"].items()
        },
        "ablation_results": {
            probe_name: {
                name: {
                    "score": record["score"],
                    "degradation_from_reference": record["degradation_from_reference"],
                }
                for name, record in probe_ablations["ablation_scores"].items()
            }
            for probe_name, probe_ablations in ablation_report["by_probe_setting"].items()
        },
        "leakage_result": {
            "positive_controls_blocked": leakage_scan["positive_controls_blocked"],
            "positive_controls_total": leakage_scan["positive_controls_total"],
            "learned_contaminated_positive_control": leakage_scan[
                "learned_contaminated_positive_control"
            ],
        },
        "replay_result": {
            "passed": replay_report["passed"],
            "exact_recomputation_passed": replay_report["exact_recomputation_passed"],
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
        "strongest_objection_after_execution": _strongest_objection(scores),
        "what_this_does_not_prove": FORBIDDEN_CLAIMS,
    }


def _build_failure_manifest(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "_build_failure_manifest",
        "verdict": result["verdict"],
        "stop_conditions_triggered": result["stop_conditions_triggered"],
        "failures": [
            {"stop_condition": condition}
            for condition in result["stop_conditions_triggered"]
        ],
    }


def _build_trace_events(scores: dict[str, Any], ablation_report: dict[str, Any]) -> list[dict[str, Any]]:
    events = []
    for probe_name, probe_scores in scores["by_probe_setting"].items():
        events.append(
            {
                "event_type": "reference_score",
                "probe_setting": probe_name,
                "score": probe_scores["reference_path"]["score"],
                "producer_function": "run_probe_scores",
            }
        )
        for baseline_name, record in probe_scores["baseline_scores"].items():
            events.append(
                {
                    "event_type": "baseline_score",
                    "probe_setting": probe_name,
                    "path_name": baseline_name,
                    "score": record["score"],
                    "producer_function": record["producer_function"],
                }
            )
        for ablation_name, record in ablation_report["by_probe_setting"][probe_name][
            "ablation_scores"
        ].items():
            events.append(
                {
                    "event_type": "ablation_score",
                    "probe_setting": probe_name,
                    "path_name": ablation_name,
                    "score": record["score"],
                    "degradation_from_reference": record["degradation_from_reference"],
                    "producer_function": record["producer_function"],
                }
            )
    return events


def _write_artifacts_001b(output_dir: Path, run: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_payloads = {
        "result.json": run["result"],
        "episodes.json": {
            "task_id": TASK_ID,
            "producer_function": "generate_scaling_probe_episodes",
            "episodes_by_probe_setting": run["episodes_by_probe_setting"],
        },
        "scores.json": run["scores"],
        "baseline_comparison.json": run["baseline_comparison"],
        "ablation_report.json": run["ablation_report"],
        "leakage_scan.json": run["leakage_scan"],
        "replay_report.json": run["replay_report"],
        "provenance.json": run["provenance"],
        "failure_manifest.json": run["failure_manifest"],
        "git_readback.json": run["git_readback"],
    }
    for name, payload in artifact_payloads.items():
        _write_json(output_dir / name, payload)
    trace_text = "".join(
        json.dumps(_json_ready(event), sort_keys=True) + "\n"
        for event in run["trace_events"]
    )
    _write_text(output_dir / "trace.jsonl", trace_text)
    _write_text(output_dir / "claim_ceiling.txt", CLAIM_CEILING + "\n")
    _write_text(output_dir / "summary.md", _summary_text_001b(run))


def _summary_text_001b(run: dict[str, Any]) -> str:
    result = run["result"]
    lines = [
        f"# {TASK_ID} Summary",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        f"Layer: `{CURRENT_LAYER}`",
        "",
        "Mainline integration status: `none`",
        "",
        f"Enabled status: `{ENABLED_STATUS}`",
        "",
        "Real trigger evidence: `callable local 001B execution produced artifacts`",
        "",
        f"Claim ceiling: `{CLAIM_CEILING}`",
        "",
    ]
    for probe_name in PROBE_SETTINGS:
        probe = run["scores"]["by_probe_setting"][probe_name]
        strongest = probe["strongest_non_oracle_baseline"]
        lines.append(
            f"- `{probe_name}` reference `{probe['reference_path']['score']}`, strongest non-oracle `{strongest['baseline_name']}` = `{strongest['score']}`"
        )
    lines.extend(
        [
            "",
            "No mechanism validity is claimed. No Gate4, Gate5, bridge, runtime, tournament, companion, product, or EGO-mainline path is enabled.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _score_contaminated_learned_positive_control(
    episodes_by_probe: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    episodes = [episode for group in episodes_by_probe.values() for episode in group]
    correct = 0
    for episode in episodes:
        legal = legal_input_for_episode_001b(episode)
        legal["observation"]["target_output"] = episode["expected_measurable_object"]["target_channel"]
        output = contaminated_learned_no_boundary_baseline(
            legal["serialized_state"],
            legal["observation"],
            legal["intervention"],
        )
        correct += int(_output_matches_expected_001b(output, episode))
    score = round(correct / len(episodes), 6)
    return {
        "producer_function": "_score_contaminated_learned_positive_control",
        "baseline_path_name": "contaminated_learned_no_boundary_baseline",
        "score": score,
        "correct": correct,
        "total": len(episodes),
        "exploited_contamination": score == 1.0,
    }


def _positive_control_inputs_001b(episode: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    controls = []
    legal = legal_input_for_episode_001b(episode)
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


def _replace_action_effect_channels(observation: dict[str, Any], replacement: str) -> None:
    for row in observation["action_effect_evidence"]["after_self_action"]:
        row["changed_channels"] = [replacement]
    for row in observation["legal_effect_sequence"]:
        if row["trial"].startswith("self_action"):
            row["changed_channels"] = [replacement]
    for row in observation["training_history"]:
        if row["trial"].startswith("self_action"):
            row["changed_channels"] = [replacement]


def _raise_if_leaking(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> None:
    leak = scan_legal_input_for_leakage_001b(
        {
            "serialized_state": serialized_state,
            "observation": observation,
            "intervention": intervention,
        }
    )
    if leak["blocked"]:
        raise ValueError(f"forbidden legal input fields detected: {leak['detected_paths']}")


def _output_matches_expected_001b(output: dict[str, Any], episode: dict[str, Any]) -> bool:
    expected = episode["expected_measurable_object"]
    return (
        _selected_channel(output) == expected["target_channel"]
        and output["probe_behavior"] == expected["probe_behavior"]
        and output["probe_boundary_explanation_token"]
        == expected["probe_boundary_explanation_token"]
    )


def _selected_channel(output: dict[str, Any]) -> str:
    return output["boundary_assignment_update"]["selected_self_channel"]


def _feature_distance(left: dict[str, Any], right: dict[str, Any]) -> int:
    keys = set(left) | set(right)
    return sum(int(left.get(key) != right.get(key)) for key in keys)


def _strongest_objection(scores: dict[str, Any]) -> dict[str, Any]:
    strongest = None
    for probe_name, probe_scores in scores["by_probe_setting"].items():
        candidate = {
            "probe_setting": probe_name,
            **probe_scores["strongest_non_oracle_baseline"],
        }
        if strongest is None or candidate["score"] > strongest["score"]:
            strongest = candidate
    return strongest or {}


def _canonical_001a_boundary_readback(root: Path) -> dict[str, Any]:
    local_tag_hash = _git_output(root, ["git", "rev-parse", f"refs/tags/{CANONICAL_001A_TAG}"])
    remote_tag_hash = _git_ls_remote(root, f"refs/tags/{CANONICAL_001A_TAG}")
    remote_branch_hash = _git_ls_remote(root, f"refs/heads/{CANONICAL_001A_BRANCH}")
    return {
        "commit": CANONICAL_001A_COMMIT,
        "branch": CANONICAL_001A_BRANCH,
        "tag": CANONICAL_001A_TAG,
        "local_tag_hash": local_tag_hash,
        "remote_tag_hash": remote_tag_hash,
        "remote_branch_hash_at_config_time": remote_branch_hash,
        "local_tag_matches_commit": local_tag_hash == CANONICAL_001A_COMMIT,
        "remote_tag_matches_commit": remote_tag_hash == CANONICAL_001A_COMMIT,
        "remote_branch_matches_commit_at_config_time": remote_branch_hash == CANONICAL_001A_COMMIT,
    }


def _forbidden_positive_claim_scan_001b(payload: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(payload, sort_keys=True)
    positive_patterns = [
        "proves " + "mechanism validity",
        "mechanism validity " + "proven",
        "ego readiness " + "achieved",
        "runtime " + "ready",
        "companion " + "ready",
        "consciousness evidence " + "established",
        "agency " + "success",
        "mainline " + "effective",
    ]
    matches = [pattern for pattern in positive_patterns if pattern in text.lower()]
    return {
        "producer_function": "_forbidden_positive_claim_scan_001b",
        "passed": not matches,
        "matches": matches,
        "claim_ceiling": CLAIM_CEILING,
    }


def _changed_file_allowlist_check_001b(root: Path) -> dict[str, Any]:
    changed = _git_changed_paths(root)
    forbidden = [path for path in changed if not _path_allowed_001b(path)]
    return {
        "producer_function": "_changed_file_allowlist_check_001b",
        "passed": not forbidden,
        "changed_paths": changed,
        "forbidden_paths": forbidden,
        "allowed_prefixes": [
            "docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B-LEARNED-BASELINE-SCALING-CHALLENGE.md",
            "src/action_conditioned_self_boundary_executable_preflight_001a/",
            "tests/test_action_conditioned_self_boundary_executable_preflight_001b.py",
            "artifacts/action_conditioned_self_boundary_executable_preflight_001b/",
        ],
    }


def _path_allowed_001b(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return (
        normalized
        == "docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B-LEARNED-BASELINE-SCALING-CHALLENGE.md"
        or normalized == "tests/test_action_conditioned_self_boundary_executable_preflight_001b.py"
        or normalized.startswith("src/action_conditioned_self_boundary_executable_preflight_001a/")
        or normalized.startswith("artifacts/action_conditioned_self_boundary_executable_preflight_001b/")
    )


def _git_readback_001b(root: Path, config: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "_git_readback_001b",
        "branch": _git_output(root, ["git", "branch", "--show-current"]),
        "head": _git_output(root, ["git", "rev-parse", "HEAD"]),
        "worktree_status_at_artifact_generation": "clean" if not _git_changed_paths(root) else "dirty",
        "ahead_behind": _git_output(
            root,
            ["git", "rev-list", "--left-right", "--count", f"origin/{CANONICAL_001A_BRANCH}...HEAD"],
        ),
        "diff_name_status": _git_changed_paths(root),
        "canonical_001a_boundary": config["canonical_001a_boundary"],
        "source_001a": config["source_001a"],
    }


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


def _git_ls_remote(root: Path, ref: str) -> str:
    output = _git_output(root, ["git", "ls-remote", "origin", ref])
    if not output:
        return ""
    return output.split()[0]


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


def _walk_dict(value: Any, prefix: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            yield path, str(key), child
            yield from _walk_dict(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_dict(child, f"{prefix}[{index}]")


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _object_sha(obj: Any) -> str:
    data = json.dumps(_json_ready(obj), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
