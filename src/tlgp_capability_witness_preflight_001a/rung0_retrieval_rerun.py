"""Run real TLGP rung0 with the validated retrieval in-context model."""
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

import torch
import torch.nn as nn

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
TASK_ID = "TLGP-CAPABILITY-WITNESS-RUNG0-RETRIEVAL-RERUN-001A"
FROZEN_DESIGN_PATH = (
    REPO_ROOT
    / "docs"
    / "task_cards"
    / "TLGP-CAPABILITY-WITNESS-RUNG0-RETRIEVAL-RERUN-001A.frozen_design.json"
)
POSITIVE_CONTROL_DESIGN_PATH = (
    REPO_ROOT
    / "docs"
    / "task_cards"
    / "TLGP-CAPABILITY-WITNESS-RUNNER-POSITIVE-CONTROL-001A.frozen_design.json"
)
ROUTE_DECISION_PATH = (
    REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "route_decision.py"
)
RETRIEVAL_MODEL_PATH = (
    REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "retrieval_model.py"
)
OUT_DIR = (
    REPO_ROOT
    / "artifacts"
    / "TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A"
    / "RUNG0_RETRIEVAL_RERUN_001A"
)

EXPECTED_HEAD_PREFIX = "9e3e3d27"
EXPECTED_RERUN_FROZEN_DESIGN_SHA256 = "e917ad29cc00cb8e48740883a10596829cec52cc2b10032698cf1c2adc61b9af"
EXPECTED_POSITIVE_CONTROL_DESIGN_SHA256 = "90f2a5034747e0153f29ccc86a672a2cfcd8fe75910de54c02966149eeeef56b"
EXPECTED_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"
EXPECTED_ROUTE_DECISION_SHA256 = "0dcf3659df802912ff2f760e9875526887e14c4c14d1e0cc91c0cb4d8863c0c8"
EXPECTED_RETRIEVAL_MODEL_SHA256 = "0cba923965f305c6c8cab41a8dd033d7a34bf1c3cd60b0ea27a7fdcc698bf2bb"
EXPECTED_POSITIVE_CONTROL_SHA256 = "b06112b59b3388886b5770a628e6361958fe07b004e34d3bf21e08588cf91749"
EXPECTED_GROKKING_PROBE_SHA256 = "9126dc9273c5aac6c909de9d503e323609dca61c6d9e51fadd0d459a89d74555"
EXPECTED_META_LEARNERS_SHA256 = "358d2bb2449f88ff5c73de52fcabcbba17f40b22dabc5c484f7b67da627e1b6f"

SEEDS = [20260710, 20260711, 20260712]
LEARNING_RATE = 0.0003
WEIGHT_DECAY = 0.1
BATCH_SIZE = 256
MAX_STEPS = 50_000
CHECKPOINT_EVERY_STEPS = 2_000
TRAIN_FIT_THRESHOLD = 0.95
HELDOUT_PASS_THRESHOLD = 0.80
HELDOUT_FAIL_THRESHOLD = 0.65

FAIR_BASELINE_NAMES = ["lookup", "count_table", "predict_all", "majority"]


class StopRung0RetrievalRerun(RuntimeError):
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
        raise StopRung0RetrievalRerun("git_readback", proc.stderr.strip(), args, "git command succeeds")
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


def retrieval_model_status() -> list[str]:
    return git_output(["status", "--porcelain=v1", "--", "src/tlgp_capability_witness_preflight_001a/retrieval_model.py"]).splitlines()


def _assert_hash(name: str, path: Path, expected: str) -> str:
    observed = MP.sha256_file(path)
    if observed != expected:
        raise StopRung0RetrievalRerun(name, f"{path.relative_to(REPO_ROOT).as_posix()} hash mismatch", observed, expected)
    return observed


def validate_pre_run_gates() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    branch = git_output(["branch", "--show-current"]).strip()
    head = git_output(["rev-parse", "HEAD"]).strip()
    if branch != "codex/meta-theory-scaffold" or not head.startswith(EXPECTED_HEAD_PREFIX):
        raise StopRung0RetrievalRerun(
            "repo_state",
            "unexpected branch or HEAD",
            {"branch": branch, "head": head},
            {"branch": "codex/meta-theory-scaffold", "head_prefix": EXPECTED_HEAD_PREFIX},
        )
    rerun_sha = canonical_design_sha256(FROZEN_DESIGN_PATH)
    pc_sha = canonical_design_sha256(POSITIVE_CONTROL_DESIGN_PATH)
    prereg_sha = MP.canonical_prereg_sha256()
    if rerun_sha != EXPECTED_RERUN_FROZEN_DESIGN_SHA256:
        raise StopRung0RetrievalRerun("rerun_frozen_design_sha", "frozen design mismatch", rerun_sha, EXPECTED_RERUN_FROZEN_DESIGN_SHA256)
    if pc_sha != EXPECTED_POSITIVE_CONTROL_DESIGN_SHA256:
        raise StopRung0RetrievalRerun("positive_control_design_sha", "positive-control design mismatch", pc_sha, EXPECTED_POSITIVE_CONTROL_DESIGN_SHA256)
    if prereg_sha != EXPECTED_PREREG_SHA256:
        raise StopRung0RetrievalRerun("prereg_sha", "prereg mismatch", prereg_sha, EXPECTED_PREREG_SHA256)

    hashes = {
        "route_decision_sha256": _assert_hash("route_decision_sha", ROUTE_DECISION_PATH, EXPECTED_ROUTE_DECISION_SHA256),
        "retrieval_model_sha256": _assert_hash("retrieval_model_sha", RETRIEVAL_MODEL_PATH, EXPECTED_RETRIEVAL_MODEL_SHA256),
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
        raise StopRung0RetrievalRerun("banked_source_guard", "protected banked source status is not empty", status, [])
    if PARAMS != {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4}:
        raise StopRung0RetrievalRerun("capacity_guard", "retrieval model capacity changed", PARAMS, "256/4/4/4")
    if not torch.cuda.is_available() or str(ML.DEVICE) != "cuda:0":
        raise StopRung0RetrievalRerun("cuda_guard", "CUDA cuda:0 unavailable", str(ML.DEVICE), "cuda:0")
    train_eps = S.make_episodes("rung0", "train", 1)
    heldout_eps = S.make_episodes("rung0", "heldout", 1)
    if len(S.r0_rule_indices()) != 8:
        raise StopRung0RetrievalRerun("r0_rule_count", "R0_RULES count mismatch", len(S.r0_rule_indices()), 8)
    train_spec = S.rung_spec("rung0", "train")
    heldout_spec = S.rung_spec("rung0", "heldout")
    full_values = tuple(range(P.M))
    if train_spec.adapt_values != full_values or train_spec.query_values != full_values:
        raise StopRung0RetrievalRerun("rung0_train_values", "rung0 train values are not full [0..4]", train_spec, full_values)
    if heldout_spec.adapt_values != full_values or heldout_spec.query_values != full_values:
        raise StopRung0RetrievalRerun("rung0_heldout_values", "rung0 heldout values are not full [0..4]", heldout_spec, full_values)
    return {
        "rerun_frozen_design_sha256": rerun_sha,
        "positive_control_design_sha256": pc_sha,
        "prereg_sha256": prereg_sha,
        **hashes,
        "git_head": head,
        "git_branch": branch,
        "banked_source_diff_empty": True,
        "protected_source_status": [],
        "retrieval_model_status": retrieval_model_status(),
        "capacity_unchanged": True,
        "capacity": {"family": FAMILY, "params": dict(PARAMS)},
        "rung0_readback": {
            "r0_rule_count": int(len(S.r0_rule_indices())),
            "r0_rule_ids": [int(v) for v in S.r0_rule_indices().tolist()],
            "adapt_values": list(full_values),
            "query_values": list(full_values),
            "sample_train_episode_id": int(train_eps[0].episode_id),
            "sample_heldout_episode_id": int(heldout_eps[0].episode_id),
        },
    }


def build_datasets() -> dict[str, Any]:
    train_eps = S.make_episodes("rung0", "train")
    heldout_eps = S.make_episodes("rung0", "heldout")
    expected_train = int(P.rungs()[S.RUNG0]["n_train_episodes"])
    expected_heldout = int(P.rungs()[S.RUNG0]["n_heldout_episodes"])
    if len(train_eps) != expected_train or len(heldout_eps) != expected_heldout:
        raise StopRung0RetrievalRerun(
            "dataset_counts",
            "rung0 episode count mismatch",
            {"train": len(train_eps), "heldout": len(heldout_eps)},
            {"train": expected_train, "heldout": expected_heldout},
        )
    ideal_mean, _, ideal_scores = ideal_predictions(heldout_eps)
    fair_all, _ = LR.evaluate(heldout_eps, int(P.seeds()["BASELINE_FIT_SEED"]))
    fair = {name: float(fair_all[name]) for name in FAIR_BASELINE_NAMES}
    fair["graph_cache"] = float(max(fair["lookup"], fair["count_table"]))
    return {
        "train": train_eps,
        "heldout": heldout_eps,
        "ideal_balacc": float(ideal_mean),
        "ideal_score_min": float(min(ideal_scores)) if ideal_scores else None,
        "fair_baselines": fair,
        "fair_baseline_max": float(max(fair[name] for name in FAIR_BASELINE_NAMES)),
        "dataset_diagnostics": {
            "train_episodes": len(train_eps),
            "heldout_episodes": len(heldout_eps),
            "r0_rule_ids": [int(v) for v in S.r0_rule_indices().tolist()],
            "train_rule_ids_observed": sorted({int(ep.rule_id) for ep in train_eps}),
            "heldout_rule_ids_observed": sorted({int(ep.rule_id) for ep in heldout_eps}),
            "train_query_adapt_overlap_mean": float(sum(S.query_adapt_overlap_fraction(ep) for ep in train_eps) / len(train_eps)),
            "heldout_query_adapt_overlap_mean": float(sum(S.query_adapt_overlap_fraction(ep) for ep in heldout_eps) / len(heldout_eps)),
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
                fitted = bool(float(train_balacc) >= TRAIN_FIT_THRESHOLD)
                row = {
                    "run_id": run_id,
                    "task_id": TASK_ID,
                    "producer_function": "src.tlgp_capability_witness_preflight_001a.rung0_retrieval_rerun.train_one_seed",
                    "model_function": "src.tlgp_capability_witness_preflight_001a.retrieval_model.RetrievalInContextTransformer",
                    "family": FAMILY,
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
                    "train_balacc": float(train_balacc),
                    "heldout_balacc": float(heldout_balacc),
                    "fitted_train_ge_0_95": fitted,
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
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
                if fitted and float(heldout_balacc) >= HELDOUT_PASS_THRESHOLD:
                    early_stopped = True
                    break
            if steps >= MAX_STEPS:
                break

    if not curve:
        raise StopRung0RetrievalRerun("training", "no checkpoints recorded", {"seed": seed}, ">=1")
    device = _device_record(model, [train_t, heldout_t])
    best_heldout = max(curve, key=lambda row: float(row["heldout_balacc_0b"]))
    best_train = max(curve, key=lambda row: float(row["train_balacc_0a"]))
    final = curve[-1]
    record = {
        "run_id": run_id,
        "task_id": TASK_ID,
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung0_retrieval_rerun.train_one_seed",
        "input_artifacts": [
            "src/tlgp_capability_witness_preflight_001a/retrieval_model.py",
            "src/tlgp_capability_witness_preflight_001a/grokking_probe.py::_eval_checkpoint",
            "src/tlgp_001b_r2/splits.py::make_episodes",
            "src/tlgp_001b_r2/splits.py::r0_rule_indices",
            "src/tlgp_001b_r2/meta_learners.py::build_tensors",
        ],
        "family": FAMILY,
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
        "early_stop_rule": "allowed by frozen design; only when train_balacc_0a >= 0.95 and heldout_balacc_0b >= 0.80 at a checkpoint",
        "budget_capped": bool(steps >= MAX_STEPS),
        "final_train_balacc_0a": float(final["train_balacc_0a"]),
        "final_heldout_balacc_0b": float(final["heldout_balacc_0b"]),
        "best_train_balacc_0a": float(best_train["train_balacc_0a"]),
        "best_train_step": int(best_train["step"]),
        "best_heldout_balacc_0b": float(best_heldout["heldout_balacc_0b"]),
        "best_heldout_step": int(best_heldout["step"]),
        "fitted": bool(float(best_train["train_balacc_0a"]) >= TRAIN_FIT_THRESHOLD),
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


def apply_fit_conditioned_go_no_go(records: list[dict[str, Any]]) -> dict[str, Any]:
    rows_by_seed = {int(row["seed"]): row for row in records if row.get("status") == "completed"}
    missing = [seed for seed in SEEDS if seed not in rows_by_seed]
    if missing:
        verdict = "incomplete"
    else:
        fitted = [rows_by_seed[seed] for seed in SEEDS if bool(rows_by_seed[seed]["fitted"])]
        fitted_pass = [row for row in fitted if float(row["best_heldout_balacc_0b"]) >= HELDOUT_PASS_THRESHOLD]
        if len(fitted_pass) >= 2:
            verdict = "witness_trend_pass"
        elif not fitted:
            verdict = "ambiguous"
        elif all(float(row["best_heldout_balacc_0b"]) <= HELDOUT_FAIL_THRESHOLD for row in fitted):
            verdict = "witness_trend_fail"
        else:
            verdict = "ambiguous"
    return {
        "task_id": TASK_ID,
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung0_retrieval_rerun.apply_fit_conditioned_go_no_go",
        "verdict": verdict,
        "thresholds": {
            "fitted_seed": "best train_balacc_0a >= 0.95",
            "witness_trend_pass": "among FITTED seeds, best heldout_balacc_0b >= 0.80 on >=2 seeds",
            "witness_trend_fail": "all FITTED seeds best heldout_balacc_0b <= 0.65",
            "ambiguous": "0b between 0.65 and 0.80, or no seed fits 0a",
        },
        "missing_completed_runs": missing,
        "fitted_seed_count": sum(1 for row in rows_by_seed.values() if bool(row["fitted"])),
        "heldout_pass_seed_count": sum(
            1 for row in rows_by_seed.values() if bool(row["fitted"]) and float(row["best_heldout_balacc_0b"]) >= HELDOUT_PASS_THRESHOLD
        ),
        "per_seed": {
            str(seed): {
                "best_train_balacc_0a": float(rows_by_seed[seed]["best_train_balacc_0a"]) if seed in rows_by_seed else None,
                "best_train_step": int(rows_by_seed[seed]["best_train_step"]) if seed in rows_by_seed else None,
                "best_heldout_balacc_0b": float(rows_by_seed[seed]["best_heldout_balacc_0b"]) if seed in rows_by_seed else None,
                "best_heldout_step": int(rows_by_seed[seed]["best_heldout_step"]) if seed in rows_by_seed else None,
                "ideal_balacc": float(rows_by_seed[seed]["ideal_balacc"]) if seed in rows_by_seed else None,
                "fair_baseline_max": float(rows_by_seed[seed]["fair_baseline_max"]) if seed in rows_by_seed else None,
                "fitted": bool(rows_by_seed[seed]["fitted"]) if seed in rows_by_seed else None,
                "steps_run": int(rows_by_seed[seed]["steps_run"]) if seed in rows_by_seed else None,
                "early_stopped": bool(rows_by_seed[seed]["early_stopped"]) if seed in rows_by_seed else None,
            }
            for seed in SEEDS
        },
        "claim_ceiling": (
            "bounded 3-seed rung0 trend only; route_decision is underpowered by design and this is not a "
            "route terminal, transfer, mechanism, agency, self, AGI, or EGO claim"
        ),
    }


def build_route_decision_input(records: list[dict[str, Any]], ideal_balacc: float, fair_baselines: dict[str, float]) -> dict[str, Any]:
    rows_by_seed = {int(row["seed"]): row for row in records if row.get("status") == "completed"}
    return {
        "rung": "rung0",
        "ideal_balacc": float(ideal_balacc),
        "fair_baseline_balacc": {name: float(fair_baselines[name]) for name in ["graph_cache", *FAIR_BASELINE_NAMES]},
        "learner_per_seed_balacc": {
            FAMILY: [float(rows_by_seed[seed]["best_heldout_balacc_0b"]) for seed in sorted(rows_by_seed)]
        },
        "n_seeds": len(rows_by_seed),
        "leakage_clean": True,
        "selection_rule": "best heldout checkpoint per seed; fit-conditioned trend verdict uses best train and best heldout",
        "leakage_clean_basis": (
            "rung0 retrieval rerun reuses read-only TLGP rung0 meta inputs: adapt_x/adapt_a/adapt_e/query_x/query_a; "
            "no rule_id or query_e are model inputs"
        ),
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
    route = json.loads((OUT_DIR / "route_decision.json").read_text(encoding="utf-8"))
    if route.get("route") != "inconclusive_underpowered":
        raise StopRung0RetrievalRerun(
            "route_decision",
            "route_decision.py did not return expected underpowered result",
            route.get("route"),
            "inconclusive_underpowered",
        )
    return route


def manifest_payload(
    gate: dict[str, Any],
    run_id: str,
    report: dict[str, Any],
    route: dict[str, Any],
    param_count: int,
) -> dict[str, Any]:
    status = protected_source_status()
    retrieval_sha = MP.sha256_file(RETRIEVAL_MODEL_PATH)
    return {
        **gate,
        "task_id": TASK_ID,
        "run_id": run_id,
        "git_head": git_output(["rev-parse", "HEAD"]).strip(),
        "git_branch": git_output(["branch", "--show-current"]).strip(),
        "gpu_env": ML.device_readback(),
        "model": {"family": FAMILY, "params": dict(PARAMS), "parameter_count": int(param_count)},
        "regime": {
            "rung": "rung0",
            "seeds": list(SEEDS),
            "optimizer": "AdamW",
            "lr": LEARNING_RATE,
            "weight_decay": WEIGHT_DECAY,
            "batch_size": BATCH_SIZE,
            "max_steps": MAX_STEPS,
            "checkpoint_every_steps": CHECKPOINT_EVERY_STEPS,
            "early_stopping": "allowed; implemented only at frozen fitted+heldout pass band",
            "n_train": int(P.rungs()[S.RUNG0]["n_train_episodes"]),
            "n_heldout": int(P.rungs()[S.RUNG0]["n_heldout_episodes"]),
        },
        "artifact_paths": {
            "training_records": str((OUT_DIR / "training_records.json").relative_to(REPO_ROOT).as_posix()),
            "val_curves": str((OUT_DIR / "val_curves.jsonl").relative_to(REPO_ROOT).as_posix()),
            "rerun_report": str((OUT_DIR / "rerun_report.json").relative_to(REPO_ROOT).as_posix()),
            "route_decision_input": str((OUT_DIR / "route_decision_input.json").relative_to(REPO_ROOT).as_posix()),
            "route_decision": str((OUT_DIR / "route_decision.json").relative_to(REPO_ROOT).as_posix()),
            "manifest": str((OUT_DIR / "manifest.json").relative_to(REPO_ROOT).as_posix()),
        },
        "go_no_go_verdict": report.get("verdict"),
        "route_decision_route": route.get("route"),
        "retrieval_model_sha256_after_run": retrieval_sha,
        "retrieval_model_unchanged": retrieval_sha == EXPECTED_RETRIEVAL_MODEL_SHA256,
        "capacity_unchanged": PARAMS == {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4},
        "banked_source_diff_empty": not status and retrieval_sha == EXPECTED_RETRIEVAL_MODEL_SHA256,
        "banked_source_status_after_run": status,
        "retrieval_model_status_after_run": retrieval_model_status(),
        "claim_ceiling": (
            "first bounded 3-seed real rung0 retrieval-model trend only; NOT a powered route terminal, "
            "transfer, mechanism, agency, self, subjectivity, AGI, or EGO claim"
        ),
    }


def run_rerun() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failure_path = OUT_DIR / "failure_manifest.json"
    if failure_path.exists():
        failure_path.unlink()
    for name in (
        "training_records.json",
        "val_curves.jsonl",
        "rerun_report.json",
        "route_decision_input.json",
        "route_decision.json",
        "manifest.json",
    ):
        path = OUT_DIR / name
        if path.exists():
            path.unlink()

    gate = validate_pre_run_gates()
    run_id = time.strftime("tlgp-rung0-retrieval-rerun-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
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

    report = apply_fit_conditioned_go_no_go(records)
    report.update(
        {
            "run_id": run_id,
            "model": {"family": FAMILY, "params": dict(PARAMS), "parameter_count": int(param_count)},
            "ideal_balacc": float(datasets["ideal_balacc"]),
            "ideal_score_min": datasets["ideal_score_min"],
            "fair_baselines": datasets["fair_baselines"],
            "fair_baseline_max": float(datasets["fair_baseline_max"]),
            "dataset_diagnostics": datasets["dataset_diagnostics"],
            "input_artifacts": [
                "docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG0-RETRIEVAL-RERUN-001A.frozen_design.json",
                "src/tlgp_capability_witness_preflight_001a/retrieval_model.py",
                "src/tlgp_capability_witness_preflight_001a/grokking_probe.py::_eval_checkpoint",
                "src/tlgp_001b_r2/splits.py::make_episodes",
                "src/tlgp_001b_r2/lower_reference.py::evaluate",
            ],
        }
    )
    write_json(OUT_DIR / "rerun_report.json", report)
    route_input = build_route_decision_input(records, float(datasets["ideal_balacc"]), datasets["fair_baselines"])
    route = write_route_decision(route_input)
    manifest = manifest_payload(gate, run_id, report, route, param_count)
    write_json(OUT_DIR / "manifest.json", manifest)
    if not manifest["banked_source_diff_empty"]:
        raise StopRung0RetrievalRerun(
            "banked_source_guard_after_run",
            "banked source changed or retrieval model hash drifted",
            {
                "banked_source_status": manifest["banked_source_status_after_run"],
                "retrieval_model_sha256_after_run": manifest["retrieval_model_sha256_after_run"],
            },
            {"banked_source_status": [], "retrieval_model_sha256": EXPECTED_RETRIEVAL_MODEL_SHA256},
        )
    return {"manifest": manifest, "rerun_report": report, "route_decision": route, "records": records}


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
        raise StopRung0RetrievalRerun("model_shape", "unexpected logits shape", tuple(logits.shape), (4, P.N_QUERY, P.K))
    train_balacc, heldout_balacc, _ = _eval_checkpoint(model, train_t, heldout_t)
    param_count = parameter_count(model)
    return {
        "gate": gate,
        "logits_shape": list(logits.shape),
        "parameter_count": int(param_count),
        "eval_smoke": {"train_balacc_0a": float(train_balacc), "heldout_balacc_0b": float(heldout_balacc)},
        "ideal_balacc": float(datasets["ideal_balacc"]),
        "fair_baselines": datasets["fair_baselines"],
        "dataset_diagnostics": datasets["dataset_diagnostics"],
    }


def write_failure_manifest(exc: BaseException) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if isinstance(exc, StopRung0RetrievalRerun):
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
            "claim_ceiling": "no completed rung0 retrieval rerun evidence; task stopped",
        }
    )
    write_json(OUT_DIR / "failure_manifest.json", payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="run frozen 3-seed rung0 retrieval rerun")
    parser.add_argument("--validate-only", action="store_true", help="validate frozen gates without training")
    parser.add_argument("--self-test", action="store_true", help="run model/data/eval smoke without training")
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
        run_rerun()
        return 0
    except BaseException as exc:
        write_failure_manifest(exc)
        print(f"rung0 retrieval rerun stopped: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
