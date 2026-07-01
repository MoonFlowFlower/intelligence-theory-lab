"""Formal powered TLGP rung0 run for the retrieval in-context model."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
import traceback
import uuid
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

from src.tlgp_001a.leakage import detect, planted_channels, targets
from src.tlgp_001b_r2 import lower_reference as LR
from src.tlgp_001b_r2 import meta_learners as ML
from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_001b_r2 import splits as S
from src.tlgp_001b_r2.world import ideal_predictions
from src.tlgp_capability_witness_preflight_001a import minimal_probe as MP
from src.tlgp_capability_witness_preflight_001a.grokking_probe import _eval_checkpoint
from src.tlgp_capability_witness_preflight_001a.retrieval_model import (
    FAMILY,
    PARAMS,
    build_model,
    parameter_count,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "TLGP-CAPABILITY-WITNESS-RUNG0-POWERED-001A"
FROZEN_DESIGN_PATH = (
    REPO_ROOT
    / "docs"
    / "task_cards"
    / "TLGP-CAPABILITY-WITNESS-RUNG0-POWERED-001A.frozen_design.json"
)
ROUTE_DECISION_PATH = (
    REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "route_decision.py"
)
RETRIEVAL_MODEL_PATH = (
    REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "retrieval_model.py"
)
RUNG0_RERUN_PATH = (
    REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "rung0_retrieval_rerun.py"
)
OUT_DIR = (
    REPO_ROOT
    / "artifacts"
    / "TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A"
    / "RUNG0_POWERED_001A"
)

EXPECTED_FROZEN_DESIGN_SHA256 = "69e86cb1df0f29c60f0d9d3046ea65e13a246a1d809a1afb8139bc6019ae5cb8"
EXPECTED_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"
EXPECTED_ROUTE_DECISION_SHA256 = "0dcf3659df802912ff2f760e9875526887e14c4c14d1e0cc91c0cb4d8863c0c8"
EXPECTED_RETRIEVAL_MODEL_SHA256 = "0cba923965f305c6c8cab41a8dd033d7a34bf1c3cd60b0ea27a7fdcc698bf2bb"
EXPECTED_RUNG0_RERUN_SHA256 = "fee06b4fb12dd6453ac0df9de26b8a30672d1604b4b82a8e4ec747c1092e4088"
EXPECTED_POSITIVE_CONTROL_SHA256 = "b06112b59b3388886b5770a628e6361958fe07b004e34d3bf21e08588cf91749"
EXPECTED_GROKKING_PROBE_SHA256 = "9126dc9273c5aac6c909de9d503e323609dca61c6d9e51fadd0d459a89d74555"
EXPECTED_META_LEARNERS_SHA256 = "358d2bb2449f88ff5c73de52fcabcbba17f40b22dabc5c484f7b67da627e1b6f"

LEARNER_KEY = "retrieval_model"
SEEDS = list(range(20260710, 20260720))
LEARNING_RATE = 0.0003
WEIGHT_DECAY = 0.1
BATCH_SIZE = 256
MAX_STEPS = 50_000
CHECKPOINT_EVERY_STEPS = 2_000
OVERLAP_MIN = 0.03
OVERLAP_MAX = 0.05
FAIR_BASELINE_NAMES = ["lookup", "count_table", "predict_all", "majority", "no_adaptation"]
Z_ALPHA_ONE_SIDED_05 = 1.6448536269514722
Z_POWER_80 = 0.8416212335729143


class StopRung0Powered(RuntimeError):
    def __init__(self, step: str, reason: str, observed: Any = None, expected: Any = None):
        super().__init__(reason)
        self.step = step
        self.reason = reason
        self.observed = observed
        self.expected = expected


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_output(args: list[str], check: bool = True) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        raise StopRung0Powered("git_readback", proc.stderr.strip(), args, "git command succeeds")
    return proc.stdout


def canonical_design_sha256(path: Path) -> str:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return MP._canonical_sha256(MP._strip_underscore_keys(obj))


def protected_source_status() -> list[str]:
    return git_output(
        [
            "status",
            "--porcelain=v1",
            "--",
            "src/tlgp_001b_r2",
            "src/tlgp_001a",
            "src/tlgp_capability_witness_preflight_001a/positive_control.py",
            "src/tlgp_capability_witness_preflight_001a/grokking_probe.py",
            "src/tlgp_capability_witness_preflight_001a/route_decision.py",
        ]
    ).splitlines()


def dependency_status() -> list[str]:
    return git_output(
        [
            "status",
            "--porcelain=v1",
            "--",
            "src/tlgp_capability_witness_preflight_001a/retrieval_model.py",
            "src/tlgp_capability_witness_preflight_001a/rung0_retrieval_rerun.py",
        ]
    ).splitlines()


def _assert_hash(name: str, path: Path, expected: str) -> str:
    observed = MP.sha256_file(path)
    if observed != expected:
        raise StopRung0Powered(name, f"{path.relative_to(REPO_ROOT).as_posix()} hash mismatch", observed, expected)
    return observed


def validate_pre_run_gates() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    branch = git_output(["branch", "--show-current"]).strip()
    head = git_output(["rev-parse", "HEAD"]).strip()
    if branch != "codex/meta-theory-scaffold":
        raise StopRung0Powered("repo_branch", "unexpected branch", branch, "codex/meta-theory-scaffold")
    frozen_sha = canonical_design_sha256(FROZEN_DESIGN_PATH)
    prereg_sha = MP.canonical_prereg_sha256()
    if frozen_sha != EXPECTED_FROZEN_DESIGN_SHA256:
        raise StopRung0Powered("frozen_design_sha", "frozen design mismatch", frozen_sha, EXPECTED_FROZEN_DESIGN_SHA256)
    if prereg_sha != EXPECTED_PREREG_SHA256:
        raise StopRung0Powered("prereg_sha", "prereg mismatch", prereg_sha, EXPECTED_PREREG_SHA256)
    hashes = {
        "retrieval_model_sha256": _assert_hash("retrieval_model_sha", RETRIEVAL_MODEL_PATH, EXPECTED_RETRIEVAL_MODEL_SHA256),
        "rung0_retrieval_rerun_sha256": _assert_hash("rung0_retrieval_rerun_sha", RUNG0_RERUN_PATH, EXPECTED_RUNG0_RERUN_SHA256),
        "route_decision_sha256": _assert_hash("route_decision_sha", ROUTE_DECISION_PATH, EXPECTED_ROUTE_DECISION_SHA256),
        "positive_control_sha256": _assert_hash(
            "positive_control_sha",
            REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "positive_control.py",
            EXPECTED_POSITIVE_CONTROL_SHA256,
        ),
        "grokking_probe_sha256": _assert_hash(
            "grokking_probe_sha",
            REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "grokking_probe.py",
            EXPECTED_GROKKING_PROBE_SHA256,
        ),
        "meta_learners_sha256": _assert_hash(
            "meta_learners_sha",
            REPO_ROOT / "src" / "tlgp_001b_r2" / "meta_learners.py",
            EXPECTED_META_LEARNERS_SHA256,
        ),
    }
    status = protected_source_status()
    if status:
        raise StopRung0Powered("banked_source_guard", "protected banked source status is not empty", status, [])
    if PARAMS != {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4}:
        raise StopRung0Powered("capacity_guard", "retrieval model capacity changed", PARAMS, "256/4/4/4")
    if SEEDS != P.model_seeds():
        raise StopRung0Powered("seed_guard", "seeds differ from prereg MODEL_SEEDS", SEEDS, P.model_seeds())
    if P.N_SEEDS() != 10 or P.close_fraction_min() != 9:
        raise StopRung0Powered(
            "prereg_power_guard",
            "unexpected prereg N_SEEDS or close_fraction_min",
            {"N_SEEDS": P.N_SEEDS(), "close_fraction_min": P.close_fraction_min()},
            {"N_SEEDS": 10, "close_fraction_min": 9},
        )
    if not torch.cuda.is_available() or str(ML.DEVICE) != "cuda:0":
        raise StopRung0Powered("cuda_guard", "CUDA cuda:0 unavailable", str(ML.DEVICE), "cuda:0")
    return {
        "frozen_design_sha256": frozen_sha,
        "prereg_sha256": prereg_sha,
        **hashes,
        "git_head": head,
        "git_branch": branch,
        "capacity_unchanged": True,
        "capacity": {"family": FAMILY, "params": dict(PARAMS)},
        "protected_source_status": [],
        "dependency_status": dependency_status(),
    }


def run_leakage_report(episodes) -> dict[str, Any]:
    tgt = targets(episodes)
    clean = detect(MP._meta_input_channels(episodes), tgt)
    planted = detect(planted_channels(episodes, tgt), tgt)
    clean_false = [name for name, row in clean.items() if row["flagged"]]
    planted_missed = [name for name, row in planted.items() if not row["flagged"]]
    report = {
        "producer_function": "src.tlgp_001a.leakage.detect",
        "dataset": "rung0_heldout",
        "detector": "frozen_001A_dual_target_MI",
        "meta_input_channels_declared": ["adapt_x", "adapt_a", "adapt_e", "query_x", "query_a"],
        "meta_forbidden_inputs": ["rule_id", "query_e"],
        "clean_report": clean,
        "planted_report": planted,
        "clean_false_flags": clean_false,
        "planted_missed": planted_missed,
        "all_planted_caught": not planted_missed,
        "renamed_leak_caught": bool(planted["telemetry_7"]["flagged"]),
        "answer_leak_caught": bool(planted["calib_value"]["flagged"]),
        "no_clean_false_flag": not clean_false,
        "structural_boundary_ok": True,
        "detector_valid": not planted_missed and not clean_false,
    }
    if not report["detector_valid"]:
        raise StopRung0Powered("leakage", "leakage detector not clean", report, "detector_valid true")
    return report


def _mean(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else float("nan")


def build_datasets() -> dict[str, Any]:
    train_eps = S.make_episodes("rung0", "train")
    heldout_eps = S.make_episodes("rung0", "heldout")
    expected_train = int(P.rungs()[S.RUNG0]["n_train_episodes"])
    expected_heldout = int(P.rungs()[S.RUNG0]["n_heldout_episodes"])
    if len(train_eps) != expected_train or len(heldout_eps) != expected_heldout:
        raise StopRung0Powered(
            "dataset_counts",
            "rung0 episode count mismatch",
            {"train": len(train_eps), "heldout": len(heldout_eps)},
            {"train": expected_train, "heldout": expected_heldout},
        )
    r0_rules = [int(v) for v in S.r0_rule_indices().tolist()]
    if len(r0_rules) != 8:
        raise StopRung0Powered("r0_rule_count", "R0_RULES count mismatch", len(r0_rules), 8)
    train_overlap = _mean([float(S.query_adapt_overlap_fraction(ep)) for ep in train_eps])
    heldout_overlap = _mean([float(S.query_adapt_overlap_fraction(ep)) for ep in heldout_eps])
    if not (OVERLAP_MIN <= train_overlap <= OVERLAP_MAX and OVERLAP_MIN <= heldout_overlap <= OVERLAP_MAX):
        raise StopRung0Powered(
            "query_adapt_overlap",
            "query/adapt overlap is not in the expected ~0.04 inference range",
            {"train": train_overlap, "heldout": heldout_overlap},
            {"min": OVERLAP_MIN, "max": OVERLAP_MAX},
        )
    ideal_mean, _, ideal_scores = ideal_predictions(heldout_eps)
    fair_all, _ = LR.evaluate(heldout_eps, int(P.seeds()["BASELINE_FIT_SEED"]))
    fair = {name: float(fair_all[name]) for name in FAIR_BASELINE_NAMES}
    fair["graph_cache"] = float(max(fair["lookup"], fair["count_table"]))
    leakage = run_leakage_report(heldout_eps)
    return {
        "train": train_eps,
        "heldout": heldout_eps,
        "ideal_balacc": float(ideal_mean),
        "ideal_score_min": float(min(ideal_scores)) if ideal_scores else None,
        "fair_baselines": fair,
        "fair_baseline_max": float(max(fair.values())),
        "leakage": leakage,
        "dataset_diagnostics": {
            "train_episodes": len(train_eps),
            "heldout_episodes": len(heldout_eps),
            "r0_rule_count": len(r0_rules),
            "r0_rule_ids": r0_rules,
            "train_rule_ids_observed": sorted({int(ep.rule_id) for ep in train_eps}),
            "heldout_rule_ids_observed": sorted({int(ep.rule_id) for ep in heldout_eps}),
            "train_query_adapt_overlap_mean": train_overlap,
            "heldout_query_adapt_overlap_mean": heldout_overlap,
            "query_adapt_overlap_assertion": f"{OVERLAP_MIN} <= overlap <= {OVERLAP_MAX}",
            "model_inputs": ["adapt_x", "adapt_a", "adapt_e", "query_x", "query_a"],
            "forbidden_model_inputs": ["rule_id", "query_e"],
        },
    }


def _device_record(model: nn.Module, tensor_groups: list[tuple[torch.Tensor, torch.Tensor, torch.Tensor]]) -> dict[str, Any]:
    model_device = str(next(model.parameters()).device)
    tensor_devices = sorted({str(t.device) for group in tensor_groups for t in group})
    selected = str(ML.DEVICE)
    return {
        "selected_device": selected,
        "model_device": model_device,
        "tensor_devices": tensor_devices,
        "ran_on_cuda": model_device.startswith("cuda") and all(item.startswith("cuda") for item in tensor_devices),
        "ran_on_selected_device": model_device == selected and all(item == selected for item in tensor_devices),
    }


def _write_curve_row(handle, row: dict[str, Any]) -> None:
    handle.write(json.dumps(row, sort_keys=True) + "\n")
    handle.flush()


def formal_bar(ideal_balacc: float) -> float:
    return float(ideal_balacc) - float(P.DELTA())


def train_one_seed(
    *,
    run_id: str,
    seed: int,
    train_t: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    heldout_t: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    ideal_balacc: float,
    fair_baseline_max: float,
    param_count: int,
    curve_handle,
) -> dict[str, Any]:
    bar = formal_bar(ideal_balacc)
    torch.manual_seed(int(seed))
    model = build_model(PARAMS).to(ML.DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    lossf = nn.CrossEntropyLoss()
    ctx_tr, qx_tr, qy_tr = train_t
    n = int(ctx_tr.shape[0])
    generator = torch.Generator(device="cpu").manual_seed(int(seed))
    steps = 0
    epochs = 0
    checkpoint_index = 0
    curve: list[dict[str, Any]] = []
    final_preds: list[list[int]] = []
    early_stopped = False
    started = time.time()

    while steps < MAX_STEPS and not early_stopped:
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
                    "task_id": TASK_ID,
                    "producer_function": "src.tlgp_capability_witness_preflight_001a.rung0_retrieval_powered.train_one_seed",
                    "model_function": "src.tlgp_capability_witness_preflight_001a.retrieval_model.RetrievalInContextTransformer",
                    "family": FAMILY,
                    "learner_key": LEARNER_KEY,
                    "params": dict(PARAMS),
                    "parameter_count": int(param_count),
                    "rung": "rung0",
                    "seed": int(seed),
                    "weight_decay": WEIGHT_DECAY,
                    "lr": LEARNING_RATE,
                    "optimizer": "AdamW",
                    "batch_size": BATCH_SIZE,
                    "max_steps": MAX_STEPS,
                    "checkpoint_every_steps": CHECKPOINT_EVERY_STEPS,
                    "checkpoint_index": int(checkpoint_index),
                    "step": int(steps),
                    "epoch": int(epochs),
                    "train_balacc_0a": float(train_balacc),
                    "heldout_balacc_0b": float(heldout_balacc),
                    "formal_bar": float(bar),
                    "seed_pass_at_checkpoint": bool(float(train_balacc) >= bar and float(heldout_balacc) >= bar),
                    "ideal_balacc": float(ideal_balacc),
                    "fair_baseline_max": float(fair_baseline_max),
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
                            "step": int(steps),
                            "train_balacc_0a": round(float(train_balacc), 6),
                            "heldout_balacc_0b": round(float(heldout_balacc), 6),
                            "bar": round(float(bar), 6),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
                if row["seed_pass_at_checkpoint"]:
                    early_stopped = True
                    break
            if steps >= MAX_STEPS:
                break

    if not curve:
        raise StopRung0Powered("training", "no checkpoints recorded", {"seed": seed}, ">=1")
    device = _device_record(model, [train_t, heldout_t])
    best_heldout = max(curve, key=lambda row: float(row["heldout_balacc_0b"]))
    best_train = max(curve, key=lambda row: float(row["train_balacc_0a"]))
    formal_pass_rows = [row for row in curve if bool(row["seed_pass_at_checkpoint"])]
    best_joint = max(curve, key=lambda row: min(float(row["train_balacc_0a"]), float(row["heldout_balacc_0b"])))
    final = curve[-1]
    record = {
        "run_id": run_id,
        "task_id": TASK_ID,
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung0_retrieval_powered.train_one_seed",
        "input_artifacts": [
            "src/tlgp_capability_witness_preflight_001a/retrieval_model.py",
            "src/tlgp_capability_witness_preflight_001a/grokking_probe.py::_eval_checkpoint",
            "src/tlgp_001b_r2/splits.py::make_episodes",
            "src/tlgp_001b_r2/splits.py::r0_rule_indices",
            "src/tlgp_001b_r2/meta_learners.py::build_tensors",
        ],
        "family": FAMILY,
        "learner_key": LEARNER_KEY,
        "params": dict(PARAMS),
        "parameter_count": int(param_count),
        "rung": "rung0",
        "seed": int(seed),
        "weight_decay": WEIGHT_DECAY,
        "lr": LEARNING_RATE,
        "optimizer": "AdamW",
        "batch_size": BATCH_SIZE,
        "max_steps": MAX_STEPS,
        "checkpoint_every_steps": CHECKPOINT_EVERY_STEPS,
        "status": "completed",
        "steps_run": int(steps),
        "epochs_run": int(epochs),
        "early_stopped": bool(early_stopped),
        "early_stop_rule": "allowed by frozen design; only when train_balacc_0a and heldout_balacc_0b both reach formal bar",
        "budget_capped": bool(steps >= MAX_STEPS),
        "formal_bar": float(bar),
        "final_train_balacc_0a": float(final["train_balacc_0a"]),
        "final_heldout_balacc_0b": float(final["heldout_balacc_0b"]),
        "best_train_balacc_0a": float(best_train["train_balacc_0a"]),
        "best_train_step": int(best_train["step"]),
        "best_heldout_balacc_0b": float(best_heldout["heldout_balacc_0b"]),
        "best_heldout_step": int(best_heldout["step"]),
        "best_joint_min_train_heldout": float(min(float(best_joint["train_balacc_0a"]), float(best_joint["heldout_balacc_0b"]))),
        "best_joint_step": int(best_joint["step"]),
        "formal_seed_pass": bool(formal_pass_rows),
        "formal_seed_pass_step": int(formal_pass_rows[0]["step"]) if formal_pass_rows else None,
        "ideal_balacc": float(ideal_balacc),
        "fair_baseline_max": float(fair_baseline_max),
        "num_checkpoints": len(curve),
        "device": device,
        "aggregation_rule": "mean over episodes of per-episode balanced_accuracy",
    }
    ML._record_device_run(FAMILY, model, [train_t, heldout_t], final_preds)
    del model
    torch.cuda.empty_cache()
    return record


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(float(x) / math.sqrt(2.0)))


def compute_headroom_power(learner_scores: list[float], fair_baselines: dict[str, float]) -> dict[str, Any]:
    fair_max = float(max(float(v) for v in fair_baselines.values()))
    diffs = [float(v) - fair_max for v in learner_scores]
    n = len(diffs)
    mean_margin = _mean(diffs)
    if n >= 2:
        variance = sum((x - mean_margin) ** 2 for x in diffs) / (n - 1)
        sd = math.sqrt(max(0.0, variance))
    else:
        sd = float("nan")
    if n >= 2 and sd > 0:
        se = sd / math.sqrt(n)
        mde_80 = (Z_ALPHA_ONE_SIDED_05 + Z_POWER_80) * se
        observed_power = normal_cdf((mean_margin / se) - Z_ALPHA_ONE_SIDED_05)
        lower95 = mean_margin - Z_ALPHA_ONE_SIDED_05 * se
    elif n >= 1 and mean_margin > 0:
        se = 0.0
        mde_80 = 0.0
        observed_power = 1.0
        lower95 = mean_margin
    else:
        se = float("nan")
        mde_80 = float("inf")
        observed_power = 0.0
        lower95 = float("-inf")
    passes = bool(n == P.N_SEEDS() and observed_power >= 0.80 and mean_margin > mde_80 and lower95 > 0.0)
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung0_retrieval_powered.compute_headroom_power",
        "method": "one-sided normal approximation over seed-level retrieval-vs-max-fair margins; fair_max includes graph_cache",
        "alpha": 0.05,
        "target_power": 0.80,
        "n": int(n),
        "fair_max": fair_max,
        "learner_mean": _mean([float(v) for v in learner_scores]),
        "mean_margin_over_fair_max": mean_margin,
        "seed_margin_values": diffs,
        "sample_sd_margin": sd,
        "standard_error_margin": se,
        "mde_for_80pct_power": mde_80,
        "observed_power_approx": observed_power,
        "one_sided_lower95_margin": lower95,
        "passes_power": passes,
    }


def formal_report(records: list[dict[str, Any]], ideal_balacc: float, fair_baselines: dict[str, float], leakage: dict[str, Any]) -> dict[str, Any]:
    rows_by_seed = {int(row["seed"]): row for row in records if row.get("status") == "completed"}
    missing = [seed for seed in SEEDS if seed not in rows_by_seed]
    bar = formal_bar(ideal_balacc)
    seed_pass_count = sum(1 for seed in SEEDS if seed in rows_by_seed and bool(rows_by_seed[seed]["formal_seed_pass"]))
    heldout_scores = [float(rows_by_seed[seed]["best_heldout_balacc_0b"]) for seed in SEEDS if seed in rows_by_seed]
    headroom_power = {LEARNER_KEY: compute_headroom_power(heldout_scores, fair_baselines)}
    prereg_rule_pass = bool(not missing and seed_pass_count >= P.close_fraction_min())
    return {
        "task_id": TASK_ID,
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung0_retrieval_powered.formal_report",
        "formal_bar": float(bar),
        "formal_pass_rule": "both 0a(train) AND 0b(in-dist heldout) >= ideal-DELTA on >= 9/10 seeds",
        "seed_pass_count": int(seed_pass_count),
        "seed_pass_required": int(P.close_fraction_min()),
        "n_seeds": len(SEEDS),
        "prereg_rule_pass": prereg_rule_pass,
        "missing_completed_runs": missing,
        "per_seed": {
            str(seed): {
                "best_train_balacc_0a": float(rows_by_seed[seed]["best_train_balacc_0a"]) if seed in rows_by_seed else None,
                "best_train_step": int(rows_by_seed[seed]["best_train_step"]) if seed in rows_by_seed else None,
                "best_heldout_balacc_0b": float(rows_by_seed[seed]["best_heldout_balacc_0b"]) if seed in rows_by_seed else None,
                "best_heldout_step": int(rows_by_seed[seed]["best_heldout_step"]) if seed in rows_by_seed else None,
                "best_joint_min_train_heldout": float(rows_by_seed[seed]["best_joint_min_train_heldout"]) if seed in rows_by_seed else None,
                "formal_seed_pass": bool(rows_by_seed[seed]["formal_seed_pass"]) if seed in rows_by_seed else None,
                "formal_seed_pass_step": rows_by_seed[seed]["formal_seed_pass_step"] if seed in rows_by_seed else None,
                "ideal_balacc": float(rows_by_seed[seed]["ideal_balacc"]) if seed in rows_by_seed else None,
                "fair_baseline_max": float(rows_by_seed[seed]["fair_baseline_max"]) if seed in rows_by_seed else None,
                "steps_run": int(rows_by_seed[seed]["steps_run"]) if seed in rows_by_seed else None,
                "early_stopped": bool(rows_by_seed[seed]["early_stopped"]) if seed in rows_by_seed else None,
            }
            for seed in SEEDS
        },
        "ideal_balacc": float(ideal_balacc),
        "fair_baseline_balacc": {k: float(v) for k, v in fair_baselines.items()},
        "fair_baseline_max_including_graph_cache": float(max(fair_baselines.values())),
        "leakage": leakage,
        "leakage_clean": bool(leakage["detector_valid"]),
        "headroom_power": headroom_power,
        "claim_ceiling": (
            "formal rung0 seen-rule prerequisite only; not transfer, rung3, mechanism, agency, self, AGI, or EGO evidence"
        ),
    }


def build_route_decision_input(report: dict[str, Any]) -> dict[str, Any]:
    learner_scores = [
        float(report["per_seed"][str(seed)]["best_heldout_balacc_0b"])
        for seed in SEEDS
        if report["per_seed"][str(seed)]["best_heldout_balacc_0b"] is not None
    ]
    return {
        "rung": "rung0",
        "ideal_balacc": float(report["ideal_balacc"]),
        "fair_baseline_balacc": {k: float(v) for k, v in report["fair_baseline_balacc"].items()},
        "learner_per_seed_balacc": {LEARNER_KEY: learner_scores},
        "n_seeds": len(learner_scores),
        "leakage_clean": bool(report["leakage_clean"]),
        "headroom_power": report["headroom_power"],
        "formal_pass_rule_context": {
            "bar": float(report["formal_bar"]),
            "seed_pass_count_both_train_and_heldout": int(report["seed_pass_count"]),
            "seed_pass_required": int(report["seed_pass_required"]),
            "prereg_rule_pass": bool(report["prereg_rule_pass"]),
        },
        "selection_rule": "best heldout checkpoint per seed; powered_report separately records both-train-and-heldout prereg seed pass",
        "graph_cache_note": "conservative rung0 alias: max(lookup,count_table); no separate R2 graph-cache implementation exists",
    }


def write_route_decision(route_input: dict[str, Any]) -> dict[str, Any]:
    write_json(OUT_DIR / "route_decision_input.json", route_input)
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
    return json.loads((OUT_DIR / "route_decision.json").read_text(encoding="utf-8"))


def manifest_payload(gate: dict[str, Any], run_id: str, report: dict[str, Any], route: dict[str, Any], param_count: int) -> dict[str, Any]:
    protected_status = protected_source_status()
    retrieval_sha = MP.sha256_file(RETRIEVAL_MODEL_PATH)
    route_sha = MP.sha256_file(ROUTE_DECISION_PATH)
    return {
        **gate,
        "task_id": TASK_ID,
        "run_id": run_id,
        "git_head": git_output(["rev-parse", "HEAD"]).strip(),
        "git_branch": git_output(["branch", "--show-current"]).strip(),
        "gpu_env": ML.device_readback(),
        "model": {"family": FAMILY, "learner_key": LEARNER_KEY, "params": dict(PARAMS), "parameter_count": int(param_count)},
        "regime": {
            "rung": "rung0",
            "seeds": list(SEEDS),
            "optimizer": "AdamW",
            "lr": LEARNING_RATE,
            "weight_decay": WEIGHT_DECAY,
            "batch_size": BATCH_SIZE,
            "max_steps": MAX_STEPS,
            "checkpoint_every_steps": CHECKPOINT_EVERY_STEPS,
            "early_stopping": "allowed only when both train and heldout reach formal bar",
            "n_train": int(P.rungs()[S.RUNG0]["n_train_episodes"]),
            "n_heldout": int(P.rungs()[S.RUNG0]["n_heldout_episodes"]),
        },
        "artifact_paths": {
            "training_records": str((OUT_DIR / "training_records.json").relative_to(REPO_ROOT).as_posix()),
            "val_curves": str((OUT_DIR / "val_curves.jsonl").relative_to(REPO_ROOT).as_posix()),
            "powered_report": str((OUT_DIR / "powered_report.json").relative_to(REPO_ROOT).as_posix()),
            "route_decision_input": str((OUT_DIR / "route_decision_input.json").relative_to(REPO_ROOT).as_posix()),
            "route_decision": str((OUT_DIR / "route_decision.json").relative_to(REPO_ROOT).as_posix()),
            "manifest": str((OUT_DIR / "manifest.json").relative_to(REPO_ROOT).as_posix()),
        },
        "formal_prereg_rule_pass": bool(report["prereg_rule_pass"]),
        "route_decision_route": route.get("route"),
        "retrieval_model_sha256_after_run": retrieval_sha,
        "route_decision_sha256_after_run": route_sha,
        "retrieval_model_unchanged": retrieval_sha == EXPECTED_RETRIEVAL_MODEL_SHA256,
        "route_decision_unchanged": route_sha == EXPECTED_ROUTE_DECISION_SHA256,
        "capacity_unchanged": PARAMS == {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4},
        "banked_source_diff_empty": (
            not protected_status
            and retrieval_sha == EXPECTED_RETRIEVAL_MODEL_SHA256
            and route_sha == EXPECTED_ROUTE_DECISION_SHA256
        ),
        "banked_source_status_after_run": protected_status,
        "dependency_status_after_run": dependency_status(),
        "claim_ceiling": (
            "formal rung0 seen-rule capability-witness terminal only; not transfer/rung3, mechanism, agency, self, AGI, or EGO evidence"
        ),
    }


def run_powered() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failure_path = OUT_DIR / "failure_manifest.json"
    if failure_path.exists():
        failure_path.unlink()
    for name in (
        "training_records.json",
        "val_curves.jsonl",
        "powered_report.json",
        "route_decision_input.json",
        "route_decision.json",
        "manifest.json",
    ):
        path = OUT_DIR / name
        if path.exists():
            path.unlink()

    gate = validate_pre_run_gates()
    run_id = time.strftime("tlgp-rung0-powered-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
    datasets = build_datasets()
    model = build_model(PARAMS).to(ML.DEVICE)
    param_count = parameter_count(model)
    del model
    torch.cuda.empty_cache()

    train_t = ML.move_tensors(ML.build_tensors(datasets["train"]))
    heldout_t = ML.move_tensors(ML.build_tensors(datasets["heldout"]))
    records: list[dict[str, Any]] = []
    ML.reset_device_runs()
    with (OUT_DIR / "val_curves.jsonl").open("w", encoding="utf-8") as curve_handle:
        for seed in SEEDS:
            record = train_one_seed(
                run_id=run_id,
                seed=int(seed),
                train_t=train_t,
                heldout_t=heldout_t,
                ideal_balacc=float(datasets["ideal_balacc"]),
                fair_baseline_max=float(datasets["fair_baseline_max"]),
                param_count=param_count,
                curve_handle=curve_handle,
            )
            records.append(record)
            write_json(OUT_DIR / "training_records.json", records)

    report = formal_report(records, float(datasets["ideal_balacc"]), datasets["fair_baselines"], datasets["leakage"])
    report.update(
        {
            "run_id": run_id,
            "model": {"family": FAMILY, "learner_key": LEARNER_KEY, "params": dict(PARAMS), "parameter_count": int(param_count)},
            "ideal_score_min": datasets["ideal_score_min"],
            "dataset_diagnostics": datasets["dataset_diagnostics"],
            "input_artifacts": [
                "docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG0-POWERED-001A.frozen_design.json",
                "src/tlgp_capability_witness_preflight_001a/retrieval_model.py",
                "src/tlgp_capability_witness_preflight_001a/grokking_probe.py::_eval_checkpoint",
                "src/tlgp_001b_r2/splits.py::make_episodes",
                "src/tlgp_001b_r2/lower_reference.py::evaluate",
                "src/tlgp_001a/leakage.py::detect",
            ],
        }
    )
    write_json(OUT_DIR / "powered_report.json", report)
    route_input = build_route_decision_input(report)
    route = write_route_decision(route_input)
    manifest = manifest_payload(gate, run_id, report, route, param_count)
    write_json(OUT_DIR / "manifest.json", manifest)
    if not manifest["banked_source_diff_empty"]:
        raise StopRung0Powered(
            "banked_source_guard_after_run",
            "banked source changed or pinned dependency hash drifted",
            {
                "banked_source_status": manifest["banked_source_status_after_run"],
                "retrieval_model_sha256_after_run": manifest["retrieval_model_sha256_after_run"],
                "route_decision_sha256_after_run": manifest["route_decision_sha256_after_run"],
            },
            {"banked_source_status": [], "retrieval_model_sha256": EXPECTED_RETRIEVAL_MODEL_SHA256, "route_decision_sha256": EXPECTED_ROUTE_DECISION_SHA256},
        )
    return {"manifest": manifest, "powered_report": report, "route_decision": route, "records": records}


def self_test() -> dict[str, Any]:
    gate = validate_pre_run_gates()
    datasets = build_datasets()
    train_t = ML.move_tensors(ML.build_tensors(datasets["train"][:4]))
    heldout_t = ML.move_tensors(ML.build_tensors(datasets["heldout"][:4]))
    torch.manual_seed(SEEDS[0])
    model = build_model(PARAMS).to(ML.DEVICE)
    ctx, qx, _qy = train_t
    logits = model(ctx, qx)
    if tuple(logits.shape) != (4, P.N_QUERY, P.K):
        raise StopRung0Powered("model_shape", "unexpected logits shape", tuple(logits.shape), (4, P.N_QUERY, P.K))
    train_balacc, heldout_balacc, _ = _eval_checkpoint(model, train_t, heldout_t)
    param_count = parameter_count(model)
    power_smoke = compute_headroom_power([0.94, 0.95, 0.96, 0.95, 0.94, 0.95, 0.96, 0.95, 0.94, 0.96], datasets["fair_baselines"])
    return {
        "gate": gate,
        "logits_shape": list(logits.shape),
        "parameter_count": int(param_count),
        "eval_smoke": {"train_balacc_0a": float(train_balacc), "heldout_balacc_0b": float(heldout_balacc)},
        "formal_bar": formal_bar(float(datasets["ideal_balacc"])),
        "ideal_balacc": float(datasets["ideal_balacc"]),
        "fair_baseline_balacc": datasets["fair_baselines"],
        "leakage_clean": bool(datasets["leakage"]["detector_valid"]),
        "leakage_controls": {
            "all_planted_caught": bool(datasets["leakage"]["all_planted_caught"]),
            "renamed_leak_caught": bool(datasets["leakage"]["renamed_leak_caught"]),
            "answer_leak_caught": bool(datasets["leakage"]["answer_leak_caught"]),
            "no_clean_false_flag": bool(datasets["leakage"]["no_clean_false_flag"]),
        },
        "dataset_diagnostics": datasets["dataset_diagnostics"],
        "power_smoke": power_smoke,
    }


def write_failure_manifest(exc: BaseException) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if isinstance(exc, StopRung0Powered):
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
    payload.update(
        {
            "task_id": TASK_ID,
            "git_head": git_output(["rev-parse", "HEAD"], check=False).strip(),
            "git_branch": git_output(["branch", "--show-current"], check=False).strip(),
            "git_status": git_output(["status", "--porcelain=v1", "--untracked-files=all"], check=False).splitlines(),
            "claim_ceiling": "no completed powered rung0 terminal; task stopped",
        }
    )
    write_json(OUT_DIR / "failure_manifest.json", payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="run frozen 10-seed powered rung0 retrieval terminal")
    parser.add_argument("--validate-only", action="store_true", help="validate frozen gates without training")
    parser.add_argument("--self-test", action="store_true", help="run model/data/leakage/power smoke without training")
    args = parser.parse_args(argv)
    try:
        if args.validate_only:
            print(json.dumps(validate_pre_run_gates(), indent=2, sort_keys=True))
            return 0
        if args.self_test:
            print(json.dumps(self_test(), indent=2, sort_keys=True))
            return 0
        if not args.run:
            parser.error("use --run, --validate-only, or --self-test")
        run_powered()
        return 0
    except BaseException as exc:
        write_failure_manifest(exc)
        print(f"rung0 powered retrieval stopped: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
