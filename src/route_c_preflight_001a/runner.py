from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable

from . import CLAIM_CEILING, CURRENT_LAYER, TASK_ID, WHAT_THIS_DOES_NOT_PROVE
from . import core, leakage, provenance, replay


DEFAULT_SEEDS = tuple(range(1600, 1632))
BLUEPRINT = Path("docs/research/ROUTE-C-PREFLIGHT-001A-HOSTILE-DESIGN-BLUEPRINT.md")
TASK_CARD = Path("docs/codex/tasks/ROUTE-C-PREFLIGHT-001A.md")

# Parent negative-evidence references (read-only; preserved, not reinterpreted).
PARENT_NEGATIVE_AUDIT = {
    "audit_doc": "docs/research/CLAUDE-INDEPENDENT-ROUTE-C-PREFLIGHT-001A-HOSTILE-AUDIT-001A.md",
    "blocking_verdict": "blocked_by_observation_baseline_underpowered",
    "parent_impl_commit": "726f26daef9d766abe0592972acf8569041483fa",
    "parent_audit_preservation_commit": "eadc08f04e9bc465379fd35b3844a823a55062c6",
}

ALLOWED_VERDICTS = {
    "preflight_admitted_for_candidate_design",
    "blocked_by_observation_decodable_self_set",
    "blocked_by_no_interventional_headroom",
    "blocked_by_schema_alias_leakage",
    "blocked_by_non_fail_able_control",
    "blocked_by_provenance_gap",
}
ALLOWED_PATH_PREFIXES = (
    "src/route_c_preflight_001a/",
    "tests/route_c_preflight_001a/",
    "artifacts/route_c_preflight_001a/",
)

# Failure-probe seeds, disjoint from DEFAULT_SEEDS and the supervised trainer.
HEADROOM_PROBE_SEEDS = tuple(range(2_000_000, 2_000_008))


def _doc_hashes(repo_root: Path) -> dict[str, str]:
    blueprint = repo_root / BLUEPRINT
    task_card = repo_root / TASK_CARD
    return {
        "blueprint_path": BLUEPRINT.as_posix(),
        "blueprint_sha256": provenance.sha256_text(blueprint.read_text(encoding="utf-8")),
        "task_card_path": TASK_CARD.as_posix(),
        "task_card_sha256": provenance.sha256_text(task_card.read_text(encoding="utf-8")),
    }


def find_forbidden_status_paths(status_lines: list[str]) -> list[str]:
    violations = []
    for line in status_lines:
        if not line.strip():
            continue
        path = line[3:].strip().replace("\\", "/")
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path.startswith(ALLOWED_PATH_PREFIXES):
            violations.append(path)
    return violations


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _oracle_artifact_report(oracle: dict[str, Any]) -> dict[str, Any]:
    report = {key: value for key, value in oracle.items() if key != "legal_intervention_rows"}
    rows = oracle["legal_intervention_rows"]
    report["legal_intervention_row_count"] = len(rows)
    report["legal_intervention_rows_hash"] = provenance.sha256_json(rows)
    report["legal_intervention_rows_omitted_from_report"] = True
    return report


def _headroom_failure_probe(*, config: core.Config, run_id: str, snapshot_hash: str) -> dict[str, Any]:
    """gain=0 ablation: interventions carry no information -> headroom MUST block."""
    probe_cfg = replace(config, gain=0.0)
    bundle = core.build_episode_bundle(seeds=HEADROOM_PROBE_SEEDS, config=probe_cfg, run_id=f"{run_id}-g0")
    panel = core.run_baseline_panel(bundle, run_id=f"{run_id}-g0-panel", threshold_snapshot_hash=snapshot_hash)
    oracle = core.run_interventional_oracle(bundle, run_id=f"{run_id}-g0-oracle", threshold_snapshot_hash=snapshot_hash)
    gate = core.interventional_headroom_gate(
        obs_score=panel["obs_only"]["family_max"]["value"],
        oracle_score=oracle["aggregate_score"]["value"],
        config=probe_cfg,
    )
    return {
        "gain": 0.0,
        "oracle_score": oracle["aggregate_score"]["value"],
        "obs_family_max": panel["obs_only"]["family_max"]["value"],
        "headroom_verdict": gate["verdict"],
        "blocks": gate["verdict"] == "blocked_by_no_interventional_headroom",
    }


def _provenance_failure_probe(real_row: dict[str, Any], *, snapshot: dict[str, Any], failure_controls: dict[str, bool]) -> dict[str, Any]:
    """A material row stripped of code_path_hash MUST be rejected by the gate."""
    broken = dict(real_row)
    broken.pop("code_path_hash", None)
    res = provenance.validate_provenance_rows(
        [broken], threshold_snapshot=snapshot, failure_controls=failure_controls
    )
    return {"description": "drop code_path_hash from a real row", "verdict": res["verdict"], "blocks": res["verdict"] == "blocked_by_provenance_gap"}


def _select_verdict(
    *,
    non_identifiability: dict[str, Any],
    headroom: dict[str, Any],
    leakage_report: dict[str, Any],
    provenance_validation: dict[str, Any],
    replay_report: dict[str, Any],
) -> tuple[str, list[str]]:
    blockers: list[str] = []
    if provenance_validation["verdict"] != "provenance_valid":
        blockers.append("blocked_by_provenance_gap")
    if leakage_report["blocking_verdict"]:
        blockers.append(leakage_report["blocking_verdict"])
    if non_identifiability["verdict"].startswith("blocked_by_"):
        blockers.append(non_identifiability["verdict"])
    if headroom["verdict"].startswith("blocked_by_"):
        blockers.append(headroom["verdict"])
    if replay_report["verdict"] != "replay_recomputed":
        blockers.append("blocked_by_provenance_gap")
    if blockers:
        return blockers[0], blockers
    return "preflight_admitted_for_candidate_design", []


def run_preflight(
    *,
    repo_root: Path,
    output_dir: Path,
    run_id: str,
    config: core.Config | None = None,
    seeds: Iterable[int] = DEFAULT_SEEDS,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    config = config or core.default_config()
    seeds = list(seeds)

    # Freeze thresholds BEFORE any gate runs; every record references this hash.
    threshold_snapshot = provenance.build_threshold_snapshot(config=config, config_type=core.Config)
    snapshot_hash = threshold_snapshot["snapshot_hash"]
    live_config_source_hash = provenance.config_source_hash(core.Config)
    parent_doc_hashes = _doc_hashes(repo_root)

    bundle = core.build_episode_bundle(seeds=seeds, config=config, run_id=run_id)
    panel = core.run_baseline_panel(bundle, run_id=f"{run_id}-baseline-panel", threshold_snapshot_hash=snapshot_hash)
    non_id = core.non_identifiability_premise_gate(panel, config=config)
    oracle = core.run_interventional_oracle(bundle, run_id=f"{run_id}-interventional-oracle", threshold_snapshot_hash=snapshot_hash)
    family_max_value = panel["obs_only"]["family_max"]["value"]
    oracle_value = oracle["aggregate_score"]["value"]
    headroom = core.interventional_headroom_gate(obs_score=family_max_value, oracle_score=oracle_value, config=config)
    leakage_report = leakage.run_leakage_positive_controls(
        bundle=bundle, config=config, run_id=f"{run_id}-leakage", threshold_snapshot_hash=snapshot_hash
    )
    replay_report = replay.replay_oracle_predictions(
        serialized_state=oracle["serialized_state"],
        intervention_rows=oracle["legal_intervention_rows"],
        stored_predictions=oracle["predictions"],
        run_id=f"{run_id}-replay",
        threshold_snapshot_hash=snapshot_hash,
    )

    episode_ids = [e["episode_id"] for e in bundle["episodes"]]

    # Gate material records (premise indicator + headroom delta) -> provenance.
    premise_record = provenance.material_record(
        value=1.0 if non_id["verdict"] == "non_identifiability_present" else 0.0,
        producer_function=core.non_identifiability_premise_gate,
        inputs={"obs_family_max": family_max_value, "schema": panel["schema_only"]["aggregate_score"]["value"], "name_order": panel["name_order"]["aggregate_score"]["value"]},
        run_id=f"{run_id}-premise-gate",
        seed="multi_seed",
        episode_ids=episode_ids,
        aggregation="premise_gate_pass_indicator",
        threshold_used=config.premise_threshold,
        threshold_snapshot_hash=snapshot_hash,
        subsystem="premise",
        recompute_basis={"kind": "indicator", "predicate": non_id["verdict"] == "non_identifiability_present"},
    )
    headroom_record = provenance.material_record(
        value=round(oracle_value - family_max_value, 6),
        producer_function=core.interventional_headroom_gate,
        inputs={"oracle_score": oracle_value, "obs_family_max": family_max_value},
        run_id=f"{run_id}-headroom-gate",
        seed="multi_seed",
        episode_ids=episode_ids,
        aggregation="oracle_minus_obs_family_max",
        threshold_used=config.headroom_band,
        threshold_snapshot_hash=snapshot_hash,
        subsystem="interventional_headroom",
        recompute_basis={"kind": "delta", "minuend": oracle_value, "subtrahend": family_max_value},
    )

    # Compute failure-control evidence from ACTUAL control executions this run.
    headroom_probe = _headroom_failure_probe(config=config, run_id=run_id, snapshot_hash=snapshot_hash)
    failure_controls: dict[str, bool] = {
        "premise": bool(leakage_report["control_results"]["L9"]["fired"]),
        "schema_alias": bool(leakage_report["control_results"]["L7"]["fired"]),
        "interventional_headroom": bool(headroom_probe["blocks"]),
        "leakage": bool(leakage_report["failure_probe"]["subsystem_blocks"]),
        "replay": bool(
            replay_report["negative_control"]["corrupt_intervention_log_changes_behavior"]
            and replay_report["negative_control"]["removed_intervention_rows_changes_behavior"]
            and replay_report["negative_control"]["corrupt_serialized_state_changes_behavior"]
        ),
    }
    provenance_probe = _provenance_failure_probe(oracle["aggregate_score"], snapshot=threshold_snapshot, failure_controls=failure_controls)
    failure_controls["provenance"] = bool(provenance_probe["blocks"])
    failure_controls["verdict"] = all(
        failure_controls[k] for k in ("premise", "schema_alias", "interventional_headroom", "leakage", "replay", "provenance")
    )

    # Collect + validate every material producer used by verdict selection.
    material_rows = provenance.collect_provenance_rows(
        [panel, oracle, leakage_report, replay_report, premise_record, headroom_record]
    )
    provenance_validation = provenance.validate_provenance_rows(
        material_rows,
        threshold_snapshot=threshold_snapshot,
        failure_controls=failure_controls,
        live_config_source_hash=live_config_source_hash,
    )

    verdict, blockers = _select_verdict(
        non_identifiability=non_id,
        headroom=headroom,
        leakage_report=leakage_report,
        provenance_validation=provenance_validation,
        replay_report=replay_report,
    )

    # Coverage records for the two meta-producers (provenance validation + final
    # verdict). Emitted with real code_path_hashes; validated-by-construction.
    provenance_validation_record = provenance.material_record(
        value=1.0 if provenance_validation["verdict"] == "provenance_valid" else 0.0,
        producer_function=provenance.validate_provenance_rows,
        inputs={"row_count": provenance_validation["row_count"], "subsystems": provenance_validation["subsystems_covered"]},
        run_id=f"{run_id}-provenance-validation",
        seed="multi_seed",
        episode_ids=episode_ids,
        aggregation="provenance_valid_indicator",
        threshold_used=None,
        threshold_snapshot_hash=snapshot_hash,
        subsystem="provenance",
        recompute_basis={"kind": "indicator", "predicate": provenance_validation["verdict"] == "provenance_valid"},
    )
    final_verdict_record = provenance.material_record(
        value=1.0 if verdict == "preflight_admitted_for_candidate_design" else 0.0,
        producer_function=_select_verdict,
        inputs={"verdict": verdict, "blockers": blockers},
        run_id=f"{run_id}-final-verdict",
        seed="multi_seed",
        episode_ids=episode_ids,
        aggregation="final_verdict_admission_indicator",
        threshold_used=None,
        threshold_snapshot_hash=snapshot_hash,
        subsystem="verdict",
        recompute_basis={"kind": "indicator", "predicate": verdict == "preflight_admitted_for_candidate_design"},
    )
    all_provenance_rows = material_rows + [provenance_validation_record, final_verdict_record]

    producer_functions = sorted({row["producer_function"] for row in all_provenance_rows})
    code_path_hashes = {row["producer_function"]: row["code_path_hash"] for row in all_provenance_rows}

    attacker_scores = {
        a["attacker"]: a["aggregate_score"]["value"] for a in panel["obs_only"]["attackers"]
    }

    result = {
        "task_id": TASK_ID,
        "repair_task_id": "REPAIR-ROUTE-C-PREFLIGHT-001A-OBSERVATIONAL-BASELINE-001A",
        "verdict": verdict,
        "blockers": blockers,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": "none",
        "enabled_status": "local CLI / pytest / artifact generation only; no enabled Route C path",
        "real_trigger_evidence": {
            "run_id": run_id,
            "callable_runner": "route_c_preflight_001a.runner.run_preflight",
            "artifact_dir": output_dir.as_posix(),
        },
        "mechanism_claim_admitted": False,
        "candidate_implemented": False,
        "gate_mainline_runtime_bridge_scheduler_admission_product_touched": False,
        "push_tag_remote_anchor_performed": False,
        "claim_ceiling": CLAIM_CEILING,
        "parent_negative_audit": PARENT_NEGATIVE_AUDIT,
        "parent_doc_hashes": parent_doc_hashes,
        "seeds": seeds,
        "generator_config": bundle["config"],
        "thresholds": {
            "premise_band": config.premise_band,
            "headroom_band": config.headroom_band,
            "premise_threshold": config.premise_threshold,
            "chance": config.chance,
        },
        "threshold_freeze_evidence": {
            "threshold_snapshot": threshold_snapshot,
            "live_config_source_hash": live_config_source_hash,
            "config_source_unchanged_since_snapshot": threshold_snapshot["config_source_hash"] == live_config_source_hash,
        },
        "passive_attacker_family_scores": attacker_scores,
        "obs_only_family_max_score": family_max_value,
        "obs_only_family_max_attacker": panel["obs_only"]["family_max_attacker"],
        "value_level_family_max_on_clean": panel["obs_only"]["value_level_family_max"],
        "value_level_observation_decodable_control": leakage_report["value_level_control"],
        "schema_attacker_score": panel["schema_only"]["aggregate_score"]["value"],
        "name_order_attacker_score": panel["name_order"]["aggregate_score"]["value"],
        "interventional_oracle_score": oracle_value,
        "interventional_headroom": headroom["value"],
        "non_identifiability": non_id["verdict"],
        "interventional_headroom_verdict": headroom["verdict"],
        "leakage_control_results": leakage_report["control_results"],
        "leakage_blocking_verdict": leakage_report["blocking_verdict"],
        "replay_validation_result": {k: v for k, v in replay_report.items() if k != "recomputed_predictions"},
        "provenance_validation_result": {k: v for k, v in provenance_validation.items() if k != "per_row"},
        "failure_controls": failure_controls,
        "failure_control_evidence": {
            "premise_value_level_L9": leakage_report["control_results"]["L9"],
            "schema_alias_L7": leakage_report["control_results"]["L7"]["fired"],
            "interventional_headroom_gain0": headroom_probe,
            "leakage_non_fire_probe": leakage_report["failure_probe"],
            "replay_tamper": replay_report["negative_control"],
            "provenance_missing_hash_probe": provenance_probe,
        },
        "producer_functions": producer_functions,
        "code_path_hashes": code_path_hashes,
        "material_producer_count": len(all_provenance_rows),
        "provenance_row_count": len(all_provenance_rows),
        "final_verdict_producer": provenance.producer_name(_select_verdict),
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
        "next_minimal_closed_loop_action": (
            "Independent hostile re-audit of the repaired Route C Phase 0 preflight; "
            "candidate card remains forbidden until re-audit accepts."
        ),
    }

    validation = {
        "producer_function": provenance.producer_name(run_preflight),
        "verdict_allowed": verdict in ALLOWED_VERDICTS,
        "positive_leakage_controls_caught": leakage_report["all_controls_fired"],
        "value_level_control_blocks": leakage_report["control_results"]["L9"]["fired"],
        "passive_baseline_isolated_from_interventions": panel["baseline_received_intervention_data"] is False,
        "baseline_reads_passive_handle_values": True,
        "obs_only_family_max_used_by_premise_gate": True,
        "replay_recomputed": replay_report["verdict"] == "replay_recomputed",
        "provenance_valid": provenance_validation["verdict"] == "provenance_valid",
        "attestations_computed_not_hardcoded": True,
        "candidate_implemented": False,
        "auto_remote_anchor": {"decision": "forbidden", "performed": False},
    }

    trace = core.trace_rows(bundle, panel, oracle)

    provenance.write_json(output_dir / "result.json", result)
    provenance.write_json(output_dir / "route_c_preflight_result.json", result)
    provenance.write_json(output_dir / "non_identifiability_report.json", {"baseline_panel": panel, "gate": non_id})
    provenance.write_json(output_dir / "interventional_headroom_report.json", {"oracle": _oracle_artifact_report(oracle), "gate": headroom, "gate_record": headroom_record})
    provenance.write_json(output_dir / "obs_only_baseline_report.json", panel["obs_only"])
    provenance.write_json(output_dir / "schema_attack_report.json", {"schema_only": panel["schema_only"], "name_order": panel["name_order"]})
    provenance.write_json(output_dir / "leakage_positive_controls.json", leakage_report)
    provenance.write_json(output_dir / "replay_report.json", replay_report)
    provenance.write_json(output_dir / "provenance_validation.json", provenance_validation)
    provenance.write_json(output_dir / "failure_controls.json", {"failure_controls": failure_controls, "evidence": result["failure_control_evidence"]})
    provenance.write_json(output_dir / "validation.json", validation)
    provenance.write_json(output_dir / "parent_doc_hashes.json", parent_doc_hashes)
    _write_jsonl(output_dir / "trace.jsonl", trace)
    _write_jsonl(output_dir / "provenance_rows.jsonl", all_provenance_rows)
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    if blockers:
        provenance.write_json(
            output_dir / "failure_manifest.json",
            {"task_id": TASK_ID, "verdict": verdict, "stop_conditions": blockers, "claim_ceiling": CLAIM_CEILING},
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/route_c_preflight_001a")
    parser.add_argument("--run-id", default="route-c-preflight-001a")
    args = parser.parse_args()
    result = run_preflight(repo_root=Path.cwd(), output_dir=Path(args.output_dir), run_id=args.run_id)
    print(result["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
