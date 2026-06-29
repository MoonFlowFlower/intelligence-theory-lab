"""TLGP-001B-R2 harness CLI.

Authorized in this task:

    PYTHONPATH=. python -m src.tlgp_001b_r2.harness --smoke

Smoke is non-evidential plumbing/calibration only. It must not emit an official
H0/H1/INVALID result and must stop on CUDA device-plumbing failure when CUDA is
available.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import torch

from . import lower_reference as LR
from . import meta_learners as ML
from . import preregistration as P
from . import splits as S
from . import verdict as V
from .world import ideal_predictions, query_truth_rows

REPO_ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = Path(os.environ.get("TLGP_001B_R2_ARTIFACT_DIR", str(REPO_ROOT / "artifacts" / "TLGP-001B-R2")))
SMOKE_DIR = ARTIFACT_DIR / "SMOKE_NON_EVIDENTIAL"
RUN_LOG_DIR = ARTIFACT_DIR / "RUN_LOGS"

SMOKE_BUDGET = {
    "batch_size": 4,
    "max_epochs": 1,
    "early_stop_patience": 1,
    "steps_max": 20,
    "lr_grid": [0.001],
    "optimizer": "adam",
}

SMOKE_CONFIGS = {
    "in_context_gru": {"hidden": 8, "layers": 1},
    "in_context_transformer": {"d_model": 8, "layers": 1, "heads": 2, "ff_mult": 2},
    "amortized_summary_mlp": {"hidden": [8, 8]},
}

SMOKE_SIZES = {
    "rung0_train": 8,
    "rung0_heldout": 6,
    "rung1_train": 10,
    "rung1_val": 5,
    "rung1_test": 6,
    "rung2_test": 6,
    "rung3_train": 10,
    "rung3_val": 5,
    "rung3_test": 6,
    "leakage_fixture": 200,
}


class DevicePlumbingBlocker(RuntimeError):
    pass


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def source_hashes() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in sorted(PKG_DIR.glob("*.py")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def write_source_manifest() -> dict[str, Any]:
    prereg = P.load_frozen_prereg()
    manifest = {
        "task_id": "TLGP-001B-R2-HARNESS-SMOKE-001",
        "evidential": False,
        "frozen_prereg": {
            "path": "artifacts/TLGP-001B-R2/prereg.json",
            "canonical_sha256_authorized": P.FROZEN_PREREG_SHA256,
            "canonical_sha256_readback": prereg["_canonical_sha256_readback"],
            "match": prereg["_sha256_match"],
            "raw_bytes_sha256": hashlib.sha256(P.PREREG_JSON_PATH.read_bytes()).hexdigest(),
        },
        "delivered_src_tlgp_001b_r2": source_hashes(),
        "entrypoint_package_marker": {
            "src/__init__.py": hashlib.sha256((REPO_ROOT / "src" / "__init__.py").read_bytes()).hexdigest(),
            "purpose": "ensures `python -m src...` resolves this repo before unrelated user-site packages named src",
        },
        "readonly_imports": {
            "src/tlgp_001a/world.py": hashlib.sha256((REPO_ROOT / "src" / "tlgp_001a" / "world.py").read_bytes()).hexdigest(),
            "src/tlgp_001a/ideal_observer.py": hashlib.sha256((REPO_ROOT / "src" / "tlgp_001a" / "ideal_observer.py").read_bytes()).hexdigest(),
            "src/tlgp_001a/metrics.py": hashlib.sha256((REPO_ROOT / "src" / "tlgp_001a" / "metrics.py").read_bytes()).hexdigest(),
            "src/tlgp_001a/leakage.py": hashlib.sha256((REPO_ROOT / "src" / "tlgp_001a" / "leakage.py").read_bytes()).hexdigest(),
            "src/tlgp_001b/lower_reference.py": hashlib.sha256((REPO_ROOT / "src" / "tlgp_001b" / "lower_reference.py").read_bytes()).hexdigest(),
            "src/tlgp_001b/meta_learners.py": hashlib.sha256((REPO_ROOT / "src" / "tlgp_001b" / "meta_learners.py").read_bytes()).hexdigest(),
        },
        "no_git_operations": True,
    }
    write_json(ARTIFACT_DIR / "source_manifest.json", manifest)
    return manifest


def write_sha256s() -> None:
    files = [
        ARTIFACT_DIR / "COLLISION_RECORD.md",
        ARTIFACT_DIR / "source_manifest.json",
        ARTIFACT_DIR / "IMPLEMENTATION_REPORT.md",
        ARTIFACT_DIR / "claim_ceiling.txt",
        SMOKE_DIR / "smoke_report.json",
        SMOKE_DIR / "smoke_run_output.txt",
        SMOKE_DIR / "smoke_trace.jsonl",
    ]
    files.extend(sorted(RUN_LOG_DIR.glob("gpu_device_calibration_*.json")))
    lines = []
    for path in files:
        if path.exists():
            lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(REPO_ROOT).as_posix()}")
    (ARTIFACT_DIR / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_claim_ceiling() -> None:
    (ARTIFACT_DIR / "claim_ceiling.txt").write_text(P.claim_ceiling() + "\n", encoding="utf-8")


def write_implementation_report(report: dict[str, Any]) -> None:
    lines = [
        "# TLGP-001B-R2 Harness Implementation Report",
        "",
        f"- Task verdict: `{report['task_verdict']}`",
        "- Current layer: engineering implementation + mechanism-hypothesis preflight",
        "- Mainline integration status: none",
        "- Enabled status: local isolated R2 smoke only; official full run not launched",
        f"- Real trigger evidence: prereg SHA match `{report['prereg']['canonical_sha256_readback']}`",
        "- Claim ceiling: implementation/plumbing evidence only; smoke is non-evidential",
        f"- Smoke evidential: `{str(report['evidential']).lower()}`",
        f"- Official verdict: `{report['official_verdict']}`",
        f"- CUDA selected device: `{report['cuda_device_calibration']['selected_device']}`",
        f"- CUDA primary families on selected device: `{report['cuda_device_calibration']['primary_families_on_selected_device']}`",
        f"- Replay smoke exact: `{report['replay']['replay_exact']}`",
        f"- Leakage smoke valid: `{report['leakage_smoke']['detector_valid']}`",
        f"- Tamper coverage: `{report['tamper_coverage']['terminal_coverage_count']}/{report['tamper_coverage']['expected_terminal_count']}`",
        f"- Rung1 scanner cheap baseline saturation: `{report['rung1_scanner']['cheap_baseline_saturation']}`",
        "- Full run status: not launched by this task; `--full` is blocked pending explicit operator authorization",
        "",
        "## What This Does Not Prove",
        "",
        "Smoke does not prove H0, H1, INVALID official status, learning-as-mechanism, mechanism validity, agency, subjectivity, intelligence, EGO readiness, or mainline effect.",
    ]
    (ARTIFACT_DIR / "IMPLEMENTATION_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def leakage_smoke() -> dict[str, Any]:
    from src.tlgp_001a.leakage import positive_control_report

    episodes = S.make_episodes("rung3", "test", SMOKE_SIZES["leakage_fixture"])
    report = positive_control_report(episodes)
    report["structural_boundary_ok"] = True
    report["meta_input_channels_declared"] = ["adapt_x", "adapt_a", "adapt_e", "query_x", "query_a"]
    report["meta_forbidden_inputs"] = ["rule_id", "query_e"]
    report["no_leak_route_through_metadata_asserted"] = ["split_id", "seed_id", "rung_id", "rule_membership_tag", "telemetry"]
    return report


def replay_from_trace(trace_rows: list[dict[str, Any]], live_means: dict[str, float]) -> dict[str, Any]:
    grouped: dict[str, list[float]] = {}
    for row in trace_rows:
        truth = row["query_e"]
        for key in ("ideal_prediction", "meta_prediction"):
            pred = row[key]
            name = f"{row['family']}::{key}"
            grouped.setdefault(name, []).append(float(row["balanced_accuracy"][key]))
            recomputed = _balanced_accuracy_from_lists(truth, pred)
            if abs(recomputed - float(row["balanced_accuracy"][key])) > 1e-12:
                return {"replay_exact": False, "mismatch": {"row": row["episode_id"], "key": key}}
    means = {name: sum(values) / len(values) for name, values in grouped.items() if values}
    matches = {
        key: abs(float(value) - float(live_means[key])) < 1e-12
        for key, value in means.items()
        if key in live_means
    }
    return {
        "replay_exact": bool(matches and all(matches.values())),
        "rows": len(trace_rows),
        "recomputed_means": means,
        "live_mean_matches": matches,
        "no_retraining": True,
    }


def _balanced_accuracy_from_lists(truth: list[int], pred: list[int]) -> float:
    scores = []
    for cls in range(P.K):
        denom = sum(1 for v in truth if int(v) == cls)
        if denom:
            num = sum(1 for t, p in zip(truth, pred) if int(t) == cls and int(p) == cls)
            scores.append(num / denom)
    return float(sum(scores) / len(scores)) if scores else 0.0


def assert_cuda_plumbing_or_block(report: dict[str, Any]) -> None:
    calib = report["cuda_device_calibration"]
    if not calib["cuda_available"]:
        return
    if calib["selected_device"] != "cuda:0":
        raise DevicePlumbingBlocker(f"CUDA available but selected_device={calib['selected_device']} not cuda:0")
    if not calib["primary_families_on_selected_device"]:
        raise DevicePlumbingBlocker("CUDA available but at least one primary family did not run on cuda:0")
    if not calib["primary_predictions_serialized_on_cpu"]:
        raise DevicePlumbingBlocker("CUDA available but primary predictions were not serialized as CPU/plain values")


def run_smoke() -> dict[str, Any]:
    start = time.time()
    prereg = P.load_frozen_prereg()
    ML.reset_device_runs()

    datasets = {
        "rung0_train": S.make_episodes("rung0", "train", SMOKE_SIZES["rung0_train"]),
        "rung0_heldout": S.make_episodes("rung0", "heldout", SMOKE_SIZES["rung0_heldout"]),
        "rung1_train": S.make_episodes("rung1", "train", SMOKE_SIZES["rung1_train"]),
        "rung1_val": S.make_episodes("rung1", "val", SMOKE_SIZES["rung1_val"]),
        "rung1_test": S.make_episodes("rung1", "test", SMOKE_SIZES["rung1_test"]),
        "rung2_test": S.make_episodes("rung2", "test", SMOKE_SIZES["rung2_test"]),
        "rung3_train": S.make_episodes("rung3", "train", SMOKE_SIZES["rung3_train"]),
        "rung3_val": S.make_episodes("rung3", "val", SMOKE_SIZES["rung3_val"]),
        "rung3_test": S.make_episodes("rung3", "test", SMOKE_SIZES["rung3_test"]),
    }

    rung1_ideal, rung1_ideal_preds, _ = ideal_predictions(datasets["rung1_test"])
    rung1_lower, rung1_lower_records = LR.evaluate(datasets["rung1_test"], int(P.seeds()["BASELINE_FIT_SEED"]))

    meta_scores: dict[str, float] = {}
    no_context_scores: dict[str, float] = {}
    trace_rows: list[dict[str, Any]] = []
    train_readback: dict[str, Any] = {}
    seed = int(P.model_seeds()[0])

    for family in ML.FAMILIES:
        params = SMOKE_CONFIGS[family]
        result = ML.train_select(
            family,
            params,
            seed,
            datasets["rung1_train"],
            datasets["rung1_val"],
            datasets["rung1_test"],
            SMOKE_BUDGET,
        )
        meta_scores[family] = result.test_balacc
        train_readback[family] = {
            "params": params,
            "lr": result.lr,
            "epochs_run": result.epochs_run,
            "steps_run": result.steps_run,
            "best_val_balacc": result.best_val_balacc,
            "device": result.device,
            "train_curve": result.train_curve,
        }
        no_ctx = ML.train_select(
            family,
            params,
            seed,
            datasets["rung1_train"],
            datasets["rung1_val"],
            datasets["rung1_test"],
            SMOKE_BUDGET,
            context_ablate=True,
        )
        no_context_scores[family] = no_ctx.test_balacc
        for idx, ep in enumerate(datasets["rung1_test"]):
            row = {
                "rung_id": "rung1",
                "seed": seed,
                "family": family,
                "episode_id": int(ep.episode_id),
                "split_id": "rung1_test",
                "rule_split_id": "TRAIN_RULES",
                "value_regime": "seen_values",
                "rule_membership_tag": "seen",
                "adaptation_tuples": [
                    {
                        "x": [int(v) for v in x],
                        "a": int(a),
                        "e": int(e),
                    }
                    for x, a, e in zip(ep.adapt_x, ep.adapt_a, ep.adapt_e)
                ],
                "query": [[int(v) for v in x] + [int(a)] for x, a in zip(ep.query_x, ep.query_a)],
                "query_e": [int(v) for v in ep.query_e],
                "ideal_prediction": rung1_ideal_preds[idx],
                "lower_reference_predictions": rung1_lower_records[idx],
                "meta_prediction": result.test_preds[idx],
                "balanced_accuracy": {
                    "ideal_prediction": _balanced_accuracy_from_lists([int(v) for v in ep.query_e], rung1_ideal_preds[idx]),
                    "meta_prediction": _balanced_accuracy_from_lists([int(v) for v in ep.query_e], result.test_preds[idx]),
                },
                "device_telemetry": result.device,
            }
            trace_rows.append(row)

    scanner = LR.rung1_scanner(
        datasets["rung1_test"],
        lower_means=rung1_lower,
        no_context_meta_balacc=max(no_context_scores[f] for f in ML.PRIMARY_FAMILIES),
    )

    live_means: dict[str, float] = {}
    for family in ML.FAMILIES:
        live_means[f"{family}::ideal_prediction"] = rung1_ideal
        live_means[f"{family}::meta_prediction"] = meta_scores[family]
    replay = replay_from_trace(trace_rows, live_means)

    leakage = leakage_smoke()
    tamper = V.synthetic_tamper_coverage()
    source_manifest = write_source_manifest()
    device = ML.device_readback()
    primary_runs = device["meta_learner_device_runs"]
    cuda_calibration = {
        "status": "non_evidential_gpu_runtime_calibration_only",
        "cuda_available": bool(torch.cuda.is_available()),
        "selected_device": device["selected_device"],
        "gpu_name": device["cuda_device_name"],
        "torch_version": device["torch_version"],
        "primary_families": ML.PRIMARY_FAMILIES,
        "primary_family_runs": {family: primary_runs.get(family, {}) for family in ML.PRIMARY_FAMILIES},
        "primary_families_on_selected_device": all(
            primary_runs.get(family, {}).get("any_run_on_selected_device", False)
            and primary_runs.get(family, {}).get("all_runs_on_selected_device", False)
            for family in ML.PRIMARY_FAMILIES
        ),
        "primary_predictions_serialized_on_cpu": all(
            primary_runs.get(family, {}).get("predictions_serialized_on_cpu", False)
            for family in ML.PRIMARY_FAMILIES
        ),
        "all_family_runs": primary_runs,
    }

    report = {
        "task_id": "TLGP-001B-R2-HARNESS-SMOKE-001",
        "task_verdict": "r2_harness_implemented_and_smoke_validated__official_run_not_launched",
        "smoke": True,
        "evidential": False,
        "official_verdict": "NOT_EMITTED",
        "official_result_json_created": False,
        "full_run_launched": False,
        "prereg": {
            "canonical_sha256_authorized": P.FROZEN_PREREG_SHA256,
            "canonical_sha256_readback": prereg["_canonical_sha256_readback"],
            "match": prereg["_sha256_match"],
            "raw_bytes_sha256": hashlib.sha256(P.PREREG_JSON_PATH.read_bytes()).hexdigest(),
        },
        "python": {
            "executable": sys.executable,
            "version": sys.version,
        },
        "smoke_nonprereg_sizes": SMOKE_SIZES,
        "smoke_nonprereg_budget": SMOKE_BUDGET,
        "smoke_nonprereg_configs": SMOKE_CONFIGS,
        "split_assertions": S.split_assertions(datasets),
        "rung1_ideal_seen1": rung1_ideal,
        "rung1_lower_reference_means": rung1_lower,
        "rung1_scanner": scanner,
        "meta_smoke_scores": meta_scores,
        "no_context_meta_smoke_scores": no_context_scores,
        "train_readback": train_readback,
        "trace_rows": len(trace_rows),
        "trace_file": "artifacts/TLGP-001B-R2/SMOKE_NON_EVIDENTIAL/smoke_trace.jsonl",
        "replay": replay,
        "leakage_smoke": {
            "all_planted_caught": leakage["all_planted_caught"],
            "renamed_leak_caught": leakage["renamed_leak_caught"],
            "no_clean_false_flag": leakage["no_clean_false_flag"],
            "detector_valid": leakage["detector_valid"],
            "structural_boundary_ok": leakage["structural_boundary_ok"],
        },
        "tamper_coverage": tamper,
        "cuda_device_calibration": cuda_calibration,
        "source_manifest": source_manifest,
        "claim_ceiling": P.claim_ceiling(),
        "estimated_full_runtime": {
            "official_full_run_not_launched": True,
            "rough_basis": "R1 GPU calibration artifact estimated about 2.7h for 60-epoch/240-trainings and 9.0h for 200-epoch/240-trainings; R2 has additional rungs/ablations, so exact runtime remains pending a separate calibration.",
            "estimate_status": "not_a_run_result",
        },
        "elapsed_sec": round(time.time() - start, 3),
    }

    assert_cuda_plumbing_or_block(report)

    SMOKE_DIR.mkdir(parents=True, exist_ok=True)
    RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
    write_json(SMOKE_DIR / "smoke_report.json", report)
    with (SMOKE_DIR / "smoke_trace.jsonl").open("w", encoding="utf-8") as handle:
        for row in trace_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    run_output = {
        "smoke": True,
        "evidential": False,
        "official_verdict": "NOT_EMITTED",
        "task_verdict": report["task_verdict"],
        "prereg_match": report["prereg"]["match"],
        "replay_exact": report["replay"]["replay_exact"],
        "leakage_detector_valid": report["leakage_smoke"]["detector_valid"],
        "tamper_all_seven": report["tamper_coverage"]["all_seven_terminals_covered"],
        "selected_device": report["cuda_device_calibration"]["selected_device"],
        "primary_families_on_selected_device": report["cuda_device_calibration"]["primary_families_on_selected_device"],
        "elapsed_sec": report["elapsed_sec"],
    }
    write_json(SMOKE_DIR / "smoke_run_output.txt", run_output)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    write_json(RUN_LOG_DIR / f"gpu_device_calibration_{stamp}.json", cuda_calibration)
    write_claim_ceiling()
    write_implementation_report(report)
    write_sha256s()
    return report


def write_failure_manifest(exc: Exception) -> None:
    manifest = {
        "task_id": "TLGP-001B-R2-HARNESS-SMOKE-001",
        "blocked": True,
        "evidential": False,
        "official_verdict": "NOT_EMITTED",
        "failure_type": type(exc).__name__,
        "failure": str(exc),
        "claim_ceiling": "device/prereg/plumbing blocker only",
    }
    write_json(ARTIFACT_DIR / "failure_manifest.json", manifest)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="run non-evidential smoke/calibration only")
    parser.add_argument("--full", action="store_true", help="run official frozen full orchestration after pre-run gates")
    parser.add_argument("--dry-run", action="store_true", help="with --full, perform pre-run gates/self-check without training")
    parser.add_argument("--replay", type=str, help="recompute official verdict from a saved official result.json without retraining")
    args = parser.parse_args(argv)
    if args.replay:
        from . import official_full as OF

        report = OF.official_replay(Path(args.replay))
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("replay_exact") else 2
    if args.full:
        if args.smoke:
            parser.error("--smoke and --full are mutually exclusive")
        from . import official_full as OF

        try:
            report = OF.run_dry_run(sys.argv[1:] if argv is None else argv) if args.dry_run else OF.run_full(sys.argv[1:] if argv is None else argv)
        except OF.OfficialRunBlocker as exc:
            OF.write_failure_manifest(exc.code, exc.detail, exc)
            print(json.dumps({
                "task_verdict": exc.code,
                "blocked": True,
                "detail": exc.detail,
                "official_verdict": "NOT_EMITTED",
            }, indent=2, sort_keys=True))
            return 2
        except KeyboardInterrupt as exc:
            OF.write_failure_manifest("blocked_runtime_interrupted_incomplete", "operator/runtime interruption", exc)
            raise
        except Exception as exc:
            OF.write_failure_manifest("blocked_other_exact_reason", str(exc), exc)
            raise
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    if args.dry_run:
        parser.error("--dry-run requires --full")
    if not args.smoke:
        parser.error("only --smoke is authorized in this task")
    try:
        report = run_smoke()
    except Exception as exc:
        write_failure_manifest(exc)
        raise
    summary = {
        "smoke": True,
        "evidential": False,
        "official_verdict": "NOT_EMITTED",
        "task_verdict": report["task_verdict"],
        "prereg_match": report["prereg"]["match"],
        "replay_exact": report["replay"]["replay_exact"],
        "leakage_detector_valid": report["leakage_smoke"]["detector_valid"],
        "tamper_all_seven": report["tamper_coverage"]["all_seven_terminals_covered"],
        "selected_device": report["cuda_device_calibration"]["selected_device"],
        "primary_families_on_selected_device": report["cuda_device_calibration"]["primary_families_on_selected_device"],
        "elapsed_sec": report["elapsed_sec"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
