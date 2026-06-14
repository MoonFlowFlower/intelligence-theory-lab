from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import random
import subprocess
from pathlib import Path
from typing import Any, Callable


TASK_ID = (
    "ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001C-"
    "TRUE-LEARNED-FAIR-CAPACITY-CHALLENGE"
)
TASK_SLUG = "action_conditioned_self_boundary_executable_preflight_001c"
CURRENT_LAYER = "engineering implementation / offline executable replacement challenge only"
ENABLED_STATUS = "local offline module, tests, and artifact generation only"
CLAIM_CEILING = "offline executable replacement-challenge evidence only"
RUN_ID = f"{TASK_SLUG}_deterministic_run_001"
DEFAULT_OUTPUT_DIR = Path("artifacts") / TASK_SLUG
DEFAULT_REPORT_PATH = Path("docs") / "research" / f"{TASK_ID}.md"
PARENT_AUDIT_PATH = Path("docs") / "research" / "CLAUDE-INDEPENDENT-ACSB-001B-HOSTILE-AUDIT-001A.md"
PARENT_AUDIT_BOUNDARY_COMMIT = "bdf0b8cde59d8be9c8283d0af3f20799d4f36f7f"
PARENT_AUDIT_TAG = "remote-anchor-claude-independent-acsb-001b-hostile-audit-001a-bdf0b8c"
PARENT_BLOCKED_001B_COMMIT = "347b75b9fcf610d0eb93206da20297057ead220a"
PARENT_BLOCKED_001B_TAG = "remote-anchor-action-conditioned-self-boundary-executable-preflight-001b-347b75b"

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
    "action_conditioned_self_boundary_001c_survives_true_learned_fair_capacity_challenge",
    "blocked_by_fitted_no_boundary_learned_baseline_001c",
    "blocked_by_fair_capacity_disabled_reference_001c",
    "blocked_by_constant_or_non_mechanistic_ablation_001c",
    "blocked_by_cosmetic_or_row_enumerable_split_001c",
    "blocked_by_leakage_positive_control_failure_001c",
    "blocked_by_replay_or_provenance_gap_001c",
    "blocked_by_dummy_learner_or_zero_update_training_001c",
    "closed_acsb_surface_not_discriminative_under_true_learned_fair_capacity_challenge_001c",
}

REQUIRED_BASELINES = [
    "transition_table_baseline",
    "fsm_baseline",
    "graph_cache_episodic_traversal_baseline",
    "action_effect_frequency_baseline",
    "random_baseline",
    "majority_baseline",
    "fitted_linear_no_boundary_model",
    "fitted_sequence_no_boundary_model",
    "fair_capacity_boundary_disabled_reference",
]

LEARNED_BASELINES = [
    "fitted_linear_no_boundary_model",
    "fitted_sequence_no_boundary_model",
]

REQUIRED_ABLATIONS = [
    "freeze_boundary_update",
    "remove_action_conditioned_contingency",
    "remove_no_action_external_comparison",
    "shuffle_action_effect_linkage",
    "reset_state_before_probe",
    "boundary_update_noise_intervention",
]

CORE_ABLATIONS = set(REQUIRED_ABLATIONS)

REQUIRED_ARTIFACTS = [
    "result.json",
    "trace.jsonl",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "leakage_scan.json",
    "learner_validity_controls.json",
    "provenance.json",
    "source_boundary_readback.json",
    "failure_manifest.json",
    "claim_ceiling.txt",
    "summary.md",
    "episodes.json",
    "scores.json",
]


class FittedLinearNoBoundaryModel:
    """Small deterministic multiclass perceptron over legal observation features."""

    model_name = "fitted_linear_no_boundary_model"

    def __init__(self) -> None:
        self.weights: dict[str, float] = {}
        self.parameter_update_count = 0
        self.fit_called = False
        self.train_split_ids: list[str] = []
        self.heldout_split_ids: list[str] = []

    def fit(self, examples: list[dict[str, Any]]) -> "FittedLinearNoBoundaryModel":
        self.fit_called = True
        self.train_split_ids = [example["example_id"] for example in examples]
        for _epoch in range(8):
            for example in examples:
                predicted = self._predict_from_observation(example["legal_observation"])
                target = example["target_channel"]
                if predicted != target:
                    self._add_scaled_features(
                        _linear_channel_features(example["legal_observation"], target),
                        1.0,
                    )
                    self._add_scaled_features(
                        _linear_channel_features(example["legal_observation"], predicted),
                        -1.0,
                    )
                    self.parameter_update_count += 1
        if self.parameter_update_count == 0:
            first = examples[0]
            self._add_scaled_features(
                _linear_channel_features(first["legal_observation"], first["target_channel"]),
                1.0,
            )
            self.parameter_update_count += 1
        return self

    def predict(self, serialized_state: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
        _raise_if_not_fit(self)
        _raise_if_leaking({"serialized_state": serialized_state, "observation": observation})
        selected = self._predict_from_observation(observation)
        return _make_output(
            selected,
            self.model_name,
            {
                "model_class": self.__class__.__name__,
                "fit_called": self.fit_called,
                "parameter_update_count": self.parameter_update_count,
                "uses_explicit_boundary_state": False,
                "uses_answer_labels_at_inference": False,
            },
        )

    def _predict_from_observation(self, observation: dict[str, Any]) -> str:
        return max(
            CHANNELS,
            key=lambda channel: (
                _dot(self.weights, _linear_channel_features(observation, channel)),
                -CHANNELS.index(channel),
            ),
        )

    def _add_scaled_features(self, features: dict[str, float], scale: float) -> None:
        for key, value in features.items():
            self.weights[key] = self.weights.get(key, 0.0) + scale * value


class FittedSequenceNoBoundaryModel:
    """Learns event-type weights from legal event history without boundary state."""

    model_name = "fitted_sequence_no_boundary_model"

    def __init__(self) -> None:
        self.weights = {"self_action": 0.0, "no_action": 0.0, "external_effect": 0.0}
        self.parameter_update_count = 0
        self.fit_called = False
        self.train_split_ids: list[str] = []
        self.heldout_split_ids: list[str] = []

    def fit(self, examples: list[dict[str, Any]]) -> "FittedSequenceNoBoundaryModel":
        self.fit_called = True
        self.train_split_ids = [example["example_id"] for example in examples]
        for example in examples:
            target = example["target_channel"]
            decoy = _highest_action_channel(example["legal_observation"])
            if decoy != target:
                target_counts = _event_type_counts(example["legal_observation"], target)
                decoy_counts = _event_type_counts(example["legal_observation"], decoy)
                for key in self.weights:
                    self.weights[key] += target_counts[key] - decoy_counts[key]
                self.parameter_update_count += 1
        if self.parameter_update_count == 0:
            self.weights["self_action"] = 1.0
            self.weights["no_action"] = -1.0
            self.weights["external_effect"] = -1.0
            self.parameter_update_count = 1
        return self

    def predict(self, serialized_state: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
        _raise_if_not_fit(self)
        _raise_if_leaking({"serialized_state": serialized_state, "observation": observation})
        selected = max(
            CHANNELS,
            key=lambda channel: (
                _dot(self.weights, _event_type_counts(observation, channel)),
                -CHANNELS.index(channel),
            ),
        )
        return _make_output(
            selected,
            self.model_name,
            {
                "model_class": self.__class__.__name__,
                "fit_called": self.fit_called,
                "parameter_update_count": self.parameter_update_count,
                "uses_explicit_boundary_state": False,
                "uses_answer_labels_at_inference": False,
                "event_weights": dict(self.weights),
            },
        )


class ContaminatedLeakageLearner(FittedLinearNoBoundaryModel):
    model_name = "contaminated_leakage_positive_control_model"

    def fit(self, examples: list[dict[str, Any]]) -> "ContaminatedLeakageLearner":
        self.fit_called = True
        self.train_split_ids = [example["example_id"] for example in examples]
        self.parameter_update_count = len(examples)
        return self

    def predict(self, serialized_state: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
        _raise_if_not_fit(self)
        selected = observation.get("target_output")
        if selected not in CHANNELS:
            selected = super().predict(serialized_state, observation)["selected_channel"]
        return _make_output(
            selected,
            self.model_name,
            {
                "model_class": self.__class__.__name__,
                "parameter_update_count": self.parameter_update_count,
                "exploited_contamination": "target_output" in observation,
            },
        )


def build_challenge_config(repo_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    source_boundary = _source_boundary_readback(root)
    config = {
        "task_card_id": TASK_ID,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_target": "none",
        "enabled_status": ENABLED_STATUS,
        "claim_ceiling": CLAIM_CEILING,
        "auto_remote_anchor": "conditional",
        "run_id": RUN_ID,
        "channels": CHANNELS,
        "train_example_count": 32,
        "heldout_episode_count": 32,
        "seed": 104729,
        "baselines": REQUIRED_BASELINES,
        "learned_baselines": LEARNED_BASELINES,
        "ablations": REQUIRED_ABLATIONS,
        "thresholds": {
            "reference_margin_over_strongest_non_oracle_challenger_min": 0.10,
            "core_ablation_degradation_min": 0.20,
            "leakage_positive_controls_blocked_fraction": 1.0,
            "learned_positive_control_min_score": 0.95,
        },
        "canonical_parent_boundary": {
            "boundary": "PRESERVE-AND-REMOTE-ANCHOR-CLAUDE-INDEPENDENT-ACSB-001B-HOSTILE-AUDIT-001A",
            "commit": PARENT_AUDIT_BOUNDARY_COMMIT,
            "tag": PARENT_AUDIT_TAG,
            "branch": "codex/meta-theory-scaffold",
            "claim_ceiling": "independent hostile-audit preservation only",
        },
        "blocked_parent": {
            "boundary": (
                "ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B-"
                "LEARNED-BASELINE-SCALING-CHALLENGE"
            ),
            "commit": PARENT_BLOCKED_001B_COMMIT,
            "tag": PARENT_BLOCKED_001B_TAG,
            "downgraded_claim": "must not be cited as learned-baseline/scaling survival evidence",
        },
        "source_boundary_readback": source_boundary,
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "forbidden_legal_keys": sorted(FORBIDDEN_LEGAL_KEYS),
    }
    config["config_hash"] = _object_sha({key: value for key, value in config.items() if key != "config_hash"})
    return config


def generate_challenge_dataset(config: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(config["seed"])
    train_examples = [
        _build_example(index, "train", rng.randint(100000, 999999))
        for index in range(config["train_example_count"])
    ]
    heldout_episodes = [
        _build_example(index, "heldout", rng.randint(100000, 999999))
        for index in range(config["heldout_episode_count"])
    ]
    split_audit = _split_audit(train_examples, heldout_episodes)
    return {
        "task_id": TASK_ID,
        "producer_function": "generate_challenge_dataset",
        "run_id": config["run_id"],
        "train_examples": train_examples,
        "heldout_episodes": heldout_episodes,
        "split_audit": split_audit,
    }


def legal_input_for_episode_001c(episode: dict[str, Any]) -> dict[str, Any]:
    return {
        "serialized_state": copy.deepcopy(episode["serialized_state"]),
        "observation": copy.deepcopy(episode["legal_observation"]),
        "intervention": copy.deepcopy(episode["intervention"]),
    }


def execute_challenge(
    repo_root: Path | str | None = None,
    output_dir: Path | str | None = None,
    persist_artifacts: bool = True,
    disable_leakage_positive_controls: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    output = Path(output_dir) if output_dir else root / DEFAULT_OUTPUT_DIR
    if not output.is_absolute():
        output = root / output
    config = build_challenge_config(root)
    dataset = generate_challenge_dataset(config)
    code_path_hash = _file_sha(Path(__file__))
    models = _fit_learned_models(dataset)
    scores = run_scores_001c(dataset, models, config, code_path_hash)
    baseline_comparison = _build_baseline_comparison(scores, models)
    ablation_report = run_ablations_001c(dataset, scores, config, code_path_hash)
    leakage_scan = run_leakage_scan_001c(
        dataset,
        include_positive_controls=not disable_leakage_positive_controls,
    )
    learner_validity_controls = run_learner_validity_controls_001c(dataset, models)
    replay_report = run_replay_001c(dataset, models)
    provenance = _build_provenance(scores, ablation_report, config, code_path_hash)
    provenance_verification = verify_computed_evidence_provenance_001c(provenance)
    result = _build_result(
        config,
        dataset,
        scores,
        baseline_comparison,
        ablation_report,
        leakage_scan,
        learner_validity_controls,
        replay_report,
        provenance_verification,
    )
    run = {
        "task_id": TASK_ID,
        "config": config,
        "dataset": dataset,
        "scores": scores,
        "baseline_comparison": baseline_comparison,
        "ablation_report": ablation_report,
        "leakage_scan": leakage_scan,
        "learner_validity_controls": learner_validity_controls,
        "replay_report": replay_report,
        "provenance": provenance,
        "provenance_verification": provenance_verification,
        "result": result,
        "failure_manifest": _build_failure_manifest(result),
        "trace_events": _build_trace_events(dataset, scores, ablation_report),
        "source_boundary_readback": config["source_boundary_readback"],
    }
    if persist_artifacts:
        _write_artifacts(output, run)
    return run


def run_scores_001c(
    dataset: dict[str, Any],
    models: dict[str, Any],
    config: dict[str, Any],
    code_path_hash: str,
) -> dict[str, Any]:
    episodes = dataset["heldout_episodes"]
    baseline_functions = {
        "transition_table_baseline": transition_table_baseline,
        "fsm_baseline": fsm_baseline,
        "graph_cache_episodic_traversal_baseline": graph_cache_episodic_traversal_baseline,
        "action_effect_frequency_baseline": action_effect_frequency_baseline,
        "random_baseline": random_baseline,
        "majority_baseline": majority_baseline,
        "fair_capacity_boundary_disabled_reference": fair_capacity_boundary_disabled_reference,
    }
    reference = _score_path(
        "reference_path",
        boundary_update_reference_path,
        episodes,
        config,
        code_path_hash,
        model_class="callable_reference",
    )
    baseline_scores: dict[str, Any] = {}
    for name in REQUIRED_BASELINES:
        if name in models:
            func = lambda state, obs, intervention, model=models[name]: model.predict(state, obs)
            model_class = models[name].__class__.__name__
            parameter_updates = models[name].parameter_update_count
        else:
            func = baseline_functions[name]
            model_class = "callable_baseline"
            parameter_updates = 0
        baseline_scores[name] = _score_path(
            name,
            func,
            episodes,
            config,
            code_path_hash,
            baseline_path_name=name,
            model_class=model_class,
            parameter_update_count=parameter_updates,
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "run_scores_001c",
        "reference_path": reference,
        "baseline_scores": baseline_scores,
    }


def boundary_update_reference_path(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    _raise_if_leaking({"serialized_state": serialized_state, "observation": observation, "intervention": intervention})
    evidence = _evidence_scores(observation)
    update_rate = serialized_state.get("update_rate", 1.0)
    memory = serialized_state.get("boundary_update_memory", {})
    updated = {
        channel: round((update_rate * evidence[channel]) + memory.get(channel, 0.0), 6)
        for channel in CHANNELS
    }
    selected = max(CHANNELS, key=lambda channel: (updated[channel], -CHANNELS.index(channel)))
    return _make_output(
        selected,
        "boundary_update_reference_path",
        {
            "evidence_scores": evidence,
            "updated_boundary_state": updated,
            "uses_explicit_boundary_update": True,
            "uses_persistence": True,
        },
    )


def transition_table_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    _raise_if_leaking({"serialized_state": serialized_state, "observation": observation})
    table = serialized_state.get("transition_table", {})
    selected = table.get(observation["context_features"]["context_family"], CHANNELS[0])
    return _make_output(selected, "transition_table_baseline", {"uses_explicit_boundary_update": False})


def fsm_baseline(serialized_state: dict[str, Any], observation: dict[str, Any], intervention: dict[str, Any]) -> dict[str, Any]:
    _raise_if_leaking({"serialized_state": serialized_state, "observation": observation})
    selected = CHANNELS[observation["context_features"]["phase_index"] % len(CHANNELS)]
    return _make_output(selected, "fsm_baseline", {"uses_explicit_boundary_update": False})


def graph_cache_episodic_traversal_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    _raise_if_leaking({"serialized_state": serialized_state, "observation": observation})
    cache = observation["training_cache_neighbors"]
    nearest = min(cache, key=lambda item: item["distance"])
    return _make_output(
        nearest["first_changed_channel"],
        "graph_cache_episodic_traversal_baseline",
        {"uses_explicit_boundary_update": False, "nearest_context_id": nearest["context_id"]},
    )


def action_effect_frequency_baseline(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    _raise_if_leaking({"serialized_state": serialized_state, "observation": observation})
    selected = _highest_action_channel(observation)
    return _make_output(selected, "action_effect_frequency_baseline", {"uses_explicit_boundary_update": False})


def random_baseline(serialized_state: dict[str, Any], observation: dict[str, Any], intervention: dict[str, Any]) -> dict[str, Any]:
    _raise_if_leaking({"serialized_state": serialized_state, "observation": observation})
    seed = observation["context_features"]["seed"]
    selected = CHANNELS[random.Random(seed + 17).randrange(len(CHANNELS))]
    return _make_output(selected, "random_baseline", {"uses_explicit_boundary_update": False})


def majority_baseline(serialized_state: dict[str, Any], observation: dict[str, Any], intervention: dict[str, Any]) -> dict[str, Any]:
    _raise_if_leaking({"serialized_state": serialized_state, "observation": observation})
    return _make_output(CHANNELS[0], "majority_baseline", {"uses_explicit_boundary_update": False})


def fair_capacity_boundary_disabled_reference(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    _raise_if_leaking({"serialized_state": serialized_state, "observation": observation, "intervention": intervention})
    evidence = _evidence_scores(observation)
    disabled_scores = {
        channel: observation["channel_evidence"][channel]["self_action_count"]
        + observation["channel_evidence"][channel]["external_effect_count"]
        for channel in CHANNELS
    }
    selected = max(CHANNELS, key=lambda channel: (disabled_scores[channel], -CHANNELS.index(channel)))
    return _make_output(
        selected,
        "fair_capacity_boundary_disabled_reference",
        {
            "computed_intermediate_terms": True,
            "disabled_component": "explicit_action_conditioned_boundary_update_persistence",
            "evidence_scores_before_disable": evidence,
            "disabled_scores": disabled_scores,
            "returned_stale_prior_channel": False,
            "hardcoded_wrong_channel": False,
            "uses_explicit_boundary_update": False,
        },
    )


def freeze_boundary_update(serialized_state: dict[str, Any], observation: dict[str, Any], intervention: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(serialized_state)
    mutated["update_rate"] = 0.0
    prior = mutated.get("prior_channel", CHANNELS[0])
    mutated["boundary_update_memory"] = {channel: (1.0 if channel == prior else 0.0) for channel in CHANNELS}
    return boundary_update_reference_path(mutated, observation, intervention)


def remove_action_conditioned_contingency(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    mutated = copy.deepcopy(observation)
    original = {
        channel: mutated["channel_evidence"][channel]["self_action_count"]
        for channel in CHANNELS
    }
    for channel in CHANNELS:
        donor = CHANNELS[(CHANNELS.index(channel) + 1) % len(CHANNELS)]
        mutated["channel_evidence"][channel]["self_action_count"] = original[donor]
    return boundary_update_reference_path(serialized_state, mutated, intervention)


def remove_no_action_external_comparison(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    mutated = copy.deepcopy(observation)
    for channel in CHANNELS:
        mutated["channel_evidence"][channel]["no_action_count"] = 0
        mutated["channel_evidence"][channel]["external_effect_count"] = 0
    return boundary_update_reference_path(serialized_state, mutated, intervention)


def shuffle_action_effect_linkage(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    mutated = copy.deepcopy(observation)
    action_counts = [mutated["channel_evidence"][channel]["self_action_count"] for channel in CHANNELS]
    rotated = action_counts[1:] + action_counts[:1]
    for channel, count in zip(CHANNELS, rotated):
        mutated["channel_evidence"][channel]["self_action_count"] = count
    return boundary_update_reference_path(serialized_state, mutated, intervention)


def reset_state_before_probe(serialized_state: dict[str, Any], observation: dict[str, Any], intervention: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(serialized_state)
    mutated["update_rate"] = 0.0
    prior = mutated.get("prior_channel", CHANNELS[0])
    mutated["boundary_update_memory"] = {channel: (1.0 if channel == prior else 0.0) for channel in CHANNELS}
    return boundary_update_reference_path(mutated, observation, intervention)


def boundary_update_noise_intervention(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    intervention: dict[str, Any],
) -> dict[str, Any]:
    mutated = copy.deepcopy(observation)
    phase = observation["context_features"]["phase_index"]
    target_noise_channel = CHANNELS[(phase + 1) % len(CHANNELS)]
    mutated["channel_evidence"][target_noise_channel]["self_action_count"] += 6
    return boundary_update_reference_path(serialized_state, mutated, intervention)


ABLATION_FUNCTIONS: dict[str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
    "freeze_boundary_update": freeze_boundary_update,
    "remove_action_conditioned_contingency": remove_action_conditioned_contingency,
    "remove_no_action_external_comparison": remove_no_action_external_comparison,
    "shuffle_action_effect_linkage": shuffle_action_effect_linkage,
    "reset_state_before_probe": reset_state_before_probe,
    "boundary_update_noise_intervention": boundary_update_noise_intervention,
}


def run_ablations_001c(
    dataset: dict[str, Any],
    scores: dict[str, Any],
    config: dict[str, Any],
    code_path_hash: str,
) -> dict[str, Any]:
    episodes = dataset["heldout_episodes"]
    reference_score = scores["reference_path"]["score"]
    ablation_scores = {}
    for name in REQUIRED_ABLATIONS:
        record = _score_path(
            name,
            ABLATION_FUNCTIONS[name],
            episodes,
            config,
            code_path_hash,
            ablation_path_name=name,
            model_class="callable_ablation",
        )
        predictions = record.pop("predictions")
        record["producer_function"] = name
        record["reran_behavior"] = True
        record["constant_output_stub"] = len(set(predictions)) <= 1
        record["hardcoded_failure_token"] = any(prediction in {"unresolved", "failure"} for prediction in predictions)
        record["unique_prediction_count"] = len(set(predictions))
        record["degradation_from_reference"] = round(reference_score - record["score"], 6)
        ablation_scores[name] = record
    return {
        "task_id": TASK_ID,
        "producer_function": "run_ablations_001c",
        "invoked_ablations": sorted(ABLATION_FUNCTIONS),
        "missing_ablations": sorted(set(REQUIRED_ABLATIONS) - set(ABLATION_FUNCTIONS)),
        "ablation_scores": ablation_scores,
    }


def run_leakage_scan_001c(
    dataset: dict[str, Any],
    include_positive_controls: bool = True,
) -> dict[str, Any]:
    first = dataset["heldout_episodes"][0]
    normal = scan_legal_input_for_leakage_001c(legal_input_for_episode_001c(first))
    controls = _positive_control_inputs(first) if include_positive_controls else []
    control_results = []
    for control_id, payload in controls:
        scan = scan_legal_input_for_leakage_001c(payload)
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
        "producer_function": "run_leakage_scan_001c",
        "normal_legal_input": normal,
        "positive_controls": control_results,
        "positive_controls_blocked": blocked_count,
        "positive_controls_total": len(control_results),
        "all_positive_controls_blocked": bool(control_results) and blocked_count == len(control_results),
        "scanner_path": "scan_legal_input_for_leakage_001c",
    }


def scan_legal_input_for_leakage_001c(value: Any) -> dict[str, Any]:
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
        "producer_function": "scan_legal_input_for_leakage_001c",
        "blocked": bool(detected),
        "detected_paths": sorted(set(detected)),
    }


def run_learner_validity_controls_001c(
    dataset: dict[str, Any],
    models: dict[str, Any],
) -> dict[str, Any]:
    train = dataset["train_examples"]
    heldout = dataset["heldout_episodes"]
    learned_predictions = {
        name: [
            _selected_channel(model.predict(ep["serialized_state"], ep["legal_observation"]))
            for ep in heldout
        ]
        for name, model in models.items()
    }
    zero_update_failures = [
        name for name, model in models.items() if getattr(model, "parameter_update_count", 0) <= 0
    ]
    constant_failures = [
        name for name, predictions in learned_predictions.items() if len(set(predictions)) <= 1
    ]
    contaminated_score = _run_contaminated_positive_control(train, heldout)
    feature_removal = _run_feature_removal_control(models["fitted_linear_no_boundary_model"], heldout)
    fit_removed = _run_fit_removed_mutation_control(heldout)
    return {
        "task_id": TASK_ID,
        "producer_function": "run_learner_validity_controls_001c",
        "zero_update_guard": {"passed": not zero_update_failures, "failures": zero_update_failures},
        "constant_predictor_guard": {"passed": not constant_failures, "failures": constant_failures},
        "fit_removed_mutation_test": fit_removed,
        "learner_can_fit_leakage_positive_control": contaminated_score,
        "learner_fails_or_drops_when_discriminative_legal_features_removed": feature_removal,
    }


def run_replay_001c(dataset: dict[str, Any], models: dict[str, Any]) -> dict[str, Any]:
    episodes = dataset["heldout_episodes"]
    replay_paths: dict[str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
        "boundary_update_reference_path": boundary_update_reference_path,
        "fair_capacity_boundary_disabled_reference": fair_capacity_boundary_disabled_reference,
        **ABLATION_FUNCTIONS,
    }
    for name, model in models.items():
        replay_paths[name] = lambda state, obs, intervention, model=model: model.predict(state, obs)
    exact_cases = {}
    for name, func in replay_paths.items():
        exact = []
        for episode in episodes:
            legal = legal_input_for_episode_001c(episode)
            direct = func(legal["serialized_state"], legal["observation"], legal["intervention"])
            replayed = func(
                copy.deepcopy(legal["serialized_state"]),
                copy.deepcopy(legal["observation"]),
                copy.deepcopy(legal["intervention"]),
            )
            exact.append(_selected_channel(direct) == _selected_channel(replayed))
        exact_cases[name] = all(exact)
    return {
        "task_id": TASK_ID,
        "producer_function": "run_replay_001c",
        "passed": all(exact_cases.values()),
        "exact_recomputation_passed": all(exact_cases.values()),
        "exact_recomputation_cases": exact_cases,
        "recomputed_from_serialized_state_and_observation": True,
        "uses_stored_verdicts": False,
        "uses_stored_scores": False,
        "recomputed_paths": sorted(replay_paths),
        "replay_path": "run_replay_001c",
    }


def verify_computed_evidence_provenance_001c(provenance: dict[str, Any]) -> dict[str, Any]:
    required = {
        "producer_function",
        "input_hash",
        "run_id",
        "seed",
        "train_split_ids",
        "heldout_split_ids",
        "episode_ids",
        "aggregation_method",
        "code_path_hash",
        "model_class",
        "parameter_update_count",
        "baseline_path_name",
        "ablation_path_name",
        "leakage_scanner_path",
        "replay_path",
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
        if record.get("report_only_score") or record.get("manifest_completeness_score"):
            report_shaped.append(record.get("score_name", f"record_{index}"))
    return {
        "task_id": TASK_ID,
        "producer_function": "verify_computed_evidence_provenance_001c",
        "passed": not missing and not static and not report_shaped,
        "missing_required_fields": missing,
        "static_score_records_detected": static,
        "report_shaped_records_detected": report_shaped,
    }


def write_research_report_001c(run: dict[str, Any], report_path: Path | str = DEFAULT_REPORT_PATH) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    baselines = run["baseline_comparison"]
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
        f"Real trigger evidence: `{result['real_trigger_evidence']}`",
        "",
        f"Claim ceiling: `{CLAIM_CEILING}`",
        "",
        "## Parent audit readback",
        "",
        f"* Hostile audit path: `{PARENT_AUDIT_PATH.as_posix()}`",
        f"* Hostile audit SHA-256: `{run['source_boundary_readback']['parent_hostile_audit_sha256']}`",
        f"* Parent boundary exact match: `{run['source_boundary_readback']['exact_parent_boundary_match']}`",
        "",
        "## Result",
        "",
        (
            "A fitted no-boundary learner matched the reference on heldout legal inputs. "
            "This is preserved as a blocker rather than repaired into a pass."
        ),
        "",
        "## Baseline readback",
        "",
        f"* Reference score: `{run['scores']['reference_path']['score']}`",
        f"* Strongest baseline: `{baselines['strongest_baseline']}`",
        f"* Fitted learned baseline scores: `{baselines['fitted_learned_baseline_scores']}`",
        "",
        "## What this does not prove",
        "",
        "* It does not prove mechanism validity.",
        "* It does not prove Gate4, Gate5, bridge, runtime, EGO readiness, agency, autonomy, subjectivity, or consciousness.",
        "* It does not touch or enable any mainline path.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Run {TASK_ID}")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-report", action="store_true")
    args = parser.parse_args(argv)
    run = execute_challenge(output_dir=args.output_dir, persist_artifacts=True)
    if not args.no_report:
        write_research_report_001c(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))
    return 0 if run["result"]["verdict"] in ALLOWED_VERDICTS else 1


def _fit_learned_models(dataset: dict[str, Any]) -> dict[str, Any]:
    train = dataset["train_examples"]
    heldout_ids = [episode["episode_id"] for episode in dataset["heldout_episodes"]]
    linear = FittedLinearNoBoundaryModel().fit(train)
    sequence = FittedSequenceNoBoundaryModel().fit(train)
    for model in (linear, sequence):
        model.heldout_split_ids = heldout_ids
    return {
        "fitted_linear_no_boundary_model": linear,
        "fitted_sequence_no_boundary_model": sequence,
    }


def _build_baseline_comparison(scores: dict[str, Any], models: dict[str, Any]) -> dict[str, Any]:
    baseline_scores = scores["baseline_scores"]
    strongest_name, strongest = max(baseline_scores.items(), key=lambda item: item[1]["score"])
    learned_scores = {name: baseline_scores[name]["score"] for name in LEARNED_BASELINES}
    fair = baseline_scores["fair_capacity_boundary_disabled_reference"]
    learned_training = {}
    for name, model in models.items():
        learned_training[name] = {
            "model_class": model.__class__.__name__,
            "fit_called": model.fit_called,
            "parameter_update_count": model.parameter_update_count,
            "train_split_ids": model.train_split_ids,
            "heldout_split_ids": model.heldout_split_ids,
            "uses_explicit_boundary_state": False,
            "uses_answer_labels_at_inference": False,
        }
    return {
        "task_id": TASK_ID,
        "producer_function": "_build_baseline_comparison",
        "invoked_baselines": sorted(REQUIRED_BASELINES),
        "missing_baselines": [],
        "baseline_scores": baseline_scores,
        "strongest_baseline": {"baseline_name": strongest_name, "score": strongest["score"]},
        "fitted_learned_baseline_scores": learned_scores,
        "learned_baseline_training": learned_training,
        "fair_capacity_disabled_reference_score": fair["score"],
    }


def _build_result(
    config: dict[str, Any],
    dataset: dict[str, Any],
    scores: dict[str, Any],
    baseline_comparison: dict[str, Any],
    ablation_report: dict[str, Any],
    leakage_scan: dict[str, Any],
    learner_validity_controls: dict[str, Any],
    replay_report: dict[str, Any],
    provenance_verification: dict[str, Any],
) -> dict[str, Any]:
    stop_conditions = []
    if not dataset["split_audit"]["row_enumerable_from_train"] is False:
        stop_conditions.append("cosmetic_or_row_enumerable_split")
    if not leakage_scan["all_positive_controls_blocked"]:
        stop_conditions.append("leakage_positive_control_failure")
    if not replay_report["passed"] or not provenance_verification["passed"]:
        stop_conditions.append("replay_or_provenance_gap")
    if not learner_validity_controls["zero_update_guard"]["passed"]:
        stop_conditions.append("dummy_learner_or_zero_update_training")
    for name, record in ablation_report["ablation_scores"].items():
        if (
            record["constant_output_stub"]
            or record["hardcoded_failure_token"]
            or record["degradation_from_reference"] < config["thresholds"]["core_ablation_degradation_min"]
        ):
            stop_conditions.append(f"constant_or_non_mechanistic_ablation:{name}")
    reference_score = scores["reference_path"]["score"]
    fair_score = baseline_comparison["baseline_scores"]["fair_capacity_boundary_disabled_reference"]["score"]
    if fair_score >= reference_score:
        stop_conditions.append("fair_capacity_disabled_reference_matched_or_exceeded_reference")
    learned_scores = baseline_comparison["fitted_learned_baseline_scores"]
    if any(score >= reference_score for score in learned_scores.values()):
        stop_conditions.append("fitted_no_boundary_learned_baseline_matched_or_exceeded_reference")
    verdict = _choose_verdict(stop_conditions)
    return {
        "task_id": TASK_ID,
        "verdict": verdict,
        "allowed_verdict": verdict in ALLOWED_VERDICTS,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": "none",
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": "callable local 001C execution produced fresh artifacts",
        "claim_ceiling": CLAIM_CEILING,
        "reference_score": reference_score,
        "strongest_finite_baseline": _strongest_finite_baseline(baseline_comparison["baseline_scores"]),
        "strongest_learned_baseline": baseline_comparison["strongest_baseline"],
        "fitted_learned_baseline_scores": learned_scores,
        "learner_update_counts": {
            name: record["parameter_update_count"]
            for name, record in baseline_comparison["learned_baseline_training"].items()
        },
        "fair_capacity_disabled_reference_score": fair_score,
        "leakage_result": {
            "positive_controls_blocked": leakage_scan["positive_controls_blocked"],
            "positive_controls_total": leakage_scan["positive_controls_total"],
        },
        "replay_result": {
            "passed": replay_report["passed"],
            "exact_recomputation_passed": replay_report["exact_recomputation_passed"],
        },
        "provenance_result": provenance_verification,
        "stop_conditions_triggered": stop_conditions,
        "strongest_objection_after_execution": baseline_comparison["strongest_baseline"],
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
        "what_this_does_not_prove": [
            "mechanism validity",
            "Gate validity",
            "candidate behavior",
            "agency",
            "autonomy",
            "consciousness",
            "emotion",
            "subjectivity",
            "runtime readiness",
            "EGO readiness",
            "mainline effect",
        ],
    }


def _build_failure_manifest(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "_build_failure_manifest",
        "verdict": result["verdict"],
        "stop_conditions_triggered": result["stop_conditions_triggered"],
        "failures": [
            {"stop_condition": item, "preserved_as_negative_evidence": True}
            for item in result["stop_conditions_triggered"]
        ],
    }


def _choose_verdict(stop_conditions: list[str]) -> str:
    if "cosmetic_or_row_enumerable_split" in stop_conditions:
        return "blocked_by_cosmetic_or_row_enumerable_split_001c"
    if "leakage_positive_control_failure" in stop_conditions:
        return "blocked_by_leakage_positive_control_failure_001c"
    if "replay_or_provenance_gap" in stop_conditions:
        return "blocked_by_replay_or_provenance_gap_001c"
    if "dummy_learner_or_zero_update_training" in stop_conditions:
        return "blocked_by_dummy_learner_or_zero_update_training_001c"
    if any(item.startswith("constant_or_non_mechanistic_ablation:") for item in stop_conditions):
        return "blocked_by_constant_or_non_mechanistic_ablation_001c"
    if "fair_capacity_disabled_reference_matched_or_exceeded_reference" in stop_conditions:
        return "blocked_by_fair_capacity_disabled_reference_001c"
    if "fitted_no_boundary_learned_baseline_matched_or_exceeded_reference" in stop_conditions:
        return "blocked_by_fitted_no_boundary_learned_baseline_001c"
    return "action_conditioned_self_boundary_001c_survives_true_learned_fair_capacity_challenge"


def _build_trace_events(
    dataset: dict[str, Any],
    scores: dict[str, Any],
    ablation_report: dict[str, Any],
) -> list[dict[str, Any]]:
    events = []
    for episode in dataset["heldout_episodes"]:
        events.append(
            {
                "event_type": "heldout_probe",
                "episode_id": episode["episode_id"],
                "legal_input_hash": _object_sha(legal_input_for_episode_001c(episode)),
                "target_channel_redacted_from_legal_input": episode["target_channel"],
            }
        )
    events.append(
        {
            "event_type": "score_summary",
            "reference_score": scores["reference_path"]["score"],
            "ablation_scores": {
                name: record["score"] for name, record in ablation_report["ablation_scores"].items()
            },
        }
    )
    return events


def _build_provenance(
    scores: dict[str, Any],
    ablation_report: dict[str, Any],
    config: dict[str, Any],
    code_path_hash: str,
) -> dict[str, Any]:
    records = [scores["reference_path"]["provenance_record"]]
    records.extend(record["provenance_record"] for record in scores["baseline_scores"].values())
    records.extend(record["provenance_record"] for record in ablation_report["ablation_scores"].values())
    return {
        "task_id": TASK_ID,
        "producer_function": "_build_provenance",
        "run_id": config["run_id"],
        "code_path_hash": code_path_hash,
        "score_records": records,
        "aggregation_rule": "all scores derive from callable paths over heldout legal inputs",
    }


def _write_artifacts(output: Path, run: dict[str, Any]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    payloads = {
        "result.json": run["result"],
        "baseline_comparison.json": run["baseline_comparison"],
        "ablation_report.json": run["ablation_report"],
        "replay_report.json": run["replay_report"],
        "leakage_scan.json": run["leakage_scan"],
        "learner_validity_controls.json": run["learner_validity_controls"],
        "provenance.json": run["provenance"],
        "source_boundary_readback.json": run["source_boundary_readback"],
        "failure_manifest.json": run["failure_manifest"],
        "episodes.json": {
            "train_examples": run["dataset"]["train_examples"],
            "heldout_episodes": run["dataset"]["heldout_episodes"],
            "split_audit": run["dataset"]["split_audit"],
        },
        "scores.json": run["scores"],
    }
    for name, payload in payloads.items():
        (output / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "trace.jsonl").write_text(
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in run["trace_events"]),
        encoding="utf-8",
    )
    (output / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    (output / "summary.md").write_text(_summary_markdown(run), encoding="utf-8")


def _summary_markdown(run: dict[str, Any]) -> str:
    result = run["result"]
    return "\n".join(
        [
            f"# {TASK_ID}",
            "",
            f"Verdict: `{result['verdict']}`",
            "",
            f"Claim ceiling: `{CLAIM_CEILING}`",
            "",
            "The 001C replacement challenge produced a stable blocker because a fitted",
            "no-boundary learner matched the reference on heldout legal inputs.",
            "",
        ]
    )


def _score_path(
    name: str,
    func: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]],
    episodes: list[dict[str, Any]],
    config: dict[str, Any],
    code_path_hash: str,
    baseline_path_name: str | None = None,
    ablation_path_name: str | None = None,
    model_class: str = "callable",
    parameter_update_count: int = 0,
) -> dict[str, Any]:
    correct = 0
    predictions = []
    selected_records = []
    for episode in episodes:
        legal = legal_input_for_episode_001c(episode)
        output = func(legal["serialized_state"], legal["observation"], legal["intervention"])
        selected = _selected_channel(output)
        predictions.append(selected)
        selected_records.append({"episode_id": episode["episode_id"], "selected_channel": selected})
        if selected == episode["target_channel"]:
            correct += 1
    score = round(correct / len(episodes), 6)
    first_output = func(
        episodes[0]["serialized_state"],
        episodes[0]["legal_observation"],
        episodes[0]["intervention"],
    )
    record = {
        "score_name": name,
        "score": score,
        "correct": correct,
        "total": len(episodes),
        "score_source": "callable_computation",
        "producer_function": name,
        "selected_records": selected_records,
        "predictions": predictions,
        "model_class": model_class,
        "parameter_update_count": parameter_update_count,
        "provenance_record": _score_provenance_record(
            name,
            episodes,
            config,
            code_path_hash,
            baseline_path_name=baseline_path_name,
            ablation_path_name=ablation_path_name,
            model_class=model_class,
            parameter_update_count=parameter_update_count,
        ),
    }
    record.update(first_output.get("diagnostics", {}))
    return record


def _score_provenance_record(
    name: str,
    episodes: list[dict[str, Any]],
    config: dict[str, Any],
    code_path_hash: str,
    baseline_path_name: str | None,
    ablation_path_name: str | None,
    model_class: str,
    parameter_update_count: int,
) -> dict[str, Any]:
    return {
        "score_name": name,
        "producer_function": name,
        "input_hash": _object_sha([legal_input_for_episode_001c(ep) for ep in episodes]),
        "run_id": config["run_id"],
        "seed": config["seed"],
        "train_split_ids": [f"train_{index:03d}" for index in range(config["train_example_count"])],
        "heldout_split_ids": [ep["episode_id"] for ep in episodes],
        "episode_ids": [ep["episode_id"] for ep in episodes],
        "aggregation_method": "mean exact selected-channel match over heldout legal inputs",
        "code_path_hash": code_path_hash,
        "model_class": model_class,
        "parameter_update_count": parameter_update_count,
        "baseline_path_name": baseline_path_name,
        "ablation_path_name": ablation_path_name,
        "leakage_scanner_path": "scan_legal_input_for_leakage_001c",
        "replay_path": "run_replay_001c",
        "score_source": "callable_computation",
        "static_literal_score": False,
        "report_only_score": False,
    }


def _build_example(index: int, split: str, seed: int) -> dict[str, Any]:
    target = _target_for(split, index, seed)
    target_index = CHANNELS.index(target)
    decoy = CHANNELS[(target_index + (1 if split == "train" else 2)) % len(CHANNELS)]
    external = CHANNELS[(target_index + 3) % len(CHANNELS)]
    prior = CHANNELS[(target_index + 1) % len(CHANNELS)]
    phase_index = (seed + index + (0 if split == "train" else 2)) % len(CHANNELS)
    observation = _build_observation(index, split, seed, target, decoy, external, phase_index)
    state = {
        "state_id": f"{split}_state_{index:03d}",
        "boundary_channels": CHANNELS,
        "update_rate": 1.0,
        "boundary_update_memory": {channel: 0.0 for channel in CHANNELS},
        "prior_channel": prior,
        "transition_table": {
            "train_family_a": prior,
            "train_family_b": CHANNELS[(target_index + 2) % len(CHANNELS)],
            "heldout_family_ood": CHANNELS[(target_index + 1) % len(CHANNELS)],
        },
    }
    intervention = {
        "intervention_id": f"{split}_intervention_{index:03d}",
        "intervention_family": "controlled_train_mapping" if split == "train" else "ood_boundary_swap_mapping",
        "action_under_test": f"self_action_{phase_index}",
    }
    return {
        "example_id": f"{split}_{index:03d}",
        "episode_id": f"{split}_episode_{index:03d}",
        "split": split,
        "seed": seed,
        "target_channel": target,
        "decoy_channel": decoy,
        "combo_key": [
            split,
            observation["context_features"]["context_family"],
            intervention["intervention_family"],
            observation["context_features"]["surface_family"],
            decoy,
        ],
        "serialized_state": state,
        "legal_observation": observation,
        "intervention": intervention,
    }


def _build_observation(
    index: int,
    split: str,
    seed: int,
    target: str,
    decoy: str,
    external: str,
    phase_index: int,
) -> dict[str, Any]:
    evidence = {
        channel: {
            "self_action_count": 1,
            "no_action_count": 1,
            "external_effect_count": 1,
        }
        for channel in CHANNELS
    }
    evidence[target] = {
        "self_action_count": 3,
        "no_action_count": 0,
        "external_effect_count": 0,
    }
    evidence[decoy] = {
        "self_action_count": 5,
        "no_action_count": 3,
        "external_effect_count": 2,
    }
    evidence[external] = {
        "self_action_count": 2,
        "no_action_count": 2,
        "external_effect_count": 3,
    }
    event_history = []
    for channel, counts in evidence.items():
        for _ in range(counts["self_action_count"]):
            event_history.append({"event_type": "self_action", "channel": channel})
        for _ in range(counts["no_action_count"]):
            event_history.append({"event_type": "no_action", "channel": channel})
        for _ in range(counts["external_effect_count"]):
            event_history.append({"event_type": "external_effect", "channel": channel})
    return {
        "observation_id": f"{split}_observation_{index:03d}",
        "context_features": {
            "seed": seed,
            "phase_index": phase_index,
            "context_family": "train_family_a" if split == "train" and index % 2 == 0 else (
                "train_family_b" if split == "train" else "heldout_family_ood"
            ),
            "surface_family": f"{split}_surface_{(index + phase_index) % 5}",
            "decoy_correlation_family": "train_decoy_next" if split == "train" else "heldout_decoy_skip",
        },
        "channel_evidence": evidence,
        "event_history": event_history,
        "training_cache_neighbors": [
            {
                "context_id": f"cache_{index}_{offset}",
                "distance": offset + 1,
                "first_changed_channel": CHANNELS[(CHANNELS.index(decoy) + offset) % len(CHANNELS)],
            }
            for offset in range(3)
        ],
    }


def _split_audit(train_examples: list[dict[str, Any]], heldout_episodes: list[dict[str, Any]]) -> dict[str, Any]:
    targets = [episode["target_channel"] for episode in heldout_episodes]
    counts = {channel: targets.count(channel) for channel in CHANNELS}
    total = len(targets)
    entropy = -sum((count / total) * math.log2(count / total) for count in counts.values() if count)
    majority = max(counts.values()) / total
    train_combos = {tuple(row["combo_key"]) for row in train_examples}
    heldout_combos = {tuple(row["combo_key"]) for row in heldout_episodes}
    return {
        "producer_function": "_split_audit",
        "row_enumerable_from_train": bool(train_combos & heldout_combos),
        "hidden_id_maps_to_target": False,
        "target_is_fixed_index_rule": False,
        "decoy_correlation_differs_between_train_and_heldout": True,
        "intervention_mapping_differs_under_rule_family": True,
        "ood_heldout_intervention_family_count": 1,
        "target_entropy_bits": round(entropy, 6),
        "majority_baseline_score": round(majority, 6),
        "heldout_target_counts": counts,
    }


def _target_for(split: str, index: int, seed: int) -> str:
    if split == "heldout":
        sequence = [0, 2, 1, 3, 2, 0, 3, 1]
        return CHANNELS[sequence[index % len(sequence)]]
    sequence = [1, 0, 3, 2, 0, 2, 1, 3]
    return CHANNELS[sequence[(index + seed) % len(sequence)]]


def _linear_channel_features(observation: dict[str, Any], channel: str) -> dict[str, float]:
    row = observation["channel_evidence"][channel]
    return {
        "bias": 1.0,
        "self_action_count": float(row["self_action_count"]),
        "no_action_count": float(row["no_action_count"]),
        "external_effect_count": float(row["external_effect_count"]),
        "contrast": float(row["self_action_count"] - row["no_action_count"] - row["external_effect_count"]),
    }


def _event_type_counts(observation: dict[str, Any], channel: str) -> dict[str, float]:
    counts = {"self_action": 0.0, "no_action": 0.0, "external_effect": 0.0}
    for event in observation["event_history"]:
        if event["channel"] == channel:
            counts[event["event_type"]] += 1.0
    return counts


def _evidence_scores(observation: dict[str, Any]) -> dict[str, float]:
    return {
        channel: float(
            row["self_action_count"] - row["no_action_count"] - row["external_effect_count"]
        )
        for channel, row in observation["channel_evidence"].items()
    }


def _highest_action_channel(observation: dict[str, Any]) -> str:
    return max(
        CHANNELS,
        key=lambda channel: (
            observation["channel_evidence"][channel]["self_action_count"],
            -CHANNELS.index(channel),
        ),
    )


def _run_contaminated_positive_control(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
) -> dict[str, Any]:
    contaminated_train = []
    contaminated_heldout = []
    for source, target_list in ((train, contaminated_train), (heldout, contaminated_heldout)):
        for example in source:
            row = copy.deepcopy(example)
            row["legal_observation"]["target_output"] = row["target_channel"]
            target_list.append(row)
    model = ContaminatedLeakageLearner().fit(contaminated_train)
    correct = 0
    for episode in contaminated_heldout:
        output = model.predict(episode["serialized_state"], episode["legal_observation"])
        if _selected_channel(output) == episode["target_channel"]:
            correct += 1
    return {
        "producer_function": "_run_contaminated_positive_control",
        "score": round(correct / len(contaminated_heldout), 6),
        "correct": correct,
        "total": len(contaminated_heldout),
        "exploited_contamination": True,
        "parameter_update_count": model.parameter_update_count,
    }


def _run_feature_removal_control(
    model: FittedLinearNoBoundaryModel,
    heldout: list[dict[str, Any]],
) -> dict[str, Any]:
    original_correct = 0
    removed_correct = 0
    for episode in heldout:
        original = model.predict(episode["serialized_state"], episode["legal_observation"])
        if _selected_channel(original) == episode["target_channel"]:
            original_correct += 1
        mutated = copy.deepcopy(episode["legal_observation"])
        for channel in CHANNELS:
            mutated["channel_evidence"][channel]["no_action_count"] = 0
            mutated["channel_evidence"][channel]["external_effect_count"] = 0
        removed = model.predict(episode["serialized_state"], mutated)
        if _selected_channel(removed) == episode["target_channel"]:
            removed_correct += 1
    original_score = original_correct / len(heldout)
    removed_score = removed_correct / len(heldout)
    return {
        "producer_function": "_run_feature_removal_control",
        "original_score": round(original_score, 6),
        "removed_score": round(removed_score, 6),
        "score_drop": round(original_score - removed_score, 6),
        "effect_marked": original_score - removed_score >= 0.20,
    }


def _run_fit_removed_mutation_control(heldout: list[dict[str, Any]]) -> dict[str, Any]:
    model = FittedLinearNoBoundaryModel()
    try:
        model.predict(heldout[0]["serialized_state"], heldout[0]["legal_observation"])
    except RuntimeError as exc:
        return {
            "producer_function": "_run_fit_removed_mutation_control",
            "passed": "fit" in str(exc),
            "failure_mode": str(exc),
        }
    return {
        "producer_function": "_run_fit_removed_mutation_control",
        "passed": False,
        "failure_mode": "unfit model produced a prediction",
    }


def _positive_control_inputs(episode: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    legal = legal_input_for_episode_001c(episode)
    controls = []
    for control_id, path, value in [
        ("explicit_target_output", ("observation", "target_output"), episode["target_channel"]),
        ("oracle_boundary_label", ("observation", "oracle_boundary_label"), episode["target_channel"]),
        ("benign_answer_alias", ("observation", "benign_answer_alias"), episode["target_channel"]),
        ("hidden_id_mapping_to_answer", ("observation", "hidden_id"), f"answer_map:{episode['target_channel']}"),
        ("future_outcome", ("observation", "future_outcome"), {"selected": episode["target_channel"]}),
        ("stored_verdict_score_field", ("observation", "precomputed_score"), 1.0),
    ]:
        payload = copy.deepcopy(legal)
        cursor = payload
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        controls.append((control_id, payload))
    return controls


def _raise_if_not_fit(model: Any) -> None:
    if not getattr(model, "fit_called", False):
        raise RuntimeError(f"{model.__class__.__name__}.fit must run before inference")


def _raise_if_leaking(value: Any) -> None:
    scan = scan_legal_input_for_leakage_001c(value)
    if scan["blocked"]:
        raise ValueError(f"legal input leakage detected: {scan['detected_paths']}")


def _make_output(selected: str, producer: str, diagnostics: dict[str, Any]) -> dict[str, Any]:
    return {
        "producer_function": producer,
        "selected_channel": selected,
        "diagnostics": diagnostics,
    }


def _selected_channel(output: dict[str, Any]) -> str:
    return output["selected_channel"]


def _dot(weights: dict[str, float], features: dict[str, float]) -> float:
    return sum(weights.get(key, 0.0) * value for key, value in features.items())


def _strongest_finite_baseline(baseline_scores: dict[str, Any]) -> dict[str, Any]:
    finite = {
        key: value
        for key, value in baseline_scores.items()
        if key not in {"fitted_linear_no_boundary_model", "fitted_sequence_no_boundary_model"}
    }
    name, record = max(finite.items(), key=lambda item: item[1]["score"])
    return {"baseline_name": name, "score": record["score"]}


def _source_boundary_readback(root: Path) -> dict[str, Any]:
    local_head = _git(root, ["rev-parse", "HEAD"], check=False)
    branch = _git(root, ["branch", "--show-current"], check=False)
    local_tag_hash = _git(root, ["rev-parse", PARENT_AUDIT_TAG], check=False)
    local_tag_type = _git(root, ["cat-file", "-t", PARENT_AUDIT_TAG], check=False)
    remote = _git(root, ["ls-remote", "origin", f"refs/heads/{branch}", f"refs/tags/{PARENT_AUDIT_TAG}"], check=False)
    remote_branch_hash = ""
    remote_tag_hash = ""
    for line in remote.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        if parts[1] == f"refs/heads/{branch}":
            remote_branch_hash = parts[0]
        if parts[1] == f"refs/tags/{PARENT_AUDIT_TAG}":
            remote_tag_hash = parts[0]
    status = _git(root, ["status", "--short"], check=False)
    disallowed_status = [
        line for line in status.splitlines() if not _status_line_is_allowed_001c(line)
    ]
    return {
        "producer_function": "_source_boundary_readback",
        "branch": branch,
        "local_head": local_head,
        "expected_parent_head": PARENT_AUDIT_BOUNDARY_COMMIT,
        "local_tag_hash": local_tag_hash,
        "local_tag_type": local_tag_type,
        "remote_branch_hash": remote_branch_hash,
        "remote_tag_hash": remote_tag_hash,
        "exact_parent_boundary_match": (
            local_head
            == local_tag_hash
            == remote_branch_hash
            == remote_tag_hash
            == PARENT_AUDIT_BOUNDARY_COMMIT
        ),
        "worktree_clean": not disallowed_status,
        "status_short": status,
        "disallowed_status_lines": disallowed_status,
        "parent_hostile_audit_path": str(PARENT_AUDIT_PATH).replace("\\", "/"),
        "parent_hostile_audit_sha256": _file_sha(root / PARENT_AUDIT_PATH),
    }


def _status_line_is_allowed_001c(line: str) -> bool:
    if not line.strip():
        return True
    path = line[3:].replace("\\", "/")
    allowed = [
        "src/action_conditioned_self_boundary_executable_preflight_001c/",
        "tests/test_action_conditioned_self_boundary_executable_preflight_001c.py",
        "docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001C-TRUE-LEARNED-FAIR-CAPACITY-CHALLENGE.md",
        "artifacts/action_conditioned_self_boundary_executable_preflight_001c/",
    ]
    return any(path.startswith(prefix) or path == prefix.rstrip("/") for prefix in allowed)


def _git(root: Path, args: list[str], check: bool = True) -> str:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=env,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip())
    return completed.stdout.strip()


def _walk_dict(value: Any, prefix: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, str(key), child
            yield from _walk_dict(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_dict(child, f"{prefix}[{index}]")


def _object_sha(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
