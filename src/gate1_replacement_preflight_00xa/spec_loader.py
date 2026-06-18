from __future__ import annotations

import hashlib
import inspect
import json
from copy import deepcopy
from pathlib import Path

from .metrics import EQUIVALENCE_BAND, PER_CLASS_FLOOR
from .readback import (
    EXPECTED_SURFACE_SPEC_SHA256,
    GENERATOR_SOURCE_PATH,
    SURFACE_FREEZE_PATH,
    SURFACE_SPEC_PATH,
    file_sha256,
)


def load_surface_spec(repo_root: str | Path) -> dict:
    root = Path(repo_root)
    spec_path = root / SURFACE_SPEC_PATH
    freeze_path = root / SURFACE_FREEZE_PATH
    spec_text = spec_path.read_text(encoding="utf-8")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    required_phrases = [
        "Target variable:",
        "Primary metric: macro F1",
        "equivalence band: 0.03 macro F1",
        "Future implementer mutation ban",
        "Baseline Panel Registry",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in spec_text]
    spec_hash = file_sha256(spec_path)
    return {
        "schema_version": "gate1_replacement_preflight_00xa_surface_readback_v1",
        "surface_spec_id": freeze.get("surface_spec_id"),
        "spec_path": SURFACE_SPEC_PATH,
        "freeze_path": SURFACE_FREEZE_PATH,
        "spec_sha256": spec_hash,
        "expected_spec_sha256": EXPECTED_SURFACE_SPEC_SHA256,
        "freeze_recorded_spec_sha256": freeze.get("spec_sha256"),
        "hash_matches_expected": spec_hash == EXPECTED_SURFACE_SPEC_SHA256,
        "hash_matches_freeze": spec_hash == freeze.get("spec_sha256"),
        "author_source": freeze.get("author_source"),
        "freeze_timestamp": freeze.get("freeze_timestamp"),
        "canonical_readback_channel": freeze.get("canonical_readback_channel"),
        "future_preflight_implementer_may_mutate_spec": freeze.get("future_preflight_implementer_may_mutate_spec"),
        "metric_contract": {
            "primary_metric": "macro_f1",
            "beta": 1.0,
            "reports_precision": True,
            "reports_recall": True,
            "equivalence_band": EQUIVALENCE_BAND,
            "per_class_floor": PER_CLASS_FLOOR,
        },
        "required_phrase_gaps": missing,
        "valid": not missing and spec_hash == EXPECTED_SURFACE_SPEC_SHA256,
        "producer_function": "gate1_replacement_preflight_00xa.spec_loader.load_surface_spec",
        "input_artifacts": [SURFACE_SPEC_PATH, SURFACE_FREEZE_PATH],
        "aggregation_rule": "markdown_freeze_json_required_field_readback",
        "consumed_by_final_verdict": True,
    }


def _target_for_seed(seed: int) -> bool:
    return seed % 4 in (0, 1)


def _weak_hint(seed: int, target: bool) -> bool:
    return target if seed % 5 in (0, 1, 2) else not target


def _legal_votes(seed: int, target: bool) -> list[bool]:
    votes = []
    for idx in range(16):
        votes.append(target if (seed + idx) % 8 != 0 else not target)
    return votes


def _function_source_hash(func) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def _source_pin_sha256(source_readback: dict, source_path: str) -> str | None:
    for row in source_readback.get("source_pins", []):
        if row.get("path") == source_path:
            return row.get("sha256")
    return None


def build_generator_provenance(repo_root: str | Path, source_readback: dict, run_id: str) -> dict:
    root = Path(repo_root)
    source_path = root / GENERATOR_SOURCE_PATH
    generator_source_hash = file_sha256(source_path) if source_path.exists() else None
    source_pin_sha256 = _source_pin_sha256(source_readback, GENERATOR_SOURCE_PATH)
    return {
        "schema_version": "gate1_replacement_preflight_00xa_generator_provenance_v1",
        "run_id": run_id,
        "generator_id": "gate1_replacement_preflight_00xa_candidate_free_generator",
        "generator_source_path": GENERATOR_SOURCE_PATH,
        "generator_source_hash": generator_source_hash,
        "source_pin_sha256": source_pin_sha256,
        "source_pin_integrity": bool(generator_source_hash and generator_source_hash == source_pin_sha256),
        "generator_version_or_code_path_hash": _function_source_hash(build_candidate_free_surface_bundle),
        "producer_function": "gate1_replacement_preflight_00xa.spec_loader.build_candidate_free_surface_bundle",
        "fair_baseline_access": "same_candidate_free_visible_state_legal_channel_and_fixed_budget",
        "hidden_target_storage": "episode.hidden_target stored outside visible_state; fair baselines and candidates receive no hidden-target field",
        "no_candidate_authored_truth": True,
        "candidate_access": False,
        "candidate_authored_truth": False,
        "readback_channels": ["canonical_file_api_read_bytes", "canonical_source_pin_readback"],
        "self_readback_only": False,
        "input_artifacts": [GENERATOR_SOURCE_PATH, "source_readback.json"],
        "aggregation_rule": "generator_source_hash_must_match_canonical_source_pin",
        "consumed_by_final_verdict": True,
    }


def build_candidate_free_surface_bundle(
    run_id: str,
    seeds: range | list[int] | None = None,
    generator_source_hash: str | None = None,
) -> dict:
    seed_list = list(seeds if seeds is not None else range(4001, 4041))
    episodes = []
    for seed in seed_list:
        target = _target_for_seed(seed)
        hint = _weak_hint(seed, target)
        votes = _legal_votes(seed, target)
        episode_id = f"surface-{seed}"
        passive_value = 0.64 if hint else 0.36
        episodes.append(
            {
                "surface_id": "gate1_replacement_surface_spec_00xa",
                "episode_id": episode_id,
                "seed": seed,
                "split": "test",
                "hidden_target": target,
                "visible_state": {
                    "context_fields": {"cohort": seed % 7, "phase": seed % 3},
                    "observable_features": {
                        "weak_hint": hint,
                        "passive_value": passive_value,
                        "passive_variance_proxy": abs(passive_value - 0.5),
                        "passive_correlation_proxy": (seed % 11) / 10,
                    },
                    "legal_channel_metadata": {
                        "budget": 16,
                        "channel_count": 16,
                        "candidate_access": False,
                    },
                },
                "legal_actions": [
                    {
                        "action_id": f"q{idx:02d}",
                        "action_type": "query_legal_channel" if idx % 2 else "probe_visible_transition",
                        "budget_cost": 1,
                        "visible_inputs": {"slot": idx, "cohort": seed % 7},
                    }
                    for idx in range(16)
                ],
                "legal_channel_responses": [
                    {
                        "query_id": f"{episode_id}-q{idx:02d}",
                        "allowed_response_fields": ["legal_channel_observation"],
                        "legal_channel_observation": vote,
                    }
                    for idx, vote in enumerate(votes)
                ],
                "provenance": {
                    "generator_id": "gate1_replacement_preflight_00xa_candidate_free_generator",
                    "generator_source_hash": generator_source_hash or "sha256-or-blocked",
                    "seed": seed,
                    "candidate_access": False,
                    "source_artifacts": ["src/gate1_replacement_preflight_00xa/spec_loader.py"],
                },
            }
        )
    return {
        "schema_version": "gate1_replacement_preflight_00xa_bundle_v1",
        "run_id": run_id,
        "surface_id": "gate1_replacement_surface_spec_00xa",
        "candidate_access": False,
        "episodes": episodes,
        "seed_policy": {
            "split": "test",
            "seeds": seed_list,
            "predeclared_range": "4001..4099",
            "unused_frozen_seed_claim": "not_claimed_all_4001_4099_used",
        },
        "fixed_budget": {"max_total_queries_per_episode": 16},
    }


def visible_bundle(bundle: dict) -> dict:
    clone = {"run_id": bundle["run_id"], "surface_id": bundle["surface_id"], "episodes": []}
    for episode in bundle["episodes"]:
        clone["episodes"].append(
            {
                "episode_id": episode["episode_id"],
                "seed": episode["seed"],
                "split": episode["split"],
                "visible_state": deepcopy(episode["visible_state"]),
                "legal_actions": deepcopy(episode["legal_actions"]),
                "provenance": {
                    "generator_id": episode["provenance"]["generator_id"],
                    "candidate_access": False,
                    "source_artifacts": episode["provenance"]["source_artifacts"],
                },
            }
        )
    return clone
