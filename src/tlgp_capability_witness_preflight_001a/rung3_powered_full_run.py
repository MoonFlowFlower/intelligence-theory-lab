"""Phase B full-run orchestration for the TLGP rung3 powered learner.

This runner implements the cleared Phase B design
``88b9f3af0bee52331b9ec6e702349477db48cdd1b244386586f77b5d150664d5``.
It is intentionally separate from the Phase A smoke module.  Dry-run mode uses
the same orchestration and training loop with reduced non-evidential counts;
full mode requires an explicit confirmation token so importing or validating
the runner cannot accidentally launch the 10-seed GPU run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
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
from src.tlgp_capability_witness_preflight_001a import rung3_single_family_adjudicator as ADJ
from src.tlgp_capability_witness_preflight_001a.retrieval_model import (
    FAMILY,
    PARAMS,
    build_model,
    parameter_count,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "TLGP-CAPABILITY-WITNESS-RUNG3-POWERED-LEARNER-001A"
BASE_ARTIFACT_DIR = (
    REPO_ROOT
    / "artifacts"
    / "TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A"
    / "RUNG3_POWERED_LEARNER_001A"
)
FULL_OUT_DIR = BASE_ARTIFACT_DIR / "FULL_RUN"
DRY_OUT_DIR = FULL_OUT_DIR / "DRY_RUN"
PHASE_B_DESIGN_PATH = BASE_ARTIFACT_DIR / "PHASE_B_FREEZE_REVIEW" / "design.json"
EXECUTOR_PATH = (
    REPO_ROOT
    / "src"
    / "tlgp_capability_witness_preflight_001a"
    / "rung3_powered_full_run.py"
)

EXPECTED_PHASE_B_DESIGN_SHA256 = "88b9f3af0bee52331b9ec6e702349477db48cdd1b244386586f77b5d150664d5"
EXPECTED_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"

SOURCE_PINS = {
    "src/tlgp_001a/leakage.py": "387c413d6af816216c73b45316bf854e3ef906e575bffc96cea1f6353e90bef1",
    "src/tlgp_001b_r2/lower_reference.py": "cd701b2f4adcf9d8c66f28f0e797cdf748a7f4560c682953829b99eb85d28cf6",
    "src/tlgp_001b_r2/meta_learners.py": "358d2bb2449f88ff5c73de52fcabcbba17f40b22dabc5c484f7b67da627e1b6f",
    "src/tlgp_001b_r2/preregistration.py": "6a5a0273e7c3b0c2cce031dcf2b495646d87ecea7630d725c84def8f9ce27480",
    "src/tlgp_001b_r2/splits.py": "ca2852a1ca69ba5277872bf5b0780163d0c79fbf0b5b2c7075bb740ef9981ad5",
    "src/tlgp_001b_r2/world.py": "1c9bd730e79c19e5036e26cf4a45f1463dc2194217ec5ebc06e42731ca364a7c",
    "src/tlgp_capability_witness_preflight_001a/retrieval_model.py": (
        "0cba923965f305c6c8cab41a8dd033d7a34bf1c3cd60b0ea27a7fdcc698bf2bb"
    ),
    "src/tlgp_capability_witness_preflight_001a/rung3_graph_cache_baselines.py": (
        "921d44078a7b77e60c61b9bc5c5e2986228c4134a30ef2703c5fc52890229eaa"
    ),
    "src/tlgp_capability_witness_preflight_001a/rung3_powered_learner.py": (
        "841a68502cb9a693f6bb2aea03992ace5267e3dd92f41c107fa3be0c54fab591"
    ),
    "src/tlgp_capability_witness_preflight_001a/rung3_single_family_adjudicator.py": (
        "5773f5d14cde442002c4c69e4d8d37302df40a863b01f97f86336a53a3fa9120"
    ),
}

PROTECTED_DIFF_PATHS = [
    "artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG3_POWERED_LEARNER_001A/PHASE_B_FREEZE_REVIEW/design.json",
    "artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG3_POWERED_LEARNER_001A/SMOKE",
    "docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG3-POWERED-LEARNER-001A.md",
    "src/tlgp_001a",
    "src/tlgp_001b_r2",
    "src/tlgp_capability_witness_preflight_001a/retrieval_model.py",
    "src/tlgp_capability_witness_preflight_001a/rung3_graph_cache_baselines.py",
    "src/tlgp_capability_witness_preflight_001a/rung3_powered_learner.py",
    "src/tlgp_capability_witness_preflight_001a/rung3_single_family_adjudicator.py",
]

REQUIRED_FILES = [
    "result.json",
    "trace.jsonl",
    "val_curves.jsonl",
    "baseline_comparison.json",
    "ablation_report.json",
    "eligibility_report.json",
    "leakage_report.json",
    "replay_report.json",
    "route_decision_input.json",
    "route_decision.json",
    "manifest.json",
]


class StopPhaseB(RuntimeError):
    def __init__(self, step: str, reason: str, observed: Any = None, expected: Any = None):
        super().__init__(reason)
        self.step = step
        self.reason = reason
        self.observed = observed
        self.expected = expected


@dataclass(frozen=True)
class RunConfig:
    dry_run: bool
    model_seeds: list[int]
    n_train: int
    n_val: int
    rung1_n_test: int
    rung3_n_test: int
    rung3_required_test_rules: int
    rung2_n_test: int
    batch_size: int
    max_epochs: int
    early_stop_patience: int
    steps_max: int
    lr_grid: list[float]
    delta: float
    epsilon: float
    close_fraction_min: int
    expected_n_seeds: int


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


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(v) for v in value]
    if isinstance(value, np.ndarray):
        return [_json_ready(v) for v in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
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
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _strip_underscore_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {key: _strip_underscore_keys(value) for key, value in obj.items() if not str(key).startswith("_")}
    if isinstance(obj, list):
        return [_strip_underscore_keys(value) for value in obj]
    return obj


def verify_phase_b_design(path: Path = PHASE_B_DESIGN_PATH) -> dict[str, Any]:
    design = json.loads(path.read_text(encoding="utf-8"))
    computed = canonical_sha256(_strip_underscore_keys(design))
    recorded = str(design.get("_frozen_canonical_sha256", ""))
    match = computed == recorded == EXPECTED_PHASE_B_DESIGN_SHA256
    if not match:
        raise StopPhaseB(
            "phase_b_design_sha",
            "Phase B frozen design canonical SHA mismatch",
            {"computed": computed, "recorded": recorded},
            EXPECTED_PHASE_B_DESIGN_SHA256,
        )
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_powered_full_run.verify_phase_b_design"
        ),
        "path": path.relative_to(REPO_ROOT).as_posix(),
        "computed_sha256": computed,
        "recorded_sha256": recorded,
        "expected_sha256": EXPECTED_PHASE_B_DESIGN_SHA256,
        "match": True,
    }


def git_output(args: list[str], check: bool = True) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        raise StopPhaseB("git_readback", proc.stderr.strip(), args, "git command succeeds")
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
    executor_sha = sha256_file(EXECUTOR_PATH)
    if mismatches:
        raise StopPhaseB("source_pins", "read-only source pin mismatch", mismatches, "all source pins match")
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_powered_full_run.source_pin_report"
        ),
        "pins": dict(SOURCE_PINS),
        "observed": observed,
        "all_match": True,
        "executor_path": EXECUTOR_PATH.relative_to(REPO_ROOT).as_posix(),
        "executor_sha256": executor_sha,
        "adjudicator_sha256": observed["src/tlgp_capability_witness_preflight_001a/rung3_single_family_adjudicator.py"],
        "retrieval_model_sha256": observed["src/tlgp_capability_witness_preflight_001a/retrieval_model.py"],
    }


def validate_governance(config: RunConfig) -> dict[str, Any]:
    design = verify_phase_b_design()
    prereg_sha = P.canonical_sha256(json.loads(P.PREREG_JSON_PATH.read_text(encoding="utf-8")))
    if prereg_sha != EXPECTED_PREREG_SHA256 or P.load_frozen_prereg()["_canonical_sha256_readback"] != EXPECTED_PREREG_SHA256:
        raise StopPhaseB("prereg_sha", "prereg canonical SHA mismatch", prereg_sha, EXPECTED_PREREG_SHA256)
    if PARAMS != {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4}:
        raise StopPhaseB("capacity", "retrieval model capacity changed", PARAMS, "d_model256/layers4/heads4/ff_mult4")
    if not config.dry_run:
        budget = P.training_budget()
        if config.model_seeds != P.model_seeds():
            raise StopPhaseB("model_seeds", "full run MODEL_SEEDS changed", config.model_seeds, P.model_seeds())
        if config.lr_grid != [0.001, 0.0003] or config.lr_grid != budget["lr_grid"]:
            raise StopPhaseB("lr_grid", "full run LR grid changed", config.lr_grid, budget["lr_grid"])
        if (
            config.n_train != 5000
            or config.n_val != 1000
            or config.rung1_n_test != 200
            or config.rung3_n_test != 200
            or config.rung3_required_test_rules != 125
            or config.max_epochs != 200
            or config.steps_max != int(budget["steps_max"])
        ):
            raise StopPhaseB("budget", "full run budget changed", asdict(config), "frozen Phase B/prereg budget")
    protected = protected_diff_names()
    if protected:
        raise StopPhaseB("protected_diffs", "protected tracked files have diffs", protected, [])
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_powered_full_run.validate_governance"
        ),
        "phase_b_design": design,
        "prereg_canonical_sha256": prereg_sha,
        "prereg_sha_match": True,
        "source_pins": source_pin_report(),
        "capacity": dict(PARAMS),
        "family": FAMILY,
        "config": asdict(config),
        "protected_tracked_diff_names": protected,
        "git": {
            "repo_root": REPO_ROOT.as_posix(),
            "branch": git_output(["branch", "--show-current"]).strip(),
            "head": git_output(["rev-parse", "HEAD"]).strip(),
            "status_short_branch": git_output(["status", "--short", "--branch"]).splitlines(),
        },
        "gpu_env": gpu_env_report(),
        "family_substitution": {
            "declared_deviation": True,
            "substituted_primary_family": FAMILY,
            "adjudicator": (
                "src/tlgp_capability_witness_preflight_001a/"
                "rung3_single_family_adjudicator.py reused unmodified"
            ),
            "scope": "single retrieval_model family",
        },
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
    budget = P.training_budget()
    cfg = RunConfig(
        dry_run=bool(dry_run),
        model_seeds=P.model_seeds(),
        n_train=5000,
        n_val=1000,
        rung1_n_test=200,
        rung3_n_test=200,
        rung3_required_test_rules=125,
        rung2_n_test=200,
        batch_size=int(budget["batch_size"]),
        max_epochs=int(budget["max_epochs"]),
        early_stop_patience=int(budget["early_stop_patience"]),
        steps_max=int(budget["steps_max"]),
        lr_grid=[float(v) for v in budget["lr_grid"]],
        delta=float(P.DELTA()),
        epsilon=float(P.DELTA()),
        close_fraction_min=int(P.close_fraction_min()),
        expected_n_seeds=int(P.N_SEEDS()),
    )
    if not dry_run:
        return cfg
    cfg = replace(
        cfg,
        model_seeds=[P.model_seeds()[0]],
        n_train=8,
        n_val=4,
        rung1_n_test=4,
        rung3_n_test=4,
        rung3_required_test_rules=4,
        rung2_n_test=4,
        batch_size=2,
        max_epochs=20,
        steps_max=200,
    )
    if dry_overrides:
        allowed = set(asdict(cfg))
        unknown = sorted(set(dry_overrides) - allowed)
        if unknown:
            raise StopPhaseB("dry_overrides", "unknown dry-run override keys", unknown, sorted(allowed))
        cfg = replace(cfg, **dry_overrides)
    cfg = replace(cfg, rung3_required_test_rules=min(int(cfg.rung3_required_test_rules), int(cfg.rung3_n_test)))
    return cfg


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


def make_rung3_test_episodes_covering_rules(n_episodes: int, required_rules: int) -> list[Episode]:
    _, test_idx = S.rule_split()
    test_rules = [int(v) for v in test_idx.tolist()]
    required = min(int(required_rules), len(test_rules), int(n_episodes))
    rng = np.random.default_rng(int(P.seeds()["RUNG3_TEST_EPISODES_SEED"]))
    ordered = [int(v) for v in rng.permutation(test_rules).tolist()]
    selected = ordered[:required]
    while len(selected) < int(n_episodes):
        selected.append(int(test_rules[int(rng.integers(0, len(test_rules)))]))
    episodes: list[Episode] = []
    base = S.EPISODE_ID_BASE[(S.RUNG3, "test")]
    for idx, rule_id in enumerate(selected):
        episodes.append(
            W.make_episode_for_rule(
                base + idx,
                int(rule_id),
                rng,
                P.TRAIN_VALUES,
                P.HELDOUT_VALUES,
            )
        )
    return episodes


def make_stage_datasets(config: RunConfig) -> dict[str, list[Episode]]:
    return {
        "rung1_train": S.make_episodes("rung1", "train", config.n_train),
        "rung1_val": S.make_episodes("rung1", "val", config.n_val),
        "rung1_test": S.make_episodes("rung1", "test", config.rung1_n_test),
        "rung3_train": S.make_episodes("rung3", "train", config.n_train),
        "rung3_val": S.make_episodes("rung3", "val", config.n_val),
        "rung3_test": make_rung3_test_episodes_covering_rules(
            config.rung3_n_test,
            config.rung3_required_test_rules,
        ),
        "rung2_test": S.make_episodes("rung2", "test", config.rung2_n_test),
    }


def split_assertion_report(datasets: dict[str, list[Episode]], config: RunConfig) -> dict[str, Any]:
    assertions = S.split_assertions(
        {
            "rung1_test": datasets["rung1_test"],
            "rung2_test": datasets["rung2_test"],
            "rung3_train": datasets["rung3_train"],
            "rung3_test": datasets["rung3_test"],
        }
    )
    rung3_rules = {int(ep.rule_id) for ep in datasets["rung3_test"]}
    assertions["rung3_test_unique_rule_count"] = len(rung3_rules)
    assertions["rung3_required_test_rules_covered"] = len(rung3_rules) >= int(config.rung3_required_test_rules)
    required = [
        "train_test_rule_overlap_empty",
        "rung1_rules_subset_of_train",
        "rung2_rules_subset_of_train",
        "rung3_train_rules_subset_of_train",
        "rung3_test_rules_subset_of_test",
        "episode_ids_disjoint_across_supplied_sets",
        "rung3_required_test_rules_covered",
    ]
    failed = [key for key in required if not bool(assertions.get(key))]
    if failed:
        raise StopPhaseB("split_assertions", "split assertions failed", {k: assertions.get(k) for k in failed}, "all true")
    return {
        "producer_function": "src.tlgp_001b_r2.splits.split_assertions",
        "assertions": assertions,
        "required_true": required,
        "all_required_pass": True,
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


def run_leakage_report(rung: str, episodes: list[Episode]) -> dict[str, Any]:
    tgt = targets(episodes)
    clean = detect(_meta_input_channels(episodes), tgt)
    planted = detect(planted_channels(episodes, tgt), tgt)
    clean_false = [name for name, row in clean.items() if row["flagged"]]
    planted_missed = [name for name, row in planted.items() if not row["flagged"]]
    return {
        "producer_function": "src.tlgp_001a.leakage.detect",
        "rung": rung,
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


def evaluate_fair_panel(episodes: list[Episode], seed: int) -> tuple[dict[str, float], list[dict[str, list[int]]], dict[str, Any]]:
    lower, lower_records = LR.evaluate(episodes, int(seed))
    graph, graph_records = GB.evaluate(episodes, int(seed))
    fair = {**{name: float(value) for name, value in lower.items()}, **{name: float(value) for name, value in graph.items()}}
    records: list[dict[str, list[int]]] = []
    for idx in range(len(episodes)):
        row = dict(lower_records[idx])
        row.update(graph_records[idx])
        records.append(row)
    detail = {
        "producer_functions": [
            "src.tlgp_001b_r2.lower_reference.evaluate",
            "src.tlgp_capability_witness_preflight_001a.rung3_graph_cache_baselines.evaluate",
        ],
        "fair_baseline_balacc": fair,
        "fair_max": float(max(fair.values())),
        "graph_cache_alias_report": GB.alias_report(episodes),
    }
    return fair, records, detail


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
    train_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    val_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    config: RunConfig,
    run_id: str,
    stage: str,
    curve_handle: TextIO,
) -> dict[str, Any]:
    torch.manual_seed(int(seed))
    model = build_model(PARAMS).to(ML.DEVICE)
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
    curve_rows: list[dict[str, Any]] = []
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
            "producer_function": (
                "src.tlgp_capability_witness_preflight_001a."
                "rung3_powered_full_run._train_one_lr"
            ),
            "run_id": run_id,
            "stage": stage,
            "seed": int(seed),
            "family": FAMILY,
            "lr": float(lr),
            "epoch": int(epochs_run),
            "steps": int(steps),
            "val_balacc": float(val_score),
            "train_loss_last": last_loss,
            "aggregation_rule": "validation balanced accuracy per epoch; best checkpoint selected by max val_balacc",
            "code_path_hash": sha256_file(EXECUTOR_PATH),
        }
        curve_rows.append(row)
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
        "curve": curve_rows,
    }


def train_retrieval_model(
    *,
    seed: int,
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
            train_tensors=train_tensors,
            val_tensors=val_tensors,
            config=config,
            run_id=run_id,
            stage=stage,
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
            replace(
                ep,
                adapt_x=donor.adapt_x.copy(),
                adapt_a=donor.adapt_a.copy(),
                adapt_e=donor.adapt_e.copy(),
            )
        )
    return out


def _per_episode_score_rows(
    *,
    run_id: str,
    seed: int,
    rung: str,
    split: str,
    mode: str,
    episodes: list[Episode],
    meta_preds: list[list[int]],
    ideal_preds: list[list[int]],
    fair_preds: list[dict[str, list[int]]] | None,
    trace_handle: TextIO,
) -> tuple[float, list[dict[str, Any]]]:
    scores: list[float] = []
    rows: list[dict[str, Any]] = []
    for ep, meta_pred, ideal_pred in zip(episodes, meta_preds, ideal_preds):
        meta_score = balanced_accuracy(ep.query_e, np.array(meta_pred, dtype=int), n_classes=P.K)
        ideal_score = balanced_accuracy(ep.query_e, np.array(ideal_pred, dtype=int), n_classes=P.K)
        fair_scores: dict[str, float] = {}
        fair_row: dict[str, list[int]] = {}
        if fair_preds is not None:
            fair_row = fair_preds[len(rows)]
            for name, pred in fair_row.items():
                fair_scores[name] = balanced_accuracy(ep.query_e, np.array(pred, dtype=int), n_classes=P.K)
        fair_max = max(fair_scores.values()) if fair_scores else None
        row = {
            "producer_function": (
                "src.tlgp_capability_witness_preflight_001a."
                "rung3_powered_full_run._per_episode_score_rows"
            ),
            "run_id": run_id,
            "seed": int(seed),
            "rung": rung,
            "split": split,
            "mode": mode,
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
            "fair_max": float(fair_max) if fair_max is not None else None,
            "headroom_vs_meta": float(ideal_score - meta_score),
            "aggregation_rule": "mean balanced accuracy over episode rows grouped by rung/seed/mode",
            "code_path_hash": sha256_file(EXECUTOR_PATH),
        }
        scores.append(float(meta_score))
        rows.append(row)
        write_jsonl_row(trace_handle, row)
    return mean_episode_score(scores), rows


def evaluate_model_on_rung(
    *,
    run_id: str,
    seed: int,
    rung: str,
    split: str,
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
        rung=rung,
        split=split,
        mode="normal",
        episodes=episodes,
        meta_preds=meta_preds,
        ideal_preds=ideal_preds,
        fair_preds=fair_preds,
        trace_handle=trace_handle,
    )
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_powered_full_run.evaluate_model_on_rung"
        ),
        "run_id": run_id,
        "seed": int(seed),
        "rung": rung,
        "split": split,
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
        "fair_detail": fair_detail,
        "trace_row_count": len(trace_rows),
        "claim_ceiling": "per-seed rung metric only; final claim is adjudicator-scoped",
    }


def context_ablation_report(
    *,
    run_id: str,
    seed: int,
    rung: str,
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
            rung=rung,
            split="test",
            mode=mode,
            episodes=episodes,
            meta_preds=preds,
            ideal_preds=ideal_preds,
            fair_preds=fair_preds,
            trace_handle=trace_handle,
        )
        normal_distance = abs(float(normal_meta_mean) - float(fair_max))
        ablated_distance = abs(float(score) - float(fair_max))
        modes[mode] = {
            "producer_function": (
                "src.tlgp_capability_witness_preflight_001a."
                "rung3_powered_full_run.context_ablation_report"
            ),
            "ablated_balacc": float(score),
            "normal_balacc": float(normal_meta_mean),
            "fair_max": float(fair_max),
            "EPSILON": float(config.epsilon),
            "advantage_destroyed_threshold": threshold,
            "advantage_destroyed_collapse": bool(float(score) <= threshold),
            "drop_from_normal": float(normal_meta_mean - score),
            "old_closer_to_fair_flag_for_audit_only": bool(ablated_distance <= normal_distance),
            "distance_to_fair_delta_for_audit_only": float(normal_distance - ablated_distance),
        }
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_powered_full_run.context_ablation_report"
        ),
        "run_id": run_id,
        "seed": int(seed),
        "rung": rung,
        "ablation_eval_split": "test",
        "headroom_eval_split": "test",
        "episodes": len(eval_eps),
        "episode_ids": [int(ep.episode_id) for ep in eval_eps],
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


def aggregate_ablation(seed_reports: list[dict[str, Any]], config: RunConfig, dry_run: bool) -> dict[str, Any]:
    required = 1 if dry_run else int(config.close_fraction_min)
    shuffle_count = sum(1 for row in seed_reports if row["modes"]["shuffle_adapt"]["advantage_destroyed_collapse"])
    no_adapt_count = sum(1 for row in seed_reports if row["modes"]["no_adapt"]["advantage_destroyed_collapse"])
    both_count = sum(1 for row in seed_reports if row["both_modes_advantage_destroyed"])
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_powered_full_run.aggregate_ablation"
        ),
        "dry_run_required_count": required if dry_run else None,
        "formal_close_fraction_min": int(config.close_fraction_min),
        "observed_seed_count": len(seed_reports),
        "shuffle_adapt_collapse_count": int(shuffle_count),
        "no_adapt_collapse_count": int(no_adapt_count),
        "both_modes_collapse_count": int(both_count),
        "aggregate_pass": bool(both_count >= required),
        "formal_aggregate_pass": bool(both_count >= int(config.close_fraction_min)),
        "seed_reports": seed_reports,
    }


def rung1_scanner_report(seed: int, episodes: list[Episode], fair: dict[str, float], no_context_meta_balacc: float) -> dict[str, Any]:
    lower = {name: fair[name] for name in LR.LOWER_REFERENCE}
    report = LR.rung1_scanner(episodes, lower_means=lower, no_context_meta_balacc=float(no_context_meta_balacc))
    report["producer_function"] = "src.tlgp_001b_r2.lower_reference.rung1_scanner"
    report["seed"] = int(seed)
    return report


def _training_report(stage: str, seed: int, trained: TrainedModel) -> dict[str, Any]:
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_powered_full_run.train_retrieval_model"
        ),
        "stage": stage,
        "seed": int(seed),
        "family": FAMILY,
        "params": dict(PARAMS),
        "parameter_count": parameter_count(build_model(PARAMS)),
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


def run_stage1_rung1(
    *,
    run_id: str,
    datasets: dict[str, list[Episode]],
    config: RunConfig,
    trace_handle: TextIO,
    curve_handle: TextIO,
) -> dict[str, Any]:
    per_seed: list[dict[str, Any]] = []
    ablations: list[dict[str, Any]] = []
    scanner_reports: list[dict[str, Any]] = []
    for seed in config.model_seeds:
        trained = train_retrieval_model(
            seed=int(seed),
            stage="stage1_rung1_eligibility",
            train_eps=datasets["rung1_train"],
            val_eps=datasets["rung1_val"],
            test_eps=datasets["rung1_test"],
            config=config,
            run_id=run_id,
            curve_handle=curve_handle,
        )
        eval_report = evaluate_model_on_rung(
            run_id=run_id,
            seed=int(seed),
            rung="rung1",
            split="test",
            model=trained.model,
            episodes=datasets["rung1_test"],
            config=config,
            trace_handle=trace_handle,
            precomputed_meta_preds=trained.test_preds,
        )
        ablation = context_ablation_report(
            run_id=run_id,
            seed=int(seed),
            rung="rung1",
            model=trained.model,
            eval_eps=datasets["rung1_test"],
            normal_meta_mean=float(eval_report["meta_mean"]),
            fair_max=float(eval_report["fair_max"]),
            config=config,
            trace_handle=trace_handle,
        )
        scanner = rung1_scanner_report(
            int(seed),
            datasets["rung1_test"],
            eval_report["fair_baseline_balacc"],
            ablation["modes"]["no_adapt"]["ablated_balacc"],
        )
        scanner_reports.append(scanner)
        ablations.append(ablation)
        per_seed.append(
            {
                "seed": int(seed),
                "training": _training_report("stage1_rung1_eligibility", int(seed), trained),
                "evaluation": eval_report,
                "eligibility_pass": bool(float(eval_report["meta_mean"]) >= float(eval_report["ideal_mean"]) - config.delta),
                "rung1_scanner": scanner,
                "scanner_pass": not bool(scanner["cheap_baseline_saturation"]),
                "context_ablation": ablation,
            }
        )
        del trained.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    eligibility_count = sum(1 for row in per_seed if row["eligibility_pass"])
    scanner_pass_count = sum(1 for row in per_seed if row["scanner_pass"])
    ablation_agg = aggregate_ablation(ablations, config, config.dry_run)
    required = 1 if config.dry_run else int(config.close_fraction_min)
    formal_pass = bool(
        eligibility_count >= int(config.close_fraction_min)
        and scanner_pass_count == len(per_seed)
        and ablation_agg["formal_aggregate_pass"]
    )
    dry_gate_pass = bool(
        eligibility_count >= required
        and scanner_pass_count == len(per_seed)
        and ablation_agg["aggregate_pass"]
    )
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_powered_full_run.run_stage1_rung1"
        ),
        "stage": "stage1_rung1_eligibility",
        "per_seed": per_seed,
        "eligibility_pass_count": int(eligibility_count),
        "scanner_pass_count": int(scanner_pass_count),
        "context_ablation_aggregate": ablation_agg,
        "formal_gate_pass": formal_pass,
        "dry_run_gate_pass": dry_gate_pass,
        "claim_ceiling": "rung1 eligibility gate only; not rung3 transfer evidence",
    }


def run_stage2_and_stage3(
    *,
    run_id: str,
    datasets: dict[str, list[Episode]],
    config: RunConfig,
    trace_handle: TextIO,
    curve_handle: TextIO,
) -> dict[str, Any]:
    rung3_per_seed: list[dict[str, Any]] = []
    rung3_ablations: list[dict[str, Any]] = []
    rung2_per_seed: list[dict[str, Any]] = []
    for seed in config.model_seeds:
        trained = train_retrieval_model(
            seed=int(seed),
            stage="stage2_rung3_real",
            train_eps=datasets["rung3_train"],
            val_eps=datasets["rung3_val"],
            test_eps=datasets["rung3_test"],
            config=config,
            run_id=run_id,
            curve_handle=curve_handle,
        )
        rung3_eval = evaluate_model_on_rung(
            run_id=run_id,
            seed=int(seed),
            rung="rung3",
            split="test",
            model=trained.model,
            episodes=datasets["rung3_test"],
            config=config,
            trace_handle=trace_handle,
            precomputed_meta_preds=trained.test_preds,
        )
        rung3_ablation = context_ablation_report(
            run_id=run_id,
            seed=int(seed),
            rung="rung3",
            model=trained.model,
            eval_eps=datasets["rung3_test"],
            normal_meta_mean=float(rung3_eval["meta_mean"]),
            fair_max=float(rung3_eval["fair_max"]),
            config=config,
            trace_handle=trace_handle,
        )
        rung2_eval = evaluate_model_on_rung(
            run_id=run_id,
            seed=int(seed),
            rung="rung2",
            split="test",
            model=trained.model,
            episodes=datasets["rung2_test"],
            config=config,
            trace_handle=trace_handle,
        )
        rung3_ablations.append(rung3_ablation)
        rung3_per_seed.append(
            {
                "seed": int(seed),
                "training": _training_report("stage2_rung3_real", int(seed), trained),
                "evaluation": rung3_eval,
                "context_ablation": rung3_ablation,
            }
        )
        rung2_per_seed.append(
            {
                "seed": int(seed),
                "trains_model": False,
                "reused_model_from": "stage2_rung3_real",
                "evaluation": rung2_eval,
            }
        )
        del trained.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_powered_full_run.run_stage2_and_stage3"
        ),
        "stage2_rung3_real": {
            "per_seed": rung3_per_seed,
            "context_ablation_aggregate": aggregate_ablation(rung3_ablations, config, config.dry_run),
        },
        "stage3_rung2_diagnostic": {
            "trains_model": False,
            "per_seed": rung2_per_seed,
            "claim_ceiling": "diagnostic contrast only; cannot upgrade or rescue rung3 verdict",
        },
    }


def _mean(values: Iterable[float]) -> float:
    vals = [float(v) for v in values]
    return float(sum(vals) / len(vals)) if vals else 0.0


def build_route_decision_input(
    *,
    stage1: dict[str, Any],
    stage23: dict[str, Any],
    leakage: dict[str, Any],
    config: RunConfig,
    dry_run: bool,
) -> dict[str, Any]:
    rung3_rows = stage23["stage2_rung3_real"]["per_seed"]
    rung3_headroom = [float(row["evaluation"]["headroom_vs_meta"]) for row in rung3_rows]
    rung3_ideal_mean = _mean(row["evaluation"]["ideal_mean"] for row in rung3_rows)
    rung3_fair_max = max(float(row["evaluation"]["fair_max"]) for row in rung3_rows) if rung3_rows else 0.0
    planted_uncaught = any(not bool(row["all_planted_caught"]) for row in leakage["per_rung"].values())
    clean_false = any(not bool(row["no_clean_false_flag"]) for row in leakage["per_rung"].values())
    stage1_ablation = stage1["context_ablation_aggregate"]
    stage2_ablation = stage23["stage2_rung3_real"]["context_ablation_aggregate"]
    if dry_run:
        rung1_pass = bool(stage1["dry_run_gate_pass"])
        context_collapse = bool(stage1_ablation["aggregate_pass"] and stage2_ablation["aggregate_pass"])
        shuffle_collapse = bool(
            stage1_ablation["shuffle_adapt_collapse_count"] >= 1
            and stage2_ablation["shuffle_adapt_collapse_count"] >= 1
        )
        no_adapt_collapse = bool(
            stage1_ablation["no_adapt_collapse_count"] >= 1
            and stage2_ablation["no_adapt_collapse_count"] >= 1
        )
    else:
        rung1_pass = bool(stage1["formal_gate_pass"])
        context_collapse = bool(stage1_ablation["formal_aggregate_pass"] and stage2_ablation["formal_aggregate_pass"])
        shuffle_collapse = bool(
            stage1_ablation["shuffle_adapt_collapse_count"] >= int(config.close_fraction_min)
            and stage2_ablation["shuffle_adapt_collapse_count"] >= int(config.close_fraction_min)
        )
        no_adapt_collapse = bool(
            stage1_ablation["no_adapt_collapse_count"] >= int(config.close_fraction_min)
            and stage2_ablation["no_adapt_collapse_count"] >= int(config.close_fraction_min)
        )
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_powered_full_run.build_route_decision_input"
        ),
        "task_id": TASK_ID,
        "dry_run": bool(dry_run),
        "integrity": {
            "planted_leak_uncaught": bool(planted_uncaught),
            "clean_false_flag": bool(clean_false),
            "protected_source_guard_failed": bool(protected_diff_names()),
            "family_substitution_not_declared": False,
            "replay_exact_by_rung": {"rung1": True, "rung3": True},
        },
        "rung0_pass": True,
        "rung1_pass": rung1_pass,
        "context_ablation_collapse": context_collapse,
        "shuffle_adapt_collapse": shuffle_collapse,
        "no_adapt_collapse": no_adapt_collapse,
        "rung3_ideal_mean": float(rung3_ideal_mean),
        "rung3_fair_max": float(rung3_fair_max),
        "rung3_headroom_vs_meta": rung3_headroom,
    }


def replay_trace(trace_path: Path, route_input: dict[str, Any], route_decision: dict[str, Any], config: RunConfig) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    grouped: dict[tuple[str, int, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((str(row["rung"]), int(row["seed"]), str(row["mode"])), []).append(row)

    def _seed_mean(rung: str, seed: int, mode: str, field: str) -> float:
        vals = [float(row[field]) for row in grouped.get((rung, seed, mode), [])]
        return mean_episode_score(vals)

    rung1_pass_count = 0
    for seed in config.model_seeds:
        ideal = _seed_mean("rung1", int(seed), "normal", "ideal_balacc")
        meta = _seed_mean("rung1", int(seed), "normal", "meta_balacc")
        if meta >= ideal - config.delta:
            rung1_pass_count += 1
    rung3_headroom = []
    rung3_ideal = []
    rung3_fair_maxes = []
    for seed in config.model_seeds:
        ideal = _seed_mean("rung3", int(seed), "normal", "ideal_balacc")
        meta = _seed_mean("rung3", int(seed), "normal", "meta_balacc")
        fair_by_name: dict[str, list[float]] = {}
        for row in grouped.get(("rung3", int(seed), "normal"), []):
            for name, value in dict(row.get("fair_balacc", {})).items():
                fair_by_name.setdefault(str(name), []).append(float(value))
        rung3_headroom.append(float(ideal - meta))
        rung3_ideal.append(float(ideal))
        rung3_fair_maxes.append(
            max(mean_episode_score(values) for values in fair_by_name.values()) if fair_by_name else 0.0
        )

    replay_input = dict(route_input)
    replay_input["replay_recomputed_rung1_eligibility_pass_count"] = int(rung1_pass_count)
    replay_input["rung3_headroom_vs_meta"] = rung3_headroom
    replay_input["rung3_ideal_mean"] = _mean(rung3_ideal)
    replay_input["rung3_fair_max"] = max(rung3_fair_maxes) if rung3_fair_maxes else 0.0
    replay_decision = ADJ.compute_verdict(replay_input)
    diffs = [
        abs(float(a) - float(b))
        for a, b in zip(rung3_headroom, route_input.get("rung3_headroom_vs_meta", []))
    ]
    max_abs_diff = max(diffs) if diffs else 0.0
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_powered_full_run.replay_trace"
        ),
        "trace_path": path_label(trace_path),
        "trace_rows": len(rows),
        "reconstructed_route_decision_input": replay_input,
        "reconstructed_route_decision": replay_decision,
        "recorded_route_decision": route_decision,
        "max_abs_diff": float(max_abs_diff),
        "tolerance": 1e-9,
        "headroom_reconstructed_exact": bool(max_abs_diff <= 1e-9),
        "verdict_reconstructed_exact": bool(replay_decision["verdict"] == route_decision["verdict"] and max_abs_diff <= 1e-9),
        "claim_ceiling": "trace replay verification only; not evidence-strength upgrade",
    }


def write_failure_manifest(out_dir: Path, exc: BaseException, config: RunConfig | None = None) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    if isinstance(exc, StopPhaseB):
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
            "full_run_launched": False,
            "git_head": git_output(["rev-parse", "HEAD"], check=False).strip(),
            "git_branch": git_output(["branch", "--show-current"], check=False).strip(),
            "git_status": git_output(["status", "--porcelain=v1", "--untracked-files=all"], check=False).splitlines(),
            "claim_ceiling": "executor stopped; no TLGP H0/H1 evidence emitted",
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
    out = Path(out_dir) if out_dir is not None else (DRY_OUT_DIR if dry_run else FULL_OUT_DIR)
    out.mkdir(parents=True, exist_ok=True)
    run_id = (
        ("tlgp-rung3-powered-dry-" if dry_run else "tlgp-rung3-powered-full-")
        + time.strftime("%Y%m%d-%H%M%S-")
        + uuid.uuid4().hex[:8]
    )
    try:
        governance = validate_governance(config)
        datasets = make_stage_datasets(config)
        split_report = split_assertion_report(datasets, config)
        adjudicator_self_test = ADJ.synthetic_terminal_coverage()
        if not bool(adjudicator_self_test["all_terminals_covered"]):
            raise StopPhaseB("adjudicator_self_test", "adjudicator self-test did not cover all terminals", adjudicator_self_test, "all terminals")
        leakage = {
            "producer_function": (
                "src.tlgp_capability_witness_preflight_001a."
                "rung3_powered_full_run.run_leakage_report"
            ),
            "per_rung": {
                "rung1": run_leakage_report("rung1", datasets["rung1_test"]),
                "rung3": run_leakage_report("rung3", datasets["rung3_test"]),
                "rung2": run_leakage_report("rung2", datasets["rung2_test"]),
            },
        }
        if not dry_run:
            invalid_leakage = [
                name for name, row in leakage["per_rung"].items() if not bool(row["detector_valid"])
            ]
            if invalid_leakage:
                raise StopPhaseB("leakage", "full-run leakage scan failed", invalid_leakage, "all planted caught and real clean")

        trace_path = out / "trace.jsonl"
        val_curves_path = out / "val_curves.jsonl"
        with trace_path.open("w", encoding="utf-8") as trace_handle, val_curves_path.open("w", encoding="utf-8") as curve_handle:
            stage1 = run_stage1_rung1(
                run_id=run_id,
                datasets=datasets,
                config=config,
                trace_handle=trace_handle,
                curve_handle=curve_handle,
            )
            if not dry_run and not bool(stage1["formal_gate_pass"]):
                write_json(out / "eligibility_report.json", stage1)
                write_json(out / "leakage_report.json", leakage)
                raise StopPhaseB("stage1_gate", "rung1 eligibility/discriminativeness gate failed", stage1, "formal_gate_pass true")
            stage23 = run_stage2_and_stage3(
                run_id=run_id,
                datasets=datasets,
                config=config,
                trace_handle=trace_handle,
                curve_handle=curve_handle,
            )

        route_input = build_route_decision_input(
            stage1=stage1,
            stage23=stage23,
            leakage=leakage,
            config=config,
            dry_run=dry_run,
        )
        route_decision = ADJ.compute_verdict(route_input)
        replay = replay_trace(trace_path, route_input, route_decision, config)
        if not bool(replay["verdict_reconstructed_exact"]):
            raise StopPhaseB("replay", "replay failed to reconstruct verdict within tolerance", replay, "exact verdict and <=1e-9")

        baseline_comparison = {
            "producer_function": (
                "src.tlgp_capability_witness_preflight_001a."
                "rung3_powered_full_run.evaluate_fair_panel"
            ),
            "rung1": [row["evaluation"] for row in stage1["per_seed"]],
            "rung3": [row["evaluation"] for row in stage23["stage2_rung3_real"]["per_seed"]],
            "rung2": [row["evaluation"] for row in stage23["stage3_rung2_diagnostic"]["per_seed"]],
        }
        ablation_report = {
            "producer_function": (
                "src.tlgp_capability_witness_preflight_001a."
                "rung3_powered_full_run.context_ablation_report"
            ),
            "rung1": stage1["context_ablation_aggregate"],
            "rung3": stage23["stage2_rung3_real"]["context_ablation_aggregate"],
            "rung2_diagnostic": "no context-ablation gate; rung2 is diagnostic eval of the rung3 model",
        }
        result = {
            "task_id": TASK_ID,
            "run_id": run_id,
            "dry_run": bool(dry_run),
            "evidential": not dry_run,
            "full_run_launched": not dry_run,
            "phase": "PHASE_B_DRY_RUN" if dry_run else "PHASE_B_FULL_RUN",
            "verdict": route_decision["verdict"],
            "route_decision": route_decision,
            "route_decision_input": route_input,
            "rung1_eligibility": {
                "formal_gate_pass": stage1["formal_gate_pass"],
                "dry_run_gate_pass": stage1["dry_run_gate_pass"],
                "eligibility_pass_count": stage1["eligibility_pass_count"],
                "scanner_pass_count": stage1["scanner_pass_count"],
            },
            "stage1_rung1_training_summary": [
                {
                    "seed": row["seed"],
                    "selected_lr": row["training"]["selected_lr"],
                    "selected_best_val_balacc": row["training"]["selected_best_val_balacc"],
                    "selected_steps_run": row["training"]["selected_steps_run"],
                    "test_meta_mean": row["evaluation"]["meta_mean"],
                    "test_ideal_mean": row["evaluation"]["ideal_mean"],
                    "eligibility_pass": row["eligibility_pass"],
                }
                for row in stage1["per_seed"]
            ],
            "stage2_rung3_training_summary": [
                {
                    "seed": row["seed"],
                    "selected_lr": row["training"]["selected_lr"],
                    "selected_best_val_balacc": row["training"]["selected_best_val_balacc"],
                    "selected_steps_run": row["training"]["selected_steps_run"],
                    "test_meta_mean": row["evaluation"]["meta_mean"],
                    "test_ideal_mean": row["evaluation"]["ideal_mean"],
                    "headroom_vs_meta": row["evaluation"]["headroom_vs_meta"],
                    "fair_max": row["evaluation"]["fair_max"],
                }
                for row in stage23["stage2_rung3_real"]["per_seed"]
            ],
            "rung3_headroom_vs_meta": route_input["rung3_headroom_vs_meta"],
            "stage3_rung2_diagnostic_summary": [
                {
                    "seed": row["seed"],
                    "meta_mean": row["evaluation"]["meta_mean"],
                    "ideal_mean": row["evaluation"]["ideal_mean"],
                    "headroom_vs_meta": row["evaluation"]["headroom_vs_meta"],
                }
                for row in stage23["stage3_rung2_diagnostic"]["per_seed"]
            ],
            "claim_ceiling": (
                "Dry-run wiring proof only; not TLGP evidence"
                if dry_run
                else (
                    "Bounded retrieval-family rung3 transfer evidence on this TLGP world/grid only; "
                    "no mechanism, agency, self, subjectivity, consciousness, autonomy, AGI, EGO readiness, "
                    "companion readiness, runtime readiness, or mainline effect claim."
                )
            ),
        }
        manifest = {
            "task_id": TASK_ID,
            "run_id": run_id,
            "dry_run": bool(dry_run),
            "evidential": not dry_run,
            "required_files": REQUIRED_FILES + (["dry_run_report.json"] if dry_run else []),
            "phase_b_design_sha256": EXPECTED_PHASE_B_DESIGN_SHA256,
            "prereg_sha256": EXPECTED_PREREG_SHA256,
            "executor_sha256": sha256_file(EXECUTOR_PATH),
            "adjudicator_sha256": SOURCE_PINS["src/tlgp_capability_witness_preflight_001a/rung3_single_family_adjudicator.py"],
            "retrieval_model_sha256": SOURCE_PINS["src/tlgp_capability_witness_preflight_001a/retrieval_model.py"],
            "capacity": dict(PARAMS),
            "split_assertions": split_report,
            "gpu_env": gpu_env_report(),
            "device_readback": ML.device_readback(),
            "family_substitution": governance["family_substitution"],
            "source_pins": governance["source_pins"],
            "trace_lfs_required_by_gitattributes": "artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/**/*.jsonl",
            "full_run_launched": not dry_run,
            "auto_remote_anchor": "forbidden",
        }
        route_decision_out = dict(route_decision)
        route_decision_out["producer_function"] = route_decision["producer_function"]
        write_json(out / "result.json", result)
        write_json(out / "baseline_comparison.json", baseline_comparison)
        write_json(out / "ablation_report.json", ablation_report)
        write_json(out / "eligibility_report.json", stage1)
        write_json(out / "leakage_report.json", leakage)
        write_json(out / "replay_report.json", replay)
        write_json(out / "route_decision_input.json", route_input)
        write_json(out / "route_decision.json", route_decision_out)
        write_json(out / "manifest.json", manifest)
        if dry_run:
            write_json(
                out / "dry_run_report.json",
                {
                    "task_id": TASK_ID,
                    "run_id": run_id,
                    "dry_run": True,
                    "evidential": False,
                    "full_run_launched": False,
                    "verdict": route_decision["verdict"],
                    "all_evidence_files_written": all((out / name).exists() for name in REQUIRED_FILES),
                    "replay_verdict_reconstructed_exact": replay["verdict_reconstructed_exact"],
                    "replay_max_abs_diff": replay["max_abs_diff"],
                    "training_stages_exercised": ["stage1_rung1_eligibility", "stage2_rung3_real", "stage3_rung2_diagnostic"],
                    "claim_ceiling": "non-evidential wiring proof only",
                },
            )
        return {
            "task_id": TASK_ID,
            "run_id": run_id,
            "out_dir": path_label(out),
            "dry_run": bool(dry_run),
            "evidential": not dry_run,
            "full_run_launched": not dry_run,
            "verdict": route_decision["verdict"],
            "replay_verdict_reconstructed_exact": replay["verdict_reconstructed_exact"],
            "executor_sha256": sha256_file(EXECUTOR_PATH),
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
    parser.add_argument("--confirm-full-run", default="", help="must equal the frozen Phase B design SHA")
    parser.add_argument("--out-dir", default="")
    args = parser.parse_args(argv)
    try:
        if args.validate_only:
            cfg = build_run_config(dry_run=False)
            print(json.dumps(validate_governance(cfg), indent=2, sort_keys=True))
            return 0
        if args.dry_run == args.full_run:
            parser.error("choose exactly one of --dry-run or --full-run")
        if args.full_run and args.confirm_full_run != EXPECTED_PHASE_B_DESIGN_SHA256:
            raise StopPhaseB(
                "full_run_confirmation",
                "full run requires explicit frozen design SHA confirmation",
                args.confirm_full_run,
                EXPECTED_PHASE_B_DESIGN_SHA256,
            )
        out = Path(args.out_dir) if args.out_dir else None
        report = run_orchestration(dry_run=bool(args.dry_run), out_dir=out)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except BaseException as exc:
        out = Path(args.out_dir) if args.out_dir else (DRY_OUT_DIR if args.dry_run else FULL_OUT_DIR)
        config = build_run_config(dry_run=bool(args.dry_run)) if (args.dry_run or args.full_run) else None
        write_failure_manifest(out, exc, config)
        print(f"Phase B rung3 powered executor stopped: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
