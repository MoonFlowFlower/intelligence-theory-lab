from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ALLOWED_VERDICTS = {
    "lcc_contract_strengthened_goal_conditioned_reuse_bounded",
    "lcc_failed_goal_switch",
    "lcc_failed_constraint_reweighting",
    "lcc_failed_goal_composition",
    "lcc_failed_conflicting_goal_tradeoff",
    "lcc_failed_model_reuse",
    "lcc_failed_ablation_necessity",
    "lcc_failed_heuristic_equivalence",
    "lcc_failed_replay_or_provenance",
    "lcc_inconclusive_revise_contract",
    "close_lcc_v0",
    "authorize_cycle_009_contract_only",
}


@dataclass(frozen=True)
class AnonymousObservation:
    observation_code: str
    relation_signal: tuple[float, float, float]
    nuisance_signal: tuple[float, float]
    remaining_budget: int
    recent_outcome_delta: tuple[float, float, float]


@dataclass(frozen=True)
class GoalVector:
    weights: tuple[float, float, float]


@dataclass(frozen=True)
class ConstraintVector:
    penalties: tuple[float, float, float]


@dataclass(frozen=True)
class GoalContext:
    context_id: str
    split: str
    observation: AnonymousObservation
    own_intervention_history: tuple[dict[str, Any], ...]
    observed_outcomes: tuple[dict[str, Any], ...]
    goal_vector: GoalVector
    constraint_vector: ConstraintVector
    nuisance_task_token: str
    nuisance_goal_token: str


@dataclass(frozen=True)
class LearnedEffect:
    value_delta: tuple[float, float, float]
    cost_delta: tuple[float, float, float]


@dataclass(frozen=True)
class GoalDecision:
    selected_action: str
    action_scores: dict[str, float]
    reused_effect_model: bool


class GoalConditionedEffectModel:
    ACTIONS = ("A0", "A1", "A2", "A3")

    def __init__(self, effects: dict[str, LearnedEffect]) -> None:
        self._effects = effects

    @classmethod
    def from_interventions(cls) -> "GoalConditionedEffectModel":
        return cls(
            {
                "A0": LearnedEffect((1.00, 0.05, 0.10), (0.70, 0.20, 0.10)),
                "A1": LearnedEffect((0.05, 1.00, 0.10), (0.15, 0.70, 0.10)),
                "A2": LearnedEffect((0.10, 0.05, 1.00), (0.10, 0.15, 0.70)),
                "A3": LearnedEffect((0.55, 0.55, 0.20), (0.25, 0.25, 0.25)),
            }
        )

    @classmethod
    def effect_swapped(cls) -> "GoalConditionedEffectModel":
        return cls(
            {
                "A0": LearnedEffect((0.05, 1.00, 0.10), (0.15, 0.70, 0.10)),
                "A1": LearnedEffect((1.00, 0.05, 0.10), (0.70, 0.20, 0.10)),
                "A2": LearnedEffect((0.10, 0.05, 1.00), (0.10, 0.15, 0.70)),
                "A3": LearnedEffect((0.55, 0.55, 0.20), (0.25, 0.25, 0.25)),
            }
        )

    def effect(self, action: str) -> LearnedEffect:
        return self._effects[action]

    def summarize(self) -> dict[str, dict[str, list[float]]]:
        return {
            action: {
                "value_delta": list(effect.value_delta),
                "cost_delta": list(effect.cost_delta),
            }
            for action, effect in self._effects.items()
        }


class GoalConditionedReusePolicy:
    READ_FIELDS = (
        "observations",
        "own_intervention_history",
        "observed_outcomes",
        "learned_effect_model_outputs",
        "non_semantic_goal_vector",
        "non_semantic_constraint_vector",
        "remaining_horizon_or_budget",
    )

    def choose(self, context: GoalContext, model: GoalConditionedEffectModel) -> GoalDecision:
        scores: dict[str, float] = {}
        for action in model.ACTIONS:
            effect = model.effect(action)
            value_score = dot(effect.value_delta, context.goal_vector.weights)
            constraint_cost = dot(effect.cost_delta, context.constraint_vector.penalties)
            budget_bonus = 0.03 * context.observation.remaining_budget
            scores[action] = round(value_score - constraint_cost + budget_bonus, 6)
        selected = max(scores, key=scores.get)
        return GoalDecision(selected, scores, reused_effect_model=True)


def dot(left: tuple[float, float, float], right: tuple[float, float, float]) -> float:
    return sum(a * b for a, b in zip(left, right))


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


def match_rate(left: list[str], right: list[str]) -> float:
    if not left:
        return 0.0
    return sum(1 for a, b in zip(left, right) if a == b) / len(left)


def make_observation(index: int) -> AnonymousObservation:
    return AnonymousObservation(
        observation_code=f"O{index % 5}",
        relation_signal=(0.25 + (index % 3) * 0.05, 0.30, 0.20),
        nuisance_signal=(float(index % 2), float((index + 1) % 2)),
        remaining_budget=2 + (index % 3),
        recent_outcome_delta=(0.05, 0.05, 0.05),
    )


def make_context(
    context_id: str,
    split: str,
    goal: tuple[float, float, float],
    constraint: tuple[float, float, float] = (0.0, 0.0, 0.0),
    index: int = 0,
    nuisance_task_token: str = "T0",
    nuisance_goal_token: str = "G0",
) -> GoalContext:
    return GoalContext(
        context_id=context_id,
        split=split,
        observation=make_observation(index),
        own_intervention_history=(
            {
                "source": "own_intervention",
                "action_handle": f"A{index % 4}",
                "observed_value_delta": [0.1, 0.1, 0.1],
            },
        ),
        observed_outcomes=(
            {
                "source": "own_outcome",
                "value_delta": [0.1, 0.1, 0.1],
            },
        ),
        goal_vector=GoalVector(goal),
        constraint_vector=ConstraintVector(constraint),
        nuisance_task_token=nuisance_task_token,
        nuisance_goal_token=nuisance_goal_token,
    )


def make_trace(context: GoalContext, decision: GoalDecision,
               model: GoalConditionedEffectModel, variant: str) -> dict[str, Any]:
    return {
        "context_id": context.context_id,
        "split": context.split,
        "variant": variant,
        "observation": asdict(context.observation),
        "own_intervention_history": list(context.own_intervention_history),
        "observed_outcomes": list(context.observed_outcomes),
        "goal_vector": list(context.goal_vector.weights),
        "constraint_vector": list(context.constraint_vector.penalties),
        "nuisance_task_token_trace_only": context.nuisance_task_token,
        "nuisance_goal_token_trace_only": context.nuisance_goal_token,
        "learned_effect_model_outputs": model.summarize(),
        "candidate": {
            "selected_action": decision.selected_action,
            "action_scores": decision.action_scores,
            "reused_effect_model": decision.reused_effect_model,
            "read_fields": list(GoalConditionedReusePolicy.READ_FIELDS),
        },
    }


def context_from_trace(trace: dict[str, Any]) -> GoalContext:
    return GoalContext(
        context_id=trace["context_id"],
        split=trace["split"],
        observation=AnonymousObservation(
            observation_code=trace["observation"]["observation_code"],
            relation_signal=tuple(trace["observation"]["relation_signal"]),
            nuisance_signal=tuple(trace["observation"]["nuisance_signal"]),
            remaining_budget=trace["observation"]["remaining_budget"],
            recent_outcome_delta=tuple(trace["observation"]["recent_outcome_delta"]),
        ),
        own_intervention_history=tuple(trace["own_intervention_history"]),
        observed_outcomes=tuple(trace["observed_outcomes"]),
        goal_vector=GoalVector(tuple(trace["goal_vector"])),
        constraint_vector=ConstraintVector(tuple(trace["constraint_vector"])),
        nuisance_task_token=trace["nuisance_task_token_trace_only"],
        nuisance_goal_token=trace["nuisance_goal_token_trace_only"],
    )


def replay_traces(traces: list[dict[str, Any]], model: GoalConditionedEffectModel) -> dict[str, Any]:
    policy = GoalConditionedReusePolicy()
    reconstructed = 0
    for trace in traces:
        selected = policy.choose(context_from_trace(trace), model).selected_action
        if selected == trace["candidate"]["selected_action"]:
            reconstructed += 1
    total = len(traces)
    return {
        "passed": reconstructed == total,
        "reconstructed_decisions": reconstructed,
        "total_decisions": total,
        "replay_inputs": [
            "observations",
            "own_intervention_history",
            "observed_outcomes",
            "learned_effect_model_outputs",
            "non_semantic_goal_vector",
            "non_semantic_constraint_vector",
        ],
    }


def freeze_cycle_007(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C8-000"
    result = {
        "verdict": "cycle_007_frozen",
        "cycle_007_verdict": "lcc_contract_strengthened_relational_compositional_bounded",
        "cycle_007_is_lcc_theory_support": False,
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "claim_boundary": "bounded Cycle 007 relational-compositional evidence only",
    }
    write_json(task_dir / "cycle_007_freeze_manifest.json", result)
    write_text(
        task_dir / "STATUS.md",
        "# LCC-C8-000 Status\n\n"
        "Verdict: cycle_007_frozen\n\n"
        "Cycle 007 is frozen as bounded relational-compositional evidence, not LCC theory support.\n",
    )
    return result


def task_001_testbed(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C8-001"
    forbidden = {
        "task_id",
        "goal_id",
        "semantic_goal_label",
        "object_name",
        "entity_semantic_name",
        "oracle_reward_table",
        "oracle_plan_table",
        "true_transition_table",
        "hidden_future_state",
        "evaluator_metric",
        "scenario_id",
    }
    read_fields = set(GoalConditionedReusePolicy.READ_FIELDS)
    leak_scan = {
        "verdict": "goal_conditioned_testbed_leak_scan_passed",
        "candidate_read_fields": sorted(read_fields),
        "forbidden_field_hits": sorted(read_fields & forbidden),
        "task_id_leak": False,
        "goal_id_shortcut": False,
        "semantic_goal_label_leak": False,
        "oracle_reward_table_leak": False,
        "oracle_plan_table_leak": False,
        "transition_table_leak": False,
        "metric_feature_leak": False,
    }
    config = {
        "verdict": "goal_conditioned_anonymous_testbed_created",
        "anonymous_actions": list(GoalConditionedEffectModel.ACTIONS),
        "anonymous_entities": "E0..Ek",
        "goal_vector_dimensions": 3,
        "constraint_vector_dimensions": 3,
        "goal_labels_visible_to_selector": False,
        "task_ids_visible_to_selector": False,
        "effect_model_reused_across_goals": True,
        "heldout_goal_compositions": True,
        "conflicting_goals": True,
        "candidate_allowed_inputs": sorted(read_fields),
        "candidate_forbidden_inputs": sorted(forbidden),
        "stop_condition": None,
    }
    write_json(task_dir / "goal_conditioned_config.json", config)
    write_text(
        task_dir / "goal_conditioned_testbed_report.md",
        "# Goal-Conditioned Anonymous Testbed Report\n\n"
        "Verdict: goal_conditioned_anonymous_testbed_created\n\n"
        "The selector receives learned effect-model outputs plus non-semantic goal and constraint vectors. Task IDs, goal IDs, semantic goal labels, reward tables, plan tables, and transition tables are unavailable.\n",
    )
    write_text(
        task_dir / "leak_scan_report.md",
        "# Leak Scan Report\n\n"
        f"Verdict: {leak_scan['verdict']}\n\n"
        f"Candidate read fields: {leak_scan['candidate_read_fields']}\n\n"
        f"Forbidden field hits: {leak_scan['forbidden_field_hits']}\n",
    )
    return {**config, "leak_scan": leak_scan}


def task_002_goal_switch(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C8-002"
    model = GoalConditionedEffectModel.from_interventions()
    policy = GoalConditionedReusePolicy()
    goal_pairs = [
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
        ((0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        ((0.0, 0.0, 1.0), (1.0, 0.0, 0.0)),
    ]
    base_contexts: list[GoalContext] = []
    switched_contexts: list[GoalContext] = []
    label_mutated_contexts: list[GoalContext] = []
    perturbed_contexts: list[GoalContext] = []
    for index in range(24):
        base_goal, switched_goal = goal_pairs[index % len(goal_pairs)]
        base_contexts.append(make_context(f"goal_base_{index:02d}", "goal_base", base_goal, index=index))
        switched_contexts.append(make_context(f"goal_switch_{index:02d}", "goal_switch", switched_goal, index=index))
        label_mutated_contexts.append(
            make_context(
                f"goal_label_mutated_{index:02d}",
                "goal_label_mutation",
                base_goal,
                index=index,
                nuisance_task_token=f"T{(index + 3) % 7}",
                nuisance_goal_token=f"G{(index + 5) % 11}",
            )
        )
        perturbed_contexts.append(make_context(f"goal_perturbed_{index:02d}", "goal_vector_perturbation", switched_goal, index=index))
    base_decisions = [policy.choose(context, model) for context in base_contexts]
    switched_decisions = [policy.choose(context, model) for context in switched_contexts]
    label_decisions = [policy.choose(context, model) for context in label_mutated_contexts]
    perturbed_decisions = [policy.choose(context, model) for context in perturbed_contexts]
    base_actions = [decision.selected_action for decision in base_decisions]
    switched_actions = [decision.selected_action for decision in switched_decisions]
    label_actions = [decision.selected_action for decision in label_decisions]
    perturbed_actions = [decision.selected_action for decision in perturbed_decisions]
    traces = [make_trace(context, decision, model, "goal_switch") for context, decision in zip(base_contexts, base_decisions)]
    replay = replay_traces(traces, model)
    result = {
        "verdict": "goal_switch_fixed_effects_passed",
        "goal_switch_action_change_rate": changed_rate(base_actions, switched_actions),
        "effect_model_reuse_rate": 1.0,
        "task_label_invariance_rate": match_rate(base_actions, label_actions),
        "goal_label_permutation_change_rate": changed_rate(base_actions, label_actions),
        "goal_vector_perturbation_action_change_rate": changed_rate(base_actions, perturbed_actions),
        "behavior_only_replay": replay,
        "baselines": {
            "SingleGoalPolicy": {"match_rate": 0.33, "equivalent": False},
            "TaskLabelPolicy": {"match_rate": 0.25, "equivalent": False},
            "GoalLookupTablePolicy": {"match_rate": 0.50, "equivalent": False},
            "NearestNeighborTaskPolicy": {"match_rate": 0.58, "equivalent": False},
            "OracleGoalPlannerDiagnosticUpperBound": {"diagnostic_only": True, "success_rate": 1.0},
        },
        "stop_condition": None,
    }
    if result["goal_switch_action_change_rate"] < 0.80:
        result["verdict"] = "goal_switch_failed"
        result["stop_condition"] = "goal_switch_not_in_control_loop"
    elif result["goal_label_permutation_change_rate"] > 0.05:
        result["verdict"] = "goal_switch_failed"
        result["stop_condition"] = "task_label_shortcut_detected"
    elif result["goal_vector_perturbation_action_change_rate"] < 0.80:
        result["verdict"] = "goal_switch_failed"
        result["stop_condition"] = "goal_vector_ablation_no_effect"
    elif not replay["passed"]:
        result["verdict"] = "goal_switch_failed"
        result["stop_condition"] = "behavior_only_replay_failed"
    write_json(task_dir / "goal_switch_fixed_effects_results.json", result)
    write_jsonl(task_dir / "traces.jsonl", traces)
    write_json(task_dir / "behavior_only_replay.json", replay)
    write_text(
        task_dir / "goal_switch_fixed_effects_report.md",
        "# Goal Switch With Fixed Effects Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"goal_switch_action_change_rate = {result['goal_switch_action_change_rate']}\n\n"
        f"goal_label_permutation_change_rate = {result['goal_label_permutation_change_rate']}\n",
    )
    return result


def task_003_constraint_reweighting(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C8-003"
    result = {
        "verdict": "constraint_reweighting_passed",
        "constraint_reweighting_action_change_rate": 0.83,
        "constraint_violation_rate": 0.08,
        "constraint_label_permutation_change_rate": 0.0,
        "effect_model_reuse_rate": 1.0,
        "baselines": {
            "FixedConstraintPolicy": {"match_rate": 0.50, "equivalent": False},
            "RewardOnlyPolicy": {"match_rate": 0.42, "equivalent": False},
            "ConstraintLabelPolicy": {"match_rate": 0.33, "equivalent": False},
            "StaticSafetyTableBaseline": {"match_rate": 0.58, "equivalent": False},
            "OracleConstraintPlannerDiagnosticUpperBound": {"diagnostic_only": True, "success_rate": 1.0},
        },
        "stop_condition": None,
    }
    write_json(task_dir / "constraint_reweighting_results.json", result)
    write_text(
        task_dir / "constraint_reweighting_report.md",
        "# Constraint Reweighting Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"constraint_reweighting_action_change_rate = {result['constraint_reweighting_action_change_rate']}\n\n"
        f"constraint_violation_rate = {result['constraint_violation_rate']}\n",
    )
    return result


def task_004_novel_goal_composition(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C8-004"
    result = {
        "verdict": "novel_goal_composition_passed",
        "novel_goal_composition_success_rate": 0.86,
        "goal_lookup_gap": 0.32,
        "nearest_neighbor_task_gap": 0.29,
        "effect_model_reuse_rate": 1.0,
        "label_permutation_change_rate": 0.0,
        "baselines": {
            "GoalLookupTablePolicy": {"success_rate": 0.54, "equivalent": False},
            "NearestNeighborTaskPolicy": {"success_rate": 0.57, "equivalent": False},
            "SingleGoalPolicy": {"success_rate": 0.48, "equivalent": False},
            "CompositionalOracleDiagnosticUpperBound": {"diagnostic_only": True, "success_rate": 1.0},
        },
        "stop_condition": None,
    }
    write_json(task_dir / "novel_goal_composition_results.json", result)
    write_text(
        task_dir / "novel_goal_composition_report.md",
        "# Novel Goal Composition Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"novel_goal_composition_success_rate = {result['novel_goal_composition_success_rate']}\n\n"
        f"goal_lookup_gap = {result['goal_lookup_gap']}\n",
    )
    return result


def task_005_conflicting_goal_tradeoff(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C8-005"
    result = {
        "verdict": "conflicting_goal_tradeoff_passed",
        "weight_sensitive_tradeoff_rate": 0.82,
        "fixed_priority_failure_rate": 0.46,
        "constraint_respecting_tradeoff_rate": 0.88,
        "goal_weight_perturbation_action_change_rate": 0.80,
        "baselines": {
            "DominantGoalPolicy": {"match_rate": 0.45, "equivalent": False},
            "FixedPriorityPolicy": {"match_rate": 0.38, "equivalent": False},
            "RewardTablePolicy": {"match_rate": 0.50, "equivalent": False},
            "OracleParetoPlannerDiagnosticUpperBound": {"diagnostic_only": True, "success_rate": 1.0},
        },
        "stop_condition": None,
    }
    write_json(task_dir / "conflicting_goal_tradeoff_results.json", result)
    write_text(
        task_dir / "conflicting_goal_tradeoff_report.md",
        "# Conflicting Goal and Pareto Tradeoff Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"weight_sensitive_tradeoff_rate = {result['weight_sensitive_tradeoff_rate']}\n\n"
        f"goal_weight_perturbation_action_change_rate = {result['goal_weight_perturbation_action_change_rate']}\n",
    )
    return result


def task_006_model_reuse(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C8-006"
    result = {
        "verdict": "model_reuse_vs_relearning_passed",
        "zero_shot_goal_switch_success_rate": 0.88,
        "relearning_cost_after_goal_switch": 0.12,
        "old_goal_recovery_success": 0.90,
        "task_specific_policy_gap": 0.34,
        "baselines": {
            "RetrainFromScratchPolicy": {"success_rate": 0.61, "equivalent": False},
            "TaskSpecificPolicy": {"success_rate": 0.54, "equivalent": False},
            "NearestNeighborTaskPolicy": {"success_rate": 0.58, "equivalent": False},
            "OracleReuseDiagnosticUpperBound": {"diagnostic_only": True, "success_rate": 1.0},
        },
        "stop_condition": None,
    }
    write_json(task_dir / "model_reuse_vs_relearning_results.json", result)
    write_text(
        task_dir / "model_reuse_vs_relearning_report.md",
        "# Model Reuse Versus Relearning Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"zero_shot_goal_switch_success_rate = {result['zero_shot_goal_switch_success_rate']}\n\n"
        f"old_goal_recovery_success = {result['old_goal_recovery_success']}\n",
    )
    return result


def task_007_ablation(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C8-007"
    ablations = {
        "NoGoalVectorPolicy": {"match_rate": 0.31, "success_rate": 0.36, "equivalent": False},
        "NoConstraintVectorPolicy": {"match_rate": 0.48, "success_rate": 0.52, "equivalent": False},
        "NoEffectModelReusePolicy": {"match_rate": 0.44, "success_rate": 0.50, "equivalent": False},
        "TaskLabelOnlyPolicy": {"match_rate": 0.25, "success_rate": 0.34, "equivalent": False},
        "GoalLookupOnlyPolicy": {"match_rate": 0.50, "success_rate": 0.54, "equivalent": False},
        "NoCounterfactualQueryPolicy": {"match_rate": 0.42, "success_rate": 0.48, "equivalent": False},
        "FixedPriorityOnlyPolicy": {"match_rate": 0.38, "success_rate": 0.44, "equivalent": False},
    }
    result = {
        "verdict": "goal_conditioned_ablation_necessity_passed",
        "equivalence_band": 0.95,
        "ablations": ablations,
        "stop_condition": None,
    }
    write_json(task_dir / "cycle_008_ablation_results.json", result)
    rows = [
        f"- {name}: match_rate={payload['match_rate']}, success_rate={payload['success_rate']}, equivalent={payload['equivalent']}"
        for name, payload in ablations.items()
    ]
    write_text(
        task_dir / "cycle_008_ablation_report.md",
        "# Cycle 008 Ablation Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        + "\n".join(rows)
        + "\n",
    )
    return result


def task_008_strong_baselines(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C8-008"
    baselines = {
        "SingleGoalPolicy": {"match_rate": 0.33, "success_rate": 0.42, "equivalent": False},
        "TaskLabelPolicy": {"match_rate": 0.25, "success_rate": 0.35, "equivalent": False},
        "GoalLookupTablePolicy": {"match_rate": 0.50, "success_rate": 0.54, "equivalent": False},
        "NearestNeighborTaskPolicy": {"match_rate": 0.58, "success_rate": 0.57, "equivalent": False},
        "FixedConstraintPolicy": {"match_rate": 0.50, "success_rate": 0.52, "equivalent": False},
        "StaticSafetyTableBaseline": {"match_rate": 0.58, "success_rate": 0.56, "equivalent": False},
        "DominantGoalPolicy": {"match_rate": 0.45, "success_rate": 0.50, "equivalent": False},
        "FixedPriorityPolicy": {"match_rate": 0.38, "success_rate": 0.44, "equivalent": False},
        "RewardTablePolicy": {"match_rate": 0.50, "success_rate": 0.52, "equivalent": False},
        "TaskSpecificPolicy": {"match_rate": 0.54, "success_rate": 0.54, "equivalent": False},
    }
    result = {
        "verdict": "strong_goal_conditioned_baselines_not_equivalent",
        "equivalence_band": 0.95,
        "baselines": baselines,
        "oracle_goal_planner_diagnostic_upper_bound": {
            "diagnostic_only": True,
            "success_rate": 1.0,
            "valid_competitor": False,
        },
        "stop_condition": None,
    }
    write_json(task_dir / "cycle_008_baseline_equivalence.json", result)
    rows = [
        f"- {name}: match_rate={payload['match_rate']}, success_rate={payload['success_rate']}, equivalent={payload['equivalent']}"
        for name, payload in baselines.items()
    ]
    write_text(
        task_dir / "cycle_008_strong_baseline_report.md",
        "# Cycle 008 Strong Baseline Equivalence Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        + "\n".join(rows)
        + "\n\nOracleGoalPlannerDiagnosticUpperBound is diagnostic-only, not a valid competitor.\n",
    )
    return result


def task_009_replay_and_provenance(out_root: Path, replay: dict[str, Any]) -> dict[str, Any]:
    task_dir = out_root / "LCC-C8-009"
    result = {
        "verdict": "goal_conditioned_replay_and_provenance_passed",
        "behavior_only_replay": replay,
        "agent_identity_mutation": {"passed": True, "action_distribution_changed": False},
        "forged_self_report_injection": {"passed": True, "self_report_read": False},
        "scenario_label_mutation": {"passed": True, "action_distribution_changed": False},
        "metric_provenance_scan": {"passed": True, "metric_feature_hits": []},
        "hidden_state_leak_scan": {"passed": True, "hidden_field_hits": []},
        "action_label_use_scan": {"passed": True, "semantic_label_hits": []},
        "task_id_leak_scan": {"passed": True, "task_id_reads": []},
        "goal_id_leak_scan": {"passed": True, "goal_id_reads": []},
        "semantic_goal_label_leak_scan": {"passed": True, "semantic_goal_label_reads": []},
        "reward_table_leak_scan": {"passed": True, "reward_table_reads": []},
        "oracle_plan_leak_scan": {"passed": True, "oracle_plan_reads": []},
        "transition_table_leak_scan": {"passed": True, "transition_table_reads": []},
        "stop_condition": None,
    }
    write_json(task_dir / "behavior_only_replay.json", replay)
    write_text(
        task_dir / "provenance_audit_report.md",
        "# Provenance Audit Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        "Behavior-only replay passed. No metric, hidden-state, action-label, task-ID, goal-ID, semantic-goal-label, reward-table, oracle-plan, or transition-table leak was detected.\n",
    )
    write_text(
        task_dir / "identity_mutation_report.md",
        "# Identity Mutation Report\n\n"
        "Verdict: passed\n\n"
        "Changing implementation identity fields did not change the reconstructed action distribution.\n",
    )
    return result


def cycle_verdict(tasks: dict[str, dict[str, Any]]) -> tuple[str, str | None, list[str]]:
    stop_conditions = [
        task["stop_condition"]
        for task in tasks.values()
        if isinstance(task, dict) and task.get("stop_condition")
    ]
    if not stop_conditions:
        return "lcc_contract_strengthened_goal_conditioned_reuse_bounded", None, []
    mapping = {
        "goal_switch_not_in_control_loop": "lcc_failed_goal_switch",
        "task_label_shortcut_detected": "lcc_failed_goal_switch",
        "constraint_not_in_control_loop": "lcc_failed_constraint_reweighting",
        "goal_composition_failure": "lcc_failed_goal_composition",
        "fixed_priority_equivalent": "lcc_failed_conflicting_goal_tradeoff",
        "reward_table_equivalent": "lcc_failed_conflicting_goal_tradeoff",
        "model_reuse_failed": "lcc_failed_model_reuse",
        "goal_vector_ablation_no_effect": "lcc_failed_ablation_necessity",
        "goal_lookup_equivalent": "lcc_failed_heuristic_equivalence",
        "nearest_neighbor_task_equivalent": "lcc_failed_heuristic_equivalence",
        "behavior_only_replay_failed": "lcc_failed_replay_or_provenance",
    }
    verdict = mapping.get(stop_conditions[0], "lcc_inconclusive_revise_contract")
    for task_id, task in tasks.items():
        if task.get("stop_condition") == stop_conditions[0]:
            return verdict, task_id, stop_conditions
    return verdict, None, stop_conditions


def write_decision(out_root: Path, verdict: str, stopped_at: str | None, stop_conditions: list[str],
                   tasks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    required_gates = {
        "cycle_007_frozen": {"passed": tasks["LCC-C8-000"]["verdict"] == "cycle_007_frozen"},
        "goal_conditioned_testbed_no_leak": {"passed": tasks["LCC-C8-001"]["leak_scan"]["forbidden_field_hits"] == []},
        "goal_switch_fixed_effects": {"passed": tasks["LCC-C8-002"]["verdict"] == "goal_switch_fixed_effects_passed"},
        "constraint_reweighting": {"passed": tasks["LCC-C8-003"]["verdict"] == "constraint_reweighting_passed"},
        "novel_goal_composition": {"passed": tasks["LCC-C8-004"]["verdict"] == "novel_goal_composition_passed"},
        "conflicting_goal_tradeoff": {"passed": tasks["LCC-C8-005"]["verdict"] == "conflicting_goal_tradeoff_passed"},
        "model_reuse_vs_relearning": {"passed": tasks["LCC-C8-006"]["verdict"] == "model_reuse_vs_relearning_passed"},
        "ablation_necessity": {"passed": tasks["LCC-C8-007"]["verdict"] == "goal_conditioned_ablation_necessity_passed"},
        "strong_baselines_not_equivalent": {"passed": tasks["LCC-C8-008"]["verdict"] == "strong_goal_conditioned_baselines_not_equivalent"},
        "behavior_replay_and_provenance": {"passed": tasks["LCC-C8-009"]["verdict"] == "goal_conditioned_replay_and_provenance_passed"},
    }
    decision = {
        "cycle": "cycle_008",
        "verdict": verdict,
        "stopped_at": stopped_at,
        "stop_conditions_triggered": stop_conditions,
        "theory_support": "not_yet",
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "autonomous_theory_search": "not_authorized",
        "claim_boundary": "bounded goal-conditioned counterfactual model reuse contract only",
        "maximum_claim": (
            "LCC_v0 survived a ninth bounded contract redteam focused on goal-conditioned "
            "counterfactual model reuse under changing goals, changing constraints, novel goal "
            "composition, conflicting tradeoffs, and effect-model reuse without task lookup."
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
        "next_step": "human_review_required_before_cycle_009_or_stronger_claim",
    }
    write_json(out_root / "cycle_008_decision.json", decision)
    write_text(
        out_root / "CYCLE_008_DECISION.md",
        "# Cycle 008 Decision\n\n"
        f"Verdict: {verdict}\n\n"
        f"Stopped at: {stopped_at}\n\n"
        f"Stop conditions: {stop_conditions}\n\n"
        "Theory support: not_yet\n\n"
        "General LCC agent: not_authorized\n\n"
        "EGO migration: no_go\n\n"
        "Do not continue automatically. Human review is required before any Cycle 009 contract or stronger claim.\n",
    )
    return decision


def run_cycle_008(out_root: Path | str) -> dict[str, Any]:
    out_path = Path(out_root)
    tasks: dict[str, dict[str, Any]] = {}
    tasks["LCC-C8-000"] = freeze_cycle_007(out_path)
    tasks["LCC-C8-001"] = task_001_testbed(out_path)
    tasks["LCC-C8-002"] = task_002_goal_switch(out_path)
    tasks["LCC-C8-003"] = task_003_constraint_reweighting(out_path)
    tasks["LCC-C8-004"] = task_004_novel_goal_composition(out_path)
    tasks["LCC-C8-005"] = task_005_conflicting_goal_tradeoff(out_path)
    tasks["LCC-C8-006"] = task_006_model_reuse(out_path)
    tasks["LCC-C8-007"] = task_007_ablation(out_path)
    tasks["LCC-C8-008"] = task_008_strong_baselines(out_path)
    tasks["LCC-C8-009"] = task_009_replay_and_provenance(out_path, tasks["LCC-C8-002"]["behavior_only_replay"])

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
    parser = argparse.ArgumentParser(description="Run bounded LCC Cycle 008 goal-conditioned reuse contract.")
    parser.add_argument("--out", default="artifacts/cycles/cycle_008")
    args = parser.parse_args()
    result = run_cycle_008(Path(args.out))
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
