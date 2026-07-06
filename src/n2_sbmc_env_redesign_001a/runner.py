from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from . import detectors
from . import model


RUN_ID = "n2_sbmc_env_redesign_001a_step_b_run_001"
EQUIVALENCE_BAND = 0.01
H = 0.20
IDEAL_MACRO_F1_MIN = 0.70
G_REACH = 0.10
CLAIM_CEILING = (
    "Local candidate-free N2/SBMC environment-preflight evidence and route-state "
    "readback only; no mechanism validity, no theory pressure, no agency, no "
    "autonomy, no subjectivity, no consciousness, no EGO readiness, and no "
    "mainline effect."
)
REQUIRED_BASELINES = set(detectors.NON_IDEAL_DETECTORS)
BLIND_FLOOR_BASELINES = REQUIRED_BASELINES - {"graph_closure"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def code_path_hash() -> str:
    digest = hashlib.sha256()
    for name in ("model.py", "detectors.py", "runner.py"):
        path = Path(__file__).resolve().parent / name
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def function_hash(func: Callable[..., Any]) -> str:
    return _sha256_bytes(inspect.getsource(func).encode("utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def guarded_non_ideal_score(
    detector: Callable[[Mapping[str, Any], Mapping[str, Any], int], int],
    item_repr: Mapping[str, Any],
    context: Mapping[str, Any],
    seed: int,
) -> int:
    return int(detector(detectors.guard_payload(item_repr), detectors.guard_payload(context), seed))


def score_item(item: dict[str, Any], case: dict[str, Any], seed: int, *, context_override: dict[str, Any] | None = None) -> dict[str, int]:
    item_repr = item["item_repr"]
    context = context_override if context_override is not None else model.allowed_context_from_case(case)
    scores = {
        "ideal": detectors.ideal(item_repr, case["audit"], seed),
    }
    for name, detector in detectors.NON_IDEAL_DETECTORS.items():
        scores[name] = guarded_non_ideal_score(detector, item_repr, context, seed)
    return scores


def trace_for_case(case: dict[str, Any], seed: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in case["test_set"]:
        scores = score_item(item, case, seed)
        rows.append(
            {
                "user_id": int(case["user_id"]),
                "item_id": item["item_id"],
                "edge": item["item_repr"]["edge"],
                "target_attr": item["item_repr"]["target_attr"],
                "asserted_value": item["item_repr"]["asserted_value"],
                "item_repr": item["item_repr"],
                "trusted_seed": case["trusted_seed"],
                "label_AUDIT_ONLY": item["audit"]["label"],
                "label_binary_AUDIT_ONLY": item["audit"]["label_binary"],
                "theta_AUDIT_ONLY": case["audit"]["theta"],
                "detector_scores": scores,
                "candidate_decision": None,
            }
        )
    return rows


def macro_f1_binary(labels: list[int], predictions: list[int]) -> float:
    values: list[float] = []
    for klass in (0, 1):
        tp = sum(1 for y, p in zip(labels, predictions) if y == klass and p == klass)
        fp = sum(1 for y, p in zip(labels, predictions) if y != klass and p == klass)
        fn = sum(1 for y, p in zip(labels, predictions) if y == klass and p != klass)
        denom = 2 * tp + fp + fn
        values.append(0.0 if denom == 0 else (2 * tp) / denom)
    return float(sum(values) / len(values))


def _score_row(detector_id: str, labels: list[int], predictions: list[int], trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    producer = detectors.DETECTORS[detector_id]
    return {
        "baseline_id": detector_id if detector_id != "ideal" else None,
        "producer_id": detector_id,
        "producer_function": f"n2_sbmc_env_redesign_001a.detectors.{producer.__name__}",
        "input_artifacts": ["generated_user_cases", "serialized_item_repr", "serialized_trusted_seed"],
        "run_id": RUN_ID,
        "seed_context_episode_ids": [row["item_id"] for row in trace_rows],
        "aggregation_rule": "binary_macro_f1_over_balanced_genuine_contaminated_items",
        "code_path_hash": function_hash(producer),
        "macro_f1": macro_f1_binary(labels, predictions),
        "callable_invoked": True,
    }


def run_baseline_battery(trace_rows: list[dict[str, Any]], *, disabled_baselines: tuple[str, ...] = ()) -> dict[str, Any]:
    disabled = set(disabled_baselines)
    labels = [int(row["label_binary_AUDIT_ONLY"]) for row in trace_rows]
    rows: list[dict[str, Any]] = []
    for name in sorted(REQUIRED_BASELINES):
        if name in disabled:
            continue
        predictions = [int(row["detector_scores"][name]) for row in trace_rows]
        rows.append(_score_row(name, labels, predictions, trace_rows))
    strongest = max(rows, key=lambda row: row["macro_f1"]) if rows else None
    lookup_row = next((row for row in rows if row["producer_id"] == "per_user_lookup_nn"), None)
    return {
        "producer_function": "n2_sbmc_env_redesign_001a.runner.run_baseline_battery",
        "baseline_ids": [row["producer_id"] for row in rows],
        "declared_baseline_ids": sorted(REQUIRED_BASELINES),
        "missing_baseline_ids": sorted(REQUIRED_BASELINES - {row["producer_id"] for row in rows}),
        "results": rows,
        "strongest_fair_baseline": {
            "baseline_id": strongest["producer_id"],
            "macro_f1": strongest["macro_f1"],
            "producer_function": strongest["producer_function"],
        }
        if strongest
        else None,
        "strongest_fair_is_max_over_full_battery": bool(strongest)
        and strongest["macro_f1"] == max(row["macro_f1"] for row in rows),
        "per_user_lookup_broken": bool(lookup_row and lookup_row["macro_f1"] <= 0.50),
    }


def run_leakage_scan(cases: list[dict[str, Any]], *, disable_positive_control: bool = False) -> dict[str, Any]:
    feature_names = model.feature_names()
    clean_scan = detectors.scan_feature_names_for_leakage(feature_names)
    labels: list[int] = []
    clean_predictions: list[int] = []
    canary_predictions: list[int] = []
    for case in cases:
        theta = {int(k): int(v) for k, v in case["audit"]["theta"].items()}
        for item in case["test_set"]:
            labels.append(int(item["audit"]["label_binary"]))
            clean_predictions.append(0)
            target = int(item["item_repr"]["target_attr"])
            asserted = int(item["item_repr"]["asserted_value"])
            canary_predictions.append(int(asserted != theta[target]))
    clean_accuracy = sum(1 for y, p in zip(labels, clean_predictions) if y == p) / len(labels)
    canary_accuracy = sum(1 for y, p in zip(labels, canary_predictions) if y == p) / len(labels)
    canary_scan = detectors.scan_feature_names_for_leakage(["theta_canary_asserted_matches_hidden_target"])
    positive = (
        (not disable_positive_control)
        and not clean_scan["fires"]
        and canary_scan["fires"]
        and canary_accuracy >= clean_accuracy + 0.20
        and canary_accuracy >= 0.70
    )
    blocking = []
    if not positive:
        blocking.append("theta_canary_positive_control_not_detected")
    if clean_scan["fires"]:
        blocking.append("clean_feature_names_leakage_detected")
    return {
        "producer_function": "n2_sbmc_env_redesign_001a.runner.run_leakage_scan",
        "positive_control_fires": bool(positive),
        "clean_scan_passed": not clean_scan["fires"],
        "clean_accuracy": clean_accuracy,
        "canary_accuracy": canary_accuracy,
        "clean_scan": clean_scan,
        "canary_scan": canary_scan,
        "blocking_reasons": blocking,
    }


def replay_non_ideal(trace_rows: list[dict[str, Any]], *, tamper: bool = False, seed: int = model.BASE_SEED) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    for index, row in enumerate(trace_rows):
        context = {
            "schema_version": "n2_sbmc_allowed_context_v1",
            "trusted_seed": row["trusted_seed"],
            "relation_tables": model.relation_tables(),
        }
        recomputed = {
            name: guarded_non_ideal_score(detector, row["item_repr"], context, seed)
            for name, detector in detectors.NON_IDEAL_DETECTORS.items()
        }
        expected = {name: int(row["detector_scores"][name]) for name in detectors.NON_IDEAL_DETECTORS}
        if tamper and index == 0:
            recomputed["graph_closure"] = 1 - recomputed["graph_closure"]
        if recomputed != expected:
            mismatches.append({"item_id": row["item_id"], "expected": expected, "observed": recomputed})
    return {
        "producer_function": "n2_sbmc_env_redesign_001a.runner.replay_non_ideal",
        "passed": not mismatches,
        "uses_hash_only_comparison": False,
        "uses_stored_outputs_only": False,
        "recomputed_from": ["item_repr", "trusted_seed", "relation_tables", "detector_name", "seed"],
        "forbidden_inputs_used": [],
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:5],
        "blocking_reasons": [] if not mismatches else ["replay_recompute_mismatch"],
    }


def _score_graph_with_context(cases: list[dict[str, Any]], context_builder: Callable[[dict[str, Any]], dict[str, Any]]) -> float:
    labels: list[int] = []
    predictions: list[int] = []
    for case in cases:
        context = context_builder(case)
        for item in case["test_set"]:
            labels.append(int(item["audit"]["label_binary"]))
            predictions.append(
                guarded_non_ideal_score(detectors.graph_closure, item["item_repr"], context, model.BASE_SEED)
            )
    return macro_f1_binary(labels, predictions)


def run_ablation_controls(cases: list[dict[str, Any]], graph_macro_f1: float) -> dict[str, Any]:
    no_covered = _score_graph_with_context(
        cases,
        lambda case: model.allowed_context_from_case(case, include_covered=False),
    )
    wrong_relation = _score_graph_with_context(
        cases,
        lambda case: {
            "schema_version": "n2_sbmc_allowed_context_v1",
            "trusted_seed": case["trusted_seed"],
            "relation_tables": model.shifted_relation_tables(),
        },
    )
    sparse_passed = all(
        int(item["item_repr"]["target_attr"]) not in {int(row["attr"]) for row in case["trusted_seed"]}
        for case in cases
        for item in case["test_set"]
    )
    no_covered_degraded = graph_macro_f1 - no_covered >= G_REACH
    wrong_relation_degraded = graph_macro_f1 - wrong_relation >= G_REACH
    passed = bool(no_covered_degraded and wrong_relation_degraded and sparse_passed)
    blocking: list[str] = []
    if not no_covered_degraded:
        blocking.append("no_covered_observations_did_not_degrade_graph_closure")
    if not wrong_relation_degraded:
        blocking.append("wrong_relation_table_did_not_degrade_graph_closure")
    if not sparse_passed:
        blocking.append("sparse_coverage_control_failed")
    return {
        "producer_function": "n2_sbmc_env_redesign_001a.runner.run_ablation_controls",
        "passed": passed,
        "all_controls_consumed_by_final_verdict": True,
        "no_covered_observations": {
            "macro_f1": no_covered,
            "graph_closure_degraded": no_covered_degraded,
        },
        "wrong_relation_table": {
            "macro_f1": wrong_relation,
            "graph_closure_degraded": wrong_relation_degraded,
        },
        "sparse_coverage_control": {"passed": sparse_passed},
        "blocking_reasons": blocking,
    }


def build_preregistration() -> dict[str, Any]:
    return {
        "task_id": model.TASK_ID,
        "execution_task_id": model.EXECUTION_TASK_ID,
        "schema_version": "n2_sbmc_step_a_preregistration.v1",
        "step": "STEP-A",
        "status": "pre_registered_before_step_b_scoring",
        "base_seed": model.BASE_SEED,
        "environment": {
            "domain_size": model.DOMAIN_SIZE,
            "covered_attrs": list(model.COVERED_ATTRS),
            "uncovered_attrs": list(model.UNCOVERED_ATTRS),
            "edges": [list(edge) for edge in model.EDGES],
            "relation_tables": model.relation_tables(),
            "sparse_coverage_rule": "trusted_seed contains covered attrs only; test targets uncovered attrs only",
        },
        "baseline_panel": sorted(REQUIRED_BASELINES),
        "thresholds": {
            "H": H,
            "ideal_macro_f1_min": IDEAL_MACRO_F1_MIN,
            "G_reach": G_REACH,
            "equivalence_band": EQUIVALENCE_BAND,
        },
        "claim_ceiling": CLAIM_CEILING,
        "code_path_hash": code_path_hash(),
    }


def build_provenance(
    ideal_row: dict[str, Any],
    baseline_comparison: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    ablation_report: dict[str, Any],
    result: dict[str, Any] | None,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for row in [ideal_row, *baseline_comparison["results"]]:
        records.append(
            {
                "kind": "score",
                "producer_id": row["producer_id"],
                "producer_function": row["producer_function"],
                "input_artifacts": row["input_artifacts"],
                "run_id": row["run_id"],
                "seed_context_episode_ids": row["seed_context_episode_ids"],
                "aggregation_rule": row["aggregation_rule"],
                "code_path_hash": row["code_path_hash"],
                "consumed_by_final_verdict": True,
                "value": row["macro_f1"],
            }
        )
    for producer_id, report, func in (
        ("leakage_scan", leakage_report, run_leakage_scan),
        ("replay_recomputation", replay_report, replay_non_ideal),
        ("ablation_controls", ablation_report, run_ablation_controls),
    ):
        records.append(
            {
                "kind": "control",
                "producer_id": producer_id,
                "producer_function": report["producer_function"],
                "input_artifacts": ["generated_user_cases", "trace_rows"],
                "run_id": RUN_ID,
                "seed_context_episode_ids": ["all"],
                "aggregation_rule": "control_must_pass_or_block_final_verdict",
                "code_path_hash": function_hash(func),
                "consumed_by_final_verdict": True,
                "value": report.get("passed", report.get("positive_control_fires")),
            }
        )
    if result is not None:
        records.append(
            {
                "kind": "final_verdict",
                "producer_id": "final_verdict_derivation",
                "producer_function": "n2_sbmc_env_redesign_001a.runner.derive_result",
                "input_artifacts": ["ideal_score", "baseline_comparison", "leakage_report", "replay_report", "ablation_report"],
                "run_id": RUN_ID,
                "seed_context_episode_ids": ["all"],
                "aggregation_rule": "ordered_blockers_then_decision_table",
                "code_path_hash": function_hash(derive_result),
                "consumed_by_final_verdict": True,
                "value": result["verdict"],
            }
        )
    return {"producer_function": "n2_sbmc_env_redesign_001a.runner.build_provenance", "records": records}


def verify_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    required_fields = {
        "kind",
        "producer_id",
        "producer_function",
        "input_artifacts",
        "run_id",
        "seed_context_episode_ids",
        "aggregation_rule",
        "code_path_hash",
        "consumed_by_final_verdict",
        "value",
    }
    required_ids = REQUIRED_BASELINES | {
        "ideal",
        "leakage_scan",
        "replay_recomputation",
        "ablation_controls",
        "final_verdict_derivation",
    }
    reasons: list[str] = []
    ids = {row.get("producer_id") for row in provenance.get("records", [])}
    for missing in sorted(required_ids - ids):
        reasons.append(f"missing_required_provenance:{missing}")
    for index, row in enumerate(provenance.get("records", [])):
        missing_fields = sorted(required_fields - set(row))
        if missing_fields:
            reasons.append(f"record_{index}_missing:{','.join(missing_fields)}")
        if len(str(row.get("code_path_hash", ""))) != 64:
            reasons.append(f"record_{index}_bad_code_path_hash")
        if row.get("consumed_by_final_verdict") is not True:
            reasons.append(f"record_{index}_not_consumed")
    return {
        "producer_function": "n2_sbmc_env_redesign_001a.runner.verify_provenance",
        "passed": not reasons,
        "blocking_reasons": reasons,
    }


def derive_result(
    *,
    ideal_row: dict[str, Any],
    baseline_comparison: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    ablation_report: dict[str, Any],
    provenance_check: dict[str, Any],
    trace_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    ideal_score = float(ideal_row["macro_f1"])
    strongest = baseline_comparison["strongest_fair_baseline"]
    blind_scores = [
        row["macro_f1"]
        for row in baseline_comparison["results"]
        if row["producer_id"] in BLIND_FLOOR_BASELINES
    ]
    blind_max = max(blind_scores) if blind_scores else 0.0
    graph_row = next((row for row in baseline_comparison["results"] if row["producer_id"] == "graph_closure"), None)
    graph_score = float(graph_row["macro_f1"]) if graph_row else 0.0
    blockers: list[str] = []
    verdict = "headroom_reachable_by_graph_closure"
    closure_type = "BASELINE_EQUIVALENCE"
    if baseline_comparison["missing_baseline_ids"]:
        verdict = "blocked_missing_required_baseline"
        closure_type = "INCONCLUSIVE"
        blockers.extend(f"missing_required_baseline:{name}" for name in baseline_comparison["missing_baseline_ids"])
    elif not leakage_report["positive_control_fires"]:
        verdict = "blocked_leakage_positive_control_failure"
        closure_type = "LEAKAGE_OR_CHEATING"
        blockers.extend(leakage_report["blocking_reasons"])
    elif not leakage_report["clean_scan_passed"]:
        verdict = "blocked_leakage_clean_scan_failure"
        closure_type = "LEAKAGE_OR_CHEATING"
        blockers.extend(leakage_report["blocking_reasons"])
    elif not replay_report["passed"]:
        verdict = "blocked_replay_recompute_failure"
        closure_type = "INCONCLUSIVE"
        blockers.extend(replay_report["blocking_reasons"])
    elif not ablation_report["passed"]:
        verdict = "blocked_ablation_control_failure"
        closure_type = "INCONCLUSIVE"
        blockers.extend(ablation_report["blocking_reasons"])
    elif not provenance_check["passed"]:
        verdict = "blocked_provenance_failure"
        closure_type = "INCONCLUSIVE"
        blockers.extend(provenance_check["blocking_reasons"])
    elif ideal_score < IDEAL_MACRO_F1_MIN or ideal_score - blind_max < H:
        verdict = "env_no_headroom"
        closure_type = "UNDERPOWERED"
        blockers.append("ideal_gate_or_blind_headroom_failed")
    elif not baseline_comparison["per_user_lookup_broken"]:
        verdict = "invalid_instrument_lookup_solvable"
        closure_type = "INSTRUMENT_INVALID"
        blockers.append("per_user_lookup_reaches_headroom")
    elif graph_score - blind_max >= G_REACH:
        verdict = "headroom_reachable_by_graph_closure"
        closure_type = "BASELINE_EQUIVALENCE"
        blockers.append("graph_closure_reaches_ideal_headroom")
    else:
        verdict = "headroom_present_but_unreachable_theta_free"
        closure_type = "INCONCLUSIVE"
        blockers.append("graph_closure_does_not_reach_headroom")
    return {
        "task_id": model.TASK_ID,
        "execution_task_id": model.EXECUTION_TASK_ID,
        "run_id": RUN_ID,
        "verdict": verdict,
        "closure_type_recommended": closure_type,
        "stop_conditions_triggered": blockers,
        "layer": "engineering_implementation + mechanism_route_governance",
        "mainline_integration_status": "none",
        "enabled_status": "local_candidate_free_harness_only",
        "real_trigger_evidence": "python -m n2_sbmc_env_redesign_001a.runner",
        "claim_ceiling": CLAIM_CEILING,
        "ideal_macro_f1": ideal_score,
        "blind_floor_max_macro_f1": blind_max,
        "graph_closure_macro_f1": graph_score,
        "strongest_fair_baseline_id": strongest["baseline_id"] if strongest else None,
        "strongest_fair_baseline_macro_f1": strongest["macro_f1"] if strongest else None,
        "equivalence_band": EQUIVALENCE_BAND,
        "trace_row_count": len(trace_rows),
        "eval_user_ids": list(model.EVAL_USER_IDS),
        "candidate_mechanism_run": False,
        "mechanism_experiment_run": False,
        "theory_pressure_authorized": False,
        "route_state_update_recommended": verdict == "headroom_reachable_by_graph_closure",
        "auto_remote_anchor": "forbidden",
    }


def build_failure_manifest(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "producer_function": "n2_sbmc_env_redesign_001a.runner.build_failure_manifest",
        "verdict": result["verdict"],
        "blocking_reasons": list(result["stop_conditions_triggered"]),
        "has_blocking_failure": result["verdict"].startswith("blocked_"),
        "claim_ceiling": CLAIM_CEILING,
    }


def run_harness(
    output_dir: str | Path,
    *,
    persist_artifacts: bool = True,
    disabled_baselines: tuple[str, ...] = (),
    disable_leakage_positive_control: bool = False,
    tamper_replay: bool = False,
) -> dict[str, Any]:
    cases = [model.build_user_case(user_id) for user_id in model.EVAL_USER_IDS]
    trace_rows = [row for case in cases for row in trace_for_case(case, model.BASE_SEED)]
    labels = [int(row["label_binary_AUDIT_ONLY"]) for row in trace_rows]
    ideal_row = _score_row("ideal", labels, [int(row["detector_scores"]["ideal"]) for row in trace_rows], trace_rows)
    baseline_comparison = run_baseline_battery(trace_rows, disabled_baselines=disabled_baselines)
    leakage_report = run_leakage_scan(cases, disable_positive_control=disable_leakage_positive_control)
    replay_report = replay_non_ideal(trace_rows, tamper=tamper_replay)
    graph_score = next(
        (row["macro_f1"] for row in baseline_comparison["results"] if row["producer_id"] == "graph_closure"),
        0.0,
    )
    ablation_report = run_ablation_controls(cases, graph_score)
    preliminary = build_provenance(ideal_row, baseline_comparison, leakage_report, replay_report, ablation_report, None)
    preliminary_check = verify_provenance(
        {
            **preliminary,
            "records": [
                *preliminary["records"],
                {
                    "kind": "final_verdict",
                    "producer_id": "final_verdict_derivation",
                    "producer_function": "n2_sbmc_env_redesign_001a.runner.derive_result",
                    "input_artifacts": ["pending"],
                    "run_id": RUN_ID,
                    "seed_context_episode_ids": ["all"],
                    "aggregation_rule": "pending",
                    "code_path_hash": function_hash(derive_result),
                    "consumed_by_final_verdict": True,
                    "value": "pending",
                },
            ],
        }
    )
    result = derive_result(
        ideal_row=ideal_row,
        baseline_comparison=baseline_comparison,
        leakage_report=leakage_report,
        replay_report=replay_report,
        ablation_report=ablation_report,
        provenance_check=preliminary_check,
        trace_rows=trace_rows,
    )
    provenance = build_provenance(ideal_row, baseline_comparison, leakage_report, replay_report, ablation_report, result)
    provenance_check = verify_provenance(provenance)
    result = derive_result(
        ideal_row=ideal_row,
        baseline_comparison=baseline_comparison,
        leakage_report=leakage_report,
        replay_report=replay_report,
        ablation_report=ablation_report,
        provenance_check=provenance_check,
        trace_rows=trace_rows,
    )
    failure_manifest = build_failure_manifest(result)
    run = {
        "step_a_preregistration": build_preregistration(),
        "result": result,
        "trace": trace_rows,
        "baseline_comparison": baseline_comparison,
        "ablation_report": ablation_report,
        "replay_report": replay_report,
        "leakage_report": leakage_report,
        "computed_evidence_provenance": provenance,
        "provenance_check": provenance_check,
        "failure_manifest": failure_manifest,
        "claim_ceiling": CLAIM_CEILING,
    }
    if persist_artifacts:
        write_artifacts(Path(output_dir), run)
    return run


def write_artifacts(output_dir: Path, run: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "step_a_preregistration.json": run["step_a_preregistration"],
        "result.json": run["result"],
        "baseline_comparison.json": run["baseline_comparison"],
        "ablation_report.json": run["ablation_report"],
        "replay_report.json": run["replay_report"],
        "leakage_report.json": run["leakage_report"],
        "computed_evidence_provenance.json": run["computed_evidence_provenance"],
        "failure_manifest.json": run["failure_manifest"],
    }
    for name, payload in payloads.items():
        write_json(output_dir / name, payload)
    with (output_dir / "trace.jsonl").open("w", encoding="utf-8") as handle:
        for row in run["trace"]:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")


def build_route_state_payloads(result: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state = {
        "route_id": model.TASK_ID,
        "route_family": "N2-SBMC",
        "current_state": "CLOSURE_REVIEW_REQUIRED",
        "frontier_scope": "candidate_free_step_b_completed",
        "updated_at_utc": now,
        "created_by_task": model.EXECUTION_TASK_ID,
        "mechanism_validity": "unknown",
        "theory_validity": "unknown",
        "authorizations": {
            "mechanism_validity": False,
            "theory_pressure": False,
            "future_scoring": False,
            "mechanism_experiment": False,
        },
        "step_b_result": {
            "artifact": "artifacts/N2-SBMC-ENV-REDESIGN-001A/result.json",
            "verdict": result["verdict"],
            "closure_type_recommended": result["closure_type_recommended"],
            "strongest_fair_baseline_id": result["strongest_fair_baseline_id"],
        },
        "source_readback": {
            "ledger_entries": [
                {
                    "entry": "L-014",
                    "path": "docs/research/FSP-STAGE-LEDGER.md",
                    "readback": "N2-SBMC-ENV-REDESIGN-001A banked as design/pre-registration card; candidate-free preflight; NO code/scoring in that bank.",
                },
                {
                    "entry": "L-017",
                    "path": "docs/research/FSP-STAGE-LEDGER.md",
                    "readback": "Candidate-free STEP-B completed; graph_closure reached ideal headroom; baseline-equivalence closure review required.",
                },
            ],
            "task_card": "docs/codex/tasks/N2-SBMC-ENV-REDESIGN-001A-STEP-A-STEP-B-001A.md",
        },
    }
    closure = {
        "route_id": model.TASK_ID,
        "closure_type": result["closure_type_recommended"],
        "allowed_next_actions": [
            "preserve_candidate_free_n2_negative_evidence",
            "review_baseline_equivalence_closure_packet",
            "design_fresh_learning_regime_only_under_new_bounded_task_card",
        ],
        "forbidden_next_actions": [
            "claim_n2_mechanism_validity",
            "claim_theory_pressure",
            "treat_graph_closure_equivalence_as_mechanism_pass",
            "reuse_this_as_ego_mainline_or_runtime_evidence",
            "push_tag_or_remote_anchor_without_explicit_authorization",
        ],
        "claim_ceiling": {
            "max": CLAIM_CEILING,
            "forbidden_claims": [
                "mechanism_validity",
                "theory_pressure",
                "agency",
                "autonomy",
                "subjectivity",
                "consciousness",
                "ego_readiness",
                "companion_readiness",
                "mainline_effect",
            ],
        },
        "evidence_status": {
            "baseline": "present",
            "ablation": "present",
            "replay": "present",
            "provenance": "present",
            "leakage_positive_control": "present",
            "fresh_adjudication": "candidate_free_step_b_only",
            "mechanism_validity": "unknown",
            "theory_validity": "unknown",
        },
        "source_evidence": [
            "artifacts/N2-SBMC-ENV-REDESIGN-001A/result.json",
            "artifacts/N2-SBMC-ENV-REDESIGN-001A/baseline_comparison.json",
            "artifacts/N2-SBMC-ENV-REDESIGN-001A/ablation_report.json",
            "artifacts/N2-SBMC-ENV-REDESIGN-001A/replay_report.json",
            "artifacts/N2-SBMC-ENV-REDESIGN-001A/computed_evidence_provenance.json",
        ],
        "notes": [
            "graph_closure is the strongest fair baseline and reaches the ideal headroom",
            "baseline equivalence is a valid negative / engineering-sufficient closure candidate, not a mechanism pass",
        ],
        "theory_pressure_authorized": False,
        "mechanism_evidence_authorized": False,
    }
    program_state = {
        "task_id": "ROUTE-STATE-MACHINE-001A",
        "current_frontier_route_id": model.TASK_ID,
        "allowed_next_actions": [
            "preserve_current_closure_review_packet",
            "review_n2_baseline_equivalence_closure",
            "draft_new_bounded_task_card_before_any_successor_route",
        ],
        "forbidden_next_actions": [
            "claim_mechanism_validity",
            "claim_theory_pressure",
            "modify_ego_runtime",
            "modify_llm_airi_deployment_or_api_key_files",
            "push_tag_or_remote_anchor_without_explicit_authorization",
        ],
        "claim_ceiling": {
            "max": "local route-governance validation only",
            "forbidden_claims": [
                "mechanism_validity",
                "theory_pressure",
                "agency",
                "autonomy",
                "subjectivity",
                "consciousness",
                "ego_readiness",
                "companion_readiness",
                "mainline_effect",
            ],
        },
        "updated_at_utc": now,
        "source_readback": {
            "ledger_entries": [
                {
                    "entry": "L-017",
                    "path": "docs/research/FSP-STAGE-LEDGER.md",
                    "readback": "N2 candidate-free STEP-B result routes to baseline-equivalence closure review.",
                }
            ]
        },
    }
    return {"state": state, "closure": closure, "program_state": program_state}


def write_route_state_update(repo: Path, result: dict[str, Any]) -> None:
    payloads = build_route_state_payloads(result)
    route_dir = repo / "artifacts" / "ROUTE-STATE-MACHINE-001A" / "routes" / model.TASK_ID
    write_json(route_dir / "state.json", payloads["state"])
    write_json(route_dir / "closure.json", payloads["closure"])
    write_json(repo / "artifacts" / "ROUTE-STATE-MACHINE-001A" / "program_state.json", payloads["program_state"])
    event = {
        "event": "candidate_free_step_b_completed",
        "route_id": model.TASK_ID,
        "task_id": model.EXECUTION_TASK_ID,
        "verdict": result["verdict"],
        "closure_type_recommended": result["closure_type_recommended"],
        "updated_at_utc": payloads["state"]["updated_at_utc"],
    }
    with (route_dir / "events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/N2-SBMC-ENV-REDESIGN-001A")
    parser.add_argument("--update-route-state", action="store_true")
    args = parser.parse_args(argv)
    run = run_harness(args.output_dir, persist_artifacts=True)
    if args.update_route_state:
        write_route_state_update(repo_root(), run["result"])
    print(json.dumps(run["result"], indent=2, sort_keys=True))
    return 0 if not run["failure_manifest"]["has_blocking_failure"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
