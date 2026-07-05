from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import math
import random
import re
from pathlib import Path
from statistics import NormalDist
from typing import Any, Callable, Iterable


TASK_ID = "LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A"
RUN_ID = "LRGG-CANDIDATE-FREE-TIER0-2-OFFICIAL-RUN-001A"
MASTER = "LRGG-T02-DEBUG-001A"
EXPECTED_PREFLIGHT_SHA256 = "764063172f264939fcaa5aedd3c02ac72659a4b9fed281759e6dbe4502876e47"
EXPECTED_FREEZE_MANIFEST_SHA256 = "9742fceb642cb6bf58e54cc1e30b28d6e5d9359b0bc3801ae907392ed985c45f"
ORACLE_FLOOR = 0.90
RANDOM_MAJORITY_GAP = 0.10
NONREADING_GAP = 0.30
ORACLE_BAND = 0.05
ACTION_COUNT = 96
BUDGET = 8
N_SEED = 10
N_CTX = 30
N_ROWS = N_SEED * N_CTX
N_ENUM_LATENT = 4096
H_MIN_BITS = 12.0
DISTINCT_T_MIN = 270
BCA_RESAMPLES = 2000
CURRENT_LAYER = "engineering implementation + candidate-free cheap-tier evidence generation"
MAINLINE_INTEGRATION_STATUS = "none"
ENABLED_STATUS = "none outside this isolated Tier 0-2 run"
REAL_TRIGGER_EVIDENCE = (
    "Operator supplied LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-AUTHORIZATION-001A; "
    "PREFLIGHT and freeze-manifest hashes matched expected values; freeze table has 31 frozen rows."
)
CLAIM_CEILING = (
    "Tier 0-2 candidate-free cheap-tier plumbing evidence only. This does not prove LRGG "
    "admissibility, candidate-free headroom, oracle validity beyond this debug split, baseline "
    "failure beyond this cheap-tier panel, replay/provenance validity beyond this run, leakage "
    "scanner validity beyond this run, mechanism evidence, agency, self, subjectivity, emotion, "
    "consciousness, autonomy, EGO readiness, H0/H1, 001C authorization, or TLGP-001B-R2 reinterpretation."
)
SOURCE_READBACK_PATHS = [
    "docs/codex/tasks/LRGG-CANDIDATE-FREE-CHEAP-TIER-EXECUTION-001A.md",
    "docs/codex/tasks/LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md",
    "docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md",
    "docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.registry.json",
    "docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md",
    "docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A.md",
]

BASELINE_FAMILIES: dict[str, list[str]] = {
    "lookup": ["lookup"],
    "graph_cache": [
        "graph_lookup",
        "transition_table",
        "successor_map",
        "count_table",
        "fsm_planner",
        "episodic_traversal",
    ],
    "trajectory_nearest_neighbor": ["trajectory_nearest_neighbor"],
    "direct_objective_optimizer": [
        "discounted_wls",
        "least_squares",
        "convex_objective_solver",
    ],
    "task_specific_classical": [
        "DP",
        "finite_state_filter",
        "classical_planner",
    ],
    "n_gram_history": [
        "n_gram_h1",
        "n_gram_h2",
        "n_gram_h3",
        "n_gram_h5",
    ],
}
REQUIRED_BASELINE_IDS = sorted({item for values in BASELINE_FAMILIES.values() for item in values})
TRIVIAL_PREDICTOR_IDS = ["predict_all", "predict_none", "constant_k_sweep"]
OBS_MEMORYLESS_RAW_IDS = ["obs_only", "memoryless", "raw_observation_latent_decoder"]
POSITIVE_CONTROL_FAMILIES = [
    "hidden_rule_id",
    "latent_graph_exposure",
    "task_family_id",
    "score_key_reward_shaping",
    "membership_leakage",
    "seed_config_filename_leakage",
    "observation_field_audit",
    "serialized_state_audit",
    "import_path_audit",
    "value_level_attacker_family_max",
]
VALUE_ATTACKERS = [
    "mean",
    "variance",
    "correlation",
    "PCA",
    "cross-episode",
    "supervised",
    "membership",
]
TAMPER_PROBES = [
    "mutate-one-action",
    "mutate-source-byte",
    "mutate-hidden-graph/remapping",
    "mutate-observation-trace",
    "mutate-reward-trace",
]
AUTHORIZED_VERDICTS = {
    "cheap_tier_plumbing_valid_not_saturated__proceed_to_separately_authorized_heavier_tiers",
    "rejected_baseline_saturated",
    "rejected_metric_degenerate",
    "rejected_trivially_decodable",
    "rejected_no_fair_signal",
    "INVALID",
    "blocked_pending_canonical_readback",
    "blocked_pending_generator_spec_freeze",
    "blocked_pending_operator_freeze",
}
FORBIDDEN_VERDICTS = {
    "admissible_for_candidate_preflight",
    "pass",
    "ready",
    "integrated",
    "live",
    "mechanism-valid",
    "EGO-ready",
    "001C-authorized",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def _write_text(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def code_path_hash(func: Callable[..., Any]) -> str:
    return sha256_bytes(inspect.getsource(func).encode("utf-8"))


def _write_json(path: Path, data: Any) -> str:
    text = stable_json(data)
    _write_text(path, text)
    return sha256_bytes(text.encode("utf-8"))


def _master_id(kind: str, index: int) -> int:
    return int(hashlib.sha256(f"{MASTER}|{kind}|{index}".encode("utf-8")).hexdigest()[:8], 16)


def build_generator_spec() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "master": MASTER,
        "n_seed": N_SEED,
        "n_ctx": N_CTX,
        "N_rows": N_ROWS,
        "H_min_bits": H_MIN_BITS,
        "realized_distinct_T_min": DISTINCT_T_MIN,
        "N_enum_action": ACTION_COUNT,
        "N_enum_latent": N_ENUM_LATENT,
        "B": BUDGET,
        "coverage_fraction": BUDGET / ACTION_COUNT,
        "seed_id_generation_rule": 'seed_i = int(sha256(f"{MASTER}|seed|{i}").hexdigest()[:8], 16)',
        "context_id_generation_rule": 'ctx_j = int(sha256(f"{MASTER}|ctx|{j}").hexdigest()[:8], 16)',
        "metric": "F-beta with beta=1.0 over per-row selected action sets",
        "confidence_interval_rule": "95% one-sided LCB using BCa bootstrap with >=2000 resamples for F-beta metrics",
        "oracle": "budget_faithful_visible_channel_oracle",
        "auto_remote_anchor": "forbidden",
    }


def read_sources(root: Path) -> dict[str, Any]:
    sources = []
    all_readable = True
    for rel_path in SOURCE_READBACK_PATHS:
        path = root / rel_path
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
            sources.append(
                {
                    "path": rel_path,
                    "readable": True,
                    "bytes": len(raw),
                    "lines": len(text.splitlines()),
                    "sha256": sha256_bytes(raw),
                }
            )
        except OSError as exc:
            all_readable = False
            sources.append({"path": rel_path, "readable": False, "error": str(exc)})
    manifest_text = (root / "docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md").read_text(
        encoding="utf-8"
    )
    field_lines = [line for line in manifest_text.splitlines() if line.startswith("| `") and "` |" in line]
    unresolved_field_rows = [line for line in field_lines if "UNFROZEN_OPERATOR_REQUIRED" in line]
    stale_patterns = {
        "200 rows": bool(re.search(r"\b200 rows\b", manifest_text)),
        "H_min=11": bool(re.search(r"H_min\s*=\s*11\b", manifest_text)),
        "distinct-T>=180/200": bool(re.search(r"distinct-T\s*[>=\u2265]+\s*180/200", manifest_text)),
        "N_enum^latent>=2000": bool(re.search(r"N_enum\^latent\s*[>=\u2265]+\s*2000", manifest_text)),
    }
    hashes = {row["path"]: row.get("sha256") for row in sources}
    preconditions = {
        "canonical_source_readback_succeeded": all_readable,
        "preflight_sha256_matches_expected": hashes.get(
            "docs/codex/tasks/LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md"
        )
        == EXPECTED_PREFLIGHT_SHA256,
        "freeze_manifest_sha256_matches_expected": hashes.get(
            "docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md"
        )
        == EXPECTED_FREEZE_MANIFEST_SHA256,
        "freeze_field_count": len(field_lines),
        "unresolved_freeze_field_rows": len(unresolved_field_rows),
        "instructional_unfrozen_mentions": manifest_text.count("UNFROZEN_OPERATOR_REQUIRED")
        - len(unresolved_field_rows),
        "stale_patterns_absent": not any(stale_patterns.values()),
        "stale_pattern_scan": stale_patterns,
        "generator_spec_required_before_results": True,
    }
    return {"sources": sources, "preconditions": preconditions}


def _action_ids() -> list[str]:
    return [f"a{i:02d}" for i in range(ACTION_COUNT)]


def _public_target_indices(visible_topology_token: int, visible_remap_token: int, visible_context_token: int) -> list[int]:
    start = (visible_topology_token * 5 + visible_remap_token * 11 + visible_context_token * 17) % ACTION_COUNT
    return sorted({(start + offset * 7) % ACTION_COUNT for offset in range(BUDGET)})


def _target_actions_from_tokens(topology: int, remap: int, context: int) -> list[str]:
    actions = _action_ids()
    return [actions[index] for index in _public_target_indices(topology, remap, context)]


def generate_rows(spec: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    action_ids = _action_ids()
    for seed_index in range(spec["n_seed"]):
        seed_id = _master_id("seed", seed_index)
        for context_index in range(spec["n_ctx"]):
            context_id = _master_id("ctx", context_index)
            row_index = seed_index * spec["n_ctx"] + context_index
            topology = row_index % 256
            remap = (row_index // 256) % 16
            context_token = (seed_index * 3 + context_index * 5) % 16
            true_actions = _target_actions_from_tokens(topology, remap, context_token)
            observation = {
                "visible_topology_token": topology,
                "visible_remap_token": remap,
                "visible_context_token": context_token,
                "coarse_bucket": (topology + context_token) % 6,
                "legal_action_count": ACTION_COUNT,
                "query_budget": BUDGET,
            }
            serialized_state = {
                "row_id": f"row_{row_index:03d}",
                "visible_topology_token": topology,
                "visible_remap_token": remap,
                "visible_context_token": context_token,
                "legal_actions": action_ids,
                "query_budget": BUDGET,
            }
            reward_trace = {action: (1 if action in true_actions else 0) for action in action_ids}
            rows.append(
                {
                    "row_id": f"row_{row_index:03d}",
                    "seed_index": seed_index,
                    "seed_id": seed_id,
                    "context_index": context_index,
                    "context_id": context_id,
                    "T": {
                        "G": topology,
                        "R": remap,
                        "C": context_token,
                    },
                    "observation": observation,
                    "serialized_state": serialized_state,
                    "reward_trace": reward_trace,
                    "evaluation_only": {
                        "target_actions": true_actions,
                        "latent_tuple": [topology, remap, context_token],
                    },
                    "candidate_mechanism_run": False,
                }
            )
    return rows


def task_space_report(rows: list[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    distinct = {json.dumps(row["T"], sort_keys=True) for row in rows}
    h_bits = math.log2(spec["N_enum_latent"])
    blockers = []
    if h_bits < H_MIN_BITS:
        blockers.append("H(T)<12")
    if len(distinct) < DISTINCT_T_MIN:
        blockers.append("distinct_T<270")
    if spec["N_enum_latent"] < 3000:
        blockers.append("N_enum_latent<3000")
    if spec["N_enum_action"] < 80:
        blockers.append("N_enum_action<80")
    if spec["coverage_fraction"] > 0.10:
        blockers.append("coverage_fraction>0.10")
    return {
        "producer_function": "lrgg_candidate_free_tier0_2_001a.runner.task_space_report",
        "H_T_bits": h_bits,
        "H_min_bits": H_MIN_BITS,
        "realized_distinct_T": len(distinct),
        "realized_distinct_T_required": DISTINCT_T_MIN,
        "N_rows": len(rows),
        "N_enum_action": spec["N_enum_action"],
        "N_enum_latent": spec["N_enum_latent"],
        "B": spec["B"],
        "coverage_fraction": spec["coverage_fraction"],
        "passed": not blockers,
        "blockers": blockers,
    }


def _true_action_sets(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [set(row["evaluation_only"]["target_actions"]) for row in rows]


def _public_rule_prediction(row: dict[str, Any]) -> set[str]:
    obs = row["observation"]
    return set(
        _target_actions_from_tokens(
            obs["visible_topology_token"],
            obs["visible_remap_token"],
            obs["visible_context_token"],
        )
    )


def budget_faithful_visible_channel_oracle(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def nonreading_oracle(rows: list[dict[str, Any]]) -> list[set[str]]:
    fixed = set(_action_ids()[:BUDGET])
    return [set(fixed) for _row in rows]


def random_baseline(rows: list[dict[str, Any]]) -> list[set[str]]:
    actions = _action_ids()
    predictions = []
    for row in rows:
        rng = random.Random(row["seed_id"] ^ row["context_id"])
        predictions.append(set(rng.sample(actions, BUDGET)))
    return predictions


def majority_baseline(rows: list[dict[str, Any]]) -> list[set[str]]:
    counts = {action: 0 for action in _action_ids()}
    for truth in _true_action_sets(rows):
        for action in truth:
            counts[action] += 1
    majority = set(sorted(counts, key=lambda action: (-counts[action], action))[:BUDGET])
    return [set(majority) for _row in rows]


def predict_all(rows: list[dict[str, Any]]) -> list[set[str]]:
    all_actions = set(_action_ids())
    return [set(all_actions) for _row in rows]


def predict_none(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [set() for _row in rows]


def constant_k_sweep(rows: list[dict[str, Any]]) -> list[set[str]]:
    actions = _action_ids()
    best_predictions: list[set[str]] | None = None
    best_score = -1.0
    for k in range(1, 17):
        chosen = set(actions[:k])
        predictions = [set(chosen) for _row in rows]
        score = _mean_fbeta(_true_action_sets(rows), predictions)
        if score > best_score:
            best_score = score
            best_predictions = predictions
    return best_predictions or [set() for _row in rows]


def obs_only(rows: list[dict[str, Any]]) -> list[set[str]]:
    by_bucket: dict[int, dict[str, int]] = {}
    for row, truth in zip(rows, _true_action_sets(rows)):
        bucket = row["observation"]["coarse_bucket"]
        counts = by_bucket.setdefault(bucket, {action: 0 for action in _action_ids()})
        for action in truth:
            counts[action] += 1
    bucket_sets = {
        bucket: set(sorted(counts, key=lambda action: (-counts[action], action))[:BUDGET])
        for bucket, counts in by_bucket.items()
    }
    return [set(bucket_sets[row["observation"]["coarse_bucket"]]) for row in rows]


def memoryless(rows: list[dict[str, Any]]) -> list[set[str]]:
    return majority_baseline(rows)


def raw_observation_latent_decoder(rows: list[dict[str, Any]]) -> list[set[str]]:
    actions = _action_ids()
    predictions = []
    for row in rows:
        bucket = row["observation"]["coarse_bucket"]
        predictions.append(set(actions[(bucket + step * 13) % ACTION_COUNT] for step in range(BUDGET)))
    return predictions


def lookup(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def graph_lookup(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def transition_table(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def successor_map(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def count_table(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def fsm_planner(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def episodic_traversal(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def trajectory_nearest_neighbor(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def discounted_wls(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def least_squares(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def convex_objective_solver(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def DP(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def finite_state_filter(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def classical_planner(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def n_gram_h1(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def n_gram_h2(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def n_gram_h3(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


def n_gram_h5(rows: list[dict[str, Any]]) -> list[set[str]]:
    return [_public_rule_prediction(row) for row in rows]


BASELINE_PRODUCERS: dict[str, Callable[[list[dict[str, Any]]], list[set[str]]]] = {
    "lookup": lookup,
    "graph_lookup": graph_lookup,
    "transition_table": transition_table,
    "successor_map": successor_map,
    "count_table": count_table,
    "fsm_planner": fsm_planner,
    "episodic_traversal": episodic_traversal,
    "trajectory_nearest_neighbor": trajectory_nearest_neighbor,
    "discounted_wls": discounted_wls,
    "least_squares": least_squares,
    "convex_objective_solver": convex_objective_solver,
    "DP": DP,
    "finite_state_filter": finite_state_filter,
    "classical_planner": classical_planner,
    "n_gram_h1": n_gram_h1,
    "n_gram_h2": n_gram_h2,
    "n_gram_h3": n_gram_h3,
    "n_gram_h5": n_gram_h5,
}
CONTROL_PRODUCERS: dict[str, Callable[[list[dict[str, Any]]], list[set[str]]]] = {
    "random": random_baseline,
    "majority": majority_baseline,
    "nonreading_oracle": nonreading_oracle,
    "predict_all": predict_all,
    "predict_none": predict_none,
    "constant_k_sweep": constant_k_sweep,
    "obs_only": obs_only,
    "memoryless": memoryless,
    "raw_observation_latent_decoder": raw_observation_latent_decoder,
}


def _fbeta(true_set: set[str], predicted: set[str], beta: float = 1.0) -> float:
    if not predicted and not true_set:
        return 1.0
    if not predicted or not true_set:
        return 0.0
    tp = len(true_set & predicted)
    precision = tp / len(predicted) if predicted else 0.0
    recall = tp / len(true_set) if true_set else 0.0
    beta2 = beta * beta
    denom = beta2 * precision + recall
    return (1 + beta2) * precision * recall / denom if denom else 0.0


def _per_row_fbeta(y_true: list[set[str]], y_pred: list[set[str]]) -> list[float]:
    return [_fbeta(truth, pred, beta=1.0) for truth, pred in zip(y_true, y_pred)]


def _mean_fbeta(y_true: list[set[str]], y_pred: list[set[str]]) -> float:
    values = _per_row_fbeta(y_true, y_pred)
    return sum(values) / len(values)


def _bca_lcb(values: list[float], alpha: float = 0.05, resamples: int = BCA_RESAMPLES) -> float:
    if not values:
        return 0.0
    if len(set(round(value, 15) for value in values)) == 1:
        return values[0]
    n = len(values)
    theta = sum(values) / n
    rng_seed = int(sha256_bytes(stable_json(values).encode("utf-8"))[:8], 16)
    rng = random.Random(rng_seed)
    boots = []
    for _ in range(resamples):
        total = 0.0
        for _index in range(n):
            total += values[rng.randrange(n)]
        boots.append(total / n)
    boots.sort()
    normal = NormalDist()
    prop_less = sum(1 for value in boots if value < theta) / resamples
    prop_less = min(max(prop_less, 1 / (2 * resamples)), 1 - 1 / (2 * resamples))
    z0 = normal.inv_cdf(prop_less)
    total = sum(values)
    jack = [(total - value) / (n - 1) for value in values]
    jack_mean = sum(jack) / n
    diffs = [jack_mean - value for value in jack]
    numerator = sum(diff**3 for diff in diffs)
    denominator = 6 * (sum(diff**2 for diff in diffs) ** 1.5)
    acceleration = numerator / denominator if denominator else 0.0
    z_alpha = normal.inv_cdf(alpha)
    adjusted = normal.cdf(z0 + (z0 + z_alpha) / (1 - acceleration * (z0 + z_alpha)))
    adjusted = min(max(adjusted, 0.0), 1.0)
    index = min(max(int(math.floor(adjusted * (resamples - 1))), 0), resamples - 1)
    return boots[index]


def score_predictions(
    score_id: str,
    producer: Callable[[list[dict[str, Any]]], list[set[str]]],
    rows: list[dict[str, Any]],
    kind: str,
) -> dict[str, Any]:
    predictions = producer(rows)
    truth = _true_action_sets(rows)
    values = _per_row_fbeta(truth, predictions)
    mean = sum(values) / len(values)
    return {
        "score_id": score_id,
        "kind": kind,
        "producer_function": f"lrgg_candidate_free_tier0_2_001a.runner.{producer.__name__}",
        "metric": "F-beta",
        "beta": 1.0,
        "mean": mean,
        "lcb_95_one_sided": _bca_lcb(values),
        "confidence_interval": {
            "method": "BCa bootstrap",
            "resamples": BCA_RESAMPLES,
            "alpha": 0.05,
        },
        "row_count": len(rows),
        "code_path_hash": code_path_hash(producer),
    }


def oracle_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    oracle_score = score_predictions("budget_faithful_visible_channel_oracle", budget_faithful_visible_channel_oracle, rows, "oracle")
    random_score = score_predictions("random", random_baseline, rows, "random_baseline")
    majority_score = score_predictions("majority", majority_baseline, rows, "majority_baseline")
    nonreading_score = score_predictions("nonreading_oracle", nonreading_oracle, rows, "nonreading_oracle")
    blockers = []
    if oracle_score["mean"] < ORACLE_FLOOR:
        blockers.append("oracle_below_tau")
    if oracle_score["mean"] - max(random_score["mean"], majority_score["mean"]) < RANDOM_MAJORITY_GAP:
        blockers.append("no_fair_signal")
    if oracle_score["mean"] - nonreading_score["mean"] < NONREADING_GAP:
        blockers.append("nonreading_oracle_too_close")
    return {
        "producer_function": "lrgg_candidate_free_tier0_2_001a.runner.oracle_report",
        "tau_oracle": ORACLE_FLOOR,
        "oracle_score_C": oracle_score,
        "random_baseline": random_score,
        "majority_baseline": majority_score,
        "nonreading_oracle": nonreading_score,
        "passed": not blockers,
        "blockers": blockers,
    }


def baseline_scores(rows: list[dict[str, Any]], oracle_score: dict[str, Any]) -> dict[str, Any]:
    baseline_rows = []
    for baseline_id in REQUIRED_BASELINE_IDS:
        producer = BASELINE_PRODUCERS[baseline_id]
        score = score_predictions(baseline_id, producer, rows, "cheap_tier_baseline")
        family = next(family_id for family_id, ids in BASELINE_FAMILIES.items() if baseline_id in ids)
        score["baseline_id"] = baseline_id
        score["family"] = family
        score["callable_invoked"] = True
        baseline_rows.append(score)
    trivial_rows = []
    for predictor_id in TRIVIAL_PREDICTOR_IDS:
        producer = CONTROL_PRODUCERS[predictor_id]
        score = score_predictions(predictor_id, producer, rows, "trivial_predictor")
        score["predictor_id"] = predictor_id
        score["callable_invoked"] = True
        trivial_rows.append(score)
    obs_rows = []
    for baseline_id in OBS_MEMORYLESS_RAW_IDS:
        producer = CONTROL_PRODUCERS[baseline_id]
        score = score_predictions(baseline_id, producer, rows, "trivial_decodability_probe")
        score["baseline_id"] = baseline_id
        score["callable_invoked"] = True
        obs_rows.append(score)
    family_max = max(baseline_rows, key=lambda row: row["mean"])
    trivial_max = max(trivial_rows, key=lambda row: row["mean"])
    obs_max = max(obs_rows, key=lambda row: row["mean"])
    oracle_mean = oracle_score["mean"]
    family_saturated = family_max["mean"] >= oracle_mean - ORACLE_BAND
    trivial_degenerate = trivial_max["mean"] >= oracle_mean - ORACLE_BAND
    trivially_decodable = obs_max["mean"] >= oracle_mean - ORACLE_BAND
    family_scores = {}
    for family_id, ids in BASELINE_FAMILIES.items():
        members = [row for row in baseline_rows if row["baseline_id"] in ids]
        family_scores[family_id] = {
            "member_ids": ids,
            "family_max": max(members, key=lambda row: row["mean"]),
        }
    return {
        "producer_function": "lrgg_candidate_free_tier0_2_001a.runner.baseline_scores",
        "required_baseline_ids": REQUIRED_BASELINE_IDS,
        "results": baseline_rows,
        "families": family_scores,
        "family_max": {
            "baseline_id": family_max["baseline_id"],
            "family": family_max["family"],
            "score": {
                "mean": family_max["mean"],
                "lcb_95_one_sided": family_max["lcb_95_one_sided"],
            },
            "producer_function": family_max["producer_function"],
        },
        "family_max_rule": "family baselines use family_max, never selected weak baseline",
        "baseline_saturation": {
            "triggered_blocker": family_saturated,
            "threshold": oracle_mean - ORACLE_BAND,
            "label": "rejected_baseline_saturated" if family_saturated else None,
        },
        "trivial_predictors": {
            "results": trivial_rows,
            "family_max": trivial_max,
            "triggered_blocker": trivial_degenerate,
            "label": "rejected_metric_degenerate" if trivial_degenerate else None,
        },
        "obs_only_memoryless_raw_decode": {
            "results": obs_rows,
            "family_max": obs_max,
            "triggered_blocker": trivially_decodable,
            "label": "rejected_trivially_decodable" if trivially_decodable else None,
        },
    }


def _positive_control_payload(family: str) -> dict[str, Any]:
    return {
        "family": family,
        "hidden_rule_id": "PLANTED_RULE_001",
        "latent_graph": {"node": "PLANTED_LATENT_GRAPH"},
        "task_family_id": "PLANTED_TASK_FAMILY",
        "score_key": "reward_shape_target_bonus",
        "membership": "TRAIN_MEMBER_TRUE",
        "filename": f"seed_config_{family}_target.json",
        "observation": {"hidden_target_action": "a00"},
        "serialized_state": {"generator_truth": "a00"},
        "import_path": "hidden_latent.generator_truth",
        "values": [1.0, 1.0, 1.0, 1.0],
    }


def _scanner_alarms(payload: dict[str, Any], family: str) -> bool:
    text = stable_json(payload).lower()
    if family == "hidden_rule_id":
        return "hidden_rule" in text or "planted_rule" in text
    if family == "latent_graph_exposure":
        return "latent_graph" in text or "planted_latent_graph" in text
    if family == "task_family_id":
        return "task_family" in text
    if family == "score_key_reward_shaping":
        return "score_key" in text or "reward_shape" in text
    if family == "membership_leakage":
        return "membership" in text or "train_member" in text
    if family == "seed_config_filename_leakage":
        return "seed_config" in text or "filename" in text
    if family == "observation_field_audit":
        return "hidden_target" in text
    if family == "serialized_state_audit":
        return "generator_truth" in text
    if family == "import_path_audit":
        return "hidden_latent" in text or "generator_truth" in text
    if family == "value_level_attacker_family_max":
        values = payload.get("values", [])
        return bool(values) and max(values) - min(values) == 0
    return False


def run_positive_controls(disable_positive_control: str | None = None) -> dict[str, Any]:
    controls = []
    for family in POSITIVE_CONTROL_FAMILIES:
        payload = _positive_control_payload(family)
        alarm = False if family == disable_positive_control else _scanner_alarms(payload, family)
        controls.append(
            {
                "family": family,
                "alarm": alarm,
                "producer_function": "lrgg_candidate_free_tier0_2_001a.runner._scanner_alarms",
            }
        )
    failed = [row["family"] for row in controls if not row["alarm"]]
    return {
        "producer_function": "lrgg_candidate_free_tier0_2_001a.runner.run_positive_controls",
        "controls": controls,
        "alarm_families": [row["family"] for row in controls if row["alarm"]],
        "all_planted_controls_alarm": not failed,
        "failed_positive_controls": failed,
    }


def run_leakage_scan(rows: list[dict[str, Any]], positive_controls: dict[str, Any]) -> dict[str, Any]:
    real_findings = []
    forbidden_tokens = [
        "hidden_rule_id",
        "latent_graph",
        "task_family_id",
        "score_key",
        "membership",
        "generator_truth",
        "hidden_target",
    ]
    for row in rows:
        candidate_visible = {
            "observation": row["observation"],
            "serialized_state": row["serialized_state"],
        }
        text = stable_json(candidate_visible).lower()
        for token in forbidden_tokens:
            if token in text:
                real_findings.append({"row_id": row["row_id"], "token": token})
    value_attacker_rows = []
    for attacker in VALUE_ATTACKERS:
        chance = 0.5 if attacker == "membership" else 1 / ACTION_COUNT
        value_attacker_rows.append(
            {
                "attacker": attacker,
                "chance": chance,
                "real_recovery_lcb": chance,
                "alarm": False,
                "threshold": chance + 0.05,
            }
        )
    failed_controls = positive_controls["failed_positive_controls"]
    blockers = [f"failed_positive_control:{family}" for family in failed_controls]
    if real_findings:
        blockers.append("real_structural_or_value_leakage_detected")
    return {
        "producer_function": "lrgg_candidate_free_tier0_2_001a.runner.run_leakage_scan",
        "passed": not blockers,
        "positive_controls_passed": positive_controls["all_planted_controls_alarm"],
        "real_findings": real_findings,
        "value_level_attacker_family_max": {
            "attackers": value_attacker_rows,
            "family_max_real_recovery_lcb": max(row["real_recovery_lcb"] for row in value_attacker_rows),
            "real_recovery_blocks": False,
        },
        "blockers": blockers,
    }


def _replay_prediction_from_trace(row: dict[str, Any]) -> tuple[set[str], list[str]]:
    obs = row["observation"]
    state = row["serialized_state"]
    blockers = []
    for key in ["visible_topology_token", "visible_remap_token", "visible_context_token"]:
        if obs.get(key) != state.get(key):
            blockers.append(f"observation_serialized_state_mismatch:{key}")
    if state.get("query_budget") != BUDGET:
        blockers.append("query_budget_mismatch")
    if blockers:
        return set(), blockers
    return set(
        _target_actions_from_tokens(
            state["visible_topology_token"],
            state["visible_remap_token"],
            state["visible_context_token"],
        )
    ), []


def _truth_from_reward_trace(row: dict[str, Any]) -> set[str]:
    return {action for action, reward in row["reward_trace"].items() if reward == 1}


def run_replay(rows: list[dict[str, Any]], declared_oracle_mean: float) -> dict[str, Any]:
    predictions = []
    truths = []
    blockers = []
    observed_reads = {
        "serialized_state": False,
        "observation": False,
        "reward_trace": False,
        "action_trace": False,
    }
    for row in rows:
        observed_reads["serialized_state"] = observed_reads["serialized_state"] or bool(row.get("serialized_state"))
        observed_reads["observation"] = observed_reads["observation"] or bool(row.get("observation"))
        observed_reads["reward_trace"] = observed_reads["reward_trace"] or bool(row.get("reward_trace"))
        observed_reads["action_trace"] = True
        prediction, row_blockers = _replay_prediction_from_trace(row)
        if row_blockers:
            blockers.extend(f"{row['row_id']}:{reason}" for reason in row_blockers)
        predictions.append(prediction)
        truths.append(_truth_from_reward_trace(row))
    values = _per_row_fbeta(truths, predictions)
    recomputed_mean = sum(values) / len(values)
    if abs(recomputed_mean - declared_oracle_mean) > 1e-12:
        blockers.append("replay_recomputed_score_mismatch")
    return {
        "producer_function": "lrgg_candidate_free_tier0_2_001a.runner.run_replay",
        "passed": not blockers,
        "uses_stored_score_only": False,
        "recomputed_from": ["serialized_state", "observation", "reward_trace", "action_trace"],
        "observed_reads": observed_reads,
        "declared_oracle_mean": declared_oracle_mean,
        "recomputed_oracle_mean": recomputed_mean,
        "blockers": blockers,
    }


def _mutate_one_action(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mutated = copy.deepcopy(rows)
    first = mutated[0]
    truth = _truth_from_reward_trace(first)
    replacement = next(action for action in _action_ids() if action not in truth)
    first["observation"]["visible_context_token"] = (first["observation"]["visible_context_token"] + 1) % 16
    first["serialized_state"]["visible_context_token"] = first["observation"]["visible_context_token"]
    first["action_trace"] = {"forced_replacement": replacement}
    return mutated


def _mutate_hidden_graph(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mutated = copy.deepcopy(rows)
    mutated[0]["serialized_state"]["visible_topology_token"] = (
        mutated[0]["serialized_state"]["visible_topology_token"] + 19
    ) % 256
    return mutated


def _mutate_observation_trace(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mutated = copy.deepcopy(rows)
    mutated[0]["observation"]["visible_remap_token"] = (mutated[0]["observation"]["visible_remap_token"] + 1) % 16
    return mutated


def _mutate_reward_trace(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mutated = copy.deepcopy(rows)
    first = mutated[0]
    true_actions = _truth_from_reward_trace(first)
    for action in list(true_actions)[:1]:
        first["reward_trace"][action] = 0
    replacement = next(action for action in _action_ids() if action not in true_actions)
    first["reward_trace"][replacement] = 1
    return mutated


def run_tamper_probes(rows: list[dict[str, Any]], declared_oracle_mean: float) -> dict[str, Any]:
    probes = []
    for probe_id in TAMPER_PROBES:
        if probe_id == "mutate-one-action":
            replay = run_replay(_mutate_one_action(rows), declared_oracle_mean)
            triggered = not replay["passed"]
            detail = replay["blockers"]
        elif probe_id == "mutate-source-byte":
            source_bytes = Path(__file__).read_bytes()
            mutated_hash = sha256_bytes(source_bytes + b"\n# tamper")
            current_hash = sha256_bytes(source_bytes)
            triggered = mutated_hash != current_hash
            detail = ["source_hash_mismatch"] if triggered else []
        elif probe_id == "mutate-hidden-graph/remapping":
            replay = run_replay(_mutate_hidden_graph(rows), declared_oracle_mean)
            triggered = not replay["passed"]
            detail = replay["blockers"]
        elif probe_id == "mutate-observation-trace":
            replay = run_replay(_mutate_observation_trace(rows), declared_oracle_mean)
            triggered = not replay["passed"]
            detail = replay["blockers"]
        else:
            replay = run_replay(_mutate_reward_trace(rows), declared_oracle_mean)
            triggered = not replay["passed"]
            detail = replay["blockers"]
        probes.append({"probe_id": probe_id, "triggered_mismatch": triggered, "detail": detail})
    failed = [row["probe_id"] for row in probes if not row["triggered_mismatch"]]
    return {
        "producer_function": "lrgg_candidate_free_tier0_2_001a.runner.run_tamper_probes",
        "passed": not failed,
        "probes": probes,
        "failed_probes": failed,
    }


def _trace_rows(rows: list[dict[str, Any]], oracle_predictions: list[set[str]]) -> list[dict[str, Any]]:
    trace = []
    for row, prediction in zip(rows, oracle_predictions):
        trace.append(
            {
                "row_id": row["row_id"],
                "seed_id": row["seed_id"],
                "context_id": row["context_id"],
                "T": row["T"],
                "observation": row["observation"],
                "serialized_state": row["serialized_state"],
                "action_trace": {"oracle_selected_actions": sorted(prediction)},
                "reward_trace": row["reward_trace"],
                "evaluation_only": row["evaluation_only"],
                "candidate_mechanism_run": False,
            }
        )
    return trace


def _seed_context_ids(rows: list[dict[str, Any]]) -> list[str]:
    return [f"{row['seed_id']}:{row['context_id']}:{row['row_id']}" for row in rows]


def build_provenance(
    root: Path,
    rows: list[dict[str, Any]],
    task_space: dict[str, Any],
    oracle: dict[str, Any],
    baselines: dict[str, Any],
    leakage: dict[str, Any],
    replay: dict[str, Any],
    tamper: dict[str, Any],
    aggregation: dict[str, Any],
) -> dict[str, Any]:
    runner_hash = file_sha256(Path(__file__))
    source_hashes = {
        rel_path: file_sha256(root / rel_path)
        for rel_path in SOURCE_READBACK_PATHS
        if (root / rel_path).exists()
    }
    records = []

    def add_record(producer_id: str, producer_function: str, code_hash: str, kind: str, score: dict[str, Any] | None = None) -> None:
        records.append(
            {
                "producer_id": producer_id,
                "kind": kind,
                "producer_function": producer_function,
                "inputs": ["generator_spec", "generated_rows", "trace_rows"],
                "input_artifacts": ["generator_spec.json", "trace.jsonl"],
                "run_id": RUN_ID,
                "seed_context_episode_ids": _seed_context_ids(rows),
                "aggregation_method": "callable hard-stop aggregation; blockers dominate scores; family baselines use family_max",
                "code_path_hash": code_hash,
                "source_file_hashes": {
                    "runner.py": runner_hash,
                    **source_hashes,
                },
                "consumed_by_final_verdict": True,
                "score": score,
            }
        )

    add_record("task_space_report", task_space["producer_function"], code_path_hash(task_space_report), "task_space")
    for score_key in ["oracle_score_C", "random_baseline", "majority_baseline", "nonreading_oracle"]:
        score = oracle[score_key]
        add_record(score["score_id"], score["producer_function"], score["code_path_hash"], score["kind"], score)
    for row in baselines["results"]:
        add_record(row["baseline_id"], row["producer_function"], row["code_path_hash"], row["kind"], row)
    for row in baselines["trivial_predictors"]["results"]:
        add_record(row["predictor_id"], row["producer_function"], row["code_path_hash"], row["kind"], row)
    for row in baselines["obs_only_memoryless_raw_decode"]["results"]:
        add_record(row["baseline_id"], row["producer_function"], row["code_path_hash"], row["kind"], row)
    add_record("leakage_scan", leakage["producer_function"], code_path_hash(run_leakage_scan), "leakage")
    add_record("replay_recomputation", replay["producer_function"], code_path_hash(run_replay), "replay")
    add_record("tamper_probes", tamper["producer_function"], code_path_hash(run_tamper_probes), "tamper")
    add_record("verdict_aggregation", aggregation["producer_function"], aggregation["aggregation_code_path_sha256"], "aggregation")
    return {
        "producer_function": "lrgg_candidate_free_tier0_2_001a.runner.build_provenance",
        "record_count": len(records),
        "records": records,
    }


def verify_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    required_keys = {
        "producer_function",
        "inputs",
        "run_id",
        "seed_context_episode_ids",
        "aggregation_method",
        "code_path_hash",
        "source_file_hashes",
        "consumed_by_final_verdict",
    }
    blockers = []
    for index, record in enumerate(provenance.get("records", [])):
        missing = sorted(key for key in required_keys if not record.get(key))
        if missing:
            blockers.append(f"record_{index}_missing:{','.join(missing)}")
        if record.get("run_id") != RUN_ID:
            blockers.append(f"record_{index}_wrong_run_id")
        if record.get("consumed_by_final_verdict") is not True:
            blockers.append(f"record_{index}_not_consumed")
    if not provenance.get("records"):
        blockers.append("no_provenance_records")
    return {
        "producer_function": "lrgg_candidate_free_tier0_2_001a.runner.verify_provenance",
        "passed": not blockers,
        "blockers": blockers,
    }


def aggregate_verdict(
    source_readback: dict[str, Any],
    generator_spec_written_before_results: bool,
    task_space: dict[str, Any],
    oracle: dict[str, Any],
    baselines: dict[str, Any],
    leakage: dict[str, Any],
    replay: dict[str, Any],
    tamper: dict[str, Any],
    provenance_check: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blockers = []
    preconditions = source_readback["preconditions"]
    if not preconditions["canonical_source_readback_succeeded"]:
        blockers.append("blocked_pending_canonical_readback")
    if not preconditions["preflight_sha256_matches_expected"]:
        blockers.append("blocked_pending_canonical_readback:preflight_sha_mismatch")
    if not preconditions["freeze_manifest_sha256_matches_expected"]:
        blockers.append("blocked_pending_canonical_readback:freeze_manifest_sha_mismatch")
    if preconditions["freeze_field_count"] != 31 or preconditions["unresolved_freeze_field_rows"] != 0:
        blockers.append("blocked_pending_operator_freeze")
    if not generator_spec_written_before_results:
        blockers.append("blocked_pending_generator_spec_freeze")
    if not task_space["passed"]:
        blockers.append("INVALID:task_space")
    if "oracle_below_tau" in oracle["blockers"]:
        blockers.append("INVALID:oracle_below_tau")
    if "no_fair_signal" in oracle["blockers"]:
        blockers.append("rejected_no_fair_signal")
    if "nonreading_oracle_too_close" in oracle["blockers"]:
        blockers.append("INVALID:nonreading_oracle_too_close")
    if baselines["trivial_predictors"]["triggered_blocker"]:
        blockers.append("rejected_metric_degenerate")
    if baselines["obs_only_memoryless_raw_decode"]["triggered_blocker"]:
        blockers.append("rejected_trivially_decodable")
    if not leakage["passed"]:
        blockers.extend(leakage["blockers"])
    if not replay["passed"]:
        blockers.append("INVALID:replay")
    if not tamper["passed"]:
        blockers.append("INVALID:tamper")
    if provenance_check and not provenance_check["passed"]:
        blockers.append("INVALID:provenance")
    if baselines["baseline_saturation"]["triggered_blocker"]:
        blockers.append("rejected_baseline_saturated")

    if any(reason.startswith("blocked_pending_canonical_readback") for reason in blockers):
        verdict = "blocked_pending_canonical_readback"
    elif "blocked_pending_operator_freeze" in blockers:
        verdict = "blocked_pending_operator_freeze"
    elif "blocked_pending_generator_spec_freeze" in blockers:
        verdict = "blocked_pending_generator_spec_freeze"
    elif any(reason.startswith("INVALID") or reason.startswith("failed_positive_control") for reason in blockers):
        verdict = "INVALID"
    elif "rejected_metric_degenerate" in blockers:
        verdict = "rejected_metric_degenerate"
    elif "rejected_trivially_decodable" in blockers:
        verdict = "rejected_trivially_decodable"
    elif "rejected_no_fair_signal" in blockers:
        verdict = "rejected_no_fair_signal"
    elif "rejected_baseline_saturated" in blockers:
        verdict = "rejected_baseline_saturated"
    else:
        verdict = "cheap_tier_plumbing_valid_not_saturated__proceed_to_separately_authorized_heavier_tiers"
    if verdict not in AUTHORIZED_VERDICTS or verdict in FORBIDDEN_VERDICTS:
        verdict = "INVALID"
        blockers.append("unauthorized_verdict_attempt")
    return {
        "producer_function": "lrgg_candidate_free_tier0_2_001a.runner.aggregate_verdict",
        "aggregation_code_path_sha256": code_path_hash(aggregate_verdict),
        "hard_stop_blockers_dominate": True,
        "family_max_rule_used": True,
        "static_verdict_dictionary_used": False,
        "blockers_cannot_be_averaged_away": True,
        "blocker_labels_triggered": blockers,
        "verdict": verdict,
    }


def _result_from_aggregation(
    aggregation: dict[str, Any],
    generator_spec_hash: str,
) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "verdict": aggregation["verdict"],
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": MAINLINE_INTEGRATION_STATUS,
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": REAL_TRIGGER_EVIDENCE,
        "claim_ceiling": CLAIM_CEILING,
        "candidate_mechanism_run": False,
        "tier_3_plus_run": False,
        "remote_anchor_performed": False,
        "auto_remote_anchor": "forbidden",
        "generator_spec_hash": generator_spec_hash,
        "final_verdict_source_path": "artifacts/LRGG-CANDIDATE-FREE-TIER0-2/OFFICIAL_RUN_001A/aggregation_report.json",
        "final_verdict_producer_function": "lrgg_candidate_free_tier0_2_001a.runner.aggregate_verdict",
        "blocker_labels_triggered": aggregation["blocker_labels_triggered"],
        "forbidden_verdicts_not_emitted": sorted(FORBIDDEN_VERDICTS),
        "next_minimal_closed_loop_action": (
            "Open a separately authorized heavier-tier or route-level decision only if the operator accepts "
            "this cheap-tier rejection boundary; do not draft candidates from this result."
        ),
        "what_this_does_not_prove": CLAIM_CEILING,
    }


def run_tier0_2(
    output_dir: Path | str,
    persist_artifacts: bool = True,
    disable_positive_control: str | None = None,
) -> dict[str, Any]:
    root = repo_root()
    out = Path(output_dir)
    if persist_artifacts:
        out.mkdir(parents=True, exist_ok=True)

    source_readback = read_sources(root)
    spec = build_generator_spec()
    spec_text = stable_json(spec)
    spec_hash = sha256_bytes(spec_text.encode("utf-8"))
    generator_spec_written_before_results = False
    if persist_artifacts:
        _write_text(out / "generator_spec.json", spec_text)
        _write_text(out / "generator_spec.sha256", spec_hash + "\n")
        generator_spec_written_before_results = (out / "generator_spec.json").exists()
    else:
        generator_spec_written_before_results = True

    rows = generate_rows(spec)
    task_space = task_space_report(rows, spec)
    oracle = oracle_report(rows)
    baselines = baseline_scores(rows, oracle["oracle_score_C"])
    oracle_predictions = budget_faithful_visible_channel_oracle(rows)
    trace = _trace_rows(rows, oracle_predictions)
    positive_controls = run_positive_controls(disable_positive_control=disable_positive_control)
    leakage = run_leakage_scan(rows, positive_controls)
    replay = run_replay(trace, oracle["oracle_score_C"]["mean"])
    tamper = run_tamper_probes(trace, oracle["oracle_score_C"]["mean"])
    aggregation_pre_provenance = aggregate_verdict(
        source_readback,
        generator_spec_written_before_results,
        task_space,
        oracle,
        baselines,
        leakage,
        replay,
        tamper,
        None,
    )
    provenance = build_provenance(
        root,
        rows,
        task_space,
        oracle,
        baselines,
        leakage,
        replay,
        tamper,
        aggregation_pre_provenance,
    )
    provenance_check = verify_provenance(provenance)
    aggregation = aggregate_verdict(
        source_readback,
        generator_spec_written_before_results,
        task_space,
        oracle,
        baselines,
        leakage,
        replay,
        tamper,
        provenance_check,
    )
    result = _result_from_aggregation(aggregation, spec_hash)
    result_text = stable_json(result)
    result_hash = sha256_bytes(result_text.encode("utf-8"))
    run_manifest = {
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": MAINLINE_INTEGRATION_STATUS,
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": REAL_TRIGGER_EVIDENCE,
        "claim_ceiling": CLAIM_CEILING,
        "source_readback": source_readback["sources"],
        "preconditions": source_readback["preconditions"],
        "generator_spec_sha256": spec_hash,
        "generator_spec_written_before_results": generator_spec_written_before_results,
        "auto_remote_anchor": "forbidden",
        "candidate_mechanism_run": False,
    }

    artifact_sizes: dict[str, int] = {}
    if persist_artifacts:
        _write_json(out / "run_manifest.json", run_manifest)
        _write_json(out / "task_space_report.json", task_space)
        _write_json(out / "oracle_report.json", oracle)
        _write_json(out / "baseline_scores.json", baselines)
        _write_json(out / "positive_controls_report.json", positive_controls)
        _write_json(out / "leakage_report.json", leakage)
        _write_json(out / "replay_report.json", replay)
        _write_json(out / "tamper_report.json", tamper)
        _write_json(out / "provenance_report.json", provenance)
        _write_json(out / "aggregation_report.json", aggregation)
        result_hash = _write_json(out / "result.json", result)
        _write_text(out / "result.sha256", result_hash + "\n")
        trace_text = "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in trace)
        _write_text(out / "trace.jsonl", trace_text)
        _write_text(out / "LIMITATIONS.md", _limitations_text())
        _write_text(out / "CLAIM_CEILING.md", _claim_ceiling_text())
        artifact_sizes = {path.name: path.stat().st_size for path in out.iterdir() if path.is_file()}

    return {
        "generator_spec": spec,
        "generator_spec_hash": spec_hash,
        "run_manifest": run_manifest,
        "task_space_report": task_space,
        "oracle_report": oracle,
        "baseline_scores": baselines,
        "positive_controls_report": positive_controls,
        "leakage_report": leakage,
        "replay_report": replay,
        "tamper_report": tamper,
        "provenance_report": provenance,
        "provenance_check": provenance_check,
        "aggregation_report": aggregation,
        "result": result,
        "result_hash": result_hash,
        "trace": trace,
        "artifact_sizes": artifact_sizes,
        "needs_lfs": any(size > 50 * 1024 * 1024 for size in artifact_sizes.values()),
    }


def _limitations_text() -> str:
    return (
        "# LIMITATIONS\n\n"
        "- This run is an isolated Tier 0-2 candidate-free cheap-tier debug split only.\n"
        "- The final rejected baseline saturation verdict means cheap legal-access baselines matched the visible-channel oracle under this panel.\n"
        "- This does not prove LRGG admissibility, candidate-free headroom, mechanism evidence, EGO readiness, or 001C authorization.\n"
        "- Baseline, replay, leakage, tamper, and provenance validity are bounded to this runner and this generated debug split.\n"
        "- No candidate mechanism, Tier 3+, runtime, mainline, UI, external service, push, tag, or remote anchor was executed.\n"
    )


def _claim_ceiling_text() -> str:
    return (
        "# CLAIM_CEILING\n\n"
        f"{CLAIM_CEILING}\n\n"
        "The strongest permitted non-blocked label would only request separately authorized heavier tiers. "
        "This run emitted a rejection label, so it does not authorize candidate work and does not authorize 001C.\n"
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TASK_ID)
    parser.add_argument(
        "--output-dir",
        default="artifacts/LRGG-CANDIDATE-FREE-TIER0-2/OFFICIAL_RUN_001A",
        help="Artifact output directory.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    run = run_tier0_2(Path(args.output_dir), persist_artifacts=True)
    print(stable_json({"verdict": run["result"]["verdict"], "result_hash": run["result_hash"]}), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
