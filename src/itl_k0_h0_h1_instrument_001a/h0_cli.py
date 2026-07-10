from __future__ import annotations

import argparse
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .h0_freeze import (
    FREEZE_PATHS,
    SOURCE_PATHS,
    TASK_CARD_PIN,
    TEST_PATHS,
    generate_freeze_files,
    verify_freeze_files,
)
from .h0_registry import all_atomic_specs, build_registry
from .h0_schema import H0Registry
from .h0_validation import (
    attach_provenance,
    code_path_hash,
    file_hashes,
    run_ablation_catalog,
    run_baseline_comparison,
    run_metamorphic_validation,
    run_mutation_validation,
    run_path_authority,
    run_permutation_validation,
    run_semantic_recompute_replay,
    run_semantic_validation,
)


PHASE_D_FILENAMES = (
    "result.json",
    "atomic_specs.json",
    "semantic_validation_report.json",
    "permutation_report.json",
    "mutation_report.json",
    "metamorphic_report.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "path_authority_report.json",
    "computed_evidence_provenance.json",
    "replay_report.json",
    "trace.jsonl",
    "failure_manifest.json",
)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _git(repo_root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo_root, text=True, capture_output=True, check=True).stdout.strip()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain an object")
    return payload


def freeze_command(args: argparse.Namespace) -> int:
    repo_root = Path(args.root).resolve()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = repo_root / output_dir
    manifest = generate_freeze_files(repo_root, output_dir)
    print(json.dumps({"task_id": manifest["task_id"], "normative_field_count": manifest["normative_field_count"], "scenario_count": manifest["scenario_count"], "permutation_count": manifest["permutation_count"], "freeze_manifest": str(output_dir / "freeze_manifest.json")}, indent=2, sort_keys=True))
    return 0


def prebank_run(args: argparse.Namespace) -> int:
    repo_root = Path(args.root).resolve()
    freeze_path = Path(args.freeze_manifest)
    if not freeze_path.is_absolute():
        freeze_path = repo_root / freeze_path
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = repo_root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    existing = [name for name in PHASE_D_FILENAMES if (output_dir / name).exists()]
    if existing:
        raise RuntimeError(f"official prebank outputs already exist; rerun forbidden: {existing}")

    freeze_check = verify_freeze_files(repo_root, freeze_path)
    if not freeze_check["passed"]:
        raise RuntimeError(f"freeze verification failed: {freeze_check}")
    manifest = freeze_check["manifest"]
    if manifest["task_card_pin"] != TASK_CARD_PIN:
        raise RuntimeError("task-card pin mismatch")
    head = _git(repo_root, "rev-parse", "HEAD")
    if _git(repo_root, "merge-base", "--is-ancestor", TASK_CARD_PIN["bank_commit"], head):
        pass
    path_report_raw = run_path_authority(repo_root, manifest)
    if not path_report_raw["worktree_clean_before_official_outputs"]:
        raise RuntimeError(f"official run requires a clean worktree/index: {path_report_raw['worktree_status']}")

    run_id = f"itl-k0-h0-code-first-prebank-001a-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    input_paths = SOURCE_PATHS + TEST_PATHS + FREEZE_PATHS + [TASK_CARD_PIN["card_path"]]
    input_hashes = file_hashes(repo_root, input_paths)
    source_test_hashes = file_hashes(repo_root, SOURCE_PATHS + TEST_PATHS)
    run_context = {
        "run_id": run_id,
        "input_hashes": input_hashes,
        "source_test_hashes": source_test_hashes,
        "code_path_hash": code_path_hash(repo_root, SOURCE_PATHS),
        "task_card_pin": TASK_CARD_PIN,
        "seed_context_episode_ids": {"permutation_seed": 9173, "context_id": "H0_SEMANTIC_PREBANK", "episode_ids": [], "mechanism_episode_run": False},
        "aggregation_rule": "CODE_FIRST_PREBANK_VALIDATED iff every frozen semantic, permutation, mutation, metamorphic, baseline, ablation, path-authority, freeze, provenance, and semantic-recompute gate passes while H0/formal execution remain false",
    }

    registry = H0Registry.from_dict(manifest["registry"])
    registry_payload = registry.to_dict()
    normative = _load_json(output_dir / "normative_field_manifest.json")
    transformations = _load_json(output_dir / "transformation_catalog.json")
    baseline_contract = _load_json(output_dir / "baseline_ablation_contract.json")
    scenarios = transformations["scenarios"]
    permutations = transformations["permutations"]

    semantic_raw = run_semantic_validation(registry, scenarios)
    permutation_raw = run_permutation_validation(permutations)
    mutation_raw = run_mutation_validation(registry_payload, normative)
    metamorphic_raw = run_metamorphic_validation(registry_payload, transformations)
    baseline_raw = run_baseline_comparison(registry_payload, normative, {"transformations": transformations["transformations"], "baseline_ids": baseline_contract["baseline_ids"]}, scenarios)
    ablation_raw = run_ablation_catalog(registry_payload, registry, baseline_contract)
    replay_raw = run_semantic_recompute_replay(registry_payload, scenarios, semantic_raw)

    semantic = attach_provenance(semantic_raw, producer_function="run_semantic_validation", run_context=run_context, input_paths=input_paths, consumed_ids=[row["scenario_id"] for row in scenarios])
    permutation = attach_provenance(permutation_raw, producer_function="run_permutation_validation", run_context=run_context, input_paths=input_paths, consumed_ids=permutation_raw["consumed_ids"])
    mutation = attach_provenance(mutation_raw, producer_function="run_mutation_validation", run_context=run_context, input_paths=input_paths, consumed_ids=[row["mutation_id"] for row in mutation_raw["results"]])
    metamorphic = attach_provenance(metamorphic_raw, producer_function="run_metamorphic_validation", run_context=run_context, input_paths=input_paths, consumed_ids=[row["transformation_id"] for row in metamorphic_raw["results"]])
    baseline = attach_provenance(baseline_raw, producer_function="run_baseline_comparison", run_context=run_context, input_paths=input_paths, consumed_ids=[row["baseline_id"] for row in baseline_raw["results"]])
    ablation = attach_provenance(ablation_raw, producer_function="run_ablation_catalog", run_context=run_context, input_paths=input_paths, consumed_ids=[row["ablation_id"] for row in ablation_raw["results"]])
    path_report = attach_provenance(path_report_raw, producer_function="run_path_authority", run_context=run_context, input_paths=input_paths, consumed_ids=path_report_raw["changed_files_manifest"])
    replay = attach_provenance(replay_raw, producer_function="run_semantic_recompute_replay", run_context=run_context, input_paths=input_paths, consumed_ids=[row["scenario_id"] for row in scenarios])

    atomic_specs = attach_provenance({"task_id": manifest["task_id"], "registry_id": registry.registry_id, "atomic_spec_count": len(all_atomic_specs(registry)), "atomic_specs": [row.to_dict() for row in all_atomic_specs(registry)]}, producer_function="all_atomic_specs", run_context=run_context, input_paths=input_paths, consumed_ids=[row.atomic_contrast_id for row in all_atomic_specs(registry)])

    gates = {
        "primary_oracle_agreement": semantic["all_candidate_oracle_agree"] and semantic["all_expected_match"],
        "atomic_specs_complete": semantic["atomic_specs_complete"],
        "permutation_invariant": permutation["all_invariant"] and permutation["all_frozen_ids_consumed"],
        "normative_mutation_kill_rate_1": mutation["normative_mutation_kill_rate"] == 1.0 and mutation["all_manifest_ids_consumed"],
        "valid_metamorphic_accept_rate_1": metamorphic["valid_transformation_accept_rate"] == 1.0 and metamorphic["all_catalog_ids_consumed"],
        "baselines_do_not_match": baseline["all_baselines_invoked"] and baseline["no_baseline_matches_candidate"],
        "all_ablations_detected": ablation["all_frozen_ablations_consumed"] and ablation["all_ablations_detected"],
        "path_authority": path_report["passed"],
        "semantic_recompute_replay": replay["candidate_behavior_recomputed"] and replay["scenario_results_match"] and not replay["mechanism_episode_replay_run"],
        "freeze_hashes_match": freeze_check["passed"],
        "no_formal_h0_h1_k0r_freeze_run": True,
        "h0_remains_false": True,
    }
    verdict = "CODE_FIRST_PREBANK_VALIDATED" if all(gates.values()) else "CODE_FIRST_PREBANK_FAILED"
    result_raw = {
        "task_id": manifest["task_id"],
        "verdict": verdict,
        "gates": gates,
        "metrics": {
            "scenario_count": semantic["scenario_count"],
            "atomic_spec_count": atomic_specs["atomic_spec_count"],
            "permutation_count": len(permutation["results"]),
            "normative_mutation_kill_rate": mutation["normative_mutation_kill_rate"],
            "valid_transformation_accept_rate": metamorphic["valid_transformation_accept_rate"],
            "ablation_detected_count": sum(row["detected"] for row in ablation["results"]),
        },
        "phase_c_commit": head,
        "formal_h0_executed": False,
        "h0_authorized": False,
        "claim_ceiling": manifest["claim_ceiling"],
    }
    result = attach_provenance(result_raw, producer_function="aggregate_prebank_gates", run_context=run_context, input_paths=input_paths, consumed_ids=[*gates])
    provenance = {
        "task_id": manifest["task_id"],
        "producer_function": "build_computed_evidence_provenance",
        "run_id": run_id,
        "phase_c_commit": head,
        "input_artifacts": input_paths,
        "input_artifact_hashes": input_hashes,
        "source_test_hashes": source_test_hashes,
        "code_path_hash": run_context["code_path_hash"],
        "task_card_pin": TASK_CARD_PIN,
        "aggregation_rule": run_context["aggregation_rule"],
        "seed_context_episode_ids": run_context["seed_context_episode_ids"],
        "consumed_counts": {"scenarios": len(scenarios), "mutations": len(mutation["results"]), "transformations": len(metamorphic["results"]), "permutations": len(permutation["results"]), "baselines": len(baseline["results"]), "ablations": len(ablation["results"])},
        "unused_frozen_inputs": [],
        "external_write_manifest": [],
    }

    outputs = {
        "atomic_specs.json": atomic_specs,
        "semantic_validation_report.json": semantic,
        "permutation_report.json": permutation,
        "mutation_report.json": mutation,
        "metamorphic_report.json": metamorphic,
        "baseline_comparison.json": baseline,
        "ablation_report.json": ablation,
        "path_authority_report.json": path_report,
        "computed_evidence_provenance.json": provenance,
        "replay_report.json": replay,
        "result.json": result,
    }
    for filename, payload in outputs.items():
        _write_json(output_dir / filename, payload)
    trace_rows = [
        {"event": "official_prebank_started", "run_id": run_id, "phase_c_commit": head},
        *[{"event": "report_computed", "run_id": run_id, "report": filename, "producer_function": payload["producer_function"]} for filename, payload in outputs.items()],
        {"event": "official_prebank_completed", "run_id": run_id, "verdict": verdict, "gates": gates},
    ]
    (output_dir / "trace.jsonl").write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in trace_rows), encoding="utf-8")
    if verdict != "CODE_FIRST_PREBANK_VALIDATED":
        failure = attach_provenance({"task_id": manifest["task_id"], "verdict": verdict, "failed_gates": [key for key, passed in gates.items() if not passed], "rerun_authorized": False, "science_branch_action": "close_pending_operator_route_decision"}, producer_function="build_failure_manifest", run_context=run_context, input_paths=input_paths, consumed_ids=[key for key, passed in gates.items() if not passed])
        _write_json(output_dir / "failure_manifest.json", failure)

    print(json.dumps({"task_id": manifest["task_id"], "run_id": run_id, "verdict": verdict, "metrics": result["metrics"], "failed_gates": [key for key, passed in gates.items() if not passed]}, indent=2, sort_keys=True))
    return 0 if verdict == "CODE_FIRST_PREBANK_VALIDATED" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="h0_cli")
    sub = parser.add_subparsers(dest="command", required=True)
    freeze = sub.add_parser("freeze")
    freeze.add_argument("--root", default=".")
    freeze.add_argument("--output-dir", required=True)
    freeze.set_defaults(func=freeze_command)
    run = sub.add_parser("prebank-run")
    run.add_argument("--root", default=".")
    run.add_argument("--freeze-manifest", required=True)
    run.add_argument("--output-dir", required=True)
    run.set_defaults(func=prebank_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
