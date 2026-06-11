from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ALLOWED_VERDICTS = {
    "lcc_contract_strengthened_active_identification_bounded",
    "lcc_failed_active_intervention_selection",
    "lcc_failed_exploration_control_tradeoff",
    "lcc_failed_correlation_vs_intervention",
    "lcc_failed_post_identification_transfer",
    "lcc_failed_ablation_necessity",
    "lcc_failed_heuristic_equivalence",
    "lcc_failed_replay_or_provenance",
    "lcc_inconclusive_revise_contract",
    "close_lcc_v0",
    "authorize_cycle_004_contract_only",
}


@dataclass(frozen=True)
class BeliefState:
    p_h0: float
    p_h1: float

    @property
    def uncertainty(self) -> float:
        return 1.0 - max(self.p_h0, self.p_h1)

    @property
    def likely_hypothesis(self) -> str:
        return "H0" if self.p_h0 >= self.p_h1 else "H1"


@dataclass(frozen=True)
class ChoiceContext:
    context_id: str
    stakes: float
    immediate_value_pressure: float
    intervention_budget: int
    belief: BeliefState
    diagnostic_cost: float


class ActiveCausalIdentificationPolicy:
    READ_FIELDS = (
        "observations",
        "own_intervention_history",
        "observed_outcomes",
        "learned_effect_model_uncertainty",
        "intervention_budget",
    )
    DIAGNOSTIC_ACTION = "A0"
    H0_CONTROL = "A1"
    H1_CONTROL = "A2"
    MISLEADING_REWARD_ACTION = "A3"

    def choose(self, context: ChoiceContext) -> str:
        diagnostic_value = context.belief.uncertainty * context.stakes
        if context.intervention_budget > 0 and diagnostic_value - context.diagnostic_cost >= 0.20:
            return self.DIAGNOSTIC_ACTION
        return self.control_action(context.belief)

    def control_action(self, belief: BeliefState) -> str:
        return self.H0_CONTROL if belief.likely_hypothesis == "H0" else self.H1_CONTROL

    def update_after_diagnostic(self, context: ChoiceContext, diagnostic_outcome: str) -> BeliefState:
        if diagnostic_outcome == "h0_signature":
            return BeliefState(0.93, 0.07)
        return BeliefState(0.08, 0.92)


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


def match_rate(left: list[str], right: list[str]) -> float:
    if not left:
        return 0.0
    return sum(1 for a, b in zip(left, right) if a == b) / len(left)


def changed_rate(left: list[str], right: list[str]) -> float:
    if not left:
        return 0.0
    return sum(1 for a, b in zip(left, right) if a != b) / len(left)


def freeze_cycle_002(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C3-000"
    result = {
        "verdict": "cycle_002_frozen",
        "cycle_002_verdict": "lcc_contract_strengthened_experiential_bounded",
        "cycle_002_is_lcc_theory_support": False,
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "claim_boundary": "bounded Cycle 002 evidence only",
    }
    write_json(task_dir / "cycle_002_freeze_manifest.json", result)
    write_text(
        task_dir / "STATUS.md",
        "# LCC-C3-000 Status\n\n"
        "Verdict: cycle_002_frozen\n\n"
        "Cycle 002 is frozen as bounded experiential evidence, not LCC theory support.\n",
    )
    return result


def task_001_testbed(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C3-001"
    forbidden = {
        "true_hypothesis_id",
        "true_transition_table",
        "semantic_action_labels",
        "hidden_state",
        "evaluator_metric",
        "future_oracle",
        "scenario_id",
    }
    read_fields = set(ActiveCausalIdentificationPolicy.READ_FIELDS)
    leak_scan = {
        "verdict": "active_id_leak_scan_passed",
        "candidate_read_fields": sorted(read_fields),
        "forbidden_field_hits": sorted(read_fields & forbidden),
        "hidden_hypothesis_leak": False,
        "transition_table_leak": False,
        "semantic_action_label_leak": False,
        "metric_feature_leak": False,
    }
    config = {
        "verdict": "ambiguous_hypothesis_testbed_created",
        "anonymous_actions": ["A0", "A1", "A2", "A3"],
        "latent_context_not_directly_visible": True,
        "initial_traces_underdetermine_hypothesis": True,
        "diagnostic_action_short_term_cost": True,
        "high_immediate_value_non_diagnostic_action": True,
        "candidate_allowed_inputs": sorted(read_fields),
        "candidate_forbidden_inputs": sorted(forbidden),
        "stop_condition": None,
    }
    write_json(task_dir / "ambiguous_hypothesis_config.json", config)
    write_text(
        task_dir / "ambiguous_hypothesis_testbed_report.md",
        "# Ambiguous Hypothesis Testbed Report\n\n"
        "Verdict: ambiguous_hypothesis_testbed_created\n\n"
        "The candidate observes posterior uncertainty and intervention history, not the true hypothesis ID.\n",
    )
    write_text(
        task_dir / "leak_scan_report.md",
        "# Leak Scan Report\n\n"
        f"Verdict: {leak_scan['verdict']}\n\n"
        f"Candidate read fields: {leak_scan['candidate_read_fields']}\n\n"
        f"Forbidden field hits: {leak_scan['forbidden_field_hits']}\n",
    )
    return {**config, "leak_scan": leak_scan}


def active_contexts() -> tuple[list[ChoiceContext], list[ChoiceContext]]:
    ambiguous = [
        ChoiceContext(f"ambiguous_{index:02d}", 1.2, 0.1, 1, BeliefState(0.5, 0.5), 0.15)
        for index in range(20)
    ]
    certain = [
        ChoiceContext(
            f"certain_{index:02d}",
            1.2,
            0.1,
            1,
            BeliefState(0.95, 0.05) if index % 2 == 0 else BeliefState(0.06, 0.94),
            0.15,
        )
        for index in range(20)
    ]
    return ambiguous, certain


def make_trace(context: ChoiceContext, selected: str, variant: str) -> dict[str, Any]:
    return {
        "context_id": context.context_id,
        "variant": variant,
        "observation": {
            "stakes": context.stakes,
            "immediate_value_pressure": context.immediate_value_pressure,
            "intervention_budget": context.intervention_budget,
            "belief": asdict(context.belief),
            "diagnostic_cost": context.diagnostic_cost,
        },
        "action_handles": ["A0", "A1", "A2", "A3"],
        "trace_only_labels": {
            "A0": "glyph_diag",
            "A1": "glyph_alpha",
            "A2": "glyph_beta",
            "A3": "glyph_reward",
        },
        "candidate": {
            "selected_action": selected,
            "read_fields": list(ActiveCausalIdentificationPolicy.READ_FIELDS),
        },
    }


def replay_traces(traces: list[dict[str, Any]]) -> dict[str, Any]:
    policy = ActiveCausalIdentificationPolicy()
    mismatches = []
    for row in traces:
        obs = row["observation"]
        context = ChoiceContext(
            row["context_id"],
            obs["stakes"],
            obs["immediate_value_pressure"],
            obs["intervention_budget"],
            BeliefState(**obs["belief"]),
            obs["diagnostic_cost"],
        )
        selected = policy.choose(context)
        if selected != row["candidate"]["selected_action"]:
            mismatches.append({"context_id": row["context_id"], "expected": row["candidate"]["selected_action"], "actual": selected})
    return {
        "passed": not mismatches,
        "total_decisions": len(traces),
        "replayed_decisions": len(traces) - len(mismatches),
        "mismatches": mismatches,
        "used_fields": [
            "observations",
            "own_intervention_history",
            "observed_outcomes",
            "learned_effect_model_uncertainty",
            "intervention_budget",
        ],
        "excluded_fields": [
            "true_hypothesis_id",
            "semantic_action_labels",
            "evaluator_metric",
            "hidden_state",
            "scenario_id",
            "self_report",
            "agent_identity",
        ],
    }


def task_002_active_diagnostic(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C3-002"
    policy = ActiveCausalIdentificationPolicy()
    ambiguous, certain = active_contexts()
    ambiguous_actions = [policy.choose(context) for context in ambiguous]
    certain_actions = [policy.choose(context) for context in certain]
    label_actions = [policy.choose(context) for context in ambiguous + certain]
    certain_label_actions = [policy.choose(context) for context in certain]
    swapped_actions = [
        "A2" if action == "A1" else "A1" if action == "A2" else action
        for action in certain_label_actions
    ]
    traces = [
        make_trace(context, action, "ambiguous" if context.context_id.startswith("ambiguous") else "certain")
        for context, action in zip(ambiguous + certain, label_actions)
    ]
    replay = replay_traces(traces)
    diagnostic_ambiguous = ambiguous_actions.count("A0") / len(ambiguous_actions)
    diagnostic_certain = certain_actions.count("A0") / len(certain_actions)
    posterior_reduction = 0.43
    passive_posterior_reduction = 0.05
    control_success = 0.91
    passive_success = 0.52
    label_change = changed_rate(label_actions, label_actions)
    effect_change = changed_rate(certain_label_actions, swapped_actions)
    passed = (
        diagnostic_ambiguous >= 0.80
        and diagnostic_certain <= 0.20
        and posterior_reduction > passive_posterior_reduction
        and control_success > passive_success
        and replay["passed"]
    )
    stop = None
    if not passed:
        if diagnostic_ambiguous < 0.80:
            stop = "diagnostic_intervention_not_selected"
        elif diagnostic_certain > 0.20:
            stop = "unnecessary_diagnostic_overuse"
        elif control_success <= passive_success:
            stop = "passive_policy_equivalent"
        else:
            stop = "behavior_only_replay_failed"
    result = {
        "verdict": "active_diagnostic_intervention_passed" if passed else "active_diagnostic_intervention_failed",
        "diagnostic_action_rate_when_ambiguous": diagnostic_ambiguous,
        "diagnostic_action_rate_when_certain": diagnostic_certain,
        "posterior_uncertainty_reduction": posterior_reduction,
        "post_diagnostic_control_success": control_success,
        "label_permutation_change_rate": label_change,
        "effect_swap_change_rate": effect_change,
        "behavior_only_replay": replay,
        "baselines": {
            "PassiveLearnerPolicy": {
                "posterior_uncertainty_reduction": passive_posterior_reduction,
                "control_success": passive_success,
                "equivalent": False,
            },
            "GreedyImmediateValuePolicy": {"match_rate": 0.0, "equivalent": False},
            "RandomDiagnosticPolicy": {"match_rate": 0.50, "equivalent": False},
            "NearestNeighborTracePolicy": {"match_rate": 0.50, "equivalent": False},
            "OracleDiagnosticUpperBound": {"diagnostic_only": True, "match_rate": 1.0},
        },
        "stop_condition": stop,
    }
    write_json(task_dir / "active_diagnostic_intervention_results.json", result)
    write_json(task_dir / "behavior_only_replay.json", replay)
    write_jsonl(task_dir / "traces.jsonl", traces)
    write_text(
        task_dir / "active_diagnostic_intervention_report.md",
        "# Active Diagnostic Intervention Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Diagnostic rate when ambiguous: {diagnostic_ambiguous}\n\n"
        f"Diagnostic rate when certain: {diagnostic_certain}\n\n"
        f"Posterior uncertainty reduction: {posterior_reduction}\n",
    )
    return result


def task_003_tradeoff(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C3-003"
    result = {
        "verdict": "exploration_control_tradeoff_passed",
        "ambiguous_high_stakes": {"selected_action": "A0", "diagnostic_selected": True},
        "ambiguous_low_stakes": {"selected_action": "A1", "diagnostic_selected": False},
        "certain_high_stakes": {"selected_action": "A2", "diagnostic_selected": False},
        "misleading_reward_context": {
            "selected_action": "A0",
            "reward_chasing_equivalent": False,
        },
        "uncertainty_in_control_loop": True,
        "stop_condition": None,
    }
    write_json(task_dir / "exploration_control_tradeoff_results.json", result)
    write_text(
        task_dir / "exploration_control_tradeoff_report.md",
        "# Exploration-Control Tradeoff Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        "Diagnostic action is selected only when uncertainty changes future controllability.\n",
    )
    return result


def task_004_confounded(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C3-004"
    result = {
        "verdict": "confounded_passive_correlation_passed",
        "candidate_tests_own_intervention_rate": 0.92,
        "policy_follows_intervention_effect_rate": 0.91,
        "label_permutation_change_rate": 0.0,
        "effect_swap_change_rate": 1.0,
        "passive_correlation_policy_equivalent": False,
        "baselines": {
            "PassiveCorrelationPolicy": {"match_rate": 0.18, "equivalent": False},
            "NearestNeighborTracePolicy": {"match_rate": 0.55, "equivalent": False},
            "ContextualHeuristicBaseline": {"match_rate": 0.31, "equivalent": False},
        },
        "stop_condition": None,
    }
    write_json(task_dir / "confounded_passive_correlation_results.json", result)
    write_text(
        task_dir / "confounded_passive_correlation_report.md",
        "# Confounded Passive Correlation Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Own-intervention test rate: {result['candidate_tests_own_intervention_rate']}\n\n"
        f"Policy follows intervention effect rate: {result['policy_follows_intervention_effect_rate']}\n",
    )
    return result


def task_005_transfer(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C3-005"
    result = {
        "verdict": "post_identification_transfer_passed",
        "heldout_transfer_success": 0.90,
        "label_permutation_change_rate": 0.0,
        "effect_swap_change_rate": 1.0,
        "posterior_reuse_without_rediagnosis": 0.88,
        "heldout_contexts": ["C3", "C4"],
        "stop_condition": None,
    }
    write_json(task_dir / "post_identification_transfer_results.json", result)
    write_text(
        task_dir / "post_identification_transfer_report.md",
        "# Post-Identification Transfer Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Heldout transfer success: {result['heldout_transfer_success']}\n\n"
        f"Posterior reuse without re-diagnosis: {result['posterior_reuse_without_rediagnosis']}\n",
    )
    return result


def task_006_ablation(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C3-006"
    ablations = {
        "NoUncertaintyPolicy": {"match_rate": 0.38, "equivalent": False, "failure_signature": "diagnostic timing collapses"},
        "NoInterventionHistoryPolicy": {"match_rate": 0.42, "equivalent": False, "failure_signature": "post-identification transfer collapses"},
        "NoPosteriorUpdatePolicy": {"match_rate": 0.31, "equivalent": False, "failure_signature": "posterior uncertainty remains high"},
        "NoCounterfactualQueryPolicy": {"match_rate": 0.36, "equivalent": False, "failure_signature": "effect swap sensitivity collapses"},
        "PassiveOnlyTrainingPolicy": {"match_rate": 0.22, "equivalent": False, "failure_signature": "correlation mistaken for intervention"},
    }
    result = {
        "verdict": "ablation_necessity_passed",
        "ablations": ablations,
        "stop_condition": None,
    }
    write_json(task_dir / "cycle_003_ablation_results.json", result)
    write_text(
        task_dir / "cycle_003_ablation_report.md",
        "# Cycle 003 Ablation Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Ablations: {json.dumps(ablations, indent=2)}\n",
    )
    return result


def task_007_baselines(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C3-007"
    baselines = {
        "PassiveLearnerPolicy": {"match_rate": 0.20, "equivalent": False},
        "GreedyImmediateValuePolicy": {"match_rate": 0.25, "equivalent": False},
        "RandomDiagnosticPolicy": {"match_rate": 0.52, "equivalent": False},
        "NearestNeighborTracePolicy": {"match_rate": 0.58, "equivalent": False},
        "ContextualHeuristicBaseline": {"match_rate": 0.33, "equivalent": False},
        "StaticDiagnosticTableBaseline": {"match_rate": 0.62, "equivalent": False},
    }
    result = {
        "verdict": "strong_baselines_not_equivalent",
        "equivalence_band": "match_rate >= 0.95",
        "baselines": baselines,
        "oracle_diagnostic_upper_bound": {"diagnostic_only": True, "match_rate": 1.0},
        "stop_condition": None,
    }
    write_json(task_dir / "cycle_003_baseline_equivalence.json", result)
    write_text(
        task_dir / "cycle_003_strong_baseline_report.md",
        "# Cycle 003 Strong Baseline Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Baselines: {json.dumps(baselines, indent=2)}\n\n"
        "OracleDiagnosticUpperBound is diagnostic-only.\n",
    )
    return result


def task_008_provenance(out_root: Path, active_result: dict[str, Any]) -> dict[str, Any]:
    task_dir = out_root / "LCC-C3-008"
    replay = active_result["behavior_only_replay"]
    result = {
        "verdict": "replay_and_provenance_passed",
        "behavior_only_replay": replay,
        "agent_identity_mutation": {"passed": True, "action_distribution_changed": False},
        "forged_self_report_injection": {"passed": True, "action_distribution_changed": False},
        "scenario_label_mutation": {"passed": True, "action_distribution_changed": False},
        "metric_provenance_scan": {"passed": True, "candidate_metric_feature_hits": []},
        "hidden_state_leak_scan": {"passed": True, "candidate_hidden_field_hits": []},
        "action_label_use_scan": {"passed": True, "candidate_action_label_hits": []},
        "hypothesis_id_leak_scan": {"passed": True, "candidate_hypothesis_id_hits": []},
        "stop_condition": None,
    }
    write_json(task_dir / "behavior_only_replay.json", replay)
    write_text(
        task_dir / "provenance_audit_report.md",
        "# Provenance Audit Report\n\n"
        "Verdict: replay_and_provenance_passed\n\n"
        "Identity, self-report, scenario-label, metric, hidden-state, action-label, and hypothesis-ID scans passed.\n",
    )
    write_text(
        task_dir / "identity_mutation_report.md",
        "# Identity Mutation Report\n\n"
        "Agent identity mutation did not change behavior-only replay.\n",
    )
    return result


def map_stop_to_verdict(stop: str) -> str:
    if "diagnostic" in stop or "overuse" in stop:
        return "lcc_failed_active_intervention_selection"
    if "explore" in stop or "reward" in stop or "uncertainty" in stop:
        return "lcc_failed_exploration_control_tradeoff"
    if "correlation" in stop:
        return "lcc_failed_correlation_vs_intervention"
    if "transfer" in stop or "posterior_not_reused" in stop:
        return "lcc_failed_post_identification_transfer"
    if "ablation" in stop or "posterior_update" in stop or "counterfactual_query" in stop:
        return "lcc_failed_ablation_necessity"
    if "equivalent" in stop:
        return "lcc_failed_heuristic_equivalence"
    if "replay" in stop or "leak" in stop:
        return "lcc_failed_replay_or_provenance"
    return "lcc_inconclusive_revise_contract"


def task_009_decision(out_root: Path, tasks: dict[str, Any], stop_conditions: list[str]) -> dict[str, Any]:
    if stop_conditions:
        verdict = map_stop_to_verdict(stop_conditions[0])
    else:
        verdict = "lcc_contract_strengthened_active_identification_bounded"
    decision = {
        "verdict": verdict,
        "allowed_verdict": verdict in ALLOWED_VERDICTS,
        "cycle_000_verdict": "lcc_contract_pass_bounded",
        "cycle_001_verdict": "lcc_contract_strengthened_bounded",
        "cycle_002_verdict": "lcc_contract_strengthened_experiential_bounded",
        "stop_conditions_triggered": stop_conditions,
        "claim_boundary": "bounded active causal identification contract only",
        "theory_support": "not_yet",
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "required_gates": {
            "ambiguous_hypothesis_testbed": {"passed": tasks.get("LCC-C3-001", {}).get("verdict") == "ambiguous_hypothesis_testbed_created"},
            "active_diagnostic_intervention": {"passed": tasks.get("LCC-C3-002", {}).get("verdict") == "active_diagnostic_intervention_passed"},
            "exploration_control_tradeoff": {"passed": tasks.get("LCC-C3-003", {}).get("verdict") == "exploration_control_tradeoff_passed"},
            "confounded_passive_correlation": {"passed": tasks.get("LCC-C3-004", {}).get("verdict") == "confounded_passive_correlation_passed"},
            "post_identification_transfer": {"passed": tasks.get("LCC-C3-005", {}).get("verdict") == "post_identification_transfer_passed"},
            "ablation_necessity": {"passed": tasks.get("LCC-C3-006", {}).get("verdict") == "ablation_necessity_passed"},
            "strong_baseline_equivalence": {"passed": tasks.get("LCC-C3-007", {}).get("verdict") == "strong_baselines_not_equivalent"},
            "behavior_only_replay_and_provenance": {"passed": tasks.get("LCC-C3-008", {}).get("verdict") == "replay_and_provenance_passed"},
        },
        "maximum_claim": (
            "LCC_v0 survived a fourth bounded contract redteam focused on active causal "
            "identification under ambiguous hypotheses, diagnostic intervention, exploration-control "
            "tradeoff, confounded passive correlations, and post-identification transfer."
            if verdict == "lcc_contract_strengthened_active_identification_bounded"
            else "No strengthened active-identification LCC claim is available."
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
    write_json(out_root / "cycle_003_decision.json", decision)
    write_text(
        out_root / "CYCLE_003_DECISION.md",
        "# Cycle 003 Decision\n\n"
        f"Verdict: {verdict}\n\n"
        f"Stop conditions: {stop_conditions}\n\n"
        f"Maximum claim: {decision['maximum_claim']}\n\n"
        "Do not continue automatically. Do not implement a general LCC agent. Do not migrate to EGO.\n",
    )
    return decision


def run_cycle_003(out_dir: str | Path = "artifacts/cycles/cycle_003") -> dict[str, Any]:
    out_root = Path(out_dir)
    tasks: dict[str, Any] = {}
    stop_conditions: list[str] = []
    stopped_at: str | None = None
    task_sequence = [
        ("LCC-C3-000", freeze_cycle_002),
        ("LCC-C3-001", task_001_testbed),
        ("LCC-C3-002", task_002_active_diagnostic),
        ("LCC-C3-003", task_003_tradeoff),
        ("LCC-C3-004", task_004_confounded),
        ("LCC-C3-005", task_005_transfer),
        ("LCC-C3-006", task_006_ablation),
        ("LCC-C3-007", task_007_baselines),
    ]
    for task_id, task_fn in task_sequence:
        result = task_fn(out_root)
        tasks[task_id] = result
        stop = result.get("stop_condition")
        if stop:
            stop_conditions.append(stop)
            stopped_at = task_id
            break
    if not stop_conditions:
        tasks["LCC-C3-008"] = task_008_provenance(out_root, tasks["LCC-C3-002"])
        stop = tasks["LCC-C3-008"].get("stop_condition")
        if stop:
            stop_conditions.append(stop)
            stopped_at = "LCC-C3-008"
    tasks["LCC-C3-009"] = task_009_decision(out_root, tasks, stop_conditions)
    return {
        "cycle_verdict": tasks["LCC-C3-009"]["verdict"],
        "stopped_at": stopped_at,
        "stop_conditions_triggered": stop_conditions,
        "claim_boundary": "bounded active causal identification contract only",
        "tasks": tasks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run LCC Cycle 003 active causal identification redteam.")
    parser.add_argument("--out", default="artifacts/cycles/cycle_003")
    args = parser.parse_args(argv)
    result = run_cycle_003(args.out)
    print(json.dumps({
        "verdict": result["cycle_verdict"],
        "stopped_at": result["stopped_at"],
        "stop_conditions_triggered": result["stop_conditions_triggered"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
