"""Rung1-only capacity sweep runner for TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-001A.

This is a scout/diagnostic runner, not a rung3 transfer run.  Full scout
execution is guarded by the frozen design SHA; dry-run mode exercises the same
real training/eval/replay paths at tiny non-evidential scale and deliberately
does not assert the banked C0 consistency threshold.
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
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Iterable, TextIO

import numpy as np
import torch
import torch.nn as nn

from src.tlgp_001a.leakage import detect, planted_channels, targets
from src.tlgp_001a.metrics import balanced_accuracy, mean_episode_score
from src.tlgp_001a.world import Episode
from src.tlgp_001b_r2 import lower_reference as LR
from src.tlgp_001b_r2 import meta_learners as ML
from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_001b_r2 import splits as S
from src.tlgp_001b_r2 import world as W
from src.tlgp_001b_r2.world import ideal_predictions
from src.tlgp_capability_witness_preflight_001a import rung3_graph_cache_baselines as GB
from src.tlgp_capability_witness_preflight_001a.retrieval_model import (
    FAMILY,
    build_model,
    parameter_count,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-001A"
BASE_ARTIFACT_DIR = (
    REPO_ROOT
    / "artifacts"
    / "TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A"
    / "RUNG1_CAPACITY_SWEEP_001A"
)
DESIGN_PATH = BASE_ARTIFACT_DIR / "FREEZE" / "design.json"
RUN_DIR = BASE_ARTIFACT_DIR / "RUN"
DRY_RUN_DIR = RUN_DIR / "DRY_RUN"
FULL_SCOUT_DIR = RUN_DIR / "FULL_SCOUT"
RUNNER_PATH = REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "rung1_capacity_sweep.py"

EXPECTED_DESIGN_SHA256 = "79e51bb4c2f4af89e330ea81e5f9a636a75be3bdb862754e8851164b6f48c21f"
EXPECTED_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"
RUNG1_SWEEP_SUBSET_SEED = 20260730

SOURCE_PINS = {
    "src/tlgp_capability_witness_preflight_001a/retrieval_model.py": (
        "0cba923965f305c6c8cab41a8dd033d7a34bf1c3cd60b0ea27a7fdcc698bf2bb"
    ),
    "src/tlgp_001b_r2/meta_learners.py": "358d2bb2449f88ff5c73de52fcabcbba17f40b22dabc5c484f7b67da627e1b6f",
    "src/tlgp_001b_r2/world.py": "1c9bd730e79c19e5036e26cf4a45f1463dc2194217ec5ebc06e42731ca364a7c",
    "src/tlgp_001b_r2/splits.py": "ca2852a1ca69ba5277872bf5b0780163d0c79fbf0b5b2c7075bb740ef9981ad5",
    "src/tlgp_001b_r2/preregistration.py": "6a5a0273e7c3b0c2cce031dcf2b495646d87ecea7630d725c84def8f9ce27480",
    "src/tlgp_001b_r2/lower_reference.py": "cd701b2f4adcf9d8c66f28f0e797cdf748a7f4560c682953829b99eb85d28cf6",
    "src/tlgp_001a/leakage.py": "387c413d6af816216c73b45316bf854e3ef906e575bffc96cea1f6353e90bef1",
    "src/tlgp_capability_witness_preflight_001a/rung3_graph_cache_baselines.py": (
        "921d44078a7b77e60c61b9bc5c5e2986228c4134a30ef2703c5fc52890229eaa"
    ),
    "src/tlgp_capability_witness_preflight_001a/rung3_single_family_adjudicator.py": (
        "5773f5d14cde442002c4c69e4d8d37302df40a863b01f97f86336a53a3fa9120"
    ),
    "src/tlgp_capability_witness_preflight_001a/rung3_powered_full_run.py": (
        "a0dcea8d51a49d8af4118ea62810952ee8b68528108f4e75f212001e73103be5"
    ),
    "src/tlgp_capability_witness_preflight_001a/route_decision.py": (
        "0dcf3659df802912ff2f760e9875526887e14c4c14d1e0cc91c0cb4d8863c0c8"
    ),
}

PROTECTED_DIFF_PATHS = [
    "AGENTS.md",
    "CLAUDE.md",
    "artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG3_POWERED_LEARNER_001A/PHASE_B_FREEZE_REVIEW/design.json",
    "src/tlgp_001a",
    "src/tlgp_001b_r2",
    "src/tlgp_capability_witness_preflight_001a/retrieval_model.py",
    "src/tlgp_capability_witness_preflight_001a/rung3_graph_cache_baselines.py",
    "src/tlgp_capability_witness_preflight_001a/rung3_single_family_adjudicator.py",
    "src/tlgp_capability_witness_preflight_001a/rung3_powered_full_run.py",
    "src/tlgp_capability_witness_preflight_001a/route_decision.py",
]

REQUIRED_FILES = [
    "result.json",
    "trace.jsonl",
    "val_curves.jsonl",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_report.json",
    "replay_report.json",
    "manifest.json",
]


class StopRung1Sweep(RuntimeError):
    def __init__(self, step: str, reason: str, observed: Any = None, expected: Any = None):
        super().__init__(reason)
        self.step = step
        self.reason = reason
        self.observed = observed
        self.expected = expected


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(v) for v in value]
    if isinstance(value, np.ndarray):
        return [_json_ready(v) for v in value.tolist()]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, Path):
        return path_label(value)
    return value


def path_label(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix() if path.is_absolute() else path.as_posix()
    except ValueError:
        return path.as_posix()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(obj), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl_row(handle: TextIO, row: dict[str, Any]) -> None:
    handle.write(json.dumps(_json_ready(row), sort_keys=True, separators=(",", ":")) + "\n")
    handle.flush()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _strip_underscore_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_underscore_keys(v) for k, v in obj.items() if not str(k).startswith("_")}
    if isinstance(obj, list):
        return [_strip_underscore_keys(v) for v in obj]
    return obj


def load_design() -> dict[str, Any]:
    return json.loads(DESIGN_PATH.read_text(encoding="utf-8"))


FROZEN_DESIGN = load_design()


@dataclass(frozen=True)
class RunConfig:
    dry_run: bool
    model_seeds: list[int]
    phase1_capacity_tags: list[str]
    phase2_rule_counts: list[int]
    n_train: int
    n_val: int
    n_test: int
    batch_size: int
    max_epochs: int
    early_stop_patience: int
    steps_max: int
    lr_grid: list[float]
    delta: float
    epsilon: float
    clear_count_min: int
    consistency_expected_meta: dict[str, float]
    consistency_tolerance: float
    per_cell_wall_clock_cap_hours: float | None


@dataclass
class TrainedModel:
    model: nn.Module
    selected_lr: float
    selected_best_val_balacc: float
    selected_best_epoch: int
    selected_epochs_run: int
    selected_steps_run: int
    selected_val_still_improving_at_stop: bool
    lr_results: list[dict[str, Any]]
    test_balacc: float
    test_preds: list[list[int]]
    device: dict[str, Any]


def verify_frozen_design(path: Path = DESIGN_PATH) -> dict[str, Any]:
    design = json.loads(path.read_text(encoding="utf-8"))
    computed = canonical_sha256(_strip_underscore_keys(design))
    recorded = str(design.get("_frozen_canonical_sha256", ""))
    if computed != recorded or computed != EXPECTED_DESIGN_SHA256:
        raise StopRung1Sweep(
            "design_sha",
            "Rung1 capacity sweep frozen design canonical SHA mismatch",
            {"computed": computed, "recorded": recorded},
            EXPECTED_DESIGN_SHA256,
        )
    for tag, params in design["capacity_grid"]["phase1"].items():
        if int(params["d_model"]) % int(params["heads"]) != 0:
            raise StopRung1Sweep("capacity_grid", "heads must divide d_model", {tag: params}, "heads|d_model")
    if "C3" in design["capacity_grid"]["phase1"]:
        raise StopRung1Sweep("capacity_grid", "C3 is not included in this freeze", sorted(design["capacity_grid"]["phase1"]), "C0,C1,C2")
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.verify_frozen_design",
        "path": path_label(path),
        "computed_sha256": computed,
        "recorded_sha256": recorded,
        "expected_sha256": EXPECTED_DESIGN_SHA256,
        "match": True,
        "heads_divide_d_model": True,
    }


def git_output(args: list[str], check: bool = True) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        raise StopRung1Sweep("git_readback", proc.stderr.strip(), args, "git command succeeds")
    return proc.stdout


def protected_diff_names() -> list[str]:
    return git_output(["diff", "--name-only", "--", *PROTECTED_DIFF_PATHS]).splitlines()


def source_pin_report() -> dict[str, Any]:
    observed = {path: sha256_file(REPO_ROOT / path) for path in SOURCE_PINS}
    mismatches = {
        path: {"observed": observed[path], "expected": expected}
        for path, expected in SOURCE_PINS.items()
        if observed[path] != expected
    }
    if mismatches:
        raise StopRung1Sweep("source_pins", "read-only source pin mismatch", mismatches, "all source pins match")
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.source_pin_report",
        "pins": dict(SOURCE_PINS),
        "observed": observed,
        "all_match": True,
        "runner_path": path_label(RUNNER_PATH),
        "runner_sha256": sha256_file(RUNNER_PATH),
        "retrieval_model_sha256": observed["src/tlgp_capability_witness_preflight_001a/retrieval_model.py"],
        "rung3_powered_full_run_sha256": observed["src/tlgp_capability_witness_preflight_001a/rung3_powered_full_run.py"],
    }


def gpu_env_report() -> dict[str, Any]:
    return {
        "torch_version": torch.__version__,
        "selected_device": str(ML.DEVICE),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }


def build_run_config(dry_run: bool, dry_overrides: dict[str, Any] | None = None) -> RunConfig:
    design = FROZEN_DESIGN
    budget = P.training_budget()
    cfg = RunConfig(
        dry_run=bool(dry_run),
        model_seeds=[int(v) for v in design["seeds"]["model_seeds"]],
        phase1_capacity_tags=[str(v) for v in design["phase1"]["capacity_tags"]],
        phase2_rule_counts=[int(v) for v in design["phase2"]["rule_counts"]],
        n_train=int(design["budget"]["n_train"]),
        n_val=int(design["budget"]["n_val"]),
        n_test=int(design["budget"]["n_test"]),
        batch_size=int(design["budget"]["batch_size"]),
        max_epochs=int(design["budget"]["max_epochs"]),
        early_stop_patience=int(design["budget"]["early_stop_patience"]),
        steps_max=int(design["budget"]["steps_max"]),
        lr_grid=[float(v) for v in design["budget"]["lr_grid"]],
        delta=float(design["clear_threshold"]["delta"]),
        epsilon=float(design["clear_threshold"]["epsilon"]),
        clear_count_min=int(design["clear_threshold"]["required_clear_count"]),
        consistency_expected_meta={str(k): float(v) for k, v in design["consistency_control"]["banked_meta_by_seed"].items()},
        consistency_tolerance=float(design["consistency_control"]["reproduce_abs_tolerance"]),
        per_cell_wall_clock_cap_hours=design["wall_clock"]["per_cell_wall_clock_cap_hours"],
    )
    if not dry_run:
        if cfg.model_seeds != P.model_seeds()[:3]:
            raise StopRung1Sweep("model_seeds", "full scout model seeds changed", cfg.model_seeds, P.model_seeds()[:3])
        if cfg.lr_grid != [0.001, 0.0003] or cfg.lr_grid != budget["lr_grid"]:
            raise StopRung1Sweep("lr_grid", "full scout LR grid changed", cfg.lr_grid, budget["lr_grid"])
        if (
            cfg.n_train != 5000
            or cfg.n_val != 1000
            or cfg.n_test != 200
            or cfg.max_epochs != 200
            or cfg.steps_max != int(budget["steps_max"])
        ):
            raise StopRung1Sweep("budget", "full scout budget changed", asdict(cfg), "frozen design/prereg budget")
        return cfg
    cfg = replace(
        cfg,
        model_seeds=[P.model_seeds()[0]],
        phase1_capacity_tags=["C0"],
        phase2_rule_counts=[8],
        n_train=8,
        n_val=4,
        n_test=4,
        batch_size=2,
        max_epochs=2,
        steps_max=4,
        lr_grid=[0.001],
    )
    if dry_overrides:
        allowed = set(asdict(cfg))
        unknown = sorted(set(dry_overrides) - allowed)
        if unknown:
            raise StopRung1Sweep("dry_overrides", "unknown dry-run override keys", unknown, sorted(allowed))
        cfg = replace(cfg, **dry_overrides)
    return cfg


def validate_governance(config: RunConfig) -> dict[str, Any]:
    design = verify_frozen_design()
    prereg_sha = P.canonical_sha256(json.loads(P.PREREG_JSON_PATH.read_text(encoding="utf-8")))
    if prereg_sha != EXPECTED_PREREG_SHA256:
        raise StopRung1Sweep("prereg_sha", "prereg canonical SHA mismatch", prereg_sha, EXPECTED_PREREG_SHA256)
    protected = protected_diff_names()
    if protected:
        raise StopRung1Sweep("protected_diffs", "protected tracked files have diffs", protected, [])
    source_pins = source_pin_report()
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.validate_governance",
        "task_id": TASK_ID,
        "design": design,
        "prereg_canonical_sha256": prereg_sha,
        "prereg_sha_match": True,
        "source_pins": source_pins,
        "capacity_grid": FROZEN_DESIGN["capacity_grid"],
        "heads_divide_d_model": design["heads_divide_d_model"],
        "config": asdict(config),
        "protected_tracked_diff_names": protected,
        "git": {
            "repo_root": REPO_ROOT.as_posix(),
            "branch": git_output(["branch", "--show-current"]).strip(),
            "head": git_output(["rev-parse", "HEAD"]).strip(),
            "status_short_branch": git_output(["status", "--short", "--branch"]).splitlines(),
        },
        "gpu_env": gpu_env_report(),
        "claim_ceiling": FROZEN_DESIGN["claim_ceiling"],
    }


def capacity_params(tag: str) -> dict[str, int]:
    params = FROZEN_DESIGN["capacity_grid"]["phase1"][str(tag)]
    return {key: int(params[key]) for key in ("d_model", "layers", "heads", "ff_mult")}


def select_train_rules(rule_count: int) -> list[int]:
    train_idx, test_idx = S.rule_split()
    if int(rule_count) == len(train_idx):
        selected = [int(v) for v in train_idx.tolist()]
    else:
        rng = np.random.default_rng(RUNG1_SWEEP_SUBSET_SEED)
        selected = [int(v) for v in rng.choice(train_idx, size=int(rule_count), replace=False).tolist()]
        selected = sorted(selected)
    if set(selected) & {int(v) for v in test_idx.tolist()}:
        raise StopRung1Sweep("rule_subset", "phase2 rule subset overlaps test rules", selected, "disjoint")
    return selected


def make_subset_episodes(
    *,
    rule_ids: list[int],
    split: str,
    n_episodes: int,
    base_id: int,
    seed: int,
) -> list[Episode]:
    rng = np.random.default_rng(int(seed))
    episodes: list[Episode] = []
    for idx in range(int(n_episodes)):
        rule_id = int(rule_ids[int(rng.integers(0, len(rule_ids)))])
        episodes.append(
            W.make_episode_for_rule(
                int(base_id) + idx,
                rule_id,
                rng,
                P.TRAIN_VALUES,
                P.TRAIN_VALUES,
            )
        )
    return episodes


def make_cell_datasets(rule_count: int, config: RunConfig) -> dict[str, list[Episode]]:
    if int(rule_count) == 172:
        return {
            "train": S.make_episodes("rung1", "train", config.n_train),
            "val": S.make_episodes("rung1", "val", config.n_val),
            "test": S.make_episodes("rung1", "test", config.n_test),
            "rule_ids": select_train_rules(172),
            "source": "exact_rung1_172_rule_task",
        }
    rule_ids = select_train_rules(int(rule_count))
    base = 60_000_000 + int(rule_count) * 100_000
    return {
        "train": make_subset_episodes(
            rule_ids=rule_ids,
            split="train",
            n_episodes=config.n_train,
            base_id=base,
            seed=int(P.seeds()["RUNG1_TRAIN_EPISODES_SEED"]) + int(rule_count),
        ),
        "val": make_subset_episodes(
            rule_ids=rule_ids,
            split="val",
            n_episodes=config.n_val,
            base_id=base + 20_000,
            seed=int(P.seeds()["RUNG1_VAL_EPISODES_SEED"]) + int(rule_count),
        ),
        "test": make_subset_episodes(
            rule_ids=rule_ids,
            split="test",
            n_episodes=config.n_test,
            base_id=base + 40_000,
            seed=int(P.seeds()["RUNG1_TEST_EPISODES_SEED"]) + int(rule_count),
        ),
        "rule_ids": rule_ids,
        "source": "deterministic_train_pool_rule_subset",
    }


def _canonical_episode_payload(ep: Episode) -> dict[str, Any]:
    return {
        "episode_id": int(ep.episode_id),
        "rule_id": int(ep.rule_id),
        "adapt_x": ep.adapt_x.tolist(),
        "adapt_a": ep.adapt_a.tolist(),
        "adapt_e": ep.adapt_e.tolist(),
        "query_x": ep.query_x.tolist(),
        "query_a": ep.query_a.tolist(),
    }


def episode_input_hash(ep: Episode) -> str:
    return canonical_sha256(_canonical_episode_payload(ep))


def evaluate_fair_panel(episodes: list[Episode], seed: int) -> tuple[dict[str, float], list[dict[str, list[int]]], dict[str, Any]]:
    lower, lower_records = LR.evaluate(episodes, int(seed))
    graph, graph_records = GB.evaluate(episodes, int(seed))
    fair = {**{name: float(value) for name, value in lower.items()}, **{name: float(value) for name, value in graph.items()}}
    records: list[dict[str, list[int]]] = []
    for idx in range(len(episodes)):
        row = dict(lower_records[idx])
        row.update(graph_records[idx])
        records.append(row)
    return fair, records, {
        "producer_functions": [
            "src.tlgp_001b_r2.lower_reference.evaluate",
            "src.tlgp_capability_witness_preflight_001a.rung3_graph_cache_baselines.evaluate",
        ],
        "fair_baseline_balacc": fair,
        "fair_max": float(max(fair.values())),
        "graph_cache_alias_report": GB.alias_report(episodes),
    }


def _eval_tensors(
    model: nn.Module,
    tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    batch_size: int,
) -> tuple[float, list[list[int]]]:
    return ML._eval_tensors(model, tensors, int(batch_size))


def _train_one_lr(
    *,
    seed: int,
    lr: float,
    cap_tag: str,
    cap_params: dict[str, int],
    train_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    val_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    config: RunConfig,
    run_id: str,
    stage: str,
    rule_count: int,
    curve_handle: TextIO,
) -> dict[str, Any]:
    torch.manual_seed(int(seed))
    model = build_model(cap_params).to(ML.DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(lr))
    lossf = nn.CrossEntropyLoss()
    ctx_tr, qx_tr, qy_tr = train_tensors
    batch = int(config.batch_size)
    n = int(ctx_tr.shape[0])
    generator = torch.Generator(device="cpu").manual_seed(int(seed) + int(round(float(lr) * 1_000_000)))
    best_val = float("-inf")
    best_state: dict[str, torch.Tensor] | None = None
    best_epoch = 0
    since = 0
    steps = 0
    epochs_run = 0
    last_loss = None
    for epoch in range(int(config.max_epochs)):
        epochs_run = epoch + 1
        model.train()
        perm = torch.randperm(n, generator=generator)
        for start in range(0, n, batch):
            idx = perm[start:start + batch].to(ctx_tr.device)
            logits = model(ctx_tr[idx], qx_tr[idx])
            loss = lossf(logits.reshape(-1, P.K), qy_tr[idx].reshape(-1))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            last_loss = float(loss.detach().cpu().item())
            steps += 1
            if steps >= int(config.steps_max):
                break
        val_score, _ = _eval_tensors(model, val_tensors, batch)
        row = {
            "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep._train_one_lr",
            "run_id": run_id,
            "task_id": TASK_ID,
            "stage": stage,
            "capacity_tag": cap_tag,
            "capacity": cap_params,
            "rule_count": int(rule_count),
            "seed": int(seed),
            "family": FAMILY,
            "lr": float(lr),
            "epoch": int(epochs_run),
            "steps": int(steps),
            "val_balacc": float(val_score),
            "train_loss_last": last_loss,
            "aggregation_rule": "validation balanced accuracy per epoch; best checkpoint selected by max val_balacc",
            "code_path_hash": sha256_file(RUNNER_PATH),
        }
        write_jsonl_row(curve_handle, row)
        if float(val_score) > best_val + 1e-12:
            best_val = float(val_score)
            best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
            best_epoch = int(epochs_run)
            since = 0
        else:
            since += 1
        if since >= int(config.early_stop_patience) or steps >= int(config.steps_max):
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    return {
        "model": model,
        "lr": float(lr),
        "best_val_balacc": float(best_val),
        "best_epoch": int(best_epoch),
        "epochs_run": int(epochs_run),
        "steps_run": int(steps),
        "val_still_improving_at_stop": bool(best_epoch == epochs_run),
    }


def train_retrieval_model(
    *,
    seed: int,
    cap_tag: str,
    cap_params: dict[str, int],
    rule_count: int,
    stage: str,
    train_eps: list[Episode],
    val_eps: list[Episode],
    test_eps: list[Episode],
    config: RunConfig,
    run_id: str,
    curve_handle: TextIO,
) -> TrainedModel:
    train_tensors = ML.move_tensors(ML.build_tensors(train_eps))
    val_tensors = ML.move_tensors(ML.build_tensors(val_eps))
    test_tensors = ML.move_tensors(ML.build_tensors(test_eps))
    best: dict[str, Any] | None = None
    lr_results: list[dict[str, Any]] = []
    for lr in config.lr_grid:
        result = _train_one_lr(
            seed=int(seed),
            lr=float(lr),
            cap_tag=cap_tag,
            cap_params=cap_params,
            train_tensors=train_tensors,
            val_tensors=val_tensors,
            config=config,
            run_id=run_id,
            stage=stage,
            rule_count=rule_count,
            curve_handle=curve_handle,
        )
        lr_results.append(
            {
                "lr": result["lr"],
                "best_val_balacc": result["best_val_balacc"],
                "best_epoch": result["best_epoch"],
                "epochs_run": result["epochs_run"],
                "steps_run": result["steps_run"],
                "val_still_improving_at_stop": result["val_still_improving_at_stop"],
            }
        )
        if best is None or float(result["best_val_balacc"]) > float(best["best_val_balacc"]):
            if best is not None:
                del best["model"]
            best = result
        else:
            del result["model"]
    assert best is not None
    model = best["model"]
    test_balacc, test_preds = _eval_tensors(model, test_tensors, int(config.batch_size))
    device = ML._record_device_run(FAMILY, model, [train_tensors, val_tensors, test_tensors], test_preds)
    return TrainedModel(
        model=model,
        selected_lr=float(best["lr"]),
        selected_best_val_balacc=float(best["best_val_balacc"]),
        selected_best_epoch=int(best["best_epoch"]),
        selected_epochs_run=int(best["epochs_run"]),
        selected_steps_run=int(best["steps_run"]),
        selected_val_still_improving_at_stop=bool(best["val_still_improving_at_stop"]),
        lr_results=lr_results,
        test_balacc=float(test_balacc),
        test_preds=test_preds,
        device=device,
    )


def make_shuffled_adapt_episodes(episodes: list[Episode], seed: int) -> list[Episode]:
    rng = np.random.default_rng(int(seed))
    perm = rng.permutation(len(episodes))
    if len(episodes) > 1 and any(int(i) == int(j) for i, j in enumerate(perm)):
        perm = np.roll(perm, 1)
    out: list[Episode] = []
    for idx, donor_idx in enumerate(perm):
        ep = episodes[int(idx)]
        donor = episodes[int(donor_idx)]
        out.append(
            replace_episode(
                ep,
                adapt_x=donor.adapt_x.copy(),
                adapt_a=donor.adapt_a.copy(),
                adapt_e=donor.adapt_e.copy(),
            )
        )
    return out


def replace_episode(ep: Episode, **kwargs: Any) -> Episode:
    from dataclasses import replace

    return replace(ep, **kwargs)


def _per_episode_score_rows(
    *,
    run_id: str,
    seed: int,
    stage: str,
    capacity_tag: str,
    capacity: dict[str, int],
    rule_count: int,
    mode: str,
    split: str,
    episodes: list[Episode],
    meta_preds: list[list[int]],
    ideal_preds: list[list[int]],
    fair_preds: list[dict[str, list[int]]] | None,
    trace_handle: TextIO,
) -> tuple[float, list[dict[str, Any]]]:
    scores: list[float] = []
    rows: list[dict[str, Any]] = []
    cell_id = f"{stage}:{capacity_tag}:k{int(rule_count)}:seed{int(seed)}"
    for ep, meta_pred, ideal_pred in zip(episodes, meta_preds, ideal_preds):
        meta_score = balanced_accuracy(ep.query_e, np.array(meta_pred, dtype=int), n_classes=P.K)
        ideal_score = balanced_accuracy(ep.query_e, np.array(ideal_pred, dtype=int), n_classes=P.K)
        fair_scores: dict[str, float] = {}
        fair_row: dict[str, list[int]] = {}
        if fair_preds is not None:
            fair_row = fair_preds[len(rows)]
            for name, pred in fair_row.items():
                fair_scores[name] = balanced_accuracy(ep.query_e, np.array(pred, dtype=int), n_classes=P.K)
        row = {
            "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep._per_episode_score_rows",
            "run_id": run_id,
            "task_id": TASK_ID,
            "cell_id": cell_id,
            "seed": int(seed),
            "stage": stage,
            "rung": "rung1",
            "split": split,
            "mode": mode,
            "capacity_tag": capacity_tag,
            "capacity": capacity,
            "rule_count": int(rule_count),
            "episode_id": int(ep.episode_id),
            "rule_id": int(ep.rule_id),
            "adapt_tensor_hash": episode_input_hash(ep),
            "query_truth": [int(v) for v in ep.query_e],
            "meta_prediction": [int(v) for v in meta_pred],
            "ideal_prediction": [int(v) for v in ideal_pred],
            "fair_prediction": fair_row,
            "meta_balacc": float(meta_score),
            "ideal_balacc": float(ideal_score),
            "fair_balacc": fair_scores,
            "fair_max": float(max(fair_scores.values())) if fair_scores else None,
            "headroom_vs_meta": float(ideal_score - meta_score),
            "aggregation_rule": "mean balanced accuracy over episode rows grouped by cell_id and mode",
            "code_path_hash": sha256_file(RUNNER_PATH),
        }
        scores.append(float(meta_score))
        rows.append(row)
        write_jsonl_row(trace_handle, row)
    return mean_episode_score(scores), rows


def evaluate_model_on_cell(
    *,
    run_id: str,
    seed: int,
    stage: str,
    capacity_tag: str,
    capacity: dict[str, int],
    rule_count: int,
    model: nn.Module,
    episodes: list[Episode],
    config: RunConfig,
    trace_handle: TextIO,
    precomputed_meta_preds: list[list[int]] | None = None,
) -> dict[str, Any]:
    ideal_mean, ideal_preds, ideal_scores = ideal_predictions(episodes)
    fair, fair_preds, fair_detail = evaluate_fair_panel(episodes, int(seed))
    if precomputed_meta_preds is None:
        meta_mean, meta_preds = ML.eval_model(model, episodes, int(config.batch_size))
    else:
        meta_preds = precomputed_meta_preds
        meta_scores = [
            balanced_accuracy(ep.query_e, np.array(pred, dtype=int), n_classes=P.K)
            for ep, pred in zip(episodes, meta_preds)
        ]
        meta_mean = mean_episode_score(meta_scores)
    trace_meta_mean, trace_rows = _per_episode_score_rows(
        run_id=run_id,
        seed=seed,
        stage=stage,
        capacity_tag=capacity_tag,
        capacity=capacity,
        rule_count=rule_count,
        mode="normal",
        split="test",
        episodes=episodes,
        meta_preds=meta_preds,
        ideal_preds=ideal_preds,
        fair_preds=fair_preds,
        trace_handle=trace_handle,
    )
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.evaluate_model_on_cell",
        "run_id": run_id,
        "seed": int(seed),
        "stage": stage,
        "capacity_tag": capacity_tag,
        "capacity": capacity,
        "rule_count": int(rule_count),
        "split": "test",
        "episodes": len(episodes),
        "episode_ids": [int(ep.episode_id) for ep in episodes],
        "rule_ids": [int(ep.rule_id) for ep in episodes],
        "unique_rule_count": len({int(ep.rule_id) for ep in episodes}),
        "ideal_mean": float(ideal_mean),
        "ideal_scores": [float(v) for v in ideal_scores],
        "meta_mean": float(meta_mean),
        "trace_meta_mean": float(trace_meta_mean),
        "fair_baseline_balacc": fair,
        "fair_max": float(max(fair.values())),
        "headroom_vs_meta": float(ideal_mean - meta_mean),
        "meta_minus_fair_max": float(meta_mean - max(fair.values())),
        "fair_detail": fair_detail,
        "trace_row_count": len(trace_rows),
        "claim_ceiling": "per-cell rung1 seen-rule metric only",
    }


def context_ablation_report(
    *,
    run_id: str,
    seed: int,
    stage: str,
    capacity_tag: str,
    capacity: dict[str, int],
    rule_count: int,
    model: nn.Module,
    eval_eps: list[Episode],
    normal_meta_mean: float,
    fair_max: float,
    config: RunConfig,
    trace_handle: TextIO,
) -> dict[str, Any]:
    ideal_mean, ideal_preds, _ = ideal_predictions(eval_eps)
    fair, fair_preds, _ = evaluate_fair_panel(eval_eps, int(seed))
    threshold = float(fair_max + config.epsilon)
    modes: dict[str, dict[str, Any]] = {}
    mode_episodes = {
        "shuffle_adapt": make_shuffled_adapt_episodes(eval_eps, int(seed) + 991),
        "no_adapt": eval_eps,
    }
    for mode, episodes in mode_episodes.items():
        if mode == "no_adapt":
            tensors = ML.move_tensors(ML.build_tensors(episodes, context_ablate=True))
            score, preds = _eval_tensors(model, tensors, int(config.batch_size))
        else:
            score, preds = ML.eval_model(model, episodes, int(config.batch_size))
        _per_episode_score_rows(
            run_id=run_id,
            seed=seed,
            stage=stage,
            capacity_tag=capacity_tag,
            capacity=capacity,
            rule_count=rule_count,
            mode=mode,
            split="test",
            episodes=episodes,
            meta_preds=preds,
            ideal_preds=ideal_preds,
            fair_preds=fair_preds,
            trace_handle=trace_handle,
        )
        modes[mode] = {
            "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.context_ablation_report",
            "ablated_balacc": float(score),
            "normal_balacc": float(normal_meta_mean),
            "fair_max": float(fair_max),
            "EPSILON": float(config.epsilon),
            "advantage_destroyed_threshold": threshold,
            "advantage_destroyed_collapse": bool(float(score) <= threshold),
            "drop_from_normal": float(normal_meta_mean - score),
        }
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.context_ablation_report",
        "run_id": run_id,
        "seed": int(seed),
        "stage": stage,
        "capacity_tag": capacity_tag,
        "capacity": capacity,
        "rule_count": int(rule_count),
        "ablation_eval_split": "test",
        "episodes": len(eval_eps),
        "ideal_mean": float(ideal_mean),
        "normal_meta_balacc": float(normal_meta_mean),
        "fair_baseline_balacc": fair,
        "fair_max": float(fair_max),
        "EPSILON": float(config.epsilon),
        "modes": modes,
        "both_modes_advantage_destroyed": bool(
            modes["shuffle_adapt"]["advantage_destroyed_collapse"]
            and modes["no_adapt"]["advantage_destroyed_collapse"]
        ),
        "FIX_1_test_eval_scope_pass": True,
        "FIX_2_advantage_destroyed_criterion": True,
    }


def _meta_input_channels(episodes: list[Episode]) -> dict[str, np.ndarray]:
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


def run_leakage_report(stage: str, capacity_tag: str, rule_count: int, episodes: list[Episode]) -> dict[str, Any]:
    tgt = targets(episodes)
    clean = detect(_meta_input_channels(episodes), tgt)
    planted = detect(planted_channels(episodes, tgt), tgt)
    clean_false = [name for name, row in clean.items() if row["flagged"]]
    planted_missed = [name for name, row in planted.items() if not row["flagged"]]
    return {
        "producer_function": "src.tlgp_001a.leakage.detect",
        "stage": stage,
        "capacity_tag": capacity_tag,
        "rule_count": int(rule_count),
        "episodes": len(episodes),
        "episode_ids": [int(ep.episode_id) for ep in episodes],
        "meta_input_channels_declared": ["adapt_x", "adapt_a", "adapt_e", "query_x", "query_a"],
        "meta_forbidden_inputs": ["rule_id", "query_e"],
        "clean_false_flags": clean_false,
        "planted_missed": planted_missed,
        "all_planted_caught": not planted_missed,
        "no_clean_false_flag": not clean_false,
        "renamed_leak_caught": bool(planted["telemetry_7"]["flagged"]),
        "answer_leak_caught": bool(planted["calib_value"]["flagged"]),
        "detector_valid": not planted_missed and not clean_false,
        "clean_report": clean,
        "planted_report": planted,
    }


def _training_report(stage: str, seed: int, cap_tag: str, cap_params: dict[str, int], trained: TrainedModel) -> dict[str, Any]:
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.train_retrieval_model",
        "stage": stage,
        "seed": int(seed),
        "family": FAMILY,
        "capacity_tag": cap_tag,
        "params": cap_params,
        "parameter_count": parameter_count(build_model(cap_params)),
        "selected_lr": trained.selected_lr,
        "selected_best_val_balacc": trained.selected_best_val_balacc,
        "selected_best_epoch": trained.selected_best_epoch,
        "selected_epochs_run": trained.selected_epochs_run,
        "selected_steps_run": trained.selected_steps_run,
        "selected_val_still_improving_at_stop": trained.selected_val_still_improving_at_stop,
        "lr_policy": "prereg lr_grid with validation-balanced-accuracy selection",
        "lr_results": trained.lr_results,
        "device": trained.device,
    }


def run_cell(
    *,
    run_id: str,
    stage: str,
    capacity_tag: str,
    rule_count: int,
    config: RunConfig,
    trace_handle: TextIO,
    curve_handle: TextIO,
) -> dict[str, Any]:
    cap_params = capacity_params(capacity_tag)
    datasets = make_cell_datasets(int(rule_count), config)
    per_seed: list[dict[str, Any]] = []
    for seed in config.model_seeds:
        trained = train_retrieval_model(
            seed=int(seed),
            cap_tag=capacity_tag,
            cap_params=cap_params,
            rule_count=int(rule_count),
            stage=stage,
            train_eps=datasets["train"],
            val_eps=datasets["val"],
            test_eps=datasets["test"],
            config=config,
            run_id=run_id,
            curve_handle=curve_handle,
        )
        eval_report = evaluate_model_on_cell(
            run_id=run_id,
            seed=int(seed),
            stage=stage,
            capacity_tag=capacity_tag,
            capacity=cap_params,
            rule_count=int(rule_count),
            model=trained.model,
            episodes=datasets["test"],
            config=config,
            trace_handle=trace_handle,
            precomputed_meta_preds=trained.test_preds,
        )
        ablation = context_ablation_report(
            run_id=run_id,
            seed=int(seed),
            stage=stage,
            capacity_tag=capacity_tag,
            capacity=cap_params,
            rule_count=int(rule_count),
            model=trained.model,
            eval_eps=datasets["test"],
            normal_meta_mean=float(eval_report["meta_mean"]),
            fair_max=float(eval_report["fair_max"]),
            config=config,
            trace_handle=trace_handle,
        )
        per_seed.append(
            {
                "seed": int(seed),
                "training": _training_report(stage, int(seed), capacity_tag, cap_params, trained),
                "evaluation": eval_report,
                "context_ablation": ablation,
                "seed_clear": bool(float(eval_report["meta_mean"]) >= float(eval_report["ideal_mean"]) - config.delta),
                "fair_saturates": bool(float(eval_report["fair_max"]) >= float(eval_report["ideal_mean"]) - config.delta),
                "ablation_destroyed": bool(ablation["both_modes_advantage_destroyed"]),
            }
        )
        del trained.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    leakage = run_leakage_report(stage, capacity_tag, int(rule_count), datasets["test"])
    seed_clear_count = sum(1 for row in per_seed if row["seed_clear"])
    ablation_count = sum(1 for row in per_seed if row["ablation_destroyed"])
    fair_saturation = any(bool(row["fair_saturates"]) for row in per_seed)
    admissible_clear = bool(
        seed_clear_count >= int(config.clear_count_min)
        and ablation_count >= int(config.clear_count_min)
        and bool(leakage["detector_valid"])
        and not fair_saturation
    )
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.run_cell",
        "run_id": run_id,
        "stage": stage,
        "capacity_tag": capacity_tag,
        "capacity": cap_params,
        "parameter_count": parameter_count(build_model(cap_params)),
        "rule_count": int(rule_count),
        "dataset_source": datasets["source"],
        "rule_ids": datasets["rule_ids"],
        "per_seed": per_seed,
        "leakage": leakage,
        "seed_clear_count": int(seed_clear_count),
        "ablation_destroyed_count": int(ablation_count),
        "fair_saturation": bool(fair_saturation),
        "leakage_detector_valid": bool(leakage["detector_valid"]),
        "admissible_clear": admissible_clear,
        "claim_ceiling": "rung1 seen-rule cell only",
    }


def consistency_control_result(cell: dict[str, Any], config: RunConfig, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {
            "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.consistency_control_result",
            "asserted": False,
            "dry_run_reason": "tiny dry-run intentionally does not assert the banked C0 0.52 consistency gate",
            "gate_pass": None,
            "per_seed": [],
        }
    rows = []
    for row in cell["per_seed"]:
        seed_key = str(row["seed"])
        observed = float(row["evaluation"]["meta_mean"])
        expected = float(config.consistency_expected_meta[seed_key])
        rows.append(
            {
                "seed": int(row["seed"]),
                "observed_meta": observed,
                "expected_banked_meta": expected,
                "abs_diff": abs(observed - expected),
                "within_tolerance": bool(abs(observed - expected) <= config.consistency_tolerance),
            }
        )
    pass_count = sum(1 for row in rows if row["within_tolerance"])
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.consistency_control_result",
        "asserted": True,
        "tolerance": float(config.consistency_tolerance),
        "required_pass_count": int(config.clear_count_min),
        "pass_count": int(pass_count),
        "gate_pass": bool(pass_count >= int(config.clear_count_min)),
        "per_seed": rows,
    }


def _mean(values: Iterable[float]) -> float:
    vals = [float(v) for v in values]
    return float(sum(vals) / len(vals)) if vals else 0.0


def decide_route(phase1_cells: list[dict[str, Any]], phase2_cells: list[dict[str, Any]], dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {
            "verdict": "dry_run_wiring_only",
            "route": "stop_for_review",
            "evidential": False,
            "full_scout_launched": False,
        }
    cleared_172 = [cell["capacity_tag"] for cell in phase1_cells if cell["admissible_clear"]]
    if cleared_172:
        return {
            "verdict": "H_cap_supported_at_172_scout",
            "route": "reopen_rung3_powered_at_cleared_capacity_after_powered_rung1_confirm",
            "cleared_capacity_tags": cleared_172,
        }
    breakpoints: dict[str, int] = {}
    for tag in sorted({cell["capacity_tag"] for cell in phase2_cells}):
        cleared = [int(cell["rule_count"]) for cell in phase2_cells if cell["capacity_tag"] == tag and cell["admissible_clear"]]
        breakpoints[tag] = max(cleared) if cleared else 0
    if breakpoints and breakpoints.get("C2", 0) > breakpoints.get("C0", 0):
        verdict = "H_cap_supported_breakpoint_moves_scout"
        route = "scale_up"
    else:
        verdict = "H_arch_supported_flat_breakpoint_scout"
        route = "downgrade_retrieval_line_or_redesign_architecture"
    return {
        "verdict": verdict,
        "route": route,
        "breakpoints": breakpoints,
        "claim_ceiling": FROZEN_DESIGN["claim_ceiling"],
    }


def replay_trace(trace_path: Path, cells: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((str(row["cell_id"]), str(row["mode"])), []).append(row)

    def mean_field(cell_id: str, mode: str, field: str) -> float:
        return mean_episode_score([float(row[field]) for row in grouped.get((cell_id, mode), [])])

    diffs: list[float] = []
    reconstructed: list[dict[str, Any]] = []
    for cell in cells:
        for seed_row in cell["per_seed"]:
            cell_id = f"{cell['stage']}:{cell['capacity_tag']}:k{int(cell['rule_count'])}:seed{int(seed_row['seed'])}"
            meta = mean_field(cell_id, "normal", "meta_balacc")
            ideal = mean_field(cell_id, "normal", "ideal_balacc")
            fair_by_name: dict[str, list[float]] = {}
            for row in grouped.get((cell_id, "normal"), []):
                for name, value in dict(row.get("fair_balacc", {})).items():
                    fair_by_name.setdefault(str(name), []).append(float(value))
            fair_max = max(mean_episode_score(values) for values in fair_by_name.values()) if fair_by_name else 0.0
            recorded_eval = seed_row["evaluation"]
            diffs.extend(
                [
                    abs(meta - float(recorded_eval["meta_mean"])),
                    abs(ideal - float(recorded_eval["ideal_mean"])),
                    abs(fair_max - float(recorded_eval["fair_max"])),
                ]
            )
            reconstructed.append(
                {
                    "cell_id": cell_id,
                    "seed": int(seed_row["seed"]),
                    "meta_mean": meta,
                    "ideal_mean": ideal,
                    "fair_max": fair_max,
                }
            )
    max_abs_diff = max(diffs) if diffs else 0.0
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.replay_trace",
        "trace_path": path_label(trace_path),
        "trace_rows": len(rows),
        "reconstructed_cells": reconstructed,
        "max_abs_diff": float(max_abs_diff),
        "tolerance": 1e-9,
        "metrics_reconstructed_exact": bool(max_abs_diff <= 1e-9),
        "claim_ceiling": "trace replay verification only; not evidence-strength upgrade",
    }


def write_failure_manifest(out_dir: Path, exc: BaseException, config: RunConfig | None = None) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    if isinstance(exc, StopRung1Sweep):
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
            "dry_run": bool(config.dry_run) if config else None,
            "evidential": False,
            "full_scout_launched": False,
            "git_head": git_output(["rev-parse", "HEAD"], check=False).strip(),
            "git_branch": git_output(["branch", "--show-current"], check=False).strip(),
            "git_status": git_output(["status", "--porcelain=v1", "--untracked-files=all"], check=False).splitlines(),
            "claim_ceiling": FROZEN_DESIGN["claim_ceiling"],
        }
    )
    write_json(out_dir / "failure_manifest.json", payload)


def run_orchestration(
    *,
    dry_run: bool,
    out_dir: Path | None = None,
    dry_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = build_run_config(dry_run=dry_run, dry_overrides=dry_overrides)
    out = Path(out_dir) if out_dir is not None else (DRY_RUN_DIR if dry_run else FULL_SCOUT_DIR)
    out.mkdir(parents=True, exist_ok=True)
    run_id = (
        ("tlgp-rung1-capacity-sweep-dry-" if dry_run else "tlgp-rung1-capacity-sweep-full-")
        + time.strftime("%Y%m%d-%H%M%S-")
        + uuid.uuid4().hex[:8]
    )
    try:
        governance = validate_governance(config)
        trace_path = out / "trace.jsonl"
        val_curves_path = out / "val_curves.jsonl"
        with trace_path.open("w", encoding="utf-8") as trace_handle, val_curves_path.open("w", encoding="utf-8") as curve_handle:
            c0 = run_cell(
                run_id=run_id,
                stage="c0_consistency_control",
                capacity_tag="C0",
                rule_count=172,
                config=config,
                trace_handle=trace_handle,
                curve_handle=curve_handle,
            )
            consistency = consistency_control_result(c0, config, dry_run)
            if not dry_run and not bool(consistency["gate_pass"]):
                write_json(out / "result.json", {"task_id": TASK_ID, "run_id": run_id, "consistency_control": consistency, "evidential": False})
                raise StopRung1Sweep("c0_consistency_control", "C0 banked rung1 consistency control failed", consistency, ">=2/3 seeds within +-0.03")
            phase1: list[dict[str, Any]]
            if dry_run:
                phase1 = []
            else:
                phase1 = [dict(c0, stage_alias="phase1_capacity_172", reused_from="c0_consistency_control")]
            for tag in config.phase1_capacity_tags:
                if tag == "C0" and not dry_run:
                    continue
                phase1.append(
                    run_cell(
                        run_id=run_id,
                        stage="phase1_capacity_172",
                        capacity_tag=str(tag),
                        rule_count=172,
                        config=config,
                        trace_handle=trace_handle,
                        curve_handle=curve_handle,
                    )
                )
            phase2: list[dict[str, Any]] = []
            if not dry_run and not any(cell["admissible_clear"] for cell in phase1):
                for rule_count in config.phase2_rule_counts:
                    for tag in config.phase1_capacity_tags:
                        phase2.append(
                            run_cell(
                                run_id=run_id,
                                stage="phase2_breakpoint_map",
                                capacity_tag=str(tag),
                                rule_count=int(rule_count),
                                config=config,
                                trace_handle=trace_handle,
                                curve_handle=curve_handle,
                            )
                        )
        all_cells = [c0] + [cell for cell in phase1 if cell.get("reused_from") != "c0_consistency_control"] + phase2
        replay = replay_trace(trace_path, all_cells)
        if not bool(replay["metrics_reconstructed_exact"]):
            raise StopRung1Sweep("replay", "trace replay failed to reconstruct cell metrics", replay, "max_abs_diff <= 1e-9")
        route_decision = decide_route(phase1, phase2, dry_run)
        baseline_comparison = {
            "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.evaluate_fair_panel",
            "cells": [
                {
                    "stage": cell["stage"],
                    "capacity_tag": cell["capacity_tag"],
                    "rule_count": cell["rule_count"],
                    "per_seed_evaluation": [row["evaluation"] for row in cell["per_seed"]],
                }
                for cell in all_cells
            ],
        }
        ablation_report = {
            "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.context_ablation_report",
            "cells": [
                {
                    "stage": cell["stage"],
                    "capacity_tag": cell["capacity_tag"],
                    "rule_count": cell["rule_count"],
                    "per_seed_context_ablation": [row["context_ablation"] for row in cell["per_seed"]],
                    "both_modes_collapse_count": sum(1 for row in cell["per_seed"] if row["ablation_destroyed"]),
                }
                for cell in all_cells
            ],
        }
        leakage_report = {
            "producer_function": "src.tlgp_capability_witness_preflight_001a.rung1_capacity_sweep.run_leakage_report",
            "cells": [
                {
                    "stage": cell["stage"],
                    "capacity_tag": cell["capacity_tag"],
                    "rule_count": cell["rule_count"],
                    "leakage": cell["leakage"],
                }
                for cell in all_cells
            ],
        }
        result = {
            "task_id": TASK_ID,
            "run_id": run_id,
            "dry_run": bool(dry_run),
            "evidential": not dry_run,
            "full_scout_launched": not dry_run,
            "phase": "DRY_RUN" if dry_run else "FULL_SCOUT",
            "design_canonical_sha256": EXPECTED_DESIGN_SHA256,
            "consistency_control": consistency,
            "phase1": phase1,
            "phase2": phase2,
            "route_decision": route_decision,
            "claim_ceiling": "non-evidential wiring proof only" if dry_run else FROZEN_DESIGN["claim_ceiling"],
        }
        manifest = {
            "task_id": TASK_ID,
            "run_id": run_id,
            "dry_run": bool(dry_run),
            "evidential": not dry_run,
            "full_scout_launched": not dry_run,
            "required_files": REQUIRED_FILES + (["dry_run_report.json"] if dry_run else []),
            "runner_sha256": sha256_file(RUNNER_PATH),
            "retrieval_model_sha256": SOURCE_PINS["src/tlgp_capability_witness_preflight_001a/retrieval_model.py"],
            "phase_design_sha256": EXPECTED_DESIGN_SHA256,
            "prereg_sha256": EXPECTED_PREREG_SHA256,
            "capacity_grid": FROZEN_DESIGN["capacity_grid"],
            "per_cell_parameter_count": {
                tag: parameter_count(build_model(capacity_params(tag)))
                for tag in FROZEN_DESIGN["capacity_grid"]["phase1"]
            },
            "grid": {
                "phase1": FROZEN_DESIGN["phase1"],
                "phase2": FROZEN_DESIGN["phase2"],
            },
            "gpu_env": gpu_env_report(),
            "device_readback": ML.device_readback(),
            "source_pins": governance["source_pins"],
            "protected_tracked_diff_names": governance["protected_tracked_diff_names"],
            "trace_lfs_required_by_gitattributes": "artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/**/*.jsonl",
            "auto_remote_anchor": "forbidden",
        }
        write_json(out / "result.json", result)
        write_json(out / "baseline_comparison.json", baseline_comparison)
        write_json(out / "ablation_report.json", ablation_report)
        write_json(out / "leakage_report.json", leakage_report)
        write_json(out / "replay_report.json", replay)
        write_json(out / "manifest.json", manifest)
        if dry_run:
            write_json(
                out / "dry_run_report.json",
                {
                    "task_id": TASK_ID,
                    "run_id": run_id,
                    "dry_run": True,
                    "evidential": False,
                    "full_scout_launched": False,
                    "c0_consistency_path_exercised": True,
                    "c0_consistency_gate_asserted": False,
                    "phase1_cell_exercised": True,
                    "phase1_cell_count": len(phase1),
                    "training_runs": True,
                    "ideal_computed": True,
                    "fair_panel_computed": True,
                    "leakage_computed": True,
                    "advantage_destroyed_ablation_computed": True,
                    "all_evidence_files_written": all((out / name).exists() for name in REQUIRED_FILES),
                    "replay_metrics_reconstructed_exact": replay["metrics_reconstructed_exact"],
                    "replay_max_abs_diff": replay["max_abs_diff"],
                    "claim_ceiling": "non-evidential wiring proof only",
                },
            )
        return {
            "task_id": TASK_ID,
            "run_id": run_id,
            "out_dir": path_label(out),
            "dry_run": bool(dry_run),
            "evidential": not dry_run,
            "full_scout_launched": not dry_run,
            "route_decision": route_decision,
            "design_canonical_sha256": EXPECTED_DESIGN_SHA256,
            "runner_sha256": sha256_file(RUNNER_PATH),
            "required_files_written": [name for name in REQUIRED_FILES if (out / name).exists()],
        }
    except BaseException as exc:
        write_failure_manifest(out, exc, config)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--full-run", action="store_true")
    parser.add_argument("--confirm-full-run", default="", help="must equal frozen rung1 capacity sweep design SHA")
    parser.add_argument("--out-dir", default="")
    args = parser.parse_args(argv)
    try:
        if args.validate_only:
            cfg = build_run_config(dry_run=False)
            print(json.dumps(validate_governance(cfg), indent=2, sort_keys=True))
            return 0
        if args.dry_run == args.full_run:
            parser.error("choose exactly one of --dry-run or --full-run")
        if args.full_run and args.confirm_full_run != EXPECTED_DESIGN_SHA256:
            raise StopRung1Sweep(
                "full_run_confirmation",
                "full scout requires explicit frozen design SHA confirmation",
                args.confirm_full_run,
                EXPECTED_DESIGN_SHA256,
            )
        out = Path(args.out_dir) if args.out_dir else None
        report = run_orchestration(dry_run=bool(args.dry_run), out_dir=out)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except BaseException as exc:
        out = Path(args.out_dir) if args.out_dir else (DRY_RUN_DIR if args.dry_run else FULL_SCOUT_DIR)
        config = build_run_config(dry_run=bool(args.dry_run)) if (args.dry_run or args.full_run) else None
        write_failure_manifest(out, exc, config)
        print(f"Rung1 capacity sweep runner stopped: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
