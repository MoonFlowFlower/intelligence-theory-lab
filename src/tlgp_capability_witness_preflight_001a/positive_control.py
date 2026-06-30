"""Positive controls for TLGP capability-witness runner validation.

This module is intentionally isolated. It reuses the banked grokking runner's
model/training/eval path read-only and changes only the episode construction.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
import traceback
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch

from src.tlgp_001a.world import Episode, enumerate_rules
from src.tlgp_001b_r2 import meta_learners as ML
from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_001b_r2 import splits as S
from src.tlgp_001b_r2.world import ideal_predictions, make_episode_for_rule
from src.tlgp_capability_witness_preflight_001a import grokking_probe as GP
from src.tlgp_capability_witness_preflight_001a import minimal_probe as MP
from src.tlgp_capability_witness_preflight_001a.grokking_probe import (
    _eval_checkpoint,
    train_one_grokking_run as _banked_train_one_grokking_run,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "TLGP-CAPABILITY-WITNESS-RUNNER-POSITIVE-CONTROL-001A"
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
    / "RUNNER_POSITIVE_CONTROL_001A"
)

EXPECTED_FROZEN_DESIGN_SHA256 = "90f2a5034747e0153f29ccc86a672a2cfcd8fe75910de54c02966149eeeef56b"
EXPECTED_GROKKING_PROBE_SHA256 = "9126dc9273c5aac6c909de9d503e323609dca61c6d9e51fadd0d459a89d74555"
EXPECTED_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"

FAMILY = "in_context_transformer"
PARAMS = {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4}
SEEDS = [20260710, 20260711]
LEARNING_RATE = 0.0003
WEIGHT_DECAY = 0.1
BATCH_SIZE = 256
MAX_STEPS = 20_000
CHECKPOINT_EVERY_STEPS = 2_000

PC_COPY = "PC_COPY"
PC_SINGLE_RULE = "PC_SINGLE_RULE"
CONTROLS = [PC_COPY, PC_SINGLE_RULE]

PROTECTED_PATHS = [
    "src/tlgp_capability_witness_preflight_001a/grokking_probe.py",
    "src/tlgp_capability_witness_preflight_001a/route_decision.py",
    "src/tlgp_001b_r2",
    "src/tlgp_001a",
]


class StopPositiveControl(RuntimeError):
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
        raise StopPositiveControl("git_readback", proc.stderr.strip(), args, "git command succeeds")
    return proc.stdout


def canonical_frozen_design_sha256(path: Path = FROZEN_DESIGN_PATH) -> str:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return MP._canonical_sha256(MP._strip_underscore_keys(obj))


def protected_source_status() -> list[str]:
    return git_output(["status", "--porcelain=v1", "--", *PROTECTED_PATHS]).splitlines()


def protected_source_diff() -> list[str]:
    return git_output(["diff", "--name-only", "--", *PROTECTED_PATHS]).splitlines()


def validate_pre_run_gates() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frozen_sha = canonical_frozen_design_sha256()
    grokking_sha = MP.sha256_file(REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "grokking_probe.py")
    prereg_sha = MP.canonical_prereg_sha256()
    if frozen_sha != EXPECTED_FROZEN_DESIGN_SHA256:
        raise StopPositiveControl(
            "frozen_design_sha",
            "frozen design canonical sha mismatch",
            frozen_sha,
            EXPECTED_FROZEN_DESIGN_SHA256,
        )
    if grokking_sha != EXPECTED_GROKKING_PROBE_SHA256:
        raise StopPositiveControl(
            "grokking_probe_sha",
            "grokking_probe.py sha mismatch",
            grokking_sha,
            EXPECTED_GROKKING_PROBE_SHA256,
        )
    if prereg_sha != EXPECTED_PREREG_SHA256:
        raise StopPositiveControl("prereg_sha", "prereg canonical sha mismatch", prereg_sha, EXPECTED_PREREG_SHA256)
    status = protected_source_status()
    diff = protected_source_diff()
    if status or diff:
        raise StopPositiveControl(
            "banked_source_guard",
            "protected banked source status is not empty",
            {"status": status, "diff": diff},
            {"status": [], "diff": []},
        )
    witness = ML.witness_params(FAMILY)
    if PARAMS != witness:
        raise StopPositiveControl("capacity_guard", "capacity differs from witness params", PARAMS, witness)
    design = json.loads(FROZEN_DESIGN_PATH.read_text(encoding="utf-8"))
    design_capacity = {
        "d_model": int(design["capacity_FROZEN"]["d_model"]),
        "layers": int(design["capacity_FROZEN"]["layers"]),
        "heads": int(design["capacity_FROZEN"]["heads"]),
        "ff_mult": int(design["capacity_FROZEN"]["ff_mult"]),
    }
    if design_capacity != PARAMS or design["capacity_FROZEN"].get("learner") != FAMILY:
        raise StopPositiveControl(
            "frozen_capacity_guard",
            "frozen design capacity differs from positive-control runner",
            {"family": design["capacity_FROZEN"].get("learner"), "params": design_capacity},
            {"family": FAMILY, "params": PARAMS},
        )
    if not torch.cuda.is_available() or str(ML.DEVICE) != "cuda:0":
        raise StopPositiveControl("cuda_guard", "CUDA cuda:0 unavailable", str(ML.DEVICE), "cuda:0")
    return {
        "frozen_design_sha256": frozen_sha,
        "grokking_probe_sha256": grokking_sha,
        "prereg_sha256": prereg_sha,
        "capacity_unchanged": True,
        "banked_source_diff_empty": True,
        "banked_source_status_empty": True,
        "protected_source_status": [],
        "protected_source_diff": [],
    }


def _full_values() -> tuple[int, ...]:
    return tuple(range(P.K))


def _episode_counts() -> tuple[int, int]:
    rung0 = P.rungs()[S.RUNG0]
    return int(rung0["n_train_episodes"]), int(rung0["n_heldout_episodes"])


def _rule_pool() -> list[int]:
    return [int(v) for v in S.r0_rule_indices().tolist()]


def _fixed_single_rule_id() -> int:
    rules = enumerate_rules()
    for rid in _rule_pool():
        rule = rules[int(rid)]
        if all(int(v) != 0 for v in rule.w) and int(rule.c) != 0:
            return int(rid)
    return int(_rule_pool()[0])


def _effect_array(rule, x: np.ndarray, a: np.ndarray) -> np.ndarray:
    return np.array([rule.effect(tuple(int(v) for v in row), int(act)) for row, act in zip(x, a)], dtype=int)


def _coverage_xa(rng: np.random.Generator, n: int) -> tuple[np.ndarray, np.ndarray]:
    values = np.array(_full_values(), dtype=int)
    x = rng.choice(values, size=(int(n), P.D), replace=True).astype(int)
    a = rng.integers(0, P.ACTION_CARD, size=int(n)).astype(int)
    row = 0
    for dim in range(P.D):
        for value in values:
            if row >= n:
                break
            x[row, :] = rng.choice(values, size=P.D, replace=True)
            x[row, dim] = int(value)
            a[row] = int(value % P.ACTION_CARD)
            row += 1
    for value in values:
        if row >= n:
            break
        x[row, :] = int(value)
        a[row] = int(value % P.ACTION_CARD)
        row += 1
    return x, a


def _make_base_episode(episode_id: int, rule_id: int, rng: np.random.Generator) -> Episode:
    return make_episode_for_rule(
        episode_id,
        int(rule_id),
        rng,
        adapt_values=_full_values(),
        query_values=_full_values(),
        n_adapt=P.N_ADAPT,
        n_query=P.N_QUERY,
    )


def _make_copy_episode(episode_id: int, rule_id: int, rng: np.random.Generator) -> Episode:
    ep = _make_base_episode(episode_id, rule_id, rng)
    chosen = rng.integers(0, P.N_ADAPT, size=P.N_QUERY)
    ep.query_x = ep.adapt_x[chosen].copy()
    ep.query_a = ep.adapt_a[chosen].copy()
    ep.query_e = ep.adapt_e[chosen].copy()
    return ep


def _make_single_rule_episode(episode_id: int, rule_id: int, rng: np.random.Generator) -> Episode:
    ep = _make_base_episode(episode_id, rule_id, rng)
    ep.adapt_x, ep.adapt_a = _coverage_xa(rng, P.N_ADAPT)
    ep.query_x, ep.query_a = _coverage_xa(rng, P.N_QUERY)
    ep.adapt_e = _effect_array(ep.rule, ep.adapt_x, ep.adapt_a)
    ep.query_e = _effect_array(ep.rule, ep.query_x, ep.query_a)
    return ep


def _make_control_episodes(control: str, split: str, n_episodes: int) -> list[Episode]:
    if split not in {"train", "heldout"}:
        raise ValueError(split)
    seed_key = "RUNG0_TRAIN_EPISODES_SEED" if split == "train" else "RUNG0_HELDOUT_EPISODES_SEED"
    seed_offset = 10_000 if control == PC_COPY else 20_000
    rng = np.random.default_rng(int(P.seeds()[seed_key]) + seed_offset)
    base_id = 60_000_000 if control == PC_COPY else 70_000_000
    base_id += 0 if split == "train" else 1_000_000
    pool = _rule_pool()
    fixed_rule = _fixed_single_rule_id()
    episodes: list[Episode] = []
    for i in range(int(n_episodes)):
        if control == PC_COPY:
            rule_id = int(pool[int(rng.integers(0, len(pool)))])
            episodes.append(_make_copy_episode(base_id + i, rule_id, rng))
        elif control == PC_SINGLE_RULE:
            episodes.append(_make_single_rule_episode(base_id + i, fixed_rule, rng))
        else:
            raise ValueError(control)
    return episodes


def dataset_diagnostics(control: str, train_eps: list[Episode], heldout_eps: list[Episode]) -> dict[str, Any]:
    def copy_overlap(episodes: list[Episode]) -> float:
        vals = []
        for ep in episodes:
            adapt = {(tuple(int(v) for v in x), int(a)) for x, a in zip(ep.adapt_x, ep.adapt_a)}
            hits = sum(1 for x, a in zip(ep.query_x, ep.query_a) if (tuple(int(v) for v in x), int(a)) in adapt)
            vals.append(float(hits / len(ep.query_a)))
        return float(np.mean(vals)) if vals else 0.0

    def coverage(episodes: list[Episode], attr: str) -> dict[str, Any]:
        arrays = [getattr(ep, attr) for ep in episodes[: min(20, len(episodes))]]
        if not arrays:
            return {"checked_episodes": 0}
        if attr.endswith("_x"):
            ok = [
                all(set(int(v) for v in arr[:, dim].tolist()) == set(_full_values()) for dim in range(P.D))
                for arr in arrays
            ]
        else:
            ok = [set(int(v) for v in arr.tolist()) == set(_full_values()) for arr in arrays]
        return {"checked_episodes": len(arrays), "all_full_coverage": bool(all(ok))}

    return {
        "control": control,
        "train_episodes": len(train_eps),
        "heldout_episodes": len(heldout_eps),
        "copy_overlap_train_mean": copy_overlap(train_eps),
        "copy_overlap_heldout_mean": copy_overlap(heldout_eps),
        "fixed_single_rule_id": _fixed_single_rule_id() if control == PC_SINGLE_RULE else None,
        "single_rule_full_coverage_sample": {
            "adapt_x": coverage(train_eps, "adapt_x"),
            "adapt_a": coverage(train_eps, "adapt_a"),
            "query_x": coverage(heldout_eps, "query_x"),
            "query_a": coverage(heldout_eps, "query_a"),
        }
        if control == PC_SINGLE_RULE
        else None,
    }


class CurveWriter:
    def __init__(self, handle, *, task_id: str, control: str, ideal_balacc: float, code_path_hash: str):
        self.handle = handle
        self.task_id = task_id
        self.control = control
        self.ideal_balacc = float(ideal_balacc)
        self.code_path_hash = code_path_hash

    def write(self, text: str) -> int:
        if not text.strip():
            return self.handle.write(text)
        row = json.loads(text)
        row.update(
            {
                "task_id": self.task_id,
                "control": self.control,
                "ideal_balacc": self.ideal_balacc,
                "code_path_hash": self.code_path_hash,
                "banked_training_step": (
                    "src.tlgp_capability_witness_preflight_001a.grokking_probe"
                    ".train_one_grokking_run"
                ),
            }
        )
        return self.handle.write(json.dumps(row, sort_keys=True) + "\n")

    def flush(self) -> None:
        self.handle.flush()


@contextmanager
def patched_grokking_regime():
    old = {
        "LEARNING_RATE": GP.LEARNING_RATE,
        "WEIGHT_DECAYS": GP.WEIGHT_DECAYS,
        "BATCH_SIZE": GP.BATCH_SIZE,
        "MAX_STEPS": GP.MAX_STEPS,
        "CHECKPOINT_EVERY_STEPS": GP.CHECKPOINT_EVERY_STEPS,
        "SEEDS": GP.SEEDS,
        "PARAMS": GP.PARAMS,
        "FAMILY": GP.FAMILY,
    }
    GP.LEARNING_RATE = LEARNING_RATE
    GP.WEIGHT_DECAYS = [WEIGHT_DECAY]
    GP.BATCH_SIZE = BATCH_SIZE
    GP.MAX_STEPS = MAX_STEPS
    GP.CHECKPOINT_EVERY_STEPS = CHECKPOINT_EVERY_STEPS
    GP.SEEDS = list(SEEDS)
    GP.PARAMS = dict(PARAMS)
    GP.FAMILY = FAMILY
    try:
        yield
    finally:
        for key, value in old.items():
            setattr(GP, key, value)


def build_control_datasets() -> dict[str, dict[str, Any]]:
    n_train, n_heldout = _episode_counts()
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


def apply_go_no_go(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_control_seed: dict[str, dict[int, dict[str, Any]]] = {control: {} for control in CONTROLS}
    for record in records:
        if record.get("status") != "completed":
            continue
        by_control_seed[str(record["control"])][int(record["seed"])] = record
    missing = {
        control: [seed for seed in SEEDS if seed not in by_seed]
        for control, by_seed in by_control_seed.items()
    }
    if any(missing[control] for control in missing):
        verdict = "incomplete"
    else:
        copy_scores = [float(by_control_seed[PC_COPY][seed]["best_heldout_balacc"]) for seed in SEEDS]
        single_scores = [float(by_control_seed[PC_SINGLE_RULE][seed]["best_heldout_balacc"]) for seed in SEEDS]
        if all(score >= 0.95 for score in copy_scores) and all(score >= 0.85 for score in single_scores):
            verdict = "runner_ok"
        elif any(score < 0.70 for score in copy_scores):
            verdict = "runner_copy_fail"
        elif all(score >= 0.95 for score in copy_scores) and any(score < 0.70 for score in single_scores):
            verdict = "representational_limit"
        else:
            verdict = "ambiguous"
    per_control_seed = {
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
            }
            for seed in SEEDS
        }
        for control in CONTROLS
    }
    return {
        "verdict": verdict,
        "thresholds": {
            "runner_ok": "PC_COPY heldout >= 0.95 all seeds AND PC_SINGLE_RULE heldout >= 0.85 all seeds",
            "runner_copy_fail": "PC_COPY heldout < 0.70 any seed",
            "representational_limit": "PC_COPY heldout >= 0.95 all seeds AND PC_SINGLE_RULE heldout < 0.70 any seed",
            "ambiguous": "anything else",
        },
        "missing_completed_runs": missing,
        "per_control_seed": per_control_seed,
        "claim_ceiling": (
            "instrument-validation evidence only; not a TLGP route terminal and not a mechanism, "
            "agency, self, subjectivity, AGI, EGO, or companion-readiness claim"
        ),
    }


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT).as_posix())


def make_manifest(gate: dict[str, Any], run_id: str, report: dict[str, Any]) -> dict[str, Any]:
    end_status = protected_source_status()
    end_diff = protected_source_diff()
    positive_control_sha = MP.sha256_file(Path(__file__).resolve())
    return {
        **gate,
        "task_id": TASK_ID,
        "run_id": run_id,
        "git_head": git_output(["rev-parse", "HEAD"]).strip(),
        "git_branch": git_output(["branch", "--show-current"]).strip(),
        "gpu_env": ML.device_readback(),
        "capacity": {"family": FAMILY, "params": PARAMS},
        "capacity_frozen_expected": {"family": FAMILY, "params": PARAMS},
        "positive_control_sha256": positive_control_sha,
        "artifact_paths": {
            "training_records": _relative(OUT_DIR / "training_records.json"),
            "val_curves": _relative(OUT_DIR / "val_curves.jsonl"),
            "positive_control_report": _relative(OUT_DIR / "positive_control_report.json"),
            "manifest": _relative(OUT_DIR / "manifest.json"),
        },
        "regime": {
            "controls": CONTROLS,
            "seeds": SEEDS,
            "optimizer": "AdamW",
            "lr": LEARNING_RATE,
            "weight_decay": WEIGHT_DECAY,
            "batch_size": BATCH_SIZE,
            "max_steps": MAX_STEPS,
            "checkpoint_every_steps": CHECKPOINT_EVERY_STEPS,
            "early_stopping": "not_used; allowed by card",
        },
        "banked_runner_reuse": {
            "model": "src.tlgp_001b_r2.meta_learners.build_model via grokking_probe training loop",
            "training_step": (
                "src.tlgp_capability_witness_preflight_001a.grokking_probe"
                ".train_one_grokking_run"
            ),
            "eval_checkpoint": (
                "src.tlgp_capability_witness_preflight_001a.grokking_probe"
                "._eval_checkpoint"
            ),
            "world_helpers": [
                "src.tlgp_001b_r2.world.make_episode_for_rule",
                "src.tlgp_001b_r2.world.ideal_predictions",
            ],
        },
        "capacity_unchanged": True,
        "banked_source_diff_empty": not end_status and not end_diff,
        "banked_source_status_after_run": end_status,
        "banked_source_diff_after_run": end_diff,
        "go_no_go_verdict": report.get("verdict"),
        "claim_ceiling": (
            "instrument-validation evidence only; confirms/refutes runner easy-task behavior only. "
            "Does not change banked TLGP verdicts."
        ),
    }


def run_positive_controls() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failure_path = OUT_DIR / "failure_manifest.json"
    if failure_path.exists():
        failure_path.unlink()
    for name in ("training_records.json", "val_curves.jsonl", "positive_control_report.json", "manifest.json"):
        path = OUT_DIR / name
        if path.exists():
            path.unlink()
    gate = validate_pre_run_gates()
    run_id = time.strftime("tlgp-runner-posctl-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
    code_path_hash = MP.sha256_file(Path(__file__).resolve())
    datasets = build_control_datasets()
    records: list[dict[str, Any]] = []
    ML.reset_device_runs()
    curve_path = OUT_DIR / "val_curves.jsonl"
    with curve_path.open("w", encoding="utf-8") as curve_file:
        with patched_grokking_regime():
            for control in CONTROLS:
                train_eps = datasets[control]["train"]
                heldout_eps = datasets[control]["heldout"]
                train_t = ML.move_tensors(ML.build_tensors(train_eps))
                heldout_t = ML.move_tensors(ML.build_tensors(heldout_eps))
                # Smoke the imported eval path before training this control.
                model = ML.build_model(FAMILY, PARAMS, SEEDS[0])
                _eval_checkpoint(model, train_t, heldout_t)
                del model
                torch.cuda.empty_cache()
                for seed in SEEDS:
                    writer = CurveWriter(
                        curve_file,
                        task_id=TASK_ID,
                        control=control,
                        ideal_balacc=float(datasets[control]["ideal_balacc"]),
                        code_path_hash=code_path_hash,
                    )
                    record = _banked_train_one_grokking_run(
                        run_id=run_id,
                        seed=int(seed),
                        weight_decay=WEIGHT_DECAY,
                        train_eps=train_eps,
                        heldout_eps=heldout_eps,
                        train_t=train_t,
                        heldout_t=heldout_t,
                        curve_handle=writer,
                    )
                    record.update(
                        {
                            "task_id": TASK_ID,
                            "control": control,
                            "ideal_balacc": float(datasets[control]["ideal_balacc"]),
                            "ideal_scores_min": datasets[control]["ideal_scores_min"],
                            "dataset_diagnostics": datasets[control]["diagnostics"],
                            "code_path_hash": code_path_hash,
                            "banked_training_step": (
                                "src.tlgp_capability_witness_preflight_001a.grokking_probe"
                                ".train_one_grokking_run"
                            ),
                            "status": "completed",
                        }
                    )
                    records.append(record)
                    write_json(OUT_DIR / "training_records.json", records)
    report = apply_go_no_go(records)
    report.update(
        {
            "task_id": TASK_ID,
            "run_id": run_id,
            "producer_function": (
                "src.tlgp_capability_witness_preflight_001a.positive_control"
                ".apply_go_no_go"
            ),
            "input_artifacts": [
                _relative(FROZEN_DESIGN_PATH),
                "src/tlgp_capability_witness_preflight_001a/grokking_probe.py",
                "src/tlgp_001b_r2/world.py",
                "src/tlgp_001b_r2/meta_learners.py",
                "artifacts/TLGP-001B-R2/prereg.json",
            ],
            "dataset_diagnostics": {control: datasets[control]["diagnostics"] for control in CONTROLS},
            "ideal_balacc_by_control": {
                control: float(datasets[control]["ideal_balacc"]) for control in CONTROLS
            },
        }
    )
    write_json(OUT_DIR / "positive_control_report.json", report)
    manifest = make_manifest(gate, run_id, report)
    write_json(OUT_DIR / "manifest.json", manifest)
    if not manifest["banked_source_diff_empty"]:
        raise StopPositiveControl(
            "banked_source_guard_after_run",
            "protected banked source status changed",
            {
                "status": manifest["banked_source_status_after_run"],
                "diff": manifest["banked_source_diff_after_run"],
            },
            {"status": [], "diff": []},
        )
    return {"manifest": manifest, "report": report, "records": records}


def write_failure_manifest(exc: BaseException) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if isinstance(exc, StopPositiveControl):
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
            "claim_ceiling": "no positive-control verdict; runner validation stopped",
        }
    )
    write_json(OUT_DIR / "failure_manifest.json", payload)


def self_test() -> dict[str, Any]:
    gate = validate_pre_run_gates()
    datasets = build_control_datasets()
    copy_diag = datasets[PC_COPY]["diagnostics"]
    single_diag = datasets[PC_SINGLE_RULE]["diagnostics"]
    if copy_diag["copy_overlap_train_mean"] != 1.0 or copy_diag["copy_overlap_heldout_mean"] != 1.0:
        raise StopPositiveControl("pc_copy_construction", "PC_COPY queries are not all in adapt context", copy_diag, 1.0)
    for key, row in single_diag["single_rule_full_coverage_sample"].items():
        if not row["all_full_coverage"]:
            raise StopPositiveControl("pc_single_rule_coverage", f"{key} lacks full value coverage", row, True)
    return {
        "gate": gate,
        "ideal_balacc_by_control": {control: datasets[control]["ideal_balacc"] for control in CONTROLS},
        "diagnostics": {control: datasets[control]["diagnostics"] for control in CONTROLS},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="run the frozen positive controls")
    parser.add_argument("--validate-only", action="store_true", help="validate source pins and GPU only")
    parser.add_argument("--self-test", action="store_true", help="validate control construction without training")
    args = parser.parse_args(argv)
    try:
        if args.validate_only:
            write_json(OUT_DIR / "validate_only_manifest.json", validate_pre_run_gates())
            return 0
        if args.self_test:
            result = self_test()
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        if not args.run:
            parser.error("use --run, --validate-only, or --self-test")
        run_positive_controls()
        return 0
    except BaseException as exc:
        write_failure_manifest(exc)
        print(f"positive control stopped: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
