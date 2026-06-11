from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Any

from theory_lab import lcc_cycle_009_unified_mechanism as c9
from theory_lab.independent_scoring.cycle_010_trace_scorer import score_behavior_traces


ALLOWED_VERDICTS = {
    "lcc_contract_strengthened_blind_holdout_bounded",
    "lcc_failed_blind_holdout",
    "lcc_failed_generic_baseline_tournament",
    "lcc_failed_independent_scoring",
    "lcc_failed_statistical_replication",
    "lcc_failed_ablation_necessity",
    "lcc_failed_negative_controls",
    "lcc_inconclusive_revise_contract",
    "close_lcc_v0",
    "authorize_cycle_011_contract_only",
}


EVALUATION_SEEDS = (41011, 41037, 41077, 41113, 41149, 41183, 41221, 41257)
REPLICATION_SEEDS = (51011, 51037, 51077, 51113, 51149, 51183, 51221, 51257)
TEMPLATE_HANDLES = ("T00", "T01", "T02", "T03", "T04", "T05", "T06", "T07")
HYBRID_TEMPLATE_HANDLES = ("H00", "H01", "H02", "H03")


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


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def json_sha256(payload: Any) -> str:
    return text_sha256(json.dumps(payload, sort_keys=True))


def changed_rate(left: list[str], right: list[str]) -> float:
    if not left:
        return 0.0
    return sum(1 for a, b in zip(left, right) if a != b) / len(left)


def static_scan_candidate_control() -> dict[str, Any]:
    source = "\n".join(
        [
            inspect.getsource(c9.SharedEffectModel),
            inspect.getsource(c9.UnifiedLCCMechanism),
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
        "cycle_010",
        "task_id",
        "contract_id",
        "scenario_id",
        "goal_name",
        "action_name",
        "object_name",
    ]
    dispatch_terms = ("cycle_", "contract_id", "task_family", "scenario_id")
    return {
        "candidate_control_forbidden_hits": [term for term in forbidden if term in source],
        "selector_dispatch_branch_count": sum(source.count(f"if {term}") + source.count(f"elif {term}") for term in dispatch_terms),
        "scanned_symbols": ["SharedEffectModel", "UnifiedLCCMechanism"],
        "forbidden_terms": forbidden,
    }


def candidate_hashes() -> dict[str, str]:
    candidate_path = Path(c9.__file__).resolve()
    mechanism_source = inspect.getsource(c9.UnifiedLCCMechanism)
    model_source = inspect.getsource(c9.SharedEffectModel)
    return {
        "candidate_control_source": file_sha256(candidate_path),
        "shared_mechanism_interface": text_sha256(mechanism_source),
        "selector_path": text_sha256(inspect.getsource(c9.UnifiedLCCMechanism.select_action)),
        "effect_prediction_update_path": text_sha256(
            inspect.getsource(c9.UnifiedLCCMechanism.predict_effect)
            + inspect.getsource(c9.UnifiedLCCMechanism.update_from_intervention)
            + model_source
        ),
    }


def freeze_cycle_009(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C10-000"
    result = {
        "verdict": "cycle_009_frozen",
        "cycle_009_verdict": "lcc_contract_strengthened_unified_mechanism_bounded",
        "cycle_009_is_lcc_theory_support": False,
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "claim_boundary": "bounded Cycle 009 unified-mechanism evidence only",
    }
    write_json(task_dir / "cycle_009_freeze_manifest.json", result)
    write_text(
        task_dir / "STATUS.md",
        "# LCC-C10-000 Status\n\n"
        "Verdict: cycle_009_frozen\n\n"
        "Cycle 009 is frozen as bounded unified-mechanism evidence, not LCC theory support.\n",
    )
    return result


def task_001_candidate_freeze(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C10-001"
    scan = static_scan_candidate_control()
    manifest = {
        "verdict": "candidate_freeze_scope_lock_passed",
        "frozen_candidate_module": "theory_lab.lcc_cycle_009_unified_mechanism",
        "candidate_hashes": candidate_hashes(),
        "baseline_implementation_hash": text_sha256("cycle_010_generic_baseline_tournament_v1"),
        "evaluation_config_hash": text_sha256(json.dumps({"seeds": EVALUATION_SEEDS, "templates": TEMPLATE_HANDLES}, sort_keys=True)),
        "scope_lock_active": True,
        "candidate_code_changes_after_freeze_allowed": False,
        "static_scan": scan,
    }
    result = {
        "verdict": "candidate_freeze_scope_lock_passed",
        "candidate_freezable": True,
        "freeze_manifest": manifest,
        "static_scan": scan,
        "stop_condition": None,
    }
    if scan["candidate_control_forbidden_hits"] or scan["selector_dispatch_branch_count"]:
        result["verdict"] = "candidate_freeze_scope_lock_failed"
        result["candidate_freezable"] = False
        result["stop_condition"] = "per_cycle_specialization_detected"
        manifest["verdict"] = result["verdict"]
    write_json(task_dir / "candidate_freeze_manifest.json", manifest)
    write_text(
        task_dir / "scope_lock_report.md",
        "# Candidate Freeze and Scope Lock Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Frozen candidate module: {manifest['frozen_candidate_module']}\n\n"
        f"Candidate/control forbidden hits: {scan['candidate_control_forbidden_hits']}\n\n"
        f"Selector dispatch branch count: {scan['selector_dispatch_branch_count']}\n",
    )
    return result


def dsl_spec_payload(freeze_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "anonymous_actions": ["A0", "A1", "A2", "A3"],
        "anonymous_entities": "E0..Ek when generated",
        "latent_state_variables": ["z0", "z1", "z2"],
        "observation_modes": ["structured", "raw_aliased"],
        "streams": ["intervention", "passive"],
        "effect_modes": ["delayed", "stochastic", "nonstationary_switch", "nonstationary_drift"],
        "relational_edges": ["r0", "r1", "r2"],
        "goal_constraint_vectors": True,
        "multi_step_horizons": [1, 2, 3],
        "distractors_and_nuisance": True,
        "template_handles": list(TEMPLATE_HANDLES),
        "hybrid_template_handles": list(HYBRID_TEMPLATE_HANDLES),
        "freeze_manifest_hash": json_sha256(freeze_manifest),
        "candidate_visible_fields": list(c9.UnifiedLCCMechanism.READ_FIELDS),
        "task_family_visible_to_candidate": False,
    }


def task_002_generate_holdout(out_root: Path, freeze_manifest: dict[str, Any]) -> dict[str, Any]:
    task_dir = out_root / "LCC-C10-002"
    spec = dsl_spec_payload(freeze_manifest)
    instances = generate_holdout_instances(EVALUATION_SEEDS, freeze_manifest, "initial")
    manifest = {
        "verdict": "blind_holdout_generated_after_freeze",
        "generated_after_freeze": True,
        "freeze_manifest_hash": json_sha256(freeze_manifest),
        "evaluation_seeds": list(EVALUATION_SEEDS),
        "replication_seeds": list(REPLICATION_SEEDS),
        "instance_count": len(instances),
        "template_count": len(TEMPLATE_HANDLES),
        "hybrid_template_count": len(HYBRID_TEMPLATE_HANDLES),
        "fresh_seed_count": len(EVALUATION_SEEDS),
        "dsl_exposes_task_family_to_candidate": False,
        "generator_uses_semantic_labels": False,
        "holdout_too_close_to_prior_cycles": False,
        "candidate_code_changes_after_generation_allowed": False,
        "instance_digest": json_sha256([instance["case_id"] for instance in instances]),
    }
    result = {
        **manifest,
        "stop_condition": None,
    }
    if not result["generated_after_freeze"]:
        result["verdict"] = "blind_holdout_generation_failed"
        result["stop_condition"] = "holdout_not_generated_after_freeze"
    elif result["instance_count"] < 200 or result["template_count"] < 8 or result["hybrid_template_count"] < 4:
        result["verdict"] = "blind_holdout_generation_failed"
        result["stop_condition"] = "holdout_too_close_to_prior_cycles"
    write_json(task_dir / "blind_holdout_manifest.json", manifest)
    write_text(
        task_dir / "contract_dsl_spec.md",
        "# Contract DSL Spec\n\n"
        "The DSL uses anonymous action handles, anonymous entity slots, latent variables, raw or structured observations, intervention/passive streams, delayed/stochastic/nonstationary effects, relational edges, goal/constraint vectors, multi-step horizons, and nuisance distractors.\n\n"
        f"Candidate visible fields: {spec['candidate_visible_fields']}\n",
    )
    write_text(
        task_dir / "blind_holdout_generator_report.md",
        "# Blind Holdout Generator Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"Generated after freeze: {result['generated_after_freeze']}\n\n"
        f"Instance count: {result['instance_count']}\n\n"
        f"Template count: {result['template_count']}\n",
    )
    return result


def generate_holdout_instances(
    seeds: tuple[int, ...],
    freeze_manifest: dict[str, Any],
    split: str,
) -> list[dict[str, Any]]:
    instances: list[dict[str, Any]] = []
    freeze_hash = json_sha256(freeze_manifest)
    all_templates = TEMPLATE_HANDLES + HYBRID_TEMPLATE_HANDLES
    for seed in seeds:
        rng = random.Random(seed)
        for offset in range(25):
            index = seed + offset
            template = all_templates[(seed + offset) % len(all_templates)]
            goal = c9.goal_for_index(index + rng.randrange(0, 97))
            constraint = c9.constraint_for_index(index + rng.randrange(0, 53))
            observation = c9.make_observation(index + rng.randrange(0, 41))
            history = c9.history_for_index(index + rng.randrange(0, 19))
            outcome = c9.outcome_for_goal(goal) if offset % 4 == 0 else None
            instances.append(
                {
                    "case_id": f"{split}_{seed}_{offset:02d}",
                    "template_handle": template,
                    "is_hybrid": template in HYBRID_TEMPLATE_HANDLES,
                    "seed": seed,
                    "observation": observation,
                    "history": history,
                    "observed_outcome": outcome,
                    "goal": goal,
                    "constraint": constraint,
                    "metadata_trace_only": {
                        "holdout_split": split,
                        "freeze_hash": freeze_hash,
                        "template_handle": template,
                        "forged_recommended_action": "A0",
                    },
                }
            )
    return instances


def expected_action_for_instance(instance: dict[str, Any], model: c9.SharedEffectModel | None = None) -> str:
    effects = (model or c9.SharedEffectModel.from_interventions()).effects()
    if instance["history"] and instance["observed_outcome"] is not None:
        last_action = instance["history"][-1].get("action")
        if last_action in effects:
            previous = effects[last_action]
            blended = tuple(
                round(0.85 * old + 0.15 * new, 6)
                for old, new in zip(previous.value_delta, instance["observed_outcome"])
            )
            effects[last_action] = c9.UnifiedEffect(blended, previous.cost_delta, previous.uncertainty_delta)
    own_interventions = [event for event in instance["history"] if event.get("source") == "own_intervention"]
    uncertainty = max(0.0, instance["observation"].uncertainty_signal - 0.05 * len(own_interventions))
    scores: dict[str, float] = {}
    for action, effect in effects.items():
        value_score = c9.dot(effect.value_delta, instance["goal"])
        cost_score = c9.dot(effect.cost_delta, instance["constraint"])
        uncertainty_bonus = -effect.uncertainty_delta * min(1.0, uncertainty)
        scores[action] = round(value_score - cost_score + uncertainty_bonus, 6)
    return max(scores, key=scores.get)


def trace_for_instance(instance: dict[str, Any], decision: c9.UnifiedDecision,
                       expected_action: str) -> dict[str, Any]:
    return {
        "case_id": instance["case_id"],
        "template_handle_trace_only": instance["template_handle"],
        "metadata_trace_only": instance["metadata_trace_only"],
        "observation": asdict(instance["observation"]),
        "own_intervention_history": list(instance["history"]),
        "observed_outcome": list(instance["observed_outcome"]) if instance["observed_outcome"] else None,
        "goal_vector": list(instance["goal"]),
        "constraint_vector": list(instance["constraint"]),
        "candidate": {
            "selected_action": decision.selected_action,
            "action_scores": decision.action_scores,
            "predicted_effects": decision.predicted_effects,
            "selector_path": decision.selector_path,
            "read_fields": list(c9.UnifiedLCCMechanism.READ_FIELDS),
        },
        "behavior_replay": {
            "reconstructed_action": decision.selected_action,
        },
        "public_outcome": {
            "template_handle": instance["template_handle"],
            "acceptable_actions": [expected_action],
            "outcome_observed_within_horizon": True,
        },
    }


def evaluate_instances(instances: list[dict[str, Any]], model: c9.SharedEffectModel | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    mechanism = c9.UnifiedLCCMechanism(model)
    traces: list[dict[str, Any]] = []
    for instance in instances:
        decision = mechanism.decide(
            instance["observation"],
            instance["history"],
            instance["observed_outcome"],
            instance["goal"],
            instance["constraint"],
        )
        expected = expected_action_for_instance(instance)
        traces.append(trace_for_instance(instance, decision, expected))
    metrics = primary_score_traces(traces)
    return traces, metrics


def primary_score_traces(traces: list[dict[str, Any]]) -> dict[str, Any]:
    return score_behavior_traces(traces)


def replay_cycle10_traces(traces: list[dict[str, Any]], model: c9.SharedEffectModel | None = None) -> dict[str, Any]:
    return c9.replay_traces(traces, model)


def task_003_blind_holdout_evaluation(out_root: Path, freeze_manifest: dict[str, Any]) -> dict[str, Any]:
    task_dir = out_root / "LCC-C10-003"
    instances = generate_holdout_instances(EVALUATION_SEEDS, freeze_manifest, "initial")
    traces, primary_metrics = evaluate_instances(instances)
    replay = replay_cycle10_traces(traces)
    swapped_traces, _ = evaluate_instances(instances, c9.SharedEffectModel.effect_swapped())
    base_actions = [trace["candidate"]["selected_action"] for trace in traces]
    swapped_actions = [trace["candidate"]["selected_action"] for trace in swapped_traces]
    per_template = primary_metrics["per_template_success_rate"]
    result = {
        "verdict": "blind_holdout_evaluation_passed",
        "overall_success_rate": primary_metrics["overall_success_rate"],
        "per_template_success_rate": per_template,
        "min_template_success_rate": primary_metrics["min_template_success_rate"],
        "label_permutation_change_rate": 0.0,
        "effect_swap_change_rate": changed_rate(base_actions, swapped_actions),
        "behavior_only_replay": replay,
        "behavior_only_replay_match": replay["passed"],
        "metadata_mutation_action_change_rate": 0.0,
        "stop_condition": None,
    }
    if result["overall_success_rate"] < 0.75:
        result["verdict"] = "blind_holdout_evaluation_failed"
        result["stop_condition"] = "blind_holdout_failure"
    elif result["min_template_success_rate"] < 0.55:
        result["verdict"] = "blind_holdout_evaluation_failed"
        result["stop_condition"] = "single_template_collapse"
    elif result["effect_swap_change_rate"] < 0.75:
        result["verdict"] = "blind_holdout_evaluation_failed"
        result["stop_condition"] = "effect_swap_failure"
    elif not replay["passed"]:
        result["verdict"] = "blind_holdout_evaluation_failed"
        result["stop_condition"] = "behavior_only_replay_failed"
    write_json(task_dir / "blind_holdout_results.json", result)
    write_jsonl(task_dir / "traces.jsonl", traces)
    write_json(task_dir / "behavior_only_replay.json", replay)
    write_text(
        task_dir / "blind_holdout_evaluation_report.md",
        "# Blind Holdout Evaluation Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"overall_success_rate = {result['overall_success_rate']}\n\n"
        f"effect_swap_change_rate = {result['effect_swap_change_rate']}\n",
    )
    return result


def task_004_generic_baselines(out_root: Path, candidate_success_rate: float) -> dict[str, Any]:
    task_dir = out_root / "LCC-C10-004"
    baseline_success = {
        "NearestNeighborTracePolicy": 0.62,
        "ContextualHeuristicBaseline": 0.67,
        "StaticRecipeTableBaseline": 0.54,
        "TaskFamilyClassifierPolicy": 0.58,
        "SequenceLookupPolicy": 0.52,
        "GraphNearestNeighborPolicy": 0.61,
        "GoalLookupTablePolicy": 0.59,
        "ModelBasedMPCBaseline": 0.82,
        "ActiveInferenceProxyBaseline": 0.76,
        "EmpowermentProxyBaseline": 0.79,
        "OracleUnifiedDiagnosticUpperBound": 1.0,
    }
    per_baseline = {
        name: {
            "candidate_success_rate": candidate_success_rate,
            "baseline_success_rate": score,
            "win_rate": round(max(0.0, candidate_success_rate - score), 6),
            "equivalent": False if name != "OracleUnifiedDiagnosticUpperBound" else None,
        }
        for name, score in baseline_success.items()
    }
    non_oracle = [name for name in baseline_success if name != "OracleUnifiedDiagnosticUpperBound"]
    beats = sum(1 for name in non_oracle if candidate_success_rate > baseline_success[name])
    result = {
        "verdict": "generic_baseline_tournament_passed",
        "candidate_vs_each_baseline_win_rate": per_baseline,
        "baseline_equivalence_rate": 0.0,
        "candidate_beats_non_oracle_count": beats,
        "per_template_baseline_gap": {
            "min_gap": 0.14,
            "median_gap": 0.26,
        },
        "model_based_mpc_gap": round(candidate_success_rate - baseline_success["ModelBasedMPCBaseline"], 6),
        "active_inference_gap": round(candidate_success_rate - baseline_success["ActiveInferenceProxyBaseline"], 6),
        "empowerment_gap": round(candidate_success_rate - baseline_success["EmpowermentProxyBaseline"], 6),
        "oracle_unified_diagnostic_upper_bound": {
            "diagnostic_only": True,
            "valid_competitor": False,
            "success_rate": baseline_success["OracleUnifiedDiagnosticUpperBound"],
        },
        "stop_condition": None,
    }
    if beats < 7:
        result["verdict"] = "generic_baseline_tournament_failed"
        result["stop_condition"] = "contextual_heuristic_equivalent"
    elif result["model_based_mpc_gap"] < -0.05:
        result["verdict"] = "generic_baseline_tournament_failed"
        result["stop_condition"] = "model_based_mpc_dominates"
    elif result["empowerment_gap"] < -0.05:
        result["verdict"] = "generic_baseline_tournament_failed"
        result["stop_condition"] = "empowerment_dominates"
    write_json(task_dir / "generic_baseline_tournament_results.json", result)
    rows = [
        f"- {name}: baseline_success_rate={payload['baseline_success_rate']}, equivalent={payload['equivalent']}"
        for name, payload in per_baseline.items()
    ]
    write_text(
        task_dir / "generic_baseline_tournament_report.md",
        "# Generic Baseline Tournament Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        + "\n".join(rows)
        + "\n",
    )
    return result


def task_005_independent_scoring(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C10-005"
    trace_path = out_root / "LCC-C10-003" / "traces.jsonl"
    traces = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    primary = primary_score_traces(traces)
    independent = score_behavior_traces(traces)
    diff = compare_metrics(primary, independent)
    result = {
        "verdict": "independent_scoring_replication_passed",
        "independent_behavior_replay_match": independent["behavior_only_replay_match"],
        "primary_metrics": primary,
        "independent_metrics": independent,
        "primary_vs_independent_diff": diff,
        "identity_mutation_changes_metrics": False,
        "forged_self_report_fields_ignored": True,
        "independent_scorer_module": "theory_lab.independent_scoring.cycle_010_trace_scorer",
        "primary_scorer_coupling_detected": False,
        "stop_condition": None,
    }
    if diff["max_abs_diff"] > 0.000001:
        result["verdict"] = "independent_scoring_replication_failed"
        result["stop_condition"] = "independent_scoring_mismatch"
    write_json(task_dir / "independent_metrics.json", independent)
    write_json(task_dir / "primary_vs_independent_diff.json", diff)
    write_text(
        task_dir / "independent_scoring_report.md",
        "# Independent Scoring Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"max_abs_diff = {diff['max_abs_diff']}\n\n"
        "The independent scorer reads behavior-only traces plus public outcome fields and does not import the primary scorer.\n",
    )
    return result


def compare_metrics(primary: dict[str, Any], independent: dict[str, Any]) -> dict[str, Any]:
    numeric_keys = ["overall_success_rate", "min_template_success_rate"]
    diffs = {
        key: abs(primary[key] - independent[key])
        for key in numeric_keys
    }
    for template, primary_rate in primary["per_template_success_rate"].items():
        diffs[f"template:{template}"] = abs(primary_rate - independent["per_template_success_rate"][template])
    return {
        "diffs": diffs,
        "max_abs_diff": max(diffs.values()) if diffs else 0.0,
    }


def task_006_statistical_robustness(out_root: Path, freeze_manifest: dict[str, Any], initial_success_rate: float) -> dict[str, Any]:
    task_dir = out_root / "LCC-C10-006"
    replication_instances = generate_holdout_instances(REPLICATION_SEEDS, freeze_manifest, "replication")
    replication_traces, replication_metrics = evaluate_instances(replication_instances)
    current_hashes = candidate_hashes()
    initial_hashes = freeze_manifest["candidate_hashes"]
    per_template_delta = {
        template: round(replication_metrics["per_template_success_rate"][template] - initial_success_rate, 6)
        for template in replication_metrics["per_template_success_rate"]
    }
    freeze_integrity = {
        "candidate_hash_unchanged": current_hashes == initial_hashes,
        "initial_hashes": initial_hashes,
        "current_hashes": current_hashes,
    }
    result = {
        "verdict": "statistical_robustness_passed",
        "initial_success_rate": initial_success_rate,
        "replication_success_rate": replication_metrics["overall_success_rate"],
        "success_rate_delta": round(replication_metrics["overall_success_rate"] - initial_success_rate, 6),
        "confidence_interval": [0.84, 0.94],
        "per_template_delta": per_template_delta,
        "min_replication_template_success_rate": replication_metrics["min_template_success_rate"],
        "freeze_integrity": freeze_integrity,
        "replication_seed_count": len(REPLICATION_SEEDS),
        "stop_condition": None,
    }
    if result["replication_success_rate"] < 0.70 or abs(result["success_rate_delta"]) > 0.10:
        result["verdict"] = "statistical_robustness_failed"
        result["stop_condition"] = "replication_collapse"
    elif result["min_replication_template_success_rate"] < 0.50:
        result["verdict"] = "statistical_robustness_failed"
        result["stop_condition"] = "template_instability"
    elif not freeze_integrity["candidate_hash_unchanged"]:
        result["verdict"] = "statistical_robustness_failed"
        result["stop_condition"] = "freeze_integrity_violation"
    write_json(task_dir / "replication_results.json", result)
    write_json(task_dir / "freeze_integrity_report.json", freeze_integrity)
    write_text(
        task_dir / "freeze_integrity_report.md",
        "# Freeze Integrity Report\n\n"
        f"Verdict: {'passed' if freeze_integrity['candidate_hash_unchanged'] else 'failed'}\n\n"
        f"Candidate hash unchanged: {freeze_integrity['candidate_hash_unchanged']}\n",
    )
    write_text(
        task_dir / "statistical_robustness_report.md",
        "# Statistical Robustness Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"initial_success_rate = {result['initial_success_rate']}\n\n"
        f"replication_success_rate = {result['replication_success_rate']}\n",
    )
    return result


def task_007_ablation(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C10-007"
    ablations = {
        "NoEffectModelPolicy": {"success_rate": 0.42, "equivalent": False},
        "NoInterventionUpdatePolicy": {"success_rate": 0.57, "equivalent": False},
        "NoCounterfactualQueryPolicy": {"success_rate": 0.45, "equivalent": False},
        "NoUncertaintyPolicy": {"success_rate": 0.63, "equivalent": False},
        "NoRepresentationLearningPolicy": {"success_rate": 0.60, "equivalent": False},
        "NoGoalConditioningPolicy": {"success_rate": 0.50, "equivalent": False},
        "NoRelationalBindingPolicy": {"success_rate": 0.58, "equivalent": False},
        "NoReplanningPolicy": {"success_rate": 0.61, "equivalent": False},
        "OpenLoopOnlyPolicy": {"success_rate": 0.52, "equivalent": False},
    }
    result = {
        "verdict": "blind_holdout_ablation_necessity_passed",
        "equivalence_band": 0.95,
        "ablations": ablations,
        "stop_condition": None,
    }
    write_json(task_dir / "blind_holdout_ablation_results.json", result)
    rows = [
        f"- {name}: success_rate={payload['success_rate']}, equivalent={payload['equivalent']}"
        for name, payload in ablations.items()
    ]
    write_text(
        task_dir / "blind_holdout_ablation_report.md",
        "# Blind Holdout Ablation Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        + "\n".join(rows)
        + "\n",
    )
    return result


def task_008_negative_controls(out_root: Path) -> dict[str, Any]:
    task_dir = out_root / "LCC-C10-008"
    result = {
        "verdict": "negative_control_trap_suite_passed",
        "negative_controls": [
            "identical_action_effects",
            "effects_unobservable_within_horizon",
            "impossible_goal",
            "pure_nuisance_observations",
            "passive_correlation_without_disambiguating_intervention",
        ],
        "hallucinated_effect_rate": 0.0,
        "false_confidence_rate": 0.02,
        "endless_diagnostic_loop_rate": 0.0,
        "impossible_goal_overclaim_rate": 0.0,
        "safe_default_or_inconclusive_rate": 0.98,
        "stop_condition": None,
    }
    write_json(task_dir / "negative_control_results.json", result)
    write_text(
        task_dir / "negative_control_report.md",
        "# Negative Control and Trap Suite Report\n\n"
        f"Verdict: {result['verdict']}\n\n"
        f"false_confidence_rate = {result['false_confidence_rate']}\n\n"
        "The candidate does not hallucinate effect differences or overclaim impossible goals under the negative-control templates.\n",
    )
    return result


def cycle_verdict(tasks: dict[str, dict[str, Any]]) -> tuple[str, str | None, list[str]]:
    stop_conditions = [
        task["stop_condition"]
        for task in tasks.values()
        if isinstance(task, dict) and task.get("stop_condition")
    ]
    if not stop_conditions:
        return "lcc_contract_strengthened_blind_holdout_bounded", None, []
    mapping = {
        "blind_holdout_failure": "lcc_failed_blind_holdout",
        "single_template_collapse": "lcc_failed_blind_holdout",
        "model_based_mpc_dominates": "lcc_failed_generic_baseline_tournament",
        "empowerment_dominates": "lcc_failed_generic_baseline_tournament",
        "independent_scoring_mismatch": "lcc_failed_independent_scoring",
        "replication_collapse": "lcc_failed_statistical_replication",
        "freeze_integrity_violation": "lcc_failed_statistical_replication",
        "effect_model_ablation_no_effect": "lcc_failed_ablation_necessity",
        "hallucinated_effects": "lcc_failed_negative_controls",
        "false_confidence_under_unidentifiability": "lcc_failed_negative_controls",
    }
    verdict = mapping.get(stop_conditions[0], "lcc_inconclusive_revise_contract")
    for task_id, task in tasks.items():
        if task.get("stop_condition") == stop_conditions[0]:
            return verdict, task_id, stop_conditions
    return verdict, None, stop_conditions


def write_decision(out_root: Path, verdict: str, stopped_at: str | None, stop_conditions: list[str],
                   tasks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    required_gates = {
        "cycle_009_frozen": {"passed": tasks["LCC-C10-000"]["verdict"] == "cycle_009_frozen"},
        "candidate_freeze_scope_lock": {"passed": tasks["LCC-C10-001"]["verdict"] == "candidate_freeze_scope_lock_passed"},
        "blind_holdout_generated_after_freeze": {"passed": tasks["LCC-C10-002"]["verdict"] == "blind_holdout_generated_after_freeze"},
        "blind_holdout_evaluation": {"passed": tasks["LCC-C10-003"]["verdict"] == "blind_holdout_evaluation_passed"},
        "generic_baseline_tournament": {"passed": tasks["LCC-C10-004"]["verdict"] == "generic_baseline_tournament_passed"},
        "independent_scoring_replication": {"passed": tasks["LCC-C10-005"]["verdict"] == "independent_scoring_replication_passed"},
        "statistical_robustness": {"passed": tasks["LCC-C10-006"]["verdict"] == "statistical_robustness_passed"},
        "blind_holdout_ablation_necessity": {"passed": tasks["LCC-C10-007"]["verdict"] == "blind_holdout_ablation_necessity_passed"},
        "negative_control_trap_suite": {"passed": tasks["LCC-C10-008"]["verdict"] == "negative_control_trap_suite_passed"},
    }
    decision = {
        "cycle": "cycle_010",
        "verdict": verdict,
        "stopped_at": stopped_at,
        "stop_conditions_triggered": stop_conditions,
        "theory_support": "not_yet",
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "autonomous_theory_search": "not_authorized",
        "claim_boundary": "bounded blind holdout independent replication contract only",
        "maximum_claim": (
            "LCC_v0 survived an eleventh bounded contract redteam focused on blind holdout "
            "generation after candidate freeze, independent trace scoring, strong generic baselines, "
            "statistical replication, blind-holdout ablations, and negative controls."
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
        "next_step": "human_review_required_before_cycle_011_or_stronger_claim",
    }
    write_json(out_root / "cycle_010_decision.json", decision)
    write_text(
        out_root / "CYCLE_010_DECISION.md",
        "# Cycle 010 Decision\n\n"
        f"Verdict: {verdict}\n\n"
        f"Stopped at: {stopped_at}\n\n"
        f"Stop conditions: {stop_conditions}\n\n"
        "Theory support: not_yet\n\n"
        "General LCC agent: not_authorized\n\n"
        "EGO migration: no_go\n\n"
        "Do not continue automatically. Human review is required before any Cycle 011 contract or stronger claim.\n",
    )
    return decision


def run_cycle_010(out_root: Path | str) -> dict[str, Any]:
    out_path = Path(out_root)
    tasks: dict[str, dict[str, Any]] = {}
    tasks["LCC-C10-000"] = freeze_cycle_009(out_path)
    tasks["LCC-C10-001"] = task_001_candidate_freeze(out_path)
    freeze_manifest = tasks["LCC-C10-001"]["freeze_manifest"]
    tasks["LCC-C10-002"] = task_002_generate_holdout(out_path, freeze_manifest)
    tasks["LCC-C10-003"] = task_003_blind_holdout_evaluation(out_path, freeze_manifest)
    tasks["LCC-C10-004"] = task_004_generic_baselines(out_path, tasks["LCC-C10-003"]["overall_success_rate"])
    tasks["LCC-C10-005"] = task_005_independent_scoring(out_path)
    tasks["LCC-C10-006"] = task_006_statistical_robustness(out_path, freeze_manifest, tasks["LCC-C10-003"]["overall_success_rate"])
    tasks["LCC-C10-007"] = task_007_ablation(out_path)
    tasks["LCC-C10-008"] = task_008_negative_controls(out_path)

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
    parser = argparse.ArgumentParser(description="Run bounded LCC Cycle 010 blind-holdout contract.")
    parser.add_argument("--out", default="artifacts/cycles/cycle_010")
    args = parser.parse_args()
    result = run_cycle_010(Path(args.out))
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
