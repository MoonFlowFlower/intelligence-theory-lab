"""Phase A tiny smoke for the TLGP rung3 powered retrieval learner.

This is a wiring-only runner.  It freezes and verifies the single-family
retrieval deviation, runs one tiny smoke seed on rung1 and rung3, emits smoke
artifacts, and stops.  It intentionally does not expose a full 10-seed run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
import traceback
import uuid
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn

from src.tlgp_001a.leakage import detect, planted_channels, targets
from src.tlgp_001b_r2 import lower_reference as LR
from src.tlgp_001b_r2 import meta_learners as ML
from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_001b_r2 import splits as S
from src.tlgp_001b_r2.world import ideal_predictions
from src.tlgp_capability_witness_preflight_001a import rung3_graph_cache_baselines as GB
from src.tlgp_capability_witness_preflight_001a import rung3_single_family_adjudicator as ADJ
from src.tlgp_capability_witness_preflight_001a.grokking_probe import _eval_checkpoint
from src.tlgp_capability_witness_preflight_001a.retrieval_model import (
    FAMILY,
    PARAMS,
    build_model,
    parameter_count,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "TLGP-CAPABILITY-WITNESS-RUNG3-POWERED-LEARNER-001A"
SMOKE_TASK_ID = "TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG3_POWERED_LEARNER_001A/SMOKE"
OUT_DIR = (
    REPO_ROOT
    / "artifacts"
    / "TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A"
    / "RUNG3_POWERED_LEARNER_001A"
    / "SMOKE"
)
DESIGN_PATH = OUT_DIR / "design.json"
ADJUDICATOR_PATH = (
    REPO_ROOT
    / "src"
    / "tlgp_capability_witness_preflight_001a"
    / "rung3_single_family_adjudicator.py"
)
RUNNER_PATH = (
    REPO_ROOT
    / "src"
    / "tlgp_capability_witness_preflight_001a"
    / "rung3_powered_learner.py"
)

EXPECTED_DESIGN_SHA256 = "12e2a81c3ae418bf328481c8622cf45e4acc7237ffa06a8fafad4f6f781cafff"
EXPECTED_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"
EXPECTED_RETRIEVAL_MODEL_SHA256 = "0cba923965f305c6c8cab41a8dd033d7a34bf1c3cd60b0ea27a7fdcc698bf2bb"
EXPECTED_GROKKING_PROBE_SHA256 = "9126dc9273c5aac6c909de9d503e323609dca61c6d9e51fadd0d459a89d74555"
EXPECTED_META_LEARNERS_SHA256 = "358d2bb2449f88ff5c73de52fcabcbba17f40b22dabc5c484f7b67da627e1b6f"
EXPECTED_GRAPH_CACHE_SHA256 = "921d44078a7b77e60c61b9bc5c5e2986228c4134a30ef2703c5fc52890229eaa"

SMOKE_SEEDS = [20260710]
SMOKE_EPISODES = 8
SMOKE_BATCH_SIZE = 8
SMOKE_STEPS_MAX = 200
CHECKPOINT_EVERY_STEPS = 50
FAIR_BASELINE_NAMES = ["lookup", "count_table", "predict_all", "majority", "no_adaptation", "graph_cache"]


class StopPhaseA(RuntimeError):
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


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def canonical_design_sha256(path: Path = DESIGN_PATH) -> str:
    return canonical_sha256(_strip_underscore_keys(json.loads(path.read_text(encoding="utf-8"))))


def canonical_prereg_sha256() -> str:
    return canonical_sha256(json.loads(P.PREREG_JSON_PATH.read_text(encoding="utf-8")))


def git_output(args: list[str], check: bool = True) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        raise StopPhaseA("git_readback", proc.stderr.strip(), args, "git command succeeds")
    return proc.stdout


def protected_diff_names() -> list[str]:
    return git_output(
        [
            "diff",
            "--name-only",
            "--",
            "docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG3-POWERED-LEARNER-001A.md",
            "src/tlgp_001b_r2/verdict.py",
            "src/tlgp_capability_witness_preflight_001a/route_decision.py",
            "src/tlgp_001b_r2/meta_learners.py",
            "src/tlgp_capability_witness_preflight_001a/retrieval_model.py",
            "src/tlgp_001b_r2",
            "src/tlgp_001a",
        ]
    ).splitlines()


def _assert_hash(name: str, path: Path, expected: str) -> str:
    observed = sha256_file(path)
    if observed != expected:
        raise StopPhaseA(name, "source hash mismatch", observed, expected)
    return observed


def validate_governance() -> dict[str, Any]:
    design = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    design_sha = canonical_design_sha256()
    prereg_sha = canonical_prereg_sha256()
    source_hashes = {
        "retrieval_model_sha256": _assert_hash(
            "retrieval_model_sha",
            REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "retrieval_model.py",
            EXPECTED_RETRIEVAL_MODEL_SHA256,
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
        "rung3_graph_cache_baselines_sha256": _assert_hash(
            "rung3_graph_cache_baselines_sha",
            REPO_ROOT / "src" / "tlgp_capability_witness_preflight_001a" / "rung3_graph_cache_baselines.py",
            EXPECTED_GRAPH_CACHE_SHA256,
        ),
    }
    if design_sha != EXPECTED_DESIGN_SHA256 or design.get("_frozen_canonical_sha256") != EXPECTED_DESIGN_SHA256:
        raise StopPhaseA(
            "frozen_design_sha",
            "frozen design canonical SHA mismatch",
            {"computed": design_sha, "recorded": design.get("_frozen_canonical_sha256")},
            EXPECTED_DESIGN_SHA256,
        )
    if prereg_sha != EXPECTED_PREREG_SHA256 or P.load_frozen_prereg()["_canonical_sha256_readback"] != EXPECTED_PREREG_SHA256:
        raise StopPhaseA("prereg_sha", "prereg canonical SHA mismatch", prereg_sha, EXPECTED_PREREG_SHA256)
    if PARAMS != {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4}:
        raise StopPhaseA("capacity_guard", "retrieval model capacity changed", PARAMS, "256/4/4/4")
    if P.model_seeds() != [
        20260710,
        20260711,
        20260712,
        20260713,
        20260714,
        20260715,
        20260716,
        20260717,
        20260718,
        20260719,
    ]:
        raise StopPhaseA("model_seeds", "MODEL_SEEDS differ from prereg expectation", P.model_seeds(), "10 frozen seeds")
    budget = P.training_budget()
    if budget.get("lr_grid") != [0.001, 0.0003] or int(budget.get("steps_max", -1)) != 200000:
        raise StopPhaseA("training_budget", "training budget or lr policy differs from prereg", budget, "prereg budget")
    if not bool(design["family_substitution"]["declared_deviation"]):
        raise StopPhaseA("family_substitution", "family substitution is not declared", design["family_substitution"], "declared")
    if design["family_substitution"]["substituted_primary_family"] != FAMILY:
        raise StopPhaseA("family_substitution_family", "substituted family mismatch", design["family_substitution"], FAMILY)
    protected = protected_diff_names()
    if protected:
        raise StopPhaseA("banked_frozen_edits", "protected tracked files have diffs", protected, [])
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a.rung3_powered_learner.validate_governance"
        ),
        "design_canonical_sha256": design_sha,
        "prereg_canonical_sha256": prereg_sha,
        "source_hashes": source_hashes,
        "capacity": dict(PARAMS),
        "model_seeds": P.model_seeds(),
        "training_budget": budget,
        "family_substitution_declared": True,
        "protected_tracked_diff_names": protected,
        "git_head": git_output(["rev-parse", "HEAD"]).strip(),
        "git_branch": git_output(["branch", "--show-current"]).strip(),
        "device": ML.device_readback(),
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


def run_leakage_report(rung: str, episodes) -> dict[str, Any]:
    tgt = targets(episodes)
    clean = detect(_meta_input_channels(episodes), tgt)
    planted = detect(planted_channels(episodes, tgt), tgt)
    clean_false = [name for name, row in clean.items() if row["flagged"]]
    planted_missed = [name for name, row in planted.items() if not row["flagged"]]
    report = {
        "producer_function": "src.tlgp_001a.leakage.detect",
        "rung": rung,
        "episodes": len(episodes),
        "meta_input_channels_declared": ["adapt_x", "adapt_a", "adapt_e", "query_x", "query_a"],
        "meta_forbidden_inputs": ["rule_id", "query_e"],
        "clean_false_flags": clean_false,
        "planted_missed": planted_missed,
        "all_planted_caught": not planted_missed,
        "renamed_leak_caught": bool(planted["telemetry_7"]["flagged"]),
        "answer_leak_caught": bool(planted["calib_value"]["flagged"]),
        "no_clean_false_flag": not clean_false,
        "detector_valid": not planted_missed and not clean_false,
        "clean_report": clean,
        "planted_report": planted,
    }
    if not report["all_planted_caught"]:
        raise StopPhaseA("leakage", f"{rung} planted leakage control missed", report, "all planted caught")
    return report


def make_shuffled_adapt_episodes(episodes, seed: int):
    rng = np.random.default_rng(int(seed))
    perm = rng.permutation(len(episodes))
    if len(episodes) > 1 and any(int(i) == int(j) for i, j in enumerate(perm)):
        perm = np.roll(perm, 1)
    out = []
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


def evaluate_fair_panel(episodes, seed: int) -> tuple[dict[str, float], dict[str, Any]]:
    lower, lower_records = LR.evaluate(episodes, int(seed))
    graph, graph_records = GB.evaluate(episodes, int(seed))
    fair = {**{name: float(value) for name, value in lower.items()}, **{name: float(value) for name, value in graph.items()}}
    return fair, {
        "producer_functions": [
            "src.tlgp_001b_r2.lower_reference.evaluate",
            "src.tlgp_capability_witness_preflight_001a.rung3_graph_cache_baselines.evaluate",
        ],
        "fair_baseline_balacc": fair,
        "fair_max": float(max(fair.values())),
        "records_sample": {
            "lower_reference_first": lower_records[0] if lower_records else {},
            "graph_cache_first": graph_records[0] if graph_records else {},
        },
    }


def _train_for_lr(
    *,
    seed: int,
    lr: float,
    train_t,
    val_t,
    steps_max: int,
    batch_size: int,
) -> dict[str, Any]:
    torch.manual_seed(int(seed))
    model = build_model(PARAMS).to(ML.DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(lr))
    lossf = nn.CrossEntropyLoss()
    ctx_tr, qx_tr, qy_tr = train_t
    n = int(ctx_tr.shape[0])
    generator = torch.Generator(device="cpu").manual_seed(int(seed) + int(float(lr) * 1_000_000))
    steps = 0
    curve: list[dict[str, Any]] = []
    best_val = float("-inf")
    best_state: dict[str, torch.Tensor] | None = None
    while steps < int(steps_max):
        model.train()
        perm = torch.randperm(n, generator=generator)
        for start in range(0, n, int(batch_size)):
            idx = perm[start:start + int(batch_size)].to(ctx_tr.device)
            logits = model(ctx_tr[idx], qx_tr[idx])
            loss = lossf(logits.reshape(-1, P.K), qy_tr[idx].reshape(-1))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            steps += 1
            if steps % CHECKPOINT_EVERY_STEPS == 0 or steps >= int(steps_max):
                train_score, val_score, _ = _eval_checkpoint(model, train_t, val_t)
                row = {
                    "lr": float(lr),
                    "step": int(steps),
                    "train_balacc": float(train_score),
                    "val_balacc": float(val_score),
                }
                curve.append(row)
                if float(val_score) > best_val:
                    best_val = float(val_score)
                    best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
            if steps >= int(steps_max):
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    return {"model": model, "best_val_balacc": best_val, "steps_run": steps, "curve": curve, "lr": float(lr)}


def train_tiny_model(*, seed: int, train_eps, val_eps, test_eps) -> dict[str, Any]:
    train_t = ML.move_tensors(ML.build_tensors(train_eps))
    val_t = ML.move_tensors(ML.build_tensors(val_eps))
    test_t = ML.move_tensors(ML.build_tensors(test_eps))
    lr_results = []
    best: dict[str, Any] | None = None
    for lr in P.training_budget()["lr_grid"]:
        result = _train_for_lr(
            seed=int(seed),
            lr=float(lr),
            train_t=train_t,
            val_t=val_t,
            steps_max=SMOKE_STEPS_MAX,
            batch_size=SMOKE_BATCH_SIZE,
        )
        lr_results.append({
            "lr": result["lr"],
            "best_val_balacc": result["best_val_balacc"],
            "steps_run": result["steps_run"],
            "curve": result["curve"],
        })
        if best is None or float(result["best_val_balacc"]) > float(best["best_val_balacc"]):
            best = result
        else:
            del result["model"]
    assert best is not None
    model = best["model"]
    train_balacc, test_balacc, test_preds = _eval_checkpoint(model, train_t, test_t)
    device = ML._record_device_run(FAMILY, model, [train_t, val_t, test_t], test_preds)
    return {
        "model": model,
        "selected_lr": float(best["lr"]),
        "selected_best_val_balacc": float(best["best_val_balacc"]),
        "train_balacc": float(train_balacc),
        "test_balacc": float(test_balacc),
        "test_preds": test_preds,
        "lr_policy": "prereg lr_grid with validation-balanced-accuracy selection",
        "lr_results": lr_results,
        "steps_per_lr_max": SMOKE_STEPS_MAX,
        "device": device,
    }


def context_ablation_report(*, model, seed: int, rung: str, eval_eps) -> dict[str, Any]:
    fair, _ = evaluate_fair_panel(eval_eps, seed)
    fair_max = float(max(fair.values()))
    normal_t = ML.move_tensors(ML.build_tensors(eval_eps))
    shuffle_t = ML.move_tensors(ML.build_tensors(make_shuffled_adapt_episodes(eval_eps, seed + 991)))
    no_adapt_t = ML.move_tensors(ML.build_tensors(eval_eps, context_ablate=True))
    normal_score, _ = ML._eval_tensors(model, normal_t, SMOKE_BATCH_SIZE)
    shuffle_score, _ = ML._eval_tensors(model, shuffle_t, SMOKE_BATCH_SIZE)
    no_adapt_score, _ = ML._eval_tensors(model, no_adapt_t, SMOKE_BATCH_SIZE)

    def _collapse(ablated: float) -> dict[str, Any]:
        drop = float(normal_score - ablated)
        normal_distance = abs(float(normal_score) - fair_max)
        ablated_distance = abs(float(ablated) - fair_max)
        crossed_or_closer = bool(ablated <= fair_max or ablated_distance <= normal_distance)
        return {
            "score": float(ablated),
            "drop_from_normal": drop,
            "distance_to_fair_delta": float(normal_distance - ablated_distance),
            "collapse_toward_fair_or_through_fair": bool(float(normal_score) >= fair_max and drop > 0.0 and crossed_or_closer),
        }

    shuffle = _collapse(float(shuffle_score))
    no_adapt = _collapse(float(no_adapt_score))
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a.rung3_powered_learner.context_ablation_report"
        ),
        "rung": rung,
        "eval_scope": "tiny_train_fit_smoke_not_evidence",
        "episodes": len(eval_eps),
        "fair_baseline_balacc": fair,
        "fair_max": fair_max,
        "normal_meta_balacc": float(normal_score),
        "shuffle_adapt": shuffle,
        "no_adapt": no_adapt,
        "both_ablation_paths_ran": True,
        "both_collapsed_toward_fair": bool(
            shuffle["collapse_toward_fair_or_through_fair"] and no_adapt["collapse_toward_fair_or_through_fair"]
        ),
        "claim_ceiling": "context-use smoke only; not formal discriminativeness evidence",
    }


def run_one_rung(rung: str, seed: int) -> dict[str, Any]:
    train_eps = S.make_episodes(rung, "train", SMOKE_EPISODES)
    val_eps = S.make_episodes(rung, "val", SMOKE_EPISODES)
    test_eps = S.make_episodes(rung, "test", SMOKE_EPISODES)
    ideal_mean, ideal_preds, ideal_scores = ideal_predictions(test_eps)
    fair, fair_detail = evaluate_fair_panel(test_eps, seed)
    ML.reset_device_runs()
    trained = train_tiny_model(seed=seed, train_eps=train_eps, val_eps=val_eps, test_eps=test_eps)
    headroom_vs_meta = float(ideal_mean - trained["test_balacc"])
    ablation = context_ablation_report(model=trained["model"], seed=seed, rung=rung, eval_eps=train_eps)
    del trained["model"]
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    rung_label = "rung1" if rung == "rung1" else "rung3"
    return {
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung3_powered_learner.run_one_rung",
        "rung": rung_label,
        "rung_source_arg": rung,
        "seed": int(seed),
        "train_episodes": len(train_eps),
        "val_episodes": len(val_eps),
        "test_episodes": len(test_eps),
        "ideal_mean": float(ideal_mean),
        "ideal_score_min": float(min(ideal_scores)) if ideal_scores else None,
        "ideal_predictions_first": ideal_preds[0] if ideal_preds else [],
        "meta_mean": float(trained["test_balacc"]),
        "meta_train_fit_balacc": float(trained["train_balacc"]),
        "headroom_vs_meta": headroom_vs_meta,
        "fair_baseline_balacc": fair,
        "fair_max": float(max(fair.values())),
        "fair_detail": fair_detail,
        "tiny_verdict": (
            "smoke_seed_reaches_formal_bar"
            if float(trained["test_balacc"]) >= float(ideal_mean) - P.DELTA()
            else "smoke_seed_below_formal_bar"
        ),
        "training": {
            "family": FAMILY,
            "params": dict(PARAMS),
            "parameter_count": parameter_count(build_model(PARAMS)),
            "selected_lr": trained["selected_lr"],
            "selected_best_val_balacc": trained["selected_best_val_balacc"],
            "lr_policy": trained["lr_policy"],
            "lr_results": trained["lr_results"],
            "steps_per_lr_max": trained["steps_per_lr_max"],
            "device": trained["device"],
        },
        "context_ablation": ablation,
        "claim_ceiling": "tiny smoke metric readback only; not evidence",
    }


def build_split_assertion_report() -> dict[str, Any]:
    datasets = {
        "rung1_test": S.make_episodes("rung1", "test", SMOKE_EPISODES),
        "rung2_test": S.make_episodes("rung2", "test", SMOKE_EPISODES),
        "rung3_train": S.make_episodes("rung3", "train", SMOKE_EPISODES),
        "rung3_test": S.make_episodes("rung3", "test", SMOKE_EPISODES),
    }
    assertions = S.split_assertions(datasets)
    required = [
        "train_test_rule_overlap_empty",
        "rung1_rules_subset_of_train",
        "rung2_rules_subset_of_train",
        "rung3_test_rules_subset_of_test",
        "rung3_train_rules_subset_of_train",
        "episode_ids_disjoint_across_supplied_sets",
    ]
    failed = [key for key in required if not bool(assertions.get(key))]
    if failed:
        raise StopPhaseA("split_assertions", "split assertions failed", {key: assertions.get(key) for key in failed}, "all true")
    return {
        "producer_function": "src.tlgp_001b_r2.splits.split_assertions",
        "assertions": assertions,
        "required_true": required,
        "all_required_pass": True,
    }


def copy_source_files() -> dict[str, str]:
    copied: dict[str, str] = {}
    for path in [RUNNER_PATH, ADJUDICATOR_PATH]:
        dest = OUT_DIR / path.name
        shutil.copy2(path, dest)
        copied[path.relative_to(REPO_ROOT).as_posix()] = dest.relative_to(REPO_ROOT).as_posix()
    return copied


def run_tiny_smoke() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failure_path = OUT_DIR / "failure_manifest.json"
    if failure_path.exists():
        failure_path.unlink()
    for name in ("smoke_report.json", RUNNER_PATH.name, ADJUDICATOR_PATH.name):
        path = OUT_DIR / name
        if path.exists():
            path.unlink()

    run_id = time.strftime("tlgp-rung3-powered-phase-a-smoke-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
    governance = validate_governance()
    split_report = build_split_assertion_report()
    self_test = ADJ.synthetic_terminal_coverage()
    if not bool(self_test["all_terminals_covered"]):
        raise StopPhaseA("adjudicator_self_test", "adjudicator self-test did not cover all terminals", self_test, "all terminals")
    leakage_reports = {
        "rung1": run_leakage_report("rung1", S.make_episodes("rung1", "test")),
        "rung3": run_leakage_report("rung3", S.make_episodes("rung3", "test")),
    }
    seed = SMOKE_SEEDS[0]
    rung1 = run_one_rung("rung1", seed)
    rung3 = run_one_rung("rung3", seed)
    if not bool(rung1["context_ablation"]["both_collapsed_toward_fair"]):
        raise StopPhaseA("rung1_context_ablation", "rung1 smoke context ablation did not collapse", rung1["context_ablation"], "collapse")
    if not bool(rung3["context_ablation"]["both_collapsed_toward_fair"]):
        raise StopPhaseA("rung3_context_ablation", "rung3 smoke context ablation did not collapse", rung3["context_ablation"], "collapse")

    adjudicator_input = {
        "integrity": {
            "planted_leak_uncaught": not all(bool(v["all_planted_caught"]) for v in leakage_reports.values()),
            "clean_false_flag": any(not bool(v["no_clean_false_flag"]) for v in leakage_reports.values()),
            "protected_source_guard_failed": bool(protected_diff_names()),
            "family_substitution_not_declared": not governance["family_substitution_declared"],
            "replay_exact_by_rung": {"rung1": True, "rung3": True},
        },
        "rung0_pass": True,
        "rung1_pass": bool(rung1["meta_mean"] >= rung1["ideal_mean"] - P.DELTA()),
        "context_ablation_collapse": bool(
            rung1["context_ablation"]["both_collapsed_toward_fair"]
            and rung3["context_ablation"]["both_collapsed_toward_fair"]
        ),
        "shuffle_adapt_collapse": bool(
            rung1["context_ablation"]["shuffle_adapt"]["collapse_toward_fair_or_through_fair"]
            and rung3["context_ablation"]["shuffle_adapt"]["collapse_toward_fair_or_through_fair"]
        ),
        "no_adapt_collapse": bool(
            rung1["context_ablation"]["no_adapt"]["collapse_toward_fair_or_through_fair"]
            and rung3["context_ablation"]["no_adapt"]["collapse_toward_fair_or_through_fair"]
        ),
        "rung3_ideal_mean": float(rung3["ideal_mean"]),
        "rung3_fair_max": float(rung3["fair_max"]),
        "rung3_headroom_vs_meta": [float(rung3["headroom_vs_meta"])],
    }
    adjudicator_verdict = ADJ.compute_verdict(adjudicator_input)
    source_copies = copy_source_files()
    report = {
        "task_id": TASK_ID,
        "smoke_task_id": SMOKE_TASK_ID,
        "run_id": run_id,
        "evidential": False,
        "full_run_launched": False,
        "phase": "A_freeze_implement_tiny_smoke_only",
        "producer_function": "src.tlgp_capability_witness_preflight_001a.rung3_powered_learner.run_tiny_smoke",
        "governance": governance,
        "split_assertions": split_report,
        "adjudicator_self_test": self_test,
        "leakage_reports": leakage_reports,
        "rung1": rung1,
        "rung3": rung3,
        "adjudicator_input": adjudicator_input,
        "adjudicator_verdict": adjudicator_verdict,
        "source_copies": source_copies,
        "smoke_budget": {
            "seeds": list(SMOKE_SEEDS),
            "episodes_per_split": SMOKE_EPISODES,
            "steps_per_lr_max": SMOKE_STEPS_MAX,
            "batch_size": SMOKE_BATCH_SIZE,
            "lr_grid": P.training_budget()["lr_grid"],
            "full_prereg_model_seed_count": P.N_SEEDS(),
            "full_prereg_steps_max": P.training_budget()["steps_max"],
        },
        "claim_ceiling": (
            "Phase A smoke-only wiring proof. No H0/H1 evidence, no mechanism/agency/self/"
            "subjectivity/AGI/EGO claim, and no production/mainline effect."
        ),
    }
    write_json(OUT_DIR / "smoke_report.json", report)
    return report


def write_failure_manifest(exc: BaseException) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if isinstance(exc, StopPhaseA):
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
            "evidential": False,
            "full_run_launched": False,
            "git_head": git_output(["rev-parse", "HEAD"], check=False).strip(),
            "git_branch": git_output(["branch", "--show-current"], check=False).strip(),
            "git_status": git_output(["status", "--porcelain=v1", "--untracked-files=all"], check=False).splitlines(),
            "claim_ceiling": "Phase A stopped; no TLGP evidence emitted",
        }
    )
    write_json(OUT_DIR / "failure_manifest.json", payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--adjudicator-self-test", action="store_true")
    parser.add_argument("--tiny-smoke", action="store_true")
    parser.add_argument("--full-run", action="store_true", help="refuses by design in Phase A")
    args = parser.parse_args(argv)
    try:
        if args.full_run:
            raise StopPhaseA("phase_a_full_run_forbidden", "full 10-seed run is forbidden in Phase A", True, False)
        if args.validate_only:
            print(json.dumps(validate_governance(), indent=2, sort_keys=True))
            return 0
        if args.adjudicator_self_test:
            report = ADJ.synthetic_terminal_coverage()
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if report["all_terminals_covered"] else 1
        if args.tiny_smoke:
            report = run_tiny_smoke()
            print(json.dumps({
                "run_id": report["run_id"],
                "design_canonical_sha256": report["governance"]["design_canonical_sha256"],
                "adjudicator_self_test_all_terminals": report["adjudicator_self_test"]["all_terminals_covered"],
                "rung1_tiny_verdict": report["rung1"]["tiny_verdict"],
                "rung3_tiny_verdict": report["rung3"]["tiny_verdict"],
                "rung3_adjudicator_verdict": report["adjudicator_verdict"]["verdict"],
                "full_run_launched": report["full_run_launched"],
            }, indent=2, sort_keys=True))
            return 0
        parser.error("use --validate-only, --adjudicator-self-test, or --tiny-smoke")
    except BaseException as exc:
        write_failure_manifest(exc)
        print(f"Phase A rung3 powered learner stopped: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
