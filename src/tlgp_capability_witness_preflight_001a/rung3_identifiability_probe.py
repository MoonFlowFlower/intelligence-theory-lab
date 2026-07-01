"""Driver for TLGP rung3 identifiability probe 001A.

Candidate-free: no learner import, no GPU, no training.
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

import numpy as np

from src.tlgp_001a.ideal_observer import predict_episode as ideal_predict_episode
from src.tlgp_001a.metrics import balanced_accuracy, mean_episode_score
from src.tlgp_001a import leakage as LK
from src.tlgp_001b_r2 import lower_reference as LR
from src.tlgp_001b_r2 import preregistration as P
from src.tlgp_001b_r2 import splits as S
from src.tlgp_001b_r2.world import make_episode_for_rule
from src.tlgp_capability_witness_preflight_001a import rung3_graph_cache_baselines as GC
from src.tlgp_capability_witness_preflight_001a import rung3_identifiability_adjudicator as ADJ

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "TLGP-CAPABILITY-WITNESS-RUNG3-IDENTIFIABILITY-PROBE-001A"
ARTIFACT_DIR = (
    REPO_ROOT
    / "artifacts"
    / "TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A"
    / "RUNG3_IDENTIFIABILITY_PROBE_001A"
)
FROZEN_DESIGN_PATH = (
    REPO_ROOT
    / "docs"
    / "task_cards"
    / "TLGP-CAPABILITY-WITNESS-RUNG3-IDENTIFIABILITY-PROBE-001A.frozen_design.json"
)
EXPECTED_FROZEN_DESIGN_SHA256 = "c2a32ed8612d53186dff54245d9c8c8a86abcdc2f020e78dcd2f6910c2b0d706"
EXPECTED_PREREG_SHA256 = ADJ.FROZEN_PREREG_SHA256

TRACE_PATH = ARTIFACT_DIR / "trace.jsonl"
RESULT_PATH = ARTIFACT_DIR / "result.json"
BASELINE_PATH = ARTIFACT_DIR / "baseline_comparison.json"
ABLATION_PATH = ARTIFACT_DIR / "ablation_report.json"
CONTROL_PATH = ARTIFACT_DIR / "control_report.json"
LEAKAGE_PATH = ARTIFACT_DIR / "leakage_report.json"
REPLAY_PATH = ARTIFACT_DIR / "replay_report.json"
ROUTE_INPUT_PATH = ARTIFACT_DIR / "route_decision_input.json"
ROUTE_DECISION_PATH = ARTIFACT_DIR / "route_decision.json"
MANIFEST_PATH = ARTIFACT_DIR / "manifest.json"
FAILURE_PATH = ARTIFACT_DIR / "failure_manifest.json"
COLLISION_PATH = ARTIFACT_DIR / "collision_record.json"

KNOWN_OUTPUTS = [
    RESULT_PATH,
    TRACE_PATH,
    BASELINE_PATH,
    ABLATION_PATH,
    CONTROL_PATH,
    LEAKAGE_PATH,
    REPLAY_PATH,
    ROUTE_INPUT_PATH,
    ROUTE_DECISION_PATH,
    MANIFEST_PATH,
    FAILURE_PATH,
    COLLISION_PATH,
]

PROTECTED_SOURCE_PATHS = [
    "src/tlgp_001a",
    "src/tlgp_001b_r2",
    "src/tlgp_capability_witness_preflight_001a/retrieval_model.py",
    "src/tlgp_capability_witness_preflight_001a/route_decision.py",
    "src/tlgp_capability_witness_preflight_001a/grokking_probe.py",
    "src/tlgp_capability_witness_preflight_001a/minimal_probe.py",
    "src/tlgp_capability_witness_preflight_001a/rung0_retrieval_powered.py",
    "src/tlgp_capability_witness_preflight_001a/rung0_retrieval_rerun.py",
]

READ_ONLY_SOURCE_FILES = [
    "src/tlgp_001a/ideal_observer.py",
    "src/tlgp_001a/leakage.py",
    "src/tlgp_001a/metrics.py",
    "src/tlgp_001a/world.py",
    "src/tlgp_001b_r2/lower_reference.py",
    "src/tlgp_001b_r2/preregistration.py",
    "src/tlgp_001b_r2/splits.py",
    "src/tlgp_001b_r2/world.py",
]

NEW_SOURCE_FILES = [
    "src/tlgp_capability_witness_preflight_001a/rung3_graph_cache_baselines.py",
    "src/tlgp_capability_witness_preflight_001a/rung3_identifiability_adjudicator.py",
    "src/tlgp_capability_witness_preflight_001a/rung3_identifiability_probe.py",
]

FAIR_PANEL = [*LR.LOWER_REFERENCE, GC.GRAPH_CACHE_NAME]


class StopProbe(RuntimeError):
    def __init__(self, step: str, reason: str, observed: Any = None, expected: Any = None):
        super().__init__(reason)
        self.step = step
        self.reason = reason
        self.observed = observed
        self.expected = expected


@dataclass(frozen=True)
class GuardedIdealEpisode:
    adapt_x: np.ndarray
    adapt_a: np.ndarray
    adapt_e: np.ndarray
    query_x: np.ndarray
    query_a: np.ndarray

    @property
    def rule_id(self) -> int:
        raise RuntimeError("ideal observer attempted to read forbidden rule_id")

    @property
    def query_e(self) -> np.ndarray:
        raise RuntimeError("ideal observer attempted to read forbidden query_e")


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


def _hash_payload(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def verify_frozen_design(path: Path = FROZEN_DESIGN_PATH) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    computed = _canonical_sha256(_strip_underscore_keys(obj))
    recorded = str(obj["_frozen_canonical_sha256"])
    if computed != recorded or computed != EXPECTED_FROZEN_DESIGN_SHA256:
        raise StopProbe(
            "frozen_design_sha",
            "frozen design canonical sha mismatch",
            {"computed": computed, "recorded": recorded},
            EXPECTED_FROZEN_DESIGN_SHA256,
        )
    return {
        "path": str(path.relative_to(REPO_ROOT).as_posix()),
        "computed_sha256": computed,
        "recorded_sha256": recorded,
        "match": True,
    }


def git_output(args: list[str], check: bool = True) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        raise StopProbe("git_readback", proc.stderr.strip(), args, "git command succeeds")
    return proc.stdout


def protected_source_status() -> list[str]:
    return git_output(["status", "--porcelain=v1", "--", *PROTECTED_SOURCE_PATHS]).splitlines()


def protected_source_diff() -> list[str]:
    return git_output(["diff", "--name-only", "--", *PROTECTED_SOURCE_PATHS]).splitlines()


def clean_known_outputs() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    for path in KNOWN_OUTPUTS:
        if path.exists():
            path.unlink()


def _jsonable_array(arr: np.ndarray) -> list[Any]:
    return np.asarray(arr, dtype=int).tolist()


def _array_payload_hash(*arrays: np.ndarray) -> str:
    return _hash_payload([_jsonable_array(arr) for arr in arrays])


def _rule_pool(spec: S.RungSpec) -> np.ndarray:
    train_idx, test_idx = S.rule_split()
    if spec.rule_pool == "TRAIN_RULES":
        return train_idx
    if spec.rule_pool == "TEST_RULES":
        return test_idx
    if spec.rule_pool == "R0_RULES":
        return S.r0_rule_indices()
    raise ValueError(spec.rule_pool)


def _default_episode_count(spec: S.RungSpec) -> int:
    cfg = P.rungs()[spec.rung]
    key_by_split = {
        "train": "n_train_episodes",
        "val": "n_val_episodes",
        "test": "n_test_episodes",
        "heldout": "n_heldout_episodes",
    }
    return int(cfg[key_by_split[spec.split]])


def make_seeded_episodes(
    rung: str,
    split: str,
    model_seed: int,
    seed_index: int,
    *,
    n_adapt: int | None = None,
    n_episodes: int | None = None,
) -> list[Any]:
    spec = S.rung_spec(rung, split)
    pool = _rule_pool(spec)
    n = _default_episode_count(spec) if n_episodes is None else int(n_episodes)
    rng = np.random.default_rng(int(P.seeds()[spec.seed_key]) + int(model_seed))
    base = int(S.EPISODE_ID_BASE[(spec.rung, spec.split)]) + int(seed_index) * 10_000
    episodes = []
    for i in range(n):
        rule_id = int(pool[int(rng.integers(0, len(pool)))])
        episodes.append(
            make_episode_for_rule(
                base + i,
                rule_id,
                rng,
                spec.adapt_values,
                spec.query_values,
                n_adapt=P.N_ADAPT if n_adapt is None else int(n_adapt),
                n_query=P.N_QUERY,
            )
        )
    return episodes


def split_assertions(episodes: list[Any], rung: str, split: str) -> dict[str, Any]:
    spec = S.rung_spec(rung, split)
    train_idx, test_idx = S.rule_split()
    train_rules = {int(v) for v in train_idx.tolist()}
    test_rules = {int(v) for v in test_idx.tolist()}
    rule_ids = {int(ep.rule_id) for ep in episodes}
    observed_query_values = sorted({int(v) for ep in episodes for row in ep.query_x for v in row})
    observed_adapt_values = sorted({int(v) for ep in episodes for row in ep.adapt_x for v in row})
    return {
        "rung": spec.rung,
        "split": spec.split,
        "rule_pool": spec.rule_pool,
        "episode_count": len(episodes),
        "rule_ids_count": len(rule_ids),
        "train_rules_intersection_query_rules_empty": train_rules.isdisjoint(rule_ids)
        if spec.rule_pool == "TEST_RULES"
        else None,
        "rung3_test_rules_subset_of_test": rule_ids.issubset(test_rules)
        if spec.rung == S.RUNG3 and spec.split == "test"
        else None,
        "rung0_rules_subset_of_train": rule_ids.issubset(train_rules)
        if spec.rule_pool == "R0_RULES"
        else None,
        "configured_adapt_values": [int(v) for v in spec.adapt_values],
        "configured_query_values": [int(v) for v in spec.query_values],
        "observed_adapt_values": observed_adapt_values,
        "observed_query_values": observed_query_values,
        "query_values_unseen_3_4_configured": list(spec.query_values) == [3, 4]
        if spec.rung == S.RUNG3 and spec.split == "test"
        else None,
    }


def guarded_ideal_prediction(ep: Any) -> tuple[np.ndarray, int, bool]:
    guarded = GuardedIdealEpisode(
        adapt_x=ep.adapt_x,
        adapt_a=ep.adapt_a,
        adapt_e=ep.adapt_e,
        query_x=ep.query_x,
        query_a=ep.query_a,
    )
    pred, n_consistent = ideal_predict_episode(guarded)
    return np.asarray(pred, dtype=int), int(n_consistent), True


def evaluate_episode(ep: Any, seed: int, phase: str, split_assertion: dict[str, Any]) -> dict[str, Any]:
    ideal_pred, n_consistent, guard_passed = guarded_ideal_prediction(ep)
    ideal_score = balanced_accuracy(ep.query_e, ideal_pred, n_classes=P.K)
    lower_pred = LR.predict_episode(ep, int(seed))
    graph_pred = GC.predict_episode(ep)
    fair_pred = {**lower_pred, **graph_pred}
    fair_scores = {
        name: balanced_accuracy(ep.query_e, np.array(pred, dtype=int), n_classes=P.K)
        for name, pred in fair_pred.items()
    }
    fair_max_name = max(fair_scores, key=fair_scores.get)
    fair_max = float(fair_scores[fair_max_name])
    headroom = float(ideal_score - fair_max)
    return {
        "task_id": TASK_ID,
        "phase": phase,
        "seed": int(seed),
        "rung": split_assertion["rung"],
        "split": split_assertion["split"],
        "episode_id": int(ep.episode_id),
        "rule_id": int(ep.rule_id),
        "assert_unseen": split_assertion["train_rules_intersection_query_rules_empty"],
        "adapt_x": _jsonable_array(ep.adapt_x),
        "adapt_a": _jsonable_array(ep.adapt_a),
        "adapt_e": _jsonable_array(ep.adapt_e),
        "query_x": _jsonable_array(ep.query_x),
        "query_a": _jsonable_array(ep.query_a),
        "query_e": _jsonable_array(ep.query_e),
        "adapt_tensors_hash": _array_payload_hash(ep.adapt_x, ep.adapt_a, ep.adapt_e),
        "query_tensors_hash": _array_payload_hash(ep.query_x, ep.query_a),
        "ideal_prediction": [int(v) for v in ideal_pred],
        "ideal_consistent_rule_count": n_consistent,
        "ideal_forbidden_input_guard_passed": guard_passed,
        "fair_prediction": fair_pred,
        "ideal_balacc": float(ideal_score),
        "fair_balacc": {name: float(v) for name, v in fair_scores.items()},
        "fair_max_name": fair_max_name,
        "fair_max": fair_max,
        "headroom": headroom,
        "graph_cache_query_hit_fraction": GC.query_hit_fraction(ep),
        "forbidden_agent_inputs": ["rule_id", "query_e"],
        "agent_input_channels": ["adapt_x", "adapt_a", "adapt_e", "query_x", "query_a"],
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a.rung3_identifiability_probe"
            ".evaluate_episode"
        ),
    }


def summarize_trace_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        raise StopProbe("empty_records", "no episode records to summarize")
    by_seed: dict[int, list[dict[str, Any]]] = {}
    for record in records:
        by_seed.setdefault(int(record["seed"]), []).append(record)

    per_seed = []
    for seed in sorted(by_seed):
        rows = by_seed[seed]
        fair_names = sorted(rows[0]["fair_balacc"])
        fair_means = {
            name: mean_episode_score([float(row["fair_balacc"][name]) for row in rows])
            for name in fair_names
        }
        per_seed.append(
            {
                "seed": int(seed),
                "episodes": len(rows),
                "ideal_balacc": mean_episode_score([float(row["ideal_balacc"]) for row in rows]),
                "fair_balacc": fair_means,
                "fair_max_episode_mean": mean_episode_score(
                    [
                        float(row.get("fair_max", max(float(v) for v in row["fair_balacc"].values())))
                        for row in rows
                    ]
                ),
                "headroom": mean_episode_score([float(row["headroom"]) for row in rows]),
            }
        )

    fair_names = sorted(records[0]["fair_balacc"])
    aggregate_fair = {
        name: mean_episode_score([float(row["fair_balacc"][name]) for row in records])
        for name in fair_names
    }
    per_seed_headroom = [float(row["headroom"]) for row in per_seed]
    return {
        "n_seeds": len(per_seed),
        "per_seed": per_seed,
        "per_seed_headroom": per_seed_headroom,
        "ideal_balacc_mean": mean_episode_score([float(row["ideal_balacc"]) for row in per_seed]),
        "fair_max_episode_mean": mean_episode_score([float(row["fair_max_episode_mean"]) for row in per_seed]),
        "fair_baseline_balacc": aggregate_fair,
        "mean_headroom": mean_episode_score(per_seed_headroom),
        "fair_saturation_seed_count": sum(1 for value in per_seed_headroom if float(value) <= P.DELTA()),
        "predict_all_or_majority_match_ideal": any(
            aggregate_fair[name] >= mean_episode_score([float(row["ideal_balacc"]) for row in per_seed]) - P.DELTA()
            for name in ("predict_all", "majority")
            if name in aggregate_fair
        ),
        "no_adaptation_matches_ideal": aggregate_fair.get("no_adaptation", 0.0)
        >= mean_episode_score([float(row["ideal_balacc"]) for row in per_seed]) - P.DELTA(),
        "ideal_degenerate": mean_episode_score([float(row["ideal_balacc"]) for row in per_seed])
        <= P.FLOOR() + P.DELTA(),
    }


def evaluate_panel(
    *,
    phase: str,
    rung: str,
    split: str,
    trace_handle: TextIO,
    n_adapt: int | None = None,
) -> dict[str, Any]:
    seeds = P.model_seeds()
    all_records: list[dict[str, Any]] = []
    all_episodes: list[Any] = []
    assertions_by_seed: dict[str, Any] = {}
    for seed_index, seed in enumerate(seeds):
        episodes = make_seeded_episodes(rung, split, seed, seed_index, n_adapt=n_adapt)
        assertion = split_assertions(episodes, rung, split)
        assertions_by_seed[str(seed)] = assertion
        if assertion["rung3_test_rules_subset_of_test"] is False:
            raise StopProbe("unseen_split_assertion", "rung3 test rules are not a subset of TEST_RULES", assertion, True)
        if assertion["train_rules_intersection_query_rules_empty"] is False:
            raise StopProbe("unseen_split_assertion", "TRAIN_RULES intersect rung3 query rules", assertion, True)
        if assertion["query_values_unseen_3_4_configured"] is False:
            raise StopProbe("unseen_split_assertion", "rung3 query values are not configured as [3,4]", assertion, True)
        for ep in episodes:
            record = evaluate_episode(ep, seed, phase, assertion)
            all_records.append(record)
            trace_handle.write(json.dumps(record, sort_keys=True) + "\n")
        all_episodes.extend(episodes)
    summary = summarize_trace_records(all_records)
    alias = GC.alias_report(all_episodes)
    if alias["implementation_alias"]:
        raise StopProbe("graph_cache_alias", "graph_cache predictions alias lookup or count_table for all episodes", alias, False)
    return {
        "phase": phase,
        "rung": S.rung_spec(rung, split).rung,
        "split": split,
        "n_adapt": P.N_ADAPT if n_adapt is None else int(n_adapt),
        "n_episodes_per_seed": len(all_records) // len(seeds),
        "summary": summary,
        "split_assertions_by_seed": assertions_by_seed,
        "graph_cache_alias_report": alias,
        "records_count": len(all_records),
        "episodes": all_episodes,
    }


def build_route_decision_input(panel: dict[str, Any], *, controls_passed: bool, leakage_clean: bool) -> dict[str, Any]:
    summary = panel["summary"]
    per_seed_headroom = [float(v) for v in summary["per_seed_headroom"]]
    return {
        "task_id": TASK_ID,
        "split": f"{panel['rung']}:{panel['split']}",
        "controls_passed": bool(controls_passed),
        "leakage_clean": bool(leakage_clean),
        "n_seeds": int(summary["n_seeds"]),
        "per_seed_headroom": per_seed_headroom,
        "fair_saturation_seed_count": int(summary["fair_saturation_seed_count"]),
        "ideal_degenerate": bool(summary["ideal_degenerate"]),
        "no_adaptation_matches_ideal": bool(summary["no_adaptation_matches_ideal"]),
        "predict_all_or_majority_match_ideal": bool(summary["predict_all_or_majority_match_ideal"]),
        "ideal_balacc_mean": float(summary["ideal_balacc_mean"]),
        "fair_max_episode_mean": float(summary["fair_max_episode_mean"]),
        "fair_baseline_balacc": summary["fair_baseline_balacc"],
        "aggregation_rule": "headroom = ideal - max(fair) per episode; per-seed mean; LCB in adjudicator",
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a.rung3_identifiability_probe"
            ".build_route_decision_input"
        ),
    }


def _agent_input_channels(episodes: list[Any]) -> dict[str, np.ndarray]:
    if not episodes:
        return {}
    n_adapt = min(int(ep.adapt_e.shape[0]) for ep in episodes)
    n_query = min(int(ep.query_a.shape[0]) for ep in episodes)
    channels: dict[str, np.ndarray] = {}
    for i in range(n_adapt):
        channels[f"adapt_a_{i:02d}"] = np.array([int(ep.adapt_a[i]) for ep in episodes], dtype=int)
        channels[f"adapt_e_{i:02d}"] = np.array([int(ep.adapt_e[i]) for ep in episodes], dtype=int)
        for d in range(P.D):
            channels[f"adapt_x_{i:02d}_{d}"] = np.array([int(ep.adapt_x[i, d]) for ep in episodes], dtype=int)
    for i in range(n_query):
        channels[f"query_a_{i:02d}"] = np.array([int(ep.query_a[i]) for ep in episodes], dtype=int)
        for d in range(P.D):
            channels[f"query_x_{i:02d}_{d}"] = np.array([int(ep.query_x[i, d]) for ep in episodes], dtype=int)
    return channels


def run_leakage_scan(named_episode_sets: dict[str, list[Any]]) -> dict[str, Any]:
    by_split: dict[str, Any] = {}
    overall_clean = True
    all_planted_caught = True
    for name, episodes in named_episode_sets.items():
        tgt = LK.targets(episodes)
        real_channels = _agent_input_channels(episodes)
        planted_channels = LK.planted_channels(episodes, tgt)
        real_report = LK.detect(real_channels, tgt)
        planted_report = LK.detect(planted_channels, tgt)
        real_flagged = [channel for channel, row in real_report.items() if row["flagged"]]
        planted_missed = [channel for channel, row in planted_report.items() if not row["flagged"]]
        split_clean = len(real_flagged) == 0
        split_planted = len(planted_missed) == 0
        overall_clean = overall_clean and split_clean
        all_planted_caught = all_planted_caught and split_planted
        by_split[name] = {
            "episodes": len(episodes),
            "agent_input_channel_count": len(real_channels),
            "real_report": real_report,
            "planted_report": planted_report,
            "real_flagged": real_flagged,
            "planted_missed": planted_missed,
            "real_channels_clean": split_clean,
            "all_planted_caught": split_planted,
            "renamed_leak_caught": bool(planted_report["telemetry_7"]["flagged"]),
        }
    return {
        "task_id": TASK_ID,
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a.rung3_identifiability_probe.run_leakage_scan"
        ),
        "by_split": by_split,
        "overall_real_channels_clean": overall_clean,
        "overall_all_planted_caught": all_planted_caught,
        "leakage_clean": bool(overall_clean and all_planted_caught),
    }


def replay_trace(trace_path: Path = TRACE_PATH, *, controls_passed: bool, leakage_clean: bool) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        phase = row.get("phase")
        split = str(row.get("split", ""))
        if phase == "real_rung3" or (phase is None and split == "rung3_test"):
            records.append(row)
    summary = summarize_trace_records(records)
    panel = {
        "rung": "rung3_real_unseen_rule_unseen_value",
        "split": "test",
        "summary": summary,
    }
    route_input = build_route_decision_input(panel, controls_passed=controls_passed, leakage_clean=leakage_clean)
    decision = ADJ.compute_route_decision(route_input)
    return {
        "task_id": TASK_ID,
        "trace_path": _display_path(trace_path),
        "records_replayed": len(records),
        "route_decision_input": route_input,
        "route_decision": decision,
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a.rung3_identifiability_probe.replay_trace"
        ),
    }


def validate_pre_run_gates() -> dict[str, Any]:
    frozen = verify_frozen_design()
    prereg = P.load_frozen_prereg()
    prereg_sha = str(prereg["_canonical_sha256_readback"])
    if prereg_sha != EXPECTED_PREREG_SHA256:
        raise StopProbe("prereg_sha", "prereg canonical sha mismatch", prereg_sha, EXPECTED_PREREG_SHA256)
    adj_self_test = ADJ.self_test()
    status = protected_source_status()
    diff = protected_source_diff()
    if status or diff:
        raise StopProbe(
            "banked_source_guard",
            "protected banked/frozen source has status or diff",
            {"status": status, "diff": diff},
            {"status": [], "diff": []},
        )
    return {
        "frozen_design": frozen,
        "prereg_sha256": prereg_sha,
        "prereg_sha_match": True,
        "adjudicator_self_test": adj_self_test,
        "protected_source_status": status,
        "protected_source_diff": diff,
    }


def _float_lists_close(a: list[float], b: list[float], tol: float = 1e-9) -> bool:
    return len(a) == len(b) and all(abs(float(x) - float(y)) <= tol for x, y in zip(a, b))


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT).as_posix())
    except ValueError:
        return str(path)


def _write_collision_record_from_frozen_design() -> dict[str, Any]:
    design = json.loads(FROZEN_DESIGN_PATH.read_text(encoding="utf-8"))
    payload = {
        "task_id": TASK_ID,
        "source": str(FROZEN_DESIGN_PATH.relative_to(REPO_ROOT).as_posix()),
        "frozen_design_sha256": design["_frozen_canonical_sha256"],
        "collision_record": design["collision_record"],
    }
    write_json(COLLISION_PATH, payload)
    return payload


def make_manifest(
    *,
    run_id: str,
    gate: dict[str, Any],
    real_panel: dict[str, Any],
    route_decision: dict[str, Any],
    replay_report: dict[str, Any],
) -> dict[str, Any]:
    source_files = {path: sha256_file(REPO_ROOT / path) for path in [*READ_ONLY_SOURCE_FILES, *NEW_SOURCE_FILES]}
    return {
        "task_id": TASK_ID,
        "run_id": run_id,
        "git_head": git_output(["rev-parse", "HEAD"]).strip(),
        "git_branch": git_output(["branch", "--show-current"]).strip(),
        "git_status_short_branch": git_output(["status", "--short", "--branch"]).splitlines(),
        "frozen_design_sha256": gate["frozen_design"]["computed_sha256"],
        "prereg_sha256": gate["prereg_sha256"],
        "source_sha256": source_files,
        "split_disjoint_assertions": real_panel["split_assertions_by_seed"],
        "graph_cache_alias_report": real_panel["graph_cache_alias_report"],
        "route": route_decision["route"],
        "replay_route": replay_report["route_decision"]["route"],
        "replay_matches_result": bool(route_decision["route"] == replay_report["route_decision"]["route"]),
        "unused_model_seeds": [],
        "used_model_seeds": P.model_seeds(),
        "artifact_paths": {
            "result": str(RESULT_PATH.relative_to(REPO_ROOT).as_posix()),
            "trace": str(TRACE_PATH.relative_to(REPO_ROOT).as_posix()),
            "baseline_comparison": str(BASELINE_PATH.relative_to(REPO_ROOT).as_posix()),
            "ablation_report": str(ABLATION_PATH.relative_to(REPO_ROOT).as_posix()),
            "control_report": str(CONTROL_PATH.relative_to(REPO_ROOT).as_posix()),
            "leakage_report": str(LEAKAGE_PATH.relative_to(REPO_ROOT).as_posix()),
            "replay_report": str(REPLAY_PATH.relative_to(REPO_ROOT).as_posix()),
            "route_decision_input": str(ROUTE_INPUT_PATH.relative_to(REPO_ROOT).as_posix()),
            "route_decision": str(ROUTE_DECISION_PATH.relative_to(REPO_ROOT).as_posix()),
            "manifest": str(MANIFEST_PATH.relative_to(REPO_ROOT).as_posix()),
            "collision_record": str(COLLISION_PATH.relative_to(REPO_ROOT).as_posix()),
        },
        "claim_ceiling": (
            "local candidate-free rung3 identifiability probe artifact provenance only; no learner, "
            "transfer, mechanism, agency, self, subjectivity, AGI, EGO, or companion-readiness claim"
        ),
    }


def run_probe() -> dict[str, Any]:
    clean_known_outputs()
    run_id = time.strftime("tlgp-rung3-ident-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
    gate = validate_pre_run_gates()
    collision = _write_collision_record_from_frozen_design()
    control_report: dict[str, Any] = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a.rung3_identifiability_probe.run_probe"
        ),
        "positive": None,
        "negative": None,
    }
    with TRACE_PATH.open("w", encoding="utf-8") as trace:
        positive = evaluate_panel(phase="positive_rung0_seen", rung=S.RUNG0, split="heldout", trace_handle=trace)
        positive_input = build_route_decision_input(positive, controls_passed=True, leakage_clean=True)
        positive_decision = ADJ.compute_route_decision(positive_input)
        control_report["positive"] = {
            "panel": {k: v for k, v in positive.items() if k != "episodes"},
            "route_decision_input": positive_input,
            "route_decision": positive_decision,
            "expected": ADJ.TERMINAL_HEADROOM,
            "passed": positive_decision["route"] == ADJ.TERMINAL_HEADROOM,
        }
        write_json(CONTROL_PATH, control_report)
        if positive_decision["route"] != ADJ.TERMINAL_HEADROOM:
            raise StopProbe(
                "positive_control",
                "positive rung0 seen-rule control did not report headroom_exists",
                positive_decision,
                ADJ.TERMINAL_HEADROOM,
            )

        negative = evaluate_panel(
            phase="negative_rung3_n_adapt_1",
            rung=S.RUNG3,
            split="test",
            trace_handle=trace,
            n_adapt=1,
        )
        negative_input = build_route_decision_input(negative, controls_passed=True, leakage_clean=True)
        negative_input["control_role"] = "negative_no_signal"
        negative_decision = ADJ.compute_route_decision(negative_input)
        control_report["negative"] = {
            "panel": {k: v for k, v in negative.items() if k != "episodes"},
            "route_decision_input": negative_input,
            "route_decision": negative_decision,
            "expected": [ADJ.TERMINAL_CEILING, ADJ.TERMINAL_INCONCLUSIVE],
            "passed": negative_decision["route"] != ADJ.TERMINAL_HEADROOM,
        }
        control_report["controls_passed"] = bool(
            control_report["positive"]["passed"] and control_report["negative"]["passed"]
        )
        write_json(CONTROL_PATH, control_report)
        if negative_decision["route"] == ADJ.TERMINAL_HEADROOM:
            raise StopProbe(
                "negative_control",
                "negative N_ADAPT=1 control reported headroom_exists",
                negative_decision,
                [ADJ.TERMINAL_CEILING, ADJ.TERMINAL_INCONCLUSIVE],
            )

        real = evaluate_panel(phase="real_rung3", rung=S.RUNG3, split="test", trace_handle=trace)
        leakage = run_leakage_scan({"real_rung3": real["episodes"]})
        write_json(LEAKAGE_PATH, leakage)
        if not leakage["overall_all_planted_caught"]:
            raise StopProbe("leakage_planted", "planted leakage channel was not caught", leakage, True)
        if not leakage["overall_real_channels_clean"]:
            route_input = build_route_decision_input(real, controls_passed=True, leakage_clean=False)
            route_decision = ADJ.compute_route_decision(route_input)
            write_json(ROUTE_INPUT_PATH, route_input)
            write_json(ROUTE_DECISION_PATH, route_decision)
            raise StopProbe("leakage_real_channels", "real agent input channel flagged as leakage", leakage, True)

        ablation = {
            "task_id": TASK_ID,
            "run_id": run_id,
            "producer_function": (
                "src.tlgp_capability_witness_preflight_001a.rung3_identifiability_probe.run_probe"
            ),
            "adapt_size": {
                "24": {k: v for k, v in real.items() if k != "episodes"},
            },
            "no_adaptation_ablation": {
                "no_adaptation_matches_ideal": real["summary"]["no_adaptation_matches_ideal"],
                "no_adaptation_balacc": real["summary"]["fair_baseline_balacc"]["no_adaptation"],
                "ideal_balacc": real["summary"]["ideal_balacc_mean"],
                "DELTA": P.DELTA(),
            },
        }
        for n_adapt in (6, 12):
            panel = evaluate_panel(
                phase=f"ablation_n_adapt_{n_adapt}",
                rung=S.RUNG3,
                split="test",
                trace_handle=trace,
                n_adapt=n_adapt,
            )
            ablation["adapt_size"][str(n_adapt)] = {k: v for k, v in panel.items() if k != "episodes"}

    route_input = build_route_decision_input(real, controls_passed=True, leakage_clean=leakage["leakage_clean"])
    route_decision = ADJ.compute_route_decision(route_input)
    replay_report = replay_trace(TRACE_PATH, controls_passed=True, leakage_clean=leakage["leakage_clean"])
    if route_decision["route"] != replay_report["route_decision"]["route"]:
        raise StopProbe(
            "replay_route",
            "replay reconstructed a different route",
            replay_report["route_decision"],
            route_decision,
        )
    if not _float_lists_close(
        route_input["per_seed_headroom"],
        replay_report["route_decision_input"]["per_seed_headroom"],
        tol=1e-9,
    ):
        raise StopProbe(
            "replay_headroom",
            "replay reconstructed different per-seed headroom",
            replay_report["route_decision_input"]["per_seed_headroom"],
            route_input["per_seed_headroom"],
        )

    baseline = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "fair_panel": FAIR_PANEL,
        "real_rung3": {k: v for k, v in real.items() if k != "episodes"},
        "graph_cache_alias_report": real["graph_cache_alias_report"],
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a.rung3_identifiability_probe.run_probe"
        ),
    }
    result = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "verdict": route_decision["route"],
        "route_decision": route_decision,
        "route_decision_input": route_input,
        "controls_passed": True,
        "leakage_clean": leakage["leakage_clean"],
        "frozen_design_sha256": gate["frozen_design"]["computed_sha256"],
        "prereg_sha256": gate["prereg_sha256"],
        "collision_record_path": str(COLLISION_PATH.relative_to(REPO_ROOT).as_posix()),
        "baseline_comparison_path": str(BASELINE_PATH.relative_to(REPO_ROOT).as_posix()),
        "ablation_report_path": str(ABLATION_PATH.relative_to(REPO_ROOT).as_posix()),
        "control_report_path": str(CONTROL_PATH.relative_to(REPO_ROOT).as_posix()),
        "leakage_report_path": str(LEAKAGE_PATH.relative_to(REPO_ROOT).as_posix()),
        "replay_report_path": str(REPLAY_PATH.relative_to(REPO_ROOT).as_posix()),
        "claim_ceiling": (
            "bounded candidate-free no-GPU rung3 identifiability probe only; "
            "headroom_exists authorizes a separate powered learner run but proves no learner transfer, "
            "mechanism, agency, self, subjectivity, AGI, EGO, or companion-readiness"
        ),
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a.rung3_identifiability_probe.run_probe"
        ),
        "input_artifacts": [
            str(FROZEN_DESIGN_PATH.relative_to(REPO_ROOT).as_posix()),
            "artifacts/TLGP-001B-R2/prereg.json",
            "src/tlgp_001a/ideal_observer.py",
            "src/tlgp_001b_r2/lower_reference.py",
            "src/tlgp_001b_r2/splits.py",
        ],
        "aggregation_rule": route_input["aggregation_rule"],
        "code_path_hash": _hash_payload(
            {path: sha256_file(REPO_ROOT / path) for path in [*NEW_SOURCE_FILES, *READ_ONLY_SOURCE_FILES]}
        ),
    }
    manifest = make_manifest(
        run_id=run_id,
        gate=gate,
        real_panel=real,
        route_decision=route_decision,
        replay_report=replay_report,
    )
    write_json(ROUTE_INPUT_PATH, route_input)
    write_json(ROUTE_DECISION_PATH, route_decision)
    write_json(BASELINE_PATH, baseline)
    write_json(ABLATION_PATH, ablation)
    write_json(REPLAY_PATH, replay_report)
    write_json(RESULT_PATH, result)
    write_json(MANIFEST_PATH, manifest)
    if protected_source_status() or protected_source_diff():
        raise StopProbe(
            "banked_source_guard_after_run",
            "protected banked/frozen source changed during run",
            {"status": protected_source_status(), "diff": protected_source_diff()},
            {"status": [], "diff": []},
        )
    return {
        "result": result,
        "baseline": baseline,
        "ablation": ablation,
        "control_report": control_report,
        "leakage": leakage,
        "replay": replay_report,
        "manifest": manifest,
        "collision": collision,
    }


def write_failure_manifest(exc: BaseException) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    if isinstance(exc, StopProbe):
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
            "git_status": git_output(["status", "--short", "--branch"], check=False).splitlines(),
            "claim_ceiling": "probe stopped; no rung3 identifiability verdict beyond the failure reason",
        }
    )
    write_json(FAILURE_PATH, payload)


def self_test() -> dict[str, Any]:
    gate = validate_pre_run_gates()
    alias_ep = make_seeded_episodes(S.RUNG3, "test", P.model_seeds()[0], 0, n_adapt=1, n_episodes=1)[0]
    graph_pred = GC.successor_map(alias_ep)
    if graph_pred.shape[0] != P.N_QUERY:
        raise StopProbe("graph_cache_self_test", "graph_cache prediction length mismatch", graph_pred.shape[0], P.N_QUERY)
    return {
        "task_id": TASK_ID,
        "gate": gate,
        "graph_cache_smoke": {
            "prediction_length": int(graph_pred.shape[0]),
            "query_hit_fraction": GC.query_hit_fraction(alias_ep),
            "alias_report": GC.alias_report([alias_ep]),
        },
        "claim_ceiling": "self-test only; no real-split result interpreted",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", help="validate static gates and module self-tests")
    parser.add_argument("--run", action="store_true", help="run controls then real rung3 probe")
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            print(json.dumps(self_test(), indent=2, sort_keys=True))
            return 0
        if args.run:
            out = run_probe()
            print(json.dumps({"verdict": out["result"]["verdict"], "result_path": str(RESULT_PATH)}, indent=2))
            return 0
        parser.error("use --self-test or --run")
    except BaseException as exc:
        write_failure_manifest(exc)
        print(f"rung3 identifiability probe stopped: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
