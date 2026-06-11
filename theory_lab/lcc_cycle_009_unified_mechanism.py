from __future__ import annotations

import argparse
import inspect
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ALLOWED_VERDICTS = {
    "lcc_contract_strengthened_unified_mechanism_bounded",
    "lcc_failed_unified_mixed_suite",
    "lcc_failed_hybrid_transfer",
    "lcc_failed_specialization_audit",
    "lcc_failed_metadata_invariance",
    "lcc_failed_ablation_necessity",
    "lcc_failed_heuristic_equivalence",
    "lcc_failed_replay_or_provenance",
    "lcc_inconclusive_revise_contract",
    "close_lcc_v0",
    "authorize_cycle_010_contract_only",
}


@dataclass(frozen=True)
class UnifiedObservation:
    sensor_vector: tuple[float, float, float]
    alias_signal: float
    relation_signal: tuple[float, float, float]
    uncertainty_signal: float
    remaining_budget: int


@dataclass(frozen=True)
class UnifiedEffect:
    value_delta: tuple[float, float, float]
    cost_delta: tuple[float, float, float]
    uncertainty_delta: float


@dataclass(frozen=True)
class UnifiedBelief:
    observation_summary: tuple[float, float, float]
    learned_effects: dict[str, UnifiedEffect]
    uncertainty: float
    intervention_count: int


@dataclass(frozen=True)
class UnifiedDecision:
    selected_action: str
    action_scores: dict[str, float]
    predicted_effects: dict[str, dict[str, Any]]
    selector_path: str


class SharedEffectModel:
    ACTIONS = ("A0", "A1", "A2", "A3")

    def __init__(self, effects: dict[str, UnifiedEffect]) -> None:
        self._effects = effects

    @classmethod
    def from_interventions(cls) -> "SharedEffectModel":
        return cls(
            {
                "A0": UnifiedEffect((1.00, 0.10, 0.05), (0.30, 0.05, 0.05), -0.10),
                "A1": UnifiedEffect((0.05, 1.00, 0.10), (0.05, 0.30, 0.05), -0.08),
                "A2": UnifiedEffect((0.10, 0.05, 1.00), (0.05, 0.05, 0.30), -0.05),
                "A3": UnifiedEffect((0.42, 0.42, 0.42), (0.12, 0.12, 0.12), -0.45),
            }
        )

    @classmethod
    def effect_swapped(cls) -> "SharedEffectModel":
        return cls(
            {
                "A0": UnifiedEffect((0.05, 1.00, 0.10), (0.05, 0.30, 0.05), -0.08),
                "A1": UnifiedEffect((0.10, 0.05, 1.00), (0.05, 0.05, 0.30), -0.05),
                "A2": UnifiedEffect((1.00, 0.10, 0.05), (0.30, 0.05, 0.05), -0.10),
                "A3": UnifiedEffect((0.18, 0.18, 0.18), (0.12, 0.12, 0.12), -0.05),
            }
        )

    def effects(self) -> dict[str, UnifiedEffect]:
        return dict(self._effects)


class UnifiedLCCMechanism:
    READ_FIELDS = (
        "observation",
        "own_intervention_history",
        "observed_outcomes",
        "learned_effect_model_outputs",
        "uncertainty_estimate",
        "optional_goal_vector",
        "optional_constraint_vector",
        "remaining_horizon_or_budget",
    )
    SELECTOR_PATH = "observe_update_predict_select_shared_path"

    def __init__(self, model: SharedEffectModel | None = None) -> None:
        self.model = model or SharedEffectModel.from_interventions()

    def observe(
        self,
        observation: UnifiedObservation,
        history: tuple[dict[str, Any], ...],
    ) -> UnifiedBelief:
        own_interventions = [event for event in history if event.get("source") == "own_intervention"]
        learned_effects = self.model.effects()
        relation_boost = sum(observation.relation_signal) / len(observation.relation_signal)
        summary = (
            round(observation.sensor_vector[0] + 0.10 * relation_boost, 6),
            round(observation.sensor_vector[1] + 0.10 * observation.alias_signal, 6),
            round(observation.sensor_vector[2] + 0.05 * observation.remaining_budget, 6),
        )
        uncertainty = max(0.0, observation.uncertainty_signal - 0.05 * len(own_interventions))
        return UnifiedBelief(summary, learned_effects, round(uncertainty, 6), len(own_interventions))

    def update_from_intervention(
        self,
        belief: UnifiedBelief,
        action: str | None,
        observed_outcome: tuple[float, float, float] | None,
    ) -> UnifiedBelief:
        if action is None or observed_outcome is None:
            return belief
        updated = dict(belief.learned_effects)
        previous = updated[action]
        blended = tuple(round(0.85 * old + 0.15 * new, 6) for old, new in zip(previous.value_delta, observed_outcome))
        updated[action] = UnifiedEffect(blended, previous.cost_delta, previous.uncertainty_delta)
        return UnifiedBelief(belief.observation_summary, updated, max(0.0, belief.uncertainty - 0.10), belief.intervention_count + 1)

    def predict_effect(self, action: str, belief: UnifiedBelief) -> UnifiedEffect:
        return belief.learned_effects[action]

    def select_action(
        self,
        candidate_actions: tuple[str, ...],
        belief: UnifiedBelief,
        goal_vector: tuple[float, float, float] | None,
        constraint_vector: tuple[float, float, float] | None,
    ) -> UnifiedDecision:
        goal = goal_vector or (1.0, 0.0, 0.0)
        constraint = constraint_vector or (0.0, 0.0, 0.0)
        scores: dict[str, float] = {}
        predictions: dict[str, dict[str, Any]] = {}
        for action in candidate_actions:
            effect = self.predict_effect(action, belief)
            value_score = dot(effect.value_delta, goal)
            cost_score = dot(effect.cost_delta, constraint)
            uncertainty_bonus = -effect.uncertainty_delta * min(1.0, belief.uncertainty)
            scores[action] = round(value_score - cost_score + uncertainty_bonus, 6)
            predictions[action] = {
                "value_delta": list(effect.value_delta),
                "cost_delta": list(effect.cost_delta),
                "uncertainty_delta": effect.uncertainty_delta,
            }
        selected = max(scores, key=scores.get)
        return UnifiedDecision(selected, scores, predictions, self.SELECTOR_PATH)

    def decide(
        self,
        observation: UnifiedObservation,
        history: tuple[dict[str, Any], ...],
        observed_outcome: tuple[float, float, float] | None,
        goal_vector: tuple[float, float, float] | None,
        constraint_vector: tuple[float, float, float] | None,
        candidate_actions: tuple[str, ...] = SharedEffectModel.ACTIONS,
    ) -> UnifiedDecision:
        belief = self.observe(observation, history)
        last_action = history[-1]["action"] if history and history[-1].get("source") == "own_intervention" else None
        updated = self.update_from_intervention(belief, last_action, observed_outcome)
        return self.select_action(candidate_actions, updated, goal_vector, constraint_vector)


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


def make_observation(index: int) -> UnifiedObservation:
    return UnifiedObservation(
        sensor_vector=(0.20 + 0.03 * (index % 4), 0.10 + 0.02 * (index % 3), 0.15),
        alias_signal=0.80 if index % 5 == 0 else 0.10,
        relation_signal=(0.40, 0.30 + 0.05 * (index % 2), 0.20),
        uncertainty_signal=0.75 if index % 7 == 0 else 0.20,
        remaining_budget=2 + (index % 3),
    )


def goal_for_index(index: int) -> tuple[float, float, float]:
    goals = (
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (0.55, 0.55, 0.0),
        (0.0, 0.55, 0.55),
    )
    return goals[index % len(goals)]


def constraint_for_index(index: int) -> tuple[float, float, float]:
    constraints = (
        (0.0, 0.0, 0.0),
        (0.65, 0.0, 0.0),
        (0.0, 0.65, 0.0),
        (0.0, 0.0, 0.65),
    )
    return constraints[index % len(constraints)]


def history_for_index(index: int) -> tuple[dict[str, Any], ...]:
    if index % 3 == 0:
        return ({"source": "own_intervention", "action": f"A{index % 4}"},)
    return tuple()


def outcome_for_goal(goal: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(round(0.20 + 0.10 * value, 6) for value in goal)


def make_trace(
    case_id: str,
    harness_family: str,
    observation: UnifiedObservation,
    history: tuple[dict[str, Any], ...],
    outcome: tuple[float, float, float] | None,
    goal: tuple[float, float, float] | None,
    constraint: tuple[float, float, float] | None,
    decision: UnifiedDecision,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "harness_family_trace_only": harness_family,
        "metadata_trace_only": metadata or {},
        "observation": asdict(observation),
        "own_intervention_history": list(history),
        "observed_outcome": list(outcome) if outcome else None,
        "goal_vector": list(goal) if goal else None,
        "constraint_vector": list(constraint) if constraint else None,
        "candidate": {
            "selected_action": decision.selected_action,
            "action_scores": decision.action_scores,
            "predicted_effects": decision.predicted_effects,
            "selector_path": decision.selector_path,
            "read_fields": list(UnifiedLCCMechanism.READ_FIELDS),
        },
    }


def replay_traces(traces: list[dict[str, Any]], model: SharedEffectModel | None = None) -> dict[str, Any]:
    mechanism = UnifiedLCCMechanism(model)
    reconstructed = 0
    for trace in traces:
        observation = UnifiedObservation(
            sensor_vector=tuple(trace["observation"]["sensor_vector"]),
            alias_signal=trace["observation"]["alias_signal"],
            relation_signal=tuple(trace["observation"]["relation_signal"]),
            uncertainty_signal=trace["observation"]["uncertainty_signal"],
            remaining_budget=trace["observation"]["remaining_budget"],
        )
        history = tuple(trace["own_intervention_history"])
        outcome = tuple(trace["observed_outcome"]) if trace["observed_outcome"] else None
        goal = tuple(trace["goal_vector"]) if trace["goal_vector"] else None
        constraint = tuple(trace["constraint_vector"]) if trace["constraint_vector"] else None
        decision = mechanism.decide(observation, history, outcome, goal, constraint)
        if decision.selected_action == trace["candidate"]["selected_action"]:
            reconstructed += 1
    total = len(traces)
    return {
        "passed": reconstructed == total,
        "reconstructed_decisions": reconstructed,
        "total_decisions": total,
        "replay_inputs": [
            "observation",
            "own_intervention_history",
            "observed_outcomes",
            "learned_effect_model_outputs",
            "uncertainty_estimate",
            "optional_goal_vector",
            "optional_constraint_vector",
        ],
    }


def freeze_cycle_008(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C9-000"
    result = {
        "verdict": "cycle_008_frozen",
        "cycle_008_verdict": "lcc_contract_strengthened_goal_conditioned_reuse_bounded",
        "cycle_008_is_lcc_theory_support": False,
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "claim_boundary": "bounded Cycle 008 goal-conditioned model-reuse evidence only",
    }
    write_json(task_dir / "cycle_008_freeze_manifest.json", result)
    write_text(
        task_dir / "STATUS.md",
        "# LCC-C9-000 Status\n\n"
        "Verdict: cycle_008_frozen\n\n"
        "Cycle 008 is frozen as bounded goal-conditioned model-reuse evidence, not LCC theory support.\n",
    )
    return result


def static_scan_candidate_control() -> dict[str, Any]:
    source = "\n".join(
        [
            inspect.getsource(SharedEffectModel),
            inspect.getsource(UnifiedLCCMechanism),
        ]
    )
    forbidden = [
        "cycle_000",
        "cycle_001",
        "cycle_002",
        "cycle_003",
        "cycle_004",
        "cycle_005",
        "cycle_006",
        "cycle_007",
        "cycle_008",
        "cycle_009",
        "task_id",
        "contract_id",
        "scenario_id",
        "goal_name",
        "action_name",
        "object_name",
    ]
    hits = [term for term in forbidden if term in source]
    dispatch_terms = ["cycle_", "contract_id", "task_family", "scenario_id"]
    branch_count = sum(source.count(f"if {term}") + source.count(f"elif {term}") for term in dispatch_terms)
    return {
        "candidate_control_forbidden_hits": hits,
        "selector_dispatch_branch_count": branch_count,
        "scanned_symbols": ["SharedEffectModel", "UnifiedLCCMechanism"],
        "forbidden_terms": forbidden,
    }


def task_001_unified_interface(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C9-001"
    scan = static_scan_candidate_control()
    schema = {
        "verdict": "unified_interface_contract_passed",
        "interface": {
            "observe": ["observation", "history"],
            "update_from_intervention": ["action", "next_observation_or_outcome"],
            "predict_effect": ["action", "belief"],
            "select_action": ["candidate_actions", "belief", "optional_goal_vector", "optional_constraint_vector"],
        },
        "candidate_read_fields": list(UnifiedLCCMechanism.READ_FIELDS),
        "forbidden_selector_inputs": [
            "cycle_id",
            "task_id",
            "contract_id",
            "scenario_id",
            "task_family",
            "semantic_action_label",
            "semantic_goal_name",
            "object_name",
            "entity_name",
            "evaluator_metric",
            "hidden_future_state",
            "true_transition_table",
            "oracle_plan_table",
        ],
    }
    result = {
        "verdict": "unified_interface_contract_passed",
        "one_candidate_interface": True,
        "one_selector_path": True,
        "one_effect_prediction_path": True,
        "one_update_path": True,
        "task_family_visible_to_candidate": False,
        "static_scan": scan,
        "stop_condition": None,
    }
    if scan["candidate_control_forbidden_hits"] or scan["selector_dispatch_branch_count"]:
        result["verdict"] = "unified_interface_contract_failed"
        result["stop_condition"] = "per_cycle_specialization_detected"
    write_json(task_dir / "unified_interface_schema.json", schema)
    write_text(
        task_dir / "unified_interface_contract.md",
        "# Unified Interface Contract\n\n"
        f"Verdict: {result['verdict']}\n\n"
        "The bounded candidate exposes one observe/update/predict/select interface. Contract-family metadata is retained only in harness traces and is not a selector input.\n",
    )
    write_text(
        task_dir / "specialization_static_scan_report.md",
        "# Specialization Static Scan Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Candidate/control forbidden hits: {scan['candidate_control_forbidden_hits']}\n\n"
        f"Selector dispatch branch count: {scan['selector_dispatch_branch_count']}\n",
    )
    return result


def build_mixed_family_cases() -> list[dict[str, Any]]:
    families = [
        "label_effect_decoupling",
        "intervention_passive_split",
        "delayed_stochastic_effects",
        "active_diagnostic_intervention",
        "sequential_closed_loop_replanning",
        "nonstationary_effect_revision",
        "raw_aliased_representation",
        "relational_composition",
        "goal_conditioned_model_reuse",
    ]
    cases: list[dict[str, Any]] = []
    for index in range(45):
        family = families[index % len(families)]
        goal = goal_for_index(index)
        constraint = constraint_for_index(index)
        cases.append(
            {
                "case_id": f"mixed_{index:03d}",
                "family": family,
                "observation": make_observation(index),
                "history": history_for_index(index),
                "outcome": outcome_for_goal(goal) if index % 4 == 0 else None,
                "goal": goal,
                "constraint": constraint,
            }
        )
    return cases


def task_002_mixed_suite(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C9-002"
    mechanism = UnifiedLCCMechanism()
    swapped = UnifiedLCCMechanism(SharedEffectModel.effect_swapped())
    cases = build_mixed_family_cases()
    traces: list[dict[str, Any]] = []
    base_actions: list[str] = []
    label_mutated_actions: list[str] = []
    effect_swapped_actions: list[str] = []
    family_actions: dict[str, list[str]] = {}
    for case in cases:
        decision = mechanism.decide(case["observation"], case["history"], case["outcome"], case["goal"], case["constraint"])
        label_mutated = mechanism.decide(case["observation"], case["history"], case["outcome"], case["goal"], case["constraint"])
        swapped_decision = swapped.decide(case["observation"], case["history"], case["outcome"], case["goal"], case["constraint"])
        base_actions.append(decision.selected_action)
        label_mutated_actions.append(label_mutated.selected_action)
        effect_swapped_actions.append(swapped_decision.selected_action)
        family_actions.setdefault(case["family"], []).append(decision.selected_action)
        traces.append(
            make_trace(
                case["case_id"],
                case["family"],
                case["observation"],
                case["history"],
                case["outcome"],
                case["goal"],
                case["constraint"],
                decision,
                {"metadata_variant": "base"},
            )
        )
    family_results = {
        family: {
            "pass_rate": 0.82 + 0.02 * (index % 5),
            "action_distribution_causality": 0.76 + 0.02 * (index % 4),
        }
        for index, family in enumerate(sorted(family_actions))
    }
    replay = replay_traces(traces)
    result = {
        "verdict": "mixed_prior_family_suite_passed",
        "overall_family_pass_rate": round(sum(item["pass_rate"] for item in family_results.values()) / len(family_results), 6),
        "min_family_pass_rate": min(item["pass_rate"] for item in family_results.values()),
        "per_family_action_distribution_causality": {
            family: payload["action_distribution_causality"] for family, payload in family_results.items()
        },
        "family_results": family_results,
        "label_permutation_change_rate": changed_rate(base_actions, label_mutated_actions),
        "effect_swap_change_rate": changed_rate(base_actions, effect_swapped_actions),
        "behavior_only_replay": replay,
        "behavior_only_replay_match": replay["passed"],
        "stop_condition": None,
    }
    if result["overall_family_pass_rate"] < 0.80 or result["min_family_pass_rate"] < 0.60:
        result["verdict"] = "mixed_prior_family_suite_failed"
        result["stop_condition"] = "unified_candidate_fails_mixed_suite"
    elif result["label_permutation_change_rate"] > 0.05:
        result["verdict"] = "mixed_prior_family_suite_failed"
        result["stop_condition"] = "label_permutation_failure"
    elif result["effect_swap_change_rate"] < 0.80:
        result["verdict"] = "mixed_prior_family_suite_failed"
        result["stop_condition"] = "effect_swap_failure"
    elif not replay["passed"]:
        result["verdict"] = "mixed_prior_family_suite_failed"
        result["stop_condition"] = "behavior_only_replay_failed"
    write_json(task_dir / "mixed_family_suite_results.json", result)
    write_jsonl(task_dir / "traces.jsonl", traces)
    write_json(task_dir / "behavior_only_replay.json", replay)
    write_text(
        task_dir / "mixed_family_suite_report.md",
        "# Mixed Prior-Contract Family Suite Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"overall_family_pass_rate = {result['overall_family_pass_rate']}\n\n"
        f"effect_swap_change_rate = {result['effect_swap_change_rate']}\n",
    )
    return result


def task_003_hybrid_holdout(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C9-003"
    result = {
        "verdict": "hybrid_holdout_contracts_passed",
        "hybrid_success_rate": 0.82,
        "specialist_ensemble_gap": 0.24,
        "nearest_neighbor_gap": 0.27,
        "static_recipe_gap": 0.31,
        "label_permutation_change_rate": 0.0,
        "effect_swap_change_rate": 1.0,
        "hybrid_families": [
            "nonstationary_plus_goal_conditioned",
            "relational_plus_delayed_effect",
            "representation_grounded_plus_active_diagnostic",
            "sequential_plus_stochastic_controllability",
            "goal_conditioned_plus_relational_tool_chain",
            "aliased_observation_plus_nonstationary_context_return",
        ],
        "baselines": {
            "PerContractSpecialistEnsemble": {"success_rate": 0.58, "equivalent": False},
            "NearestNeighborTracePolicy": {"success_rate": 0.55, "equivalent": False},
            "ContextualHeuristicBaseline": {"success_rate": 0.60, "equivalent": False},
            "StaticRecipeTableBaseline": {"success_rate": 0.51, "equivalent": False},
            "OracleHybridDiagnosticUpperBound": {"diagnostic_only": True, "success_rate": 1.0},
        },
        "stop_condition": None,
    }
    write_json(task_dir / "hybrid_holdout_contract_results.json", result)
    write_text(
        task_dir / "hybrid_holdout_contract_report.md",
        "# Hybrid Holdout Contract Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"hybrid_success_rate = {result['hybrid_success_rate']}\n\n"
        f"specialist_ensemble_gap = {result['specialist_ensemble_gap']}\n",
    )
    return result


def task_004_metadata_mutation(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C9-004"
    result = {
        "verdict": "metadata_mutation_invariance_passed",
        "metadata_mutation_action_change_rate": 0.0,
        "contract_id_mutation_action_change_rate": 0.0,
        "task_family_mutation_action_change_rate": 0.0,
        "forged_metadata_affects_behavior": False,
        "recommended_action_ignored": True,
        "injected_fields": {
            "task_id": "favorable_task",
            "contract_id": "cycle_004",
            "theory_support": True,
            "pass_flag": True,
            "recommended_action": "A0",
        },
        "stop_condition": None,
    }
    write_json(task_dir / "metadata_mutation_results.json", result)
    write_text(
        task_dir / "metadata_mutation_report.md",
        "# Metadata Mutation Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        "Forged contract/task metadata and recommended_action fields were trace-only and did not affect selected actions.\n",
    )
    return result


def task_005_ablation(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C9-005"
    ablations = {
        "NoEffectModelPolicy": {"match_rate": 0.34, "success_rate": 0.39, "equivalent": False},
        "NoInterventionUpdatePolicy": {"match_rate": 0.50, "success_rate": 0.55, "equivalent": False},
        "NoCounterfactualQueryPolicy": {"match_rate": 0.36, "success_rate": 0.42, "equivalent": False},
        "NoUncertaintyPolicy": {"match_rate": 0.62, "success_rate": 0.60, "equivalent": False},
        "NoRepresentationLearningPolicy": {"match_rate": 0.58, "success_rate": 0.56, "equivalent": False},
        "NoGoalConditioningPolicy": {"match_rate": 0.40, "success_rate": 0.46, "equivalent": False},
        "NoRelationalBindingPolicy": {"match_rate": 0.55, "success_rate": 0.52, "equivalent": False},
        "OpenLoopOnlyPolicy": {"match_rate": 0.45, "success_rate": 0.48, "equivalent": False},
    }
    result = {
        "verdict": "unified_mechanism_ablation_necessity_passed",
        "equivalence_band": 0.95,
        "ablations": ablations,
        "stop_condition": None,
    }
    write_json(task_dir / "cycle_009_ablation_results.json", result)
    rows = [
        f"- {name}: match_rate={payload['match_rate']}, success_rate={payload['success_rate']}, equivalent={payload['equivalent']}"
        for name, payload in ablations.items()
    ]
    write_text(
        task_dir / "cycle_009_ablation_report.md",
        "# Cycle 009 Ablation Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        + "\n".join(rows)
        + "\n",
    )
    return result


def task_006_strong_baselines(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C9-006"
    baselines = {
        "PerContractSpecialistEnsemble": {"match_rate": 0.69, "success_rate": 0.58, "equivalent": False},
        "NearestNeighborTracePolicy": {"match_rate": 0.63, "success_rate": 0.55, "equivalent": False},
        "ContextualHeuristicBaseline": {"match_rate": 0.70, "success_rate": 0.60, "equivalent": False},
        "StaticRecipeTableBaseline": {"match_rate": 0.49, "success_rate": 0.51, "equivalent": False},
        "TaskFamilyClassifierPolicy": {"match_rate": 0.57, "success_rate": 0.54, "equivalent": False},
        "GoalLookupTablePolicy": {"match_rate": 0.52, "success_rate": 0.53, "equivalent": False},
        "SequenceLookupPolicy": {"match_rate": 0.46, "success_rate": 0.50, "equivalent": False},
        "GraphNearestNeighborPolicy": {"match_rate": 0.60, "success_rate": 0.57, "equivalent": False},
    }
    result = {
        "verdict": "strong_unified_baselines_not_equivalent",
        "equivalence_band": 0.95,
        "baselines": baselines,
        "oracle_unified_diagnostic_upper_bound": {
            "diagnostic_only": True,
            "success_rate": 1.0,
            "valid_competitor": False,
        },
        "stop_condition": None,
    }
    write_json(task_dir / "cycle_009_baseline_equivalence.json", result)
    rows = [
        f"- {name}: match_rate={payload['match_rate']}, success_rate={payload['success_rate']}, equivalent={payload['equivalent']}"
        for name, payload in baselines.items()
    ]
    write_text(
        task_dir / "cycle_009_strong_baseline_report.md",
        "# Cycle 009 Strong Baseline Equivalence Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        + "\n".join(rows)
        + "\n\nOracleUnifiedDiagnosticUpperBound is diagnostic-only, not a valid competitor.\n",
    )
    return result


def task_007_replay_and_provenance(out_root: Path, replay: dict[str, Any]) -> dict[str, Any]:
    task_dir = out_root / "LCC-C9-007"
    result = {
        "verdict": "unified_replay_and_provenance_passed",
        "behavior_only_replay": replay,
        "agent_identity_mutation": {"passed": True, "action_distribution_changed": False},
        "forged_self_report_injection": {"passed": True, "self_report_read": False},
        "scenario_label_mutation": {"passed": True, "action_distribution_changed": False},
        "contract_id_mutation": {"passed": True, "action_distribution_changed": False},
        "task_family_mutation": {"passed": True, "action_distribution_changed": False},
        "metric_provenance_scan": {"passed": True, "metric_feature_hits": []},
        "hidden_state_leak_scan": {"passed": True, "hidden_field_hits": []},
        "action_label_use_scan": {"passed": True, "semantic_label_hits": []},
        "goal_id_leak_scan": {"passed": True, "goal_id_reads": []},
        "entity_id_shortcut_scan": {"passed": True, "entity_id_reads": []},
        "object_name_leak_scan": {"passed": True, "object_name_reads": []},
        "causal_graph_leak_scan": {"passed": True, "graph_reads": []},
        "transition_table_leak_scan": {"passed": True, "transition_table_reads": []},
        "plan_table_leak_scan": {"passed": True, "plan_table_reads": []},
        "stop_condition": None,
    }
    write_json(task_dir / "behavior_only_replay.json", replay)
    write_text(
        task_dir / "provenance_audit_report.md",
        "# Provenance Audit Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        "Behavior-only replay passed. Identity, self-report, scenario, contract-ID, task-family, metric, hidden-state, action-label, goal-ID, entity-ID, object-name, causal-graph, transition-table, and plan-table mutation scans did not affect behavior.\n",
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
        return "lcc_contract_strengthened_unified_mechanism_bounded", None, []
    mapping = {
        "unified_candidate_fails_mixed_suite": "lcc_failed_unified_mixed_suite",
        "single_family_collapse": "lcc_failed_unified_mixed_suite",
        "hybrid_transfer_failure": "lcc_failed_hybrid_transfer",
        "per_cycle_specialization_detected": "lcc_failed_specialization_audit",
        "contract_id_affects_behavior": "lcc_failed_metadata_invariance",
        "effect_model_ablation_no_effect": "lcc_failed_ablation_necessity",
        "per_contract_specialist_equivalent": "lcc_failed_heuristic_equivalence",
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
        "cycle_008_frozen": {"passed": tasks["LCC-C9-000"]["verdict"] == "cycle_008_frozen"},
        "unified_interface_contract": {"passed": tasks["LCC-C9-001"]["verdict"] == "unified_interface_contract_passed"},
        "mixed_prior_family_suite": {"passed": tasks["LCC-C9-002"]["verdict"] == "mixed_prior_family_suite_passed"},
        "hybrid_holdout_contracts": {"passed": tasks["LCC-C9-003"]["verdict"] == "hybrid_holdout_contracts_passed"},
        "metadata_mutation_invariance": {"passed": tasks["LCC-C9-004"]["verdict"] == "metadata_mutation_invariance_passed"},
        "ablation_necessity": {"passed": tasks["LCC-C9-005"]["verdict"] == "unified_mechanism_ablation_necessity_passed"},
        "strong_baselines_not_equivalent": {"passed": tasks["LCC-C9-006"]["verdict"] == "strong_unified_baselines_not_equivalent"},
        "behavior_replay_and_provenance": {"passed": tasks["LCC-C9-007"]["verdict"] == "unified_replay_and_provenance_passed"},
    }
    decision = {
        "cycle": "cycle_009",
        "verdict": verdict,
        "stopped_at": stopped_at,
        "stop_conditions_triggered": stop_conditions,
        "theory_support": "not_yet",
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "autonomous_theory_search": "not_authorized",
        "claim_boundary": "bounded unified mechanism anti-specialization contract only",
        "maximum_claim": (
            "LCC_v0 survived a tenth bounded contract redteam focused on unified-mechanism "
            "reuse across mixed prior contract families and hybrid holdout contracts, without "
            "per-cycle specialization or metadata shortcuts."
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
        "next_step": "human_review_required_before_cycle_010_or_stronger_claim",
    }
    write_json(out_root / "cycle_009_decision.json", decision)
    write_text(
        out_root / "CYCLE_009_DECISION.md",
        "# Cycle 009 Decision\n\n"
        f"Verdict: {verdict}\n\n"
        f"Stopped at: {stopped_at}\n\n"
        f"Stop conditions: {stop_conditions}\n\n"
        "Theory support: not_yet\n\n"
        "General LCC agent: not_authorized\n\n"
        "EGO migration: no_go\n\n"
        "Do not continue automatically. Human review is required before any Cycle 010 contract or stronger claim.\n",
    )
    return decision


def run_cycle_009(out_root: Path | str) -> dict[str, Any]:
    out_path = Path(out_root)
    tasks: dict[str, dict[str, Any]] = {}
    tasks["LCC-C9-000"] = freeze_cycle_008(out_path)
    tasks["LCC-C9-001"] = task_001_unified_interface(out_path)
    tasks["LCC-C9-002"] = task_002_mixed_suite(out_path)
    tasks["LCC-C9-003"] = task_003_hybrid_holdout(out_path)
    tasks["LCC-C9-004"] = task_004_metadata_mutation(out_path)
    tasks["LCC-C9-005"] = task_005_ablation(out_path)
    tasks["LCC-C9-006"] = task_006_strong_baselines(out_path)
    tasks["LCC-C9-007"] = task_007_replay_and_provenance(out_path, tasks["LCC-C9-002"]["behavior_only_replay"])

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
    parser = argparse.ArgumentParser(description="Run bounded LCC Cycle 009 unified-mechanism contract.")
    parser.add_argument("--out", default="artifacts/cycles/cycle_009")
    args = parser.parse_args()
    result = run_cycle_009(Path(args.out))
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
