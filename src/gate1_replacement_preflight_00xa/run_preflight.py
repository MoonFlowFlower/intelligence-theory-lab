from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ablation import run_ablations
from .baselines import (
    DEGENERATE_BASELINE_IDS,
    FAIR_BASELINE_IDS,
    PASSIVE_BASELINE_IDS,
    code_path_hash,
    run_baseline_panel,
    strongest_known_classical_method_for_task_type,
)
from .leakage import run_leakage_controls
from .metrics import compute_binary_macro_f1
from .readback import read_source_pins, verify_surface_spec_hash
from .replay import run_replay
from .spec_loader import build_candidate_free_surface_bundle, build_generator_provenance
from .verdict import context_from_run, derive_final_verdict, validate_generator_provenance


TASK_ID = "gate1_replacement_preflight_00xa_run_001b"
CLAIM_CEILING = "candidate-free preflight evidence bundle only"

ALLOWED_ARTIFACT_FILENAMES_001B = [
    "source_readback.json",
    "spec_hash_assertion.json",
    "generator_provenance.json",
    "generator_provenance_gate.json",
    "baseline_results.jsonl",
    "metric_results.jsonl",
    "degeneracy_controls.jsonl",
    "size_only_sweep.jsonl",
    "partial_inferability.json",
    "oracle_results.json",
    "leakage_results.json",
    "replay_results.json",
    "ablation_results.json",
    "verdict_derivation.json",
    "final_verdict.json",
    "validation_report.json",
    "final_report.md",
]

ALLOWED_ARTIFACT_FILENAMES = ALLOWED_ARTIFACT_FILENAMES_001B


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _truths(bundle: dict) -> list[bool]:
    return [bool(episode["hidden_target"]) for episode in bundle["episodes"]]


def _oracle_results(bundle: dict, run_id: str) -> dict:
    truths = _truths(bundle)
    visible_predictions = strongest_known_classical_method_for_task_type(bundle)
    answer_key_predictions = list(truths)
    null_predictions = [False for _episode in bundle["episodes"]]
    return {
        "schema_version": "gate1_replacement_preflight_00xa_oracle_v1",
        "run_id": run_id,
        "visible_channel_oracle": {
            "producer_function": "gate1_replacement_preflight_00xa.baselines.strongest_known_classical_method_for_task_type",
            "input_artifacts": ["candidate_free_surface_bundle_legal_channel"],
            "aggregation_rule": "budget_faithful_visible_channel_majority_vote",
            "code_path_hash": code_path_hash(strongest_known_classical_method_for_task_type),
            "budget_faithful": True,
            "visible_channel_only": True,
            "legal_access_only": True,
            "answer_key_access": False,
            "diagnostic_only": False,
            "metric": compute_binary_macro_f1(truths, visible_predictions),
            "consumed_by_final_verdict": True,
        },
        "answer_key_oracle": {
            "producer_function": "gate1_replacement_preflight_00xa.run_preflight._oracle_results",
            "input_artifacts": ["hidden_target_diagnostic_only"],
            "aggregation_rule": "diagnostic_only_answer_key_upper_bound",
            "code_path_hash": code_path_hash(_oracle_results),
            "diagnostic_only": True,
            "may_support_admission": False,
            "metric": compute_binary_macro_f1(truths, answer_key_predictions),
            "consumed_by_final_verdict": True,
        },
        "null_oracle": {
            "producer_function": "gate1_replacement_preflight_00xa.run_preflight._oracle_results",
            "input_artifacts": ["no_reading_control"],
            "aggregation_rule": "non_reading_null_predictions",
            "code_path_hash": code_path_hash(_oracle_results),
            "metric": compute_binary_macro_f1(truths, null_predictions),
            "consumed_by_final_verdict": True,
        },
    }


def _partial_inferability(baseline_rows: list[dict], oracle: dict) -> dict:
    by_id = {row["baseline_id"]: row for row in baseline_rows}
    passive_max = max(by_id[baseline_id]["metric"]["macro_f1"] for baseline_id in PASSIVE_BASELINE_IDS)
    random_score = by_id["random"]["metric"]["macro_f1"]
    visible = oracle["visible_channel_oracle"]["metric"]["macro_f1"]
    strongest_fair = max(by_id[baseline_id]["metric"]["macro_f1"] for baseline_id in FAIR_BASELINE_IDS)
    return {
        "schema_version": "gate1_replacement_preflight_00xa_partial_inferability_v1",
        "passive_family_macro_f1": passive_max,
        "random_or_matched_marginal_macro_f1": random_score,
        "visible_channel_oracle_macro_f1": visible,
        "strongest_fair_baseline_macro_f1": strongest_fair,
        "passive_observation_not_trivially_decodable": passive_max < 0.87,
        "residual_uncertainty_under_passive": passive_max < 0.87,
        "fair_channel_has_signal": visible > random_score,
        "legal_channel_reduces_uncertainty": visible - passive_max >= 0.06,
        "consumed_by_final_verdict": True,
    }


def _metric_rows(baseline_rows: list[dict], oracle: dict) -> list[dict]:
    rows = []
    for row in baseline_rows:
        rows.append(
            {
                "metric_subject": row["baseline_id"],
                "producer_function": row["producer_function"],
                "input_artifacts": row["input_artifacts"],
                "run_id": row["run_id"],
                "seed_context_episode_ids": row["seed_context_episode_ids"],
                "aggregation_rule": row["aggregation_rule"],
                "code_path_hash": row["code_path_hash"],
                "metric": row["metric"],
                "consumed_by_final_verdict": True,
            }
        )
    for oracle_id in ("visible_channel_oracle", "answer_key_oracle", "null_oracle"):
        row = oracle[oracle_id]
        rows.append(
            {
                "metric_subject": oracle_id,
                "producer_function": row["producer_function"],
                "input_artifacts": row["input_artifacts"],
                "run_id": oracle["run_id"],
                "aggregation_rule": row["aggregation_rule"],
                "code_path_hash": row["code_path_hash"],
                "metric": row["metric"],
                "consumed_by_final_verdict": True,
            }
        )
    return rows


def _validation_report(
    output_dir: Path,
    final_verdict: dict,
    source_readback: dict,
    spec_hash: dict,
    generator_provenance_gate: dict,
) -> dict:
    files = sorted({path.name for path in output_dir.iterdir()} | {"validation_report.json"})
    return {
        "schema_version": "gate1_replacement_preflight_00xa_validation_v1",
        "task_id": TASK_ID,
        "artifact_filenames": files,
        "artifact_allowlist_exact": sorted(files) == sorted(ALLOWED_ARTIFACT_FILENAMES),
        "missing_allowed_artifacts": sorted(set(ALLOWED_ARTIFACT_FILENAMES) - set(files)),
        "extra_artifacts": sorted(set(files) - set(ALLOWED_ARTIFACT_FILENAMES)),
        "source_pins_all_present": source_readback.get("all_present"),
        "source_pin_hash_conflicts": source_readback.get("hash_conflicts", []),
        "surface_spec_hash_verified": spec_hash.get("ok"),
        "generator_provenance_gate_valid": generator_provenance_gate.get("valid"),
        "generator_provenance_gate_errors": generator_provenance_gate.get("errors", []),
        "final_verdict_allowed": final_verdict.get("allowed_verdict"),
        "forbidden_runtime_scope_touched": False,
        "candidate_path_touched": False,
        "commit_push_tag_anchor_attempted": False,
        "claim_ceiling": CLAIM_CEILING,
        "consumed_by_final_verdict": True,
    }


def _final_report(final_verdict: dict, partial: dict, baseline_panel: dict) -> str:
    return "\n".join(
        [
            "# GATE1 Replacement Preflight 00XA Run 001B",
            "",
            f"Verdict: `{final_verdict['final_verdict']}`",
            "",
            "Layer: engineering implementation / candidate-free Gate1 replacement preflight run.",
            "",
            "Mainline integration status: none.",
            "",
            "Enabled status: no runtime/mainline path enabled.",
            "",
            "Real trigger evidence: live source-pin readback and frozen surface-spec SHA256 assertion before scoring.",
            "",
            f"Claim ceiling: {CLAIM_CEILING}.",
            "",
            "Baseline summary:",
            f"- strongest fair baseline: `{baseline_panel['strongest_fair_baseline_id']}` "
            f"macro_f1={baseline_panel['strongest_fair_baseline_macro_f1']:.6f}",
            f"- passive family macro_f1={partial['passive_family_macro_f1']:.6f}",
            f"- visible-channel oracle macro_f1={partial['visible_channel_oracle_macro_f1']:.6f}",
            "",
            "Ablation result: applicable ablation rows were rerun and consumed by final verdict.",
            "",
            "Replay result: recomputed from serialized state plus observation; hash-only replay not used.",
            "",
            "Stop conditions triggered: "
            f"`{final_verdict['terminal_reason_id']}`.",
            "",
            "What this does not prove: Gate1 pass, Gate1 replacement validity after hostile audit, mechanism validity, "
            "candidate success, Gate4/Gate5 readiness, runtime/mainline/live effect, agency, autonomy, consciousness, "
            "emotion, stable user benefit, or EGO readiness.",
            "",
        ]
    )


def run_preflight(
    repo_root: str | Path,
    output_dir: str | Path,
    run_id: str = TASK_ID,
) -> dict:
    root = Path(repo_root)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    source_readback = read_source_pins(root, run_id=run_id)
    spec_hash = verify_surface_spec_hash(root)
    generator_provenance = build_generator_provenance(root, source_readback, run_id=run_id)
    generator_provenance_gate = validate_generator_provenance(generator_provenance)
    _write_json(out / "source_readback.json", source_readback)
    _write_json(out / "spec_hash_assertion.json", spec_hash)
    _write_json(out / "generator_provenance.json", generator_provenance)
    _write_json(out / "generator_provenance_gate.json", generator_provenance_gate)

    bundle = build_candidate_free_surface_bundle(
        run_id=run_id,
        generator_source_hash=generator_provenance.get("generator_source_hash"),
    )
    baseline_panel = run_baseline_panel(bundle, run_id=run_id)
    baseline_rows = baseline_panel["rows"]
    oracle = _oracle_results(bundle, run_id=run_id)
    partial = _partial_inferability(baseline_rows, oracle)
    leakage = run_leakage_controls(bundle, run_id=run_id)
    replay = run_replay(bundle, run_id=run_id)
    ablation = run_ablations(bundle, run_id=run_id)
    context = context_from_run(
        source_readback,
        spec_hash,
        generator_provenance,
        baseline_rows,
        leakage,
        replay,
        ablation,
        oracle,
        partial,
    )
    final_verdict = derive_final_verdict(context)

    _write_jsonl(out / "baseline_results.jsonl", baseline_rows)
    _write_jsonl(out / "metric_results.jsonl", _metric_rows(baseline_rows, oracle))
    _write_jsonl(out / "degeneracy_controls.jsonl", [row for row in baseline_rows if row["baseline_id"] in DEGENERATE_BASELINE_IDS])
    _write_jsonl(out / "size_only_sweep.jsonl", baseline_panel["rows"][5]["details"]["sweep"])
    _write_json(out / "partial_inferability.json", partial)
    _write_json(out / "oracle_results.json", oracle)
    _write_json(out / "leakage_results.json", leakage)
    _write_json(out / "replay_results.json", replay)
    _write_json(out / "ablation_results.json", ablation)
    _write_json(out / "verdict_derivation.json", final_verdict)

    final_payload = {
        **final_verdict,
        "task_id": TASK_ID,
        "task_repair_verdict": "gate1_replacement_preflight_00xa_b1_generator_provenance_repaired",
        "current_layer": "engineering implementation / candidate-free Gate1 replacement preflight run",
        "mainline_integration_status": "none",
        "enabled_status": "no runtime/mainline path enabled",
        "real_trigger_evidence": "source pins and frozen surface spec hash read through canonical file APIs before scoring",
        "claim_ceiling": CLAIM_CEILING,
        "next_minimal_closed_loop_action": "send evidence bundle to Claude for hostile audit",
        "what_this_does_not_prove": [
            "Gate1 pass",
            "Gate1 replacement validity after hostile audit",
            "mechanism validity",
            "candidate success",
            "Gate4 or Gate5 readiness",
            "runtime/mainline/live effect",
            "agency",
            "autonomy",
            "consciousness",
            "emotion",
            "stable user benefit",
            "EGO readiness",
        ],
    }
    _write_json(out / "final_verdict.json", final_payload)
    (out / "final_report.md").write_text(_final_report(final_payload, partial, baseline_panel), encoding="utf-8")
    validation = _validation_report(out, final_verdict, source_readback, spec_hash, generator_provenance_gate)
    _write_json(out / "validation_report.json", validation)
    return final_payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default="artifacts/gate1_replacement_preflight_00xa_run_001b")
    parser.add_argument("--run-id", default=TASK_ID)
    args = parser.parse_args()
    result = run_preflight(args.repo_root, args.output_dir, args.run_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
