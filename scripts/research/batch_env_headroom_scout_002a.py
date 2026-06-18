from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Callable

from evidence_provenance_001a import code_path_hash, stable_json_hash, write_json


TASK_ID = "BATCH-ENV-HEADROOM-SCOUT-002A"
ARTIFACT_DIR_REL = "artifacts/batch_env_headroom_scout_002a"
CURRENT_LAYER = "engineering-governance / Phase-0 environment portfolio scouting"
MAINLINE_STATUS = "none"
ENABLED_STATUS = "no runtime/mainline/admission/bridge path enabled"
CLAIM_CEILING = (
    "candidate-free environment portfolio scouting only. No headroom confirmation. "
    "No Gate1 pass. No mechanism validity. No candidate feasibility. No runtime/mainline effect. "
    "No agency/autonomy/consciousness/EGO readiness."
)

LABELS = ["route_alpha", "route_beta", "route_gamma"]
TRAIN_COUNT = 180
TEST_COUNT = 120
PROMOTION_GAP = 0.08
ORACLE_FLOOR = 0.80
EQUIVALENCE_BAND = 0.03

REQUIRED_ARTIFACT_FILENAMES = [
    "sketch_registry.json",
    "static_kill_scan.json",
    "micro_probe_results.json",
    "promoted_full_harness_candidates.json",
    "rejected_sketches.json",
    "final_report.md",
]

STATIC_KILL_CRITERIA = [
    "target_deterministic_from_le_budget_visible_channels",
    "legal_query_can_read_all_target_components",
    "graph_cache_transition_table_recovers_target_exactly",
    "visible_fields_leak_target",
    "passive_decoder_likely_reaches_oracle",
    "oracle_needs_hidden_state_answer_key_or_future_labels",
    "metric_degenerate",
    "state_space_small_enough_for_trivial_lookup_saturation",
]

ALLOWED_MICRO_PROBE_VERDICTS = {
    "reject_no_headroom_likely",
    "reject_direct_decode",
    "reject_graph_cache_saturated",
    "reject_passive_decodable",
    "reject_metric_degenerate",
    "blocked_oracle_not_budget_faithful",
    "promote_to_full_harness_candidate",
}


def _run_git(repo_root: Path, args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    if completed.returncode != 0:
        return (completed.stderr or completed.stdout).strip()
    return completed.stdout.strip()


def _stable_seed(*parts: str) -> int:
    digest = hashlib.sha256("::".join(parts).encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def _risk(level: str, rationale: str) -> dict[str, str]:
    return {"level": level, "rationale": rationale}


def _sketch(
    sketch_id: str,
    target_rule: str,
    visible_channel_boundary: str,
    legal_query_budget: int,
    oracle_definition: str,
    expected_strongest_cheap_baseline: str,
    direct_decode_risk: dict[str, str],
    graph_cache_lookup_risk: dict[str, str],
    passive_decoder_risk: dict[str, str],
    metric_degeneracy_risk: dict[str, str],
    replay_requirement: str,
    leakage_controls: list[str],
    stop_condition: str,
    static_flags: dict[str, bool],
    probe_kind: str | None = None,
) -> dict[str, Any]:
    return {
        "sketch_id": sketch_id,
        "target_rule": target_rule,
        "visible_channel_boundary": visible_channel_boundary,
        "legal_query_budget": legal_query_budget,
        "oracle_definition": oracle_definition,
        "expected_strongest_cheap_baseline": expected_strongest_cheap_baseline,
        "direct_decode_risk": direct_decode_risk,
        "graph_cache_lookup_risk": graph_cache_lookup_risk,
        "passive_decoder_risk": passive_decoder_risk,
        "metric_degeneracy_risk": metric_degeneracy_risk,
        "replay_requirement": replay_requirement,
        "leakage_controls": leakage_controls,
        "claim_ceiling": CLAIM_CEILING,
        "stop_condition": stop_condition,
        "static_kill_flags": {criterion: bool(static_flags.get(criterion, False)) for criterion in STATIC_KILL_CRITERIA},
        "probe_kind": probe_kind,
        "candidate_implementation_authorized": False,
        "route_tournament_authorized": False,
        "auto_remote_anchor": "forbidden",
    }


def build_sketch_registry() -> list[dict[str, Any]]:
    base_visible_boundary = (
        "Passive fields may include public counters, coarse buckets, and non-answer hints. "
        "Diagnostic hidden_state, answer_key, future labels, and target aliases are forbidden."
    )
    base_replay = "Replay must recompute prediction from serialized visible state, legal query trace, and budget ledger."
    base_leakage = [
        "inject target_label_alias positive control",
        "inject answer_key positive control",
        "inject future_label positive control",
        "inject context_id_as_target_key positive control",
    ]
    no_flags = {criterion: False for criterion in STATIC_KILL_CRITERIA}
    return [
        _sketch(
            "legal_bundle_linear_sum",
            "Target is a deterministic sum of all legal component probes modulo the label count.",
            base_visible_boundary,
            5,
            "Visible oracle reads every component probe and applies the same sum.",
            "exhaustive_legal_query",
            _risk("fatal", "The full legal bundle is the target decomposition."),
            _risk("fatal", "Transition table over the legal bundle is exact."),
            _risk("medium", "Passive hints are not enough, but active legal query is fatal."),
            _risk("low", "Balanced labels can be generated."),
            base_replay,
            base_leakage,
            "Reject if legal query reads all target components.",
            {
                "target_deterministic_from_le_budget_visible_channels": True,
                "legal_query_can_read_all_target_components": True,
                "graph_cache_transition_table_recovers_target_exactly": True,
            },
        ),
        _sketch(
            "context_id_lookup_surface",
            "Target is keyed by public context id.",
            "Public context_id is visible before any query.",
            2,
            "Oracle maps public context_id to target.",
            "context lookup table",
            _risk("fatal", "context_id is an answer-bearing alias."),
            _risk("fatal", "Lookup by context_id is exact."),
            _risk("fatal", "Passive decoder can read context_id."),
            _risk("low", "Metric can be balanced but target is leaked."),
            base_replay,
            base_leakage,
            "Reject if visible fields leak target.",
            {"visible_fields_leak_target": True, "graph_cache_transition_table_recovers_target_exactly": True},
        ),
        _sketch(
            "tiny_fsm_trap",
            "Target depends on one of eight finite machine states.",
            base_visible_boundary,
            3,
            "Oracle identifies the finite state and maps to target.",
            "fsm_planner",
            _risk("high", "Finite states are small enough for exact induction."),
            _risk("fatal", "FSM planner saturates the surface."),
            _risk("medium", "Passive sequence id may correlate."),
            _risk("low", "Metric is not inherently degenerate."),
            base_replay,
            base_leakage,
            "Reject if state space is small enough for trivial lookup saturation.",
            {
                "graph_cache_transition_table_recovers_target_exactly": True,
                "state_space_small_enough_for_trivial_lookup_saturation": True,
            },
        ),
        _sketch(
            "answer_key_oracle_surface",
            "Target is defined by an answer-key table outside the legal channel.",
            base_visible_boundary,
            2,
            "Oracle reads answer_key to score the target.",
            "answer-key diagnostic oracle",
            _risk("fatal", "Oracle requires answer_key."),
            _risk("unknown", "Graph cache not needed because oracle is invalid."),
            _risk("unknown", "Passive risk not reached."),
            _risk("unknown", "Metric not reached."),
            base_replay,
            base_leakage,
            "Reject if oracle needs hidden_state, answer_key, or future labels.",
            {"oracle_needs_hidden_state_answer_key_or_future_labels": True},
        ),
        _sketch(
            "passive_color_code",
            "Target is encoded in a visible color bucket.",
            "color_bucket is visible passively and maps one-to-one to target.",
            1,
            "Oracle reads color_bucket.",
            "passive decoder",
            _risk("fatal", "Visible color is a benign-named answer alias."),
            _risk("high", "Lookup also works."),
            _risk("fatal", "Passive decoder reaches oracle."),
            _risk("low", "Balanced labels possible."),
            base_replay,
            base_leakage,
            "Reject if passive decoder likely reaches oracle.",
            {"visible_fields_leak_target": True, "passive_decoder_likely_reaches_oracle": True},
        ),
        _sketch(
            "graph_cache_transition_grid",
            "Target is the next node in a finite public transition grid.",
            base_visible_boundary,
            2,
            "Oracle follows public transition edge.",
            "transition_table",
            _risk("high", "Edge readout is nearly direct."),
            _risk("fatal", "Transition table recovers target exactly."),
            _risk("medium", "Passive start node is informative."),
            _risk("low", "Metric not degenerate."),
            base_replay,
            base_leakage,
            "Reject if graph-cache or transition table recovers target exactly.",
            {"graph_cache_transition_table_recovers_target_exactly": True},
        ),
        _sketch(
            "rare_positive_metric_trap",
            "Target is a rare positive event under a mostly negative stream.",
            base_visible_boundary,
            2,
            "Oracle detects rare event.",
            "predict_none",
            _risk("low", "No direct answer field."),
            _risk("medium", "Lookup may recover rare cases."),
            _risk("medium", "Passive base rate dominates."),
            _risk("fatal", "Accuracy-like metric would be degenerate under rare positives."),
            base_replay,
            base_leakage,
            "Reject if metric is degenerate.",
            {"metric_degenerate": True},
        ),
        _sketch(
            "future_label_dependency",
            "Target depends on the future episode label after an intervention.",
            base_visible_boundary,
            2,
            "Oracle reads future label after the decision point.",
            "future-label oracle",
            _risk("fatal", "Future label is answer-bearing."),
            _risk("unknown", "Invalid oracle blocks first."),
            _risk("unknown", "Invalid oracle blocks first."),
            _risk("unknown", "Invalid oracle blocks first."),
            base_replay,
            base_leakage,
            "Reject if oracle needs future labels.",
            {"oracle_needs_hidden_state_answer_key_or_future_labels": True},
        ),
        _sketch(
            "all_components_readable_budget",
            "Target is a four-factor relation and budget permits four legal reads.",
            base_visible_boundary,
            4,
            "Oracle reads the four factors and computes the relation.",
            "budget_limited_belief_state_planner",
            _risk("fatal", "Budget equals target-component count."),
            _risk("fatal", "Graph/cache over the four reads is exact."),
            _risk("low", "Passive channel is not enough."),
            _risk("low", "Balanced labels possible."),
            base_replay,
            base_leakage,
            "Reject if legal query can read all target components.",
            {
                "target_deterministic_from_le_budget_visible_channels": True,
                "legal_query_can_read_all_target_components": True,
                "graph_cache_transition_table_recovers_target_exactly": True,
            },
        ),
        _sketch(
            "train_context_memorization",
            "Target is keyed by a repeating train/test context.",
            base_visible_boundary,
            1,
            "Oracle maps context to target.",
            "graph_lookup",
            _risk("fatal", "Context key is a direct lookup handle."),
            _risk("fatal", "Train/test key reuse saturates lookup."),
            _risk("high", "Context key may be passive."),
            _risk("low", "Metric can be balanced."),
            base_replay,
            base_leakage,
            "Reject if state space is small enough for lookup saturation.",
            {"state_space_small_enough_for_trivial_lookup_saturation": True, "visible_fields_leak_target": True},
        ),
        _sketch(
            "filename_label_alias",
            "Target appears as a benign filename suffix.",
            "Visible file handle contains benign suffix encoding target.",
            1,
            "Oracle parses file handle.",
            "passive decoder",
            _risk("fatal", "Filename suffix leaks target."),
            _risk("high", "Lookup can memorize suffix."),
            _risk("fatal", "Passive decoder reaches oracle."),
            _risk("low", "Metric can be balanced."),
            base_replay,
            base_leakage,
            "Reject if visible fields leak target.",
            {"visible_fields_leak_target": True, "passive_decoder_likely_reaches_oracle": True},
        ),
        _sketch(
            "single_probe_xor",
            "Target is determined by one public XOR bit and a public class map.",
            base_visible_boundary,
            1,
            "Oracle reads one XOR bit and class map.",
            "greedy_information_gain_or_uncertainty_planner_under_budget",
            _risk("fatal", "One legal query determines target."),
            _risk("fatal", "Transition table is exact."),
            _risk("medium", "Passive class map is informative."),
            _risk("low", "Balanced labels possible."),
            base_replay,
            base_leakage,
            "Reject if target is deterministic from <= budget visible channels.",
            {
                "target_deterministic_from_le_budget_visible_channels": True,
                "legal_query_can_read_all_target_components": True,
            },
        ),
        _sketch(
            "adaptive_pointer_noise_probe",
            "Target is estimated from a budgeted pointer-followed intervention cue with residual noise.",
            base_visible_boundary,
            2,
            "Oracle queries selector, then the selected noisy intervention cue; it never reads target, hidden_state, answer_key, or future labels.",
            "budget_limited_belief_state_planner",
            _risk("low", "No fixed legal channel is exact; selected cue is noisy and pointer-dependent."),
            _risk("medium", "Exact graph lookup should fail on held-out signatures if split is respected."),
            _risk("low", "Passive fields are independent coarse buckets."),
            _risk("low", "Balanced macro-F1 over three labels."),
            base_replay,
            base_leakage,
            "Reject if fixed-channel baselines enter oracle equivalence band.",
            no_flags,
            probe_kind="adaptive_pointer_noise",
        ),
        _sketch(
            "relational_contrast_budget_probe",
            "Target is estimated from a noisy relation among legal contrast probes under a limited budget.",
            base_visible_boundary,
            3,
            "Oracle queries contrast_a, contrast_b, and phase_probe; residual environment noise prevents direct deterministic decode.",
            "greedy_information_gain_or_uncertainty_planner_under_budget",
            _risk("low", "The queried relation is predictive but not exact."),
            _risk("medium", "Graph-cache should miss held-out legal tuples."),
            _risk("low", "Passive fields carry only coarse size and bucket information."),
            _risk("low", "Balanced macro-F1 over three labels."),
            base_replay,
            base_leakage,
            "Reject if cheap fixed baselines close the preliminary oracle gap.",
            no_flags,
            probe_kind="relational_contrast_budget",
        ),
        _sketch(
            "passive_alias_probe",
            "Target is estimated from legal cue, but passive alias may leak the same target.",
            base_visible_boundary,
            2,
            "Oracle queries a legal noisy cue and budget echo.",
            "passive decoder",
            _risk("medium", "Legal cue is noisy, not exact."),
            _risk("medium", "Graph-cache risk unresolved until split probe."),
            _risk("medium", "Passive alias risk intentionally left for micro-probe."),
            _risk("low", "Balanced macro-F1 over three labels."),
            base_replay,
            base_leakage,
            "Reject if passive decoder reaches oracle in micro-probe.",
            no_flags,
            probe_kind="passive_alias",
        ),
        _sketch(
            "pairwise_graph_collision_probe",
            "Target is estimated from pairwise legal signatures with possible train/test collision.",
            base_visible_boundary,
            2,
            "Oracle queries node_probe and edge_probe within budget.",
            "graph_lookup",
            _risk("medium", "No answer-key field, but pair signature may be too stable."),
            _risk("medium", "Graph-cache risk intentionally left for micro-probe."),
            _risk("low", "Passive fields are coarse and non-answer."),
            _risk("low", "Balanced macro-F1 over three labels."),
            base_replay,
            base_leakage,
            "Reject if graph-cache saturates in micro-probe.",
            no_flags,
            probe_kind="pairwise_graph_collision",
        ),
    ]


def run_static_kill_scan(sketches: list[dict[str, Any]]) -> dict[str, Any]:
    results = []
    for sketch in sketches:
        flags = sketch.get("static_kill_flags", {})
        kill_reasons = [criterion for criterion in STATIC_KILL_CRITERIA if flags.get(criterion)]
        results.append(
            {
                "sketch_id": sketch["sketch_id"],
                "static_verdict": "rejected_static_kill" if kill_reasons else "survived_static_kill",
                "kill_reasons": kill_reasons,
                "legal_query_budget": sketch["legal_query_budget"],
                "expected_strongest_cheap_baseline": sketch["expected_strongest_cheap_baseline"],
                "claim_ceiling": sketch["claim_ceiling"],
                "candidate_implementation_authorized": False,
                "route_tournament_authorized": False,
            }
        )
    survivors = [row["sketch_id"] for row in results if row["static_verdict"] == "survived_static_kill"]
    return {
        "schema_version": "batch_env_headroom_scout_002a_static_kill_scan_v1",
        "task_id": TASK_ID,
        "stage": "stage_1_static_kill_scan",
        "criteria": list(STATIC_KILL_CRITERIA),
        "results": results,
        "survivors": survivors,
        "survivor_count": len(survivors),
        "rejected_count": len(results) - len(survivors),
        "claim_ceiling": CLAIM_CEILING,
        "mainline_integration_status": MAINLINE_STATUS,
        "enabled_status": ENABLED_STATUS,
    }


def _label(index: int) -> str:
    return LABELS[index % len(LABELS)]


def _wrong_label(index: int, rng: random.Random) -> str:
    choices = [label for label in LABELS if label != _label(index)]
    return choices[rng.randrange(len(choices))]


def _episode(
    sketch_id: str,
    split: str,
    index: int,
    target: str,
    legal: dict[str, int | str],
    passive: dict[str, int | str],
    budget: int,
) -> dict[str, Any]:
    return {
        "episode_id": f"{sketch_id}-{split}-{index:03d}",
        "split": split,
        "context_id": f"{split}-ctx-{index:03d}",
        "target": target,
        "legal_channels": legal,
        "passive_visible": passive,
        "legal_query_budget": budget,
        "hidden_state": "diagnostic_only_not_used_by_oracle_or_baselines",
    }


def _generate_adaptive_pointer(sketch: dict[str, Any], split: str, count: int) -> list[dict[str, Any]]:
    rng = random.Random(_stable_seed(sketch["sketch_id"], split))
    episodes = []
    for index in range(count):
        selector = rng.randrange(3)
        target_index = (rng.randrange(3) + index + (0 if split == "train" else 1)) % 3
        signals = [rng.randrange(3) for _ in range(3)]
        signals[selector] = target_index if rng.random() < 0.90 else LABELS.index(_wrong_label(target_index, rng))
        legal = {
            "selector": selector,
            "signal_0": signals[0],
            "signal_1": signals[1],
            "signal_2": signals[2],
            "distractor_a": rng.randrange(7),
            "distractor_b": rng.randrange(11),
        }
        passive = {"size_bin": index % 5, "coarse_bucket": rng.randrange(4), "public_marker": (index * 7) % 13}
        episodes.append(_episode(sketch["sketch_id"], split, index, _label(target_index), legal, passive, sketch["legal_query_budget"]))
    return episodes


def _generate_relational_contrast(sketch: dict[str, Any], split: str, count: int) -> list[dict[str, Any]]:
    rng = random.Random(_stable_seed(sketch["sketch_id"], split))
    episodes = []
    offset = 17 if split == "test" else 0
    for index in range(count):
        contrast_a = (index * 5 + offset + rng.randrange(4)) % 17
        contrast_b = (index * 7 + offset + rng.randrange(5)) % 19
        phase = (index + rng.randrange(6)) % 5
        oracle_index = (contrast_a + 2 * contrast_b + phase) % 3
        target_index = oracle_index if rng.random() < 0.86 else LABELS.index(_wrong_label(oracle_index, rng))
        legal = {
            "contrast_a": contrast_a,
            "contrast_b": contrast_b,
            "phase_probe": phase,
            "contrast_decoy": (contrast_a * contrast_b + index) % 23,
            "drift_probe": rng.randrange(29),
        }
        passive = {"size_bin": (index + offset) % 6, "coarse_bucket": rng.randrange(5), "public_marker": rng.randrange(17)}
        episodes.append(_episode(sketch["sketch_id"], split, index, _label(target_index), legal, passive, sketch["legal_query_budget"]))
    return episodes


def _generate_passive_alias(sketch: dict[str, Any], split: str, count: int) -> list[dict[str, Any]]:
    rng = random.Random(_stable_seed(sketch["sketch_id"], split))
    episodes = []
    split_offset = 1000 if split == "test" else 0
    for index in range(count):
        target_index = (rng.randrange(3) + index) % 3
        legal_signal = target_index if rng.random() < 0.88 else LABELS.index(_wrong_label(target_index, rng))
        passive_alias = target_index if rng.random() < 0.96 else LABELS.index(_wrong_label(target_index, rng))
        legal = {"legal_noisy_cue": legal_signal, "budget_echo": index % 2, "decoy": split_offset + index}
        passive = {"size_bin": index % 4, "public_alias": passive_alias, "coarse_bucket": rng.randrange(3)}
        episodes.append(_episode(sketch["sketch_id"], split, index, _label(target_index), legal, passive, sketch["legal_query_budget"]))
    return episodes


def _generate_graph_collision(sketch: dict[str, Any], split: str, count: int) -> list[dict[str, Any]]:
    rng = random.Random(_stable_seed(sketch["sketch_id"], split))
    patterns = [(node, edge) for node in range(6) for edge in range(3)]
    episodes = []
    for index in range(count):
        node, edge = patterns[index % len(patterns)]
        target_index = (node + 2 * edge) % 3
        legal = {"node_probe": node, "edge_probe": edge, "collision_decoy": rng.randrange(5)}
        passive = {"size_bin": index % 6, "coarse_bucket": rng.randrange(5), "public_marker": rng.randrange(13)}
        episodes.append(_episode(sketch["sketch_id"], split, index, _label(target_index), legal, passive, sketch["legal_query_budget"]))
    return episodes


PROBE_GENERATORS: dict[str, Callable[[dict[str, Any], str, int], list[dict[str, Any]]]] = {
    "adaptive_pointer_noise": _generate_adaptive_pointer,
    "relational_contrast_budget": _generate_relational_contrast,
    "passive_alias": _generate_passive_alias,
    "pairwise_graph_collision": _generate_graph_collision,
}


def generate_micro_probe_episodes(sketch: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    probe_kind = sketch.get("probe_kind")
    if probe_kind not in PROBE_GENERATORS:
        raise ValueError(f"sketch {sketch['sketch_id']} is not configured for micro-probe")
    generator = PROBE_GENERATORS[probe_kind]
    return {
        "train": generator(sketch, "train", TRAIN_COUNT),
        "test": generator(sketch, "test", TEST_COUNT),
    }


def _macro_f1(truth: list[str], pred: list[str]) -> float:
    per_label = []
    for label in LABELS:
        tp = sum(1 for t, p in zip(truth, pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(truth, pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(truth, pred) if t == label and p != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        per_label.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(per_label) / len(per_label)


def _score(test: list[dict[str, Any]], predictions: list[str]) -> float:
    return _macro_f1([episode["target"] for episode in test], predictions)


def _majority_label(episodes: list[dict[str, Any]]) -> str:
    return Counter(episode["target"] for episode in episodes).most_common(1)[0][0]


def _fit_lookup(train: list[dict[str, Any]], extractor: Callable[[dict[str, Any]], tuple[Any, ...]]) -> dict[tuple[Any, ...], str]:
    buckets: dict[tuple[Any, ...], Counter] = {}
    for episode in train:
        buckets.setdefault(extractor(episode), Counter())[episode["target"]] += 1
    return {key: counter.most_common(1)[0][0] for key, counter in buckets.items()}


def _predict_lookup(
    train: list[dict[str, Any]],
    test: list[dict[str, Any]],
    extractor: Callable[[dict[str, Any]], tuple[Any, ...]],
) -> list[str]:
    lookup = _fit_lookup(train, extractor)
    fallback = _majority_label(train)
    return [lookup.get(extractor(episode), fallback) for episode in test]


def _legal_keys(episodes: list[dict[str, Any]]) -> list[str]:
    return sorted(episodes[0]["legal_channels"])


def _passive_keys(episodes: list[dict[str, Any]]) -> list[str]:
    return sorted(episodes[0]["passive_visible"])


def _extract_legal(keys: list[str]) -> Callable[[dict[str, Any]], tuple[Any, ...]]:
    return lambda episode: tuple(episode["legal_channels"].get(key) for key in keys)


def _extract_passive(keys: list[str]) -> Callable[[dict[str, Any]], tuple[Any, ...]]:
    return lambda episode: tuple(episode["passive_visible"].get(key) for key in keys)


def visible_channel_oracle(sketch: dict[str, Any], test: list[dict[str, Any]]) -> dict[str, Any]:
    predictions = []
    traces = []
    for episode in test:
        legal = episode["legal_channels"]
        if sketch["probe_kind"] == "adaptive_pointer_noise":
            selector = int(legal["selector"])
            queried = ["selector", f"signal_{selector}"]
            prediction = _label(int(legal[f"signal_{selector}"]))
        elif sketch["probe_kind"] == "relational_contrast_budget":
            queried = ["contrast_a", "contrast_b", "phase_probe"]
            prediction = _label((int(legal["contrast_a"]) + 2 * int(legal["contrast_b"]) + int(legal["phase_probe"])) % 3)
        elif sketch["probe_kind"] == "passive_alias":
            queried = ["legal_noisy_cue", "budget_echo"]
            prediction = _label(int(legal["legal_noisy_cue"]))
        elif sketch["probe_kind"] == "pairwise_graph_collision":
            queried = ["node_probe", "edge_probe"]
            prediction = _label((int(legal["node_probe"]) + 2 * int(legal["edge_probe"])) % 3)
        else:
            raise ValueError(sketch["probe_kind"])
        predictions.append(prediction)
        traces.append(
            {
                "episode_id": episode["episode_id"],
                "queried_channels": queried,
                "query_count": len(queried),
                "budget": sketch["legal_query_budget"],
                "budget_faithful": len(queried) <= int(sketch["legal_query_budget"])
                and all(channel in legal for channel in queried),
                "hidden_state_accessed": False,
                "answer_key_accessed": False,
                "future_label_accessed": False,
            }
        )
    return {
        "producer_function": "batch_env_headroom_scout_002a.visible_channel_oracle",
        "code_path_hash": code_path_hash(visible_channel_oracle),
        "predictions": predictions,
        "trace": traces,
        "score": _score(test, predictions),
        "budget_faithful": all(row["budget_faithful"] for row in traces),
        "inputs": ["legal_channels", "legal_query_budget"],
    }


def _best_single_or_tuple_keys(train: list[dict[str, Any]], key_budget: int, max_tuple_size: int = 2) -> list[str]:
    keys = _legal_keys(train)
    candidates: list[tuple[float, tuple[str, ...]]] = []
    for size in range(1, min(max_tuple_size, key_budget, len(keys)) + 1):
        for combo in combinations(keys, size):
            preds = _predict_lookup(train, train, _extract_legal(list(combo)))
            candidates.append((_score(train, preds), combo))
    candidates.sort(key=lambda item: (item[0], -len(item[1])), reverse=True)
    selected: list[str] = []
    for _score_value, combo in candidates:
        for key in combo:
            if key not in selected and len(selected) < key_budget:
                selected.append(key)
        if len(selected) >= key_budget:
            break
    return selected or keys[:key_budget]


def budget_limited_belief_state_planner(train: list[dict[str, Any]], test: list[dict[str, Any]], budget: int) -> list[str]:
    keys = _best_single_or_tuple_keys(train, budget, max_tuple_size=2)
    return _predict_lookup(train, test, _extract_legal(keys))


def greedy_information_gain_or_uncertainty_planner_under_budget(
    train: list[dict[str, Any]], test: list[dict[str, Any]], budget: int
) -> list[str]:
    remaining = _legal_keys(train)
    selected: list[str] = []
    for _step in range(min(budget, len(remaining))):
        scored = []
        for key in remaining:
            combo = selected + [key]
            preds = _predict_lookup(train, train, _extract_legal(combo))
            scored.append((_score(train, preds), key))
        scored.sort(reverse=True)
        best_key = scored[0][1]
        selected.append(best_key)
        remaining.remove(best_key)
    return _predict_lookup(train, test, _extract_legal(selected))


def graph_lookup(train: list[dict[str, Any]], test: list[dict[str, Any]], _budget: int) -> list[str]:
    return _predict_lookup(train, test, _extract_legal(_legal_keys(train)))


def transition_table(train: list[dict[str, Any]], test: list[dict[str, Any]], budget: int) -> list[str]:
    keys = _legal_keys(train)[: min(2, budget)]
    return _predict_lookup(train, test, _extract_legal(keys))


def successor_map(train: list[dict[str, Any]], test: list[dict[str, Any]], budget: int) -> list[str]:
    keys = _legal_keys(train)
    selected = keys[1 : 1 + min(2, budget)] if len(keys) > 1 else keys[:1]
    return _predict_lookup(train, test, _extract_legal(selected))


def fsm_planner(train: list[dict[str, Any]], test: list[dict[str, Any]], budget: int) -> list[str]:
    keys = _legal_keys(train)[: max(1, min(2, budget))]

    def extractor(episode: dict[str, Any]) -> tuple[Any, ...]:
        values = []
        for key in keys:
            value = episode["legal_channels"].get(key)
            values.append(int(value) % 2 if isinstance(value, int) else value)
        return tuple(values)

    return _predict_lookup(train, test, extractor)


def passive_decoder(train: list[dict[str, Any]], test: list[dict[str, Any]], _budget: int) -> list[str]:
    return _predict_lookup(train, test, _extract_passive(_passive_keys(train)))


def size_only(train: list[dict[str, Any]], test: list[dict[str, Any]], _budget: int) -> list[str]:
    return _predict_lookup(train, test, lambda episode: (episode["passive_visible"].get("size_bin"),))


def degenerate_controls(train: list[dict[str, Any]], test: list[dict[str, Any]], _budget: int) -> list[str]:
    label = _majority_label(train)
    return [label for _episode in test]


BASELINE_FUNCTIONS: dict[str, Callable[[list[dict[str, Any]], list[dict[str, Any]], int], list[str]]] = {
    "budget_limited_belief_state_planner": budget_limited_belief_state_planner,
    "greedy_information_gain_or_uncertainty_planner_under_budget": greedy_information_gain_or_uncertainty_planner_under_budget,
    "graph_lookup": graph_lookup,
    "transition_table": transition_table,
    "successor_map": successor_map,
    "fsm_planner": fsm_planner,
    "passive_decoder": passive_decoder,
    "size_only": size_only,
    "degenerate_controls": degenerate_controls,
}


def _baseline_family(baseline_id: str) -> str:
    if baseline_id in {"graph_lookup", "transition_table", "successor_map", "fsm_planner"}:
        return "graph_cache_lookup"
    if baseline_id == "passive_decoder":
        return "passive"
    if baseline_id == "size_only":
        return "size_only"
    if baseline_id == "degenerate_controls":
        return "degenerate"
    return "budgeted_active_query"


def _run_baselines(sketch: dict[str, Any], train: list[dict[str, Any]], test: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    budget = int(sketch["legal_query_budget"])
    for baseline_id, func in BASELINE_FUNCTIONS.items():
        predictions = func(train, test, budget)
        rows.append(
            {
                "baseline_id": baseline_id,
                "baseline_family": _baseline_family(baseline_id),
                "score": _score(test, predictions),
                "producer_function": f"batch_env_headroom_scout_002a.{func.__name__}",
                "code_path_hash": code_path_hash(func),
                "input_boundary": "train legal/passive visible channels and heldout legal/passive visible channels only",
                "candidate_free": True,
                "consumed_by_micro_probe_verdict": True,
            }
        )
    return rows


def _detect_direct_decode(train: list[dict[str, Any]], test: list[dict[str, Any]]) -> dict[str, Any]:
    direct_rows = []
    for key in _legal_keys(train):
        preds = _predict_lookup(train, test, _extract_legal([key]))
        score = _score(test, preds)
        direct_rows.append({"channel": key, "score": score})
    best = max(direct_rows, key=lambda row: row["score"])
    suspicious_names = [
        row for row in direct_rows if any(token in row["channel"].lower() for token in ("target", "answer", "label", "oracle"))
    ]
    return {
        "producer_function": "batch_env_headroom_scout_002a._detect_direct_decode",
        "code_path_hash": code_path_hash(_detect_direct_decode),
        "direct_decode_detected": best["score"] >= 0.98 or bool(suspicious_names),
        "best_single_channel": best,
        "suspicious_channel_names": suspicious_names,
    }


def _split_resists_memorization(train: list[dict[str, Any]], test: list[dict[str, Any]]) -> dict[str, Any]:
    legal_keys = _legal_keys(train)
    train_signatures = {tuple(episode["legal_channels"][key] for key in legal_keys) for episode in train}
    test_signatures = {tuple(episode["legal_channels"][key] for key in legal_keys) for episode in test}
    overlap = train_signatures & test_signatures
    return {
        "producer_function": "batch_env_headroom_scout_002a._split_resists_memorization",
        "code_path_hash": code_path_hash(_split_resists_memorization),
        "train_signature_count": len(train_signatures),
        "test_signature_count": len(test_signatures),
        "overlap_count": len(overlap),
        "resists_memorization": len(overlap) == 0,
    }


def _micro_probe_verdict(
    oracle: dict[str, Any],
    baseline_rows: list[dict[str, Any]],
    direct_decode: dict[str, Any],
    split_report: dict[str, Any],
) -> tuple[str, str]:
    by_id = {row["baseline_id"]: row for row in baseline_rows}
    oracle_score = float(oracle["score"])
    graph_max = max(row["score"] for row in baseline_rows if row["baseline_family"] == "graph_cache_lookup")
    passive_score = float(by_id["passive_decoder"]["score"])
    size_score = float(by_id["size_only"]["score"])
    degenerate_score = float(by_id["degenerate_controls"]["score"])
    strongest_cheap = max(
        row["score"]
        for row in baseline_rows
        if row["baseline_family"] not in {"passive", "size_only", "degenerate"}
    )
    if not oracle["budget_faithful"]:
        return "blocked_oracle_not_budget_faithful", "visible_channel_oracle exceeded budget or used unavailable channel"
    if direct_decode["direct_decode_detected"]:
        return "reject_direct_decode", "single legal channel or answer-bearing name directly decodes target"
    if graph_max >= oracle_score - EQUIVALENCE_BAND or not split_report["resists_memorization"]:
        return "reject_graph_cache_saturated", "graph/cache family entered oracle equivalence band or train/test signature overlap exists"
    if passive_score >= min(0.80, oracle_score - EQUIVALENCE_BAND):
        return "reject_passive_decodable", "passive decoder reached oracle-equivalent or high standalone score"
    if degenerate_score >= 0.75 or size_score >= 0.75:
        return "reject_metric_degenerate", "degenerate or size-only control crossed scouting ceiling"
    if oracle_score < ORACLE_FLOOR or oracle_score - strongest_cheap < PROMOTION_GAP:
        return "reject_no_headroom_likely", "preliminary oracle is too low or strongest cheap baseline gap is below promotion floor"
    return "promote_to_full_harness_candidate", "candidate-free micro-probe gap warrants a separate full baseline-first harness task card"


def run_micro_probe_for_sketch(sketch: dict[str, Any], run_id: str) -> dict[str, Any]:
    episodes = generate_micro_probe_episodes(sketch)
    train = episodes["train"]
    test = episodes["test"]
    oracle = visible_channel_oracle(sketch, test)
    baseline_rows = _run_baselines(sketch, train, test)
    direct_decode = _detect_direct_decode(train, test)
    split_report = _split_resists_memorization(train, test)
    verdict, reason = _micro_probe_verdict(oracle, baseline_rows, direct_decode, split_report)
    strongest_cheap = max(
        (row for row in baseline_rows if row["baseline_family"] not in {"passive", "size_only", "degenerate"}),
        key=lambda row: row["score"],
    )
    graph_max = max(row["score"] for row in baseline_rows if row["baseline_family"] == "graph_cache_lookup")
    passive_score = next(row["score"] for row in baseline_rows if row["baseline_id"] == "passive_decoder")
    size_score = next(row["score"] for row in baseline_rows if row["baseline_id"] == "size_only")
    degenerate_score = next(row["score"] for row in baseline_rows if row["baseline_id"] == "degenerate_controls")
    return {
        "schema_version": "batch_env_headroom_scout_002a_micro_probe_result_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "sketch_id": sketch["sketch_id"],
        "micro_probe_verdict": verdict,
        "allowed_verdict": verdict in ALLOWED_MICRO_PROBE_VERDICTS,
        "verdict_reason": reason,
        "oracle_score": oracle["score"],
        "oracle_budget_faithful": oracle["budget_faithful"],
        "strongest_cheap_baseline": strongest_cheap["baseline_id"],
        "strongest_cheap_baseline_score": strongest_cheap["score"],
        "preliminary_gap": oracle["score"] - strongest_cheap["score"],
        "graph_cache_lookup_max_score": graph_max,
        "passive_decoder_score": passive_score,
        "size_only_score": size_score,
        "degenerate_control_score": degenerate_score,
        "train_test_split_resists_memorization": split_report["resists_memorization"],
        "direct_decode": direct_decode,
        "split_report": split_report,
        "baseline_results": baseline_rows,
        "oracle_trace_sample": oracle["trace"][:5],
        "producer_function": "batch_env_headroom_scout_002a.run_micro_probe_for_sketch",
        "code_path_hash": code_path_hash(run_micro_probe_for_sketch),
        "claim_ceiling": CLAIM_CEILING,
    }


def run_micro_probes(sketches: list[dict[str, Any]], static_scan: dict[str, Any], run_id: str) -> dict[str, Any]:
    sketch_by_id = {sketch["sketch_id"]: sketch for sketch in sketches}
    results = [run_micro_probe_for_sketch(sketch_by_id[sketch_id], run_id) for sketch_id in static_scan["survivors"]]
    return {
        "schema_version": "batch_env_headroom_scout_002a_micro_probe_results_v1",
        "task_id": TASK_ID,
        "stage": "stage_2_micro_probe_only_for_survivors",
        "run_id": run_id,
        "allowed_verdicts": sorted(ALLOWED_MICRO_PROBE_VERDICTS),
        "results": results,
        "probed_sketch_ids": [row["sketch_id"] for row in results],
        "not_probed_static_rejections": [
            row["sketch_id"] for row in static_scan["results"] if row["static_verdict"] == "rejected_static_kill"
        ],
        "claim_ceiling": CLAIM_CEILING,
    }


def _task_card_for_promoted(row: dict[str, Any], sketch: dict[str, Any]) -> dict[str, Any]:
    card_id = f"{TASK_ID}-FULL-HARNESS-CARD-{sketch['sketch_id'].upper().replace('-', '_')}"
    baseline_requirements = [
        "budget_limited_belief_state_planner",
        "greedy_information_gain_or_uncertainty_planner_under_budget",
        "graph_lookup",
        "transition_table",
        "successor_map",
        "fsm_planner",
        "passive decoder",
        "size-only",
        "degenerate controls",
    ]
    return {
        "task_id": card_id,
        "problem_definition": (
            f"Build a full candidate-free baseline-first harness for promoted sketch `{sketch['sketch_id']}` "
            "to test whether the preliminary micro-probe gap survives stronger callable baselines and controls."
        ),
        "current_stage": "candidate-free full baseline-first harness task card draft only",
        "current_layer": CURRENT_LAYER,
        "mainline_target": "none",
        "enabled_state_requirement": ENABLED_STATUS,
        "real_trigger_evidence_requirement": "Run the full harness from generated episodes and write machine-readable baseline/oracle/control artifacts.",
        "hypothesis": "The environment surface may retain measurable oracle-vs-cheap-baseline separation under a full baseline battery.",
        "strongest_baseline": row["strongest_cheap_baseline"],
        "baseline_requirements": baseline_requirements,
        "ablation_requirement": "Rerun the full harness with oracle query budget reduced, adaptive query disabled, passive-only view, graph-cache-only view, and leakage-positive controls.",
        "trace_replay_requirement": "Replay must recompute predictions from serialized visible state plus legal query trace; stored prediction or hash-only replay must fail.",
        "computed_evidence_provenance_gate": (
            "Every score must record producer_function, input artifacts, run_id, seed/context/episode IDs, aggregation rule, and code path hash."
        ),
        "acceptance_gate": (
            "Only candidate-free full-harness candidate promotion if oracle is high, strongest cheap baseline remains at least 0.08 below oracle, "
            "passive/degenerate/size-only remain low, graph-cache does not saturate, oracle is budget-faithful, and train/test split resists memorization."
        ),
        "claim_ceiling": (
            "No headroom confirmation from this task card. Candidate-free full baseline-first harness candidate only. "
            "No candidate authorization, no route tournament, no Gate1 pass, no mechanism validity, no runtime/mainline effect."
        ),
        "stop_condition": "Stop on direct decode, graph-cache saturation, passive decodability, metric degeneracy, non-budget-faithful oracle, or gap < 0.08.",
        "rollback_plan": "Delete only the new full-harness draft artifacts for this sketch; do not mutate prior negative evidence or MINIMAL-ENV-SPEC-001A.",
        "expected_changed_files": [
            f"scripts/research/{sketch['sketch_id']}_full_baseline_first_harness.py",
            f"tests/research/test_{sketch['sketch_id']}_full_baseline_first_harness.py",
            f"artifacts/{sketch['sketch_id']}_full_baseline_first_harness/",
        ],
        "forbidden_changes": [
            "WM-P / VSB-C / CSL implementation",
            "candidate implementation",
            "route tournament",
            "runtime/mainline/admission/bridge wiring",
            "MINIMAL-ENV-SPEC-001A edits",
            "push/tag/remote-anchor",
        ],
        "auto_remote_anchor": "forbidden",
        "candidate_implementation_authorized": False,
        "route_tournament_authorized": False,
    }


def _task_card_markdown(card: dict[str, Any], source_row: dict[str, Any]) -> str:
    lines = [
        f"# {card['task_id']}",
        "",
        f"Problem definition: {card['problem_definition']}",
        f"Current stage/layer: {card['current_stage']} / {card['current_layer']}",
        f"Mainline target: {card['mainline_target']}",
        f"Enabled-state requirement: {card['enabled_state_requirement']}",
        f"Real-trigger evidence requirement: {card['real_trigger_evidence_requirement']}",
        f"Hypothesis: {card['hypothesis']}",
        f"Strongest baseline: {card['strongest_baseline']}",
        f"Preliminary oracle score: {source_row['oracle_score']}",
        f"Preliminary strongest cheap baseline score: {source_row['strongest_cheap_baseline_score']}",
        f"Preliminary gap: {source_row['preliminary_gap']}",
        "",
        "Baseline requirements:",
    ]
    lines.extend(f"- {baseline}" for baseline in card["baseline_requirements"])
    lines.extend(
        [
            "",
            f"Ablation requirement: {card['ablation_requirement']}",
            f"Trace/replay requirement: {card['trace_replay_requirement']}",
            f"Computed-evidence provenance gate: {card['computed_evidence_provenance_gate']}",
            f"Acceptance gate: {card['acceptance_gate']}",
            f"Claim ceiling: {card['claim_ceiling']}",
            f"Stop condition: {card['stop_condition']}",
            f"Rollback plan: {card['rollback_plan']}",
            "",
            "Expected changed files:",
        ]
    )
    lines.extend(f"- {path}" for path in card["expected_changed_files"])
    lines.extend(["", "Forbidden changes:"])
    lines.extend(f"- {item}" for item in card["forbidden_changes"])
    lines.extend(
        [
            "",
            f"Auto-Remote-Anchor: {card['auto_remote_anchor']}",
            f"Candidate implementation authorized: {card['candidate_implementation_authorized']}",
            f"Route tournament authorized: {card['route_tournament_authorized']}",
            "",
        ]
    )
    return "\n".join(lines)


def promote_full_harness_candidates(
    sketches: list[dict[str, Any]],
    micro_probe_results: dict[str, Any],
    out_dir: Path | None = None,
) -> dict[str, Any]:
    sketch_by_id = {sketch["sketch_id"]: sketch for sketch in sketches}
    eligible = [
        row
        for row in micro_probe_results["results"]
        if row["micro_probe_verdict"] == "promote_to_full_harness_candidate"
        and row["oracle_score"] >= ORACLE_FLOOR
        and row["preliminary_gap"] >= PROMOTION_GAP
        and row["passive_decoder_score"] < 0.80
        and row["size_only_score"] < 0.75
        and row["degenerate_control_score"] < 0.75
        and row["graph_cache_lookup_max_score"] < row["oracle_score"] - EQUIVALENCE_BAND
        and row["oracle_budget_faithful"]
        and row["train_test_split_resists_memorization"]
        and not row["direct_decode"]["direct_decode_detected"]
    ]
    eligible.sort(key=lambda row: (row["preliminary_gap"], row["oracle_score"]), reverse=True)
    promoted = []
    task_cards = []
    task_card_filenames = []
    for row in eligible[:2]:
        promoted_row = {
            "sketch_id": row["sketch_id"],
            "micro_probe_verdict": row["micro_probe_verdict"],
            "oracle_score": row["oracle_score"],
            "strongest_cheap_baseline": row["strongest_cheap_baseline"],
            "strongest_cheap_baseline_score": row["strongest_cheap_baseline_score"],
            "preliminary_gap": row["preliminary_gap"],
            "passive_decoder_score": row["passive_decoder_score"],
            "size_only_score": row["size_only_score"],
            "degenerate_control_score": row["degenerate_control_score"],
            "graph_cache_lookup_max_score": row["graph_cache_lookup_max_score"],
            "oracle_budget_faithful": row["oracle_budget_faithful"],
            "train_test_split_resists_memorization": row["train_test_split_resists_memorization"],
            "candidate_authorized": False,
            "route_tournament_authorized": False,
            "auto_remote_anchor": "forbidden",
            "claim_ceiling": CLAIM_CEILING,
        }
        promoted.append(promoted_row)
        card = _task_card_for_promoted(row, sketch_by_id[row["sketch_id"]])
        task_cards.append(card)
        if out_dir is not None:
            filename = f"full_harness_task_card_{row['sketch_id']}.md"
            (out_dir / filename).write_text(_task_card_markdown(card, row), encoding="utf-8")
            task_card_filenames.append(filename)
    return {
        "schema_version": "batch_env_headroom_scout_002a_promoted_candidates_v1",
        "task_id": TASK_ID,
        "promotion_rule": {
            "max_promoted": 2,
            "oracle_score_min": ORACLE_FLOOR,
            "preliminary_gap_min": PROMOTION_GAP,
            "passive_degenerate_size_only_low_required": True,
            "direct_decode_forbidden": True,
            "graph_cache_saturation_forbidden": True,
            "budget_faithful_oracle_required": True,
            "train_test_split_resists_memorization_required": True,
        },
        "promoted": promoted,
        "full_baseline_first_harness_task_cards": task_cards,
        "task_card_filenames": task_card_filenames,
        "candidate_authorized": False,
        "route_tournament_authorized": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_rejected_sketches(static_scan: dict[str, Any], micro_probe_results: dict[str, Any]) -> dict[str, Any]:
    rejected = []
    for row in static_scan["results"]:
        if row["static_verdict"] == "rejected_static_kill":
            rejected.append(
                {
                    "sketch_id": row["sketch_id"],
                    "rejection_stage": "static_kill_scan",
                    "static_verdict": row["static_verdict"],
                    "kill_reasons": row["kill_reasons"],
                    "candidate_authorized": False,
                    "route_tournament_authorized": False,
                }
            )
    for row in micro_probe_results["results"]:
        if row["micro_probe_verdict"] != "promote_to_full_harness_candidate":
            rejected.append(
                {
                    "sketch_id": row["sketch_id"],
                    "rejection_stage": "micro_probe",
                    "micro_probe_verdict": row["micro_probe_verdict"],
                    "verdict_reason": row["verdict_reason"],
                    "oracle_score": row["oracle_score"],
                    "strongest_cheap_baseline": row["strongest_cheap_baseline"],
                    "strongest_cheap_baseline_score": row["strongest_cheap_baseline_score"],
                    "graph_cache_lookup_max_score": row["graph_cache_lookup_max_score"],
                    "passive_decoder_score": row["passive_decoder_score"],
                    "size_only_score": row["size_only_score"],
                    "degenerate_control_score": row["degenerate_control_score"],
                    "candidate_authorized": False,
                    "route_tournament_authorized": False,
                }
            )
    return {
        "schema_version": "batch_env_headroom_scout_002a_rejected_sketches_v1",
        "task_id": TASK_ID,
        "rejected": rejected,
        "rejected_count": len(rejected),
        "claim_ceiling": CLAIM_CEILING,
    }


def _final_report(
    registry: dict[str, Any],
    static_scan: dict[str, Any],
    micro_probe_results: dict[str, Any],
    promoted: dict[str, Any],
    rejected: dict[str, Any],
) -> str:
    promoted_count = len(promoted["promoted"])
    verdict = (
        f"promoted_{promoted_count}_full_harness_candidates"
        if promoted_count
        else "zero_sketches_survived_to_full_harness_candidate"
    )
    lines = [
        "# BATCH-ENV-HEADROOM-SCOUT-002A Final Report",
        "",
        f"Verdict: `{verdict}`",
        "",
        f"Current layer: {CURRENT_LAYER}",
        f"Mainline integration status: {MAINLINE_STATUS}",
        f"Enabled status: {ENABLED_STATUS}",
        "Real trigger evidence: callable static kill scan over the sketch registry, plus callable micro-probes only for static survivors.",
        f"Claim ceiling: {CLAIM_CEILING}",
        "",
        "Relevant prior negative evidence cited:",
        "- `BASELINE-FIRST-HARNESS-001A-R1` accepted verdict: `rejected_no_headroom_baseline_saturated`.",
        "- Prior measured facts: visible-channel oracle 1.0, strongest fair baseline 1.0, graph-cache family saturated at 1.0.",
        "- Required interpretation: preserve no-headroom negative environment evidence; do not start route tournament or candidate implementation.",
        "",
        "Scout summary:",
        f"- sketches screened: {len(registry['sketches'])}",
        f"- static rejections: {static_scan['rejected_count']}",
        f"- static survivors micro-probed: {len(micro_probe_results['results'])}",
        f"- micro-probe rejections: {sum(1 for row in micro_probe_results['results'] if row['micro_probe_verdict'] != 'promote_to_full_harness_candidate')}",
        f"- promoted full-harness candidates: {promoted_count}",
        "",
        "Promoted candidates:",
    ]
    if promoted["promoted"]:
        for row in promoted["promoted"]:
            lines.append(
                f"- `{row['sketch_id']}`: oracle={row['oracle_score']:.3f}, strongest cheap `{row['strongest_cheap_baseline']}`={row['strongest_cheap_baseline_score']:.3f}, preliminary_gap={row['preliminary_gap']:.3f}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "Rejected sketches:"])
    for row in rejected["rejected"]:
        reason = row.get("micro_probe_verdict") or ",".join(row.get("kill_reasons", []))
        lines.append(f"- `{row['sketch_id']}` via {row['rejection_stage']}: {reason}")
    lines.extend(
        [
            "",
            "Generated artifacts:",
        ]
    )
    lines.extend(f"- `{ARTIFACT_DIR_REL}/{name}`" for name in REQUIRED_ARTIFACT_FILENAMES)
    lines.extend(f"- `{ARTIFACT_DIR_REL}/{name}`" for name in promoted["task_card_filenames"])
    lines.extend(
        [
            "",
            "Baseline results:",
            "- Micro-probe baseline results are in `micro_probe_results.json` for static survivors only.",
            "- Required cheap baselines invoked: budget-limited belief-state planner, greedy information-gain planner, graph_lookup, transition_table, successor_map, fsm_planner, passive decoder, size-only, and degenerate controls.",
            "",
            "Ablation results:",
            "- Formal ablations were not run; this scout only ran static kills and micro-probes.",
            "- Draft full-harness task cards require budget, passive-only, graph-cache-only, and leakage-positive-control ablations before any stronger claim.",
            "",
            "Replay result:",
            "- Full replay was not run. Each sketch declares replay requirements; promoted task cards require recomputation from serialized visible state plus legal query trace.",
            "",
            "Stop conditions triggered:",
            "- Static kill stop conditions and micro-probe rejection verdicts are recorded in `static_kill_scan.json` and `rejected_sketches.json`.",
            "",
            "Next minimal closed-loop action:",
        ]
    )
    if promoted["promoted"]:
        lines.append("- Run one promoted full baseline-first harness task card as a separate candidate-free task. Stop before candidate implementation.")
    else:
        lines.extend(
            [
                "- Design the next batch with larger held-out legal-signature spaces, noisy non-direct budgeted oracle cues, passive fields proven independent of target, and graph-cache collision controls.",
                "- Keep oracle budget below target-component count and require train/test legal-signature disjointness by construction.",
            ]
        )
    lines.extend(
        [
            "",
            "What this does not prove:",
            "- No headroom confirmation.",
            "- No Gate1 pass.",
            "- No mechanism validity.",
            "- No candidate feasibility or candidate authorization.",
            "- No route tournament authorization.",
            "- No runtime/mainline/admission/bridge effect.",
            "- No agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def _registry_payload(sketches: list[dict[str, Any]], run_id: str, repo_root: Path) -> dict[str, Any]:
    return {
        "schema_version": "batch_env_headroom_scout_002a_sketch_registry_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": MAINLINE_STATUS,
        "enabled_status": ENABLED_STATUS,
        "claim_ceiling": CLAIM_CEILING,
        "primary_rule": "parallelize environment screening, not candidate implementation",
        "forbidden": [
            "WM-P",
            "VSB-C",
            "CSL",
            "route tournament",
            "candidate implementation",
            "runtime/mainline/admission/bridge wiring",
            "MINIMAL-ENV-SPEC-001A reopen or optimization",
            "commit/push/tag/remote-anchor",
        ],
        "auto_remote_anchor": "forbidden",
        "repo_readback": {
            "root": str(repo_root),
            "branch": _run_git(repo_root, ["branch", "--show-current"]),
            "head": _run_git(repo_root, ["rev-parse", "HEAD"]),
            "status_short": _run_git(repo_root, ["status", "--short"]),
            "ahead_behind": _run_git(repo_root, ["status", "-sb"]),
        },
        "prior_negative_evidence": {
            "baseline_first_harness_001a_r1": {
                "accepted_verdict": "rejected_no_headroom_baseline_saturated",
                "visible_channel_oracle_score": 1.0,
                "strongest_fair_baseline_score": 1.0,
                "oracle_minus_baseline_margin": 0.0,
                "graph_cache_family_saturated": True,
                "claim_ceiling": "candidate-free Phase-0 environment no-headroom evidence only",
            },
            "minimal_env_spec_001a": {
                "status": "closed_for_candidate_work",
                "next_ordering_constraint": "new bounded environment surface before any candidate or route tournament work",
            },
        },
        "sketch_count": len(sketches),
        "sketches": sketches,
        "producer_function": "batch_env_headroom_scout_002a._registry_payload",
        "code_path_hash": code_path_hash(_registry_payload),
    }


def run_batch_scout(out_dir: str | Path, run_id: str = TASK_ID, repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sketches = build_sketch_registry()
    registry = _registry_payload(sketches, run_id, root)
    static_scan = run_static_kill_scan(sketches)
    micro_probe_results = run_micro_probes(sketches, static_scan, run_id)
    promoted = promote_full_harness_candidates(sketches, micro_probe_results, out_dir=out)
    rejected = build_rejected_sketches(static_scan, micro_probe_results)
    final_report = _final_report(registry, static_scan, micro_probe_results, promoted, rejected)

    write_json(out / "sketch_registry.json", registry)
    write_json(out / "static_kill_scan.json", static_scan)
    write_json(out / "micro_probe_results.json", micro_probe_results)
    write_json(out / "promoted_full_harness_candidates.json", promoted)
    write_json(out / "rejected_sketches.json", rejected)
    (out / "final_report.md").write_text(final_report, encoding="utf-8")

    return {
        "task_id": TASK_ID,
        "run_id": run_id,
        "sketch_registry": registry,
        "static_kill_scan": static_scan,
        "micro_probe_results": micro_probe_results,
        "promoted_full_harness_candidates": promoted,
        "rejected_sketches": rejected,
        "final_report": final_report,
        "promoted_task_card_filenames": promoted["task_card_filenames"],
        "artifact_hashes": {
            path.name: stable_json_hash(json.loads(path.read_text(encoding="utf-8")))
            for path in out.glob("*.json")
        },
        "claim_ceiling": CLAIM_CEILING,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=ARTIFACT_DIR_REL)
    parser.add_argument("--run-id", default=TASK_ID)
    args = parser.parse_args()
    result = run_batch_scout(out_dir=args.out, run_id=args.run_id)
    print(
        json.dumps(
            {
                "task_id": result["task_id"],
                "run_id": result["run_id"],
                "static_survivor_count": result["static_kill_scan"]["survivor_count"],
                "promoted_count": len(result["promoted_full_harness_candidates"]["promoted"]),
                "claim_ceiling": result["claim_ceiling"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
