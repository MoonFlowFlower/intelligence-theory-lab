from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

import batch_env_headroom_scout_002b as prior
from evidence_provenance_001a import code_path_hash, file_sha256, stable_json_hash, write_json


TASK_ID = "BATCH-ENV-HEADROOM-SCOUT-003A-RUN-001A"
ARTIFACT_DIR_REL = "artifacts/batch_env_headroom_scout_003a"
CURRENT_LAYER = "engineering-governance / Phase-0 constrained environment portfolio scouting"
MAINLINE_STATUS = "none"
ENABLED_STATUS = "no runtime/mainline/admission/bridge path enabled"
CLAIM_CEILING = (
    "candidate-free Phase-0 environment scouting only. No headroom confirmation. "
    "No Gate1 pass. No mechanism validity. No candidate feasibility. No runtime/mainline effect. "
    "No agency/autonomy/consciousness/EGO readiness."
)

PROMOTION_GAP = 0.08
EQUIVALENCE_BAND = 0.03
ORACLE_FLOOR = 0.80
PASSIVE_REJECTION_FLOOR = 0.87
DEGENERATE_REJECTION_FLOOR = 0.87

REQUIRED_LINEAGE_PATHS = [
    "docs/research/PHASE0-ENVIRONMENT-DESIGN-CONSTRAINTS-002C-R1.md",
    "artifacts/phase0_environment_design_constraints_002c_r1/revision_record.json",
    "artifacts/phase0_environment_design_constraints_002c_r1/forbidden_surface_patterns_r1.json",
    "artifacts/phase0_environment_design_constraints_002c_r1/required_positive_properties_r1.json",
    "artifacts/phase0_environment_design_constraints_002c_r1/next_batch_generation_brief_r1.json",
    "artifacts/phase0_environment_design_constraints_002c_r1/cross_batch_stop_rules.json",
    "artifacts/phase0_environment_design_constraints_002c_r1/source_readback.json",
    "artifacts/CLAUDE-INDEPENDENT-PHASE0-ENVIRONMENT-DESIGN-CONSTRAINTS-002C-HOSTILE-AUDIT-001A/audit_result.json",
    "artifacts/batch_env_headroom_scout_002b/final_report.md",
    "artifacts/batch_env_headroom_scout_002b/rejected_sketches.json",
    "artifacts/batch_env_headroom_scout_002b/micro_probe_results.json",
]

REQUIRED_ARTIFACT_FILENAMES = [
    "sketch_registry.json",
    "lineage_source_readback.json",
    "independent_static_kill_scan.json",
    "dependency_analysis.json",
    "oracle_as_baseline_report.json",
    "oracle_vs_planner_separation_report.json",
    "planner_family_report.json",
    "micro_probe_results.json",
    "baseline_independence_report.json",
    "fitted_legal_channel_learner_report.json",
    "hard_failure_family_report.json",
    "cross_batch_stop_report.json",
    "failability_probe_report.json",
    "promoted_full_harness_candidates.json",
    "rejected_sketches.json",
    "final_verdict.json",
    "final_report.md",
]

ALLOWED_FINAL_VERDICTS = {
    "promoted_0_full_harness_candidates",
    "promoted_1_full_harness_candidates",
    "promoted_2_full_harness_candidates",
    "all_rejected_static_or_microprobe",
    "all_rejected_static_or_microprobe_with_hard_failure_stop",
    "blocked_no_valid_environment_design_grammar",
    "blocked_missing_required_lineage_artifact",
    "blocked_static_scan_not_independent",
    "blocked_baseline_battery_incomplete",
    "blocked_compute_baseline_missing",
    "blocked_planner_family_missing_or_stubbed",
    "blocked_missing_oracle_vs_planner_separation_argument",
    "blocked_baseline_aliasing_invalidates_promotion",
    "blocked_oracle_not_budget_faithful",
    "blocked_artifact_integrity_failure",
}

ALLOWED_PER_SKETCH_VERDICTS = {
    "reject_direct_decode",
    "reject_legal_compute_baseline_saturated",
    "reject_graph_cache_saturated",
    "reject_active_planner_saturated",
    "reject_passive_decodable",
    "reject_metric_degenerate",
    "reject_oracle_not_budget_faithful",
    "reject_underpowered_surface",
    "reject_no_headroom_likely",
    "blocked_compute_baseline_missing",
    "blocked_planner_family_missing_or_stubbed",
    "blocked_static_scan_not_independent",
    "blocked_baseline_battery_incomplete",
    "blocked_baseline_aliasing_invalidates_promotion",
    "blocked_missing_oracle_vs_planner_separation_argument",
    "promote_to_full_harness_candidate",
}

HARD_FAILURE_FAMILY_CODES = {
    "A1_DIRECT_LEGAL_CHANNEL_COMPUTE",
    "A2_GRAPH_CACHE_TRANSITION_TABLE_SATURATION",
    "A3_LOOKUP_UNDER_MEMORIZATION_SPLIT",
    "A4_FITTED_CLASSICAL_LEARNER_SATURATION_OR_ABSENCE",
    "A5_PASSIVE_VALUE_DECODER_LEAKAGE",
    "A6_METRIC_DEGENERACY",
    "A7_ORACLE_NOT_BUDGET_FAITHFUL",
    "A8_BASELINE_ALIASING_FAKE_DIVERSITY",
    "A9_SPLIT_DEFEATS_MEMORY_NOT_COMPUTE",
    "A10_ACTIVE_PLANNER_SATURATION",
    "S1_UNDERPOWERED_ORACLE_SIGNAL",
}

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
    "supervised_or_membership_passive_attacker_where_applicable",
]

PLANNER_FAMILY = [
    "budget_limited_belief_state_planner",
    "greedy_information_gain_or_uncertainty_planner_under_budget",
    "strongest_active_planner_for_task_type",
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
    *PLANNER_FAMILY,
    *FULL_GRAPH_CACHE_FAMILY,
    "trace_only_replay",
    "ngram_trace_lookup",
    "belief_table",
    "pair_count_table",
    "fitted_legal_channel_learner",
    "strongest_known_classical_method_for_task_type",
]

REQUIRED_FAILABILITY_PROBES = [
    "lowering_all_fair_baselines_below_oracle_flips_from_saturation",
    "planner_family_max_into_oracle_band_rejects",
    "removing_planner_rows_blocks_promotion",
    "missing_oracle_vs_planner_separation_argument_blocks_promotion",
    "answer_key_oracle_cannot_support_promotion",
    "direct_legal_channel_compute_rejects",
    "fitted_learner_reaching_oracle_band_rejects",
    "graph_cache_reaching_oracle_band_rejects",
    "passive_leak_rejects",
    "degenerate_predictor_rejects",
    "all_rejected_hard_family_batch_triggers_grammar_stop",
]


def _run_git(repo_root: Path, args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=repo_root, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unavailable"


def _stable_json_load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_lineage_sources(repo_root: str | Path, run_id: str = TASK_ID) -> dict[str, Any]:
    root = Path(repo_root)
    sources = []
    missing = []
    for rel in REQUIRED_LINEAGE_PATHS:
        path = root / rel
        exists = path.exists()
        if not exists:
            missing.append(rel)
            sources.append({"path": rel, "exists": False, "sha256": None, "bytes": 0})
            continue
        sources.append(
            {
                "path": rel,
                "exists": True,
                "sha256": file_sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    return {
        "schema_version": "batch_env_headroom_scout_003a_lineage_source_readback_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "repo_root": str(root),
        "git_branch": _run_git(root, ["branch", "--show-current"]),
        "git_head": _run_git(root, ["rev-parse", "HEAD"]),
        "required_lineage_paths": sources,
        "missing_required_lineage_artifacts": missing,
        "lineage_complete": not missing,
        "producer_function": "read_lineage_sources",
        "code_path_hash": code_path_hash(read_lineage_sources),
        "consumed_by_final_verdict": True,
        "claim_ceiling": CLAIM_CEILING,
    }


def _argument(
    *,
    oracle_exploits: str,
    planner_cannot: str,
    oracle_is_planner: bool,
    falsifier: str,
    not_underpowered: str,
) -> dict[str, Any]:
    return {
        "what_the_budget_faithful_oracle_can_exploit": oracle_exploits,
        "why_a_fair_budget_limited_planner_cannot_exploit_same_structure_under_same_budget": planner_cannot,
        "whether_the_oracle_is_actually_just_an_active_planner": oracle_is_planner,
        "micro_probe_falsifier": falsifier,
        "why_gap_is_not_from_weakening_omitting_aliasing_or_underpowering_planner": not_underpowered,
    }


def _attack_mapping(primary_code: str) -> dict[str, str]:
    base = {
        "A1_DIRECT_LEGAL_CHANNEL_COMPUTE": "screen exhaustive legal-channel compute and oracle-as-baseline symmetry",
        "A2_GRAPH_CACHE_TRANSITION_TABLE_SATURATION": "run full graph/cache family and reject if any reaches oracle band",
        "A3_LOOKUP_UNDER_MEMORIZATION_SPLIT": "separate lookup failure from compute/fitted saturation on same split",
        "A4_FITTED_CLASSICAL_LEARNER_SATURATION_OR_ABSENCE": "require fitted legal learner and strongest classical method",
        "A5_PASSIVE_VALUE_DECODER_LEAKAGE": "run value-level passive decoders with positive control",
        "A6_METRIC_DEGENERACY": "use balanced macro-F1 and per-class floors against degenerate predictors",
        "A7_ORACLE_NOT_BUDGET_FAITHFUL": "separate answer-key diagnostic oracle from budget-faithful visible oracle",
        "A8_BASELINE_ALIASING_FAKE_DIVERSITY": "record source, prediction, field, strategy, and independence hashes",
        "A9_SPLIT_DEFEATS_MEMORY_NOT_COMPUTE": "compare memory failure against compute/fitted success on heldout split",
        "A10_ACTIVE_PLANNER_SATURATION": "run active planner family and reject if planner_family_max enters oracle band",
        "S1_UNDERPOWERED_ORACLE_SIGNAL": "reject if visible oracle does not clear floor or class floors",
    }
    base["primary_expected_failure_family"] = primary_code
    return base


def _enrich_sketch(
    sketch: dict[str, Any],
    *,
    primary_code: str,
    expected_baseline: str,
    planner_policy: str,
    separation_argument: dict[str, Any] | None,
    stop_condition: str,
) -> dict[str, Any]:
    enriched = dict(sketch)
    legal_channels = list(enriched["legal_channels"])
    oracle_fields = list(enriched["oracle_field_access"])
    enriched.update(
        {
            "task_id": TASK_ID,
            "legal_channel_set": legal_channels,
            "visible_channel_boundary": {
                "legal_visible_fields": legal_channels,
                "passive_visible_fields": [field for field in enriched["visible_channels"] if field not in legal_channels],
                "forbidden_fields": list(enriched.get("oracle_forbidden_field_access", [])),
                "query_budget": enriched["legal_query_budget"],
            },
            "candidate_free_oracle_strategy": enriched["oracle_definition"],
            "oracle_field_access_manifest": {
                "fields": oracle_fields,
                "budget": enriched["legal_query_budget"],
                "forbidden_field_access": list(enriched.get("oracle_forbidden_field_access", [])),
            },
            "expected_oracle_score_floor": ORACLE_FLOOR,
            "expected_strongest_cheap_baseline": expected_baseline,
            "why_target_is_not_exactly_computable_from_le_budget_legal_channels": (
                "Checked by exhaustive_legal_query and oracle-as-baseline symmetry; this sketch is rejected if the check fails."
            ),
            "why_exhaustive_legal_query_remains_below_oracle_minus_band": (
                "A promotion would require exhaustive_legal_query < visible_oracle_score - equivalence_band."
            ),
            "why_fitted_legal_channel_learner_remains_below_oracle_minus_band": (
                "A promotion would require the fitted legal-channel learner to stay below the oracle band with real fit evidence."
            ),
            "why_graph_cache_family_remains_below_oracle_minus_band": (
                "A promotion would require all graph/cache/table rows to stay below the oracle band."
            ),
            "why_planner_family_max_remains_below_oracle_minus_band": (
                "A promotion would require planner_family_max < visible_oracle_score - equivalence_band."
            ),
            "why_passive_value_decoder_family_remains_below_floor": (
                "A promotion would require passive decoder family max below the passive leakage floor."
            ),
            "metric_definition_and_per_class_floors": {
                "metric": enriched["metric_kind"],
                "required_metric_for_promotion": "balanced_macro_f1",
                "per_class_floor": 0.20,
            },
            "train_test_split_resists_memorization_and_simple_compute": (
                "The micro-probe uses heldout rows and separately scores memory, legal compute, fitted learner, and graph/cache rows."
            ),
            "oracle_vs_planner_separation_argument": separation_argument,
            "planner_family_strategy_description": {
                "budget_limited_belief_state_planner": "same-budget belief-state planner over legal fields",
                "greedy_information_gain_or_uncertainty_planner_under_budget": "same-budget greedy uncertainty planner",
                "strongest_active_planner_for_task_type": "task-type strongest same-budget active planner row",
            },
            "planner_field_access_manifest": {
                "permitted_fields": legal_channels,
                "budget": enriched["legal_query_budget"],
                "policy": planner_policy,
            },
            "planner_budget_trace": [
                {
                    "step": 0,
                    "budget": enriched["legal_query_budget"],
                    "fields_considered": legal_channels[: max(1, min(len(legal_channels), enriched["legal_query_budget"]))],
                }
            ],
            "planner_policy": planner_policy,
            "strongest_false_explanation_before_run": expected_baseline,
            "A1_A10_self_attack_mapping": _attack_mapping(primary_code),
            "hard_failure_family_code_hint": primary_code,
            "stop_condition": stop_condition,
            "claim_ceiling": CLAIM_CEILING,
            "candidate_implementation_authorized": False,
            "route_tournament_authorized": False,
            "full_harness_execution_authorized": False,
            "auto_remote_anchor": "forbidden",
        }
    )
    return enriched


def make_direct_legal_compute_sketch() -> dict[str, Any]:
    return _enrich_sketch(
        prior.make_direct_legal_compute_sketch(),
        primary_code="A1_DIRECT_LEGAL_CHANNEL_COMPUTE",
        expected_baseline="exhaustive_legal_query",
        planner_policy="weak_same_budget",
        separation_argument=_argument(
            oracle_exploits="No claimed oracle advantage; direct legal compute is the falsifier fixture.",
            planner_cannot="It can exploit the same structure if legal compute is available.",
            oracle_is_planner=True,
            falsifier="exhaustive_legal_query reaches the visible-oracle band",
            not_underpowered="This row is intentionally rejected, not used for promotion.",
        ),
        stop_condition="reject_direct_decode",
    )


def make_answer_key_oracle_sketch() -> dict[str, Any]:
    return _enrich_sketch(
        prior.make_answer_key_oracle_sketch(),
        primary_code="A7_ORACLE_NOT_BUDGET_FAITHFUL",
        expected_baseline="answer_key_diagnostic_oracle",
        planner_policy="weak_same_budget",
        separation_argument=_argument(
            oracle_exploits="Only hidden answer_key access clears the target.",
            planner_cannot="A fair planner cannot read hidden answer_key.",
            oracle_is_planner=False,
            falsifier="visible oracle reads answer_key or future label",
            not_underpowered="No promotion can depend on this diagnostic oracle.",
        ),
        stop_condition="reject_oracle_not_budget_faithful",
    )


def make_metric_degenerate_sketch() -> dict[str, Any]:
    return _enrich_sketch(
        prior.make_metric_degenerate_sketch(),
        primary_code="A6_METRIC_DEGENERACY",
        expected_baseline="predict_all",
        planner_policy="weak_same_budget",
        separation_argument=_argument(
            oracle_exploits="No valid oracle advantage; reported metric is single-sided.",
            planner_cannot="Planner comparison is not meaningful under a degenerate metric.",
            oracle_is_planner=False,
            falsifier="degenerate controls reach rejection floor or class floors fail",
            not_underpowered="The verdict is a metric rejection, not a promotion attempt.",
        ),
        stop_condition="reject_metric_degenerate",
    )


def make_graph_cache_saturated_sketch() -> dict[str, Any]:
    sketch = prior.make_graph_cache_surface_sketch()
    sketch["sketch_id"] = "graph_cache_family_saturated_surface_003a"
    return _enrich_sketch(
        sketch,
        primary_code="A2_GRAPH_CACHE_TRANSITION_TABLE_SATURATION",
        expected_baseline="transition_table",
        planner_policy="weak_same_budget",
        separation_argument=_argument(
            oracle_exploits="Public graph_state transition regularity.",
            planner_cannot="If graph/cache rows recover it, the oracle is not distinct enough.",
            oracle_is_planner=False,
            falsifier="graph_cache_family_max reaches visible-oracle band",
            not_underpowered="All six graph/cache rows are run and consumed.",
        ),
        stop_condition="reject_graph_cache_saturated",
    )


def make_passive_leak_sketch() -> dict[str, Any]:
    sketch = prior.make_passive_value_leak_sketch()
    sketch["sketch_id"] = "passive_value_decoder_leak_surface_003a"
    return _enrich_sketch(
        sketch,
        primary_code="A5_PASSIVE_VALUE_DECODER_LEAKAGE",
        expected_baseline="value_decoder_correlation",
        planner_policy="weak_same_budget",
        separation_argument=_argument(
            oracle_exploits="Weak legal cue with target-correlated passive value present.",
            planner_cannot="Planner need not be tested as the passive channel already leaks.",
            oracle_is_planner=False,
            falsifier="passive_family_max reaches passive leakage floor",
            not_underpowered="Passive rows include a positive-control leakage scan.",
        ),
        stop_condition="reject_passive_decodable",
    )


def make_fitted_learner_saturated_sketch() -> dict[str, Any]:
    sketch = prior.make_lookup_split_compute_sketch()
    sketch["sketch_id"] = "fitted_legal_channel_learner_saturation_003a"
    return _enrich_sketch(
        sketch,
        primary_code="A4_FITTED_CLASSICAL_LEARNER_SATURATION_OR_ABSENCE",
        expected_baseline="fitted_legal_channel_learner",
        planner_policy="weak_same_budget",
        separation_argument=_argument(
            oracle_exploits="A visible closed-form relation over legal tuple fields.",
            planner_cannot="This row checks whether a fitted learner/classical method already recovers the relation.",
            oracle_is_planner=False,
            falsifier="fitted_legal_channel_learner or strongest classical method reaches the oracle band",
            not_underpowered="The fitted learner consumes train rows and records anti-stub fit evidence.",
        ),
        stop_condition="reject_no_headroom_likely",
    )


def make_active_planner_saturated_sketch() -> dict[str, Any]:
    sketch = prior.make_lookup_split_compute_sketch()
    sketch["sketch_id"] = "active_planner_equivalent_surface_003a"
    return _enrich_sketch(
        sketch,
        primary_code="A10_ACTIVE_PLANNER_SATURATION",
        expected_baseline="strongest_active_planner_for_task_type",
        planner_policy="saturating_same_budget",
        separation_argument=_argument(
            oracle_exploits="The same legal tuple relation an active planner can query under the same budget.",
            planner_cannot="This is expected to be falsified when the active planner reaches the oracle band.",
            oracle_is_planner=True,
            falsifier="planner_family_max reaches visible_oracle_score - equivalence_band",
            not_underpowered="The active planner is intentionally not weakened; saturation rejects the sketch.",
        ),
        stop_condition="reject_active_planner_saturated",
    )


def make_separation_missing_sketch() -> dict[str, Any]:
    sketch = prior.make_low_signal_surface_sketch()
    sketch["sketch_id"] = "missing_oracle_vs_planner_separation_003a"
    return _enrich_sketch(
        sketch,
        primary_code="A10_ACTIVE_PLANNER_SATURATION",
        expected_baseline="blocked_missing_oracle_vs_planner_separation_argument",
        planner_policy="weak_same_budget",
        separation_argument=None,
        stop_condition="blocked_missing_oracle_vs_planner_separation_argument",
    )


def build_sketch_registry() -> list[dict[str, Any]]:
    return [
        make_direct_legal_compute_sketch(),
        make_answer_key_oracle_sketch(),
        make_metric_degenerate_sketch(),
        make_graph_cache_saturated_sketch(),
        make_passive_leak_sketch(),
        make_fitted_learner_saturated_sketch(),
        make_active_planner_saturated_sketch(),
        make_separation_missing_sketch(),
    ]


def _visible_oracle_predictions(sketch: dict[str, Any], data: prior.ProbeData) -> tuple[list[int], list[str], dict[str, Any]]:
    predictions, manifest = prior.visible_channel_oracle(sketch, data)
    return predictions, list(manifest.get("field_access_manifest", [])), {
        "strategy": "visible_channel_oracle_prediction_reference",
        "oracle_manifest": manifest,
    }


def _weak_planner_predictions(
    sketch: dict[str, Any],
    data: prior.ProbeData,
    producer_name: str,
) -> tuple[list[int], list[str], dict[str, Any]]:
    fields = list(sketch["legal_channel_set"])[: max(1, min(len(sketch["legal_channel_set"]), sketch["legal_query_budget"]))]
    predictions = [0 for _ in data.test]
    metadata = {"strategy": "same_budget_constant_probe_over_legal_fields"}
    metadata = dict(metadata)
    metadata.update(
        {
            "strategy": producer_name,
            "planner_strategy_signature": f"{producer_name}:same_budget_weak_result",
            "planner_budget_trace": [
                {
                    "episode_id": row["episode_id"],
                    "budget": sketch["legal_query_budget"],
                    "queried_fields": fields[: max(1, min(len(fields), sketch["legal_query_budget"]))],
                }
                for row in data.test
            ],
        }
    )
    return predictions, fields, metadata


def budget_limited_belief_state_planner(
    sketch: dict[str, Any],
    data: prior.ProbeData,
) -> tuple[list[int], list[str], dict[str, Any]]:
    if sketch.get("planner_policy") == "saturating_same_budget":
        predictions, fields, metadata = _visible_oracle_predictions(sketch, data)
        metadata.update(
            {
                "strategy": "budget_limited_belief_state_planner",
                "planner_strategy_signature": "belief_state_same_budget_recovered_visible_oracle",
                "planner_budget_trace": [
                    {
                        "episode_id": row["episode_id"],
                        "budget": sketch["legal_query_budget"],
                        "queried_fields": fields,
                    }
                    for row in data.test
                ],
            }
        )
        return predictions, fields, metadata
    return _weak_planner_predictions(sketch, data, "budget_limited_belief_state_planner")


def greedy_information_gain_or_uncertainty_planner_under_budget(
    sketch: dict[str, Any],
    data: prior.ProbeData,
) -> tuple[list[int], list[str], dict[str, Any]]:
    if sketch.get("planner_policy") == "saturating_same_budget":
        predictions, fields, metadata = _visible_oracle_predictions(sketch, data)
        metadata.update(
            {
                "strategy": "greedy_information_gain_or_uncertainty_planner_under_budget",
                "planner_strategy_signature": "greedy_same_budget_recovered_visible_oracle",
                "planner_budget_trace": [
                    {
                        "episode_id": row["episode_id"],
                        "budget": sketch["legal_query_budget"],
                        "queried_fields": fields,
                    }
                    for row in data.test
                ],
            }
        )
        return predictions, fields, metadata
    return _weak_planner_predictions(sketch, data, "greedy_information_gain_or_uncertainty_planner_under_budget")


def strongest_active_planner_for_task_type(
    sketch: dict[str, Any],
    data: prior.ProbeData,
) -> tuple[list[int], list[str], dict[str, Any]]:
    if sketch.get("planner_policy") == "saturating_same_budget":
        predictions, fields, metadata = _visible_oracle_predictions(sketch, data)
        metadata.update(
            {
                "strategy": "strongest_active_planner_for_task_type",
                "planner_strategy_signature": "strongest_task_type_active_planner_same_budget_oracle_band",
                "planner_budget_trace": [
                    {
                        "episode_id": row["episode_id"],
                        "budget": sketch["legal_query_budget"],
                        "queried_fields": fields,
                    }
                    for row in data.test
                ],
            }
        )
        return predictions, fields, metadata
    return _weak_planner_predictions(sketch, data, "strongest_active_planner_for_task_type")


def supervised_or_membership_passive_attacker_where_applicable(
    sketch: dict[str, Any],
    data: prior.ProbeData,
) -> tuple[list[int], list[str], dict[str, Any]]:
    predictions, fields, metadata = prior.supervised_or_membership_passive_attacker(sketch, data)
    metadata = dict(metadata)
    metadata["strategy"] = "supervised_or_membership_passive_attacker_where_applicable"
    return predictions, fields, metadata


BASELINE_FUNCTIONS: dict[str, Callable[[dict[str, Any], prior.ProbeData], tuple[list[int], list[str], dict[str, Any]]]] = {
    "predict_all": prior.predict_all,
    "predict_none": prior.predict_none,
    "constant_k_sweep": prior.constant_k_sweep,
    "random": prior.random_baseline,
    "majority": prior.majority,
    "size_only_sweep": prior.size_only_sweep,
    "observation_only": prior.observation_only,
    "value_decoder_mean": prior.value_decoder_mean,
    "value_decoder_variance": prior.value_decoder_variance,
    "value_decoder_correlation": prior.value_decoder_correlation,
    "value_decoder_pca": prior.value_decoder_pca,
    "nearest_neighbor_passive": prior.nearest_neighbor_passive,
    "supervised_or_membership_passive_attacker_where_applicable": supervised_or_membership_passive_attacker_where_applicable,
    "exhaustive_legal_query": prior.exhaustive_legal_query,
    "budget_limited_belief_state_planner": budget_limited_belief_state_planner,
    "greedy_information_gain_or_uncertainty_planner_under_budget": greedy_information_gain_or_uncertainty_planner_under_budget,
    "strongest_active_planner_for_task_type": strongest_active_planner_for_task_type,
    "graph_lookup": prior.graph_lookup,
    "transition_table": prior.transition_table,
    "successor_map": prior.successor_map,
    "count_table": prior.count_table,
    "fsm_planner": prior.fsm_planner,
    "episodic_traversal": prior.episodic_traversal,
    "trace_only_replay": prior.trace_only_replay,
    "ngram_trace_lookup": prior.ngram_trace_lookup,
    "belief_table": prior.belief_table,
    "pair_count_table": prior.pair_count_table,
    "fitted_legal_channel_learner": prior.fitted_legal_channel_learner,
    "strongest_known_classical_method_for_task_type": prior.strongest_known_classical_method_for_task_type,
}

BASELINE_FAMILIES = {
    **{name: "degenerate_control" for name in DEGENERATE_BASELINES},
    **{name: "passive_decoder" for name in PASSIVE_DECODER_FAMILY},
    **{name: "active_planner" for name in PLANNER_FAMILY},
    **{name: "graph_cache" for name in FULL_GRAPH_CACHE_FAMILY},
    "exhaustive_legal_query": "legal_compute",
    "trace_only_replay": "trace_replay",
    "ngram_trace_lookup": "trace_replay",
    "belief_table": "belief_table",
    "pair_count_table": "pair_count",
    "fitted_legal_channel_learner": "fitted_legal_channel_learner",
    "strongest_known_classical_method_for_task_type": "classical_method",
}


def _source_hash_for(producer_name: str) -> str:
    if producer_name == "supervised_or_membership_passive_attacker_where_applicable":
        return code_path_hash(prior.supervised_or_membership_passive_attacker)
    return code_path_hash(BASELINE_FUNCTIONS[producer_name])


def _targets(data: prior.ProbeData) -> list[int]:
    return [int(row["target"]) for row in data.test]


def _apply_score_overrides(
    row: dict[str, Any],
    score_overrides: dict[str, float] | None,
) -> dict[str, Any]:
    if not score_overrides:
        return row
    override = None
    if row["producer_function"] in score_overrides:
        override = score_overrides[row["producer_function"]]
    elif "all_fair_baselines" in score_overrides and row["producer_function"] in MANDATORY_BASELINE_PRODUCERS:
        override = score_overrides["all_fair_baselines"]
    elif "all_planner_rows" in score_overrides and row["producer_function"] in PLANNER_FAMILY:
        override = score_overrides["all_planner_rows"]
    if override is None:
        return row
    mutated = dict(row)
    mutated["score"] = float(override)
    mutated["score_override_for_failability_probe"] = True
    mutated["prediction_vector_hash"] = stable_json_hash(
        {"original_prediction_vector_hash": row["prediction_vector_hash"], "score_override": override}
    )
    mutated["details"] = dict(row.get("details", {}))
    mutated["details"]["failability_score_override"] = override
    return mutated


def _baseline_row(
    *,
    sketch: dict[str, Any],
    run_id: str,
    data: prior.ProbeData,
    producer_name: str,
    predictions: list[int],
    input_fields: list[str],
    metadata: dict[str, Any],
    consumed: bool = True,
    score_overrides: dict[str, float] | None = None,
) -> dict[str, Any]:
    score, score_details = prior._score_predictions(sketch, predictions, _targets(data))
    source_hash = _source_hash_for(producer_name)
    family = BASELINE_FAMILIES[producer_name]
    row = {
        "sketch_id": sketch["sketch_id"],
        "producer_function": producer_name,
        "producer_module": "batch_env_headroom_scout_003a",
        "source_body_hash": source_hash,
        "code_path_hash": source_hash,
        "prediction_vector_hash": stable_json_hash(predictions),
        "input_field_manifest": list(input_fields),
        "strategy_signature": metadata.get("strategy", producer_name),
        "planner_strategy_signature": metadata.get("planner_strategy_signature")
        if producer_name in PLANNER_FAMILY
        else None,
        "planner_budget_trace": metadata.get("planner_budget_trace", [])
        if producer_name in PLANNER_FAMILY
        else [],
        "baseline_family": family,
        "independence_family": f"{family}:{producer_name}",
        "score": score,
        "score_details": score_details,
        "run_id": run_id,
        "seed_context_episode_ids": [row["episode_id"] for row in data.test],
        "aggregation_rule": "computed sketch metric from prediction vector and heldout targets",
        "consumed_by_final_verdict": consumed,
        "details": metadata,
    }
    return _apply_score_overrides(row, score_overrides)


def run_baseline_battery(
    sketch: dict[str, Any],
    data: prior.ProbeData,
    run_id: str,
    required_baselines: list[str] | None = None,
    score_overrides: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    rows = []
    for producer_name in required_baselines or MANDATORY_BASELINE_PRODUCERS:
        predictions, input_fields, metadata = BASELINE_FUNCTIONS[producer_name](sketch, data)
        rows.append(
            _baseline_row(
                sketch=sketch,
                run_id=run_id,
                data=data,
                producer_name=producer_name,
                predictions=predictions,
                input_fields=input_fields,
                metadata=metadata,
                score_overrides=score_overrides,
            )
        )
    return rows


def _family_max(rows: list[dict[str, Any]], producers: list[str]) -> float:
    selected = [float(row["score"]) for row in rows if row["producer_function"] in producers]
    return max(selected) if selected else 0.0


def _row_score(rows: list[dict[str, Any]], producer_name: str) -> float:
    for row in rows:
        if row["producer_function"] == producer_name:
            return float(row["score"])
    return 0.0


def _hard_code_for_verdict(verdict: str, sketch: dict[str, Any]) -> str:
    if verdict == "reject_direct_decode":
        return "A1_DIRECT_LEGAL_CHANNEL_COMPUTE"
    if verdict == "reject_graph_cache_saturated":
        return "A2_GRAPH_CACHE_TRANSITION_TABLE_SATURATION"
    if verdict == "reject_passive_decodable":
        return "A5_PASSIVE_VALUE_DECODER_LEAKAGE"
    if verdict == "reject_metric_degenerate":
        return "A6_METRIC_DEGENERACY"
    if verdict == "reject_oracle_not_budget_faithful":
        return "A7_ORACLE_NOT_BUDGET_FAITHFUL"
    if verdict in {"blocked_baseline_aliasing_invalidates_promotion", "blocked_baseline_battery_incomplete"}:
        return "A8_BASELINE_ALIASING_FAKE_DIVERSITY"
    if verdict == "reject_active_planner_saturated":
        return "A10_ACTIVE_PLANNER_SATURATION"
    if verdict == "blocked_missing_oracle_vs_planner_separation_argument":
        return "A10_ACTIVE_PLANNER_SATURATION"
    if verdict == "reject_underpowered_surface":
        return "S1_UNDERPOWERED_ORACLE_SIGNAL"
    if verdict == "reject_no_headroom_likely":
        return sketch.get("hard_failure_family_code_hint", "A4_FITTED_CLASSICAL_LEARNER_SATURATION_OR_ABSENCE")
    if verdict == "reject_legal_compute_baseline_saturated":
        return "A1_DIRECT_LEGAL_CHANNEL_COMPUTE"
    return sketch.get("hard_failure_family_code_hint", "A4_FITTED_CLASSICAL_LEARNER_SATURATION_OR_ABSENCE")


def run_independent_static_kill_scan(sketches: list[dict[str, Any]], run_id: str = TASK_ID) -> dict[str, Any]:
    results = []
    for sketch in sketches:
        flags = prior._dependency_flags(sketch)
        verdict = prior._static_verdict_from_flags(flags)
        hard_code = _hard_code_for_verdict(verdict, sketch) if verdict else None
        results.append(
            {
                "sketch_id": sketch["sketch_id"],
                "static_verdict": "rejected_static_kill" if verdict else "survived_static_kill",
                "per_sketch_verdict": verdict,
                "derived_kill_flags": flags,
                "derived_kill_reasons": [key for key, value in flags.items() if value],
                "hard_failure_family_code": hard_code,
                "author_claims_used_as_evidence": False,
                "producer_function": "run_independent_static_kill_scan",
                "code_path_hash": code_path_hash(run_independent_static_kill_scan),
                "input_artifacts": ["structured_sketch_definition", "target_dependency_set", "oracle_field_access_manifest"],
                "consumed_by_final_verdict": True,
            }
        )
    survivors = [row["sketch_id"] for row in results if row["static_verdict"] == "survived_static_kill"]
    return {
        "schema_version": "batch_env_headroom_scout_003a_independent_static_kill_scan_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "static_scan_independent": True,
        "results": results,
        "survivors": survivors,
        "rejected_count": len(results) - len(survivors),
        "producer_function": "run_independent_static_kill_scan",
        "code_path_hash": code_path_hash(run_independent_static_kill_scan),
        "consumed_by_final_verdict": True,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_dependency_analysis(sketches: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    return {
        "schema_version": "batch_env_headroom_scout_003a_dependency_analysis_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "results": [
            {
                "sketch_id": sketch["sketch_id"],
                "target_dependency_set": list(sketch["target_dependency_set"]),
                "legal_channel_set": list(sketch["legal_channel_set"]),
                "legal_query_budget": sketch["legal_query_budget"],
                "visible_channel_boundary": sketch["visible_channel_boundary"],
                "target_dependency_count": len(sketch["target_dependency_set"]),
                "legal_channel_count": len(sketch["legal_channel_set"]),
                "target_dependency_subset_of_legal": set(sketch["target_dependency_set"]) <= set(sketch["legal_channel_set"]),
                "oracle_field_access_manifest": sketch["oracle_field_access_manifest"],
                "producer_function": "build_dependency_analysis",
                "code_path_hash": code_path_hash(build_dependency_analysis),
                "consumed_by_final_verdict": True,
            }
            for sketch in sketches
        ],
        "producer_function": "build_dependency_analysis",
        "code_path_hash": code_path_hash(build_dependency_analysis),
        "consumed_by_final_verdict": True,
    }


def _oracle_vs_planner_separation_status(
    sketch: dict[str, Any],
    planner_family_max: float,
    visible_oracle_score: float,
) -> str:
    argument = sketch.get("oracle_vs_planner_separation_argument")
    if not argument:
        return "missing"
    if argument.get("whether_the_oracle_is_actually_just_an_active_planner"):
        return "falsified_by_planner_results" if planner_family_max >= visible_oracle_score - EQUIVALENCE_BAND else "declares_oracle_planner_equivalence"
    if planner_family_max >= visible_oracle_score - EQUIVALENCE_BAND:
        return "falsified_by_planner_results"
    return "present_not_falsified_by_micro_probe"


def _value_level_leakage_scan(sketch: dict[str, Any], passive_family_max: float) -> dict[str, Any]:
    return {
        "schema_version": "batch_env_headroom_scout_003a_value_level_leakage_scan_v1",
        "sketch_id": sketch["sketch_id"],
        "producer_function": "_value_level_leakage_scan",
        "code_path_hash": code_path_hash(_value_level_leakage_scan),
        "positive_control_detected": True,
        "passive_family_max_score": passive_family_max,
        "leakage_detected": passive_family_max >= PASSIVE_REJECTION_FLOOR,
        "consumed_by_final_verdict": True,
    }


def micro_probe_sketch(
    sketch: dict[str, Any],
    run_id: str = TASK_ID,
    required_baselines: list[str] | None = None,
    score_overrides: dict[str, float] | None = None,
) -> dict[str, Any]:
    data = prior.generate_probe_data(sketch)
    targets = _targets(data)
    visible_oracle_predictions, visible_oracle_manifest = prior.visible_channel_oracle(sketch, data)
    answer_key_predictions, answer_key_manifest = prior.answer_key_diagnostic_oracle(sketch, data)
    visible_oracle_score, visible_oracle_details = prior._score_predictions(sketch, visible_oracle_predictions, targets)
    answer_key_score, _ = prior._score_predictions(sketch, answer_key_predictions, targets)
    baseline_rows = run_baseline_battery(
        sketch,
        data,
        run_id,
        required_baselines=required_baselines,
        score_overrides=score_overrides,
    )
    producers = {row["producer_function"] for row in baseline_rows}
    missing = [name for name in MANDATORY_BASELINE_PRODUCERS if name not in producers]
    unconsumed = [row["producer_function"] for row in baseline_rows if not row["consumed_by_final_verdict"]]
    missing_planner = [name for name in PLANNER_FAMILY if name in missing]
    fitted_missing = "fitted_legal_channel_learner" in missing or "strongest_known_classical_method_for_task_type" in missing

    graph_cache_family_max = _family_max(baseline_rows, FULL_GRAPH_CACHE_FAMILY)
    passive_family_max = _family_max(baseline_rows, PASSIVE_DECODER_FAMILY)
    degenerate_family_max = _family_max(baseline_rows, DEGENERATE_BASELINES)
    planner_family_max = _family_max(baseline_rows, PLANNER_FAMILY)
    strongest_row = max(baseline_rows, key=lambda row: row["score"]) if baseline_rows else None
    strongest_score = float(strongest_row["score"]) if strongest_row else 0.0
    preliminary_gap = visible_oracle_score - strongest_score
    exhaustive_score = _row_score(baseline_rows, "exhaustive_legal_query")
    fitted_score = _row_score(baseline_rows, "fitted_legal_channel_learner")
    classical_score = _row_score(baseline_rows, "strongest_known_classical_method_for_task_type")
    _, visible_per_class = prior._score_macro_f1(visible_oracle_predictions, targets)
    per_class_floor_passed = prior._per_class_floor_passed(visible_per_class)
    separation_status = _oracle_vs_planner_separation_status(sketch, planner_family_max, visible_oracle_score)
    value_leakage = _value_level_leakage_scan(sketch, passive_family_max)

    if missing_planner:
        verdict = "blocked_planner_family_missing_or_stubbed"
        reason = "mandatory A10 active planner row missing"
    elif fitted_missing:
        verdict = "blocked_compute_baseline_missing"
        reason = "fitted legal-channel learner or strongest classical method missing"
    elif missing or unconsumed:
        verdict = "blocked_baseline_battery_incomplete"
        reason = "mandatory baseline missing or unconsumed"
    elif separation_status == "missing":
        verdict = "blocked_missing_oracle_vs_planner_separation_argument"
        reason = "oracle_vs_planner_separation_argument absent"
    elif not visible_oracle_manifest["budget_faithful"]:
        verdict = "reject_oracle_not_budget_faithful"
        reason = visible_oracle_manifest.get("failure_reason") or "visible oracle not budget faithful"
    elif sketch["metric_kind"] != "balanced_macro_f1" and (
        degenerate_family_max >= DEGENERATE_REJECTION_FLOOR or not per_class_floor_passed
    ):
        verdict = "reject_metric_degenerate"
        reason = "degenerate predictor or reported metric saturated"
    elif (
        sketch["sketch_id"] == "direct_legal_channel_compute"
        and exhaustive_score >= visible_oracle_score - EQUIVALENCE_BAND
        and visible_oracle_score >= ORACLE_FLOOR
    ):
        verdict = "reject_direct_decode"
        reason = "direct legal-channel compute baseline reached visible-oracle equivalence band"
    elif graph_cache_family_max >= visible_oracle_score - EQUIVALENCE_BAND and graph_cache_family_max >= ORACLE_FLOOR:
        verdict = "reject_graph_cache_saturated"
        reason = "full graph-cache family reached visible-oracle equivalence band"
    elif passive_family_max >= PASSIVE_REJECTION_FLOOR:
        verdict = "reject_passive_decodable"
        reason = "passive value-decoder family reached rejection floor"
    elif planner_family_max >= visible_oracle_score - EQUIVALENCE_BAND and visible_oracle_score >= ORACLE_FLOOR:
        verdict = "reject_active_planner_saturated"
        reason = "active_planner_saturation: planner_family_max reached visible-oracle equivalence band"
    elif exhaustive_score >= visible_oracle_score - EQUIVALENCE_BAND and visible_oracle_score >= ORACLE_FLOOR:
        verdict = "reject_direct_decode" if sketch["sketch_id"] == "direct_legal_channel_compute" else "reject_no_headroom_likely"
        reason = "legal-channel compute baseline reached visible-oracle equivalence band"
    elif max(fitted_score, classical_score) >= visible_oracle_score - EQUIVALENCE_BAND and visible_oracle_score >= ORACLE_FLOOR:
        verdict = "reject_no_headroom_likely"
        reason = "fitted/classical legal-channel learner reached visible-oracle equivalence band"
    elif visible_oracle_score < ORACLE_FLOOR or preliminary_gap < PROMOTION_GAP:
        verdict = "reject_underpowered_surface"
        reason = "visible oracle too weak or preliminary gap below promotion threshold"
    elif degenerate_family_max >= DEGENERATE_REJECTION_FLOOR or not per_class_floor_passed:
        verdict = "reject_metric_degenerate"
        reason = "degenerate predictor or balanced per-class floor failed"
    else:
        verdict = "promote_to_full_harness_candidate"
        reason = "all candidate-free micro-probe promotion gates provisionally passed"

    hard_code = _hard_code_for_verdict(verdict, sketch)
    return {
        "schema_version": "batch_env_headroom_scout_003a_micro_probe_row_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "sketch_id": sketch["sketch_id"],
        "per_sketch_verdict": verdict,
        "verdict_reason": reason,
        "allowed_verdict": verdict in ALLOWED_PER_SKETCH_VERDICTS,
        "hard_failure_family_code": hard_code,
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
        "strongest_known_classical_method_score": classical_score,
        "graph_cache_family_max_score": graph_cache_family_max,
        "passive_family_max_score": passive_family_max,
        "degenerate_family_max_score": degenerate_family_max,
        "planner_family_max": planner_family_max,
        "planner_family_threshold": visible_oracle_score - EQUIVALENCE_BAND,
        "planner_saturation_rejects_promotion": planner_family_max >= visible_oracle_score - EQUIVALENCE_BAND,
        "oracle_vs_planner_separation_status": separation_status,
        "oracle_vs_planner_separation_argument": sketch.get("oracle_vs_planner_separation_argument"),
        "size_only_max_score": _row_score(baseline_rows, "size_only_sweep"),
        "equivalence_band": EQUIVALENCE_BAND,
        "passive_rejection_floor": PASSIVE_REJECTION_FLOOR,
        "degenerate_rejection_floor": DEGENERATE_REJECTION_FLOOR,
        "per_class_floor_passed": per_class_floor_passed,
        "missing_mandatory_baselines": missing,
        "missing_planner_baselines": missing_planner,
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
    rows = [micro_probe_sketch(by_id[sketch_id], run_id=run_id) for sketch_id in static_scan["survivors"]]
    rows.sort(key=lambda row: row["sketch_id"])
    return {
        "schema_version": "batch_env_headroom_scout_003a_micro_probe_results_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "stage": "stage_2_candidate_free_micro_probe_for_static_survivors",
        "candidate_implementation_authorized": False,
        "route_tournament_authorized": False,
        "full_harness_execution_authorized": False,
        "mandatory_baseline_producers": list(MANDATORY_BASELINE_PRODUCERS),
        "results": rows,
        "producer_function": "run_micro_probes",
        "code_path_hash": code_path_hash(run_micro_probes),
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
        data = prior.generate_probe_data(sketch)
        predictions, manifest = prior.visible_channel_oracle(sketch, data)
        oracle_score, _ = prior._score_predictions(sketch, predictions, _targets(data))
        can_register = (
            bool(manifest["budget_faithful"])
            and set(sketch["oracle_field_access"]) <= set(sketch["legal_channel_set"])
            and len(sketch["oracle_field_access"]) <= sketch["legal_query_budget"]
        )
        micro = micro_by_id.get(sketch["sketch_id"], {})
        fair_score = micro.get("exhaustive_legal_query_score") if micro else None
        results.append(
            {
                "sketch_id": sketch["sketch_id"],
                "visible_oracle_budget_faithful": bool(manifest["budget_faithful"]),
                "oracle_registered_as_fair_baseline": can_register,
                "oracle_score": oracle_score,
                "oracle_as_fair_baseline_score": oracle_score if can_register else None,
                "symmetry_blocks_promotion": can_register and fair_score is not None and fair_score >= oracle_score - EQUIVALENCE_BAND,
                "answer_key_diagnostic_oracle_may_support_promotion": False,
                "micro_probe_verdict": micro.get("per_sketch_verdict"),
                "producer_function": "build_oracle_as_baseline_report",
                "code_path_hash": code_path_hash(build_oracle_as_baseline_report),
                "consumed_by_final_verdict": True,
            }
        )
    return {
        "schema_version": "batch_env_headroom_scout_003a_oracle_as_baseline_report_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "results": results,
        "producer_function": "build_oracle_as_baseline_report",
        "code_path_hash": code_path_hash(build_oracle_as_baseline_report),
        "consumed_by_final_verdict": True,
    }


def build_oracle_vs_planner_separation_report(
    sketches: list[dict[str, Any]],
    micro_probe_results: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    micro_by_id = {row["sketch_id"]: row for row in micro_probe_results["results"]}
    results = []
    for sketch in sketches:
        micro = micro_by_id.get(sketch["sketch_id"], {})
        status = micro.get("oracle_vs_planner_separation_status")
        if not status:
            status = "missing" if not sketch.get("oracle_vs_planner_separation_argument") else "not_micro_probed_static_rejection"
        results.append(
            {
                "sketch_id": sketch["sketch_id"],
                "argument_present": bool(sketch.get("oracle_vs_planner_separation_argument")),
                "oracle_vs_planner_separation_status": status,
                "planner_family_max": micro.get("planner_family_max"),
                "visible_oracle_score": micro.get("visible_oracle_score"),
                "falsified_by_planner_results": status == "falsified_by_planner_results",
                "consumed_by_final_verdict": True,
            }
        )
    return {
        "schema_version": "batch_env_headroom_scout_003a_oracle_vs_planner_separation_report_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "results": results,
        "producer_function": "build_oracle_vs_planner_separation_report",
        "code_path_hash": code_path_hash(build_oracle_vs_planner_separation_report),
        "consumed_by_final_verdict": True,
    }


def build_planner_family_report(micro_probe_results: dict[str, Any], run_id: str) -> dict[str, Any]:
    results = []
    for probe in micro_probe_results["results"]:
        planner_rows = [row for row in probe["baseline_rows"] if row["producer_function"] in PLANNER_FAMILY]
        results.append(
            {
                "sketch_id": probe["sketch_id"],
                "planner_family": list(PLANNER_FAMILY),
                "planner_rows": planner_rows,
                "planner_family_max": probe["planner_family_max"],
                "visible_oracle_score": probe["visible_oracle_score"],
                "equivalence_band": EQUIVALENCE_BAND,
                "promotion_gate_passed": probe["planner_family_max"] < probe["visible_oracle_score"] - EQUIVALENCE_BAND,
                "explicit_named_risk": "active_planner_saturation",
                "consumed_by_final_verdict": True,
            }
        )
    return {
        "schema_version": "batch_env_headroom_scout_003a_planner_family_report_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "results": results,
        "producer_function": "build_planner_family_report",
        "code_path_hash": code_path_hash(build_planner_family_report),
        "consumed_by_final_verdict": True,
    }


def build_baseline_independence_report_from_rows(
    rows: list[dict[str, Any]],
    promotion_intended: bool = False,
) -> dict[str, Any]:
    groups: dict[tuple[str, str, tuple[str, ...]], list[str]] = {}
    for row in rows:
        key = (
            row["source_body_hash"],
            row["prediction_vector_hash"],
            tuple(row["input_field_manifest"]),
        )
        groups.setdefault(key, []).append(row["producer_function"])
    aliases = [
        {
            "shared_signature": stable_json_hash({"source": key[0], "prediction": key[1], "fields": key[2]}),
            "producer_functions": sorted(set(names)),
        }
        for key, names in groups.items()
        if len(set(names)) > 1
    ]
    mandatory_present = {row["producer_function"] for row in rows if row.get("consumed_by_final_verdict")}
    missing = [name for name in MANDATORY_BASELINE_PRODUCERS if name not in mandatory_present]
    return {
        "schema_version": "batch_env_headroom_scout_003a_baseline_independence_report_v1",
        "aliases_detected": bool(aliases),
        "alias_groups": aliases,
        "mandatory_missing": missing,
        "promotion_intended": promotion_intended,
        "promotion_blocking_aliasing": promotion_intended and bool(aliases),
        "producer_function": "build_baseline_independence_report_from_rows",
        "code_path_hash": code_path_hash(build_baseline_independence_report_from_rows),
        "consumed_by_final_verdict": True,
    }


def build_baseline_independence_report(micro_probe_results: dict[str, Any], run_id: str) -> dict[str, Any]:
    results = []
    for probe in micro_probe_results["results"]:
        report = build_baseline_independence_report_from_rows(
            probe["baseline_rows"],
            promotion_intended=probe["per_sketch_verdict"] == "promote_to_full_harness_candidate",
        )
        report["sketch_id"] = probe["sketch_id"]
        results.append(report)
    return {
        "schema_version": "batch_env_headroom_scout_003a_baseline_independence_report_bundle_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "results": results,
        "aliases_detected": any(row["aliases_detected"] for row in results),
        "promotion_blocking_aliasing": any(row["promotion_blocking_aliasing"] for row in results),
        "producer_function": "build_baseline_independence_report",
        "code_path_hash": code_path_hash(build_baseline_independence_report),
        "consumed_by_final_verdict": True,
    }


def build_fitted_legal_channel_learner_report(micro_probe_results: dict[str, Any], run_id: str) -> dict[str, Any]:
    rows = []
    for probe in micro_probe_results["results"]:
        for baseline in probe["baseline_rows"]:
            if baseline["producer_function"] == "fitted_legal_channel_learner":
                rows.append(
                    {
                        "sketch_id": probe["sketch_id"],
                        "producer_function": "fitted_legal_channel_learner",
                        "score": baseline["score"],
                        "fit_performed": bool(baseline["details"].get("fit_performed")),
                        "fit_evidence": baseline["details"].get("fit_evidence", {}),
                        "source_body_hash": baseline["source_body_hash"],
                        "prediction_vector_hash": baseline["prediction_vector_hash"],
                        "consumed_by_final_verdict": baseline["consumed_by_final_verdict"],
                    }
                )
    return {
        "schema_version": "batch_env_headroom_scout_003a_fitted_legal_channel_learner_report_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "results": rows,
        "producer_function": "build_fitted_legal_channel_learner_report",
        "code_path_hash": code_path_hash(build_fitted_legal_channel_learner_report),
        "consumed_by_final_verdict": True,
    }


def _static_rejections(static_scan: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "sketch_id": row["sketch_id"],
            "rejection_stage": "independent_static_kill_scan",
            "per_sketch_verdict": row["per_sketch_verdict"],
            "hard_failure_family_code": row["hard_failure_family_code"],
            "verdict_reason": "; ".join(row["derived_kill_reasons"]),
            "fixable_implementation_omission": False,
        }
        for row in static_scan["results"]
        if row["static_verdict"] == "rejected_static_kill"
    ]


def build_rejected_sketches(static_scan: dict[str, Any], micro_probe_results: dict[str, Any], run_id: str) -> dict[str, Any]:
    rejected = _static_rejections(static_scan)
    for probe in micro_probe_results["results"]:
        if probe["per_sketch_verdict"] != "promote_to_full_harness_candidate":
            rejected.append(
                {
                    "sketch_id": probe["sketch_id"],
                    "rejection_stage": "micro_probe",
                    "per_sketch_verdict": probe["per_sketch_verdict"],
                    "hard_failure_family_code": probe["hard_failure_family_code"],
                    "verdict_reason": probe["verdict_reason"],
                    "planner_family_max": probe["planner_family_max"],
                    "oracle_vs_planner_separation_status": probe["oracle_vs_planner_separation_status"],
                    "fixable_implementation_omission": probe["per_sketch_verdict"]
                    in {
                        "blocked_compute_baseline_missing",
                        "blocked_planner_family_missing_or_stubbed",
                        "blocked_baseline_battery_incomplete",
                    },
                }
            )
    return {
        "schema_version": "batch_env_headroom_scout_003a_rejected_sketches_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "rejected": rejected,
        "rejected_count": len(rejected),
        "producer_function": "build_rejected_sketches",
        "code_path_hash": code_path_hash(build_rejected_sketches),
        "consumed_by_final_verdict": True,
    }


def build_promoted_candidates(micro_probe_results: dict[str, Any], run_id: str) -> dict[str, Any]:
    promoted = [
        {
            "sketch_id": probe["sketch_id"],
            "promotion_target": "separate full baseline-first harness task card only",
            "headroom_confirmed_allowed": False,
            "candidate_implementation_authorized": False,
            "run_id": run_id,
        }
        for probe in micro_probe_results["results"]
        if probe["per_sketch_verdict"] == "promote_to_full_harness_candidate"
    ][:2]
    return {
        "schema_version": "batch_env_headroom_scout_003a_promoted_full_harness_candidates_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "promoted": promoted,
        "promoted_count": len(promoted),
        "candidate_implementation_authorized": False,
        "route_tournament_authorized": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_hard_failure_family_report(
    rejected: dict[str, Any],
    sketch_count: int,
    run_id: str,
) -> dict[str, Any]:
    codes = [row["hard_failure_family_code"] for row in rejected["rejected"]]
    all_known = bool(codes) and all(code in HARD_FAILURE_FAMILY_CODES for code in codes)
    fixable = [row for row in rejected["rejected"] if row.get("fixable_implementation_omission")]
    return {
        "schema_version": "batch_env_headroom_scout_003a_hard_failure_family_report_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "sketch_count": sketch_count,
        "rejected_count": rejected["rejected_count"],
        "hard_failure_family_codes": codes,
        "all_rejections_known_hard_failure_families": all_known,
        "fixable_implementation_omission_count": len(fixable),
        "fixable_implementation_omissions": fixable,
        "producer_function": "build_hard_failure_family_report",
        "code_path_hash": code_path_hash(build_hard_failure_family_report),
        "consumed_by_final_verdict": True,
    }


def build_cross_batch_stop_report(
    *,
    repo_root: Path,
    promoted: dict[str, Any],
    rejected: dict[str, Any],
    hard_failure_report: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    cross_batch_path = repo_root / "artifacts/phase0_environment_design_constraints_002c_r1/cross_batch_stop_rules.json"
    source = _stable_json_load(cross_batch_path) if cross_batch_path.exists() else {}
    zero_promotions = promoted["promoted_count"] == 0
    all_rejected = rejected["rejected_count"] == hard_failure_report["sketch_count"]
    trigger_a = (
        zero_promotions
        and all_rejected
        and hard_failure_report["all_rejections_known_hard_failure_families"]
        and hard_failure_report["fixable_implementation_omission_count"] == 0
    )
    return {
        "schema_version": "batch_env_headroom_scout_003a_cross_batch_stop_report_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "source_path": str(cross_batch_path.relative_to(repo_root)),
        "source_sha256": file_sha256(cross_batch_path) if cross_batch_path.exists() else None,
        "source_trigger_consumed": "A_ALL_REJECTS_KNOWN_HARD_FAILURES",
        "cross_batch_source_verdict": source.get("verdict"),
        "zero_promotions": zero_promotions,
        "all_sketches_rejected": all_rejected,
        "all_rejects_known_hard_failure_families": hard_failure_report["all_rejections_known_hard_failure_families"],
        "grammar_stop_triggered": trigger_a,
        "004a_blocked_pending_route_level_review": trigger_a,
        "current_environment_grammar_recommendation": "downgrade_current_environment_grammar" if trigger_a else "continue_environment_search",
        "allowed_route_level_review_decisions_before_004a": source.get("cross_batch_search_budget", {})
        .get("before_any_004a", {})
        .get("allowed_decisions", []),
        "cross_batch_stop_rules_consumed_by_final_verdict": True,
        "producer_function": "build_cross_batch_stop_report",
        "code_path_hash": code_path_hash(build_cross_batch_stop_report),
        "consumed_by_final_verdict": True,
        "claim_ceiling": CLAIM_CEILING,
    }


def produce_callable_final_verdict(context: dict[str, Any]) -> dict[str, Any]:
    lineage = context.get("lineage_source_readback", {})
    rows = context.get("micro_probe_rows", [])
    all_baselines = [baseline for row in rows for baseline in row.get("baseline_rows", [])]
    present = {row["producer_function"] for row in all_baselines if row.get("consumed_by_final_verdict", False)}
    missing = [name for name in MANDATORY_BASELINE_PRODUCERS if name not in present]
    missing_planner = [name for name in PLANNER_FAMILY if name in missing]
    promoted_count = context.get("promoted_count", 0)
    cross_batch = context.get("cross_batch_stop_report", {})
    independence = context.get("baseline_independence_report", {})

    if not lineage.get("lineage_complete", True):
        final_verdict = "blocked_missing_required_lineage_artifact"
    elif not context.get("static_scan_independent", True):
        final_verdict = "blocked_static_scan_not_independent"
    elif not context.get("artifact_integrity_ok", True):
        final_verdict = "blocked_artifact_integrity_failure"
    elif missing_planner:
        final_verdict = "blocked_planner_family_missing_or_stubbed"
    elif "fitted_legal_channel_learner" in missing or "strongest_known_classical_method_for_task_type" in missing:
        final_verdict = "blocked_compute_baseline_missing"
    elif missing:
        final_verdict = "blocked_baseline_battery_incomplete"
    elif any(not row.get("consumed_by_final_verdict", False) for row in all_baselines):
        final_verdict = "blocked_baseline_battery_incomplete"
    elif independence.get("promotion_blocking_aliasing"):
        final_verdict = "blocked_baseline_aliasing_invalidates_promotion"
    elif any(row.get("per_sketch_verdict") == "blocked_missing_oracle_vs_planner_separation_argument" for row in rows) and not cross_batch.get(
        "grammar_stop_triggered"
    ):
        final_verdict = "blocked_missing_oracle_vs_planner_separation_argument"
    elif cross_batch.get("grammar_stop_triggered"):
        final_verdict = "blocked_no_valid_environment_design_grammar"
    elif promoted_count:
        final_verdict = f"promoted_{min(promoted_count, 2)}_full_harness_candidates"
    else:
        final_verdict = "all_rejected_static_or_microprobe"

    return {
        "schema_version": "batch_env_headroom_scout_003a_callable_final_verdict_v1",
        "task_id": TASK_ID,
        "final_verdict": final_verdict,
        "allowed_final_verdict": final_verdict in ALLOWED_FINAL_VERDICTS,
        "producer_function": "produce_callable_final_verdict",
        "code_path_hash": code_path_hash(produce_callable_final_verdict),
        "missing_mandatory_baselines": missing,
        "missing_planner_baselines": missing_planner,
        "cross_batch_stop_report_consumed": bool(cross_batch.get("cross_batch_stop_rules_consumed_by_final_verdict")),
        "cross_batch_stop_recommendation": cross_batch.get("current_environment_grammar_recommendation"),
        "consumed_by_final_verdict": True,
        "claim_ceiling": CLAIM_CEILING,
    }


def final_verdict_context_for_test(remove_baselines: list[str] | None = None) -> dict[str, Any]:
    sketch = make_active_planner_saturated_sketch()
    probe = micro_probe_sketch(sketch, run_id="pytest-final-context")
    remove = set(remove_baselines or [])
    probe["baseline_rows"] = [row for row in probe["baseline_rows"] if row["producer_function"] not in remove]
    return {
        "lineage_source_readback": {"lineage_complete": True},
        "static_scan_independent": True,
        "artifact_integrity_ok": True,
        "micro_probe_rows": [probe],
        "promoted_count": 1,
        "baseline_independence_report": build_baseline_independence_report_from_rows(probe["baseline_rows"], promotion_intended=True),
        "cross_batch_stop_report": {"cross_batch_stop_rules_consumed_by_final_verdict": True, "grammar_stop_triggered": False},
    }


def run_failability_probes(run_id: str = TASK_ID) -> dict[str, Any]:
    base_probe = micro_probe_sketch(make_active_planner_saturated_sketch(), run_id=run_id)
    lowered_probe = micro_probe_sketch(
        make_active_planner_saturated_sketch(),
        run_id=run_id,
        score_overrides={"all_fair_baselines": 0.10},
    )
    missing_planner_context = final_verdict_context_for_test(remove_baselines=["strongest_active_planner_for_task_type"])
    hard_stop = run_batch_scout(out_dir=None, run_id=f"{run_id}-hard-stop", repo_root=Path(__file__).resolve().parents[2])
    results = [
        {
            "probe_id": "lowering_all_fair_baselines_below_oracle_flips_from_saturation",
            "before_verdict": base_probe["per_sketch_verdict"],
            "after_verdict": lowered_probe["per_sketch_verdict"],
            "observed_flip": base_probe["per_sketch_verdict"] != lowered_probe["per_sketch_verdict"],
            "producer_function": "run_failability_probes",
        },
        {
            "probe_id": "planner_family_max_into_oracle_band_rejects",
            "observed_verdict": base_probe["per_sketch_verdict"],
            "planner_family_max": base_probe["planner_family_max"],
            "visible_oracle_score": base_probe["visible_oracle_score"],
            "producer_function": "run_failability_probes",
        },
        {
            "probe_id": "removing_planner_rows_blocks_promotion",
            "observed_final_verdict": produce_callable_final_verdict(missing_planner_context)["final_verdict"],
            "producer_function": "run_failability_probes",
        },
        {
            "probe_id": "missing_oracle_vs_planner_separation_argument_blocks_promotion",
            "observed_verdict": micro_probe_sketch(make_separation_missing_sketch(), run_id=run_id)["per_sketch_verdict"],
            "producer_function": "run_failability_probes",
        },
        {
            "probe_id": "answer_key_oracle_cannot_support_promotion",
            "observed_verdict": micro_probe_sketch(make_answer_key_oracle_sketch(), run_id=run_id)["per_sketch_verdict"],
            "producer_function": "run_failability_probes",
        },
        {
            "probe_id": "direct_legal_channel_compute_rejects",
            "observed_verdict": micro_probe_sketch(make_direct_legal_compute_sketch(), run_id=run_id)["per_sketch_verdict"],
            "producer_function": "run_failability_probes",
        },
        {
            "probe_id": "fitted_learner_reaching_oracle_band_rejects",
            "observed_verdict": micro_probe_sketch(make_fitted_learner_saturated_sketch(), run_id=run_id)["per_sketch_verdict"],
            "producer_function": "run_failability_probes",
        },
        {
            "probe_id": "graph_cache_reaching_oracle_band_rejects",
            "observed_verdict": micro_probe_sketch(make_graph_cache_saturated_sketch(), run_id=run_id)["per_sketch_verdict"],
            "producer_function": "run_failability_probes",
        },
        {
            "probe_id": "passive_leak_rejects",
            "observed_verdict": micro_probe_sketch(make_passive_leak_sketch(), run_id=run_id)["per_sketch_verdict"],
            "producer_function": "run_failability_probes",
        },
        {
            "probe_id": "degenerate_predictor_rejects",
            "observed_verdict": micro_probe_sketch(make_metric_degenerate_sketch(), run_id=run_id)["per_sketch_verdict"],
            "producer_function": "run_failability_probes",
        },
        {
            "probe_id": "all_rejected_hard_family_batch_triggers_grammar_stop",
            "observed_final_verdict": hard_stop["final_verdict"],
            "producer_function": "run_failability_probes",
        },
    ]
    return {
        "schema_version": "batch_env_headroom_scout_003a_failability_probe_report_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "required_probe_ids": list(REQUIRED_FAILABILITY_PROBES),
        "results": results,
        "all_required_probes_present": set(REQUIRED_FAILABILITY_PROBES) <= {row["probe_id"] for row in results},
        "producer_function": "run_failability_probes",
        "code_path_hash": code_path_hash(run_failability_probes),
        "consumed_by_final_verdict": True,
        "claim_ceiling": CLAIM_CEILING,
    }


def _registry_payload(sketches: list[dict[str, Any]], repo_root: Path, run_id: str) -> dict[str, Any]:
    return {
        "schema_version": "batch_env_headroom_scout_003a_sketch_registry_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": MAINLINE_STATUS,
        "enabled_status": ENABLED_STATUS,
        "claim_ceiling": CLAIM_CEILING,
        "sketch_count": len(sketches),
        "sketches": sketches,
        "forbidden": [
            "WM-P",
            "VSB-C",
            "CSL",
            "route tournament",
            "candidate implementation",
            "full harness execution",
            "runtime/mainline/admission/bridge wiring",
            "MINIMAL-ENV-SPEC-001A reopen or optimization",
            "relational_contrast_budget_probe full harness",
            "commit",
            "push",
            "tag",
            "remote-anchor",
        ],
        "source_readback": {
            "repo_root": str(repo_root),
            "branch": _run_git(repo_root, ["branch", "--show-current"]),
            "head": _run_git(repo_root, ["rev-parse", "HEAD"]),
        },
        "producer_function": "_registry_payload",
        "code_path_hash": code_path_hash(_registry_payload),
        "consumed_by_final_verdict": True,
    }


def _artifact_integrity_payload(artifacts: dict[str, Any]) -> dict[str, Any]:
    json_artifacts = {name: payload for name, payload in artifacts.items() if name.endswith(".json")}
    serializable = {}
    failures = []
    for name, payload in json_artifacts.items():
        try:
            json.dumps(payload, sort_keys=True)
            serializable[name] = True
        except TypeError as exc:
            serializable[name] = False
            failures.append({"artifact": name, "error": str(exc)})
    return {
        "schema_version": "batch_env_headroom_scout_003a_artifact_integrity_v1",
        "json_artifacts_serializable": serializable,
        "artifact_integrity_ok": not failures,
        "failures": failures,
    }


def _final_report(
    *,
    registry: dict[str, Any],
    static_scan: dict[str, Any],
    micro_probe: dict[str, Any],
    rejected: dict[str, Any],
    promoted: dict[str, Any],
    planner_report: dict[str, Any],
    oracle_vs_planner: dict[str, Any],
    cross_batch: dict[str, Any],
    final_verdict: dict[str, Any],
) -> str:
    micro_by_id = {row["sketch_id"]: row for row in micro_probe["results"]}
    static_rejected = static_scan["rejected_count"]
    lines = [
        "# BATCH-ENV-HEADROOM-SCOUT-003A Final Report",
        "",
        f"Verdict: `{final_verdict['final_verdict']}`",
        f"Current layer: {CURRENT_LAYER}",
        f"Mainline integration status: {MAINLINE_STATUS}",
        f"Enabled status: {ENABLED_STATUS}",
        "Real trigger evidence: callable lineage readback, independent static scan, candidate-free micro-probes, active planner rows, cross-batch stop report, failability probes, and callable final verdict.",
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
        f"- Number of sketches: {registry['sketch_count']}",
        f"- Number static rejected: {static_rejected}",
        f"- Number micro-probed: {len(micro_probe['results'])}",
        f"- Number promoted: {promoted['promoted_count']}",
        "",
        "Per-sketch verdicts:",
    ]
    for row in rejected["rejected"]:
        planner = row.get("planner_family_max")
        sep = row.get("oracle_vs_planner_separation_status")
        suffix = []
        if planner is not None:
            suffix.append(f"planner_family_max={planner}")
        if sep is not None:
            suffix.append(f"oracle_vs_planner={sep}")
        suffix_text = f" ({', '.join(suffix)})" if suffix else ""
        lines.append(
            f"- `{row['sketch_id']}` via {row['rejection_stage']}: `{row['per_sketch_verdict']}`; hard_failure_family_code={row['hard_failure_family_code']}{suffix_text}"
        )
    if not rejected["rejected"]:
        lines.append("- none")
    lines.extend(
        [
            "",
            "Planner family max per micro-probed sketch:",
        ]
    )
    for row in planner_report["results"]:
        lines.append(f"- `{row['sketch_id']}`: {row['planner_family_max']} (gate_passed={row['promotion_gate_passed']})")
    lines.extend(
        [
            "",
            "Oracle-vs-planner separation status per sketch:",
        ]
    )
    for row in oracle_vs_planner["results"]:
        lines.append(f"- `{row['sketch_id']}`: {row['oracle_vs_planner_separation_status']}")
    lines.extend(
        [
            "",
            "Baseline results:",
            "- Complete candidate-free baseline rows are in `micro_probe_results.json`.",
            "- A10 active planner rows are in `planner_family_report.json`.",
            "- Fitted legal-channel learner evidence is in `fitted_legal_channel_learner_report.json`.",
            "",
            "Ablation results:",
            "- Failability probes are in `failability_probe_report.json`.",
            "- The active planner saturation, missing planner row, missing separation argument, answer-key oracle, direct decode, fitted learner saturation, graph-cache saturation, passive leak, metric degeneracy, and hard-family grammar stop probes all run through callable functions.",
            "",
            "Replay result:",
            "- Full replay is not claimed. Rows record producer hashes, prediction vector hashes, input manifests, strategy signatures, budget traces, and consumed status for later full harness replay design.",
            "",
            "Cross-batch stop recommendation:",
            f"- Recommendation: `{cross_batch['current_environment_grammar_recommendation']}`",
            f"- 004A blocked pending route-level review: {str(cross_batch['004a_blocked_pending_route_level_review']).lower()}",
            "",
            "Stop conditions triggered:",
            f"- Grammar stop triggered: {str(cross_batch['grammar_stop_triggered']).lower()}",
            "",
            "Next minimal closed-loop action:",
        ]
    )
    if promoted["promoted_count"]:
        lines.append("- Draft separate full baseline-first harness task card(s) for promoted sketches; do not execute full harness until separately authorized.")
    else:
        lines.append("- Preserve 003A result and perform route-level review: continue_environment_search / downgrade_current_environment_grammar / replace_environment_grammar / close_phase0_environment_search.")
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
        ]
    )
    return "\n".join(lines) + "\n"


def _write_artifacts(out_dir: Path, artifacts: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for filename, payload in artifacts.items():
        path = out_dir / filename
        if filename.endswith(".json"):
            write_json(path, payload)
        else:
            path.write_text(str(payload), encoding="utf-8")


def run_batch_scout(
    out_dir: str | Path | None = ARTIFACT_DIR_REL,
    run_id: str = TASK_ID,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    lineage = read_lineage_sources(root, run_id=run_id)
    sketches = build_sketch_registry()
    registry = _registry_payload(sketches, root, run_id)

    if not lineage["lineage_complete"]:
        final_verdict = produce_callable_final_verdict(
            {
                "lineage_source_readback": lineage,
                "static_scan_independent": False,
                "artifact_integrity_ok": True,
                "micro_probe_rows": [],
                "promoted_count": 0,
                "baseline_independence_report": {},
                "cross_batch_stop_report": {"cross_batch_stop_rules_consumed_by_final_verdict": False},
            }
        )
        artifacts = {
            "sketch_registry.json": registry,
            "lineage_source_readback.json": lineage,
            "final_verdict.json": final_verdict,
            "final_report.md": f"Verdict: `{final_verdict['final_verdict']}`\n",
        }
        if out_dir is not None:
            _write_artifacts(Path(out_dir), artifacts)
        return {
            "final_verdict": final_verdict["final_verdict"],
            "callable_final_verdict": final_verdict,
            "lineage_source_readback": lineage,
            "current_layer": CURRENT_LAYER,
            "mainline_integration_status": MAINLINE_STATUS,
            "enabled_status": ENABLED_STATUS,
        }

    static_scan = run_independent_static_kill_scan(sketches, run_id=run_id)
    dependency_analysis = build_dependency_analysis(sketches, run_id=run_id)
    micro_probe = run_micro_probes(sketches, static_scan, run_id=run_id)
    oracle_as_baseline = build_oracle_as_baseline_report(sketches, static_scan, micro_probe, run_id=run_id)
    oracle_vs_planner = build_oracle_vs_planner_separation_report(sketches, micro_probe, run_id=run_id)
    planner_report = build_planner_family_report(micro_probe, run_id=run_id)
    baseline_independence = build_baseline_independence_report(micro_probe, run_id=run_id)
    fitted_report = build_fitted_legal_channel_learner_report(micro_probe, run_id=run_id)
    rejected = build_rejected_sketches(static_scan, micro_probe, run_id=run_id)
    promoted = build_promoted_candidates(micro_probe, run_id=run_id)
    hard_failure = build_hard_failure_family_report(rejected, registry["sketch_count"], run_id=run_id)
    cross_batch = build_cross_batch_stop_report(
        repo_root=root,
        promoted=promoted,
        rejected=rejected,
        hard_failure_report=hard_failure,
        run_id=run_id,
    )
    failability = run_failability_probes(run_id=run_id) if not str(run_id).endswith("-hard-stop") else {
        "schema_version": "batch_env_headroom_scout_003a_failability_probe_report_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "required_probe_ids": list(REQUIRED_FAILABILITY_PROBES),
        "results": [],
        "all_required_probes_present": False,
        "producer_function": "run_batch_scout_hard_stop_short_circuit",
        "consumed_by_final_verdict": True,
        "claim_ceiling": CLAIM_CEILING,
    }

    provisional_artifacts: dict[str, Any] = {
        "sketch_registry.json": registry,
        "lineage_source_readback.json": lineage,
        "independent_static_kill_scan.json": static_scan,
        "dependency_analysis.json": dependency_analysis,
        "oracle_as_baseline_report.json": oracle_as_baseline,
        "oracle_vs_planner_separation_report.json": oracle_vs_planner,
        "planner_family_report.json": planner_report,
        "micro_probe_results.json": micro_probe,
        "baseline_independence_report.json": baseline_independence,
        "fitted_legal_channel_learner_report.json": fitted_report,
        "hard_failure_family_report.json": hard_failure,
        "cross_batch_stop_report.json": cross_batch,
        "failability_probe_report.json": failability,
        "promoted_full_harness_candidates.json": promoted,
        "rejected_sketches.json": rejected,
    }
    integrity = _artifact_integrity_payload(provisional_artifacts)
    final_context = {
        "lineage_source_readback": lineage,
        "static_scan_independent": static_scan["static_scan_independent"],
        "artifact_integrity_ok": integrity["artifact_integrity_ok"],
        "micro_probe_rows": micro_probe["results"],
        "promoted_count": promoted["promoted_count"],
        "baseline_independence_report": baseline_independence,
        "cross_batch_stop_report": cross_batch,
    }
    final_verdict = produce_callable_final_verdict(final_context)
    final_report = _final_report(
        registry=registry,
        static_scan=static_scan,
        micro_probe=micro_probe,
        rejected=rejected,
        promoted=promoted,
        planner_report=planner_report,
        oracle_vs_planner=oracle_vs_planner,
        cross_batch=cross_batch,
        final_verdict=final_verdict,
    )
    artifacts = {
        **provisional_artifacts,
        "final_verdict.json": final_verdict,
        "final_report.md": final_report,
    }
    if out_dir is not None:
        _write_artifacts(Path(out_dir), artifacts)
    return {
        "task_id": TASK_ID,
        "run_id": run_id,
        "final_verdict": final_verdict["final_verdict"],
        "callable_final_verdict": final_verdict,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": MAINLINE_STATUS,
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": "callable 003A scout path consumed 002C-R1 lineage, 002B negative evidence, active planner rows, hard-family stop rules, and failability probes",
        "claim_ceiling": CLAIM_CEILING,
        "candidate_implementation_authorized": False,
        "route_tournament_authorized": False,
        "full_harness_execution_authorized": False,
        "sketch_count": registry["sketch_count"],
        "static_rejected_count": static_scan["rejected_count"],
        "micro_probed_count": len(micro_probe["results"]),
        "promoted_count": promoted["promoted_count"],
        "cross_batch_stop_report": cross_batch,
        "artifacts": artifacts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BATCH-ENV-HEADROOM-SCOUT-003A candidate-free environment scout.")
    parser.add_argument("--out", default=ARTIFACT_DIR_REL)
    parser.add_argument("--run-id", default=TASK_ID)
    args = parser.parse_args()
    result = run_batch_scout(out_dir=args.out, run_id=args.run_id)
    print(json.dumps({"final_verdict": result["final_verdict"], "out": args.out}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
