"""Grokking-regime probe for TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001A.

This runner is additive and bounded. It reuses the minimal-probe gates/helpers and
the TLGP-R2 world/model/eval code read-only, while overriding only the frozen
training regime: AdamW, weight decay grid, no early stopping, 50k steps, and dense
checkpoint metrics.
"""
from __future__ import annotations

import argparse
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
import torch.nn as nn

from src.tlgp_001a.leakage import detect, planted_channels, targets
from src.tlgp_001a.metrics import mean_episode_score
from src.tlgp_001b_r2 import lower_reference as LR
from src.tlgp_001b_r2 import meta_learners as ML
from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_001b_r2 import splits as S
from src.tlgp_001b_r2.world import ideal_predictions
from src.tlgp_capability_witness_preflight_001a import minimal_probe as MP

REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_DESIGN_PATH = (
    REPO_ROOT
    / "docs"
    / "task_cards"
    / "TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001A.frozen_design.json"
)
ROUTE_DECISION_PATH = (
    REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "route_decision.py"
)
OUT_BASE_DIR = REPO_ROOT / "artifacts" / "TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A"
OUT_SUBDIR = "GROKKING_PROBE_001A"
OUT_DIR = OUT_BASE_DIR / OUT_SUBDIR

EXPECTED_FROZEN_DESIGN_SHA256 = "93bae0c65171e35e06e2e3ca858026f623be585ae0d3873b1e253ce8b7604be6"
EXPECTED_ROUTE_DECISION_SHA256 = "0dcf3659df802912ff2f760e9875526887e14c4c14d1e0cc91c0cb4d8863c0c8"
EXPECTED_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"

FAMILY = "in_context_transformer"
PARAMS = {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4}
SEEDS = [20260710, 20260711, 20260712]
WEIGHT_DECAYS = [0.1, 1.0]
DEFAULT_WEIGHT_DECAY_GRID_ARG = "0.1,1.0"
LEARNING_RATE = 0.0003
BATCH_SIZE = 256
MAX_STEPS = 50_000
CHECKPOINT_EVERY_STEPS = 2_000
TRAIN_FIT_THRESHOLD = 0.95
HELDOUT_POSITIVE_THRESHOLD = 0.75
LATE_RISE_DELTA = 0.15
LATE_RISE_SUSTAINED_CHECKPOINTS = 3
NEGATIVE_HELDOUT_MAX = 0.60


class StopGrokkingProbe(RuntimeError):
    def __init__(self, step: str, reason: str, observed: Any = None, expected: Any = None):
        super().__init__(reason)
        self.step = step
        self.reason = reason
        self.observed = observed
        self.expected = expected


def canonical_frozen_design_sha256(path: Path = FROZEN_DESIGN_PATH) -> str:
    return MP._canonical_sha256(MP._strip_underscore_keys(json.loads(path.read_text(encoding="utf-8"))))


def resolve_frozen_design_path(path: str | Path = FROZEN_DESIGN_PATH) -> Path:
    frozen_design_path = Path(path)
    if not frozen_design_path.is_absolute():
        frozen_design_path = REPO_ROOT / frozen_design_path
    return frozen_design_path.resolve()


def expected_frozen_design_sha256(path: Path = FROZEN_DESIGN_PATH) -> str:
    path = resolve_frozen_design_path(path)
    design = json.loads(path.read_text(encoding="utf-8"))
    return str(design.get("_frozen_canonical_sha256", EXPECTED_FROZEN_DESIGN_SHA256))


def validate_pre_result_gates(frozen_design_path: Path = FROZEN_DESIGN_PATH) -> dict[str, Any]:
    frozen_design_path = resolve_frozen_design_path(frozen_design_path)
    frozen_sha = canonical_frozen_design_sha256(frozen_design_path)
    expected_frozen_sha = expected_frozen_design_sha256(frozen_design_path)
    route_sha = MP.sha256_file(ROUTE_DECISION_PATH)
    prereg_sha = MP.canonical_prereg_sha256()
    if frozen_sha != expected_frozen_sha:
        raise StopGrokkingProbe(
            "frozen_design_sha",
            "frozen design canonical sha mismatch",
            frozen_sha,
            expected_frozen_sha,
        )
    if route_sha != EXPECTED_ROUTE_DECISION_SHA256:
        raise StopGrokkingProbe(
            "route_decision_sha",
            "route_decision.py sha mismatch",
            route_sha,
            EXPECTED_ROUTE_DECISION_SHA256,
        )
    if prereg_sha != EXPECTED_PREREG_SHA256:
        raise StopGrokkingProbe(
            "prereg_sha",
            "prereg canonical sha mismatch",
            prereg_sha,
            EXPECTED_PREREG_SHA256,
        )
    protected_status = MP.git_output(
        ["status", "--porcelain=v1", "--", "src/tlgp_001b_r2", "src/tlgp_001a"]
    ).splitlines()
    if protected_status:
        raise StopGrokkingProbe(
            "banked_source_guard",
            "protected TLGP source status is not empty",
            protected_status,
            [],
        )
    witness_params = ML.witness_params(FAMILY)
    if PARAMS != witness_params:
        raise StopGrokkingProbe(
            "capacity_guard",
            "probe params differ from frozen transformer witness params",
            PARAMS,
            witness_params,
        )
    design = json.loads(frozen_design_path.read_text(encoding="utf-8"))
    observed_capacity = {k: design["capacity_FROZEN"].get(k) for k in ("d_model", "layers", "heads", "ff_mult", "learner")}
    if observed_capacity != {**PARAMS, "learner": FAMILY}:
        raise StopGrokkingProbe(
            "frozen_design_capacity",
            "frozen design capacity does not match expected transformer 256/4",
            observed_capacity,
            {**PARAMS, "learner": FAMILY},
        )
    if not torch.cuda.is_available() or str(ML.DEVICE) != "cuda:0":
        raise StopGrokkingProbe("cuda_guard", "CUDA cuda:0 unavailable", str(ML.DEVICE), "cuda:0")
    return {
        "frozen_design_sha256": frozen_sha,
        "frozen_design_path": str(frozen_design_path.relative_to(REPO_ROOT).as_posix()),
        "route_decision_sha256": route_sha,
        "prereg_sha256": prereg_sha,
        "capacity_unchanged": True,
        "banked_source_status_empty": True,
        "protected_source_status": [],
    }


def parse_weight_decay_grid(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated float grid: {value}") from exc
    if not values:
        raise argparse.ArgumentTypeError("weight-decay grid must include at least one float")
    return values


def resolve_out_dir(out_subdir: str) -> Path:
    subdir = Path(out_subdir)
    if subdir.is_absolute() or ".." in subdir.parts:
        raise argparse.ArgumentTypeError(f"out-subdir must stay under {OUT_BASE_DIR.relative_to(REPO_ROOT).as_posix()}")
    return OUT_BASE_DIR / subdir


def run_leakage_report(episodes) -> dict[str, Any]:
    tgt = targets(episodes)
    clean = detect(MP._meta_input_channels(episodes), tgt)
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
    MP.write_json(OUT_DIR / "leakage_report.json", report)
    if not report["detector_valid"]:
        raise StopGrokkingProbe("leakage", "leakage detector not clean", report, "detector_valid true")
    return report


def _eval_checkpoint(model: nn.Module, train_t, heldout_t) -> tuple[float, float, list[list[int]]]:
    train_balacc, _ = ML._eval_tensors(model, train_t, BATCH_SIZE)
    heldout_balacc, heldout_preds = ML._eval_tensors(model, heldout_t, BATCH_SIZE)
    return float(train_balacc), float(heldout_balacc), heldout_preds


def _write_curve_row(handle, row: dict[str, Any]) -> None:
    handle.write(json.dumps(row, sort_keys=True) + "\n")
    handle.flush()


def train_one_grokking_run(
    *,
    run_id: str,
    seed: int,
    weight_decay: float,
    train_eps,
    heldout_eps,
    train_t,
    heldout_t,
    curve_handle,
) -> dict[str, Any]:
    model = ML.build_model(FAMILY, PARAMS, int(seed))
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=float(weight_decay))
    lossf = nn.CrossEntropyLoss()
    ctx_tr, qx_tr, qy_tr = train_t
    n = int(ctx_tr.shape[0])
    generator = torch.Generator(device="cpu").manual_seed(int(seed))
    steps = 0
    epochs = 0
    checkpoint_index = 0
    curve: list[dict[str, Any]] = []
    final_preds: list[list[int]] = []

    started = time.time()
    while steps < MAX_STEPS:
        epochs += 1
        model.train()
        perm = torch.randperm(n, generator=generator)
        for start in range(0, n, BATCH_SIZE):
            idx = perm[start:start + BATCH_SIZE].to(ctx_tr.device)
            logits = model(ctx_tr[idx], qx_tr[idx])
            loss = lossf(logits.reshape(-1, P.K), qy_tr[idx].reshape(-1))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            steps += 1
            if steps % CHECKPOINT_EVERY_STEPS == 0 or steps >= MAX_STEPS:
                train_balacc, heldout_balacc, final_preds = _eval_checkpoint(model, train_t, heldout_t)
                row = {
                    "run_id": run_id,
                    "producer_function": (
                        "src.tlgp_capability_witness_preflight_001a.grokking_probe"
                        ".train_one_grokking_run"
                    ),
                    "family": FAMILY,
                    "params": PARAMS,
                    "seed": int(seed),
                    "weight_decay": float(weight_decay),
                    "lr": LEARNING_RATE,
                    "optimizer": "AdamW",
                    "early_stopping": "disabled",
                    "batch_size": BATCH_SIZE,
                    "max_steps": MAX_STEPS,
                    "checkpoint_every_steps": CHECKPOINT_EVERY_STEPS,
                    "checkpoint_index": checkpoint_index,
                    "step": int(steps),
                    "epoch": int(epochs),
                    "train_balacc": train_balacc,
                    "heldout_balacc": heldout_balacc,
                    "elapsed_sec": round(time.time() - started, 3),
                }
                checkpoint_index += 1
                curve.append(row)
                _write_curve_row(curve_handle, row)
                print(
                    json.dumps(
                        {
                            "event": "checkpoint",
                            "seed": int(seed),
                            "weight_decay": float(weight_decay),
                            "step": int(steps),
                            "train_balacc": round(train_balacc, 6),
                            "heldout_balacc": round(heldout_balacc, 6),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
            if steps >= MAX_STEPS:
                break

    if not curve:
        raise StopGrokkingProbe("training", "no checkpoints were recorded", {"seed": seed, "wd": weight_decay}, ">=1")
    device = ML._record_device_run(FAMILY, model, [train_t, heldout_t], final_preds)
    analysis = analyze_curve(curve)
    best = max(curve, key=lambda row: float(row["heldout_balacc"]))
    final = curve[-1]
    record = {
        "run_id": run_id,
        "producer_function": "src.tlgp_capability_witness_preflight_001a.grokking_probe.train_one_grokking_run",
        "input_artifacts": [
            "src/tlgp_capability_witness_preflight_001a/minimal_probe.py",
            "src/tlgp_001b_r2/meta_learners.py",
            "src/tlgp_001b_r2/splits.py",
            "src/tlgp_001b_r2/world.py",
        ],
        "family": FAMILY,
        "params": PARAMS,
        "seed": int(seed),
        "weight_decay": float(weight_decay),
        "lr": LEARNING_RATE,
        "optimizer": "AdamW",
        "early_stopping": "disabled",
        "batch_size": BATCH_SIZE,
        "max_steps": MAX_STEPS,
        "checkpoint_every_steps": CHECKPOINT_EVERY_STEPS,
        "status": "completed",
        "steps_run": int(steps),
        "epochs_run": int(epochs),
        "budget_capped": bool(steps >= MAX_STEPS),
        "final_train_balacc": float(final["train_balacc"]),
        "final_heldout_balacc": float(final["heldout_balacc"]),
        "best_heldout_balacc": float(best["heldout_balacc"]),
        "best_heldout_step": int(best["step"]),
        "best_train_balacc": max(float(row["train_balacc"]) for row in curve),
        "train_first_ge_0_95_step": analysis["train_first_ge_0_95_step"],
        "late_heldout_rise": analysis["late_heldout_rise"],
        "late_heldout_rise_detail": analysis["late_heldout_rise_detail"],
        "num_checkpoints": len(curve),
        "device": device,
        "aggregation_rule": "mean over episodes of per-episode balanced_accuracy",
    }
    del model
    torch.cuda.empty_cache()
    return record


def analyze_curve(curve: list[dict[str, Any]]) -> dict[str, Any]:
    first_fit = next((row for row in curve if float(row["train_balacc"]) >= TRAIN_FIT_THRESHOLD), None)
    if first_fit is None:
        return {
            "train_first_ge_0_95_step": None,
            "late_heldout_rise": False,
            "late_heldout_rise_detail": {
                "reason": "train_balacc never reached 0.95 at a logged checkpoint",
                "interpretation": "late rise is evaluated only after first logged train>=0.95",
            },
        }
    baseline = float(first_fit["heldout_balacc"])
    target = baseline + LATE_RISE_DELTA
    post = [row for row in curve if int(row["step"]) > int(first_fit["step"])]
    sustained: list[list[dict[str, Any]]] = []
    for i in range(0, max(0, len(post) - LATE_RISE_SUSTAINED_CHECKPOINTS + 1)):
        window = post[i:i + LATE_RISE_SUSTAINED_CHECKPOINTS]
        if all(float(row["heldout_balacc"]) >= target for row in window):
            sustained.append(window)
    if sustained:
        first = sustained[0]
        detail = {
            "interpretation": "heldout rise is measured against heldout at first logged train>=0.95",
            "first_fit_step": int(first_fit["step"]),
            "first_fit_heldout_balacc": baseline,
            "target_heldout_balacc": target,
            "sustained_steps": [int(row["step"]) for row in first],
            "sustained_heldout_balacc": [float(row["heldout_balacc"]) for row in first],
        }
        return {
            "train_first_ge_0_95_step": int(first_fit["step"]),
            "late_heldout_rise": True,
            "late_heldout_rise_detail": detail,
        }
    return {
        "train_first_ge_0_95_step": int(first_fit["step"]),
        "late_heldout_rise": False,
        "late_heldout_rise_detail": {
            "interpretation": "heldout rise is measured against heldout at first logged train>=0.95",
            "first_fit_step": int(first_fit["step"]),
            "first_fit_heldout_balacc": baseline,
            "target_heldout_balacc": target,
            "reason": "no 3 consecutive post-fit checkpoints sustained the target",
        },
    }


def compute_probe_trend_report(records: list[dict[str, Any]], curves: list[dict[str, Any]]) -> dict[str, Any]:
    per_run = []
    positive_abs = False
    positive_late = False
    for record in records:
        run_curves = [
            row
            for row in curves
            if int(row["seed"]) == int(record["seed"])
            and float(row["weight_decay"]) == float(record["weight_decay"])
        ]
        analysis = analyze_curve(run_curves)
        best = max(run_curves, key=lambda row: float(row["heldout_balacc"]))
        positive_abs = positive_abs or float(best["heldout_balacc"]) >= HELDOUT_POSITIVE_THRESHOLD
        positive_late = positive_late or bool(analysis["late_heldout_rise"])
        per_run.append({
            "seed": int(record["seed"]),
            "weight_decay": float(record["weight_decay"]),
            "final_step": int(record["steps_run"]),
            "final_train_balacc": float(record["final_train_balacc"]),
            "final_heldout_balacc": float(record["final_heldout_balacc"]),
            "best_heldout_balacc": float(best["heldout_balacc"]),
            "best_heldout_step": int(best["step"]),
            "train_first_ge_0_95_step": analysis["train_first_ge_0_95_step"],
            "late_heldout_rise": bool(analysis["late_heldout_rise"]),
            "late_heldout_rise_detail": analysis["late_heldout_rise_detail"],
        })
    all_train_fit = all(float(row["best_train_balacc"]) >= TRAIN_FIT_THRESHOLD for row in records)
    all_heldout_low = all(float(row["best_heldout_balacc"]) <= NEGATIVE_HELDOUT_MAX for row in records)
    any_late = any(bool(row["late_heldout_rise"]) for row in per_run)
    if positive_abs or positive_late:
        verdict = "grok_positive"
    elif all_train_fit and all_heldout_low and not any_late:
        verdict = "grok_negative_family_limited"
    else:
        verdict = "ambiguous"
    best_overall = max(per_run, key=lambda row: float(row["best_heldout_balacc"])) if per_run else None
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.grokking_probe.compute_probe_trend_report",
        "go_no_go_verdict": verdict,
        "thresholds": {
            "grok_positive": {
                "absolute": "any best heldout >= 0.75 by 50000 steps",
                "delayed_generalization_signature": (
                    "heldout rises >= +0.15 sustained over >=3 consecutive checkpoints "
                    "after train_balacc first reaches >=0.95"
                ),
            },
            "grok_negative_family_limited": (
                "all runs train_balacc reaches >=0.95, all runs heldout stays <=0.60, "
                "and no sustained late heldout rise"
            ),
            "ambiguous": "anything else",
        },
        "signature_test": {
            "train_fit_threshold": TRAIN_FIT_THRESHOLD,
            "late_rise_delta": LATE_RISE_DELTA,
            "sustained_checkpoints": LATE_RISE_SUSTAINED_CHECKPOINTS,
            "checkpoint_every_steps": CHECKPOINT_EVERY_STEPS,
            "interpretation": "rise measured relative to heldout at first logged train>=0.95 checkpoint",
        },
        "per_run": per_run,
        "best_overall": best_overall,
        "aggregate_flags": {
            "positive_abs_heldout_ge_0_75": positive_abs,
            "positive_delayed_generalization_signature": positive_late,
            "all_runs_train_fit_ge_0_95": all_train_fit,
            "all_runs_heldout_max_le_0_60": all_heldout_low,
            "any_late_heldout_rise": any_late,
        },
        "claim_ceiling": (
            "bounded trend/lean on the training-regime lever only; not a scientific "
            "route terminal and not a transfer/mechanism claim"
        ),
    }


def build_route_decision_input(
    records: list[dict[str, Any]],
    ideal_balacc: float,
    fair_baseline: dict[str, float],
    leakage_clean: bool,
) -> dict[str, Any]:
    by_seed: dict[int, float] = {}
    for record in records:
        seed = int(record["seed"])
        value = float(record["best_heldout_balacc"])
        if seed not in by_seed or value > by_seed[seed]:
            by_seed[seed] = value
    fair = {k: float(v) for k, v in fair_baseline.items()}
    fair["graph_cache"] = float(max(fair["lookup"], fair["count_table"]))
    return {
        "rung": "rung0",
        "ideal_balacc": float(ideal_balacc),
        "fair_baseline_balacc": fair,
        "learner_per_seed_balacc": {FAMILY: [by_seed[k] for k in sorted(by_seed)]},
        "n_seeds": len(by_seed),
        "leakage_clean": bool(leakage_clean),
        "selection_rule": "best heldout checkpoint over the frozen weight_decay grid per seed",
        "graph_cache_note": "conservative rung0 alias: max(lookup,count_table); no separate R2 graph-cache implementation exists",
    }


def run_probe(
    weight_decays: list[float] = WEIGHT_DECAYS,
    out_subdir: str = OUT_SUBDIR,
    frozen_design_path: Path = FROZEN_DESIGN_PATH,
) -> dict[str, Any]:
    global OUT_DIR
    weight_decays = [float(value) for value in weight_decays]
    frozen_design_path = resolve_frozen_design_path(frozen_design_path)
    OUT_DIR = resolve_out_dir(out_subdir)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failure_path = OUT_DIR / "failure_manifest.json"
    if failure_path.exists():
        failure_path.unlink()
    run_id = time.strftime("tlgp-capability-grokprobe-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
    gate = validate_pre_result_gates(frozen_design_path)
    design = json.loads(frozen_design_path.read_text(encoding="utf-8"))
    train_eps = S.make_episodes("rung0", "train")
    heldout_eps = S.make_episodes("rung0", "heldout")
    ideal_mean, _, _ = ideal_predictions(heldout_eps)
    fair, _ = LR.evaluate(heldout_eps, int(P.seeds()["BASELINE_FIT_SEED"]))
    leakage = run_leakage_report(heldout_eps)
    train_t = ML.move_tensors(ML.build_tensors(train_eps))
    heldout_t = ML.move_tensors(ML.build_tensors(heldout_eps))
    records: list[dict[str, Any]] = []
    curves: list[dict[str, Any]] = []
    curve_path = OUT_DIR / "val_curves.jsonl"
    if curve_path.exists():
        curve_path.unlink()
    ML.reset_device_runs()
    with curve_path.open("w", encoding="utf-8") as curve_handle:
        for seed in SEEDS:
            for weight_decay in weight_decays:
                record = train_one_grokking_run(
                    run_id=run_id,
                    seed=int(seed),
                    weight_decay=float(weight_decay),
                    train_eps=train_eps,
                    heldout_eps=heldout_eps,
                    train_t=train_t,
                    heldout_t=heldout_t,
                    curve_handle=curve_handle,
                )
                records.append(record)
                MP.write_json(OUT_DIR / "training_records.json", records)
    for line in curve_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            curves.append(json.loads(line))
    if len(records) != len(SEEDS) * len(weight_decays):
        raise StopGrokkingProbe(
            "run_count",
            "not all frozen seed x weight_decay runs completed",
            len(records),
            len(SEEDS) * len(weight_decays),
        )
    trend = compute_probe_trend_report(records, curves)
    MP.write_json(OUT_DIR / "probe_trend_report.json", trend)
    route_input = build_route_decision_input(records, ideal_mean, fair, leakage["detector_valid"])
    MP.write_json(OUT_DIR / "route_decision_input.json", route_input)
    subprocess.run(
        [
            sys.executable,
            str(ROUTE_DECISION_PATH),
            str(OUT_DIR / "route_decision_input.json"),
            str(OUT_DIR / "route_decision.json"),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    route = json.loads((OUT_DIR / "route_decision.json").read_text(encoding="utf-8"))
    if route.get("route") != "inconclusive_underpowered":
        raise StopGrokkingProbe(
            "route_decision",
            "route_decision.py did not return the expected underpowered terminal",
            route.get("route"),
            "inconclusive_underpowered",
        )
    end_status = MP.git_output(
        ["status", "--porcelain=v1", "--", "src/tlgp_001b_r2", "src/tlgp_001a"]
    ).splitlines()
    manifest = {
        **gate,
        "run_id": run_id,
        "task_id": str(design.get("task_id", "TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001A")),
        "git_head": MP.git_output(["rev-parse", "HEAD"]).strip(),
        "git_branch": MP.git_output(["branch", "--show-current"]).strip(),
        "gpu_env": ML.device_readback(),
        "grokking_probe_sha256": MP.sha256_file(Path(__file__).resolve()),
        "probe_capacity": {"family": FAMILY, "params": PARAMS},
        "capacity_frozen_expected": {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4},
        "regime": {
            "rung": "rung0",
            "early_stopping": "disabled",
            "optimizer": "AdamW",
            "weight_decay_grid": weight_decays,
            "lr": LEARNING_RATE,
            "batch_size": BATCH_SIZE,
            "max_steps": MAX_STEPS,
            "checkpoint_every_steps": CHECKPOINT_EVERY_STEPS,
            "seeds": SEEDS,
        },
        "artifact_paths": {
            "training_records": str((OUT_DIR / "training_records.json").relative_to(REPO_ROOT).as_posix()),
            "val_curves": str((OUT_DIR / "val_curves.jsonl").relative_to(REPO_ROOT).as_posix()),
            "probe_trend_report": str((OUT_DIR / "probe_trend_report.json").relative_to(REPO_ROOT).as_posix()),
            "route_decision_input": str((OUT_DIR / "route_decision_input.json").relative_to(REPO_ROOT).as_posix()),
            "route_decision": str((OUT_DIR / "route_decision.json").relative_to(REPO_ROOT).as_posix()),
            "leakage_report": str((OUT_DIR / "leakage_report.json").relative_to(REPO_ROOT).as_posix()),
        },
        "route_decision_route": route.get("route"),
        "go_no_go_verdict": trend["go_no_go_verdict"],
        "banked_source_diff_empty": not end_status,
        "banked_source_status_after_run": end_status,
        "claim_ceiling": (
            "bounded training-regime trend/lean only; NOT a scientific route terminal, "
            "transfer, mechanism, learning, agency, self, subjectivity, AGI, or EGO claim"
        ),
    }
    if end_status:
        MP.write_json(OUT_DIR / "manifest.json", manifest)
        raise StopGrokkingProbe("banked_source_guard_after_run", "protected TLGP source status changed", end_status, [])
    MP.write_json(OUT_DIR / "manifest.json", manifest)
    return {"manifest": manifest, "trend": trend, "route_input": route_input, "route": route}


def write_failure_manifest(exc: BaseException) -> None:
    if isinstance(exc, StopGrokkingProbe):
        payload = {
            "failed_step": exc.step,
            "reason": exc.reason,
            "observed": exc.observed,
            "expected": exc.expected,
        }
    else:
        payload = {
            "failed_step": "unexpected_exception",
            "reason": repr(exc),
            "traceback": traceback.format_exc(),
        }
    payload["git_status"] = MP.git_output(["status", "--porcelain=v1", "--untracked-files=all"], check=False).splitlines()
    payload["claim_ceiling"] = "no completed grokking probe evidence; run stopped"
    MP.write_json(OUT_DIR / "failure_manifest.json", payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="execute the authorized 6-run grokking probe")
    parser.add_argument("--validate-only", action="store_true", help="check frozen gates without training")
    parser.add_argument(
        "--weight-decay-grid",
        default=DEFAULT_WEIGHT_DECAY_GRID_ARG,
        help="comma-separated AdamW weight decay grid; default preserves 001A",
    )
    parser.add_argument("--out-subdir", default=OUT_SUBDIR, help="artifact subdirectory under the preflight artifact root")
    parser.add_argument("--frozen-design", default=str(FROZEN_DESIGN_PATH), help="frozen design JSON path to validate")
    args = parser.parse_args(argv)
    try:
        global OUT_DIR
        weight_decays = parse_weight_decay_grid(args.weight_decay_grid)
        frozen_design_path = resolve_frozen_design_path(args.frozen_design)
        OUT_DIR = resolve_out_dir(args.out_subdir)
        if args.validate_only:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            MP.write_json(OUT_DIR / "validate_only_manifest.json", validate_pre_result_gates(frozen_design_path))
            return 0
        if not args.run:
            parser.error("use --run for the authorized probe or --validate-only")
        run_probe(
            weight_decays=weight_decays,
            out_subdir=args.out_subdir,
            frozen_design_path=frozen_design_path,
        )
        return 0
    except BaseException as exc:
        write_failure_manifest(exc)
        print(f"grokking probe stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
