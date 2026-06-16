from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from . import CLAIM_CEILING, CURRENT_LAYER, TASK_ID, WHAT_THIS_DOES_NOT_PROVE
from . import core, leakage, provenance, replay


DEFAULT_SEEDS = tuple(range(1600, 1632))
BLUEPRINT = Path("docs/research/ROUTE-C-PREFLIGHT-001A-HOSTILE-DESIGN-BLUEPRINT.md")
TASK_CARD = Path("docs/codex/tasks/ROUTE-C-PREFLIGHT-001A.md")
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


def _write_trace(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _write_provenance(path: Path, rows: list[dict[str, Any]]) -> None:
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


def _select_verdict(
    *,
    non_identifiability: dict[str, Any],
    headroom: dict[str, Any],
    leakage_report: dict[str, Any],
    provenance_validation: dict[str, Any],
    replay_report: dict[str, Any],
) -> tuple[str, list[str]]:
    blockers = []
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
    parent_doc_hashes = _doc_hashes(repo_root)
    bundle = core.build_episode_bundle(seeds=seeds, config=config, run_id=run_id)
    panel = core.run_baseline_panel(bundle, run_id=f"{run_id}-baseline-panel")
    non_id = core.non_identifiability_premise_gate(panel, config=config)
    oracle = core.run_interventional_oracle(bundle, run_id=f"{run_id}-interventional-oracle")
    headroom = core.interventional_headroom_gate(
        obs_score=panel["obs_only"]["aggregate_score"]["value"],
        oracle_score=oracle["aggregate_score"]["value"],
        config=config,
    )
    leakage_report = leakage.run_leakage_positive_controls(bundle=bundle, config=config, run_id=f"{run_id}-leakage")
    replay_report = replay.replay_oracle_predictions(
        serialized_state=oracle["serialized_state"],
        intervention_rows=oracle["legal_intervention_rows"],
        stored_predictions=oracle["predictions"],
        run_id=f"{run_id}-replay",
    )
    artifacts_for_provenance = [panel, oracle]
    provenance_rows = provenance.collect_provenance_rows(artifacts_for_provenance)
    provenance_validation = provenance.validate_provenance_rows(provenance_rows)
    verdict, blockers = _select_verdict(
        non_identifiability=non_id,
        headroom=headroom,
        leakage_report=leakage_report,
        provenance_validation=provenance_validation,
        replay_report=replay_report,
    )
    trace = core.trace_rows(bundle, panel, oracle)
    result = {
        "task_id": TASK_ID,
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
        "parent_doc_hashes": parent_doc_hashes,
        "seeds": list(seeds),
        "generator_config": bundle["config"],
        "producer_functions": sorted(
            {
                panel["obs_only"]["aggregate_score"]["producer_function"],
                panel["schema_only"]["aggregate_score"]["producer_function"],
                panel["name_order"]["aggregate_score"]["producer_function"],
                oracle["aggregate_score"]["producer_function"],
                leakage_report["producer_function"],
                replay_report["producer_function"],
            }
        ),
        "code_path_hashes": {
            "obs_only_baseline": panel["obs_only"]["aggregate_score"]["code_path_hash"],
            "schema_only_attacker": panel["schema_only"]["aggregate_score"]["code_path_hash"],
            "name_order_attacker": panel["name_order"]["aggregate_score"]["code_path_hash"],
            "interventional_oracle": oracle["aggregate_score"]["code_path_hash"],
        },
        "passive_baseline_score": panel["obs_only"]["aggregate_score"]["value"],
        "schema_attacker_score": panel["schema_only"]["aggregate_score"]["value"],
        "name_order_attacker_score": panel["name_order"]["aggregate_score"]["value"],
        "interventional_oracle_score": oracle["aggregate_score"]["value"],
        "interventional_headroom": headroom["value"],
        "non_identifiability": non_id["verdict"],
        "interventional_headroom_verdict": headroom["verdict"],
        "leakage_control_results": leakage_report["control_results"],
        "provenance_validation_result": provenance_validation,
        "replay_validation_result": replay_report,
        "thresholds_frozen_before_run": True,
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
        "next_minimal_closed_loop_action": (
            "Run independent hostile audit against the generated Phase 0 artifacts before any Route C candidate card."
        ),
    }
    validation = {
        "producer_function": provenance.producer_name(run_preflight),
        "verdict_allowed": verdict in ALLOWED_VERDICTS,
        "positive_leakage_controls_caught": leakage_report["all_controls_fired"],
        "passive_baseline_isolated_from_interventions": panel["baseline_received_intervention_data"] is False,
        "replay_recomputed": replay_report["verdict"] == "replay_recomputed",
        "provenance_valid": provenance_validation["verdict"] == "provenance_valid",
        "candidate_implemented": False,
        "auto_remote_anchor": {"decision": "forbidden", "performed": False},
    }
    provenance.write_json(output_dir / "result.json", result)
    provenance.write_json(output_dir / "route_c_preflight_result.json", result)
    provenance.write_json(output_dir / "non_identifiability_report.json", {"baseline_panel": panel, "gate": non_id})
    provenance.write_json(output_dir / "interventional_headroom_report.json", {"oracle": _oracle_artifact_report(oracle), "gate": headroom})
    provenance.write_json(output_dir / "obs_only_baseline_report.json", panel["obs_only"])
    provenance.write_json(
        output_dir / "schema_attack_report.json",
        {"schema_only": panel["schema_only"], "name_order": panel["name_order"]},
    )
    provenance.write_json(output_dir / "leakage_positive_controls.json", leakage_report)
    provenance.write_json(output_dir / "replay_report.json", replay_report)
    provenance.write_json(output_dir / "validation.json", validation)
    provenance.write_json(output_dir / "parent_doc_hashes.json", parent_doc_hashes)
    _write_trace(output_dir / "trace.jsonl", trace)
    _write_provenance(output_dir / "provenance_rows.jsonl", provenance_rows)
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    if blockers:
        provenance.write_json(
            output_dir / "failure_manifest.json",
            {
                "task_id": TASK_ID,
                "verdict": verdict,
                "stop_conditions": blockers,
                "claim_ceiling": CLAIM_CEILING,
            },
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
