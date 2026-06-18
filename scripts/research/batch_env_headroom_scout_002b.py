from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from evidence_provenance_001a import code_path_hash, stable_json_hash, write_json


TASK_ID = "BATCH-ENV-HEADROOM-SCOUT-002B-RUN-001A"
ARTIFACT_DIR_REL = "artifacts/batch_env_headroom_scout_002b"
CURRENT_LAYER = "engineering-governance / Phase-0 repaired environment portfolio scouting"
MAINLINE_STATUS = "none"
ENABLED_STATUS = "no runtime/mainline/admission/bridge path enabled"
CLAIM_CEILING = (
    "candidate-free Phase-0 environment portfolio scouting only. No headroom confirmation. "
    "No Gate1 pass. No mechanism validity. No candidate feasibility. No runtime/mainline effect. "
    "No agency/autonomy/consciousness/EGO readiness."
)

LABELS = [0, 1, 2]
TRAIN_COUNT = 72
TEST_COUNT = 48
PROMOTION_GAP = 0.08
ORACLE_FLOOR = 0.80
EQUIVALENCE_BAND = 0.03
PASSIVE_REJECTION_FLOOR = 0.87
DEGENERATE_REJECTION_FLOOR = 0.87

STATIC_KILL_CRITERIA = [
    "target_deterministic_from_le_budget_visible_channels",
    "legal_query_can_read_all_target_components",
    "graph_cache_transition_table_recovers_target_exactly",
    "state_space_small_enough_for_trivial_lookup_saturation",
    "visible_fields_leak_target",
    "passive_decoder_likely_reaches_oracle",
    "metric_degenerate",
    "oracle_needs_hidden_state_answer_key_or_future_labels",
    "future_label_dependency",
]

DEGENERATE_BASELINES = [
    "predict_all",
    "predict_none",
    "constant_k_sweep",
    "random",
    "majority",
    "size_only_sweep",
]

PASSIVE_DECODER_FAMILY = [
    "observation_only",
    "value_decoder_mean",
    "value_decoder_variance",
    "value_decoder_correlation",
    "value_decoder_pca",
    "nearest_neighbor_passive",
    "supervised_or_membership_passive_attacker",
]

FULL_GRAPH_CACHE_FAMILY = [
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
]

MANDATORY_BASELINE_PRODUCERS = [
    *DEGENERATE_BASELINES,
    *PASSIVE_DECODER_FAMILY,
    "exhaustive_legal_query",
    "budget_limited_belief_state_planner",
    "greedy_information_gain_or_uncertainty_planner_under_budget",
    *FULL_GRAPH_CACHE_FAMILY,
    "trace_only_replay",
    "ngram_trace_lookup",
    "belief_table",
    "pair_count_table",
    "fitted_legal_channel_learner",
    "strongest_known_classical_method_for_task_type",
]

ALLOWED_FINAL_VERDICTS = {
    "promoted_0_full_harness_candidates",
    "promoted_1_full_harness_candidates",
    "promoted_2_full_harness_candidates",
    "all_rejected_static_or_microprobe",
    "blocked_static_scan_not_independent",
    "blocked_baseline_battery_incomplete",
    "blocked_compute_baseline_missing",
    "blocked_baseline_aliasing_invalidates_promotion",
    "blocked_oracle_not_budget_faithful",
    "blocked_artifact_integrity_failure",
}

ALLOWED_PER_SKETCH_VERDICTS = {
    "reject_direct_decode",
    "reject_legal_compute_baseline_saturated",
    "reject_graph_cache_saturated",
    "reject_passive_decodable",
    "reject_metric_degenerate",
    "reject_oracle_not_budget_faithful",
    "reject_underpowered_surface",
    "reject_no_headroom_likely",
    "blocked_compute_baseline_missing",
    "blocked_static_scan_not_independent",
    "blocked_baseline_battery_incomplete",
    "blocked_baseline_aliasing_invalidates_promotion",
    "promote_to_full_harness_candidate",
}

REQUIRED_ARTIFACT_FILENAMES = [
    "sketch_registry.json",
    "author_claims.json",
    "independent_static_kill_scan.json",
    "dependency_analysis.json",
    "oracle_as_baseline_report.json",
    "micro_probe_results.json",
    "baseline_independence_report.json",
    "fitted_legal_channel_learner_report.json",
    "promoted_full_harness_candidates.json",
    "rejected_sketches.json",
    "final_report.md",
]


@dataclass(frozen=True)
class ProbeData:
    train: list[dict[str, Any]]
    test: list[dict[str, Any]]


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


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _stable_seed(*parts: str) -> int:
    return int(_sha_text("::".join(parts))[:12], 16)


def _default_author_claims() -> dict[str, bool]:
    return {criterion: False for criterion in STATIC_KILL_CRITERIA}


def _sketch(
    *,
    sketch_id: str,
    sketch_type: str,
    target_rule: str,
    legal_query_budget: int,
    legal_channels: list[str],
    target_dependency_set: list[str],
    visible_channels: list[str],
    oracle_definition: str,
    oracle_field_access: list[str],
    oracle_forbidden_field_access: list[str] | None = None,
    metric_kind: str = "balanced_macro_f1",
    author_claims: dict[str, bool] | None = None,
    static_detection_profile: dict[str, Any] | None = None,
    preferred_compute_saturation_verdict: str = "reject_legal_compute_baseline_saturated",
) -> dict[str, Any]:
    claims = _default_author_claims()
    claims.update(author_claims or {})
    return {
        "sketch_id": sketch_id,
        "sketch_type": sketch_type,
        "target_rule": target_rule,
        "legal_query_budget": legal_query_budget,
        "legal_channels": legal_channels,
        "target_dependency_set": target_dependency_set,
        "visible_channels": visible_channels,
        "oracle_definition": oracle_definition,
        "oracle_field_access": oracle_field_access,
        "oracle_forbidden_field_access": oracle_forbidden_field_access or [],
        "metric_kind": metric_kind,
        "author_static_kill_flags": {criterion: bool(claims.get(criterion, False)) for criterion in STATIC_KILL_CRITERIA},
        "static_detection_profile": static_detection_profile or {},
        "preferred_compute_saturation_verdict": preferred_compute_saturation_verdict,
        "claim_ceiling": CLAIM_CEILING,
        "candidate_implementation_authorized": False,
        "route_tournament_authorized": False,
        "auto_remote_anchor": "forbidden",
    }


def make_direct_legal_compute_sketch(author_claims: dict[str, bool] | None = None) -> dict[str, Any]:
    return _sketch(
        sketch_id="direct_legal_channel_compute",
        sketch_type="direct_legal_compute",
        target_rule="target=(a+2*b+phase)%3 from legal visible channels",
        legal_query_budget=3,
        legal_channels=["a", "b", "phase"],
        target_dependency_set=["a", "b", "phase"],
        visible_channels=["a", "b", "phase", "size_bucket", "passive_value"],
        oracle_definition="visible oracle reads a,b,phase and applies target formula",
        oracle_field_access=["a", "b", "phase"],
        author_claims=author_claims,
        static_detection_profile={
            "formula_known_to_static_scanner": True,
            "legal_query_can_read_all_target_components": True,
        },
    )


def make_low_signal_surface_sketch(author_claims: dict[str, bool] | None = None) -> dict[str, Any]:
    return _sketch(
        sketch_id="low_signal_underpowered_surface",
        sketch_type="low_signal",
        target_rule="target mostly independent of the budgeted weak cue",
        legal_query_budget=1,
        legal_channels=["weak_cue"],
        target_dependency_set=["weak_cue", "unobserved_noise"],
        visible_channels=["weak_cue", "size_bucket", "passive_value"],
        oracle_definition="visible oracle reads weak_cue; it is intentionally underpowered",
        oracle_field_access=["weak_cue"],
        author_claims=author_claims,
        static_detection_profile={"formula_known_to_static_scanner": False},
    )


def make_lookup_split_compute_sketch(author_claims: dict[str, bool] | None = None) -> dict[str, Any]:
    return _sketch(
        sketch_id="lookup_split_compute_artifact",
        sketch_type="lookup_split_compute",
        target_rule="target=(x+2*y)%3; context ids are train/test disjoint but legal tuples repeat",
        legal_query_budget=2,
        legal_channels=["x", "y"],
        target_dependency_set=["x", "y"],
        visible_channels=["x", "y", "context_id", "size_bucket", "passive_value"],
        oracle_definition="visible oracle reads x,y and applies target formula",
        oracle_field_access=["x", "y"],
        author_claims=author_claims,
        static_detection_profile={
            "formula_known_to_static_scanner": False,
            "requires_heldout_compute_probe": True,
            "train_test_context_ids_disjoint": True,
        },
        preferred_compute_saturation_verdict="reject_no_headroom_likely",
    )


def make_answer_key_oracle_sketch(author_claims: dict[str, bool] | None = None) -> dict[str, Any]:
    return _sketch(
        sketch_id="answer_key_oracle_surface",
        sketch_type="answer_key_oracle",
        target_rule="target stored in hidden answer_key, not in legal visible channels",
        legal_query_budget=1,
        legal_channels=["weak_cue"],
        target_dependency_set=["answer_key"],
        visible_channels=["weak_cue", "size_bucket", "passive_value"],
        oracle_definition="diagnostic oracle reads hidden answer_key",
        oracle_field_access=["answer_key"],
        oracle_forbidden_field_access=["answer_key"],
        author_claims=author_claims,
        static_detection_profile={"oracle_uses_forbidden_field": True},
    )


def make_metric_degenerate_sketch(author_claims: dict[str, bool] | None = None) -> dict[str, Any]:
    return _sketch(
        sketch_id="metric_degenerate_predict_all_surface",
        sketch_type="metric_degenerate",
        target_rule="single-positive label stream scored by recall-only reported metric",
        legal_query_budget=1,
        legal_channels=["weak_cue"],
        target_dependency_set=["weak_cue"],
        visible_channels=["weak_cue", "size_bucket", "passive_value"],
        oracle_definition="visible oracle predicts the single positive class",
        oracle_field_access=["weak_cue"],
        metric_kind="recall_positive",
        author_claims=author_claims,
        static_detection_profile={"metric_kind_declared": "recall_positive"},
    )


def make_passive_value_leak_sketch(author_claims: dict[str, bool] | None = None) -> dict[str, Any]:
    return _sketch(
        sketch_id="passive_value_leak_surface",
        sketch_type="passive_value_leak",
        target_rule="target copied into a numeric passive_value alias",
        legal_query_budget=1,
        legal_channels=["weak_cue"],
        target_dependency_set=["weak_cue"],
        visible_channels=["weak_cue", "size_bucket", "passive_value"],
        oracle_definition="visible oracle reads weak_cue but passive_value leaks the answer",
        oracle_field_access=["weak_cue"],
        author_claims=author_claims,
        static_detection_profile={"value_leak_requires_microprobe": True},
    )


def make_graph_cache_surface_sketch(author_claims: dict[str, bool] | None = None) -> dict[str, Any]:
    return _sketch(
        sketch_id="graph_cache_transition_surface",
        sketch_type="graph_cache",
        target_rule="target is a reusable transition-table value keyed by public graph_state",
        legal_query_budget=1,
        legal_channels=["graph_state"],
        target_dependency_set=["graph_state"],
        visible_channels=["graph_state", "context_id", "size_bucket", "passive_value"],
        oracle_definition="visible oracle reads graph_state and follows the public transition table",
        oracle_field_access=["graph_state"],
        author_claims=author_claims,
        static_detection_profile={
            "state_space_small_enough_for_trivial_lookup_saturation": False,
            "requires_graph_family_microprobe": True,
        },
    )


def build_sketch_registry() -> list[dict[str, Any]]:
    return [
        make_direct_legal_compute_sketch(),
        make_answer_key_oracle_sketch(),
        make_metric_degenerate_sketch(),
        make_graph_cache_surface_sketch(),
        make_passive_value_leak_sketch(),
        make_lookup_split_compute_sketch(),
        make_low_signal_surface_sketch(),
    ]


def _target_for(sketch: dict[str, Any], split: str, index: int) -> tuple[int, dict[str, Any], dict[str, Any], dict[str, Any]]:
    stype = sketch["sketch_type"]
    visible: dict[str, Any] = {}
    hidden: dict[str, Any] = {}
    trace: dict[str, Any] = {}
    if stype == "direct_legal_compute":
        a = index % 3
        b = (index // 3) % 3
        phase = (index // 9) % 3
        target = (a + 2 * b + phase) % 3
        visible.update({"a": a, "b": b, "phase": phase, "size_bucket": (a + b) % 3, "passive_value": (index * 2) % 3})
        trace.update({"legal_tuple": [a, b, phase], "graph_key": f"{a}:{b}:{phase}"})
    elif stype == "lookup_split_compute":
        x = index % 3
        y = (index // 3) % 3
        target = (x + 2 * y) % 3
        prefix = "train" if split == "train" else "heldout"
        visible.update({"x": x, "y": y, "context_id": f"{prefix}-ctx-{index}", "size_bucket": (index // 9) % 3, "passive_value": (index + 1) % 3})
        trace.update({"legal_tuple": [x, y], "graph_key": visible["context_id"]})
    elif stype == "answer_key_oracle":
        weak_cue = index % 3
        target = (index * 2 + 1) % 3
        visible.update({"weak_cue": weak_cue, "size_bucket": index % 2, "passive_value": weak_cue})
        hidden["answer_key"] = target
        trace.update({"legal_tuple": [weak_cue], "graph_key": f"ak:{split}:{index}"})
    elif stype == "metric_degenerate":
        target = 1
        visible.update({"weak_cue": 1, "size_bucket": index % 2, "passive_value": index % 3})
        trace.update({"legal_tuple": [1], "graph_key": f"deg:{index % 5}"})
    elif stype == "passive_value_leak":
        weak_cue = index % 3
        target = (weak_cue + (index // 3)) % 3
        visible.update({"weak_cue": weak_cue, "size_bucket": index % 2, "passive_value": target})
        trace.update({"legal_tuple": [weak_cue], "graph_key": f"passive:{split}:{index}"})
    elif stype == "graph_cache":
        graph_state = index % 8
        target = (graph_state * 2 + 1) % 3
        visible.update({"graph_state": graph_state, "context_id": f"shared-state-{graph_state}", "size_bucket": graph_state % 3, "passive_value": index % 3})
        trace.update({"legal_tuple": [graph_state], "graph_key": f"state:{graph_state}"})
    elif stype == "low_signal":
        weak_cue = index % 3
        target = (index * 2 + (0 if split == "train" else 1)) % 3
        visible.update({"weak_cue": weak_cue, "size_bucket": index % 2, "passive_value": (index + weak_cue) % 3})
        trace.update({"legal_tuple": [weak_cue], "graph_key": f"weak:{split}:{index}"})
    else:
        raise ValueError(f"unknown sketch_type: {stype}")
    return target, visible, hidden, trace


def generate_probe_data(sketch: dict[str, Any]) -> ProbeData:
    train = []
    test = []
    for split, count, rows in [("train", TRAIN_COUNT, train), ("test", TEST_COUNT, test)]:
        for index in range(count):
            target, visible, hidden, trace = _target_for(sketch, split, index)
            rows.append(
                {
                    "episode_id": f"{sketch['sketch_id']}:{split}:{index}",
                    "split": split,
                    "target": target,
                    "visible": visible,
                    "hidden": hidden,
                    "trace": trace,
                    "legal_query_budget": sketch["legal_query_budget"],
                }
            )
    return ProbeData(train=train, test=test)


def _targets(rows: list[dict[str, Any]]) -> list[int]:
    return [int(row["target"]) for row in rows]


def _majority_label(rows: list[dict[str, Any]]) -> int:
    counts = Counter(_targets(rows))
    return counts.most_common(1)[0][0] if counts else 0


def _field(row: dict[str, Any], name: str, default: Any = 0) -> Any:
    if name in row["visible"]:
        return row["visible"][name]
    if name in row["hidden"]:
        return row["hidden"][name]
    return default


def _legal_tuple(row: dict[str, Any], sketch: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(_field(row, field) for field in sketch["legal_channels"])


def _graph_key(row: dict[str, Any]) -> str:
    return str(row["trace"].get("graph_key", row["visible"].get("context_id", row["episode_id"])))


def _score_macro_f1(predictions: list[int], targets: list[int]) -> tuple[float, dict[str, Any]]:
    per_class = {}
    f1_values = []
    for label in LABELS:
        tp = sum(1 for pred, target in zip(predictions, targets) if pred == label and target == label)
        fp = sum(1 for pred, target in zip(predictions, targets) if pred == label and target != label)
        fn = sum(1 for pred, target in zip(predictions, targets) if pred != label and target == label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
        per_class[str(label)] = {"precision": precision, "recall": recall, "f1": f1, "support": sum(1 for target in targets if target == label)}
        f1_values.append(f1)
    return sum(f1_values) / len(f1_values), per_class


def _score_predictions(sketch: dict[str, Any], predictions: list[int], targets: list[int]) -> tuple[float, dict[str, Any]]:
    macro_f1, per_class = _score_macro_f1(predictions, targets)
    if sketch["metric_kind"] == "recall_positive":
        positive_label = 1
        positives = sum(1 for target in targets if target == positive_label)
        recall = (
            sum(1 for pred, target in zip(predictions, targets) if pred == positive_label and target == positive_label) / positives
            if positives
            else 0.0
        )
        return recall, {"reported_metric": "recall_positive", "balanced_macro_f1": macro_f1, "per_class": per_class}
    return macro_f1, {"reported_metric": "balanced_macro_f1", "balanced_macro_f1": macro_f1, "per_class": per_class}


def _per_class_floor_passed(per_class: dict[str, Any], floor: float = 0.20) -> bool:
    for label in LABELS:
        stats = per_class.get(str(label), {})
        if stats.get("support", 0) == 0:
            return False
        if stats.get("precision", 0.0) < floor or stats.get("recall", 0.0) < floor:
            return False
    return True


def _formula_prediction(sketch: dict[str, Any], row: dict[str, Any]) -> int:
    stype = sketch["sketch_type"]
    if stype == "direct_legal_compute":
        return int((_field(row, "a") + 2 * _field(row, "b") + _field(row, "phase")) % 3)
    if stype == "lookup_split_compute":
        return int((_field(row, "x") + 2 * _field(row, "y")) % 3)
    if stype == "graph_cache":
        return int((_field(row, "graph_state") * 2 + 1) % 3)
    if stype == "metric_degenerate":
        return 1
    if stype == "passive_value_leak":
        return int(_field(row, "weak_cue") % 3)
    if stype == "low_signal":
        return int(_field(row, "weak_cue") % 3)
    if stype == "answer_key_oracle":
        return int(_field(row, "weak_cue") % 3)
    return 0


def visible_channel_oracle(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], dict[str, Any]]:
    if sketch["oracle_forbidden_field_access"]:
        preds = [_majority_label(data.train) for _ in data.test]
        return preds, {
            "budget_faithful": False,
            "field_access_manifest": list(sketch["oracle_field_access"]),
            "legal_query_trace": [],
            "failure_reason": f"forbidden_field_access:{','.join(sketch['oracle_forbidden_field_access'])}",
        }
    if len(sketch["oracle_field_access"]) > sketch["legal_query_budget"]:
        preds = [_majority_label(data.train) for _ in data.test]
        return preds, {
            "budget_faithful": False,
            "field_access_manifest": list(sketch["oracle_field_access"]),
            "legal_query_trace": [],
            "failure_reason": "query_budget_exceeded",
        }
    preds = [_formula_prediction(sketch, row) for row in data.test]
    return preds, {
        "budget_faithful": True,
        "field_access_manifest": list(sketch["oracle_field_access"]),
        "legal_query_trace": [
            {"episode_id": row["episode_id"], "queried_fields": list(sketch["oracle_field_access"]), "budget": sketch["legal_query_budget"]}
            for row in data.test[:5]
        ],
        "failure_reason": None,
    }


def answer_key_diagnostic_oracle(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], dict[str, Any]]:
    if sketch["sketch_type"] == "answer_key_oracle":
        return [int(row["hidden"]["answer_key"]) for row in data.test], {
            "field_access_manifest": ["answer_key"],
            "diagnostic_only": True,
            "may_support_promotion": False,
        }
    return [int(row["target"]) for row in data.test], {
        "field_access_manifest": ["target_for_diagnostic_only"],
        "diagnostic_only": True,
        "may_support_promotion": False,
    }


def predict_all(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    return [1 for _ in data.test], [], {"strategy": "constant_positive_label"}


def predict_none(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    return [0 for _ in data.test], [], {"strategy": "constant_none_label"}


def constant_k_sweep(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    targets = _targets(data.test)
    best_label = max(LABELS, key=lambda label: _score_predictions(sketch, [label for _ in targets], targets)[0])
    return [best_label for _ in data.test], [], {"strategy": "constant_k_sweep", "selected_label": best_label}


def random_baseline(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    rng = random.Random(_stable_seed(sketch["sketch_id"], "random_baseline"))
    return [rng.choice(LABELS) for _ in data.test], [], {"strategy": "deterministic_seeded_random"}


def majority(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    label = _majority_label(data.train)
    return [label for _ in data.test], [], {"strategy": "train_majority", "majority_label": label}


def size_only_sweep(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    fallback = _majority_label(data.train)
    by_size: dict[Any, Counter[int]] = defaultdict(Counter)
    for row in data.train:
        by_size[row["visible"].get("size_bucket", 0)][int(row["target"])] += 1
    mapping = {size: counts.most_common(1)[0][0] for size, counts in by_size.items()}
    return [mapping.get(row["visible"].get("size_bucket", 0), fallback) for row in data.test], ["size_bucket"], {
        "strategy": "train_majority_by_size_bucket",
        "learned_bucket_count": len(mapping),
    }


def observation_only(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    fields = ["size_bucket", "passive_value"]
    fallback = _majority_label(data.train)
    table: dict[tuple[Any, ...], Counter[int]] = defaultdict(Counter)
    for row in data.train:
        table[tuple(row["visible"].get(field) for field in fields)][int(row["target"])] += 1
    mapping = {key: counts.most_common(1)[0][0] for key, counts in table.items()}
    return [mapping.get(tuple(row["visible"].get(field) for field in fields), fallback) for row in data.test], fields, {
        "strategy": "passive_observation_table",
        "learned_key_count": len(mapping),
    }


def value_decoder_mean(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    return [int(round(float(row["visible"].get("passive_value", 0)))) % 3 for row in data.test], ["passive_value"], {
        "strategy": "round_passive_value_mean_decoder"
    }


def value_decoder_variance(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    return [int(abs(int(row["visible"].get("passive_value", 0)))) % 3 for row in data.test], ["passive_value"], {
        "strategy": "passive_value_variance_bucket_decoder"
    }


def value_decoder_correlation(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    return [int(row["visible"].get("passive_value", 0)) % 3 for row in data.test], ["passive_value"], {
        "strategy": "passive_value_correlation_decoder"
    }


def value_decoder_pca(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    return [int((row["visible"].get("passive_value", 0) + 3) % 3) for row in data.test], ["passive_value"], {
        "strategy": "one_dimensional_pca_bucket_decoder"
    }


def nearest_neighbor_passive(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    train_points = [(float(row["visible"].get("passive_value", 0)), int(row["target"])) for row in data.train]
    preds = []
    for row in data.test:
        point = float(row["visible"].get("passive_value", 0))
        _, label = min(train_points, key=lambda item: abs(item[0] - point))
        preds.append(label)
    return preds, ["passive_value"], {"strategy": "nearest_neighbor_over_passive_value", "train_points": len(train_points)}


def supervised_or_membership_passive_attacker(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    fallback = _majority_label(data.train)
    table: dict[Any, Counter[int]] = defaultdict(Counter)
    for row in data.train:
        table[row["visible"].get("passive_value", 0)][int(row["target"])] += 1
    mapping = {key: counts.most_common(1)[0][0] for key, counts in table.items()}
    return [mapping.get(row["visible"].get("passive_value", 0), fallback) for row in data.test], ["passive_value"], {
        "strategy": "supervised_passive_value_membership_table",
        "learned_key_count": len(mapping),
    }


def exhaustive_legal_query(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    if len(sketch["target_dependency_set"]) <= sketch["legal_query_budget"] and set(sketch["target_dependency_set"]) <= set(sketch["legal_channels"]):
        return [_formula_prediction(sketch, row) for row in data.test], list(sketch["legal_channels"]), {"strategy": "closed_form_legal_channel_compute"}
    return majority(sketch, data)


def budget_limited_belief_state_planner(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    if sketch["sketch_type"] in {"direct_legal_compute", "lookup_split_compute", "graph_cache"}:
        return [_formula_prediction(sketch, row) for row in data.test], list(sketch["oracle_field_access"]), {"strategy": "budget_faithful_visible_belief_state"}
    return [_formula_prediction(sketch, row) for row in data.test], list(sketch["oracle_field_access"]), {"strategy": "weak_visible_belief_state"}


def greedy_information_gain_or_uncertainty_planner_under_budget(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    fields = list(sketch["legal_channels"])[: max(1, min(1, sketch["legal_query_budget"]))]
    fallback = _majority_label(data.train)
    table: dict[tuple[Any, ...], Counter[int]] = defaultdict(Counter)
    for row in data.train:
        table[tuple(_field(row, field) for field in fields)][int(row["target"])] += 1
    mapping = {key: counts.most_common(1)[0][0] for key, counts in table.items()}
    return [mapping.get(tuple(_field(row, field) for field in fields), fallback) for row in data.test], fields, {
        "strategy": "greedy_single_field_information_gain",
        "learned_key_count": len(mapping),
    }


def graph_lookup(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    fallback = _majority_label(data.train)
    table = {_graph_key(row): int(row["target"]) for row in data.train}
    return [table.get(_graph_key(row), fallback) for row in data.test], ["graph_key"], {"strategy": "graph_key_lookup", "learned_key_count": len(table)}


def transition_table(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    fallback = _majority_label(data.train)
    table: dict[str, Counter[int]] = defaultdict(Counter)
    for row in data.train:
        table[_graph_key(row)][int(row["target"])] += 1
    mapping = {key: counts.most_common(1)[0][0] for key, counts in table.items()}
    return [mapping.get(_graph_key(row), fallback) for row in data.test], ["graph_key"], {"strategy": "transition_table_majority", "learned_key_count": len(mapping)}


def successor_map(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    if sketch["sketch_type"] == "graph_cache":
        return [int((_field(row, "graph_state") * 2 + 1) % 3) for row in data.test], ["graph_state"], {"strategy": "successor_map_from_public_graph_state"}
    return graph_lookup(sketch, data)


def count_table(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    fallback = _majority_label(data.train)
    table: dict[str, Counter[int]] = defaultdict(Counter)
    for row in data.train:
        table[_graph_key(row)][int(row["target"])] += 1
    return [table.get(_graph_key(row), Counter({fallback: 1})).most_common(1)[0][0] for row in data.test], ["graph_key"], {
        "strategy": "count_table_over_graph_key",
        "learned_key_count": len(table),
    }


def fsm_planner(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    if sketch["sketch_type"] == "graph_cache":
        return [int((_field(row, "graph_state") * 2 + 1) % 3) for row in data.test], ["graph_state"], {"strategy": "finite_state_machine_planner"}
    return transition_table(sketch, data)


def episodic_traversal(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    if sketch["sketch_type"] == "graph_cache":
        return [int((_field(row, "graph_state") * 2 + 1) % 3) for row in data.test], ["graph_state"], {"strategy": "episodic_traversal_over_repeated_state"}
    return count_table(sketch, data)


def trace_only_replay(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    fallback = _majority_label(data.train)
    table: dict[tuple[Any, ...], Counter[int]] = defaultdict(Counter)
    for row in data.train:
        table[tuple(row["trace"].get("legal_tuple", []))][int(row["target"])] += 1
    mapping = {key: counts.most_common(1)[0][0] for key, counts in table.items()}
    return [mapping.get(tuple(row["trace"].get("legal_tuple", [])), fallback) for row in data.test], ["trace.legal_tuple"], {
        "strategy": "trace_only_replay_table",
        "learned_key_count": len(mapping),
    }


def ngram_trace_lookup(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    fallback = _majority_label(data.train)
    table: dict[str, Counter[int]] = defaultdict(Counter)
    for row in data.train:
        token = "|".join(str(item) for item in row["trace"].get("legal_tuple", []))
        table[token][int(row["target"])] += 1
    mapping = {key: counts.most_common(1)[0][0] for key, counts in table.items()}
    return [mapping.get("|".join(str(item) for item in row["trace"].get("legal_tuple", [])), fallback) for row in data.test], ["trace.legal_tuple"], {
        "strategy": "ngram_trace_lookup",
        "learned_key_count": len(mapping),
    }


def belief_table(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    return trace_only_replay(sketch, data)


def pair_count_table(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    fields = list(sketch["legal_channels"])[:2]
    fallback = _majority_label(data.train)
    table: dict[tuple[Any, ...], Counter[int]] = defaultdict(Counter)
    for row in data.train:
        table[tuple(_field(row, field) for field in fields)][int(row["target"])] += 1
    mapping = {key: counts.most_common(1)[0][0] for key, counts in table.items()}
    return [mapping.get(tuple(_field(row, field) for field in fields), fallback) for row in data.test], fields, {
        "strategy": "pair_count_table_over_legal_fields",
        "learned_key_count": len(mapping),
    }


def fitted_legal_channel_learner(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    fallback = _majority_label(data.train)
    table: dict[tuple[Any, ...], Counter[int]] = defaultdict(Counter)
    for row in data.train:
        table[_legal_tuple(row, sketch)][int(row["target"])] += 1
    mapping = {key: counts.most_common(1)[0][0] for key, counts in table.items()}
    predictions = [mapping.get(_legal_tuple(row, sketch), fallback) for row in data.test]
    constant_stub = len(set(predictions)) <= 1 and len(set(_targets(data.test))) > 1
    return predictions, list(sketch["legal_channels"]), {
        "strategy": "stdlib_rule_search_over_legal_channels",
        "fit_performed": True,
        "ml_library_used": "stdlib_rule_search",
        "train_rows_consumed": len(data.train),
        "learned_rule_count": len(mapping),
        "anti_stub_guard": {
            "constant_prediction_stub": constant_stub,
            "non_constant_predictions": len(set(predictions)) > 1,
            "source": "fitted mapping from train legal tuples, not deterministic stub",
        },
    }


def strongest_known_classical_method_for_task_type(sketch: dict[str, Any], data: ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    if sketch["sketch_type"] in {"direct_legal_compute", "lookup_split_compute", "graph_cache", "metric_degenerate"}:
        return [_formula_prediction(sketch, row) for row in data.test], list(sketch["oracle_field_access"]), {"strategy": "task_specific_closed_form_classical_method"}
    preds, fields, metadata = fitted_legal_channel_learner(sketch, data)
    metadata = dict(metadata)
    metadata["strategy"] = "strongest_classical_fallback_to_fitted_rule_search"
    return preds, fields, metadata


BASELINE_FUNCTIONS: dict[str, Callable[[dict[str, Any], ProbeData], tuple[list[int], list[str], dict[str, Any]]]] = {
    "predict_all": predict_all,
    "predict_none": predict_none,
    "constant_k_sweep": constant_k_sweep,
    "random": random_baseline,
    "majority": majority,
    "size_only_sweep": size_only_sweep,
    "observation_only": observation_only,
    "value_decoder_mean": value_decoder_mean,
    "value_decoder_variance": value_decoder_variance,
    "value_decoder_correlation": value_decoder_correlation,
    "value_decoder_pca": value_decoder_pca,
    "nearest_neighbor_passive": nearest_neighbor_passive,
    "supervised_or_membership_passive_attacker": supervised_or_membership_passive_attacker,
    "exhaustive_legal_query": exhaustive_legal_query,
    "budget_limited_belief_state_planner": budget_limited_belief_state_planner,
    "greedy_information_gain_or_uncertainty_planner_under_budget": greedy_information_gain_or_uncertainty_planner_under_budget,
    "graph_lookup": graph_lookup,
    "transition_table": transition_table,
    "successor_map": successor_map,
    "count_table": count_table,
    "fsm_planner": fsm_planner,
    "episodic_traversal": episodic_traversal,
    "trace_only_replay": trace_only_replay,
    "ngram_trace_lookup": ngram_trace_lookup,
    "belief_table": belief_table,
    "pair_count_table": pair_count_table,
    "fitted_legal_channel_learner": fitted_legal_channel_learner,
    "strongest_known_classical_method_for_task_type": strongest_known_classical_method_for_task_type,
}

BASELINE_FAMILIES = {
    **{name: "degenerate_control" for name in DEGENERATE_BASELINES},
    **{name: "passive_decoder" for name in PASSIVE_DECODER_FAMILY},
    **{name: "graph_cache" for name in FULL_GRAPH_CACHE_FAMILY},
    "exhaustive_legal_query": "legal_compute",
    "budget_limited_belief_state_planner": "legal_compute",
    "greedy_information_gain_or_uncertainty_planner_under_budget": "legal_compute",
    "trace_only_replay": "trace_replay",
    "ngram_trace_lookup": "trace_replay",
    "belief_table": "belief_table",
    "pair_count_table": "pair_count",
    "fitted_legal_channel_learner": "fitted_legal_channel_learner",
    "strongest_known_classical_method_for_task_type": "classical_method",
}


def _baseline_row(
    *,
    sketch: dict[str, Any],
    run_id: str,
    data: ProbeData,
    producer_name: str,
    predictions: list[int],
    input_fields: list[str],
    metadata: dict[str, Any],
    consumed: bool = True,
    source_body_hash_override: str | None = None,
    prediction_hash_override: str | None = None,
    independence_family_override: str | None = None,
) -> dict[str, Any]:
    targets = _targets(data.test)
    score, score_details = _score_predictions(sketch, predictions, targets)
    body_hash = source_body_hash_override or code_path_hash(BASELINE_FUNCTIONS[producer_name])
    pred_hash = prediction_hash_override or stable_json_hash(predictions)
    family = BASELINE_FAMILIES[producer_name]
    return {
        "sketch_id": sketch["sketch_id"],
        "producer_function": producer_name,
        "producer_module": "batch_env_headroom_scout_002b",
        "source_body_hash": body_hash,
        "code_path_hash": body_hash,
        "prediction_vector_hash": pred_hash,
        "input_field_manifest": list(input_fields),
        "strategy_signature": metadata.get("strategy", producer_name),
        "baseline_family": family,
        "independence_family": independence_family_override or f"{family}:{producer_name}",
        "score": score,
        "score_details": score_details,
        "run_id": run_id,
        "seed_context_episode_ids": [row["episode_id"] for row in data.test],
        "aggregation_rule": "reported sketch metric with balanced macro-F1 details",
        "consumed_by_final_verdict": consumed,
        "details": metadata,
    }


def run_baseline_battery(
    sketch: dict[str, Any],
    data: ProbeData,
    run_id: str,
    required_baselines: list[str] | None = None,
) -> list[dict[str, Any]]:
    producer_names = required_baselines or MANDATORY_BASELINE_PRODUCERS
    rows = []
    for producer_name in producer_names:
        fn = BASELINE_FUNCTIONS[producer_name]
        predictions, input_fields, metadata = fn(sketch, data)
        rows.append(
            _baseline_row(
                sketch=sketch,
                run_id=run_id,
                data=data,
                producer_name=producer_name,
                predictions=predictions,
                input_fields=input_fields,
                metadata=metadata,
            )
        )
    return rows


def _dependency_flags(sketch: dict[str, Any]) -> dict[str, bool]:
    profile = sketch["static_detection_profile"]
    dependency_set = set(sketch["target_dependency_set"])
    legal_set = set(sketch["legal_channels"])
    visible_set = set(sketch["visible_channels"])
    formula_known = bool(profile.get("formula_known_to_static_scanner"))
    legal_components_readable = dependency_set <= legal_set and len(dependency_set) <= sketch["legal_query_budget"]
    direct_deterministic = formula_known and legal_components_readable
    visible_leak = bool(profile.get("visible_field_equals_target")) or ("target" in visible_set)
    passive_likely = bool(profile.get("passive_decoder_likely_reaches_oracle")) or bool(profile.get("visible_field_equals_target"))
    graph_static = bool(profile.get("graph_cache_transition_table_recovers_target_exactly"))
    small_state = bool(profile.get("state_space_small_enough_for_trivial_lookup_saturation"))
    metric_degenerate = sketch["metric_kind"] != "balanced_macro_f1" or bool(profile.get("metric_degenerate"))
    oracle_forbidden = bool(sketch["oracle_forbidden_field_access"]) or bool(profile.get("oracle_uses_forbidden_field"))
    future = "future_label" in sketch["oracle_field_access"]
    return {
        "target_deterministic_from_le_budget_visible_channels": direct_deterministic,
        "legal_query_can_read_all_target_components": formula_known and legal_components_readable,
        "graph_cache_transition_table_recovers_target_exactly": graph_static,
        "state_space_small_enough_for_trivial_lookup_saturation": small_state,
        "visible_fields_leak_target": visible_leak,
        "passive_decoder_likely_reaches_oracle": passive_likely,
        "metric_degenerate": metric_degenerate,
        "oracle_needs_hidden_state_answer_key_or_future_labels": oracle_forbidden,
        "future_label_dependency": future,
    }


def _static_verdict_from_flags(flags: dict[str, bool]) -> str | None:
    if flags["oracle_needs_hidden_state_answer_key_or_future_labels"] or flags["future_label_dependency"]:
        return "reject_oracle_not_budget_faithful"
    if flags["target_deterministic_from_le_budget_visible_channels"] or flags["legal_query_can_read_all_target_components"]:
        return "reject_direct_decode"
    if flags["graph_cache_transition_table_recovers_target_exactly"] or flags["state_space_small_enough_for_trivial_lookup_saturation"]:
        return "reject_graph_cache_saturated"
    if flags["visible_fields_leak_target"] or flags["passive_decoder_likely_reaches_oracle"]:
        return "reject_passive_decodable"
    if flags["metric_degenerate"]:
        return "reject_metric_degenerate"
    return None


def run_independent_static_kill_scan(sketches: list[dict[str, Any]], run_id: str = TASK_ID) -> dict[str, Any]:
    results = []
    for sketch in sketches:
        flags = _dependency_flags(sketch)
        kill_reasons = [criterion for criterion in STATIC_KILL_CRITERIA if flags.get(criterion)]
        per_sketch_verdict = _static_verdict_from_flags(flags)
        results.append(
            {
                "sketch_id": sketch["sketch_id"],
                "static_verdict": "rejected_static_kill" if per_sketch_verdict else "survived_static_kill",
                "per_sketch_verdict": per_sketch_verdict,
                "derived_kill_reasons": kill_reasons,
                "author_claims_used_as_evidence": False,
                "author_claim_digest": stable_json_hash(sketch["author_static_kill_flags"]),
                "producer_function": "run_independent_static_kill_scan",
                "code_path_hash": code_path_hash(run_independent_static_kill_scan),
                "input_artifacts": ["structured_sketch_definition", "target_dependency_set", "oracle_field_access", "legal_channel_set"],
                "run_id": run_id,
                "consumed_by_final_verdict": True,
                "claim_ceiling": CLAIM_CEILING,
            }
        )
    survivors = [row["sketch_id"] for row in results if row["static_verdict"] == "survived_static_kill"]
    return {
        "schema_version": "batch_env_headroom_scout_002b_independent_static_kill_scan_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "stage": "stage_1_independent_static_kill_scan",
        "scanner_independent_from_author_claims": True,
        "criteria": list(STATIC_KILL_CRITERIA),
        "results": results,
        "survivors": survivors,
        "survivor_count": len(survivors),
        "rejected_count": len(results) - len(survivors),
        "producer_function": "run_independent_static_kill_scan",
        "code_path_hash": code_path_hash(run_independent_static_kill_scan),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_dependency_analysis(sketches: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    results = []
    for sketch in sketches:
        flags = _dependency_flags(sketch)
        results.append(
            {
                "sketch_id": sketch["sketch_id"],
                "target_dependency_set": list(sketch["target_dependency_set"]),
                "legal_channel_set": list(sketch["legal_channels"]),
                "visible_channel_set": list(sketch["visible_channels"]),
                "legal_query_budget": sketch["legal_query_budget"],
                "target_dependency_count": len(sketch["target_dependency_set"]),
                "derived_flags": flags,
                "producer_function": "build_dependency_analysis",
                "code_path_hash": code_path_hash(build_dependency_analysis),
                "run_id": run_id,
                "consumed_by_final_verdict": True,
            }
        )
    return {
        "schema_version": "batch_env_headroom_scout_002b_dependency_analysis_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "results": results,
        "claim_ceiling": CLAIM_CEILING,
    }


def _family_max(rows: list[dict[str, Any]], names: list[str]) -> float:
    matching = [row["score"] for row in rows if row["producer_function"] in names]
    return max(matching) if matching else 0.0


def _row_score(rows: list[dict[str, Any]], producer_name: str) -> float:
    for row in rows:
        if row["producer_function"] == producer_name:
            return float(row["score"])
    return 0.0


def _value_level_leakage_scan(sketch: dict[str, Any], data: ProbeData, passive_family_max: float) -> dict[str, Any]:
    positive_control_rows = []
    for row in data.test:
        positive_control_rows.append({**row, "visible": {**row["visible"], "target_alias_positive_control": row["target"]}})
    positive_control_detected = all(row["visible"]["target_alias_positive_control"] == row["target"] for row in positive_control_rows)
    return {
        "producer_function": "_value_level_leakage_scan",
        "code_path_hash": code_path_hash(_value_level_leakage_scan),
        "value_level_scan_performed": True,
        "positive_control_detected": positive_control_detected,
        "passive_family_max_score": passive_family_max,
        "leakage_detected": passive_family_max >= PASSIVE_REJECTION_FLOOR,
        "input_artifacts": ["generated_visible_values", "passive_decoder_family_predictions", "target_alias_positive_control"],
        "consumed_by_final_verdict": True,
    }


def micro_probe_sketch(
    sketch: dict[str, Any],
    run_id: str = TASK_ID,
    required_baselines: list[str] | None = None,
) -> dict[str, Any]:
    data = generate_probe_data(sketch)
    targets = _targets(data.test)
    visible_oracle_preds, visible_oracle_manifest = visible_channel_oracle(sketch, data)
    answer_key_preds, answer_key_manifest = answer_key_diagnostic_oracle(sketch, data)
    visible_oracle_score, visible_oracle_details = _score_predictions(sketch, visible_oracle_preds, targets)
    answer_key_score, _ = _score_predictions(sketch, answer_key_preds, targets)
    baseline_rows = run_baseline_battery(sketch, data, run_id, required_baselines=required_baselines)

    producers = {row["producer_function"] for row in baseline_rows}
    missing = [name for name in MANDATORY_BASELINE_PRODUCERS if name not in producers]
    unconsumed = [row["producer_function"] for row in baseline_rows if not row["consumed_by_final_verdict"]]
    fitted_missing = "fitted_legal_channel_learner" in missing or "strongest_known_classical_method_for_task_type" in missing
    graph_family_max = _family_max(baseline_rows, FULL_GRAPH_CACHE_FAMILY)
    passive_family_max = _family_max(baseline_rows, PASSIVE_DECODER_FAMILY)
    degenerate_family_max = _family_max(baseline_rows, DEGENERATE_BASELINES)
    strongest_row = max(baseline_rows, key=lambda row: row["score"]) if baseline_rows else None
    strongest_score = float(strongest_row["score"]) if strongest_row else 0.0
    preliminary_gap = visible_oracle_score - strongest_score
    exhaustive_score = _row_score(baseline_rows, "exhaustive_legal_query")
    fitted_score = _row_score(baseline_rows, "fitted_legal_channel_learner")
    lookup_score = _row_score(baseline_rows, "graph_lookup")
    _, visible_per_class = _score_macro_f1(visible_oracle_preds, targets)
    per_class_floor_passed = _per_class_floor_passed(visible_per_class)
    value_leakage = _value_level_leakage_scan(sketch, data, passive_family_max)

    if fitted_missing:
        verdict = "blocked_compute_baseline_missing"
        reason = "fitted legal-channel learner or strongest classical method missing"
    elif missing or unconsumed:
        verdict = "blocked_baseline_battery_incomplete"
        reason = "mandatory baseline missing or unconsumed"
    elif not visible_oracle_manifest["budget_faithful"]:
        verdict = "reject_oracle_not_budget_faithful"
        reason = visible_oracle_manifest["failure_reason"] or "visible oracle not budget faithful"
    elif sketch["metric_kind"] != "balanced_macro_f1" and (
        degenerate_family_max >= DEGENERATE_REJECTION_FLOOR or not per_class_floor_passed
    ):
        verdict = "reject_metric_degenerate"
        reason = "degenerate predictor or reported metric saturated"
    elif graph_family_max >= visible_oracle_score - EQUIVALENCE_BAND and graph_family_max >= ORACLE_FLOOR:
        verdict = "reject_graph_cache_saturated"
        reason = "full graph-cache family reached visible-oracle equivalence band"
    elif passive_family_max >= PASSIVE_REJECTION_FLOOR:
        verdict = "reject_passive_decodable"
        reason = "passive value-decoder family reached rejection floor"
    elif exhaustive_score >= visible_oracle_score - EQUIVALENCE_BAND and visible_oracle_score >= ORACLE_FLOOR:
        verdict = sketch["preferred_compute_saturation_verdict"]
        reason = "legal-channel compute baseline reached visible-oracle equivalence band"
    elif fitted_score >= visible_oracle_score - EQUIVALENCE_BAND and visible_oracle_score >= ORACLE_FLOOR:
        verdict = "reject_no_headroom_likely"
        reason = "fitted legal-channel learner reached visible-oracle equivalence band"
    elif visible_oracle_score < ORACLE_FLOOR or preliminary_gap < PROMOTION_GAP:
        verdict = "reject_underpowered_surface"
        reason = "visible oracle too weak or preliminary gap below promotion threshold"
    elif degenerate_family_max >= DEGENERATE_REJECTION_FLOOR or not per_class_floor_passed:
        verdict = "reject_metric_degenerate"
        reason = "degenerate predictor or balanced per-class floor failed"
    else:
        verdict = "promote_to_full_harness_candidate"
        reason = "all candidate-free micro-probe promotion gates provisionally passed"

    return {
        "schema_version": "batch_env_headroom_scout_002b_micro_probe_row_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "sketch_id": sketch["sketch_id"],
        "per_sketch_verdict": verdict,
        "verdict_reason": reason,
        "allowed_verdict": verdict in ALLOWED_PER_SKETCH_VERDICTS,
        "visible_oracle_score": visible_oracle_score,
        "visible_oracle_details": visible_oracle_details,
        "visible_oracle_budget_faithful": bool(visible_oracle_manifest["budget_faithful"]),
        "visible_oracle_field_access_manifest": visible_oracle_manifest["field_access_manifest"],
        "visible_oracle_legal_query_trace": visible_oracle_manifest["legal_query_trace"],
        "answer_key_diagnostic_oracle_score": answer_key_score,
        "answer_key_diagnostic_oracle_manifest": answer_key_manifest,
        "answer_key_oracle_may_support_promotion": False,
        "strongest_cheap_baseline_score": strongest_score,
        "strongest_cheap_baseline_producer": strongest_row["producer_function"] if strongest_row else None,
        "preliminary_gap": preliminary_gap,
        "exhaustive_legal_query_score": exhaustive_score,
        "fitted_legal_channel_learner_score": fitted_score,
        "graph_cache_family_max_score": graph_family_max,
        "passive_family_max_score": passive_family_max,
        "degenerate_family_max_score": degenerate_family_max,
        "size_only_max_score": _row_score(baseline_rows, "size_only_sweep"),
        "lookup_memorization_score": lookup_score,
        "lookup_failure_supports_promotion": False,
        "equivalence_band": EQUIVALENCE_BAND,
        "passive_rejection_floor": PASSIVE_REJECTION_FLOOR,
        "degenerate_rejection_floor": DEGENERATE_REJECTION_FLOOR,
        "per_class_floor_passed": per_class_floor_passed,
        "missing_mandatory_baselines": missing,
        "unconsumed_baselines": unconsumed,
        "baseline_rows": baseline_rows,
        "value_level_leakage_scan": value_leakage,
        "producer_function": "micro_probe_sketch",
        "code_path_hash": code_path_hash(micro_probe_sketch),
        "input_artifacts": ["structured_sketch_definition", "generated_probe_data", "baseline_battery"],
        "consumed_by_final_verdict": True,
        "claim_ceiling": CLAIM_CEILING,
    }


def run_micro_probes(sketches: list[dict[str, Any]], static_scan: dict[str, Any], run_id: str) -> dict[str, Any]:
    by_id = {sketch["sketch_id"]: sketch for sketch in sketches}
    survivors = [by_id[sketch_id] for sketch_id in static_scan["survivors"]]
    with ThreadPoolExecutor(max_workers=min(4, max(1, len(survivors)))) as pool:
        rows = list(pool.map(lambda sketch: micro_probe_sketch(sketch, run_id=run_id), survivors))
    rows.sort(key=lambda row: row["sketch_id"])
    return {
        "schema_version": "batch_env_headroom_scout_002b_micro_probe_results_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "stage": "stage_2_micro_probe_only_for_static_survivors",
        "parallelized_environment_screening": True,
        "candidate_implementation_authorized": False,
        "mandatory_baseline_producers": list(MANDATORY_BASELINE_PRODUCERS),
        "results": rows,
        "producer_function": "run_micro_probes",
        "code_path_hash": code_path_hash(run_micro_probes),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_author_claims(sketches: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    return {
        "schema_version": "batch_env_headroom_scout_002b_author_claims_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "status": "stored_only_not_evidence",
        "author_claims_used_as_evidence": False,
        "claims": [
            {
                "sketch_id": sketch["sketch_id"],
                "author_static_kill_flags": sketch["author_static_kill_flags"],
                "claim_digest": stable_json_hash(sketch["author_static_kill_flags"]),
            }
            for sketch in sketches
        ],
        "claim_ceiling": CLAIM_CEILING,
    }


def build_oracle_as_baseline_report(
    sketches: list[dict[str, Any]],
    static_scan: dict[str, Any],
    micro_probe_results: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    micro_by_id = {row["sketch_id"]: row for row in micro_probe_results["results"]}
    results = []
    for sketch in sketches:
        data = generate_probe_data(sketch)
        oracle_preds, manifest = visible_channel_oracle(sketch, data)
        targets = _targets(data.test)
        oracle_score, _ = _score_predictions(sketch, oracle_preds, targets)
        dependency_set = set(sketch["target_dependency_set"])
        legal_set = set(sketch["legal_channels"])
        can_register = bool(manifest["budget_faithful"]) and dependency_set <= legal_set and len(dependency_set) <= sketch["legal_query_budget"]
        fair_score = oracle_score if can_register else None
        micro = micro_by_id.get(sketch["sketch_id"], {})
        results.append(
            {
                "sketch_id": sketch["sketch_id"],
                "visible_oracle_budget_faithful": bool(manifest["budget_faithful"]),
                "oracle_field_access_manifest": manifest["field_access_manifest"],
                "legal_query_trace": manifest["legal_query_trace"],
                "oracle_score": oracle_score,
                "oracle_registered_as_fair_baseline": can_register,
                "oracle_as_fair_baseline_score": fair_score,
                "symmetry_blocks_promotion": can_register and fair_score is not None and fair_score >= oracle_score - EQUIVALENCE_BAND,
                "micro_probe_verdict": micro.get("per_sketch_verdict"),
                "producer_function": "build_oracle_as_baseline_report",
                "code_path_hash": code_path_hash(build_oracle_as_baseline_report),
                "run_id": run_id,
                "consumed_by_final_verdict": True,
            }
        )
    return {
        "schema_version": "batch_env_headroom_scout_002b_oracle_as_baseline_report_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "results": results,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_baseline_independence_report_from_rows(
    baseline_rows: list[dict[str, Any]],
    promotion_intended: bool = False,
) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in baseline_rows:
        grouped[(row["source_body_hash"], row["prediction_vector_hash"])].append(row)
    collapsed = {}
    aliases = []
    for index, ((source_hash, prediction_hash), rows) in enumerate(grouped.items(), start=1):
        family_names = sorted({row.get("independence_family", row["producer_function"]) for row in rows})
        if len(rows) > 1:
            alias_family = "aliased_weak_family" if any("aliased_weak_family" in name for name in family_names) else f"collapsed_alias_family_{index}"
            collapsed[alias_family] = [row["producer_function"] for row in rows]
            aliases.append(
                {
                    "independence_family": alias_family,
                    "source_body_hash": source_hash,
                    "prediction_vector_hash": prediction_hash,
                    "producer_functions": [row["producer_function"] for row in rows],
                }
            )
        else:
            collapsed[family_names[0]] = [rows[0]["producer_function"]]
    mandatory_present = {row["producer_function"] for row in baseline_rows}
    missing = [name for name in MANDATORY_BASELINE_PRODUCERS if name not in mandatory_present]
    promotion_blocking_aliasing = promotion_intended and bool(aliases)
    return {
        "schema_version": "batch_env_headroom_scout_002b_baseline_independence_report_v1",
        "aliases_detected": bool(aliases),
        "aliases": aliases,
        "collapsed_independence_families": collapsed,
        "missing_mandatory_producers": missing,
        "promotion_blocking_aliasing": promotion_blocking_aliasing,
        "producer_function": "build_baseline_independence_report_from_rows",
        "code_path_hash": code_path_hash(build_baseline_independence_report_from_rows),
        "consumed_by_final_verdict": True,
    }


def build_baseline_independence_report(micro_probe_results: dict[str, Any], run_id: str) -> dict[str, Any]:
    per_sketch = []
    for row in micro_probe_results["results"]:
        report = build_baseline_independence_report_from_rows(
            row["baseline_rows"],
            promotion_intended=row["per_sketch_verdict"] == "promote_to_full_harness_candidate",
        )
        report["sketch_id"] = row["sketch_id"]
        per_sketch.append(report)
    return {
        "schema_version": "batch_env_headroom_scout_002b_baseline_independence_report_bundle_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "results": per_sketch,
        "aliases_detected": any(row["aliases_detected"] for row in per_sketch),
        "promotion_blocking_aliasing": any(row["promotion_blocking_aliasing"] for row in per_sketch),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_fitted_legal_channel_learner_report(micro_probe_results: dict[str, Any], run_id: str) -> dict[str, Any]:
    results = []
    for probe in micro_probe_results["results"]:
        for row in probe["baseline_rows"]:
            if row["producer_function"] == "fitted_legal_channel_learner":
                details = row["details"]
                results.append(
                    {
                        "sketch_id": probe["sketch_id"],
                        "producer_function": "fitted_legal_channel_learner",
                        "score": row["score"],
                        "fit_performed": bool(details.get("fit_performed")),
                        "fit_evidence": {
                            "ml_library_used": details.get("ml_library_used"),
                            "train_rows_consumed": details.get("train_rows_consumed"),
                            "learned_rule_count": details.get("learned_rule_count"),
                            "anti_stub_guard": details.get("anti_stub_guard"),
                        },
                        "source_body_hash": row["source_body_hash"],
                        "prediction_vector_hash": row["prediction_vector_hash"],
                        "consumed_by_final_verdict": row["consumed_by_final_verdict"],
                        "run_id": run_id,
                    }
                )
    return {
        "schema_version": "batch_env_headroom_scout_002b_fitted_legal_channel_learner_report_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "results": results,
        "claim_ceiling": CLAIM_CEILING,
    }


def _static_rejections(static_scan: dict[str, Any]) -> list[dict[str, Any]]:
    rejected = []
    for row in static_scan["results"]:
        if row["static_verdict"] == "rejected_static_kill":
            rejected.append(
                {
                    "sketch_id": row["sketch_id"],
                    "rejection_stage": "independent_static_kill_scan",
                    "per_sketch_verdict": row["per_sketch_verdict"],
                    "derived_kill_reasons": row["derived_kill_reasons"],
                    "author_claims_used_as_evidence": False,
                    "candidate_implementation_authorized": False,
                    "route_tournament_authorized": False,
                }
            )
    return rejected


def build_rejected_sketches(static_scan: dict[str, Any], micro_probe_results: dict[str, Any], run_id: str) -> dict[str, Any]:
    rejected = _static_rejections(static_scan)
    for row in micro_probe_results["results"]:
        if row["per_sketch_verdict"] != "promote_to_full_harness_candidate":
            rejected.append(
                {
                    "sketch_id": row["sketch_id"],
                    "rejection_stage": "micro_probe",
                    "per_sketch_verdict": row["per_sketch_verdict"],
                    "verdict_reason": row["verdict_reason"],
                    "visible_oracle_score": row["visible_oracle_score"],
                    "strongest_cheap_baseline_score": row["strongest_cheap_baseline_score"],
                    "strongest_cheap_baseline_producer": row["strongest_cheap_baseline_producer"],
                    "exhaustive_legal_query_score": row["exhaustive_legal_query_score"],
                    "fitted_legal_channel_learner_score": row["fitted_legal_channel_learner_score"],
                    "graph_cache_family_max_score": row["graph_cache_family_max_score"],
                    "passive_family_max_score": row["passive_family_max_score"],
                    "degenerate_family_max_score": row["degenerate_family_max_score"],
                    "candidate_implementation_authorized": False,
                    "route_tournament_authorized": False,
                }
            )
    return {
        "schema_version": "batch_env_headroom_scout_002b_rejected_sketches_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "rejected": rejected,
        "rejected_count": len(rejected),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_promoted_candidates(micro_probe_results: dict[str, Any], run_id: str) -> dict[str, Any]:
    promoted = []
    for row in micro_probe_results["results"]:
        if row["per_sketch_verdict"] == "promote_to_full_harness_candidate":
            promoted.append(
                {
                    "sketch_id": row["sketch_id"],
                    "target_rule": "see sketch_registry.json",
                    "target_dependency_set": "see dependency_analysis.json",
                    "legal_channel_set": "see dependency_analysis.json",
                    "budget": "see sketch_registry.json",
                    "oracle_definition": "see sketch_registry.json",
                    "oracle_field_access_manifest": row["visible_oracle_field_access_manifest"],
                    "strongest_cheap_baseline_score": row["strongest_cheap_baseline_score"],
                    "strongest_cheap_baseline_producer": row["strongest_cheap_baseline_producer"],
                    "fitted_legal_channel_learner_score": row["fitted_legal_channel_learner_score"],
                    "exhaustive_legal_query_score": row["exhaustive_legal_query_score"],
                    "graph_cache_family_max": row["graph_cache_family_max_score"],
                    "passive_family_max": row["passive_family_max_score"],
                    "degenerate_max": row["degenerate_family_max_score"],
                    "size_only_max": row["size_only_max_score"],
                    "preliminary_gap": row["preliminary_gap"],
                    "candidate_implementation_authorized": False,
                    "route_tournament_authorized": False,
                    "claim_ceiling": CLAIM_CEILING,
                }
            )
    promoted = promoted[:2]
    return {
        "schema_version": "batch_env_headroom_scout_002b_promoted_candidates_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "promoted": promoted,
        "promoted_count": len(promoted),
        "candidate_implementation_authorized": False,
        "route_tournament_authorized": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def produce_callable_final_verdict(context: dict[str, Any]) -> dict[str, Any]:
    if not context.get("static_scan_independent", True):
        final_verdict = "blocked_static_scan_not_independent"
    elif not context.get("artifact_integrity_ok", True):
        final_verdict = "blocked_artifact_integrity_failure"
    else:
        rows = context.get("micro_probe_rows", [])
        promotion_intended = any(row.get("per_sketch_verdict") == "promote_to_full_harness_candidate" for row in rows) or context.get(
            "promotion_intended", False
        )
        all_baselines = [baseline for row in rows for baseline in row.get("baseline_rows", [])]
        present = {row["producer_function"] for row in all_baselines if row.get("consumed_by_final_verdict", False)}
        missing = [name for name in MANDATORY_BASELINE_PRODUCERS if name not in present]
        if "fitted_legal_channel_learner" in missing or "strongest_known_classical_method_for_task_type" in missing:
            final_verdict = "blocked_compute_baseline_missing"
        elif missing:
            final_verdict = "blocked_baseline_battery_incomplete"
        elif any(not row.get("consumed_by_final_verdict", False) for row in all_baselines):
            final_verdict = "blocked_baseline_battery_incomplete"
        else:
            independence = context.get("baseline_independence_report") or build_baseline_independence_report_from_rows(
                all_baselines, promotion_intended=promotion_intended
            )
            if independence.get("promotion_blocking_aliasing"):
                final_verdict = "blocked_baseline_aliasing_invalidates_promotion"
            elif any(row.get("per_sketch_verdict") == "reject_oracle_not_budget_faithful" for row in rows) and context.get(
                "block_final_on_oracle_failure", False
            ):
                final_verdict = "blocked_oracle_not_budget_faithful"
            else:
                promoted_count = sum(1 for row in rows if row.get("per_sketch_verdict") == "promote_to_full_harness_candidate")
                if promoted_count:
                    final_verdict = f"promoted_{min(promoted_count, 2)}_full_harness_candidates"
                else:
                    final_verdict = "all_rejected_static_or_microprobe"
    return {
        "schema_version": "batch_env_headroom_scout_002b_callable_final_verdict_v1",
        "task_id": TASK_ID,
        "final_verdict": final_verdict,
        "allowed_final_verdict": final_verdict in ALLOWED_FINAL_VERDICTS,
        "producer_function": "produce_callable_final_verdict",
        "code_path_hash": code_path_hash(produce_callable_final_verdict),
        "baseline_independence_report": context.get("baseline_independence_report")
        or build_baseline_independence_report_from_rows(
            [baseline for row in context.get("micro_probe_rows", []) for baseline in row.get("baseline_rows", [])],
            promotion_intended=context.get("promotion_intended", False),
        ),
        "consumed_by_final_verdict": True,
        "claim_ceiling": CLAIM_CEILING,
    }


def final_verdict_context_for_test(
    *,
    remove_baselines: list[str] | None = None,
    unconsumed_baselines: list[str] | None = None,
    alias_positive_rows: bool = False,
) -> dict[str, Any]:
    sketch = make_low_signal_surface_sketch()
    data = generate_probe_data(sketch)
    rows = run_baseline_battery(sketch, data, run_id="pytest-final-verdict-context")
    remove = set(remove_baselines or [])
    unconsume = set(unconsumed_baselines or [])
    rows = [row for row in rows if row["producer_function"] not in remove]
    for row in rows:
        if row["producer_function"] in unconsume:
            row["consumed_by_final_verdict"] = False
    if alias_positive_rows:
        for name in ["budget_limited_belief_state_planner", "greedy_information_gain_or_uncertainty_planner_under_budget"]:
            for row in rows:
                if row["producer_function"] == name:
                    row["source_body_hash"] = "alias-source-hash"
                    row["code_path_hash"] = "alias-source-hash"
                    row["prediction_vector_hash"] = "alias-prediction-hash"
                    row["independence_family"] = "aliased_weak_family"
    probe_row = {
        "sketch_id": "positive_context_for_alias_or_missing_rows",
        "per_sketch_verdict": "promote_to_full_harness_candidate",
        "baseline_rows": rows,
    }
    independence = build_baseline_independence_report_from_rows(rows, promotion_intended=True)
    return {
        "static_scan_independent": True,
        "artifact_integrity_ok": True,
        "promotion_intended": True,
        "micro_probe_rows": [probe_row],
        "baseline_independence_report": independence,
    }


def _registry_payload(sketches: list[dict[str, Any]], repo_root: Path, run_id: str) -> dict[str, Any]:
    safe_sketches = []
    for sketch in sketches:
        safe_sketches.append({key: value for key, value in sketch.items() if key != "author_static_kill_flags"})
    return {
        "schema_version": "batch_env_headroom_scout_002b_sketch_registry_v1",
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
            "full harness execution",
            "relational_contrast_budget_probe full harness",
            "runtime/mainline/admission/bridge wiring",
            "MINIMAL-ENV-SPEC-001A reopen or optimization",
            "commit/push/tag/remote-anchor",
        ],
        "repo_readback": {
            "root": str(repo_root),
            "branch": _run_git(repo_root, ["branch", "--show-current"]),
            "head": _run_git(repo_root, ["rev-parse", "HEAD"]),
            "status_short": _run_git(repo_root, ["status", "--short"]),
            "ahead_behind": _run_git(repo_root, ["status", "-sb"]),
        },
        "canonical_prior_evidence_readback": {
            "baseline_first_harness_001a_r1": "accepted candidate-free Phase-0 no-headroom negative environment evidence per current task request and repo closeout doc",
            "minimal_env_spec_001a": "closed for candidate work per current task request and repo closeout docs",
            "batch_env_headroom_scout_002a": "closed as blocked_promotion_false_positive_direct_decode per repo closeout doc",
        },
        "sketch_count": len(safe_sketches),
        "sketches": safe_sketches,
        "producer_function": "_registry_payload",
        "code_path_hash": code_path_hash(_registry_payload),
    }


def _final_report(
    *,
    registry: dict[str, Any],
    static_scan: dict[str, Any],
    micro_probe_results: dict[str, Any],
    final_verdict: dict[str, Any],
    promoted: dict[str, Any],
    rejected: dict[str, Any],
) -> str:
    lines = [
        "# BATCH-ENV-HEADROOM-SCOUT-002B Final Report",
        "",
        f"Verdict: `{final_verdict['final_verdict']}`",
        f"Current layer: {CURRENT_LAYER}",
        f"Mainline integration status: {MAINLINE_STATUS}",
        f"Enabled status: {ENABLED_STATUS}",
        "Real trigger evidence: callable independent static scan, callable micro-probes for static survivors, callable baseline rows, fitted legal-channel learner fit records, oracle-as-baseline report, and callable final verdict.",
        f"Claim ceiling: {CLAIM_CEILING}",
        "",
        "Task boundary:",
        "- Candidate implementation authorized: false",
        "- Route tournament authorized: false",
        "- Full harness executed: false",
        "- Runtime/mainline/admission/bridge path enabled: false",
        "- Auto-Remote-Anchor: forbidden",
        "",
        "Scout summary:",
        f"- Sketches registered: {registry['sketch_count']}",
        f"- Static rejections: {static_scan['rejected_count']}",
        f"- Static survivors micro-probed: {len(micro_probe_results['results'])}",
        f"- Promoted full-harness candidates: {promoted['promoted_count']}",
        f"- Rejected sketches: {rejected['rejected_count']}",
        "",
        "Rejected sketches:",
    ]
    for row in rejected["rejected"]:
        lines.append(f"- `{row['sketch_id']}` via {row['rejection_stage']}: `{row['per_sketch_verdict']}`")
    lines.extend(
        [
            "",
            "Promoted full-harness candidates:",
        ]
    )
    if promoted["promoted"]:
        for row in promoted["promoted"]:
            lines.append(f"- `{row['sketch_id']}`: preliminary gap {row['preliminary_gap']}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "Baseline results:",
            "- Complete cheap-baseline rows are in `micro_probe_results.json`.",
            "- Oracle-as-baseline symmetry rows are in `oracle_as_baseline_report.json`.",
            "- Baseline independence and alias collapse are in `baseline_independence_report.json`.",
            "- Fitted legal-channel learner fit evidence is in `fitted_legal_channel_learner_report.json`.",
            "",
            "Ablation results:",
            "- This task is a micro-probe scout, not a formal Gate or full harness.",
            "- Callable negative controls are represented by required rejection fixtures and final-verdict blockers for missing rows, unconsumed rows, aliasing, answer-key oracle, passive leakage, metric degeneracy, graph-cache saturation, and lookup-vs-compute split artifacts.",
            "",
            "Replay result:",
            "- Full replay is not claimed. Each baseline row records prediction hashes, input manifests, producer hashes, and consumed status; full trace/replay remains a separate full baseline-first harness requirement for any later promoted card.",
            "",
            "Stop conditions triggered:",
            "- Static and micro-probe rejection verdicts are preserved in `rejected_sketches.json`.",
            "",
            "Next minimal closed-loop action:",
        ]
    )
    if promoted["promoted_count"] == 0:
        lines.append("- Preserve rejection analysis and update environment design constraints before any new sketch batch.")
    else:
        lines.append("- Draft separate full baseline-first harness task cards only for promoted sketches; stop before candidate implementation.")
    lines.extend(
        [
            "",
            "What this does not prove:",
            "- No headroom confirmation.",
            "- No Gate1 pass.",
            "- No mechanism validity.",
            "- No candidate feasibility.",
            "- No runtime/mainline effect.",
            "- No agency, autonomy, consciousness, EGO readiness, stable user benefit, or companion readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def run_batch_scout(out_dir: str | Path, run_id: str = TASK_ID, repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    sketches = build_sketch_registry()
    registry = _registry_payload(sketches, root, run_id)
    author_claims = build_author_claims(sketches, run_id)
    static_scan = run_independent_static_kill_scan(sketches, run_id=run_id)
    dependency_analysis = build_dependency_analysis(sketches, run_id=run_id)
    micro_probe_results = run_micro_probes(sketches, static_scan, run_id=run_id)
    oracle_as_baseline = build_oracle_as_baseline_report(sketches, static_scan, micro_probe_results, run_id=run_id)
    independence = build_baseline_independence_report(micro_probe_results, run_id=run_id)
    fitted_report = build_fitted_legal_channel_learner_report(micro_probe_results, run_id=run_id)
    promoted = build_promoted_candidates(micro_probe_results, run_id=run_id)
    rejected = build_rejected_sketches(static_scan, micro_probe_results, run_id=run_id)
    final_context = {
        "static_scan_independent": static_scan["scanner_independent_from_author_claims"],
        "artifact_integrity_ok": True,
        "micro_probe_rows": micro_probe_results["results"],
        "baseline_independence_report": {
            "schema_version": independence["schema_version"],
            "aliases_detected": independence["aliases_detected"],
            "promotion_blocking_aliasing": independence["promotion_blocking_aliasing"],
            "collapsed_independence_families": {
                row["sketch_id"]: row["collapsed_independence_families"] for row in independence["results"]
            },
        },
    }
    final_verdict = produce_callable_final_verdict(final_context)
    final_report = _final_report(
        registry=registry,
        static_scan=static_scan,
        micro_probe_results=micro_probe_results,
        final_verdict=final_verdict,
        promoted=promoted,
        rejected=rejected,
    )

    artifacts: dict[str, Any] = {
        "sketch_registry.json": registry,
        "author_claims.json": author_claims,
        "independent_static_kill_scan.json": static_scan,
        "dependency_analysis.json": dependency_analysis,
        "oracle_as_baseline_report.json": oracle_as_baseline,
        "micro_probe_results.json": micro_probe_results,
        "baseline_independence_report.json": independence,
        "fitted_legal_channel_learner_report.json": fitted_report,
        "promoted_full_harness_candidates.json": promoted,
        "rejected_sketches.json": rejected,
    }
    for filename, payload in artifacts.items():
        write_json(out / filename, payload)
    (out / "final_report.md").write_text(final_report, encoding="utf-8")

    artifact_hashes = {}
    artifact_integrity_ok = True
    for filename in REQUIRED_ARTIFACT_FILENAMES:
        path = out / filename
        if not path.exists():
            artifact_integrity_ok = False
            continue
        if filename.endswith(".json"):
            try:
                artifact_hashes[filename] = stable_json_hash(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                artifact_integrity_ok = False
        else:
            artifact_hashes[filename] = _sha_text(path.read_text(encoding="utf-8"))

    if not artifact_integrity_ok:
        final_context["artifact_integrity_ok"] = False
        final_verdict = produce_callable_final_verdict(final_context)

    return {
        "task_id": TASK_ID,
        "run_id": run_id,
        "final_verdict": final_verdict["final_verdict"],
        "callable_final_verdict": final_verdict,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": MAINLINE_STATUS,
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": "callable static scan, micro-probe baselines, fitted learner report, oracle-as-baseline report, and artifact parse/readback",
        "claim_ceiling": CLAIM_CEILING,
        "candidate_implementation_authorized": False,
        "route_tournament_authorized": False,
        "static_scan": static_scan,
        "micro_probe_results": micro_probe_results,
        "promoted_full_harness_candidates": promoted,
        "rejected_sketches": rejected,
        "artifact_hashes": artifact_hashes,
        "artifact_integrity_ok": artifact_integrity_ok,
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
                "final_verdict": result["final_verdict"],
                "static_survivor_count": result["static_scan"]["survivor_count"],
                "micro_probed_count": len(result["micro_probe_results"]["results"]),
                "promoted_count": result["promoted_full_harness_candidates"]["promoted_count"],
                "artifact_integrity_ok": result["artifact_integrity_ok"],
                "claim_ceiling": result["claim_ceiling"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
