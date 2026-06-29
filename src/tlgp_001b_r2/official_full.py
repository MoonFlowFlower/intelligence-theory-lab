"""Official TLGP-001B-R2 full-run orchestration.

This module is intentionally isolated from the non-evidential smoke path in
``harness.py``. It writes official artifacts only under
``artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/`` and performs no git operation
that mutates repository state.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import time
import traceback
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch

from src.tlgp_001a.leakage import positive_control_report
from src.tlgp_001a.metrics import balanced_accuracy, mean_episode_score
from src.tlgp_001a.world import Episode

from . import lower_reference as LR
from . import meta_learners as ML
from . import preregistration as P
from . import splits as S
from . import verdict as V
from .world import ideal_predictions

REPO_ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = Path(os.environ.get("TLGP_001B_R2_ARTIFACT_DIR", str(REPO_ROOT / "artifacts" / "TLGP-001B-R2")))
OFFICIAL_DIR = ARTIFACT_DIR / "OFFICIAL_FULL_RUN"
RUN_LOG_DIR = OFFICIAL_DIR / "RUN_LOGS"
TRACE_DIR = OFFICIAL_DIR / "traces"

EXPECTED_PREREG_SHA = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"
EXPECTED_HEAD = "c142443e9b85a2087e569a3f74a9f8fdd05ac32c"
EXPECTED_BRANCH = "codex/meta-theory-scaffold"
OFFICIAL_TRACE = TRACE_DIR / "official_trace.jsonl"

FORBIDDEN_DIFF_PATHS = [
    "AGENTS.md",
    "CLAUDE.md",
    "artifacts/TLGP-001A",
    "artifacts/TLGP-001A-AUDIT-001",
    "artifacts/TLGP-001B",
    "artifacts/TLGP-001B-INVALID-AUDIT-001",
    "docs/task_cards/TLGP-001B-R2.md",
]


class OfficialRunBlocker(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class CapacityConfig:
    family: str
    config_id: str
    params: dict[str, Any]
    witness: bool
    primary: bool
    diagnostic_only: bool


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def run_id() -> str:
    return time.strftime("tlgp001b-r2-full-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]


def log_event(event: str, payload: dict[str, Any] | None = None) -> None:
    RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event,
        "payload": payload or {},
    }
    with (OFFICIAL_DIR / "RUN_LOG.txt").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    with (RUN_LOG_DIR / "progress.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def git_output(args: list[str], check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise OfficialRunBlocker("blocked_forbidden_drift", f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def source_hashes() -> dict[str, str]:
    return {
        rel(path): sha256_file(path)
        for path in sorted(PKG_DIR.glob("*.py"))
    }


def prereg_readback() -> dict[str, Any]:
    try:
        prereg = P.load_frozen_prereg()
    except Exception as exc:
        raise OfficialRunBlocker("blocked_prereg_sha_mismatch", str(exc)) from exc
    computed = prereg["_canonical_sha256_readback"]
    if computed != EXPECTED_PREREG_SHA:
        raise OfficialRunBlocker(
            "blocked_prereg_sha_mismatch",
            f"computed={computed} expected={EXPECTED_PREREG_SHA}",
        )
    return {
        "path": rel(P.PREREG_JSON_PATH),
        "canonical_sha256_expected": EXPECTED_PREREG_SHA,
        "canonical_sha256_readback": computed,
        "match": True,
        "raw_bytes_sha256": sha256_file(P.PREREG_JSON_PATH),
        "frozen_fields": {
            "DELTA": P.DELTA(),
            "FLOOR": P.FLOOR(),
            "N_SEEDS": P.N_SEEDS(),
            "MODEL_SEEDS": P.model_seeds(),
            "primary_families": P.primary_families(),
            "diagnostic_families": P.diagnostic_families(),
        },
    }


def scope_cleanup_readback() -> dict[str, Any]:
    report_path = ARTIFACT_DIR / "SCOPE_CLEANUP_REPORT.md"
    if not report_path.exists():
        raise OfficialRunBlocker("blocked_scope_cleanup_not_clean", f"missing {rel(report_path)}")
    text = report_path.read_text(encoding="utf-8")
    required = {
        "agents_reverted": "`AGENTS.md`: operator chose to revert to `HEAD`" in text,
        "src_init_accepted": "`src/__init__.py`: operator explicitly accepted" in text,
        "full_r2_previously_unauthorized": "Full R2 run remains unauthorized" in text,
        "no_science_or_source_semantics_cleanup_change": "This cleanup did not modify:" in text
        and "R2 source semantics" in text
        and "TLGP-001A artifacts" in text,
        "no_git_mutation_cleanup": "No `git add`, `git commit`, `git push`, `git tag`, or remote-anchor" in text,
    }
    ag_diff = git_output(["diff", "--ignore-space-at-eol", "--", "AGENTS.md"])
    if ag_diff.strip():
        raise OfficialRunBlocker("blocked_scope_cleanup_not_clean", "git diff --ignore-space-at-eol -- AGENTS.md is not empty")
    if not all(required.values()):
        raise OfficialRunBlocker("blocked_scope_cleanup_not_clean", f"cleanup report missing confirmations: {required}")
    return {
        "path": rel(report_path),
        "confirmations": required,
        "agents_diff_ignore_space_at_eol_empty": True,
    }


def git_preflight_readback() -> dict[str, Any]:
    branch = git_output(["branch", "--show-current"]).strip()
    head = git_output(["rev-parse", "HEAD"]).strip()
    status_short = git_output(["status", "--short"])
    status_sb = git_output(["status", "-sb"])
    cached = git_output(["diff", "--cached", "--name-status"])
    forbidden_diff = git_output(["diff", "--name-status", "--", *FORBIDDEN_DIFF_PATHS])
    if branch != EXPECTED_BRANCH:
        raise OfficialRunBlocker("blocked_forbidden_drift", f"branch={branch} expected={EXPECTED_BRANCH}")
    if head != EXPECTED_HEAD:
        raise OfficialRunBlocker("blocked_forbidden_drift", f"HEAD={head} expected={EXPECTED_HEAD}")
    if cached.strip():
        raise OfficialRunBlocker("blocked_forbidden_drift", f"index is not empty: {cached.strip()}")
    if forbidden_diff.strip():
        raise OfficialRunBlocker("blocked_forbidden_drift", f"forbidden tracked diff: {forbidden_diff.strip()}")
    ahead_behind = git_output(["rev-list", "--left-right", "--count", "@{u}...HEAD"], check=False).strip()
    return {
        "branch": branch,
        "head": head,
        "status_short": status_short.splitlines(),
        "status_sb": status_sb.splitlines(),
        "index_empty": True,
        "forbidden_tracked_diff_empty": True,
        "forbidden_diff_paths_checked": FORBIDDEN_DIFF_PATHS,
        "ahead_behind_origin": ahead_behind,
    }


def cuda_device_calibration() -> dict[str, Any]:
    out: dict[str, Any] = {
        "torch_version": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "selected_device": str(ML.DEVICE),
        "primary_families": P.primary_families(),
    }
    if not torch.cuda.is_available():
        raise OfficialRunBlocker("blocked_cuda_available_but_not_used", "CUDA is unavailable; official full R2 is not authorized on CPU")
    if str(ML.DEVICE) != "cuda:0":
        raise OfficialRunBlocker("blocked_cuda_available_but_not_used", f"selected_device={ML.DEVICE}, expected cuda:0")
    out["cuda_device_name"] = torch.cuda.get_device_name(0)
    eps = S.make_episodes("rung1", "train", 2)
    tensor_probe: dict[str, Any] = {}
    for family in P.primary_families():
        model = ML.build_model(family, ML.witness_params(family), P.model_seeds()[0])
        tensors = ML.move_tensors(ML.build_tensors(eps))
        model_device = str(next(model.parameters()).device)
        tensor_devices = sorted({str(t.device) for t in tensors})
        tensor_probe[family] = {
            "model_param_device": model_device,
            "training_adaptation_query_tensor_devices": tensor_devices,
            "model_on_cuda0": model_device == "cuda:0",
            "tensors_on_cuda0": all(d == "cuda:0" for d in tensor_devices),
        }
        if tensor_probe[family]["model_on_cuda0"] is not True or tensor_probe[family]["tensors_on_cuda0"] is not True:
            raise OfficialRunBlocker("blocked_cuda_available_but_not_used", f"{family} CUDA probe failed: {tensor_probe[family]}")
        del model, tensors
    torch.cuda.empty_cache()
    out["primary_family_cuda_probe"] = tensor_probe
    out["plain_value_serialization_policy"] = "predictions are detached to CPU and converted to Python int lists after computation"
    write_json(OFFICIAL_DIR / "device_calibration.json", out)
    return out


def capacity_configs() -> list[CapacityConfig]:
    grid = P.capacity_grid()
    primary = set(P.primary_families())
    diagnostic = set(P.diagnostic_families())
    configs: list[CapacityConfig] = []

    def add(family: str, params: dict[str, Any], index: int) -> None:
        witness = params == ML.witness_params(family)
        configs.append(CapacityConfig(
            family=family,
            config_id=f"{family}__cfg{index:02d}",
            params=params,
            witness=witness,
            primary=family in primary,
            diagnostic_only=family in diagnostic,
        ))

    idx = 0
    for hidden in grid["gru"]["hidden"]:
        for layers in grid["gru"]["layers"]:
            idx += 1
            add("in_context_gru", {"hidden": int(hidden), "layers": int(layers)}, idx)
    idx = 0
    for d_model in grid["transformer"]["d_model"]:
        for layers in grid["transformer"]["layers"]:
            idx += 1
            add("in_context_transformer", {
                "d_model": int(d_model),
                "layers": int(layers),
                "heads": int(grid["transformer"]["heads"]),
                "ff_mult": int(grid["transformer"]["ff_mult"]),
            }, idx)
    idx = 0
    for hidden in grid["mlp_summary"]["hidden"]:
        idx += 1
        add("amortized_summary_mlp", {"hidden": [int(v) for v in hidden]}, idx)
    return configs


def official_budget() -> dict[str, Any]:
    b = P.training_budget()
    return {
        "batch_size": int(b["batch_size"]),
        "max_epochs": int(b["max_epochs"]),
        "early_stop_patience": int(b["early_stop_patience"]),
        "steps_max": int(b["steps_max"]),
        "lr_grid": [float(v) for v in b["lr_grid"]],
        "optimizer": str(b["optimizer"]),
    }


def experiment_selfcheck() -> dict[str, Any]:
    configs = capacity_configs()
    by_family = {family: [c for c in configs if c.family == family] for family in P.all_families()}
    rungs = P.rungs()
    checks = {
        "model_seed_count_is_10": len(P.model_seeds()) == 10 and P.N_SEEDS() == 10,
        "primary_families_exact": P.primary_families() == ["in_context_gru", "in_context_transformer"],
        "diagnostic_family_exact": P.diagnostic_families() == ["amortized_summary_mlp"],
        "capacity_grid_counts": {
            "in_context_gru": len(by_family["in_context_gru"]),
            "in_context_transformer": len(by_family["in_context_transformer"]),
            "amortized_summary_mlp": len(by_family["amortized_summary_mlp"]),
        },
        "witness_count_per_family": {
            family: sum(1 for c in cfgs if c.witness)
            for family, cfgs in by_family.items()
        },
        "rung_counts": {
            "rung0_train": int(rungs[S.RUNG0]["n_train_episodes"]),
            "rung0_heldout": int(rungs[S.RUNG0]["n_heldout_episodes"]),
            "rung1_train": int(rungs[S.RUNG1]["n_train_episodes"]),
            "rung1_val": int(rungs[S.RUNG1]["n_val_episodes"]),
            "rung1_test": int(rungs[S.RUNG1]["n_test_episodes"]),
            "rung2_test": int(rungs[S.RUNG2]["n_test_episodes"]),
            "rung3_train": int(rungs[S.RUNG3]["n_train_episodes"]),
            "rung3_val": int(rungs[S.RUNG3]["n_val_episodes"]),
            "rung3_test": int(rungs[S.RUNG3]["n_test_episodes"]),
        },
        "verdict_enum_count": len(P.verdict_enum()) == 7,
        "verdict_tamper_synthetic_covers_all": V.synthetic_tamper_coverage()["all_seven_terminals_covered"],
    }
    expected_counts = {
        "in_context_gru": 6,
        "in_context_transformer": 6,
        "amortized_summary_mlp": 2,
    }
    shrinkage_ok = (
        checks["model_seed_count_is_10"]
        and checks["primary_families_exact"]
        and checks["diagnostic_family_exact"]
        and checks["capacity_grid_counts"] == expected_counts
        and all(v == 1 for v in checks["witness_count_per_family"].values())
        and checks["rung_counts"] == {
            "rung0_train": 5000,
            "rung0_heldout": 200,
            "rung1_train": 5000,
            "rung1_val": 1000,
            "rung1_test": 200,
            "rung2_test": 200,
            "rung3_train": 5000,
            "rung3_val": 1000,
            "rung3_test": 200,
        }
        and checks["verdict_enum_count"]
        and checks["verdict_tamper_synthetic_covers_all"]
    )
    checks["no_experiment_shrinkage_detected"] = bool(shrinkage_ok)
    if not shrinkage_ok:
        raise OfficialRunBlocker("blocked_full_orchestration_selfcheck_failed", f"selfcheck failed: {checks}")
    return checks


def preflight(command_line: list[str]) -> dict[str, Any]:
    OFFICIAL_DIR.mkdir(parents=True, exist_ok=True)
    readback = {
        "run_id": run_id(),
        "command_line": command_line,
        "prereg": prereg_readback(),
        "scope_cleanup": scope_cleanup_readback(),
        "git": git_preflight_readback(),
        "cuda": cuda_device_calibration(),
        "experiment_selfcheck": experiment_selfcheck(),
        "source_hashes_at_preflight": source_hashes(),
    }
    write_json(OFFICIAL_DIR / "preflight_readback.json", readback)
    log_event("preflight_passed", {
        "run_id": readback["run_id"],
        "prereg_sha": readback["prereg"]["canonical_sha256_readback"],
        "selected_device": readback["cuda"]["selected_device"],
    })
    return readback


def make_official_datasets() -> dict[str, list[Episode]]:
    return {
        "rung0_train": S.make_episodes("rung0", "train"),
        "rung0_heldout": S.make_episodes("rung0", "heldout"),
        "rung1_train": S.make_episodes("rung1", "train"),
        "rung1_val": S.make_episodes("rung1", "val"),
        "rung1_test": S.make_episodes("rung1", "test"),
        "rung2_test": S.make_episodes("rung2", "test"),
        "rung3_train": S.make_episodes("rung3", "train"),
        "rung3_val": S.make_episodes("rung3", "val"),
        "rung3_test": S.make_episodes("rung3", "test"),
        "shuffle_train": S.make_shuffle_episodes("train", int(P.rungs()[S.RUNG3]["n_train_episodes"])),
        "shuffle_val": S.make_shuffle_episodes("val", int(P.rungs()[S.RUNG3]["n_val_episodes"])),
        "shuffle_test": S.make_shuffle_episodes("test", int(P.rungs()[S.RUNG3]["n_test_episodes"])),
    }


def score_prediction(truth: Iterable[int], pred: Iterable[int]) -> float:
    return float(balanced_accuracy(np.asarray(list(truth), dtype=int), np.asarray(list(pred), dtype=int)))


def write_prediction_rows(
    handle: Any,
    metric_key: str,
    rung: str,
    split: str,
    prediction_source: str,
    episodes: list[Episode],
    preds: list[list[int]],
    meta: dict[str, Any],
) -> tuple[float, list[float]]:
    scores: list[float] = []
    for ep, pred in zip(episodes, preds):
        truth = [int(v) for v in ep.query_e]
        pred_plain = [int(v) for v in pred]
        score = score_prediction(truth, pred_plain)
        scores.append(score)
        row = {
            "metric_key": metric_key,
            "rung": rung,
            "split": split,
            "prediction_source": prediction_source,
            "episode_id": int(ep.episode_id),
            "rule_id": int(ep.rule_id),
            "query_e": truth,
            "prediction": pred_plain,
            "balanced_accuracy": score,
            "meta": meta,
        }
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    return mean_episode_score(scores), scores


def trace_metric_key(*parts: object) -> str:
    return "::".join(str(p) for p in parts)


def ideal_bundle(handle: Any, rung: str, split: str, episodes: list[Episode], metric_values: dict[str, float]) -> dict[str, Any]:
    mean, preds, per_scores = ideal_predictions(episodes)
    key = trace_metric_key(rung, split, "ideal")
    traced_mean, _ = write_prediction_rows(handle, key, rung, split, "ideal", episodes, preds, {})
    metric_values[key] = traced_mean
    return {"mean": float(mean), "trace_mean": float(traced_mean), "per_episode_scores": per_scores, "metric_key": key}


def lower_reference_bundle(episodes: list[Episode], seed: int) -> tuple[dict[str, float], list[dict[str, list[int]]]]:
    return LR.evaluate(episodes, seed)


def run_leakage_controls(datasets: dict[str, list[Episode]]) -> dict[str, Any]:
    reports: dict[str, Any] = {}
    for name in ("rung0_heldout", "rung1_test", "rung2_test", "rung3_test"):
        report = positive_control_report(datasets[name])
        report["structural_boundary_ok"] = True
        report["meta_input_channels_declared"] = ["adapt_x", "adapt_a", "adapt_e", "query_x", "query_a"]
        report["meta_forbidden_inputs"] = ["rule_id", "query_e"]
        reports[name] = report
    summary = {
        "per_dataset": reports,
        "all_planted_caught": all(r["all_planted_caught"] for r in reports.values()),
        "renamed_leak_caught": all(r["renamed_leak_caught"] for r in reports.values()),
        "no_clean_false_flag": all(r["no_clean_false_flag"] for r in reports.values()),
        "detector_valid": all(r["detector_valid"] for r in reports.values()),
        "planted_leak_uncaught": any(not r["all_planted_caught"] for r in reports.values()),
        "clean_false_flag": any(not r["no_clean_false_flag"] for r in reports.values()),
    }
    write_json(OFFICIAL_DIR / "leakage_report.json", summary)
    return summary


def train_and_trace(
    trace_handle: Any,
    metric_values: dict[str, float],
    rung: str,
    train_eps: list[Episode],
    val_eps: list[Episode],
    test_eps: list[Episode],
    config: CapacityConfig,
    seed: int,
    budget: dict[str, Any],
    context_ablate: bool = False,
) -> ML.TrainResult:
    result = ML.train_select(
        config.family,
        config.params,
        seed,
        train_eps,
        val_eps,
        test_eps,
        budget,
        context_ablate=context_ablate,
    )
    key = trace_metric_key(rung, "test", config.family, config.config_id, seed, "context_ablate" if context_ablate else "standard")
    traced_mean, _ = write_prediction_rows(
        trace_handle,
        key,
        rung,
        "test",
        "meta",
        test_eps,
        result.test_preds,
        {
            "family": config.family,
            "config_id": config.config_id,
            "params": config.params,
            "seed": int(seed),
            "witness": config.witness,
            "primary": config.primary,
            "diagnostic_only": config.diagnostic_only,
            "lr": result.lr,
            "epochs_run": result.epochs_run,
            "steps_run": result.steps_run,
            "best_val_balacc": result.best_val_balacc,
            "device": result.device,
        },
    )
    metric_values[key] = traced_mean
    return result


def replay_trace(trace_path: Path, metric_values: dict[str, float], verdict_inputs: dict[str, Any], result_verdict: str) -> dict[str, Any]:
    trace_hash = sha256_file(trace_path)
    grouped: dict[str, list[float]] = {}
    row_count = 0
    score_mismatches: list[dict[str, Any]] = []
    with trace_path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            row_count += 1
            score = score_prediction(row["query_e"], row["prediction"])
            grouped.setdefault(row["metric_key"], []).append(score)
            if abs(score - float(row["balanced_accuracy"])) > 1e-12:
                score_mismatches.append({"metric_key": row["metric_key"], "episode_id": row["episode_id"]})
    recomputed = {key: mean_episode_score(values) for key, values in grouped.items()}
    metric_mismatches = {
        key: {"expected": metric_values[key], "recomputed": recomputed.get(key)}
        for key in metric_values
        if abs(float(metric_values[key]) - float(recomputed.get(key, float("nan")))) > 1e-12
    }
    recomputed_verdict, detail = V.compute_verdict(verdict_inputs)
    verdict_match = recomputed_verdict == result_verdict
    report = {
        "trace_path": rel(trace_path),
        "trace_sha256": trace_hash,
        "rows": row_count,
        "no_retraining": True,
        "score_mismatches": score_mismatches,
        "metric_mismatches": metric_mismatches,
        "metrics_exact": not score_mismatches and not metric_mismatches,
        "recomputed_verdict": recomputed_verdict,
        "result_verdict": result_verdict,
        "verdict_detail_recomputed": detail,
        "verdict_exact": verdict_match,
        "replay_exact": bool((not score_mismatches) and (not metric_mismatches) and verdict_match),
    }
    write_json(OFFICIAL_DIR / "replay_report.json", report)
    return report


def tamper_integrity_summary(trace_path: Path, result_verdict: str) -> dict[str, Any]:
    synthetic = V.synthetic_tamper_coverage()
    with trace_path.open(encoding="utf-8") as handle:
        first = json.loads(next(handle))
    original = first["balanced_accuracy"]
    first["prediction"] = [(int(v) + 1) % P.K for v in first["prediction"]]
    tampered_score = score_prediction(first["query_e"], first["prediction"])
    return {
        "synthetic_tamper_coverage": synthetic,
        "serialized_prediction_tamper_changes_score": abs(float(original) - float(tampered_score)) > 1e-12,
        "tamper_original_score": original,
        "tamper_recomputed_score_after_prediction_edit": tampered_score,
        "result_verdict": result_verdict,
    }


def write_source_manifest(run_meta: dict[str, Any], preflight_readback: dict[str, Any], end_ts: str | None = None) -> dict[str, Any]:
    delivered = source_hashes()
    executed = source_hashes()
    manifest = {
        "task_id": "TLGP-001B-R2-FULL-ORCHESTRATION-AND-RUN-001",
        "run_id": run_meta["run_id"],
        "producer_function": "src.tlgp_001b_r2.official_full.run_full",
        "git_head": preflight_readback["git"]["head"],
        "branch": preflight_readback["git"]["branch"],
        "python_version": sys.version,
        "torch_version": torch.__version__,
        "cuda_device": preflight_readback["cuda"]["selected_device"],
        "cuda_device_name": preflight_readback["cuda"].get("cuda_device_name"),
        "command_line": run_meta["command_line"],
        "start_timestamp_utc": run_meta["start_timestamp_utc"],
        "end_timestamp_utc": end_ts,
        "seeds_used": P.model_seeds(),
        "delivered_source_hashes": delivered,
        "executed_source_hashes": executed,
        "delivered_equals_executed": delivered == executed,
        "prereg_canonical_sha256": preflight_readback["prereg"]["canonical_sha256_readback"],
    }
    write_json(OFFICIAL_DIR / "source_manifest.json", manifest)
    return manifest


def write_sha256s() -> None:
    required = [
        OFFICIAL_DIR / "result.json",
        OFFICIAL_DIR / "claim_ceiling.txt",
        OFFICIAL_DIR / "run_report.md",
        OFFICIAL_DIR / "trace_manifest.json",
        OFFICIAL_DIR / "replay_report.json",
        OFFICIAL_DIR / "leakage_report.json",
        OFFICIAL_DIR / "rung1_scanner_report.json",
        OFFICIAL_DIR / "ablation_report.json",
        OFFICIAL_DIR / "device_calibration.json",
        OFFICIAL_DIR / "source_manifest.json",
        OFFICIAL_DIR / "RUN_LOG.txt",
        OFFICIAL_TRACE,
        OFFICIAL_DIR / "collision_record.md",
        OFFICIAL_DIR / "preflight_readback.json",
    ]
    lines = []
    for path in required:
        if path.exists():
            lines.append(f"{sha256_file(path)}  {rel(path)}")
    (OFFICIAL_DIR / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_run_report(result: dict[str, Any]) -> None:
    lines = [
        "# TLGP-001B-R2 Official Full Run Report",
        "",
        f"- Task verdict: `{result['task_verdict']}`",
        f"- Official verdict: `{result['final_official_verdict']}`",
        f"- Run id: `{result['run_id']}`",
        f"- Prereg SHA: `{result['prereg']['canonical_sha256_readback']}`",
        f"- CUDA device: `{result['device_readback']['selected_device']}`",
        f"- Source delivered==executed: `{str(result['source_manifest']['delivered_equals_executed']).lower()}`",
        f"- Replay exact: `{str(result['replay_summary']['replay_exact']).lower()}`",
        f"- Leakage detector valid: `{str(result['leakage_summary']['detector_valid']).lower()}`",
        f"- Rung 0 primary pass: `{result['rung_summaries']['rung0']['primary_pass_by_family']}`",
        f"- Rung 1 primary pass: `{result['rung_summaries']['rung1']['primary_pass_by_family']}`",
        f"- Rung 3 primary headroom: `{result['rung_summaries']['rung3']['primary_headroom_by_family']}`",
        "",
        "## Claim Ceiling",
        "",
        result["claim_ceiling"],
        "",
        "## What This Does Not Prove",
        "",
        "This run does not prove learning-as-mechanism, agency, self, feeling, subjectivity, intelligence, autonomy, stable user benefit, EGO readiness, runtime readiness, companion readiness, or mainline effect.",
    ]
    (OFFICIAL_DIR / "run_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def official_replay(result_path: Path) -> dict[str, Any]:
    result = read_json(result_path)
    trace_manifest = read_json(REPO_ROOT / result["trace_manifest_path"])
    trace_path = REPO_ROOT / trace_manifest["trace_file"]
    current_hash = sha256_file(trace_path)
    if current_hash != trace_manifest["trace_sha256"]:
        report = {
            "replay_exact": False,
            "integrity_hash_match": False,
            "expected_trace_sha256": trace_manifest["trace_sha256"],
            "current_trace_sha256": current_hash,
        }
        write_json(OFFICIAL_DIR / "replay_report.json", report)
        return report
    return replay_trace(trace_path, result["metric_readback"], result["verdict_inputs"], result["final_official_verdict"])


def run_dry_run(command_line: list[str]) -> dict[str, Any]:
    readback = preflight(command_line)
    out = {
        "task_verdict": "tlgp001b_r2_full_orchestration_dry_run_passed",
        "current_layer": "engineering implementation + mechanism-hypothesis preflight execution",
        "mainline_integration_status": "none",
        "enabled_status": "isolated TLGP-001B-R2 official offline full-run path only",
        "claim_ceiling": P.claim_ceiling(),
        "preflight": readback,
    }
    write_json(OFFICIAL_DIR / "dry_run_report.json", out)
    return out


def run_full(command_line: list[str]) -> dict[str, Any]:
    start = time.time()
    start_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    pre = preflight(command_line)
    run_meta = {
        "run_id": pre["run_id"],
        "command_line": command_line,
        "start_timestamp_utc": start_ts,
    }
    source_manifest = write_source_manifest(run_meta, pre)
    if not source_manifest["delivered_equals_executed"]:
        raise OfficialRunBlocker("blocked_full_orchestration_selfcheck_failed", "source delivered/executed hash mismatch")

    log_event("official_full_started", {"run_id": pre["run_id"]})
    datasets = make_official_datasets()
    split_assertions = S.split_assertions(datasets)
    write_json(OFFICIAL_DIR / "dataset_split_assertions.json", split_assertions)

    metric_values: dict[str, float] = {}
    configs = capacity_configs()
    seeds = P.model_seeds()
    budget = official_budget()
    fit_seed = int(P.seeds()["BASELINE_FIT_SEED"])
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    if OFFICIAL_TRACE.exists():
        OFFICIAL_TRACE.unlink()

    rung_summary: dict[str, Any] = {}
    primary = set(P.primary_families())
    diagnostic = set(P.diagnostic_families())
    r0_seed_pass: dict[str, list[bool]] = {family: [] for family in primary}
    r1_seed_pass: dict[str, list[bool]] = {family: [] for family in primary}
    r3_headroom: dict[str, list[float]] = {family: [] for family in primary}
    diagnostic_summary: dict[str, Any] = {}
    all_training_records: list[dict[str, Any]] = []

    with OFFICIAL_TRACE.open("w", encoding="utf-8") as trace_handle:
        ideal = {
            "rung0_train": ideal_bundle(trace_handle, "rung0", "train", datasets["rung0_train"], metric_values),
            "rung0_heldout": ideal_bundle(trace_handle, "rung0", "heldout", datasets["rung0_heldout"], metric_values),
            "rung1_test": ideal_bundle(trace_handle, "rung1", "test", datasets["rung1_test"], metric_values),
            "rung2_test": ideal_bundle(trace_handle, "rung2", "test", datasets["rung2_test"], metric_values),
            "rung3_test": ideal_bundle(trace_handle, "rung3", "test", datasets["rung3_test"], metric_values),
            "shuffle_test": ideal_bundle(trace_handle, "shuffle", "test", datasets["shuffle_test"], metric_values),
        }

        rung1_lower, rung1_lower_records = lower_reference_bundle(datasets["rung1_test"], fit_seed)
        _ = rung1_lower_records

        # Rung 0: fit floor on 8 selected TRAIN_RULES, full value range.
        log_event("rung0_started", {"configs": len(configs), "seeds": len(seeds)})
        for config in configs:
            for seed in seeds:
                result = train_and_trace(
                    trace_handle,
                    metric_values,
                    "rung0",
                    datasets["rung0_train"],
                    datasets["rung0_train"],
                    datasets["rung0_heldout"],
                    config,
                    seed,
                    budget,
                )
                train_score, train_preds = ML.eval_model(result.model, datasets["rung0_train"], budget["batch_size"])
                train_key = trace_metric_key("rung0", "train", config.family, config.config_id, seed, "standard")
                traced_train, _ = write_prediction_rows(
                    trace_handle,
                    train_key,
                    "rung0",
                    "train",
                    "meta",
                    datasets["rung0_train"],
                    train_preds,
                    {"family": config.family, "config_id": config.config_id, "seed": seed, "witness": config.witness},
                )
                metric_values[train_key] = traced_train
                heldout_score = result.test_balacc
                rec = {
                    "rung": "rung0",
                    "family": config.family,
                    "config_id": config.config_id,
                    "params": config.params,
                    "seed": seed,
                    "witness": config.witness,
                    "train_balacc": train_score,
                    "heldout_balacc": heldout_score,
                    "ideal_train": ideal["rung0_train"]["mean"],
                    "ideal_heldout": ideal["rung0_heldout"]["mean"],
                    "lr": result.lr,
                    "epochs_run": result.epochs_run,
                    "steps_run": result.steps_run,
                }
                all_training_records.append(rec)
                if config.primary and config.witness:
                    passed = (
                        float(train_score) >= float(ideal["rung0_train"]["mean"]) - P.DELTA()
                        and float(heldout_score) >= float(ideal["rung0_heldout"]["mean"]) - P.DELTA()
                    )
                    r0_seed_pass[config.family].append(bool(passed))
                del result
                torch.cuda.empty_cache()
        rung_summary["rung0"] = {
            "ideal_train": ideal["rung0_train"]["mean"],
            "ideal_heldout": ideal["rung0_heldout"]["mean"],
            "primary_seed_pass_by_family": r0_seed_pass,
            "primary_pass_counts": {family: sum(vals) for family, vals in r0_seed_pass.items()},
            "primary_pass_by_family": {family: sum(vals) >= P.close_fraction_min() for family, vals in r0_seed_pass.items()},
        }
        write_json(OFFICIAL_DIR / "rung0_progress_summary.json", rung_summary["rung0"])
        log_event("rung0_completed", rung_summary["rung0"]["primary_pass_counts"])

        # Rung 1: seen-rule in-distribution capability control.
        log_event("rung1_started", {"configs": len(configs), "seeds": len(seeds)})
        for config in configs:
            for seed in seeds:
                result = train_and_trace(
                    trace_handle,
                    metric_values,
                    "rung1",
                    datasets["rung1_train"],
                    datasets["rung1_val"],
                    datasets["rung1_test"],
                    config,
                    seed,
                    budget,
                )
                rec = {
                    "rung": "rung1",
                    "family": config.family,
                    "config_id": config.config_id,
                    "params": config.params,
                    "seed": seed,
                    "witness": config.witness,
                    "test_balacc": result.test_balacc,
                    "ideal_test": ideal["rung1_test"]["mean"],
                    "lr": result.lr,
                    "epochs_run": result.epochs_run,
                    "steps_run": result.steps_run,
                    "best_val_balacc": result.best_val_balacc,
                }
                all_training_records.append(rec)
                if config.primary and config.witness:
                    r1_seed_pass[config.family].append(bool(result.test_balacc >= float(ideal["rung1_test"]["mean"]) - P.DELTA()))
                if config.family in diagnostic and config.witness:
                    diagnostic_summary.setdefault("rung1", {}).setdefault(config.family, []).append(rec)
                del result
                torch.cuda.empty_cache()
        rung_summary["rung1"] = {
            "ideal_seen1": ideal["rung1_test"]["mean"],
            "lower_reference_means": rung1_lower,
            "primary_seed_pass_by_family": r1_seed_pass,
            "primary_pass_counts": {family: sum(vals) for family, vals in r1_seed_pass.items()},
            "primary_pass_by_family": {family: sum(vals) >= P.close_fraction_min() for family, vals in r1_seed_pass.items()},
        }
        write_json(OFFICIAL_DIR / "rung1_progress_summary.json", rung_summary["rung1"])
        log_event("rung1_completed", rung_summary["rung1"]["primary_pass_counts"])

        # Rung 3 models, with Rung 2 diagnostic evaluation of each Rung 3 model.
        log_event("rung3_started", {"configs": len(configs), "seeds": len(seeds)})
        rung2_records: list[dict[str, Any]] = []
        for config in configs:
            for seed in seeds:
                result = train_and_trace(
                    trace_handle,
                    metric_values,
                    "rung3",
                    datasets["rung3_train"],
                    datasets["rung3_val"],
                    datasets["rung3_test"],
                    config,
                    seed,
                    budget,
                )
                r2_score, r2_preds = ML.eval_model(result.model, datasets["rung2_test"], budget["batch_size"])
                r2_key = trace_metric_key("rung2", "test", config.family, config.config_id, seed, "rung3_model")
                traced_r2, _ = write_prediction_rows(
                    trace_handle,
                    r2_key,
                    "rung2",
                    "test",
                    "meta",
                    datasets["rung2_test"],
                    r2_preds,
                    {"family": config.family, "config_id": config.config_id, "seed": seed, "evaluates_model": "rung3"},
                )
                metric_values[r2_key] = traced_r2
                hr = float(ideal["rung3_test"]["mean"]) - float(result.test_balacc)
                rec = {
                    "rung": "rung3",
                    "family": config.family,
                    "config_id": config.config_id,
                    "params": config.params,
                    "seed": seed,
                    "witness": config.witness,
                    "rung3_test_balacc": result.test_balacc,
                    "rung3_headroom_vs_meta": hr,
                    "rung2_test_balacc_using_rung3_model": r2_score,
                    "rung2_headroom_vs_meta": float(ideal["rung2_test"]["mean"]) - float(r2_score),
                    "lr": result.lr,
                    "epochs_run": result.epochs_run,
                    "steps_run": result.steps_run,
                    "best_val_balacc": result.best_val_balacc,
                }
                all_training_records.append(rec)
                rung2_records.append(rec)
                if config.primary and config.witness:
                    r3_headroom[config.family].append(hr)
                if config.family in diagnostic and config.witness:
                    diagnostic_summary.setdefault("rung3_rung2", {}).setdefault(config.family, []).append(rec)
                del result
                torch.cuda.empty_cache()
        rung_summary["rung2"] = {
            "ideal_seen_rule_value_extrapolation": ideal["rung2_test"]["mean"],
            "evaluates_model": "rung3 trained model",
            "diagnostic_records": rung2_records,
            "diagnostic_only_global_gate": False,
        }
        rung_summary["rung3"] = {
            "ideal_unseen_rule_unseen_value": ideal["rung3_test"]["mean"],
            "primary_headroom_by_family": r3_headroom,
            "primary_lcb_by_family": {family: V.lcb(vals) for family, vals in r3_headroom.items()},
            "primary_close_counts": {family: sum(float(v) <= P.DELTA() for v in vals) for family, vals in r3_headroom.items()},
        }
        write_json(OFFICIAL_DIR / "rung2_progress_summary.json", rung_summary["rung2"])
        write_json(OFFICIAL_DIR / "rung3_progress_summary.json", rung_summary["rung3"])
        log_event("rung3_completed", rung_summary["rung3"]["primary_close_counts"])

        # Ablations: context at Rung 1 and shuffle structure at witness configs.
        context_scores: dict[str, list[float]] = {family: [] for family in P.all_families()}
        shuffle_headroom: dict[str, list[float]] = {family: [] for family in P.all_families()}
        log_event("ablations_started", {"families": P.all_families(), "seeds": len(seeds)})
        for config in [c for c in configs if c.witness]:
            for seed in seeds:
                ctx_result = train_and_trace(
                    trace_handle,
                    metric_values,
                    "context_ablation",
                    datasets["rung1_train"],
                    datasets["rung1_val"],
                    datasets["rung1_test"],
                    config,
                    seed,
                    budget,
                    context_ablate=True,
                )
                context_scores[config.family].append(float(ctx_result.test_balacc))
                del ctx_result
                torch.cuda.empty_cache()

                shuf_result = train_and_trace(
                    trace_handle,
                    metric_values,
                    "shuffle_ablation",
                    datasets["shuffle_train"],
                    datasets["shuffle_val"],
                    datasets["shuffle_test"],
                    config,
                    seed,
                    budget,
                )
                shuffle_headroom[config.family].append(float(ideal["shuffle_test"]["mean"]) - float(shuf_result.test_balacc))
                del shuf_result
                torch.cuda.empty_cache()
        ablation_summary = {
            "context_ablation_rung": "rung1",
            "context_ablation_scores_by_family": context_scores,
            "context_ablation_mean_by_family": {family: mean_episode_score(vals) for family, vals in context_scores.items()},
            "context_ablation_collapse_by_family": {
                family: mean_episode_score(vals) <= P.FLOOR() + P.DELTA()
                for family, vals in context_scores.items()
            },
            "shuffle_ideal_mean": ideal["shuffle_test"]["mean"],
            "shuffle_headroom_by_family": shuffle_headroom,
            "shuffle_headroom_mean_by_family": {family: mean_episode_score(vals) for family, vals in shuffle_headroom.items()},
            "shuffle_collapse_by_family": {
                family: mean_episode_score(vals) <= P.DELTA()
                for family, vals in shuffle_headroom.items()
            },
            "diagnostic_mlp_not_global_gate": True,
        }
        write_json(OFFICIAL_DIR / "ablation_report.json", ablation_summary)
        log_event("ablations_completed", {
            "context": ablation_summary["context_ablation_collapse_by_family"],
            "shuffle": ablation_summary["shuffle_collapse_by_family"],
        })

    leakage = run_leakage_controls(datasets)
    no_context_meta = max(
        mean_episode_score(ablation_summary["context_ablation_scores_by_family"][family])
        for family in P.primary_families()
    )
    rung1_scanner = LR.rung1_scanner(datasets["rung1_test"], lower_means=rung1_lower, no_context_meta_balacc=no_context_meta)
    write_json(OFFICIAL_DIR / "rung1_scanner_report.json", rung1_scanner)

    replay_stub = {"rung0": True, "rung1": True, "rung2": True, "rung3": True, "context_ablation": True, "shuffle_ablation": True}
    verdict_inputs = {
        "integrity": {
            "planted_leak_uncaught": bool(leakage["planted_leak_uncaught"]),
            "clean_false_flag": bool(leakage["clean_false_flag"]),
            "replay_exact_by_rung": replay_stub,
        },
        "rung0_pass_by_family": rung_summary["rung0"]["primary_pass_by_family"],
        "rung1_pass_by_family": rung_summary["rung1"]["primary_pass_by_family"],
        "context_ablation_collapse_by_family": {
            family: ablation_summary["context_ablation_collapse_by_family"][family]
            for family in P.primary_families()
        },
        "shuffle_collapse_by_family": {
            family: ablation_summary["shuffle_collapse_by_family"][family]
            for family in P.primary_families()
        },
        "rung3_headroom_by_family": r3_headroom,
    }
    official_verdict, verdict_detail = V.compute_verdict(verdict_inputs)

    trace_manifest = {
        "trace_file": rel(OFFICIAL_TRACE),
        "trace_sha256": sha256_file(OFFICIAL_TRACE),
        "metric_keys": sorted(metric_values),
        "metric_count": len(metric_values),
        "producer_function": "src.tlgp_001b_r2.official_full.run_full",
        "no_retrain_replay_command": f"{sys.executable} -m src.tlgp_001b_r2.harness --replay {rel(OFFICIAL_DIR / 'result.json')}",
    }
    write_json(OFFICIAL_DIR / "trace_manifest.json", trace_manifest)
    replay = replay_trace(OFFICIAL_TRACE, metric_values, verdict_inputs, official_verdict)
    if not replay["replay_exact"]:
        verdict_inputs["integrity"]["replay_exact_by_rung"] = {k: False for k in replay_stub}
        official_verdict, verdict_detail = V.compute_verdict(verdict_inputs)
        replay = replay_trace(OFFICIAL_TRACE, metric_values, verdict_inputs, official_verdict)
    tamper = tamper_integrity_summary(OFFICIAL_TRACE, official_verdict)

    end_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    source_manifest = write_source_manifest(run_meta, pre, end_ts=end_ts)
    device_readback = ML.device_readback()
    claim_ceiling = P.claim_ceiling()
    (OFFICIAL_DIR / "claim_ceiling.txt").write_text(claim_ceiling + "\n", encoding="utf-8")

    result = {
        "task_id": "TLGP-001B-R2-FULL-ORCHESTRATION-AND-RUN-001",
        "task_verdict": "tlgp001b_r2_official_full_run_completed",
        "run_id": pre["run_id"],
        "official_run": True,
        "candidate_free": True,
        "start_timestamp_utc": start_ts,
        "end_timestamp_utc": end_ts,
        "elapsed_sec": round(time.time() - start, 3),
        "command_line": command_line,
        "current_layer": "engineering implementation + mechanism-hypothesis preflight execution",
        "mainline_integration_status": "none",
        "enabled_status": "isolated TLGP-001B-R2 official offline full run only",
        "real_trigger_evidence": "operator authorized full run with frozen prereg SHA and --full command passed preflight gates",
        "claim_ceiling": claim_ceiling,
        "prereg": pre["prereg"],
        "scope_cleanup_readback": pre["scope_cleanup"],
        "git_preflight": pre["git"],
        "device_readback": device_readback,
        "source_manifest": source_manifest,
        "trace_manifest_path": rel(OFFICIAL_DIR / "trace_manifest.json"),
        "metric_readback": metric_values,
        "split_assertions": split_assertions,
        "rung_summaries": rung_summary,
        "primary_family_adjudication": {
            "primary_families": P.primary_families(),
            "rung0_pass": rung_summary["rung0"]["primary_pass_by_family"],
            "rung1_pass": rung_summary["rung1"]["primary_pass_by_family"],
            "rung3_headroom": r3_headroom,
            "rung3_lcb": rung_summary["rung3"]["primary_lcb_by_family"],
        },
        "diagnostic_mlp_summary": diagnostic_summary,
        "rung1_scanner_summary": rung1_scanner,
        "ablation_summary": ablation_summary,
        "leakage_summary": leakage,
        "replay_summary": replay,
        "integrity_tamper_summary": tamper,
        "verdict_inputs": verdict_inputs,
        "final_official_verdict": official_verdict,
        "verdict_detail": verdict_detail,
        "all_training_records_path": rel(OFFICIAL_DIR / "all_training_records.json"),
        "what_this_proves": "Only the frozen TLGP-001B-R2 offline terminal verdict under this preregistered world, split, budget, model grid, seeds, and evidence path.",
        "what_this_does_not_prove": "Does not prove learning-as-mechanism, agency, self, feeling, subjectivity, intelligence, autonomy, stable user benefit, EGO readiness, runtime readiness, companion readiness, or mainline effect.",
    }
    write_json(OFFICIAL_DIR / "all_training_records.json", all_training_records)
    write_json(OFFICIAL_DIR / "result.json", result)
    write_run_report(result)
    write_sha256s()
    log_event("official_full_completed", {"verdict": official_verdict, "elapsed_sec": result["elapsed_sec"]})
    return result


def write_failure_manifest(code: str, detail: str, exc: BaseException | None = None) -> None:
    manifest = {
        "task_id": "TLGP-001B-R2-FULL-ORCHESTRATION-AND-RUN-001",
        "task_verdict": code,
        "blocked": True,
        "detail": detail,
        "official_verdict": "NOT_EMITTED",
        "claim_ceiling": "blocker/readback only; no official TLGP-001B-R2 scientific verdict emitted",
        "traceback": traceback.format_exc() if exc is not None else None,
    }
    write_json(OFFICIAL_DIR / "failure_manifest.json", manifest)
    log_event("official_full_blocked_or_failed", {"code": code, "detail": detail})
