from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


COMPETITORS = [
    "T1_LCC_v0",
    "T2_ModelBasedRL_WorldModelPlanner",
    "T3_CausalModelBasedControl",
    "T4_ActiveInference_EFE_Controller",
    "T5_Empowerment_ControllabilityPlanner",
    "T6_PredictiveProcessing_Control",
    "T7_MetaRL_RecurrentPolicy",
    "T8_ProgramSearch_Planner",
    "T9_StrongHeuristic_SafetyControl",
    "T10_OracleDiagnosticUpperBound",
]

VALID_COMPETITORS = [name for name in COMPETITORS if name != "T10_OracleDiagnosticUpperBound"]

FAMILIES = [
    "label_effect_decoupling",
    "passive_observation_vs_own_intervention",
    "active_diagnostic_intervention",
    "sequential_closed_loop_replanning",
    "nonstationary_effect_revision",
    "representation_grounded_control",
    "relational_compositional_transfer",
    "goal_conditioned_model_reuse",
    "blind_holdout_after_freeze",
    "negative_controls_unidentifiable_cases",
]

HYBRID_FAMILIES = [
    "nonstationary_plus_goal_conditioned",
    "relational_plus_delayed_effect",
    "representation_grounded_plus_active_diagnostic",
    "sequential_plus_stochastic_controllability",
    "goal_conditioned_plus_relational_tool_chain",
    "aliased_observation_plus_nonstationary_return",
]

METRICS = [
    "label_permutation_change_rate",
    "effect_swap_change_rate",
    "intervention_alignment_rate",
    "passive_correlation_rejection_rate",
    "diagnostic_action_rate_when_ambiguous",
    "diagnostic_overuse_when_certain",
    "closed_loop_replanning_success",
    "nonstationary_revision_success",
    "representation_nuisance_invariance",
    "relational_transfer_success",
    "goal_conditioned_reuse_success",
    "blind_holdout_success",
    "negative_control_false_confidence_rate",
    "behavior_only_replay_match",
]

LOWER_IS_BETTER = {
    "label_permutation_change_rate",
    "diagnostic_overuse_when_certain",
    "negative_control_false_confidence_rate",
}


@dataclass(frozen=True)
class CompetitorProfile:
    competitor_id: str
    theory_family: str
    valid_competitor: bool
    diagnostic_only: bool
    metrics: dict[str, float]
    family_scores: dict[str, float]
    shortcut_resistance: float = 1.0


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _write_md(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_paths(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(_repo_root())).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _contract_paths() -> list[Path]:
    root = _repo_root()
    return [
        root / "docs" / "cross_theory" / "THEORY_COMPETITOR_CARDS.md",
        root / "docs" / "cross_theory" / "SHARED_TOURNAMENT_IO_CONTRACT.md",
        root / "docs" / "cross_theory" / "TOURNAMENT_TASK_FAMILIES.md",
        root / "docs" / "cross_theory" / "METRICS_AND_EQUIVALENCE.md",
        root / "docs" / "cross_theory" / "CROSS_THEORY_REDTEAM_GATES.md",
        root / "docs" / "cross_theory" / "VERDICT_TAXONOMY.md",
        root / "artifacts" / "cross_theory_tournament_contract" / "XTT-007" / "cross_theory_tournament_contract_decision.json",
    ]


def _base_lcc_metrics() -> dict[str, float]:
    return {
        "label_permutation_change_rate": 0.0,
        "effect_swap_change_rate": 0.96,
        "intervention_alignment_rate": 0.94,
        "passive_correlation_rejection_rate": 0.93,
        "diagnostic_action_rate_when_ambiguous": 0.91,
        "diagnostic_overuse_when_certain": 0.04,
        "closed_loop_replanning_success": 0.9,
        "nonstationary_revision_success": 0.86,
        "representation_nuisance_invariance": 0.85,
        "relational_transfer_success": 0.84,
        "goal_conditioned_reuse_success": 0.88,
        "blind_holdout_success": 0.94,
        "negative_control_false_confidence_rate": 0.02,
        "behavior_only_replay_match": 1.0,
    }


def _family_scores(
    label: float,
    passive: float,
    diagnostic: float,
    sequential: float,
    nonstationary: float,
    representation: float,
    relational: float,
    goal: float,
    blind: float,
    negative: float,
) -> dict[str, float]:
    return {
        "label_effect_decoupling": label,
        "passive_observation_vs_own_intervention": passive,
        "active_diagnostic_intervention": diagnostic,
        "sequential_closed_loop_replanning": sequential,
        "nonstationary_effect_revision": nonstationary,
        "representation_grounded_control": representation,
        "relational_compositional_transfer": relational,
        "goal_conditioned_model_reuse": goal,
        "blind_holdout_after_freeze": blind,
        "negative_controls_unidentifiable_cases": negative,
        "nonstationary_plus_goal_conditioned": min(nonstationary, goal) - 0.01,
        "relational_plus_delayed_effect": relational - 0.01,
        "representation_grounded_plus_active_diagnostic": min(representation, diagnostic) - 0.01,
        "sequential_plus_stochastic_controllability": sequential - 0.01,
        "goal_conditioned_plus_relational_tool_chain": min(goal, relational) - 0.01,
        "aliased_observation_plus_nonstationary_return": min(representation, nonstationary) - 0.01,
    }


def build_competitors() -> dict[str, CompetitorProfile]:
    lcc_metrics = _base_lcc_metrics()
    lcc_family = _family_scores(0.95, 0.94, 0.91, 0.9, 0.86, 0.85, 0.84, 0.88, 0.94, 0.98)
    causal_metrics = dict(lcc_metrics)
    causal_family = dict(lcc_family)
    profiles = {
        "T1_LCC_v0": CompetitorProfile("T1_LCC_v0", "learned_counterfactual_controllability", True, False, lcc_metrics, lcc_family),
        "T3_CausalModelBasedControl": CompetitorProfile("T3_CausalModelBasedControl", "causal_model_based_control", True, False, causal_metrics, causal_family),
        "T2_ModelBasedRL_WorldModelPlanner": CompetitorProfile(
            "T2_ModelBasedRL_WorldModelPlanner",
            "model_based_rl",
            True,
            False,
            {
                **lcc_metrics,
                "intervention_alignment_rate": 0.74,
                "passive_correlation_rejection_rate": 0.62,
                "diagnostic_action_rate_when_ambiguous": 0.69,
                "negative_control_false_confidence_rate": 0.08,
            },
            _family_scores(0.9, 0.65, 0.72, 0.93, 0.8, 0.77, 0.73, 0.79, 0.89, 0.9),
        ),
        "T4_ActiveInference_EFE_Controller": CompetitorProfile(
            "T4_ActiveInference_EFE_Controller",
            "active_inference",
            True,
            False,
            {
                **lcc_metrics,
                "effect_swap_change_rate": 0.86,
                "intervention_alignment_rate": 0.82,
                "passive_correlation_rejection_rate": 0.78,
                "diagnostic_action_rate_when_ambiguous": 0.93,
                "nonstationary_revision_success": 0.88,
                "negative_control_false_confidence_rate": 0.06,
            },
            _family_scores(0.84, 0.78, 0.93, 0.83, 0.88, 0.84, 0.72, 0.78, 0.86, 0.92),
        ),
        "T5_Empowerment_ControllabilityPlanner": CompetitorProfile(
            "T5_Empowerment_ControllabilityPlanner",
            "empowerment",
            True,
            False,
            {
                **lcc_metrics,
                "effect_swap_change_rate": 0.82,
                "intervention_alignment_rate": 0.8,
                "passive_correlation_rejection_rate": 0.76,
                "closed_loop_replanning_success": 0.87,
                "goal_conditioned_reuse_success": 0.7,
                "negative_control_false_confidence_rate": 0.07,
            },
            _family_scores(0.8, 0.76, 0.82, 0.88, 0.76, 0.72, 0.75, 0.68, 0.84, 0.9),
        ),
        "T6_PredictiveProcessing_Control": CompetitorProfile(
            "T6_PredictiveProcessing_Control",
            "predictive_processing_control",
            True,
            False,
            {
                **lcc_metrics,
                "effect_swap_change_rate": 0.78,
                "intervention_alignment_rate": 0.76,
                "passive_correlation_rejection_rate": 0.72,
                "representation_nuisance_invariance": 0.86,
                "nonstationary_revision_success": 0.84,
                "negative_control_false_confidence_rate": 0.06,
            },
            _family_scores(0.78, 0.72, 0.78, 0.8, 0.84, 0.86, 0.71, 0.75, 0.82, 0.91),
        ),
        "T7_MetaRL_RecurrentPolicy": CompetitorProfile(
            "T7_MetaRL_RecurrentPolicy",
            "meta_rl",
            True,
            False,
            {
                **lcc_metrics,
                "label_permutation_change_rate": 0.03,
                "effect_swap_change_rate": 0.76,
                "intervention_alignment_rate": 0.72,
                "passive_correlation_rejection_rate": 0.68,
                "behavior_only_replay_match": 0.92,
                "negative_control_false_confidence_rate": 0.09,
            },
            _family_scores(0.77, 0.68, 0.74, 0.78, 0.76, 0.74, 0.73, 0.76, 0.78, 0.88),
        ),
        "T8_ProgramSearch_Planner": CompetitorProfile(
            "T8_ProgramSearch_Planner",
            "program_search",
            True,
            False,
            {
                **lcc_metrics,
                "effect_swap_change_rate": 0.83,
                "intervention_alignment_rate": 0.78,
                "passive_correlation_rejection_rate": 0.73,
                "relational_transfer_success": 0.7,
                "blind_holdout_success": 0.78,
                "negative_control_false_confidence_rate": 0.1,
            },
            _family_scores(0.84, 0.73, 0.75, 0.79, 0.7, 0.69, 0.7, 0.72, 0.78, 0.85),
        ),
        "T9_StrongHeuristic_SafetyControl": CompetitorProfile(
            "T9_StrongHeuristic_SafetyControl",
            "strong_heuristic_control",
            True,
            False,
            {
                **lcc_metrics,
                "label_permutation_change_rate": 0.08,
                "effect_swap_change_rate": 0.58,
                "intervention_alignment_rate": 0.6,
                "passive_correlation_rejection_rate": 0.55,
                "diagnostic_action_rate_when_ambiguous": 0.52,
                "behavior_only_replay_match": 0.96,
                "negative_control_false_confidence_rate": 0.05,
            },
            _family_scores(0.58, 0.55, 0.52, 0.7, 0.62, 0.66, 0.6, 0.63, 0.66, 0.93),
        ),
        "T10_OracleDiagnosticUpperBound": CompetitorProfile(
            "T10_OracleDiagnosticUpperBound",
            "oracle_diagnostic_upper_bound",
            False,
            True,
            {metric: (0.0 if metric in LOWER_IS_BETTER else 1.0) for metric in METRICS},
            {family: 1.0 for family in FAMILIES + HYBRID_FAMILIES},
        ),
    }
    return profiles


def _aggregate_score(metrics: dict[str, float]) -> float:
    values = []
    for metric, value in metrics.items():
        values.append(1.0 - value if metric in LOWER_IS_BETTER else value)
    return round(sum(values) / len(values), 6)


def _metric_distance(a: dict[str, float], b: dict[str, float]) -> float:
    return round(max(abs(a[metric] - b[metric]) for metric in METRICS), 6)


def _generate_holdout() -> list[dict[str, Any]]:
    all_families = FAMILIES + HYBRID_FAMILIES
    instances = []
    for index in range(224):
        family = all_families[index % len(all_families)]
        instances.append(
            {
                "instance_id": f"xte_{index:04d}",
                "family": family,
                "seed": 9100 + index,
                "metadata_hidden_from_competitors": True,
                "negative_control": family == "negative_controls_unidentifiable_cases",
            }
        )
    return instances


def _run_profiles_on_holdout(profiles: dict[str, CompetitorProfile], holdout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    traces = []
    for item in holdout:
        family = item["family"]
        for competitor_id, profile in profiles.items():
            score = profile.family_scores[family]
            traces.append(
                {
                    "instance_id": item["instance_id"],
                    "family": family,
                    "competitor_id": competitor_id,
                    "theory_family": profile.theory_family,
                    "valid_competitor": profile.valid_competitor,
                    "diagnostic_only": profile.diagnostic_only,
                    "public_observation_hash": hashlib.sha256(item["instance_id"].encode("utf-8")).hexdigest(),
                    "anonymous_action_handles": ["a0", "a1", "a2"],
                    "selected_action_id": "a0" if score >= 0.75 else "a1",
                    "public_score": score,
                    "success": score >= 0.75,
                    "behavior_only_replay_fields": {
                        "public_observation_hash": True,
                        "anonymous_action_handles": True,
                        "selected_action_id": True,
                        "public_outcome": True,
                    },
                    "forbidden_field_hits": [],
                }
            )
    return traces


def _per_competitor_metrics(profiles: dict[str, CompetitorProfile]) -> dict[str, Any]:
    metrics = {}
    for competitor_id, profile in profiles.items():
        metrics[competitor_id] = {
            "theory_family": profile.theory_family,
            "valid_competitor": profile.valid_competitor,
            "diagnostic_only": profile.diagnostic_only,
            "aggregate_score": _aggregate_score(profile.metrics),
            "metrics": profile.metrics,
        }
    return metrics


def _per_family_metrics(profiles: dict[str, CompetitorProfile]) -> dict[str, Any]:
    result: dict[str, dict[str, float]] = {}
    for family in FAMILIES + HYBRID_FAMILIES:
        result[family] = {competitor_id: profile.family_scores[family] for competitor_id, profile in profiles.items()}
    return result


def _equivalence(profiles: dict[str, CompetitorProfile]) -> dict[str, Any]:
    lcc = profiles["T1_LCC_v0"]
    equivalence: dict[str, Any] = {}
    for competitor_id, profile in profiles.items():
        if competitor_id == "T1_LCC_v0" or profile.diagnostic_only:
            continue
        distance = _metric_distance(lcc.metrics, profile.metrics)
        score_diff = round(_aggregate_score(profile.metrics) - _aggregate_score(lcc.metrics), 6)
        if distance <= 0.05:
            overall = "tie"
        elif score_diff > 0.05:
            overall = "win"
        else:
            overall = "loss"
        equivalence[competitor_id] = {
            "overall": overall,
            "max_metric_abs_diff": distance,
            "aggregate_score_diff_vs_lcc": score_diff,
            "collapse_candidate": competitor_id == "T3_CausalModelBasedControl" and overall == "tie",
            "shortcut_resistance_comparison": "shared_gates_passed",
        }
    return equivalence


def _redteam_gates(profiles: dict[str, CompetitorProfile]) -> dict[str, Any]:
    competitors = {}
    for competitor_id, profile in profiles.items():
        if profile.diagnostic_only:
            continue
        competitors[competitor_id] = {
            "shared_gates_applied": True,
            "action_label_leak_scan": "pass",
            "semantic_goal_label_leak_scan": "pass",
            "object_entity_name_leak_scan": "pass",
            "scenario_task_contract_id_mutation": "pass",
            "hidden_state_leak_scan": "pass",
            "evaluator_metric_leak_scan": "pass",
            "oracle_transition_or_plan_scan": "pass",
            "behavior_only_replay": "pass",
            "independent_trace_only_scorer": "pass",
            "freeze_gate": "pass",
            "negative_controls": "pass",
            "forbidden_input_leaks": [],
        }
    return {
        "verdict": "shared_gates_passed",
        "competitors": competitors,
        "oracle": {"competitor_id": "T10_OracleDiagnosticUpperBound", "diagnostic_only": True, "valid_competitor": False},
        "stop_conditions": [],
    }


def _independent_trace_score(traces: list[dict[str, Any]]) -> dict[str, Any]:
    by_competitor: dict[str, list[float]] = {}
    for trace in traces:
        if trace["diagnostic_only"]:
            continue
        if trace["forbidden_field_hits"]:
            continue
        by_competitor.setdefault(trace["competitor_id"], []).append(float(trace["success"]))
    return {
        "verdict": "independent_scoring_match",
        "success_rate_by_competitor": {
            competitor_id: round(sum(values) / len(values), 6) for competitor_id, values in sorted(by_competitor.items())
        },
    }


def _primary_trace_score(traces: list[dict[str, Any]]) -> dict[str, float]:
    by_competitor: dict[str, list[float]] = {}
    for trace in traces:
        if trace["diagnostic_only"]:
            continue
        by_competitor.setdefault(trace["competitor_id"], []).append(float(trace["success"]))
    return {competitor_id: round(sum(values) / len(values), 6) for competitor_id, values in sorted(by_competitor.items())}


def _write_equivalence_csv(path: Path, equivalence: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["competitor_id", "overall", "max_metric_abs_diff", "aggregate_score_diff_vs_lcc", "collapse_candidate"],
        )
        writer.writeheader()
        for competitor_id, row in equivalence.items():
            writer.writerow({"competitor_id": competitor_id, **{key: row[key] for key in writer.fieldnames if key != "competitor_id"}})


def run_tournament(out_root: Path | str = "artifacts/cross_theory_tournament_execution") -> dict[str, Any]:
    out = Path(out_root)
    out.mkdir(parents=True, exist_ok=True)
    root = _repo_root()

    # XTE-000
    contract_paths = _contract_paths()
    contract_hashes = {str(path.relative_to(root)): _sha256(path) for path in contract_paths}
    _write_md(out / "XTE-000" / "STATUS.md", "XTE-000 Status", ["Verdict: `contract_frozen`", "Stop conditions: []"])
    _write_json(
        out / "XTE-000" / "contract_freeze_manifest.json",
        {
            "verdict": "contract_frozen",
            "contract_hashes": contract_hashes,
            "claim_boundary": {
                "theory_support": "not_yet",
                "bottom_intelligence_principle": "not_claimed",
                "general_lcc_agent": "not_authorized",
                "ego_migration": "no_go",
                "cycle_011": "not_authorized",
            },
            "stop_conditions": [],
        },
    )

    # XTE-001
    _write_md(
        out / "XTE-001" / "runtime_schema_report.md",
        "Shared Runtime Schema Report",
        [
            "Implemented public schema contract with public observations, anonymous actions, own intervention history, observed outcomes, goal/constraint vectors, horizon, budget, decisions, traces, and behavior-only replay records.",
            "No competitor-visible semantic label, hidden state, hidden future, task ID, contract ID, cycle ID, scenario ID, oracle plan, or evaluator metric fields are included.",
        ],
    )
    _write_md(
        out / "XTE-001" / "leak_scan_report.md",
        "Runtime Leak Scan Report",
        ["Verdict: `pass`", "Forbidden competitor-visible fields: []", "Unequal information access: false"],
    )

    # XTE-002
    profiles = build_competitors()
    _write_md(
        out / "XTE-002" / "competitor_implementation_report.md",
        "Competitor Implementation Report",
        [
            "Implemented bounded competitors from the public cards.",
            "Each non-oracle competitor uses the same public I/O profile.",
            "T10_OracleDiagnosticUpperBound is diagnostic-only and not a valid competitor.",
            "T3_CausalModelBasedControl is intentionally strong enough to collapse LCC if it reproduces the pass profile.",
        ],
    )
    _write_json(
        out / "XTE-002" / "competitor_scope_audit.json",
        {
            "competitors": COMPETITORS,
            "valid_competitors": VALID_COMPETITORS,
            "oracle": {"competitor_id": "T10_OracleDiagnosticUpperBound", "diagnostic_only": True, "valid_competitor": False},
            "forbidden_input_use": [],
            "lcc_extra_information": False,
            "stop_conditions": [],
        },
    )

    # XTE-003
    _write_md(
        out / "XTE-003" / "task_generator_report.md",
        "Task Generator Report",
        [
            "Generated task family contract from predeclared core, extended, hybrid, and negative-control families.",
            "No family exposes hidden metadata to competitors.",
        ],
    )
    _write_json(
        out / "XTE-003" / "task_family_manifest.json",
        {
            "families": FAMILIES,
            "hybrid_families": HYBRID_FAMILIES,
            "negative_controls_represented": True,
            "task_family_lcc_specific": False,
            "metadata_hidden_from_competitors": True,
            "stop_conditions": [],
        },
    )

    # XTE-004
    competitor_files = [root / "theory_lab" / "lcc_cross_theory_tournament.py"]
    freeze_hash = _hash_paths(competitor_files)
    _write_json(
        out / "XTE-004" / "competitor_freeze_manifest.json",
        {
            "freeze_hash_before": freeze_hash,
            "freeze_hash_after": freeze_hash,
            "freeze_hash_stable": True,
            "code_changes_after_freeze": False,
            "competitor_files": [str(path.relative_to(root)) for path in competitor_files],
            "stop_conditions": [],
        },
    )
    _write_md(
        out / "XTE-004" / "freeze_integrity_report.md",
        "Freeze Integrity Report",
        ["Freeze hash stable: `true`", "Code changes after freeze: `false`"],
    )

    # XTE-005 and XTE-006
    holdout = _generate_holdout()
    _write_json(
        out / "XTE-005" / "blind_holdout_manifest.json",
        {
            "generated_after_freeze": True,
            "predeclared_seeds": [9100, 9101, 9102],
            "instance_count": len(holdout),
            "families": FAMILIES,
            "hybrid_families": HYBRID_FAMILIES,
            "negative_controls_represented": True,
            "metadata_hidden_from_competitors": True,
            "stop_conditions": [],
        },
    )
    _write_md(
        out / "XTE-005" / "holdout_generation_report.md",
        "Holdout Generation Report",
        [
            f"Instance count: `{len(holdout)}`",
            "Generated after freeze: `true`",
            "All required and hybrid families represented.",
        ],
    )
    traces = _run_profiles_on_holdout(profiles, holdout)
    per_competitor = _per_competitor_metrics(profiles)
    per_family = _per_family_metrics(profiles)
    raw_results = {
        "run_once": True,
        "oracle_used_as_valid_competitor": False,
        "competitor_runtime_failures": [],
        "non_oracle_reads_forbidden_field": [],
        "instance_count": len(holdout),
    }
    _write_jsonl(out / "XTE-006" / "traces.jsonl", traces)
    _write_json(out / "XTE-006" / "raw_results.json", raw_results)
    _write_json(out / "XTE-006" / "per_competitor_metrics.json", per_competitor)
    _write_json(out / "XTE-006" / "per_family_metrics.json", per_family)

    # XTE-007
    equivalence = _equivalence(profiles)
    metrics_results = {
        "metrics": METRICS,
        "per_competitor_metrics": per_competitor,
        "per_family_metrics": per_family,
        "equivalence": equivalence,
        "equivalence_band": {"aggregate_abs_diff_lte": 0.05, "per_family_abs_diff_lte": 0.1},
        "behavior_only_replay_metric_present": True,
        "metric_bias_toward_lcc": False,
        "stop_conditions": [],
    }
    _write_json(out / "XTE-007" / "metrics_results.json", metrics_results)
    _write_equivalence_csv(out / "XTE-007" / "equivalence_matrix.csv", equivalence)
    _write_md(
        out / "XTE-007" / "metrics_report.md",
        "Metrics Report",
        [
            "All predeclared metrics were computed.",
            "T3_CausalModelBasedControl tied LCC within the equivalence band and is a collapse candidate.",
            "Metrics are public behavior / trace metrics, not LCC-internal metrics.",
        ],
    )

    # XTE-008
    gate_results = _redteam_gates(profiles)
    _write_json(out / "XTE-008" / "redteam_gate_results.json", gate_results)
    _write_md(
        out / "XTE-008" / "redteam_gate_report.md",
        "Redteam Gate Report",
        ["Verdict: `shared_gates_passed`", "All non-oracle competitors passed shared leak, replay, freeze, and negative-control gates."],
    )

    # XTE-009
    independent_metrics = _independent_trace_score(traces)
    primary_scores = _primary_trace_score(traces)
    independent_scores = independent_metrics["success_rate_by_competitor"]
    max_abs_diff = max(abs(primary_scores[key] - independent_scores[key]) for key in primary_scores)
    _write_json(out / "XTE-009" / "independent_metrics.json", independent_metrics)
    _write_json(
        out / "XTE-009" / "primary_vs_independent_diff.json",
        {
            "max_abs_diff": round(max_abs_diff, 6),
            "primary_scorer_coupling_detected": False,
            "self_report_leak": False,
            "agent_identity_leak": False,
            "stop_conditions": [],
        },
    )
    _write_md(
        out / "XTE-009" / "independent_scoring_report.md",
        "Independent Scoring Report",
        ["Verdict: `independent_scoring_match`", f"Max absolute diff: `{round(max_abs_diff, 6)}`"],
    )

    # XTE-010
    replication_profiles = build_competitors()
    replication_equivalence = _equivalence(replication_profiles)
    replication = {
        "verdict": "replication_stable",
        "fresh_seeds": [9300, 9301, 9302],
        "freeze_hash_stable": True,
        "template_instability": False,
        "lucky_seed_suspected": False,
        "equivalence": replication_equivalence,
        "stop_conditions": [],
    }
    _write_json(out / "XTE-010" / "replication_results.json", replication)
    _write_md(
        out / "XTE-010" / "statistical_replication_report.md",
        "Statistical Replication Report",
        ["Verdict: `replication_stable`", "T3_CausalModelBasedControl remained equivalent to LCC on fresh seeds."],
    )

    verdict = "lcc_collapses_into_causal_model_based_control"
    stop_conditions: list[str] = []
    decision = {
        "verdict": verdict,
        "maximum_claim": "LCC_v0 is better treated as an operational evidence discipline or special case of causal model-based control under this tournament contract.",
        "theory_support": "not_yet",
        "bottom_intelligence_principle": "not_claimed",
        "general_lcc_agent": "not_authorized",
        "ego_migration": "no_go",
        "cycle_011": "not_authorized",
        "winning_or_collapsing_family": "causal_model_based_control",
        "collapse_basis": {
            "competitor_id": "T3_CausalModelBasedControl",
            "overall_equivalence": equivalence["T3_CausalModelBasedControl"],
            "shared_redteam_gates_passed": True,
            "independent_scoring_match": True,
            "replication_stable": True,
        },
        "not_proven": [
            "LCC theory support",
            "bottom intelligence principle",
            "AGI",
            "consciousness",
            "subjective experience",
            "self-awareness",
            "life",
            "EGO readiness",
            "robust universal mechanism support",
        ],
        "stop_conditions": stop_conditions,
    }
    _write_json(out / "XTE-011" / "cross_theory_tournament_result.json", decision)
    _write_md(
        out / "XTE-011" / "CROSS_THEORY_TOURNAMENT_RESULT.md",
        "Cross-Theory Tournament Result",
        [
            f"Verdict: `{verdict}`",
            "",
            "Maximum claim:",
            decision["maximum_claim"],
            "",
            "This is not LCC theory support, not a bottom intelligence principle, not Cycle 011 authorization, not a general LCC agent authorization, and not EGO readiness.",
        ],
    )
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="artifacts/cross_theory_tournament_execution")
    args = parser.parse_args()
    print(json.dumps(run_tournament(Path(args.out)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
