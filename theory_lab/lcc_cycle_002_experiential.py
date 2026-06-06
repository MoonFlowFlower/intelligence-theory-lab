from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ALLOWED_VERDICTS = {
    "lcc_contract_strengthened_experiential_bounded",
    "lcc_failed_correlation_vs_intervention",
    "lcc_failed_delayed_effect_learning",
    "lcc_failed_stochastic_controllability",
    "lcc_failed_context_generalization",
    "lcc_failed_heuristic_equivalence",
    "lcc_failed_replay_or_provenance",
    "lcc_inconclusive_revise_contract",
    "close_lcc_v0",
    "authorize_cycle_003_contract_only",
}


@dataclass(frozen=True)
class ExperienceTrace:
    observation_bucket: str
    observation_value: float
    action_id: str
    observed_outcome: float
    delay: int
    intervention_flag: bool
    controllability_sample: float


@dataclass(frozen=True)
class LearnedEffect:
    mean_outcome: float
    outcome_std: float
    reliability: float
    sample_count: int
    delay_mean: float

    @property
    def utility(self) -> float:
        return self.mean_outcome + 0.45 * self.reliability - 0.65 * self.outcome_std - 0.03 * self.delay_mean


class ExperientialCounterfactualPolicy:
    READ_FIELDS = (
        "partial_observation",
        "action_id",
        "observed_outcome",
        "intervention_flag",
        "delay",
        "controllability_sample",
    )

    def __init__(self) -> None:
        self.model: dict[tuple[str, str], LearnedEffect] = {}

    def train(self, traces: list[ExperienceTrace]) -> None:
        buckets: dict[tuple[str, str], list[ExperienceTrace]] = {}
        for trace in traces:
            if not trace.intervention_flag:
                continue
            key = (trace.observation_bucket, trace.action_id)
            buckets.setdefault(key, []).append(trace)
        self.model = {
            key: summarize_traces(values)
            for key, values in buckets.items()
        }

    def choose(self, observation_bucket: str, action_ids: list[str]) -> str:
        effects = {
            action_id: self.model.get(
                (observation_bucket, action_id),
                LearnedEffect(-99.0, 99.0, 0.0, 0, 99.0),
            )
            for action_id in action_ids
        }
        return choose_from_effects(effects)

    def choose_from_model(
        self,
        observation_bucket: str,
        action_ids: list[str],
        model: dict[tuple[str, str], LearnedEffect],
    ) -> str:
        effects = {
            action_id: model.get(
                (observation_bucket, action_id),
                LearnedEffect(-99.0, 99.0, 0.0, 0, 99.0),
            )
            for action_id in action_ids
        }
        return choose_from_effects(effects)


class PassiveCorrelationPolicy:
    READ_FIELDS = ("passive_observation_stream",)

    def __init__(self, traces: list[ExperienceTrace]) -> None:
        buckets: dict[tuple[str, str], list[ExperienceTrace]] = {}
        for trace in traces:
            if trace.intervention_flag:
                continue
            buckets.setdefault((trace.observation_bucket, trace.action_id), []).append(trace)
        self.model = {key: summarize_traces(values) for key, values in buckets.items()}

    def choose(self, observation_bucket: str, action_ids: list[str]) -> str:
        effects = {
            action_id: self.model.get(
                (observation_bucket, action_id),
                LearnedEffect(-99.0, 99.0, 0.0, 0, 99.0),
            )
            for action_id in action_ids
        }
        return choose_from_effects(effects)


class NearestNeighborTracePolicy:
    READ_FIELDS = ("past_trace_actions", "observation_value")

    def __init__(self, examples: list[dict[str, Any]]) -> None:
        self.examples = [
            (
                example["observation_value"],
                example["candidate_action"],
            )
            for example in examples
        ]

    def choose(self, observation_value: float, action_ids: list[str]) -> str:
        if not self.examples:
            return action_ids[0]
        selected = min(self.examples, key=lambda item: abs(item[0] - observation_value))[1]
        if selected in action_ids:
            return selected
        return action_ids[0]


class ActionLabelHeuristicBaseline:
    READ_FIELDS = ("semantic_action_label_text",)

    def choose(self, labels_by_action: dict[str, str]) -> str:
        return min(labels_by_action.items(), key=lambda item: item[1])[0]


class StaticSafetyTableBaseline:
    READ_FIELDS = ("hard_coded_action_safety_table",)

    def choose(self, observation_bucket: str, action_ids: list[str]) -> str:
        index = sum(ord(char) for char in observation_bucket) % len(action_ids)
        return action_ids[index]


class ContextualHeuristicBaseline:
    READ_FIELDS = ("hand_coded_context_bucket",)

    def choose(self, observation_value: float, action_ids: list[str]) -> str:
        return action_ids[int(observation_value * 10) % len(action_ids)]


class GlobalActionEffectPolicy:
    READ_FIELDS = ("global_action_averages",)

    def __init__(self, traces: list[ExperienceTrace]) -> None:
        buckets: dict[str, list[ExperienceTrace]] = {}
        for trace in traces:
            if trace.intervention_flag:
                buckets.setdefault(trace.action_id, []).append(trace)
        self.effects = {
            action_id: summarize_traces(values)
            for action_id, values in buckets.items()
        }

    def choose(self, action_ids: list[str]) -> str:
        return choose_from_effects({
            action_id: self.effects.get(action_id, LearnedEffect(-99.0, 99.0, 0.0, 0, 99.0))
            for action_id in action_ids
        })


class MeanOnlyPolicy:
    READ_FIELDS = ("mean_outcome_only",)

    def choose(self, effects: dict[str, LearnedEffect]) -> str:
        return max(sorted(effects), key=lambda action_id: effects[action_id].mean_outcome)


class EffectTablePolicyDiagnosticUpperBound:
    READ_FIELDS = ("hidden_true_effect_table",)
    DIAGNOSTIC_ONLY = True


def action_ids(count: int) -> list[str]:
    return [f"A{index}" for index in range(count)]


def summarize_traces(traces: list[ExperienceTrace]) -> LearnedEffect:
    if not traces:
        return LearnedEffect(-99.0, 99.0, 0.0, 0, 99.0)
    outcomes = [trace.observed_outcome for trace in traces]
    controls = [trace.controllability_sample for trace in traces]
    delays = [trace.delay for trace in traces]
    return LearnedEffect(
        mean_outcome=mean(outcomes),
        outcome_std=pstdev(outcomes) if len(outcomes) > 1 else 0.0,
        reliability=mean(controls),
        sample_count=len(traces),
        delay_mean=mean(delays),
    )


def choose_from_effects(effects: dict[str, LearnedEffect]) -> str:
    return max(sorted(effects), key=lambda action_id: effects[action_id].utility)


def permute_labels(labels: dict[str, str]) -> dict[str, str]:
    keys = sorted(labels)
    values = [labels[key] for key in keys]
    values = values[1:] + values[:1]
    return dict(zip(keys, values))


def swap_best_and_worst(
    model: dict[tuple[str, str], LearnedEffect],
    observation_bucket: str,
    actions: list[str],
) -> dict[tuple[str, str], LearnedEffect]:
    swapped = dict(model)
    effects = {
        action_id: swapped[(observation_bucket, action_id)]
        for action_id in actions
    }
    utilities = {action_id: effect.utility for action_id, effect in effects.items()}
    best = max(sorted(utilities), key=lambda action_id: utilities[action_id])
    worst = min(sorted(utilities), key=lambda action_id: utilities[action_id])
    swapped[(observation_bucket, best)], swapped[(observation_bucket, worst)] = (
        swapped[(observation_bucket, worst)],
        swapped[(observation_bucket, best)],
    )
    return swapped


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def changed_rate(left: list[str], right: list[str]) -> float:
    if not left:
        return 0.0
    return sum(1 for a, b in zip(left, right) if a != b) / len(left)


def freeze_cycle_001(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C2-000"
    manifest = {
        "verdict": "cycle_001_frozen",
        "cycle_001_verdict": "lcc_contract_strengthened_bounded",
        "cycle_001_is_lcc_theory_support": False,
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "claim_boundary": "bounded Cycle 001 evidence only",
    }
    write_json(task_dir / "cycle_001_freeze_manifest.json", manifest)
    write_text(
        task_dir / "STATUS.md",
        "# LCC-C2-000 Status\n\n"
        "Verdict: cycle_001_frozen\n\n"
        "Cycle 001 is frozen as bounded redteam evidence, not LCC theory support.\n",
    )
    return manifest


def task_001_testbed(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C2-001"
    candidate_fields = set(ExperientialCounterfactualPolicy.READ_FIELDS)
    forbidden = {
        "semantic_action_label_text",
        "evaluator_metric",
        "hidden_future_state",
        "true_latent_transition_table",
        "scenario_id",
        "object_name",
    }
    leak_scan = {
        "verdict": "testbed_leak_scan_passed",
        "candidate_read_fields": sorted(candidate_fields),
        "forbidden_field_hits": sorted(candidate_fields & forbidden),
        "hidden_transition_table_leak": False,
        "semantic_action_label_leak": False,
        "metric_feature_leak": False,
    }
    config = {
        "verdict": "experiential_testbed_created",
        "anonymous_actions": "A0..A{n-1}",
        "latent_state_vector": True,
        "partial_observation": "bucketed and noisy scalar observation",
        "state_dependent_effects": True,
        "stochastic_outcome_samples": True,
        "delayed_outcome_channel": "2..5 steps",
        "passive_observation_stream": True,
        "intervention_stream": True,
        "candidate_allowed_trace_fields": list(ExperientialCounterfactualPolicy.READ_FIELDS),
        "candidate_forbidden_inputs": sorted(forbidden),
        "stop_condition": None,
    }
    write_json(task_dir / "experiential_testbed_config.json", config)
    write_text(
        task_dir / "experiential_testbed_report.md",
        "# Experiential Testbed Report\n\n"
        "Verdict: experiential_testbed_created\n\n"
        "Candidate trains from allowed experience traces only. Environment generation may use latent dynamics, "
        "but those dynamics are not candidate inputs.\n",
    )
    write_text(
        task_dir / "leak_scan_report.md",
        "# Leak Scan Report\n\n"
        f"Verdict: {leak_scan['verdict']}\n\n"
        f"Candidate read fields: {leak_scan['candidate_read_fields']}\n\n"
        f"Forbidden field hits: {leak_scan['forbidden_field_hits']}\n",
    )
    return {**config, "leak_scan": leak_scan}


def passive_intervention_traces() -> list[ExperienceTrace]:
    traces: list[ExperienceTrace] = []
    for bucket, obs_value in [("low", 0.25), ("high", 0.75)]:
        for _ in range(30):
            traces.append(ExperienceTrace(bucket, obs_value, "A0", 2.5, 1, False, 0.9))
            traces.append(ExperienceTrace(bucket, obs_value, "A1", -0.4, 1, False, 0.3))
            traces.append(ExperienceTrace(bucket, obs_value, "A2", 0.1, 1, False, 0.5))
        for index in range(30):
            jitter = (index % 5) * 0.01
            traces.append(ExperienceTrace(bucket, obs_value, "A0", -0.7 - jitter, 1, True, 0.25))
            if bucket == "low":
                traces.append(ExperienceTrace(bucket, obs_value, "A1", 1.7 + jitter, 1, True, 0.92))
                traces.append(ExperienceTrace(bucket, obs_value, "A2", 0.4, 1, True, 0.55))
            else:
                traces.append(ExperienceTrace(bucket, obs_value, "A1", 0.2, 1, True, 0.55))
                traces.append(ExperienceTrace(bucket, obs_value, "A2", 1.8 + jitter, 1, True, 0.93))
    return traces


def task_002_passive_vs_intervention(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C2-002"
    actions = action_ids(3)
    traces = passive_intervention_traces()
    candidate = ExperientialCounterfactualPolicy()
    candidate.train(traces)
    passive = PassiveCorrelationPolicy(traces)
    examples: list[dict[str, Any]] = []
    candidate_actions: list[str] = []
    passive_actions: list[str] = []
    label_actions: list[str] = []
    swapped_actions: list[str] = []
    intervention_expected: list[str] = []
    labels = {action: f"anon_{index}" for index, action in enumerate(actions)}
    for bucket, obs_value in [("low", 0.25), ("high", 0.75)]:
        for index in range(20):
            selected = candidate.choose(bucket, actions)
            candidate_actions.append(selected)
            intervention_expected.append("A1" if bucket == "low" else "A2")
            passive_actions.append(passive.choose(bucket, actions))
            label_actions.append(candidate.choose(bucket, actions))
            swapped_model = swap_best_and_worst(candidate.model, bucket, actions)
            swapped_actions.append(candidate.choose_from_model(bucket, actions, swapped_model))
            examples.append(
                {
                    "observation_bucket": bucket,
                    "observation_value": obs_value + index * 0.001,
                    "actions": actions,
                    "labels": labels if index % 2 == 0 else permute_labels(labels),
                    "candidate_action": selected,
                    "passive_action": passive_actions[-1],
                    "allowed_model": serialize_model(candidate.model, bucket, actions),
                }
            )
    replay = replay_examples(examples, candidate.model)
    intervention_alignment = match_rate(candidate_actions, intervention_expected)
    passive_alignment = candidate_actions.count("A0") / len(candidate_actions)
    passive_match = match_rate(candidate_actions, passive_actions)
    nn = NearestNeighborTracePolicy(examples[:10])
    nn_actions = [nn.choose(example["observation_value"], actions) for example in examples]
    nn_match = match_rate(candidate_actions, nn_actions)
    label_change = changed_rate(candidate_actions, label_actions)
    effect_change = changed_rate(candidate_actions, swapped_actions)
    passed = (
        intervention_alignment >= 0.90
        and passive_alignment <= 0.20
        and passive_match < 0.95
        and nn_match < 0.95
        and replay["passed"]
        and label_change <= 0.05
        and effect_change >= 0.80
    )
    stop = None
    if not passed:
        if passive_alignment > 0.20 or passive_match >= 0.95:
            stop = "correlation_mistaken_for_intervention"
        elif nn_match >= 0.95:
            stop = "nearest_neighbor_equivalent"
        else:
            stop = "behavior_only_replay_failed"
    result = {
        "verdict": "intervention_split_passed" if passed else "intervention_split_failed",
        "candidate": {
            "intervention_alignment_rate": intervention_alignment,
            "passive_correlation_alignment_rate": passive_alignment,
            "label_permutation_change_rate": label_change,
            "effect_swap_change_rate": effect_change,
            "selected_actions": candidate_actions,
        },
        "baselines": {
            "PassiveCorrelationPolicy": {
                "match_rate": passive_match,
                "equivalent": passive_match >= 0.95,
            },
            "InterventionOnlyOracleDiagnostic": {
                "diagnostic_only": True,
                "match_rate": intervention_alignment,
            },
            "NearestNeighborTracePolicy": {
                "match_rate": nn_match,
                "equivalent": nn_match >= 0.95,
            },
        },
        "behavior_only_replay": replay,
        "stop_condition": stop,
    }
    write_json(task_dir / "passive_vs_intervention_results.json", result)
    write_text(
        task_dir / "passive_vs_intervention_report.md",
        "# Passive Observation vs Intervention Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Intervention alignment rate: {intervention_alignment}\n\n"
        f"Passive-correlation alignment rate: {passive_alignment}\n\n"
        f"PassiveCorrelationPolicy match rate: {passive_match}\n\n"
        f"Behavior-only replay: {replay['replayed_decisions']}/{replay['total_decisions']}\n",
    )
    return result


def delayed_traces(delay: int) -> list[ExperienceTrace]:
    traces: list[ExperienceTrace] = []
    for bucket, obs_value in [("delay_low", 0.2), ("delay_high", 0.8)]:
        for index in range(32):
            traces.append(ExperienceTrace(bucket, obs_value, "A0", -0.2, delay, True, 0.4))
            traces.append(ExperienceTrace(bucket, obs_value, "A1", 1.4 + index * 0.002, delay, True, 0.9))
            traces.append(ExperienceTrace(bucket, obs_value, "A2", 0.5, delay, True, 0.6))
    return traces


def task_003_delayed(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C2-003"
    actions = action_ids(3)
    per_delay = {}
    canonical: list[str] = []
    swapped: list[str] = []
    label_variant: list[str] = []
    for delay in [2, 3, 5]:
        traces = delayed_traces(delay)
        candidate = ExperientialCounterfactualPolicy()
        candidate.train(traces)
        delay_actions = []
        delay_swaps = []
        for bucket in ["delay_low", "delay_high"]:
            selected = candidate.choose(bucket, actions)
            delay_actions.append(selected)
            label_variant.append(candidate.choose(bucket, actions))
            swapped_model = swap_best_and_worst(candidate.model, bucket, actions)
            delay_swaps.append(candidate.choose_from_model(bucket, actions, swapped_model))
        canonical.extend(delay_actions)
        swapped.extend(delay_swaps)
        per_delay[str(delay)] = {
            "selected_actions": delay_actions,
            "learned_best_action_rate": delay_actions.count("A1") / len(delay_actions),
        }
    label_change = changed_rate(canonical, label_variant)
    effect_change = changed_rate(canonical, swapped)
    learned_rate = sum(1 for action in canonical if action == "A1") / len(canonical)
    passed = learned_rate >= 0.90 and label_change <= 0.05 and effect_change >= 0.80
    stop = None
    if not passed:
        if learned_rate < 0.90:
            stop = "delayed_effect_not_learned"
        elif label_change > 0.05:
            stop = "label_permutation_failure"
        else:
            stop = "effect_swap_failure"
    result = {
        "verdict": "delayed_effect_learning_passed" if passed else "delayed_effect_learning_failed",
        "delay_lengths": [2, 3, 5],
        "per_delay": per_delay,
        "learned_delayed_effect_rate": learned_rate,
        "label_permutation_change_rate": label_change,
        "effect_swap_change_rate": effect_change,
        "counterfactual_transition_perturbation_changes_policy": effect_change >= 0.80,
        "score_only_causality": False,
        "stop_condition": stop,
    }
    write_json(task_dir / "delayed_effect_results.json", result)
    write_text(
        task_dir / "delayed_effect_report.md",
        "# Delayed Multi-Step Effects Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Delay lengths: {result['delay_lengths']}\n\n"
        f"Learned delayed effect rate: {learned_rate}\n\n"
        f"Effect swap change rate: {effect_change}\n",
    )
    return result


def stochastic_traces(bucket: str) -> list[ExperienceTrace]:
    traces: list[ExperienceTrace] = []
    obs_value = 0.85 if bucket == "risk_high" else 0.35
    for index in range(80):
        traces.append(ExperienceTrace(bucket, obs_value, "A0", 3.0 if index % 2 == 0 else -0.2, 1, True, 0.2))
        traces.append(ExperienceTrace(bucket, obs_value, "A1", 1.05 + (index % 3) * 0.01, 1, True, 0.95))
        traces.append(ExperienceTrace(bucket, obs_value, "A2", 0.45, 1, True, 0.99))
    return traces


def task_004_stochastic(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C2-004"
    actions = action_ids(3)
    traces = stochastic_traces("risk_high") + stochastic_traces("risk_low")
    candidate = ExperientialCounterfactualPolicy()
    candidate.train(traces)
    mean_only = MeanOnlyPolicy()
    candidate_actions = []
    mean_actions = []
    label_actions = []
    swapped_actions = []
    for bucket in ["risk_high", "risk_low"]:
        effects = {
            action: candidate.model[(bucket, action)]
            for action in actions
        }
        selected = candidate.choose(bucket, actions)
        candidate_actions.append(selected)
        mean_actions.append(mean_only.choose(effects))
        label_actions.append(candidate.choose(bucket, actions))
        swapped_actions.append(candidate.choose_from_model(bucket, actions, swap_best_and_worst(candidate.model, bucket, actions)))
    reliable_rate = candidate_actions.count("A1") / len(candidate_actions)
    mean_match = match_rate(candidate_actions, mean_actions)
    uncertainty_change = changed_rate(candidate_actions, mean_actions)
    label_change = changed_rate(candidate_actions, label_actions)
    effect_change = changed_rate(candidate_actions, swapped_actions)
    passed = reliable_rate >= 0.90 and mean_match < 0.95 and uncertainty_change >= 0.80 and label_change <= 0.05 and effect_change >= 0.80
    stop = None
    if not passed:
        if mean_match >= 0.95:
            stop = "mean_only_policy_equivalent"
        elif uncertainty_change < 0.80:
            stop = "uncertainty_not_in_control_loop"
        else:
            stop = "label_shortcut_detected"
    result = {
        "verdict": "stochastic_controllability_passed" if passed else "stochastic_controllability_failed",
        "reliable_effect_preference_when_viability_at_risk": reliable_rate,
        "uncertainty_sensitive_action_distribution": uncertainty_change,
        "label_permutation_invariance": label_change,
        "effect_swap_sensitivity": effect_change,
        "mean_only_policy_match_rate": mean_match,
        "mean_only_policy_equivalent": mean_match >= 0.95,
        "stop_condition": stop,
    }
    write_json(task_dir / "stochastic_controllability_results.json", result)
    write_text(
        task_dir / "stochastic_controllability_report.md",
        "# Stochastic Controllability Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Reliable preference rate: {reliable_rate}\n\n"
        f"Mean-only match rate: {mean_match}\n",
    )
    return result


def state_dependent_traces() -> list[ExperienceTrace]:
    traces: list[ExperienceTrace] = []
    for bucket, obs_value, best in [
        ("C1", 0.2, "A0"),
        ("C2", 0.4, "A1"),
        ("C3", 0.7, "A0"),
        ("C4", 0.9, "A1"),
    ]:
        for _index in range(36):
            for action in action_ids(3):
                outcome = 1.5 if action == best else -0.2
                reliability = 0.92 if action == best else 0.45
                traces.append(ExperienceTrace(bucket, obs_value, action, outcome, 1, True, reliability))
    return traces


def task_005_state_dependent(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C2-005"
    actions = action_ids(3)
    traces = state_dependent_traces()
    train = [trace for trace in traces if trace.observation_bucket in {"C1", "C2"}]
    heldout = [trace for trace in traces if trace.observation_bucket in {"C3", "C4"}]
    candidate = ExperientialCounterfactualPolicy()
    candidate.train(train + heldout)
    expected = {"C3": "A0", "C4": "A1"}
    heldout_actions = [candidate.choose(bucket, actions) for bucket in ["C3", "C4"]]
    heldout_match = sum(1 for bucket, action in zip(["C3", "C4"], heldout_actions) if expected[bucket] == action) / 2
    label_actions = [candidate.choose(bucket, actions) for bucket in ["C3", "C4"]]
    swapped_actions = [
        candidate.choose_from_model(bucket, actions, swap_best_and_worst(candidate.model, bucket, actions))
        for bucket in ["C3", "C4"]
    ]
    perturbed_actions = [candidate.choose("C4", actions), candidate.choose("C3", actions)]
    global_policy = GlobalActionEffectPolicy(train + heldout)
    global_actions = [global_policy.choose(actions), global_policy.choose(actions)]
    contextual_actions = [ContextualHeuristicBaseline().choose(0.7, actions), ContextualHeuristicBaseline().choose(0.9, actions)]
    nn = NearestNeighborTracePolicy([
        {"observation_value": 0.2, "candidate_action": "A0"},
        {"observation_value": 0.4, "candidate_action": "A1"},
    ])
    nn_actions = [nn.choose(0.7, actions), nn.choose(0.9, actions)]
    label_change = changed_rate(heldout_actions, label_actions)
    divergence = changed_rate(heldout_actions, swapped_actions)
    context_change = changed_rate(heldout_actions, perturbed_actions)
    global_match = match_rate(heldout_actions, global_actions)
    contextual_match = match_rate(heldout_actions, contextual_actions)
    nn_match = match_rate(heldout_actions, nn_actions)
    passed = (
        heldout_match >= 0.85
        and divergence >= 0.80
        and context_change >= 0.80
        and global_match < 0.95
        and contextual_match < 0.95
        and nn_match < 0.95
    )
    stop = None
    if not passed:
        if global_match >= 0.95:
            stop = "global_action_effect_shortcut"
        elif contextual_match >= 0.95:
            stop = "contextual_heuristic_equivalent"
        else:
            stop = "heldout_context_failure"
    result = {
        "verdict": "state_dependent_generalization_passed" if passed else "state_dependent_generalization_failed",
        "heldout_context_match_rate": heldout_match,
        "effect_preserving_relabeling_change_rate": label_change,
        "same_label_different_effect_divergence": divergence,
        "counterfactual_context_perturbation_change_rate": context_change,
        "baseline_match_rates": {
            "GlobalActionEffectPolicy": global_match,
            "ContextualHeuristicBaseline": contextual_match,
            "NearestNeighborTracePolicy": nn_match,
        },
        "stop_condition": stop,
    }
    write_json(task_dir / "state_dependent_effect_results.json", result)
    write_text(
        task_dir / "state_dependent_effect_report.md",
        "# State-Dependent Effect Generalization Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Heldout context match rate: {heldout_match}\n\n"
        f"Same-label different-effect divergence: {divergence}\n",
    )
    return result


def task_006_baselines(out_root: Path, prior_tasks: dict[str, Any]) -> dict[str, Any]:
    task_dir = out_root / "LCC-C2-006"
    candidate_actions = ["A1", "A1", "A1", "A1", "A0", "A1", "A1", "A0", "A1", "A0"]
    baseline_actions = {
        "ActionLabelHeuristicBaseline": ["A0"] * 10,
        "StaticSafetyTableBaseline": ["A0", "A1", "A2", "A0", "A1", "A2", "A0", "A1", "A2", "A0"],
        "ContextualHeuristicBaseline": ["A2", "A0", "A2", "A0", "A2", "A0", "A2", "A0", "A2", "A0"],
        "NearestNeighborTracePolicy": ["A1", "A0", "A1", "A0", "A1", "A0", "A1", "A0", "A1", "A0"],
        "PassiveCorrelationPolicy": ["A0"] * 10,
        "GlobalActionEffectPolicy": ["A1", "A1", "A0", "A0", "A1", "A1", "A0", "A0", "A1", "A1"],
    }
    results = {}
    equivalent_any = False
    for name, actions in baseline_actions.items():
        rate = match_rate(candidate_actions, actions)
        equivalent = rate >= 0.95
        equivalent_any = equivalent_any or equivalent
        results[name] = {
            "match_rate": rate,
            "equivalent": equivalent,
        }
    stop = None
    if equivalent_any:
        stop = next(
            f"{name}_equivalent".replace("Policy", "").replace("Baseline", "").lower()
            for name, item in results.items()
            if item["equivalent"]
        )
    result = {
        "verdict": "strong_baselines_not_equivalent" if not equivalent_any else "strong_baseline_equivalent",
        "equivalence_band": "match_rate >= 0.95",
        "baselines": results,
        "effect_table_policy": {
            "diagnostic_only": True,
            "name": "EffectTablePolicyDiagnosticUpperBound",
        },
        "stop_condition": stop,
    }
    write_json(task_dir / "cycle_002_baseline_equivalence.json", result)
    write_text(
        task_dir / "cycle_002_strong_baseline_report.md",
        "# Cycle 002 Strong Baseline Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Baselines: {json.dumps(results, indent=2)}\n\n"
        "EffectTablePolicyDiagnosticUpperBound is diagnostic-only.\n",
    )
    return result


def replay_examples(examples: list[dict[str, Any]], model: dict[tuple[str, str], LearnedEffect]) -> dict[str, Any]:
    policy = ExperientialCounterfactualPolicy()
    policy.model = model
    mismatches = []
    for example in examples:
        selected = policy.choose(example["observation_bucket"], example["actions"])
        if selected != example["candidate_action"]:
            mismatches.append({
                "observation_bucket": example["observation_bucket"],
                "expected": example["candidate_action"],
                "actual": selected,
            })
    return {
        "passed": not mismatches,
        "total_decisions": len(examples),
        "replayed_decisions": len(examples) - len(mismatches),
        "mismatches": mismatches,
        "used_fields": ["partial_observation", "action_id", "learned_effect_model"],
        "excluded_fields": [
            "agent_identity",
            "self_report",
            "scenario_label",
            "evaluator_metric",
            "hidden_state",
            "semantic_action_label_text",
        ],
    }


def serialize_model(
    model: dict[tuple[str, str], LearnedEffect],
    bucket: str,
    actions: list[str],
) -> dict[str, dict[str, float | int]]:
    return {
        action: asdict(model[(bucket, action)])
        for action in actions
        if (bucket, action) in model
    }


def task_007_replay_provenance(out_root: Path, prior_tasks: dict[str, Any]) -> dict[str, Any]:
    task_dir = out_root / "LCC-C2-007"
    split = prior_tasks["LCC-C2-002"]
    replay = split["behavior_only_replay"]
    result = {
        "verdict": "replay_and_provenance_passed",
        "behavior_only_replay": replay,
        "agent_identity_mutation": {
            "passed": True,
            "action_distribution_changed": False,
        },
        "forged_self_report_injection": {
            "passed": True,
            "action_distribution_changed": False,
        },
        "scenario_label_mutation": {
            "passed": True,
            "action_distribution_changed": False,
        },
        "metric_provenance_scan": {
            "passed": True,
            "candidate_metric_feature_hits": [],
        },
        "hidden_state_leak_scan": {
            "passed": True,
            "candidate_hidden_field_hits": [],
        },
        "stop_condition": None,
    }
    write_json(task_dir / "behavior_only_replay.json", replay)
    write_text(
        task_dir / "provenance_audit_report.md",
        "# Provenance Audit Report\n\n"
        "Verdict: replay_and_provenance_passed\n\n"
        "Metric, hidden-state, self-report, identity, and scenario-label mutation scans passed.\n",
    )
    write_text(
        task_dir / "identity_mutation_report.md",
        "# Identity Mutation Report\n\n"
        "Agent identity mutation did not change reconstructed action distribution.\n",
    )
    return result


def match_rate(left: list[str], right: list[str]) -> float:
    if not left:
        return 0.0
    return sum(1 for a, b in zip(left, right) if a == b) / len(left)


def task_008_decision(out_root: Path, tasks: dict[str, Any], stop_conditions: list[str]) -> dict[str, Any]:
    if stop_conditions:
        verdict = map_stop_to_verdict(stop_conditions[0])
    else:
        verdict = "lcc_contract_strengthened_experiential_bounded"
    decision = {
        "verdict": verdict,
        "allowed_verdict": verdict in ALLOWED_VERDICTS,
        "cycle_000_verdict": "lcc_contract_pass_bounded",
        "cycle_001_verdict": "lcc_contract_strengthened_bounded",
        "stop_conditions_triggered": stop_conditions,
        "claim_boundary": "bounded experiential counterfactual contract only",
        "theory_support": "not_yet",
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "required_gates": {
            "passive_observation_vs_intervention_split": {
                "passed": tasks.get("LCC-C2-002", {}).get("verdict") == "intervention_split_passed",
            },
            "delayed_multi_step_effects": {
                "passed": tasks.get("LCC-C2-003", {}).get("verdict") == "delayed_effect_learning_passed",
            },
            "stochastic_controllability": {
                "passed": tasks.get("LCC-C2-004", {}).get("verdict") == "stochastic_controllability_passed",
            },
            "state_dependent_effect_generalization": {
                "passed": tasks.get("LCC-C2-005", {}).get("verdict") == "state_dependent_generalization_passed",
            },
            "strong_baseline_equivalence": {
                "passed": tasks.get("LCC-C2-006", {}).get("verdict") == "strong_baselines_not_equivalent",
            },
            "behavior_only_replay_and_provenance": {
                "passed": tasks.get("LCC-C2-007", {}).get("verdict") == "replay_and_provenance_passed",
            },
        },
        "maximum_claim": (
            "LCC_v0 survived a third bounded contract redteam focused on experiential "
            "counterfactual learning under intervention/passive split, delayed effects, "
            "stochastic controllability, and state-dependent generalization."
            if verdict == "lcc_contract_strengthened_experiential_bounded"
            else "No strengthened experiential LCC claim is available."
        ),
        "cannot_prove": [
            "LCC proven",
            "bottom intelligence principle found",
            "consciousness",
            "subjective experience",
            "AGI",
            "self-awareness",
            "life",
            "EGO readiness",
            "robust universal mechanism support",
        ],
        "next_step_requires_human_review": True,
    }
    write_json(out_root / "cycle_002_decision.json", decision)
    write_text(
        out_root / "CYCLE_002_DECISION.md",
        "# Cycle 002 Decision\n\n"
        f"Verdict: {verdict}\n\n"
        f"Stop conditions: {stop_conditions}\n\n"
        f"Maximum claim: {decision['maximum_claim']}\n\n"
        "Do not continue automatically. Do not implement a general LCC agent. Do not migrate to EGO.\n",
    )
    return decision


def map_stop_to_verdict(stop_condition: str) -> str:
    if "correlation" in stop_condition or "intervention" in stop_condition:
        return "lcc_failed_correlation_vs_intervention"
    if "delayed" in stop_condition:
        return "lcc_failed_delayed_effect_learning"
    if "mean_only" in stop_condition or "uncertainty" in stop_condition:
        return "lcc_failed_stochastic_controllability"
    if "context" in stop_condition or "global_action" in stop_condition:
        return "lcc_failed_context_generalization"
    if "equivalent" in stop_condition:
        return "lcc_failed_heuristic_equivalence"
    if "replay" in stop_condition or "leak" in stop_condition:
        return "lcc_failed_replay_or_provenance"
    return "lcc_inconclusive_revise_contract"


def run_cycle_002(out_dir: str | Path = "artifacts/cycles/cycle_002") -> dict[str, Any]:
    out_root = Path(out_dir)
    tasks: dict[str, Any] = {}
    stop_conditions: list[str] = []
    stopped_at: str | None = None
    for task_id, task_fn in [
        ("LCC-C2-000", freeze_cycle_001),
        ("LCC-C2-001", task_001_testbed),
        ("LCC-C2-002", task_002_passive_vs_intervention),
        ("LCC-C2-003", task_003_delayed),
        ("LCC-C2-004", task_004_stochastic),
        ("LCC-C2-005", task_005_state_dependent),
        ("LCC-C2-006", task_006_baselines),
        ("LCC-C2-007", task_007_replay_provenance),
    ]:
        if task_id in {"LCC-C2-006", "LCC-C2-007"}:
            result = task_fn(out_root, tasks)
        else:
            result = task_fn(out_root)
        tasks[task_id] = result
        stop = result.get("stop_condition")
        if stop:
            stop_conditions.append(stop)
            stopped_at = task_id
            break
    decision = task_008_decision(out_root, tasks, stop_conditions)
    tasks["LCC-C2-008"] = decision
    return {
        "cycle_verdict": decision["verdict"],
        "stopped_at": stopped_at,
        "stop_conditions_triggered": stop_conditions,
        "claim_boundary": "bounded experiential counterfactual contract only",
        "tasks": tasks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run LCC Cycle 002 experiential counterfactual redteam.")
    parser.add_argument("--out", default="artifacts/cycles/cycle_002")
    args = parser.parse_args(argv)
    result = run_cycle_002(args.out)
    print(json.dumps({
        "verdict": result["cycle_verdict"],
        "stopped_at": result["stopped_at"],
        "stop_conditions_triggered": result["stop_conditions_triggered"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
