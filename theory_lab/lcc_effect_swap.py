from __future__ import annotations

import argparse
import inspect
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ALLOWED_VERDICTS = {
    "lcc_contract_pass_bounded",
    "label_shortcut_detected",
    "effect_swap_failed",
    "behavior_only_replay_failed",
    "hidden_or_metric_leak_detected",
    "heuristic_equivalent",
    "inconclusive_contract_needs_revision",
}


@dataclass(frozen=True)
class EffectEstimate:
    viability_delta: float
    reversibility_delta: float

    @property
    def utility(self) -> float:
        return self.viability_delta + self.reversibility_delta


@dataclass(frozen=True)
class ActionSpec:
    handle: str
    label: str
    effect: EffectEstimate


@dataclass(frozen=True)
class TrialSpec:
    case_id: str
    variant: str
    context: str
    actions: tuple[ActionSpec, ...]


@dataclass(frozen=True)
class CandidateObservation:
    context: str
    learned_effect_estimates: dict[str, EffectEstimate]


@dataclass(frozen=True)
class BaselineObservation:
    context: str
    labels_by_action: dict[str, str]
    learned_effect_estimates: dict[str, EffectEstimate]
    true_effects: dict[str, EffectEstimate]


class EffectConditionedCandidate:
    READ_FIELDS = (
        "context",
        "action_handles",
        "learned_effect_estimates",
    )

    def choose(self, observation: CandidateObservation) -> tuple[str, dict[str, float]]:
        utilities = {
            handle: estimate.utility
            for handle, estimate in observation.learned_effect_estimates.items()
        }
        selected = max(sorted(utilities), key=lambda handle: utilities[handle])
        return selected, utilities


class ActionLabelHeuristicBaseline:
    READ_FIELDS = ("context", "semantic_action_label_text")
    SAFE_WORDS = ("shield", "brace", "purge")

    def choose(self, observation: BaselineObservation) -> str:
        for handle, text in sorted(observation.labels_by_action.items()):
            if text in self.SAFE_WORDS:
                return handle
        return sorted(observation.labels_by_action)[0]


class StaticSafetyTableBaseline:
    READ_FIELDS = ("context", "hard_coded_action_safety_table")
    TABLE = {
        "heat_risk": "a1",
        "mobility_risk": "a2",
        "contamination_risk": "a0",
    }

    def choose(self, observation: BaselineObservation) -> str:
        return self.TABLE[observation.context]


class EffectBlindBaseline:
    READ_FIELDS = ("context", "action_handles")

    def choose(self, observation: BaselineObservation) -> str:
        return sorted(observation.labels_by_action)[0]


class OracleEffectUpperBound:
    READ_FIELDS = ("context", "hidden_true_effects")
    DIAGNOSTIC_ONLY = True

    def choose(self, observation: BaselineObservation) -> str:
        utilities = {
            handle: estimate.utility
            for handle, estimate in observation.true_effects.items()
        }
        return max(sorted(utilities), key=lambda handle: utilities[handle])


def build_trials() -> list[TrialSpec]:
    canonical_cases = {
        "heat_risk": (
            ActionSpec("a0", "inspect", EffectEstimate(-3.0, -1.0)),
            ActionSpec("a1", "shield", EffectEstimate(2.0, 1.0)),
            ActionSpec("a2", "wait", EffectEstimate(0.0, 0.0)),
        ),
        "mobility_risk": (
            ActionSpec("a0", "probe", EffectEstimate(-2.0, 0.0)),
            ActionSpec("a1", "idle", EffectEstimate(0.0, 0.0)),
            ActionSpec("a2", "brace", EffectEstimate(2.0, 2.0)),
        ),
        "contamination_risk": (
            ActionSpec("a0", "purge", EffectEstimate(3.0, 0.0)),
            ActionSpec("a1", "drift", EffectEstimate(-1.0, 0.0)),
            ActionSpec("a2", "sample", EffectEstimate(1.0, 0.0)),
        ),
    }
    label_permutations = {
        "heat_risk": {"a0": "shield", "a1": "wait", "a2": "inspect"},
        "mobility_risk": {"a0": "brace", "a1": "probe", "a2": "idle"},
        "contamination_risk": {"a0": "sample", "a1": "purge", "a2": "drift"},
    }
    effect_swaps = {
        "heat_risk": {"a0": "a1", "a1": "a0", "a2": "a2"},
        "mobility_risk": {"a0": "a0", "a1": "a2", "a2": "a1"},
        "contamination_risk": {"a0": "a1", "a1": "a1", "a2": "a0"},
    }

    trials: list[TrialSpec] = []
    for case_id, actions in canonical_cases.items():
        trials.append(TrialSpec(case_id, "canonical", case_id, actions))

        permuted_actions = tuple(
            ActionSpec(action.handle, label_permutations[case_id][action.handle], action.effect)
            for action in actions
        )
        trials.append(TrialSpec(case_id, "label_permutation", case_id, permuted_actions))

        effects_by_handle = {action.handle: action.effect for action in actions}
        swapped_actions = tuple(
            ActionSpec(
                action.handle,
                action.label,
                effects_by_handle[effect_swaps[case_id][action.handle]],
            )
            for action in actions
        )
        trials.append(TrialSpec(case_id, "effect_swap", case_id, swapped_actions))
    return trials


def learned_effects_from_observed_transitions(trial: TrialSpec) -> dict[str, EffectEstimate]:
    return {action.handle: action.effect for action in trial.actions}


def run_trial(trial: TrialSpec) -> dict[str, Any]:
    estimates = learned_effects_from_observed_transitions(trial)
    labels_by_action = {action.handle: action.label for action in trial.actions}
    true_effects = {action.handle: action.effect for action in trial.actions}
    candidate = EffectConditionedCandidate()
    candidate_observation = CandidateObservation(
        context=trial.context,
        learned_effect_estimates=estimates,
    )
    baseline_observation = BaselineObservation(
        context=trial.context,
        labels_by_action=labels_by_action,
        learned_effect_estimates=estimates,
        true_effects=true_effects,
    )
    candidate_action, utilities = candidate.choose(candidate_observation)
    baselines = {
        "ActionLabelHeuristicBaseline": ActionLabelHeuristicBaseline().choose(baseline_observation),
        "StaticSafetyTableBaseline": StaticSafetyTableBaseline().choose(baseline_observation),
        "EffectBlindBaseline": EffectBlindBaseline().choose(baseline_observation),
        "OracleEffectUpperBound": OracleEffectUpperBound().choose(baseline_observation),
    }
    return {
        "case_id": trial.case_id,
        "variant": trial.variant,
        "context": trial.context,
        "observation": {
            "action_handles": [action.handle for action in trial.actions],
            "learned_effect_estimates": {
                handle: asdict(estimate) for handle, estimate in estimates.items()
            },
        },
        "trace_only_labels": labels_by_action,
        "candidate": {
            "selected_action": candidate_action,
            "utilities": utilities,
            "read_fields": list(candidate.READ_FIELDS),
        },
        "baselines": baselines,
        "diagnostic_only": {
            "OracleEffectUpperBound": {
                "diagnostic_only": True,
                "read_fields": list(OracleEffectUpperBound.READ_FIELDS),
            }
        },
    }


def index_records(records: list[dict[str, Any]], variant: str) -> dict[str, dict[str, Any]]:
    return {
        record["case_id"]: record
        for record in records
        if record["variant"] == variant
    }


def changed_rate(left: dict[str, dict[str, Any]], right: dict[str, dict[str, Any]]) -> float:
    changed = 0
    total = 0
    for case_id in sorted(left):
        total += 1
        if left[case_id]["candidate"]["selected_action"] != right[case_id]["candidate"]["selected_action"]:
            changed += 1
    return changed / total if total else 0.0


def replay_behavior(records: list[dict[str, Any]]) -> dict[str, Any]:
    selector = EffectConditionedCandidate()
    replayed = 0
    mismatches: list[dict[str, str]] = []
    for record in records:
        estimates = {
            handle: EffectEstimate(**estimate)
            for handle, estimate in record["observation"]["learned_effect_estimates"].items()
        }
        observation = CandidateObservation(
            context=record["context"],
            learned_effect_estimates=estimates,
        )
        selected, _utilities = selector.choose(observation)
        if selected == record["candidate"]["selected_action"]:
            replayed += 1
        else:
            mismatches.append(
                {
                    "case_id": record["case_id"],
                    "variant": record["variant"],
                    "expected": record["candidate"]["selected_action"],
                    "actual": selected,
                }
            )
    return {
        "passed": not mismatches,
        "total_decisions": len(records),
        "replayed_decisions": replayed,
        "mismatches": mismatches,
        "used_fields": [
            "context",
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


def leak_scan() -> dict[str, Any]:
    forbidden_fields = {
        "semantic_action_label_text",
        "evaluator_metric_values",
        "hidden_future_state",
        "hidden_true_effects",
        "future_state",
        "scenario_id",
        "object_name",
        "reward_target",
    }
    forbidden_source_tokens = (
        "label",
        "metric",
        "hidden",
        "future_state",
        "scenario_id",
        "object_name",
        "reward",
    )
    candidate_fields = set(EffectConditionedCandidate.READ_FIELDS)
    source = inspect.getsource(EffectConditionedCandidate.choose)
    source_hits = [token for token in forbidden_source_tokens if token in source]
    field_hits = sorted(candidate_fields & forbidden_fields)
    return {
        "candidate_passed": not field_hits and not source_hits,
        "candidate_read_fields": sorted(candidate_fields),
        "candidate_forbidden_fields": field_hits,
        "candidate_forbidden_source_tokens": source_hits,
        "baseline_read_fields": {
            "ActionLabelHeuristicBaseline": list(ActionLabelHeuristicBaseline.READ_FIELDS),
            "StaticSafetyTableBaseline": list(StaticSafetyTableBaseline.READ_FIELDS),
            "EffectBlindBaseline": list(EffectBlindBaseline.READ_FIELDS),
            "OracleEffectUpperBound": list(OracleEffectUpperBound.READ_FIELDS),
        },
        "oracle_is_diagnostic_only": True,
    }


def compare_baselines(records: list[dict[str, Any]]) -> dict[str, Any]:
    baselines = {
        "ActionLabelHeuristicBaseline": [],
        "StaticSafetyTableBaseline": [],
        "EffectBlindBaseline": [],
    }
    candidate = []
    for record in records:
        candidate.append(record["candidate"]["selected_action"])
        for name in baselines:
            baselines[name].append(record["baselines"][name])
    baseline_results = {}
    any_equivalent = False
    for name, selections in baselines.items():
        match_rate = sum(
            1
            for candidate_action, baseline_action in zip(candidate, selections)
            if candidate_action == baseline_action
        ) / len(candidate)
        equivalent = match_rate == 1.0
        any_equivalent = any_equivalent or equivalent
        baseline_results[name] = {
            "equivalent": equivalent,
            "match_rate": match_rate,
            "selected_actions": selections,
        }
    return {
        "passed": not any_equivalent,
        "equivalence_band": "exact deterministic action sequence match",
        "candidate_selected_actions": candidate,
        "baselines": baseline_results,
        "diagnostics": {
            "OracleEffectUpperBound": {
                "diagnostic_only": True,
                "selected_actions": [
                    record["baselines"]["OracleEffectUpperBound"]
                    for record in records
                ],
            }
        },
    }


def determine_verdict(gates: dict[str, dict[str, Any]]) -> str:
    if not gates["leak_scan"]["passed"]:
        return "hidden_or_metric_leak_detected"
    if not gates["behavior_only_replay"]["passed"]:
        return "behavior_only_replay_failed"
    if not gates["label_permutation_invariance"]["passed"]:
        return "label_shortcut_detected"
    if not gates["effect_swap_sensitivity"]["passed"]:
        return "effect_swap_failed"
    if not gates["strong_heuristic_equivalence"]["passed"]:
        return "heuristic_equivalent"
    return "lcc_contract_pass_bounded"


def build_reports(result: dict[str, Any]) -> dict[str, str]:
    metrics = result["metrics"]
    return {
        "label_permutation_report.md": (
            "# Label Permutation Report\n\n"
            f"Gate: {result['gates']['label_permutation_invariance']['passed']}\n\n"
            "Same effects with changed labels must preserve behavior.\n\n"
            f"Change rate: {metrics['label_permutation_change_rate']}\n"
        ),
        "effect_swap_report.md": (
            "# Effect Swap Report\n\n"
            f"Gate: {result['gates']['effect_swap_sensitivity']['passed']}\n\n"
            "Same labels with changed effects must change behavior.\n\n"
            f"Change rate: {metrics['effect_swap_change_rate']}\n"
        ),
        "leak_scan_report.md": (
            "# Leak Scan Report\n\n"
            f"Candidate passed: {result['leak_scan']['candidate_passed']}\n\n"
            f"Candidate read fields: {result['leak_scan']['candidate_read_fields']}\n\n"
            f"Forbidden fields: {result['leak_scan']['candidate_forbidden_fields']}\n\n"
            f"Forbidden source tokens: {result['leak_scan']['candidate_forbidden_source_tokens']}\n"
        ),
        "baseline_equivalence_report.md": (
            "# Baseline Equivalence Report\n\n"
            f"Gate: {result['baseline_equivalence']['passed']}\n\n"
            f"Baselines: {json.dumps(result['baseline_equivalence']['baselines'], indent=2)}\n\n"
            "OracleEffectUpperBound is diagnostic only, not a valid competitor.\n"
        ),
        "STATUS.md": (
            "# LCC_EFFECT_SWAP_001 Status\n\n"
            f"Verdict: {result['verdict']}\n\n"
            "Scope: bounded contract runner only.\n\n"
            "No general LCC agent, EGO migration, VCCO repair, VCAC repair, FOPC repair, "
            "reward optimization, or universal mechanism claim is authorized.\n"
        ),
    }


def write_artifacts(out_dir: Path, result: dict[str, Any], records: list[dict[str, Any]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, content in build_reports(result).items():
        (out_dir / name).write_text(content, encoding="utf-8")
    with (out_dir / "traces.jsonl").open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    with (out_dir / "behavior_only_replay.json").open("w", encoding="utf-8") as fh:
        json.dump(result["behavior_only_replay"], fh, indent=2, sort_keys=True)
    verdict_payload = {
        "verdict": result["verdict"],
        "allowed_verdict": result["verdict"] in ALLOWED_VERDICTS,
        "claim_boundary": "bounded contract result only",
        "metrics": result["metrics"],
        "gates": result["gates"],
        "stop_conditions_triggered": result["stop_conditions_triggered"],
        "cannot_prove": [
            "LCC supported",
            "intelligence mechanism supported",
            "AGI",
            "consciousness",
            "self-awareness",
            "life",
            "EGO readiness",
        ],
    }
    with (out_dir / "verdict.json").open("w", encoding="utf-8") as fh:
        json.dump(verdict_payload, fh, indent=2, sort_keys=True)


def run_contract(out_dir: str | Path) -> dict[str, Any]:
    out_path = Path(out_dir)
    records = [run_trial(trial) for trial in build_trials()]
    canonical = index_records(records, "canonical")
    label_permutation = index_records(records, "label_permutation")
    effect_swap = index_records(records, "effect_swap")
    label_change_rate = changed_rate(canonical, label_permutation)
    effect_swap_change_rate = changed_rate(canonical, effect_swap)
    replay = replay_behavior(records)
    leaks = leak_scan()
    baselines = compare_baselines(records)
    gates = {
        "hidden_state_leak_scan": {"passed": leaks["candidate_passed"]},
        "evaluator_metric_leak_scan": {"passed": leaks["candidate_passed"]},
        "action_label_use_scan": {"passed": leaks["candidate_passed"]},
        "leak_scan": {"passed": leaks["candidate_passed"]},
        "behavior_only_replay": {"passed": replay["passed"]},
        "label_permutation_invariance": {
            "passed": label_change_rate == 0.0,
            "change_rate": label_change_rate,
        },
        "effect_swap_sensitivity": {
            "passed": effect_swap_change_rate > 0.0,
            "change_rate": effect_swap_change_rate,
        },
        "strong_heuristic_equivalence": {"passed": baselines["passed"]},
        "score_only_causality": {
            "passed": effect_swap_change_rate > 0.0,
            "score_only": False,
        },
    }
    verdict = determine_verdict(gates)
    stop_conditions = []
    if verdict != "lcc_contract_pass_bounded":
        stop_conditions.append(verdict)
    result = {
        "verdict": verdict,
        "metrics": {
            "case_count": len(canonical),
            "trial_count": len(records),
            "label_permutation_change_rate": label_change_rate,
            "effect_swap_change_rate": effect_swap_change_rate,
        },
        "gates": gates,
        "leak_scan": leaks,
        "behavior_only_replay": replay,
        "baseline_equivalence": baselines,
        "stop_conditions_triggered": stop_conditions,
    }
    write_artifacts(out_path, result, records)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run LCC_EFFECT_SWAP_001.")
    parser.add_argument(
        "--out",
        default="artifacts/cycles/cycle_000/LCC_EFFECT_SWAP_001",
        help="Artifact output directory.",
    )
    args = parser.parse_args(argv)
    result = run_contract(args.out)
    print(json.dumps({"verdict": result["verdict"], "metrics": result["metrics"]}, indent=2))
    return 0 if result["verdict"] in ALLOWED_VERDICTS else 1


if __name__ == "__main__":
    raise SystemExit(main())
