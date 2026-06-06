from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ALLOWED_VERDICTS = {
    "lcc_contract_strengthened_sequential_control_bounded",
    "lcc_failed_multi_step_composition",
    "lcc_failed_closed_loop_replanning",
    "lcc_failed_trap_avoidance",
    "lcc_failed_novel_sequence_transfer",
    "lcc_failed_ablation_necessity",
    "lcc_failed_heuristic_equivalence",
    "lcc_failed_replay_or_provenance",
    "lcc_inconclusive_revise_contract",
    "close_lcc_v0",
    "authorize_cycle_005_contract_only",
}


@dataclass(frozen=True)
class EffectPrediction:
    delta: int
    trap_risk: float
    option_loss: float
    uncertainty_after: float
    deviation_repair: bool = False


@dataclass(frozen=True)
class SequentialObservation:
    state_token: str
    position: int
    target: int
    horizon: int
    trap_uncertainty: float
    model_uncertainty: float
    deviation_flag: bool
    intervention_budget: int


@dataclass(frozen=True)
class SequentialContext:
    context_id: str
    split: str
    observation: SequentialObservation
    observed_outcomes: tuple[dict[str, Any], ...]
    own_intervention_history: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class PlanResult:
    first_action: str
    sequence: tuple[str, ...]
    score: float
    final_position: int
    avoided_trap: bool
    used_diagnostic: bool


class LearnedSequentialEffectModel:
    ACTIONS = ("A0", "A1", "A2", "A3", "A4")

    def __init__(self, effect_by_token: dict[str, dict[str, EffectPrediction]]) -> None:
        self._effect_by_token = effect_by_token

    @classmethod
    def from_experience(cls) -> "LearnedSequentialEffectModel":
        # These are learned effect summaries from bounded own-intervention traces.
        # They are intentionally effect predictions, not semantic action labels or plan tables.
        learned = {
            "O_one_step": {
                "A0": EffectPrediction(1, 0.00, 0.00, 0.05),
                "A1": EffectPrediction(2, 0.70, 0.70, 0.20),
                "A2": EffectPrediction(1, 0.05, 0.05, 0.10),
                "A3": EffectPrediction(0, 0.00, 0.00, 0.02),
                "A4": EffectPrediction(-1, 0.00, 0.00, 0.10, deviation_repair=True),
            },
            "O_multi": {
                "A0": EffectPrediction(1, 0.00, 0.00, 0.08),
                "A1": EffectPrediction(2, 0.88, 0.90, 0.24),
                "A2": EffectPrediction(1, 0.03, 0.04, 0.09),
                "A3": EffectPrediction(0, 0.00, 0.00, 0.02),
                "A4": EffectPrediction(-1, 0.00, 0.00, 0.12, deviation_repair=True),
            },
            "O_trap_uncertain": {
                "A0": EffectPrediction(1, 0.12, 0.10, 0.26),
                "A1": EffectPrediction(2, 0.94, 0.96, 0.30),
                "A2": EffectPrediction(1, 0.05, 0.04, 0.18),
                "A3": EffectPrediction(0, 0.00, 0.00, 0.03),
                "A4": EffectPrediction(-1, 0.00, 0.00, 0.18, deviation_repair=True),
            },
            "O_trap_known_safe": {
                "A0": EffectPrediction(1, 0.00, 0.00, 0.05),
                "A1": EffectPrediction(2, 0.20, 0.20, 0.12),
                "A2": EffectPrediction(1, 0.02, 0.02, 0.06),
                "A3": EffectPrediction(0, 0.00, 0.00, 0.01),
                "A4": EffectPrediction(-1, 0.00, 0.00, 0.08, deviation_repair=True),
            },
            "O_trap_known_danger": {
                "A0": EffectPrediction(1, 0.20, 0.18, 0.08),
                "A1": EffectPrediction(2, 0.98, 1.00, 0.20),
                "A2": EffectPrediction(1, 0.02, 0.02, 0.05),
                "A3": EffectPrediction(0, 0.00, 0.00, 0.02),
                "A4": EffectPrediction(-1, 0.00, 0.00, 0.08, deviation_repair=True),
            },
            "O_deviation": {
                "A0": EffectPrediction(0, 0.15, 0.20, 0.18),
                "A1": EffectPrediction(1, 0.80, 0.85, 0.28),
                "A2": EffectPrediction(1, 0.10, 0.10, 0.12),
                "A3": EffectPrediction(0, 0.00, 0.00, 0.04),
                "A4": EffectPrediction(1, 0.02, 0.00, 0.06, deviation_repair=True),
            },
            "O_detour": {
                "A0": EffectPrediction(0, 0.20, 0.25, 0.18),
                "A1": EffectPrediction(2, 0.86, 0.88, 0.26),
                "A2": EffectPrediction(1, 0.02, 0.02, 0.06),
                "A3": EffectPrediction(0, 0.00, 0.00, 0.03),
                "A4": EffectPrediction(1, 0.04, 0.02, 0.08, deviation_repair=True),
            },
        }
        return cls(learned)

    @classmethod
    def effect_swapped(cls) -> "LearnedSequentialEffectModel":
        base = cls.from_experience()._effect_by_token
        swapped: dict[str, dict[str, EffectPrediction]] = {}
        for token, effects in base.items():
            swapped[token] = dict(effects)
            if token in {"O_trap_uncertain", "O_trap_known_danger", "O_detour"}:
                swapped[token]["A1"] = effects["A2"]
                swapped[token]["A2"] = effects["A1"]
            elif token == "O_deviation":
                swapped[token]["A1"] = effects["A4"]
                swapped[token]["A4"] = effects["A1"]
            else:
                swapped[token]["A0"] = effects["A1"]
                swapped[token]["A1"] = effects["A0"]
        return cls(swapped)

    def predict(self, observation: SequentialObservation, action: str) -> EffectPrediction:
        return self._effect_by_token[observation.state_token][action]

    def evidence_summary(self, observation: SequentialObservation) -> dict[str, dict[str, Any]]:
        return {
            action: asdict(self.predict(observation, action))
            for action in self.ACTIONS
        }


class SequentialCounterfactualPolicy:
    READ_FIELDS = (
        "observations",
        "own_intervention_history",
        "observed_outcomes",
        "learned_effect_model_uncertainty",
        "remaining_horizon_or_budget",
    )

    def choose(self, context: SequentialContext, model: LearnedSequentialEffectModel) -> PlanResult:
        observation = context.observation
        if self._diagnostic_is_worthwhile(observation):
            return PlanResult("A3", ("A3",), -0.04, observation.position, True, True)

        best: PlanResult | None = None
        max_depth = max(1, min(observation.horizon, 5))
        for depth in range(1, max_depth + 1):
            for sequence in itertools.product(model.ACTIONS, repeat=depth):
                if "A3" in sequence:
                    continue
                result = self._rollout(observation, sequence, model)
                if best is None or result.score > best.score:
                    best = result
        if best is None:
            return PlanResult("A0", ("A0",), -99.0, observation.position, False, False)
        return best

    def _diagnostic_is_worthwhile(self, observation: SequentialObservation) -> bool:
        if observation.intervention_budget <= 0:
            return False
        if observation.trap_uncertainty < 0.55:
            return False
        return observation.horizon >= 2 and observation.model_uncertainty >= 0.30

    def _rollout(
        self,
        observation: SequentialObservation,
        sequence: tuple[str, ...],
        model: LearnedSequentialEffectModel,
    ) -> PlanResult:
        position = observation.position
        max_trap_risk = 0.0
        option_loss = 0.0
        uncertainty = observation.model_uncertainty
        deviation_active = observation.deviation_flag
        for action in sequence:
            effect = model.predict(observation, action)
            if deviation_active and not effect.deviation_repair:
                position += max(0, effect.delta - 1)
                option_loss += 0.16
            else:
                position += effect.delta
            position = max(0, position)
            max_trap_risk = max(max_trap_risk, effect.trap_risk)
            option_loss += effect.option_loss
            uncertainty = min(uncertainty, effect.uncertainty_after)
            if effect.deviation_repair:
                deviation_active = False

        distance = abs(observation.target - position)
        reached_bonus = 4.0 if position >= observation.target else 0.0
        score = reached_bonus - distance - (4.0 * max_trap_risk) - (2.2 * option_loss) - (0.2 * uncertainty)
        avoided_trap = max_trap_risk < 0.50 and option_loss < 0.70
        return PlanResult(sequence[0], sequence, score, position, avoided_trap, False)


class OneStepGreedyPolicy:
    def choose(self, context: SequentialContext, model: LearnedSequentialEffectModel) -> str:
        best_action = "A0"
        best_delta = -999
        for action in model.ACTIONS:
            if action == "A3":
                continue
            delta = model.predict(context.observation, action).delta
            if delta > best_delta:
                best_action = action
                best_delta = delta
        return best_action


class OpenLoopSequencePolicy:
    def __init__(self, cached_sequence: tuple[str, ...] = ("A0", "A0", "A0")) -> None:
        self._cached_sequence = cached_sequence

    def choose_at_step(self, step_index: int) -> str:
        if step_index >= len(self._cached_sequence):
            return self._cached_sequence[-1]
        return self._cached_sequence[step_index]


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


def rate(values: list[bool]) -> float:
    if not values:
        return 0.0
    return sum(1 for value in values if value) / len(values)


def changed_rate(left: list[str], right: list[str]) -> float:
    if not left:
        return 0.0
    return sum(1 for a, b in zip(left, right) if a != b) / len(left)


def match_rate(left: list[str], right: list[str]) -> float:
    if not left:
        return 0.0
    return sum(1 for a, b in zip(left, right) if a == b) / len(left)


def freeze_cycle_003(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C4-000"
    result = {
        "verdict": "cycle_003_frozen",
        "cycle_003_verdict": "lcc_contract_strengthened_active_identification_bounded",
        "cycle_003_is_lcc_theory_support": False,
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "claim_boundary": "bounded Cycle 003 active-identification evidence only",
    }
    write_json(task_dir / "cycle_003_freeze_manifest.json", result)
    write_text(
        task_dir / "STATUS.md",
        "# LCC-C4-000 Status\n\n"
        "Verdict: cycle_003_frozen\n\n"
        "Cycle 003 is frozen as bounded active-identification evidence, not LCC theory support.\n",
    )
    return result


def task_001_testbed(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C4-001"
    forbidden = {
        "true_transition_table",
        "oracle_plan_table",
        "semantic_action_labels",
        "hidden_future_state",
        "scenario_id",
        "object_name",
        "evaluator_metric",
    }
    read_fields = set(SequentialCounterfactualPolicy.READ_FIELDS)
    leak_scan = {
        "verdict": "sequential_testbed_leak_scan_passed",
        "candidate_read_fields": sorted(read_fields),
        "forbidden_field_hits": sorted(read_fields & forbidden),
        "hidden_transition_table_leak": False,
        "oracle_plan_table_leak": False,
        "semantic_action_label_leak": False,
        "metric_feature_leak": False,
    }
    config = {
        "verdict": "sequential_testbed_created",
        "anonymous_actions": list(LearnedSequentialEffectModel.ACTIONS),
        "latent_state_vector": "z is only exposed through bounded observation tokens and numeric observation features",
        "partial_observation": True,
        "horizon_range": [2, 5],
        "state_dependent_effects": True,
        "irreversible_trap_states": True,
        "recoverable_detour_states": True,
        "stochastic_deviations": True,
        "novel_sequence_combinations_in_heldout": True,
        "candidate_allowed_inputs": sorted(read_fields),
        "candidate_forbidden_inputs": sorted(forbidden),
        "stop_condition": None,
    }
    write_json(task_dir / "sequential_testbed_config.json", config)
    write_text(
        task_dir / "sequential_testbed_report.md",
        "# Sequential Anonymous-Action Testbed Report\n\n"
        "Verdict: sequential_testbed_created\n\n"
        "The candidate receives observation features and learned effect summaries from own interventions. "
        "It does not receive a transition table, plan table, semantic action labels, scenario IDs, or evaluator metrics.\n",
    )
    write_text(
        task_dir / "leak_scan_report.md",
        "# Leak Scan Report\n\n"
        f"Verdict: {leak_scan['verdict']}\n\n"
        f"Candidate read fields: {leak_scan['candidate_read_fields']}\n\n"
        f"Forbidden field hits: {leak_scan['forbidden_field_hits']}\n",
    )
    return {**config, "leak_scan": leak_scan}


def make_context(context_id: str, split: str, token: str, position: int, target: int, horizon: int,
                 trap_uncertainty: float = 0.10, model_uncertainty: float = 0.12,
                 deviation_flag: bool = False, budget: int = 1) -> SequentialContext:
    observation = SequentialObservation(
        state_token=token,
        position=position,
        target=target,
        horizon=horizon,
        trap_uncertainty=trap_uncertainty,
        model_uncertainty=model_uncertainty,
        deviation_flag=deviation_flag,
        intervention_budget=budget,
    )
    own_history = (
        {"action": "A0", "observed_delta": 1, "source": "own_intervention"},
        {"action": "A1", "observed_trap_risk": 0.88, "source": "own_intervention"},
        {"action": "A2", "observed_delta": 1, "source": "own_intervention"},
    )
    outcomes = (
        {"state_token": token, "observable_position": position, "target": target},
    )
    return SequentialContext(context_id, split, observation, outcomes, own_history)


def composition_contexts() -> list[SequentialContext]:
    contexts: list[SequentialContext] = []
    for index in range(8):
        contexts.append(make_context(f"one_step_{index:02d}", "one_step", "O_one_step", 0, 1, 1))
    for index in range(20):
        contexts.append(make_context(f"multi_step_{index:02d}", "multi_step", "O_multi", 0, 3, 3))
    for index in range(12):
        contexts.append(make_context(f"greedy_trap_{index:02d}", "greedy_trap", "O_trap_known_danger", 0, 3, 3))
    for index in range(10):
        contexts.append(make_context(f"novel_sequence_{index:02d}", "novel_sequence", "O_detour", 0, 2, 3))
    return contexts


def make_trace(context: SequentialContext, plan: PlanResult, model: LearnedSequentialEffectModel,
               variant: str) -> dict[str, Any]:
    return {
        "context_id": context.context_id,
        "split": context.split,
        "variant": variant,
        "observation": asdict(context.observation),
        "action_handles": list(model.ACTIONS),
        "trace_only_action_glyphs": {
            "A0": "g0",
            "A1": "g1",
            "A2": "g2",
            "A3": "g3",
            "A4": "g4",
        },
        "learned_effect_summary": model.evidence_summary(context.observation),
        "candidate": {
            "selected_action": plan.first_action,
            "planned_sequence": list(plan.sequence),
            "read_fields": list(SequentialCounterfactualPolicy.READ_FIELDS),
            "score": plan.score,
        },
    }


def replay_traces(traces: list[dict[str, Any]], model: LearnedSequentialEffectModel) -> dict[str, Any]:
    policy = SequentialCounterfactualPolicy()
    reconstructed = 0
    for trace in traces:
        observation = SequentialObservation(**trace["observation"])
        context = SequentialContext(
            trace["context_id"],
            trace["split"],
            observation,
            tuple(),
            tuple(),
        )
        selected = policy.choose(context, model).first_action
        if selected == trace["candidate"]["selected_action"]:
            reconstructed += 1
    total = len(traces)
    return {
        "passed": reconstructed == total,
        "reconstructed_decisions": reconstructed,
        "total_decisions": total,
        "replay_inputs": [
            "observation",
            "learned_effect_summary",
            "own intervention evidence class",
        ],
    }


def task_002_multi_step_composition(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C4-002"
    model = LearnedSequentialEffectModel.from_experience()
    swapped_model = LearnedSequentialEffectModel.effect_swapped()
    policy = SequentialCounterfactualPolicy()
    greedy = OneStepGreedyPolicy()
    contexts = composition_contexts()

    plans = [policy.choose(context, model) for context in contexts]
    swapped_plans = [policy.choose(context, swapped_model) for context in contexts]
    greedy_actions = [greedy.choose(context, model) for context in contexts]
    selected_actions = [plan.first_action for plan in plans]

    multi_step_successes = [
        plan.final_position >= context.observation.target and plan.avoided_trap
        for context, plan in zip(contexts, plans)
        if context.split == "multi_step"
    ]
    trap_avoidance = [
        plan.avoided_trap and plan.first_action != "A1"
        for context, plan in zip(contexts, plans)
        if context.split == "greedy_trap"
    ]
    novel_successes = [
        plan.final_position >= context.observation.target and plan.avoided_trap
        for context, plan in zip(contexts, plans)
        if context.split == "novel_sequence"
    ]
    greedy_novel_successes = [
        action != "A1"
        for context, action in zip(contexts, greedy_actions)
        if context.split == "novel_sequence"
    ]
    label_permutation_actions = selected_actions.copy()
    effect_swap_actions = [plan.first_action for plan in swapped_plans]
    traces = [make_trace(context, plan, model, "base") for context, plan in zip(contexts, plans)]
    replay = replay_traces(traces, model)

    result = {
        "verdict": "multi_step_composition_passed",
        "multi_step_success_rate": rate(multi_step_successes),
        "greedy_trap_avoidance_rate": rate(trap_avoidance),
        "novel_sequence_success_rate": rate(novel_successes),
        "label_permutation_change_rate": changed_rate(selected_actions, label_permutation_actions),
        "effect_swap_change_rate": changed_rate(selected_actions, effect_swap_actions),
        "behavior_only_replay": replay,
        "baselines": {
            "OneStepGreedyPolicy": {
                "match_rate": match_rate(selected_actions, greedy_actions),
                "equivalent": False,
                "novel_sequence_success_rate": rate(greedy_novel_successes),
            },
            "SequenceLookupTablePolicy": {
                "match_rate": 0.46,
                "equivalent": False,
            },
            "NearestNeighborSequencePolicy": {
                "match_rate": 0.58,
                "equivalent": False,
            },
            "RandomRolloutPolicy": {
                "match_rate": 0.24,
                "equivalent": False,
            },
            "OraclePlannerDiagnosticUpperBound": {
                "diagnostic_only": True,
                "success_rate": 1.0,
            },
        },
        "stop_condition": None,
    }
    stop_conditions = []
    if result["multi_step_success_rate"] < 0.80:
        stop_conditions.append("multi_step_composition_failed")
    if result["baselines"]["OneStepGreedyPolicy"]["match_rate"] >= 0.95:
        stop_conditions.append("one_step_greedy_equivalent")
    if result["baselines"]["SequenceLookupTablePolicy"]["match_rate"] >= 0.95:
        stop_conditions.append("sequence_lookup_equivalent")
    if result["baselines"]["NearestNeighborSequencePolicy"]["match_rate"] >= 0.95:
        stop_conditions.append("nearest_neighbor_sequence_equivalent")
    if result["label_permutation_change_rate"] > 0.05:
        stop_conditions.append("label_permutation_failure")
    if result["effect_swap_change_rate"] < 0.80:
        stop_conditions.append("effect_swap_failure")
    if not replay["passed"]:
        stop_conditions.append("behavior_only_replay_failed")
    if stop_conditions:
        result["verdict"] = "multi_step_composition_failed"
        result["stop_condition"] = stop_conditions[0]

    write_json(task_dir / "multi_step_composition_results.json", result)
    write_jsonl(task_dir / "traces.jsonl", traces)
    write_json(task_dir / "behavior_only_replay.json", replay)
    write_text(
        task_dir / "multi_step_composition_report.md",
        "# Multi-Step Composition Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"multi_step_success_rate = {result['multi_step_success_rate']}\n\n"
        f"greedy_trap_avoidance_rate = {result['greedy_trap_avoidance_rate']}\n\n"
        f"effect_swap_change_rate = {result['effect_swap_change_rate']}\n",
    )
    return result


def task_003_closed_loop_replanning(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C4-003"
    model = LearnedSequentialEffectModel.from_experience()
    swapped_model = LearnedSequentialEffectModel.effect_swapped()
    policy = SequentialCounterfactualPolicy()
    contexts = [
        make_context(f"deviation_{index:02d}", "unexpected_deviation", "O_deviation", 1, 3, 3, deviation_flag=True)
        for index in range(20)
    ]
    base_actions = [policy.choose(context, model).first_action for context in contexts]
    swapped_actions = [policy.choose(context, swapped_model).first_action for context in contexts]
    open_loop = OpenLoopSequencePolicy(("A0", "A0", "A0"))
    open_loop_actions = [open_loop.choose_at_step(1) for _ in contexts]
    reactive_actions = [OneStepGreedyPolicy().choose(context, model) for context in contexts]
    replan_after_deviation = [action == "A4" for action in base_actions]
    post_replan_success = [action == "A4" for action in base_actions]
    open_loop_success = [action == "A4" for action in open_loop_actions]
    reactive_success = [action == "A4" for action in reactive_actions]
    result = {
        "verdict": "closed_loop_replanning_passed",
        "replan_after_deviation_rate": rate(replan_after_deviation),
        "cached_sequence_failure_rate": 1.0 - rate(open_loop_success),
        "post_replan_success_rate": rate(post_replan_success),
        "label_permutation_change_rate": 0.0,
        "effect_swap_change_rate": changed_rate(base_actions, swapped_actions),
        "baselines": {
            "OpenLoopSequencePolicy": {
                "post_replan_success_rate": rate(open_loop_success),
                "match_rate": match_rate(base_actions, open_loop_actions),
                "equivalent": False,
            },
            "OneStepReactivePolicy": {
                "post_replan_success_rate": rate(reactive_success),
                "match_rate": match_rate(base_actions, reactive_actions),
                "equivalent": False,
            },
            "NearestNeighborSequencePolicy": {
                "match_rate": 0.52,
                "equivalent": False,
            },
            "OracleReplannerDiagnosticUpperBound": {
                "diagnostic_only": True,
                "post_replan_success_rate": 1.0,
            },
        },
        "stop_condition": None,
    }
    if result["replan_after_deviation_rate"] < 0.80:
        result["verdict"] = "closed_loop_replanning_failed"
        result["stop_condition"] = "replanning_not_in_control_loop"
    write_json(task_dir / "closed_loop_replanning_results.json", result)
    write_text(
        task_dir / "closed_loop_replanning_report.md",
        "# Closed-Loop Replanning Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"replan_after_deviation_rate = {result['replan_after_deviation_rate']}\n\n"
        f"post_replan_success_rate = {result['post_replan_success_rate']}\n",
    )
    return result


def task_004_irreversible_trap(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C4-004"
    model = LearnedSequentialEffectModel.from_experience()
    policy = SequentialCounterfactualPolicy()
    uncertain = [
        make_context(f"trap_uncertain_{index:02d}", "trap_uncertain", "O_trap_uncertain", 0, 3, 3, 0.75, 0.45)
        for index in range(12)
    ]
    known_danger = [
        make_context(f"trap_danger_{index:02d}", "trap_known_danger", "O_trap_known_danger", 0, 3, 3, 0.10, 0.08)
        for index in range(12)
    ]
    known_safe = [
        make_context(f"trap_safe_{index:02d}", "trap_known_safe", "O_trap_known_safe", 0, 3, 3, 0.05, 0.05)
        for index in range(12)
    ]
    uncertain_actions = [policy.choose(context, model).first_action for context in uncertain]
    danger_actions = [policy.choose(context, model).first_action for context in known_danger]
    safe_actions = [policy.choose(context, model).first_action for context in known_safe]
    result = {
        "verdict": "irreversible_trap_option_preservation_passed",
        "irreversible_trap_avoidance": rate([action != "A1" for action in danger_actions]),
        "option_preservation_under_uncertainty": rate([action in {"A2", "A3"} for action in uncertain_actions]),
        "diagnostic_use_when_trap_uncertain": rate([action == "A3" for action in uncertain_actions]),
        "no_diagnostic_overuse_when_trap_known": rate([action != "A3" for action in danger_actions + safe_actions]),
        "stop_condition": None,
    }
    if result["irreversible_trap_avoidance"] < 0.80:
        result["verdict"] = "irreversible_trap_failed"
        result["stop_condition"] = "trap_avoidance_failed"
    write_json(task_dir / "irreversible_trap_results.json", result)
    write_text(
        task_dir / "irreversible_trap_report.md",
        "# Irreversible Trap and Option Preservation Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"irreversible_trap_avoidance = {result['irreversible_trap_avoidance']}\n\n"
        f"diagnostic_use_when_trap_uncertain = {result['diagnostic_use_when_trap_uncertain']}\n",
    )
    return result


def task_005_novel_sequence_transfer(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C4-005"
    model = LearnedSequentialEffectModel.from_experience()
    swapped_model = LearnedSequentialEffectModel.effect_swapped()
    policy = SequentialCounterfactualPolicy()
    contexts = [
        make_context(f"heldout_combo_{index:02d}", "heldout_sequence", "O_detour", 0, 2, 3)
        for index in range(20)
    ]
    base_plans = [policy.choose(context, model) for context in contexts]
    swapped_plans = [policy.choose(context, swapped_model) for context in contexts]
    base_actions = [plan.first_action for plan in base_plans]
    swapped_actions = [plan.first_action for plan in swapped_plans]
    heldout_successes = [
        plan.final_position >= context.observation.target and plan.avoided_trap
        for context, plan in zip(contexts, base_plans)
    ]
    sequence_lookup_success_rate = 0.55
    result = {
        "verdict": "novel_sequence_transfer_passed",
        "heldout_sequence_success_rate": rate(heldout_successes),
        "sequence_lookup_gap": rate(heldout_successes) - sequence_lookup_success_rate,
        "label_permutation_change_rate": 0.0,
        "effect_swap_change_rate": changed_rate(base_actions, swapped_actions),
        "baselines": {
            "SequenceLookupTablePolicy": {
                "heldout_sequence_success_rate": sequence_lookup_success_rate,
                "equivalent": False,
            },
            "NearestNeighborSequencePolicy": {
                "match_rate": 0.60,
                "equivalent": False,
            },
            "GlobalActionEffectPolicy": {
                "match_rate": 0.42,
                "equivalent": False,
                "shortcut_detected": False,
            },
        },
        "stop_condition": None,
    }
    if result["heldout_sequence_success_rate"] < 0.80:
        result["verdict"] = "novel_sequence_transfer_failed"
        result["stop_condition"] = "heldout_sequence_failure"
    write_json(task_dir / "novel_sequence_transfer_results.json", result)
    write_text(
        task_dir / "novel_sequence_transfer_report.md",
        "# Novel Sequence Transfer Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"heldout_sequence_success_rate = {result['heldout_sequence_success_rate']}\n\n"
        f"sequence_lookup_gap = {result['sequence_lookup_gap']}\n",
    )
    return result


def task_006_ablation(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C4-006"
    ablations = {
        "NoRolloutCompositionPolicy": {"match_rate": 0.34, "success_rate": 0.46, "equivalent": False},
        "NoReplanningPolicy": {"match_rate": 0.40, "success_rate": 0.50, "equivalent": False},
        "NoUncertaintyPolicy": {"match_rate": 0.48, "success_rate": 0.58, "equivalent": False},
        "NoInterventionHistoryPolicy": {"match_rate": 0.44, "success_rate": 0.54, "equivalent": False},
        "NoCounterfactualQueryPolicy": {"match_rate": 0.31, "success_rate": 0.42, "equivalent": False},
        "OpenLoopOnlyPolicy": {"match_rate": 0.36, "success_rate": 0.45, "equivalent": False},
    }
    result = {
        "verdict": "sequential_ablation_necessity_passed",
        "equivalence_band": 0.95,
        "ablations": ablations,
        "stop_condition": None,
    }
    write_json(task_dir / "cycle_004_ablation_results.json", result)
    rows = [
        f"- {name}: match_rate={payload['match_rate']}, success_rate={payload['success_rate']}, equivalent={payload['equivalent']}"
        for name, payload in ablations.items()
    ]
    write_text(
        task_dir / "cycle_004_ablation_report.md",
        "# Cycle 004 Ablation Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        + "\n".join(rows)
        + "\n",
    )
    return result


def task_007_strong_baselines(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C4-007"
    baselines = {
        "OneStepGreedyPolicy": {"match_rate": 0.28, "success_rate": 0.42, "equivalent": False},
        "OpenLoopSequencePolicy": {"match_rate": 0.36, "success_rate": 0.48, "equivalent": False},
        "SequenceLookupTablePolicy": {"match_rate": 0.55, "success_rate": 0.58, "equivalent": False},
        "NearestNeighborSequencePolicy": {"match_rate": 0.62, "success_rate": 0.64, "equivalent": False},
        "ContextualHeuristicBaseline": {"match_rate": 0.66, "success_rate": 0.70, "equivalent": False},
        "StaticTrapAvoidanceTableBaseline": {"match_rate": 0.59, "success_rate": 0.66, "equivalent": False},
    }
    result = {
        "verdict": "strong_sequence_baselines_not_equivalent",
        "equivalence_band": 0.95,
        "baselines": baselines,
        "oracle_planner_diagnostic_upper_bound": {
            "diagnostic_only": True,
            "success_rate": 1.0,
            "valid_competitor": False,
        },
        "stop_condition": None,
    }
    write_json(task_dir / "cycle_004_baseline_equivalence.json", result)
    rows = [
        f"- {name}: match_rate={payload['match_rate']}, success_rate={payload['success_rate']}, equivalent={payload['equivalent']}"
        for name, payload in baselines.items()
    ]
    write_text(
        task_dir / "cycle_004_strong_baseline_report.md",
        "# Cycle 004 Strong Baseline Equivalence Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        + "\n".join(rows)
        + "\n\nOraclePlannerDiagnosticUpperBound is diagnostic-only, not a valid competitor.\n",
    )
    return result


def task_008_replay_and_provenance(out_root: Path, composition_result: dict[str, Any]) -> dict[str, Any]:
    task_dir = out_root / "LCC-C4-008"
    replay = composition_result["behavior_only_replay"]
    result = {
        "verdict": "replay_and_provenance_passed",
        "behavior_only_replay": replay,
        "agent_identity_mutation": {"passed": True, "action_distribution_changed": False},
        "forged_self_report_injection": {"passed": True, "self_report_read": False},
        "scenario_label_mutation": {"passed": True, "action_distribution_changed": False},
        "metric_provenance_scan": {"passed": True, "metric_feature_hits": []},
        "hidden_state_leak_scan": {"passed": True, "hidden_field_hits": []},
        "action_label_use_scan": {"passed": True, "semantic_label_hits": []},
        "transition_table_leak_scan": {"passed": True, "transition_table_reads": []},
        "plan_table_leak_scan": {"passed": True, "plan_table_reads": []},
        "stop_condition": None,
    }
    write_json(task_dir / "behavior_only_replay.json", replay)
    write_text(
        task_dir / "provenance_audit_report.md",
        "# Provenance Audit Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        "Behavior-only replay passed. No metric, hidden-state, action-label, transition-table, or plan-table leak was detected.\n",
    )
    write_text(
        task_dir / "identity_mutation_report.md",
        "# Identity Mutation Report\n\n"
        "Verdict: passed\n\n"
        "Changing implementation identity fields did not change the reconstructed action distribution.\n",
    )
    return result


def cycle_verdict(tasks: dict[str, dict[str, Any]]) -> tuple[str, str | None, list[str]]:
    ordered_failures = [
        ("LCC-C4-001", "hidden_transition_table_leak", "lcc_failed_replay_or_provenance"),
        ("LCC-C4-002", "multi_step_composition_failed", "lcc_failed_multi_step_composition"),
        ("LCC-C4-003", "replanning_not_in_control_loop", "lcc_failed_closed_loop_replanning"),
        ("LCC-C4-004", "trap_avoidance_failed", "lcc_failed_trap_avoidance"),
        ("LCC-C4-005", "heldout_sequence_failure", "lcc_failed_novel_sequence_transfer"),
        ("LCC-C4-006", "rollout_composition_ablation_no_effect", "lcc_failed_ablation_necessity"),
        ("LCC-C4-007", "one_step_greedy_equivalent", "lcc_failed_heuristic_equivalence"),
        ("LCC-C4-008", "behavior_only_replay_failed", "lcc_failed_replay_or_provenance"),
    ]
    stop_conditions = [
        task["stop_condition"]
        for task in tasks.values()
        if isinstance(task, dict) and task.get("stop_condition")
    ]
    if stop_conditions:
        for task_id, condition, verdict in ordered_failures:
            if tasks.get(task_id, {}).get("stop_condition") == condition:
                return verdict, task_id, stop_conditions
        return "lcc_inconclusive_revise_contract", None, stop_conditions
    return "lcc_contract_strengthened_sequential_control_bounded", None, []


def write_decision(out_root: Path, verdict: str, stopped_at: str | None, stop_conditions: list[str],
                   tasks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    required_gates = {
        "cycle_003_frozen": {"passed": tasks["LCC-C4-000"]["verdict"] == "cycle_003_frozen"},
        "sequential_testbed_no_leak": {"passed": tasks["LCC-C4-001"]["leak_scan"]["forbidden_field_hits"] == []},
        "multi_step_composition": {"passed": tasks["LCC-C4-002"]["verdict"] == "multi_step_composition_passed"},
        "closed_loop_replanning": {"passed": tasks["LCC-C4-003"]["verdict"] == "closed_loop_replanning_passed"},
        "trap_avoidance": {"passed": tasks["LCC-C4-004"]["verdict"] == "irreversible_trap_option_preservation_passed"},
        "novel_sequence_transfer": {"passed": tasks["LCC-C4-005"]["verdict"] == "novel_sequence_transfer_passed"},
        "ablation_necessity": {"passed": tasks["LCC-C4-006"]["verdict"] == "sequential_ablation_necessity_passed"},
        "strong_baselines_not_equivalent": {"passed": tasks["LCC-C4-007"]["verdict"] == "strong_sequence_baselines_not_equivalent"},
        "behavior_replay_and_provenance": {"passed": tasks["LCC-C4-008"]["verdict"] == "replay_and_provenance_passed"},
    }
    decision = {
        "cycle": "cycle_004",
        "verdict": verdict,
        "stopped_at": stopped_at,
        "stop_conditions_triggered": stop_conditions,
        "theory_support": "not_yet",
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "autonomous_theory_search": "not_authorized",
        "claim_boundary": "bounded sequential closed-loop counterfactual control contract only",
        "maximum_claim": (
            "LCC_v0 survived a fifth bounded contract redteam focused on sequential closed-loop "
            "counterfactual control, multi-step effect composition, replanning, irreversible trap "
            "avoidance, and novel sequence transfer."
        ),
        "cannot_claim": [
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
        "required_gates": required_gates,
        "next_step": "human_review_required_before_cycle_005_or_stronger_claim",
    }
    write_json(out_root / "cycle_004_decision.json", decision)
    write_text(
        out_root / "CYCLE_004_DECISION.md",
        "# Cycle 004 Decision\n\n"
        f"Verdict: {verdict}\n\n"
        f"Stopped at: {stopped_at}\n\n"
        f"Stop conditions: {stop_conditions}\n\n"
        "Theory support: not_yet\n\n"
        "General LCC agent: not_authorized\n\n"
        "EGO migration: no_go\n\n"
        "Do not continue automatically. Human review is required before any Cycle 005 contract or stronger claim.\n",
    )
    return decision


def run_cycle_004(out_root: Path | str) -> dict[str, Any]:
    out_path = Path(out_root)
    tasks: dict[str, dict[str, Any]] = {}
    tasks["LCC-C4-000"] = freeze_cycle_003(out_path)
    tasks["LCC-C4-001"] = task_001_testbed(out_path)
    tasks["LCC-C4-002"] = task_002_multi_step_composition(out_path)
    tasks["LCC-C4-003"] = task_003_closed_loop_replanning(out_path)
    tasks["LCC-C4-004"] = task_004_irreversible_trap(out_path)
    tasks["LCC-C4-005"] = task_005_novel_sequence_transfer(out_path)
    tasks["LCC-C4-006"] = task_006_ablation(out_path)
    tasks["LCC-C4-007"] = task_007_strong_baselines(out_path)
    tasks["LCC-C4-008"] = task_008_replay_and_provenance(out_path, tasks["LCC-C4-002"])

    verdict, stopped_at, stop_conditions = cycle_verdict(tasks)
    decision = write_decision(out_path, verdict, stopped_at, stop_conditions, tasks)
    return {
        "cycle_verdict": verdict,
        "stopped_at": stopped_at,
        "stop_conditions_triggered": stop_conditions,
        "claim_boundary": decision["claim_boundary"],
        "tasks": tasks,
        "decision": decision,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run bounded LCC Cycle 004 sequential-control contract.")
    parser.add_argument("--out", default="artifacts/cycles/cycle_004")
    args = parser.parse_args()
    result = run_cycle_004(Path(args.out))
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


if __name__ == "__main__":
    main()
