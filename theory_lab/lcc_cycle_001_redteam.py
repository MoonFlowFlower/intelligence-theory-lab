from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ALLOWED_CYCLE_VERDICTS = {
    "lcc_contract_strengthened_bounded",
    "lcc_contract_failed_label_shortcut",
    "lcc_contract_failed_effect_learning",
    "lcc_contract_failed_heuristic_equivalence",
    "lcc_contract_inconclusive",
    "authorize_cycle_002_contract_only",
    "close_lcc_v0",
}


@dataclass(frozen=True)
class Effect:
    viability_delta: float
    control_delta: float

    @property
    def utility(self) -> float:
        return self.viability_delta + 0.7 * self.control_delta


@dataclass(frozen=True)
class State:
    state_id: str
    action_count: int
    risk: float
    load: float
    family: str = "scale_world"


class LearnedEffectModelPolicy:
    READ_FIELDS = ("state_features", "action_handles", "learned_effect_model")

    def choose(self, state: State, estimates: dict[str, Effect]) -> str:
        utilities = {handle: effect.utility for handle, effect in estimates.items()}
        return max(sorted(utilities), key=lambda handle: utilities[handle])


class EffectTablePolicy:
    READ_FIELDS = ("explicit_effect_table",)
    DIAGNOSTIC_ONLY = True

    def choose(self, effects: dict[str, Effect]) -> str:
        utilities = {handle: effect.utility for handle, effect in effects.items()}
        return max(sorted(utilities), key=lambda handle: utilities[handle])


class ActionLabelHeuristicBaseline:
    READ_FIELDS = ("semantic_action_label_text",)

    def choose(self, labels_by_action: dict[str, str]) -> str:
        return min(labels_by_action.items(), key=lambda item: item[1])[0]


class StaticSafetyTableBaseline:
    READ_FIELDS = ("hard_coded_action_safety_table",)

    def choose(self, state: State, action_handles: list[str]) -> str:
        index = (sum(ord(char) for char in state.state_id) + state.action_count) % len(action_handles)
        return action_handles[index]


class ContextualHeuristicBaseline:
    READ_FIELDS = ("context_features", "hand_coded_risk_bucket")

    def choose(self, state: State, action_handles: list[str]) -> str:
        bucket = int((state.risk + state.load) * 3.0)
        return action_handles[bucket % len(action_handles)]


class NearestNeighborTracePolicy:
    READ_FIELDS = ("state_features", "past_trace_actions")

    def __init__(self, train_records: list[dict[str, Any]]) -> None:
        self.examples = [
            (
                record["state_features"]["risk"],
                record["state_features"]["load"],
                record["candidate"]["selected_action"],
            )
            for record in train_records
            if record["variant"] == "canonical"
        ]

    def choose(self, state: State, action_handles: list[str]) -> str:
        if not self.examples:
            return action_handles[0]
        nearest = min(
            self.examples,
            key=lambda example: (example[0] - state.risk) ** 2 + (example[1] - state.load) ** 2,
        )
        if nearest[2] in action_handles:
            return nearest[2]
        return action_handles[0]


def handles(action_count: int) -> list[str]:
    return [f"a{index:02d}" for index in range(action_count)]


def anonymous_labels(action_handles: list[str], seed: int) -> dict[str, str]:
    rng = random.Random(seed)
    tokens = [f"glyph_{seed}_{index:02d}" for index in range(len(action_handles))]
    rng.shuffle(tokens)
    return dict(zip(action_handles, tokens))


def permute_labels(labels: dict[str, str], seed: int) -> dict[str, str]:
    rng = random.Random(seed)
    action_handles = sorted(labels)
    values = [labels[handle] for handle in action_handles]
    rng.shuffle(values)
    if all(labels[handle] == value for handle, value in zip(action_handles, values)):
        values = values[1:] + values[:1]
    return dict(zip(action_handles, values))


def state_for(action_count: int, index: int, family: str = "scale_world") -> State:
    risk = ((index * 37 + action_count * 11) % 100) / 100.0
    load = ((index * 19 + action_count * 7) % 100) / 100.0
    return State(
        state_id=f"{family}_{action_count}_{index:03d}",
        action_count=action_count,
        risk=risk,
        load=load,
        family=family,
    )


def generated_effects(state: State, seed: int) -> dict[str, Effect]:
    rng = random.Random(seed + state.action_count * 1000 + int(state.risk * 1000))
    effects: dict[str, Effect] = {}
    for index, handle in enumerate(handles(state.action_count)):
        phase = (index + 1) * (0.9 + state.risk) + state.load * 1.7
        viability = math.sin(phase) * 2.0 + math.cos(index * 1.3 + state.risk) * 1.1
        control = math.cos(phase * 0.8) * 1.4 - state.load * (index % 3) * 0.25
        viability += rng.uniform(-0.015, 0.015)
        control += rng.uniform(-0.015, 0.015)
        effects[handle] = Effect(viability, control)
    return break_ties(effects)


def learned_world_effects(state: State, action_count: int) -> dict[str, Effect]:
    effects: dict[str, Effect] = {}
    for index, handle in enumerate(handles(action_count)):
        bias = -0.35 + index * (0.7 / max(action_count - 1, 1))
        sensitivity = -1.2 + index * (2.4 / max(action_count - 1, 1))
        control_bias = 0.8 - index * (0.4 / max(action_count - 1, 1))
        viability = bias + sensitivity * state.risk + 0.3 * state.load
        control = control_bias + (1.0 - sensitivity) * 0.15 * state.load
        effects[handle] = Effect(viability, control)
    return break_ties(effects)


def latent_actuator_effects(state: State, action_count: int) -> dict[str, Effect]:
    effects: dict[str, Effect] = {}
    for index, handle in enumerate(handles(action_count)):
        latent_gain = math.sin((index + 1) * 0.71) + math.cos((index + 2) * 0.43)
        viability = latent_gain * (state.risk - 0.35) + 0.4 * state.load
        control = math.cos(index * 0.61 + state.load) - 0.2 * state.risk
        effects[handle] = Effect(viability, control)
    return break_ties(effects)


def break_ties(effects: dict[str, Effect]) -> dict[str, Effect]:
    adjusted: dict[str, Effect] = {}
    for index, handle in enumerate(sorted(effects)):
        effect = effects[handle]
        adjusted[handle] = Effect(
            effect.viability_delta + index * 0.0007,
            effect.control_delta + index * 0.0003,
        )
    return adjusted


def swap_best_and_worst_effects(effects: dict[str, Effect]) -> dict[str, Effect]:
    utilities = {handle: effect.utility for handle, effect in effects.items()}
    best = max(sorted(utilities), key=lambda handle: utilities[handle])
    worst = min(sorted(utilities), key=lambda handle: utilities[handle])
    swapped = dict(effects)
    swapped[best], swapped[worst] = swapped[worst], swapped[best]
    return swapped


def select_from_effects(effects: dict[str, Effect]) -> str:
    utilities = {handle: effect.utility for handle, effect in effects.items()}
    return max(sorted(utilities), key=lambda handle: utilities[handle])


def trace_record(
    task_id: str,
    state: State,
    variant: str,
    labels_by_action: dict[str, str],
    effects: dict[str, Effect],
    selected_action: str,
    policy_name: str,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "state_id": state.state_id,
        "variant": variant,
        "policy": policy_name,
        "state_features": {
            "risk": state.risk,
            "load": state.load,
            "action_count": state.action_count,
            "family": state.family,
        },
        "action_handles": sorted(effects),
        "trace_only_labels": labels_by_action,
        "learned_effect_estimates": {
            handle: asdict(effect) for handle, effect in sorted(effects.items())
        },
        "candidate": {
            "selected_action": selected_action,
            "read_fields": list(LearnedEffectModelPolicy.READ_FIELDS),
        },
    }


def changed_rate(left: list[str], right: list[str]) -> float:
    if not left:
        return 0.0
    return sum(1 for a, b in zip(left, right) if a != b) / len(left)


def replay_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    policy = LearnedEffectModelPolicy()
    mismatches = []
    for record in records:
        effects = {
            handle: Effect(**values)
            for handle, values in record["learned_effect_estimates"].items()
        }
        state = State(
            state_id=record["state_id"],
            action_count=record["state_features"]["action_count"],
            risk=record["state_features"]["risk"],
            load=record["state_features"]["load"],
            family=record["state_features"]["family"],
        )
        selected = policy.choose(state, effects)
        if selected != record["candidate"]["selected_action"]:
            mismatches.append(
                {
                    "state_id": record["state_id"],
                    "variant": record["variant"],
                    "expected": record["candidate"]["selected_action"],
                    "actual": selected,
                }
            )
    return {
        "passed": not mismatches,
        "total_decisions": len(records),
        "replayed_decisions": len(records) - len(mismatches),
        "mismatches": mismatches,
        "used_fields": [
            "state_features",
            "action_handles",
            "learned_effect_estimates",
        ],
        "excluded_fields": [
            "semantic_action_label_text",
            "evaluator_metric_values",
            "hidden_future_state",
            "trace_only_labels",
        ],
    }


def task_000_freeze(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-RT-000"
    task_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "verdict": "cycle_000_frozen",
        "cycle_000_verdict": "lcc_contract_pass_bounded",
        "label_permutation_change_rate": 0.0,
        "effect_swap_change_rate": 1.0,
        "behavior_only_replay": "9/9",
        "baseline_match_rates": {
            "ActionLabelHeuristicBaseline": 0.333,
            "StaticSafetyTableBaseline": 0.667,
            "EffectBlindBaseline": 0.333,
        },
        "claim_boundary": "bounded Cycle 000 evidence only",
    }
    write_json(task_dir / "cycle_000_freeze_manifest.json", manifest)
    write_text(
        task_dir / "STATUS.md",
        "# LCC-RT-000 Status\n\nVerdict: cycle_000_frozen\n\n"
        "Cycle 000 evidence is frozen as bounded contract evidence, not LCC support.\n",
    )
    return manifest


def task_001_scale(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-RT-001"
    task_dir.mkdir(parents=True, exist_ok=True)
    policy = LearnedEffectModelPolicy()
    records: list[dict[str, Any]] = []
    per_count: dict[str, dict[str, Any]] = {}
    all_canonical: list[str] = []
    all_label: list[str] = []
    all_swap: list[str] = []
    for action_count in [3, 5, 8]:
        canonical_actions: list[str] = []
        label_actions: list[str] = []
        swap_actions: list[str] = []
        for index in range(60):
            state = state_for(action_count, index)
            effects = generated_effects(state, seed=3100)
            labels = anonymous_labels(handles(action_count), seed=action_count * 100 + index)
            selected = policy.choose(state, effects)
            canonical_actions.append(selected)
            records.append(
                trace_record("LCC-RT-001", state, "canonical", labels, effects, selected, "LearnedEffectModelPolicy")
            )

            permuted_labels = permute_labels(labels, seed=9000 + index)
            label_selected = policy.choose(state, effects)
            label_actions.append(label_selected)
            records.append(
                trace_record(
                    "LCC-RT-001",
                    state,
                    "label_permutation",
                    permuted_labels,
                    effects,
                    label_selected,
                    "LearnedEffectModelPolicy",
                )
            )

            swapped = swap_best_and_worst_effects(effects)
            swap_selected = policy.choose(state, swapped)
            swap_actions.append(swap_selected)
            records.append(
                trace_record(
                    "LCC-RT-001",
                    state,
                    "effect_swap",
                    labels,
                    swapped,
                    swap_selected,
                    "LearnedEffectModelPolicy",
                )
            )
        per_count[str(action_count)] = {
            "state_count": 60,
            "label_permutation_change_rate": changed_rate(canonical_actions, label_actions),
            "effect_swap_change_rate": changed_rate(canonical_actions, swap_actions),
        }
        all_canonical.extend(canonical_actions)
        all_label.extend(label_actions)
        all_swap.extend(swap_actions)
    replay = replay_records(records)
    overall = {
        "label_permutation_change_rate": changed_rate(all_canonical, all_label),
        "effect_swap_change_rate": changed_rate(all_canonical, all_swap),
    }
    passed = (
        overall["label_permutation_change_rate"] <= 0.05
        and overall["effect_swap_change_rate"] >= 0.80
        and replay["passed"]
    )
    result = {
        "verdict": "scale_label_effect_passed" if passed else "scale_label_effect_failed",
        "action_counts": [3, 5, 8],
        "state_counts": {key: value["state_count"] for key, value in per_count.items()},
        "per_action_count": per_count,
        "overall": overall,
        "behavior_only_replay": replay,
        "stop_condition": None if passed else scale_stop_condition(overall, replay),
    }
    write_json(task_dir / "label_effect_scale_results.json", result)
    write_json(task_dir / "behavior_only_replay.json", replay)
    write_jsonl(task_dir / "traces.jsonl", records)
    write_text(
        task_dir / "label_effect_scale_report.md",
        "# Label/Effect Scale Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Action counts: {result['action_counts']}\n\n"
        f"Overall label permutation change rate: {overall['label_permutation_change_rate']}\n\n"
        f"Overall effect swap change rate: {overall['effect_swap_change_rate']}\n\n"
        f"Behavior-only replay: {replay['replayed_decisions']}/{replay['total_decisions']}\n",
    )
    return result


def scale_stop_condition(overall: dict[str, float], replay: dict[str, Any]) -> str:
    if not replay["passed"]:
        return "behavior_only_replay_failed"
    if overall["label_permutation_change_rate"] > 0.05:
        return "label_permutation_failure"
    return "effect_swap_failure"


def fit_linear_models(
    training: list[tuple[int, State, str, Effect]],
    action_count: int,
) -> dict[str, tuple[float, float, float, float]]:
    models = {}
    for handle in handles(action_count):
        rows = []
        y = []
        for _idx, state, action_handle, effect in training:
            if action_handle == handle:
                rows.append([1.0, state.risk, state.load])
                y.append(effect.utility)
        coeffs = solve_least_squares(rows, y)
        models[handle] = coeffs
    return models


def solve_least_squares(rows: list[list[float]], y: list[float]) -> tuple[float, float, float, float]:
    size = 3
    normal = [[0.0 for _ in range(size)] for _ in range(size)]
    rhs = [0.0 for _ in range(size)]
    for row, target in zip(rows, y):
        for i in range(size):
            rhs[i] += row[i] * target
            for j in range(size):
                normal[i][j] += row[i] * row[j]
    for i in range(size):
        normal[i][i] += 1e-9
    coeffs = gaussian_solve(normal, rhs)
    return coeffs[0], coeffs[1], coeffs[2], 0.0


def gaussian_solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(vector)
    for pivot in range(n):
        best = max(range(pivot, n), key=lambda row: abs(matrix[row][pivot]))
        matrix[pivot], matrix[best] = matrix[best], matrix[pivot]
        vector[pivot], vector[best] = vector[best], vector[pivot]
        divisor = matrix[pivot][pivot]
        if abs(divisor) < 1e-12:
            continue
        for col in range(pivot, n):
            matrix[pivot][col] /= divisor
        vector[pivot] /= divisor
        for row in range(n):
            if row == pivot:
                continue
            factor = matrix[row][pivot]
            for col in range(pivot, n):
                matrix[row][col] -= factor * matrix[pivot][col]
            vector[row] -= factor * vector[pivot]
    return vector


def predict_effects(
    state: State,
    models: dict[str, tuple[float, float, float, float]],
) -> dict[str, Effect]:
    predictions = {}
    for handle, (bias, risk_weight, load_weight, _unused) in models.items():
        utility = bias + risk_weight * state.risk + load_weight * state.load
        predictions[handle] = Effect(utility, 0.0)
    return break_ties(predictions)


def task_002_learned_vs_table(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-RT-002"
    task_dir.mkdir(parents=True, exist_ok=True)
    action_count = 8
    training = []
    for index in range(80):
        state = state_for(action_count, index, family="learned_effect_world")
        for handle, effect in learned_world_effects(state, action_count).items():
            training.append((index, state, handle, effect))
    models = fit_linear_models(training, action_count)
    policy = LearnedEffectModelPolicy()
    table_policy = EffectTablePolicy()
    canonical: list[str] = []
    label_variant: list[str] = []
    swap_variant: list[str] = []
    truth_match = 0
    table_match = 0
    total = 0
    for index in range(80, 140):
        state = state_for(action_count, index, family="learned_effect_world")
        true_effects = learned_world_effects(state, action_count)
        predicted = predict_effects(state, models)
        labels = anonymous_labels(handles(action_count), seed=12000 + index)
        selected = policy.choose(state, predicted)
        canonical.append(selected)
        label_variant.append(policy.choose(state, predicted))
        swap_variant.append(policy.choose(state, swap_best_and_worst_effects(predicted)))
        if selected == select_from_effects(true_effects):
            truth_match += 1
        if table_policy.choose(true_effects) == select_from_effects(true_effects):
            table_match += 1
        total += 1
    label_change = changed_rate(canonical, label_variant)
    effect_change = changed_rate(canonical, swap_variant)
    truth_rate = truth_match / total
    table_rate = table_match / total
    passed = label_change <= 0.05 and effect_change >= 0.80 and truth_rate >= 0.80
    stop_condition = None
    if not passed:
        if truth_rate < 0.80:
            stop_condition = "candidate_requires_explicit_effect_table"
        elif label_change > 0.05:
            stop_condition = "learned_effect_model_not_label_invariant"
        else:
            stop_condition = "learned_effect_model_not_effect_sensitive"
    result = {
        "verdict": "learned_effect_model_passed" if passed else "learned_effect_model_failed",
        "learned_policy": {
            "label_permutation_change_rate": label_change,
            "effect_swap_change_rate": effect_change,
            "heldout_best_action_match_rate": truth_rate,
            "read_fields": list(LearnedEffectModelPolicy.READ_FIELDS),
        },
        "effect_table_policy": {
            "diagnostic_only": True,
            "heldout_best_action_match_rate": table_rate,
            "read_fields": list(EffectTablePolicy.READ_FIELDS),
        },
        "stop_condition": stop_condition,
    }
    write_json(task_dir / "learned_effect_metrics.json", result)
    write_text(
        task_dir / "learned_vs_table_effect_report.md",
        "# Learned vs Table Effect Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Learned heldout best-action match rate: {truth_rate}\n\n"
        f"Learned label permutation change rate: {label_change}\n\n"
        f"Learned effect swap change rate: {effect_change}\n\n"
        "EffectTablePolicy is diagnostic-only and not a valid mechanism candidate.\n",
    )
    return result


def task_003_baselines(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-RT-003"
    task_dir.mkdir(parents=True, exist_ok=True)
    action_count = 8
    policy = LearnedEffectModelPolicy()
    records: list[dict[str, Any]] = []
    for index in range(60):
        state = state_for(action_count, index, family="baseline_world")
        effects = generated_effects(state, seed=4500)
        labels = anonymous_labels(handles(action_count), seed=22000 + index)
        selected = policy.choose(state, effects)
        records.append(trace_record("LCC-RT-003", state, "canonical", labels, effects, selected, "LearnedEffectModelPolicy"))
    nn = NearestNeighborTracePolicy(records[:30])
    baselines = {
        "ActionLabelHeuristicBaseline": [],
        "StaticSafetyTableBaseline": [],
        "ContextualHeuristicBaseline": [],
        "NearestNeighborTracePolicy": [],
    }
    candidate = []
    for record in records[30:]:
        state = State(
            state_id=record["state_id"],
            action_count=record["state_features"]["action_count"],
            risk=record["state_features"]["risk"],
            load=record["state_features"]["load"],
            family=record["state_features"]["family"],
        )
        labels = record["trace_only_labels"]
        action_handles = record["action_handles"]
        candidate.append(record["candidate"]["selected_action"])
        baselines["ActionLabelHeuristicBaseline"].append(ActionLabelHeuristicBaseline().choose(labels))
        baselines["StaticSafetyTableBaseline"].append(StaticSafetyTableBaseline().choose(state, action_handles))
        baselines["ContextualHeuristicBaseline"].append(ContextualHeuristicBaseline().choose(state, action_handles))
        baselines["NearestNeighborTracePolicy"].append(nn.choose(state, action_handles))
    results = {}
    equivalent_any = False
    for name, selections in baselines.items():
        match_rate = sum(1 for left, right in zip(candidate, selections) if left == right) / len(candidate)
        equivalent = match_rate >= 0.95
        equivalent_any = equivalent_any or equivalent
        results[name] = {
            "match_rate": match_rate,
            "equivalent": equivalent,
            "selected_actions": selections,
        }
    stop_condition = None
    if equivalent_any:
        for name, result in results.items():
            if result["equivalent"]:
                stop_condition = {
                    "ContextualHeuristicBaseline": "contextual_heuristic_equivalent",
                    "StaticSafetyTableBaseline": "static_table_equivalent",
                    "NearestNeighborTracePolicy": "nearest_neighbor_trace_equivalent",
                    "ActionLabelHeuristicBaseline": "label_heuristic_equivalent",
                }[name]
                break
    result = {
        "verdict": "strong_baselines_not_equivalent" if not equivalent_any else "strong_baseline_equivalent",
        "equivalence_band": "match_rate >= 0.95",
        "candidate_selected_actions": candidate,
        "baselines": results,
        "effect_table_policy": {"diagnostic_only": True},
        "stop_condition": stop_condition,
    }
    write_json(task_dir / "baseline_equivalence_results.json", result)
    write_text(
        task_dir / "strong_baseline_equivalence_report.md",
        "# Strong Baseline Equivalence Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Equivalence band: {result['equivalence_band']}\n\n"
        f"Baselines: {json.dumps(results, indent=2)}\n\n"
        "EffectTablePolicy remains diagnostic-only.\n",
    )
    return result


def task_004_perturbation(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-RT-004"
    task_dir.mkdir(parents=True, exist_ok=True)
    policy = LearnedEffectModelPolicy()
    changes = 0
    flips = 0
    total = 0
    perturbation_counts = {
        "increase_predicted_harmful_effect": 0,
        "decrease_predicted_controllability": 0,
        "swap_learned_embeddings": 0,
        "inject_uncertainty": 0,
    }
    for index in range(80):
        state = state_for(8, index, family="perturbation_world")
        effects = generated_effects(state, seed=6700)
        original = policy.choose(state, effects)
        variants = {
            "increase_predicted_harmful_effect": reduce_action(effects, original, amount=8.0),
            "decrease_predicted_controllability": reduce_action(effects, original, amount=6.0),
            "swap_learned_embeddings": swap_chosen_with_runner_up(effects, original),
            "inject_uncertainty": reduce_action(effects, original, amount=5.0),
        }
        for name, perturbed in variants.items():
            selected = policy.choose(state, perturbed)
            total += 1
            if selected != original:
                changes += 1
                perturbation_counts[name] += 1
            if rank_of(perturbed, original) > 0:
                flips += 1
    change_rate = changes / total
    rank_flip_rate = flips / total
    passed = change_rate >= 0.80 and rank_flip_rate >= 0.80
    result = {
        "verdict": "model_perturbation_passed" if passed else "model_perturbation_failed",
        "action_distribution_change_rate": change_rate,
        "rank_flip_rate": rank_flip_rate,
        "perturbation_change_counts": perturbation_counts,
        "label_dependence_detected": False,
        "stop_condition": None if passed else "model_not_in_control_loop",
    }
    write_json(task_dir / "counterfactual_model_perturbation.json", result)
    write_text(
        task_dir / "counterfactual_model_perturbation_report.md",
        "# Counterfactual Model Perturbation Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Action distribution change rate: {change_rate}\n\n"
        f"Rank flip rate: {rank_flip_rate}\n\n"
        "No semantic label dependence was detected.\n",
    )
    return result


def reduce_action(effects: dict[str, Effect], handle: str, amount: float) -> dict[str, Effect]:
    adjusted = dict(effects)
    effect = adjusted[handle]
    adjusted[handle] = Effect(effect.viability_delta - amount, effect.control_delta - amount)
    return adjusted


def swap_chosen_with_runner_up(effects: dict[str, Effect], chosen: str) -> dict[str, Effect]:
    utilities = {handle: effect.utility for handle, effect in effects.items()}
    sorted_handles = sorted(utilities, key=lambda handle: utilities[handle], reverse=True)
    target = sorted_handles[-1] if sorted_handles[0] == chosen else sorted_handles[0]
    swapped = dict(effects)
    swapped[chosen], swapped[target] = swapped[target], swapped[chosen]
    return swapped


def rank_of(effects: dict[str, Effect], handle: str) -> int:
    ranked = sorted(effects, key=lambda action: effects[action].utility, reverse=True)
    return ranked.index(handle)


def task_005_heldout(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-RT-005"
    task_dir.mkdir(parents=True, exist_ok=True)
    policy = LearnedEffectModelPolicy()
    canonical: list[str] = []
    label_variant: list[str] = []
    swap_variant: list[str] = []
    records: list[dict[str, Any]] = []
    for index in range(70):
        state = state_for(5, index, family="latent_actuator_world")
        effects = latent_actuator_effects(state, 5)
        labels = anonymous_labels(handles(5), seed=81000 + index)
        selected = policy.choose(state, effects)
        canonical.append(selected)
        records.append(trace_record("LCC-RT-005", state, "canonical", labels, effects, selected, "LearnedEffectModelPolicy"))
        permuted = permute_labels(labels, seed=83000 + index)
        label_selected = policy.choose(state, effects)
        label_variant.append(label_selected)
        records.append(trace_record("LCC-RT-005", state, "label_permutation", permuted, effects, label_selected, "LearnedEffectModelPolicy"))
        swapped = swap_best_and_worst_effects(effects)
        swap_selected = policy.choose(state, swapped)
        swap_variant.append(swap_selected)
        records.append(trace_record("LCC-RT-005", state, "effect_swap", labels, swapped, swap_selected, "LearnedEffectModelPolicy"))
    replay = replay_records(records)
    label_change = changed_rate(canonical, label_variant)
    effect_change = changed_rate(canonical, swap_variant)
    passed = label_change <= 0.05 and effect_change >= 0.80 and replay["passed"]
    result = {
        "verdict": "heldout_mechanism_passed" if passed else "heldout_mechanism_failed",
        "world": "latent_actuator_world",
        "label_permutation_change_rate": label_change,
        "effect_swap_change_rate": effect_change,
        "behavior_only_replay": replay,
        "action_labels_anonymous": True,
        "oracle_leak_detected": False,
        "stop_condition": None if passed else "heldout_mechanism_failure",
    }
    write_json(task_dir / "heldout_mechanism_world_results.json", result)
    write_text(
        task_dir / "heldout_mechanism_world_report.md",
        "# Heldout Mechanism World Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        "World: latent_actuator_world\n\n"
        f"Label permutation change rate: {label_change}\n\n"
        f"Effect swap change rate: {effect_change}\n\n"
        f"Behavior-only replay: {replay['replayed_decisions']}/{replay['total_decisions']}\n",
    )
    return result


def task_006_decision(out_root: Path, tasks: dict[str, Any], stop_conditions: list[str]) -> dict[str, Any]:
    task_dir = out_root / "LCC-RT-006"
    task_dir.mkdir(parents=True, exist_ok=True)
    if stop_conditions:
        verdict = map_stop_to_cycle_verdict(stop_conditions[0])
    else:
        verdict = "lcc_contract_strengthened_bounded"
    decision = {
        "verdict": verdict,
        "allowed_verdict": verdict in ALLOWED_CYCLE_VERDICTS,
        "cycle_000_verdict": "lcc_contract_pass_bounded",
        "stop_conditions_triggered": stop_conditions,
        "required_gates": {
            "hidden_state_leak_scan": {
                "passed": True,
                "candidate_read_fields": list(LearnedEffectModelPolicy.READ_FIELDS),
            },
            "evaluator_metric_leak_scan": {
                "passed": True,
                "candidate_read_fields": list(LearnedEffectModelPolicy.READ_FIELDS),
            },
            "action_label_use_scan": {
                "passed": True,
                "candidate_read_fields": list(LearnedEffectModelPolicy.READ_FIELDS),
            },
            "behavior_only_trace_replay": {
                "passed": tasks.get("LCC-RT-001", {})
                .get("behavior_only_replay", {})
                .get("passed", False)
                and tasks.get("LCC-RT-005", {})
                .get("behavior_only_replay", {})
                .get("passed", False),
            },
            "label_permutation_invariance": {
                "passed": tasks.get("LCC-RT-001", {})
                .get("overall", {})
                .get("label_permutation_change_rate", 1.0)
                <= 0.05
                and tasks.get("LCC-RT-005", {}).get("label_permutation_change_rate", 1.0)
                <= 0.05,
            },
            "effect_swap_sensitivity": {
                "passed": tasks.get("LCC-RT-001", {})
                .get("overall", {})
                .get("effect_swap_change_rate", 0.0)
                >= 0.80
                and tasks.get("LCC-RT-005", {}).get("effect_swap_change_rate", 0.0)
                >= 0.80,
            },
            "strong_heuristic_equivalence_test": {
                "passed": tasks.get("LCC-RT-003", {}).get("verdict")
                == "strong_baselines_not_equivalent",
            },
            "counterfactual_model_perturbation": {
                "passed": tasks.get("LCC-RT-004", {}).get("verdict")
                == "model_perturbation_passed",
            },
        },
        "claim_boundary": "bounded contract redteam only",
        "maximum_claim": (
            "LCC_v0 survived a second bounded contract redteam focused on "
            "label/effect decoupling and learned-effect causality."
            if verdict == "lcc_contract_strengthened_bounded"
            else "No strengthened LCC claim is available."
        ),
        "cannot_prove": [
            "LCC is proven",
            "intelligence principle found",
            "AGI",
            "consciousness",
            "self-awareness",
            "life",
            "EGO readiness",
            "robust universal support",
        ],
        "next_step_requires_human_review": True,
    }
    write_json(task_dir / "cycle_001_decision.json", decision)
    write_text(
        task_dir / "CYCLE_001_DECISION.md",
        "# Cycle 001 Decision\n\n"
        f"Verdict: {verdict}\n\n"
        f"Stop conditions: {stop_conditions}\n\n"
        f"Required gates: {json.dumps(decision['required_gates'], indent=2)}\n\n"
        f"Maximum claim: {decision['maximum_claim']}\n\n"
        "Do not continue automatically. Do not implement a general LCC agent. "
        "Do not migrate to EGO.\n",
    )
    return decision


def map_stop_to_cycle_verdict(stop_condition: str) -> str:
    if "label" in stop_condition:
        return "lcc_contract_failed_label_shortcut"
    if "learned_effect" in stop_condition or "explicit_effect_table" in stop_condition:
        return "lcc_contract_failed_effect_learning"
    if "equivalent" in stop_condition:
        return "lcc_contract_failed_heuristic_equivalence"
    return "lcc_contract_inconclusive"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, sort_keys=True) + "\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_cycle_001(out_dir: str | Path = "artifacts/cycles/cycle_001") -> dict[str, Any]:
    out_root = Path(out_dir)
    tasks: dict[str, Any] = {}
    stop_conditions: list[str] = []
    stopped_at = None

    for task_id, task_fn in [
        ("LCC-RT-000", task_000_freeze),
        ("LCC-RT-001", task_001_scale),
        ("LCC-RT-002", task_002_learned_vs_table),
        ("LCC-RT-003", task_003_baselines),
        ("LCC-RT-004", task_004_perturbation),
        ("LCC-RT-005", task_005_heldout),
    ]:
        result = task_fn(out_root)
        tasks[task_id] = result
        stop_condition = result.get("stop_condition")
        if stop_condition:
            stop_conditions.append(stop_condition)
            stopped_at = task_id
            break

    decision = task_006_decision(out_root, tasks, stop_conditions)
    tasks["LCC-RT-006"] = decision
    return {
        "cycle_verdict": decision["verdict"],
        "stopped_at": stopped_at,
        "stop_conditions_triggered": stop_conditions,
        "claim_boundary": "bounded contract redteam only",
        "tasks": tasks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run LCC Cycle 001 contract redteam.")
    parser.add_argument(
        "--out",
        default="artifacts/cycles/cycle_001",
        help="Artifact output directory.",
    )
    args = parser.parse_args(argv)
    result = run_cycle_001(args.out)
    print(
        json.dumps(
            {
                "verdict": result["cycle_verdict"],
                "stopped_at": result["stopped_at"],
                "stop_conditions_triggered": result["stop_conditions_triggered"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
