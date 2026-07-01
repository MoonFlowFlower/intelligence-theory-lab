"""Validate the retrieval-capable TLGP in-context model on frozen positive controls."""
from __future__ import annotations

import argparse
import json
import subprocess
import time
import traceback
import uuid
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

from src.tlgp_001b_r2 import meta_learners as ML
from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_001b_r2 import splits as S
from src.tlgp_001b_r2.world import ideal_predictions
from src.tlgp_capability_witness_preflight_001a import minimal_probe as MP
from src.tlgp_capability_witness_preflight_001a import positive_control as PC
from src.tlgp_capability_witness_preflight_001a.positive_control import (
    CONTROLS,
    PC_COPY,
    PC_SINGLE_RULE,
    _eval_checkpoint,
    _make_control_episodes,
    _make_copy_episode,
    _make_single_rule_episode,
    dataset_diagnostics,
)
from src.tlgp_capability_witness_preflight_001a.retrieval_model import (
    FAMILY,
    PARAMS,
    build_model,
    model_card,
    parameter_count,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "TLGP-ICL-RETRIEVAL-RUNNER-001A"
FROZEN_DESIGN_PATH = (
    REPO_ROOT
    / "docs"
    / "task_cards"
    / "TLGP-CAPABILITY-WITNESS-RUNNER-POSITIVE-CONTROL-001A.frozen_design.json"
)
OUT_DIR = (
    REPO_ROOT
    / "artifacts"
    / "TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A"
    / "ICL_RETRIEVAL_RUNNER_001A"
)

EXPECTED_HEAD_PREFIX = "9e3e3d27"
EXPECTED_FROZEN_DESIGN_SHA256 = "90f2a5034747e0153f29ccc86a672a2cfcd8fe75910de54c02966149eeeef56b"
EXPECTED_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"
EXPECTED_META_LEARNERS_SHA256 = "358d2bb2449f88ff5c73de52fcabcbba17f40b22dabc5c484f7b67da627e1b6f"
EXPECTED_POSITIVE_CONTROL_SHA256 = "b06112b59b3388886b5770a628e6361958fe07b004e34d3bf21e08588cf91749"
EXPECTED_GROKKING_PROBE_SHA256 = "9126dc9273c5aac6c909de9d503e323609dca61c6d9e51fadd0d459a89d74555"
EXPECTED_ROUTE_DECISION_SHA256 = "0dcf3659df802912ff2f760e9875526887e14c4c14d1e0cc91c0cb4d8863c0c8"

SEEDS = [20260710, 20260711]
LEARNING_RATE = 0.0003
WEIGHT_DECAY = 0.1
BATCH_SIZE = 256
MAX_STEPS = 20_000
CHECKPOINT_EVERY_STEPS = 2_000
RUNNER_OK_COPY_THRESHOLD = 0.95
RUNNER_OK_SINGLE_RULE_THRESHOLD = 0.85
COPY_FAIL_THRESHOLD = 0.70

BANKED_HASH_PATHS = {
    "meta_learners_sha256": (REPO_ROOT / "src" / "tlgp_001b_r2" / "meta_learners.py", EXPECTED_META_LEARNERS_SHA256),
    "positive_control_sha256": (
        REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "positive_control.py",
        EXPECTED_POSITIVE_CONTROL_SHA256,
    ),
    "grokking_probe_sha256": (
        REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "grokking_probe.py",
        EXPECTED_GROKKING_PROBE_SHA256,
    ),
    "route_decision_sha256": (
        REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "route_decision.py",
        EXPECTED_ROUTE_DECISION_SHA256,
    ),
}


class StopRetrievalRunner(RuntimeError):
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
        raise StopRetrievalRunner("git_readback", proc.stderr.strip(), args, "git command succeeds")
    return proc.stdout


def canonical_frozen_design_sha256() -> str:
    obj = json.loads(FROZEN_DESIGN_PATH.read_text(encoding="utf-8"))
    return MP._canonical_sha256(MP._strip_underscore_keys(obj))


def banked_status() -> list[str]:
    return git_output(
        [
            "status",
            "--porcelain",
            "--",
            "src/tlgp_001b_r2",
            "src/tlgp_001a",
            "src/tlgp_capability_witness_preflight_001a/positive_control.py",
            "src/tlgp_capability_witness_preflight_001a/grokking_probe.py",
            "src/tlgp_capability_witness_preflight_001a/route_decision.py",
        ]
    ).splitlines()


def validate_pre_run_gates() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    branch = git_output(["branch", "--show-current"]).strip()
    head = git_output(["rev-parse", "HEAD"]).strip()
    if branch != "codex/meta-theory-scaffold" or not head.startswith(EXPECTED_HEAD_PREFIX):
        raise StopRetrievalRunner(
            "repo_state",
            "unexpected branch or HEAD",
            {"branch": branch, "head": head},
            {"branch": "codex/meta-theory-scaffold", "head_prefix": EXPECTED_HEAD_PREFIX},
        )
    frozen_sha = canonical_frozen_design_sha256()
    prereg_sha = MP.canonical_prereg_sha256()
    if frozen_sha != EXPECTED_FROZEN_DESIGN_SHA256:
        raise StopRetrievalRunner("frozen_design_sha", "frozen design mismatch", frozen_sha, EXPECTED_FROZEN_DESIGN_SHA256)
    if prereg_sha != EXPECTED_PREREG_SHA256:
        raise StopRetrievalRunner("prereg_sha", "prereg mismatch", prereg_sha, EXPECTED_PREREG_SHA256)
    hash_readback: dict[str, str] = {}
    for name, (path, expected) in BANKED_HASH_PATHS.items():
        observed = MP.sha256_file(path)
        hash_readback[name] = observed
        if observed != expected:
            raise StopRetrievalRunner(name, f"{path.relative_to(REPO_ROOT).as_posix()} hash mismatch", observed, expected)
    status = banked_status()
    if status:
        raise StopRetrievalRunner("banked_source_guard", "banked source status is not empty", status, [])
    if not torch.cuda.is_available() or str(ML.DEVICE) != "cuda:0":
        raise StopRetrievalRunner("cuda_guard", "CUDA cuda:0 unavailable", str(ML.DEVICE), "cuda:0")
    if PARAMS != {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4}:
        raise StopRetrievalRunner("capacity_guard", "retrieval model capacity changed", PARAMS, "256/4/4/4")
    return {
        "positive_control_frozen_design_sha256": frozen_sha,
        "prereg_sha256": prereg_sha,
        **hash_readback,
        "git_head": head,
        "git_branch": branch,
        "banked_source_diff_empty": True,
        "banked_source_status": [],
        "capacity": {"family": FAMILY, "params": PARAMS},
    }


def episode_counts() -> tuple[int, int]:
    rung0 = P.rungs()[S.RUNG0]
    return int(rung0["n_train_episodes"]), int(rung0["n_heldout_episodes"])


def build_control_datasets() -> dict[str, dict[str, Any]]:
    n_train, n_heldout = episode_counts()
    datasets: dict[str, dict[str, Any]] = {}
    for control in CONTROLS:
        train_eps = _make_control_episodes(control, "train", n_train)
        heldout_eps = _make_control_episodes(control, "heldout", n_heldout)
        ideal_mean, _, ideal_scores = ideal_predictions(heldout_eps)
        datasets[control] = {
            "train": train_eps,
            "heldout": heldout_eps,
            "ideal_balacc": float(ideal_mean),
            "ideal_scores_min": float(min(ideal_scores)) if ideal_scores else None,
            "diagnostics": dataset_diagnostics(control, train_eps, heldout_eps),
        }
    return datasets


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


def _target_for_control(control: str) -> float:
    if control == PC_COPY:
        return RUNNER_OK_COPY_THRESHOLD
    if control == PC_SINGLE_RULE:
        return RUNNER_OK_SINGLE_RULE_THRESHOLD
    raise ValueError(control)


def train_one_validation_run(
    *,
    run_id: str,
    control: str,
    seed: int,
    train_t: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    heldout_t: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    ideal_balacc: float,
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
    early_stop_threshold = _target_for_control(control)
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
                    "producer_function": "src.tlgp_capability_witness_preflight_001a.icl_retrieval_runner.train_one_validation_run",
                    "model_function": "src.tlgp_capability_witness_preflight_001a.retrieval_model.RetrievalInContextTransformer",
                    "control": control,
                    "family": FAMILY,
                    "params": PARAMS,
                    "parameter_count": int(param_count),
                    "seed": int(seed),
                    "weight_decay": WEIGHT_DECAY,
                    "lr": LEARNING_RATE,
                    "optimizer": "AdamW",
                    "batch_size": BATCH_SIZE,
                    "max_steps": MAX_STEPS,
                    "checkpoint_every_steps": CHECKPOINT_EVERY_STEPS,
                    "checkpoint_index": checkpoint_index,
                    "step": int(steps),
                    "epoch": int(epochs),
                    "train_balacc": float(train_balacc),
                    "heldout_balacc": float(heldout_balacc),
                    "ideal_balacc": float(ideal_balacc),
                    "early_stop_threshold": float(early_stop_threshold),
                    "elapsed_sec": round(time.time() - started, 3),
                }
                checkpoint_index += 1
                curve.append(row)
                _write_curve_row(curve_handle, row)
                print(
                    json.dumps(
                        {
                            "event": "checkpoint",
                            "control": control,
                            "seed": int(seed),
                            "step": int(steps),
                            "train_balacc": round(float(train_balacc), 6),
                            "heldout_balacc": round(float(heldout_balacc), 6),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
                if float(train_balacc) >= early_stop_threshold and float(heldout_balacc) >= early_stop_threshold:
                    early_stopped = True
                    break
            if steps >= MAX_STEPS:
                break

    if not curve:
        raise StopRetrievalRunner("training", "no checkpoints recorded", {"control": control, "seed": seed}, ">=1")
    device = _device_record(model, [train_t, heldout_t])
    best = max(curve, key=lambda row: float(row["heldout_balacc"]))
    final = curve[-1]
    record = {
        "run_id": run_id,
        "task_id": TASK_ID,
        "producer_function": "src.tlgp_capability_witness_preflight_001a.icl_retrieval_runner.train_one_validation_run",
        "input_artifacts": [
            "src/tlgp_capability_witness_preflight_001a/retrieval_model.py",
            "src/tlgp_capability_witness_preflight_001a/positive_control.py",
            "src/tlgp_capability_witness_preflight_001a/grokking_probe.py::_eval_checkpoint",
            "src/tlgp_001b_r2/meta_learners.py::build_tensors",
        ],
        "control": control,
        "family": FAMILY,
        "params": PARAMS,
        "parameter_count": int(param_count),
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
        "early_stop_threshold": float(early_stop_threshold),
        "budget_capped": bool(steps >= MAX_STEPS),
        "final_train_balacc": float(final["train_balacc"]),
        "final_heldout_balacc": float(final["heldout_balacc"]),
        "best_heldout_balacc": float(best["heldout_balacc"]),
        "best_heldout_step": int(best["step"]),
        "ideal_balacc": float(ideal_balacc),
        "num_checkpoints": len(curve),
        "device": device,
        "aggregation_rule": "mean over episodes of per-episode balanced_accuracy",
    }
    del model
    torch.cuda.empty_cache()
    return record


def apply_go_no_go(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_control_seed: dict[str, dict[int, dict[str, Any]]] = {control: {} for control in CONTROLS}
    for record in records:
        if record.get("status") == "completed":
            by_control_seed[str(record["control"])][int(record["seed"])] = record
    missing = {control: [seed for seed in SEEDS if seed not in rows] for control, rows in by_control_seed.items()}
    if any(missing[control] for control in missing):
        verdict = "incomplete"
    else:
        copy_scores = [float(by_control_seed[PC_COPY][seed]["best_heldout_balacc"]) for seed in SEEDS]
        single_scores = [float(by_control_seed[PC_SINGLE_RULE][seed]["best_heldout_balacc"]) for seed in SEEDS]
        if all(score >= RUNNER_OK_COPY_THRESHOLD for score in copy_scores) and all(
            score >= RUNNER_OK_SINGLE_RULE_THRESHOLD for score in single_scores
        ):
            verdict = "runner_ok"
        elif any(score < COPY_FAIL_THRESHOLD for score in copy_scores):
            verdict = "runner_copy_fail"
        elif all(score >= RUNNER_OK_COPY_THRESHOLD for score in copy_scores) and any(
            score < COPY_FAIL_THRESHOLD for score in single_scores
        ):
            verdict = "representational_limit"
        else:
            verdict = "ambiguous"
    return {
        "task_id": TASK_ID,
        "producer_function": "src.tlgp_capability_witness_preflight_001a.icl_retrieval_runner.apply_go_no_go",
        "verdict": verdict,
        "thresholds": {
            "runner_ok": "PC_COPY heldout >= 0.95 all seeds AND PC_SINGLE_RULE heldout >= 0.85 all seeds",
            "runner_copy_fail": "PC_COPY heldout < 0.70 any seed",
            "representational_limit": "PC_COPY heldout >= 0.95 all seeds AND PC_SINGLE_RULE heldout < 0.70 any seed",
            "ambiguous": "anything else",
        },
        "missing_completed_runs": missing,
        "per_control_seed": {
            control: {
                str(seed): {
                    "best_heldout_balacc": float(by_control_seed[control][seed]["best_heldout_balacc"])
                    if seed in by_control_seed[control]
                    else None,
                    "best_heldout_step": int(by_control_seed[control][seed]["best_heldout_step"])
                    if seed in by_control_seed[control]
                    else None,
                    "final_heldout_balacc": float(by_control_seed[control][seed]["final_heldout_balacc"])
                    if seed in by_control_seed[control]
                    else None,
                    "ideal_balacc": float(by_control_seed[control][seed]["ideal_balacc"])
                    if seed in by_control_seed[control]
                    else None,
                    "early_stopped": bool(by_control_seed[control][seed]["early_stopped"])
                    if seed in by_control_seed[control]
                    else None,
                    "steps_run": int(by_control_seed[control][seed]["steps_run"]) if seed in by_control_seed[control] else None,
                }
                for seed in SEEDS
            }
            for control in CONTROLS
        },
        "claim_ceiling": (
            "retrieval-runner validation against frozen positive controls only; not a TLGP route terminal, "
            "mechanism, transfer, agency, self, AGI, or EGO claim"
        ),
    }


def manifest_payload(gate: dict[str, Any], run_id: str, validation_report: dict[str, Any], param_count: int) -> dict[str, Any]:
    status = banked_status()
    return {
        **gate,
        "task_id": TASK_ID,
        "run_id": run_id,
        "gpu_env": {
            "torch_version": torch.__version__,
            "selected_device": str(ML.DEVICE),
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
            "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        },
        "retrieval_model_sha256": MP.sha256_file(REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "retrieval_model.py"),
        "validation_runner_sha256": MP.sha256_file(Path(__file__).resolve()),
        "model": {"family": FAMILY, "params": PARAMS, "parameter_count": int(param_count)},
        "regime": {
            "controls": CONTROLS,
            "seeds": SEEDS,
            "optimizer": "AdamW",
            "lr": LEARNING_RATE,
            "weight_decay": WEIGHT_DECAY,
            "batch_size": BATCH_SIZE,
            "max_steps": MAX_STEPS,
            "checkpoint_every_steps": CHECKPOINT_EVERY_STEPS,
            "early_stopping": "enabled at frozen control threshold per control",
        },
        "artifact_paths": {
            "training_records": str((OUT_DIR / "training_records.json").relative_to(REPO_ROOT).as_posix()),
            "val_curves": str((OUT_DIR / "val_curves.jsonl").relative_to(REPO_ROOT).as_posix()),
            "validation_report": str((OUT_DIR / "validation_report.json").relative_to(REPO_ROOT).as_posix()),
            "model_card": str((OUT_DIR / "model_card.json").relative_to(REPO_ROOT).as_posix()),
            "manifest": str((OUT_DIR / "manifest.json").relative_to(REPO_ROOT).as_posix()),
        },
        "go_no_go_verdict": validation_report.get("verdict"),
        "banked_source_diff_empty": not status,
        "banked_source_status_after_run": status,
        "claim_ceiling": (
            "instrument-repair validation only; does not alter banked TLGP verdicts and does not authorize "
            "capability-witness probe claims inside this task"
        ),
    }


def run_validation() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failure_path = OUT_DIR / "failure_manifest.json"
    if failure_path.exists():
        failure_path.unlink()
    for name in ("training_records.json", "val_curves.jsonl", "validation_report.json", "model_card.json", "manifest.json"):
        path = OUT_DIR / name
        if path.exists():
            path.unlink()
    gate = validate_pre_run_gates()
    run_id = time.strftime("tlgp-icl-retrieval-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
    model = build_model(PARAMS).to(ML.DEVICE)
    param_count = parameter_count(model)
    write_json(OUT_DIR / "model_card.json", model_card(param_count))
    del model
    torch.cuda.empty_cache()

    datasets = build_control_datasets()
    records: list[dict[str, Any]] = []
    curve_path = OUT_DIR / "val_curves.jsonl"
    with curve_path.open("w", encoding="utf-8") as curve_handle:
        for control in CONTROLS:
            train_t = ML.move_tensors(ML.build_tensors(datasets[control]["train"]))
            heldout_t = ML.move_tensors(ML.build_tensors(datasets[control]["heldout"]))
            for seed in SEEDS:
                record = train_one_validation_run(
                    run_id=run_id,
                    control=control,
                    seed=int(seed),
                    train_t=train_t,
                    heldout_t=heldout_t,
                    ideal_balacc=float(datasets[control]["ideal_balacc"]),
                    param_count=param_count,
                    curve_handle=curve_handle,
                )
                records.append(record)
                write_json(OUT_DIR / "training_records.json", records)
    report = apply_go_no_go(records)
    report.update(
        {
            "run_id": run_id,
            "model": {"family": FAMILY, "params": PARAMS, "parameter_count": int(param_count)},
            "ideal_balacc_by_control": {control: float(datasets[control]["ideal_balacc"]) for control in CONTROLS},
            "dataset_diagnostics": {control: datasets[control]["diagnostics"] for control in CONTROLS},
            "input_artifacts": [
                "docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNNER-POSITIVE-CONTROL-001A.frozen_design.json",
                "src/tlgp_capability_witness_preflight_001a/positive_control.py",
                "src/tlgp_capability_witness_preflight_001a/retrieval_model.py",
            ],
        }
    )
    write_json(OUT_DIR / "validation_report.json", report)
    manifest = manifest_payload(gate, run_id, report, param_count)
    write_json(OUT_DIR / "manifest.json", manifest)
    if not manifest["banked_source_diff_empty"]:
        raise StopRetrievalRunner("banked_source_guard_after_run", "banked source status changed", manifest["banked_source_status_after_run"], [])
    return {"manifest": manifest, "validation_report": report, "records": records}


def self_test() -> dict[str, Any]:
    gate = validate_pre_run_gates()
    _ = _make_copy_episode
    _ = _make_single_rule_episode
    datasets = build_control_datasets()
    train_t = ML.move_tensors(ML.build_tensors(datasets[PC_COPY]["train"][:4]))
    heldout_t = ML.move_tensors(ML.build_tensors(datasets[PC_COPY]["heldout"][:4]))
    model = build_model(PARAMS).to(ML.DEVICE)
    ctx, qx, _qy = train_t
    logits = model(ctx, qx)
    if tuple(logits.shape) != (4, P.N_QUERY, P.K):
        raise StopRetrievalRunner("model_shape", "unexpected logits shape", tuple(logits.shape), (4, P.N_QUERY, P.K))
    eval_train, eval_heldout, _ = _eval_checkpoint(model, train_t, heldout_t)
    param_count = parameter_count(model)
    return {
        "gate": gate,
        "logits_shape": list(logits.shape),
        "eval_smoke": {"train_balacc": eval_train, "heldout_balacc": eval_heldout},
        "parameter_count": param_count,
        "model_card": model_card(param_count),
    }


def write_failure_manifest(exc: BaseException) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if isinstance(exc, StopRetrievalRunner):
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
            "claim_ceiling": "no retrieval-runner validation verdict; task stopped",
        }
    )
    write_json(OUT_DIR / "failure_manifest.json", payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="run frozen ICL retrieval validation")
    parser.add_argument("--validate-only", action="store_true", help="validate source pins and CUDA only")
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
        run_validation()
        return 0
    except BaseException as exc:
        write_failure_manifest(exc)
        print(f"ICL retrieval runner stopped: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
