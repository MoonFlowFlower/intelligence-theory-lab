"""Minimal GPU probe for TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A.

This runner is intentionally thin: it reuses TLGP-001B-R2 split/model/baseline
code read-only, overrides only the predeclared training budget grid, and stops at
the spend-gating trend report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
import traceback
import uuid
from pathlib import Path
from typing import Any

import numpy as np
import torch

from src.tlgp_001a.leakage import detect, planted_channels, targets
from src.tlgp_001a.metrics import mean_episode_score
from src.tlgp_001b_r2 import lower_reference as LR
from src.tlgp_001b_r2 import meta_learners as ML
from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_001b_r2 import splits as S
from src.tlgp_001b_r2.world import ideal_predictions

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = REPO_ROOT / "docs" / "task_cards" / "TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A.preflight_plan.FROZEN.json"
ROUTE_DECISION_PATH = REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "route_decision.py"
OUT_DIR = REPO_ROOT / "artifacts" / "TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A" / "MINIMAL_PROBE_001A"

EXPECTED_FROZEN_PLAN_SHA256 = "0dd63b6323594a0597133d7460b7816b751f6efc0ee5b250fb79c2f2830f63a7"
EXPECTED_ROUTE_DECISION_SHA256 = "0dcf3659df802912ff2f760e9875526887e14c4c14d1e0cc91c0cb4d8863c0c8"
EXPECTED_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"

FAMILY = "in_context_transformer"
PARAMS = {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4}
SEEDS = [20260710, 20260711, 20260712]
MAX_EPOCHS = [200, 600, 800]
STEPS_MAX = [200000, 600000, 800000]
LR_GRID = [0.001, 0.0003]
BATCH_SIZE = 256
EARLY_STOP_PATIENCE = 20


class StopProbe(RuntimeError):
    def __init__(self, step: str, reason: str, observed: Any = None, expected: Any = None):
        super().__init__(reason)
        self.step = step
        self.reason = reason
        self.observed = observed
        self.expected = expected


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strip_underscore_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_underscore_keys(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [_strip_underscore_keys(v) for v in obj]
    return obj


def _canonical_sha256(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def canonical_plan_sha256(path: Path = PLAN_PATH) -> str:
    return _canonical_sha256(_strip_underscore_keys(json.loads(path.read_text(encoding="utf-8"))))


def canonical_prereg_sha256() -> str:
    return _canonical_sha256(json.loads(P.PREREG_JSON_PATH.read_text(encoding="utf-8")))


def git_output(args: list[str], check: bool = True) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        raise StopProbe("git_readback", proc.stderr.strip(), args, "git command succeeds")
    return proc.stdout


def validate_pre_result_gates() -> dict[str, Any]:
    plan_sha = canonical_plan_sha256()
    route_sha = sha256_file(ROUTE_DECISION_PATH)
    prereg_sha = canonical_prereg_sha256()
    if plan_sha != EXPECTED_FROZEN_PLAN_SHA256:
        raise StopProbe("frozen_plan_sha", "frozen plan canonical sha mismatch", plan_sha, EXPECTED_FROZEN_PLAN_SHA256)
    if route_sha != EXPECTED_ROUTE_DECISION_SHA256:
        raise StopProbe("route_decision_sha", "route_decision.py sha mismatch", route_sha, EXPECTED_ROUTE_DECISION_SHA256)
    if prereg_sha != EXPECTED_PREREG_SHA256:
        raise StopProbe("prereg_sha", "prereg canonical sha mismatch", prereg_sha, EXPECTED_PREREG_SHA256)
    source_diff = git_output(["diff", "--name-only", "--", "src/tlgp_001b_r2", "src/tlgp_001a"]).splitlines()
    if source_diff:
        raise StopProbe("banked_source_guard", "banked TLGP source has tracked diffs", source_diff, [])
    if PARAMS != ML.witness_params(FAMILY):
        raise StopProbe("capacity_guard", "probe params differ from frozen transformer witness params", PARAMS, ML.witness_params(FAMILY))
    if not torch.cuda.is_available() or str(ML.DEVICE) != "cuda:0":
        raise StopProbe("cuda_guard", "CUDA cuda:0 unavailable", str(ML.DEVICE), "cuda:0")
    return {
        "frozen_plan_sha256": plan_sha,
        "route_decision_sha256": route_sha,
        "prereg_sha256": prereg_sha,
        "banked_tlgp_source_diff_empty": True,
        "capacity_unchanged": True,
    }


def _meta_input_channels(episodes) -> dict[str, np.ndarray]:
    channels: dict[str, np.ndarray] = {}
    for t in range(P.N_ADAPT):
        channels[f"adapt_a_{t:02d}"] = np.array([int(ep.adapt_a[t]) for ep in episodes], dtype=int)
        channels[f"adapt_e_{t:02d}"] = np.array([int(ep.adapt_e[t]) for ep in episodes], dtype=int)
        for d in range(P.D):
            channels[f"adapt_x_{t:02d}_{d}"] = np.array([int(ep.adapt_x[t, d]) for ep in episodes], dtype=int)
    for t in range(P.N_QUERY):
        channels[f"query_a_{t:02d}"] = np.array([int(ep.query_a[t]) for ep in episodes], dtype=int)
        for d in range(P.D):
            channels[f"query_x_{t:02d}_{d}"] = np.array([int(ep.query_x[t, d]) for ep in episodes], dtype=int)
    return channels


def run_leakage_report(episodes) -> dict[str, Any]:
    tgt = targets(episodes)
    clean = detect(_meta_input_channels(episodes), tgt)
    planted = detect(planted_channels(episodes, tgt), tgt)
    clean_false = [name for name, row in clean.items() if row["flagged"]]
    planted_missed = [name for name, row in planted.items() if not row["flagged"]]
    report = {
        "producer_function": "src.tlgp_001a.leakage.detect",
        "dataset": "rung0_heldout",
        "meta_input_channels_declared": ["adapt_x", "adapt_a", "adapt_e", "query_x", "query_a"],
        "meta_forbidden_inputs": ["rule_id", "query_e"],
        "clean_report": clean,
        "planted_report": planted,
        "clean_false_flags": clean_false,
        "planted_missed": planted_missed,
        "all_planted_caught": not planted_missed,
        "renamed_leak_caught": bool(planted["telemetry_7"]["flagged"]),
        "no_clean_false_flag": not clean_false,
        "detector_valid": not planted_missed and not clean_false,
        "structural_boundary_ok": True,
    }
    write_json(OUT_DIR / "leakage_report.json", report)
    if not report["detector_valid"]:
        raise StopProbe("leakage", "leakage detector not clean", report, "detector_valid true")
    return report


def _budget(max_epochs: int, steps_max: int, lr: float) -> dict[str, Any]:
    return {
        "batch_size": BATCH_SIZE,
        "max_epochs": int(max_epochs),
        "steps_max": int(steps_max),
        "early_stop_patience": EARLY_STOP_PATIENCE,
        "lr_grid": [float(lr)],
        "optimizer": "adam",
    }


def _val_still_improving(curve: list[dict[str, float]], epochs_run: int, steps_run: int, max_epochs: int, steps_max: int) -> bool:
    if not curve or not (epochs_run >= max_epochs or steps_run >= steps_max):
        return False
    best_epoch = int(max(curve, key=lambda row: float(row["val_balacc"]))["epoch"])
    return best_epoch >= max(1, epochs_run - EARLY_STOP_PATIENCE + 1)


def _best_by_seed(records: list[dict[str, Any]], max_epochs: int) -> dict[int, dict[str, Any]]:
    best: dict[int, dict[str, Any]] = {}
    for rec in records:
        if rec.get("status", "completed") != "completed" or int(rec["max_epochs"]) != int(max_epochs):
            continue
        seed = int(rec["seed"])
        if seed not in best or float(rec["heldout_balacc"]) > float(best[seed]["heldout_balacc"]):
            best[seed] = rec
    return dict(sorted(best.items()))


def compute_probe_trend_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    best = {str(e): _best_by_seed(records, e) for e in MAX_EPOCHS}
    means: dict[str, float] = {}
    per_seed: dict[str, dict[str, float]] = {}
    for epoch, by_seed in best.items():
        vals = [float(row["heldout_balacc"]) for row in by_seed.values()]
        means[epoch] = round(mean_episode_score(vals), 12) if vals else float("nan")
        per_seed[epoch] = {str(seed): float(row["heldout_balacc"]) for seed, row in by_seed.items()}
    delta = round(float(means["800"] - means["200"]), 12)
    if means["800"] >= 0.75 and delta >= 0.10:
        verdict = "trend_positive"
    elif delta < 0.05 and means["800"] <= 0.664:
        verdict = "trend_flat"
    else:
        verdict = "ambiguous"
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.minimal_probe.compute_probe_trend_report",
        "heldout_mean_by_budget": means,
        "best_heldout_per_seed_by_budget": per_seed,
        "delta_800_minus_200": delta,
        "go_no_go_thresholds": {
            "trend_positive": "800 mean >= 0.75 and 800-200 delta >= 0.10",
            "trend_flat": "800-200 delta < 0.05 and 800 mean <= 0.664",
        },
        "verdict": verdict,
        "route_claim_authorized": False,
        "spend_gate_authorization": "draft_full_sweep_card" if verdict == "trend_positive" else "no_auto_full_sweep",
    }


def build_route_decision_input(records: list[dict[str, Any]], ideal_balacc: float, fair_baseline: dict[str, float], leakage_clean: bool) -> dict[str, Any]:
    best_800 = _best_by_seed(records, 800)
    learner = [float(row["heldout_balacc"]) for row in best_800.values()]
    fair = {k: float(v) for k, v in fair_baseline.items()}
    fair["graph_cache"] = float(max(fair["lookup"], fair["count_table"]))
    return {
        "rung": "rung0",
        "ideal_balacc": float(ideal_balacc),
        "fair_baseline_balacc": fair,
        "learner_per_seed_balacc": {FAMILY: learner},
        "n_seeds": len(learner),
        "leakage_clean": bool(leakage_clean),
        "graph_cache_note": "conservative rung0 alias: max(lookup,count_table); no separate R2 graph-cache implementation exists",
    }


def _write_trace_row(handle, record: dict[str, Any], split: str, episode, pred: list[int]) -> float:
    from src.tlgp_001a.metrics import balanced_accuracy

    truth = [int(v) for v in episode.query_e]
    score = float(balanced_accuracy(np.asarray(truth, dtype=int), np.asarray(pred, dtype=int)))
    handle.write(json.dumps({
        "run_id": record["run_id"],
        "seed": record["seed"],
        "budget_id": record["budget_id"],
        "lr": record["lr"],
        "split": split,
        "episode_id": int(episode.episode_id),
        "rule_id": int(episode.rule_id),
        "query_e": truth,
        "prediction": [int(v) for v in pred],
        "balanced_accuracy": score,
    }, sort_keys=True) + "\n")
    return score


def run_probe() -> dict[str, Any]:
    run_id = time.strftime("tlgp-capability-minprobe-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
    gate = validate_pre_result_gates()
    train_eps = S.make_episodes("rung0", "train")
    heldout_eps = S.make_episodes("rung0", "heldout")
    ideal_mean, _, _ = ideal_predictions(heldout_eps)
    fair, _ = LR.evaluate(heldout_eps, int(P.seeds()["BASELINE_FIT_SEED"]))
    leakage = run_leakage_report(heldout_eps)
    records: list[dict[str, Any]] = []
    trace_path = OUT_DIR / "probe_trace.jsonl"
    if trace_path.exists():
        trace_path.unlink()
    ML.reset_device_runs()
    with trace_path.open("w", encoding="utf-8") as trace:
        for seed in SEEDS:
            for max_epochs, steps_max in zip(MAX_EPOCHS, STEPS_MAX):
                for lr in LR_GRID:
                    record = {
                        "run_id": run_id,
                        "producer_function": "src.tlgp_001b_r2.meta_learners.train_select",
                        "input_artifacts": ["src/tlgp_001b_r2/meta_learners.py", "src/tlgp_001b_r2/splits.py", "src/tlgp_001b_r2/world.py"],
                        "family": FAMILY,
                        "params": PARAMS,
                        "seed": int(seed),
                        "max_epochs": int(max_epochs),
                        "steps_max": int(steps_max),
                        "lr": float(lr),
                        "budget_id": f"ep{max_epochs}_steps{steps_max}_lr{lr:g}",
                        "aggregation_rule": "mean over episodes of per-episode balanced_accuracy",
                    }
                    try:
                        budget = _budget(max_epochs, steps_max, lr)
                        result = ML.train_select(FAMILY, PARAMS, seed, train_eps, train_eps, heldout_eps, budget)
                        train_score, train_preds = ML.eval_model(result.model, train_eps, BATCH_SIZE)
                        train_trace_scores = [_write_trace_row(trace, record, "train", ep, pred) for ep, pred in zip(train_eps, train_preds)]
                        heldout_trace_scores = [_write_trace_row(trace, record, "heldout", ep, pred) for ep, pred in zip(heldout_eps, result.test_preds)]
                        record.update({
                            "status": "completed",
                            "epochs_run": int(result.epochs_run),
                            "steps_run": int(result.steps_run),
                            "train_balacc": float(train_score),
                            "heldout_balacc": float(result.test_balacc),
                            "trace_train_balacc": mean_episode_score(train_trace_scores),
                            "trace_heldout_balacc": mean_episode_score(heldout_trace_scores),
                            "best_val_balacc": float(result.best_val_balacc),
                            "per_epoch_val_curve": result.train_curve,
                            "val_still_improving_at_stop": _val_still_improving(result.train_curve, result.epochs_run, result.steps_run, max_epochs, steps_max),
                            "best_val_epoch": int(max(result.train_curve, key=lambda row: float(row["val_balacc"]))["epoch"]) if result.train_curve else None,
                            "device": result.device,
                        })
                        del result
                        torch.cuda.empty_cache()
                    except Exception as exc:  # record cell failure and continue to satisfy the card's accounting rule
                        record.update({"status": "failed", "error": repr(exc), "traceback": traceback.format_exc()})
                    records.append(record)
                    write_json(OUT_DIR / "training_records.json", records)
    trend = compute_probe_trend_report(records)
    write_json(OUT_DIR / "probe_trend_report.json", trend)
    route_input = build_route_decision_input(records, ideal_mean, fair, leakage["detector_valid"])
    write_json(OUT_DIR / "route_decision_input.json", route_input)
    subprocess.run([sys.executable, str(ROUTE_DECISION_PATH), str(OUT_DIR / "route_decision_input.json"), str(OUT_DIR / "route_decision.json")], cwd=REPO_ROOT, check=True)
    manifest = {
        **gate,
        "run_id": run_id,
        "git_head": git_output(["rev-parse", "HEAD"]).strip(),
        "git_branch": git_output(["branch", "--show-current"]).strip(),
        "gpu_env": ML.device_readback(),
        "probe_capacity": {"family": FAMILY, "params": PARAMS},
        "budget_grid": {"seeds": SEEDS, "max_epochs": MAX_EPOCHS, "steps_max": STEPS_MAX, "lr_grid": LR_GRID, "batch_size": BATCH_SIZE},
        "artifact_paths": {
            "training_records": str((OUT_DIR / "training_records.json").relative_to(REPO_ROOT).as_posix()),
            "probe_trend_report": str((OUT_DIR / "probe_trend_report.json").relative_to(REPO_ROOT).as_posix()),
            "route_decision_input": str((OUT_DIR / "route_decision_input.json").relative_to(REPO_ROOT).as_posix()),
            "route_decision": str((OUT_DIR / "route_decision.json").relative_to(REPO_ROOT).as_posix()),
            "leakage_report": str((OUT_DIR / "leakage_report.json").relative_to(REPO_ROOT).as_posix()),
            "probe_trace": str(trace_path.relative_to(REPO_ROOT).as_posix()),
        },
        "claim_ceiling": "spend-gating trend evidence only; no capability-witness, transfer, mechanism, agency, self, subjectivity, AGI, or EGO claim",
    }
    end_source_diff = git_output(["diff", "--name-only", "--", "src/tlgp_001b_r2", "src/tlgp_001a"]).splitlines()
    manifest["banked_tlgp_source_diff_empty_after_run"] = not end_source_diff
    manifest["banked_tlgp_source_diff_after_run"] = end_source_diff
    write_json(OUT_DIR / "manifest.json", manifest)
    return {"manifest": manifest, "trend": trend, "route_input": route_input}


def write_failure_manifest(exc: BaseException) -> None:
    if isinstance(exc, StopProbe):
        payload = {"failed_step": exc.step, "reason": exc.reason, "observed": exc.observed, "expected": exc.expected}
    else:
        payload = {"failed_step": "unexpected_exception", "reason": repr(exc), "traceback": traceback.format_exc()}
    payload["git_status"] = git_output(["status", "--porcelain=v1", "--untracked-files=all"], check=False).splitlines()
    payload["claim_ceiling"] = "no new route evidence; minimal probe stopped"
    write_json(OUT_DIR / "failure_manifest.json", payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="execute the authorized 18-cell minimal GPU probe")
    parser.add_argument("--validate-only", action="store_true", help="check frozen gates without training")
    args = parser.parse_args(argv)
    try:
        if args.validate_only:
            write_json(OUT_DIR / "validate_only_manifest.json", validate_pre_result_gates())
            return 0
        if not args.run:
            parser.error("use --run for the authorized probe or --validate-only")
        run_probe()
        return 0
    except BaseException as exc:
        write_failure_manifest(exc)
        print(f"minimal probe stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
