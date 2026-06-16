from __future__ import annotations

from copy import deepcopy
from math import ceil
from typing import Any


ACTIONS = ["probe", "shield", "repair", "defer"]
ACTION_DELTAS = {"probe": 0, "shield": 1, "repair": 3, "defer": 5}
FACTOR_FAMILIES = {
    "signal_family": {
        "observation_key": "signal_code",
        "seen": set(range(0, 6)),
        "unseen": set(range(6, 10)),
    },
    "topology_family": {
        "observation_key": "topology_code",
        "seen": set(range(0, 4)),
        "unseen": set(range(4, 6)),
    },
    "risk_family": {
        "observation_key": "risk_code",
        "seen": set(range(0, 5)),
        "unseen": set(range(5, 8)),
    },
    "phase_family": {
        "observation_key": "phase_code",
        "seen": set(range(0, 3)),
        "unseen": set(range(3, 5)),
    },
}


def truth_for(episode: dict[str, Any], action: str) -> dict[str, int]:
    observation = episode["observation"]
    signal = int(observation["signal_code"])
    topology = int(observation["topology_code"])
    risk = int(observation["risk_code"])
    phase = int(observation["phase_code"])
    action_delta = ACTION_DELTAS[action]
    boundary = (1 + (2 * signal) + (3 * topology) + (4 * risk) + (5 * phase) + action_delta) % 7
    viability_raw = (2 + signal + (2 * topology) + (3 * risk) + phase + action_delta) % 5
    viability = 1 if viability_raw in {0, 2} else 0
    return {"boundary_state": boundary, "viability_state": viability}


def _episode(
    *,
    seed: int,
    split: str,
    index: int,
    signal: int,
    topology: int,
    risk: int,
    phase: int,
) -> dict[str, Any]:
    action = ACTIONS[(seed + index) % len(ACTIONS)]
    counterfactual_actions = [candidate for candidate in ACTIONS if candidate != action][:2]
    observation = {
        "signal_code": signal,
        "topology_code": topology,
        "risk_code": risk,
        "phase_code": phase,
        "available_actions": list(ACTIONS),
    }
    episode = {
        "seed": seed,
        "split": split,
        "context_id": f"{split}.ctx.{seed}.{index:03d}",
        "episode_id": f"{split}.ep.{seed}.{index:03d}",
        "observation": observation,
        "chosen_action": action,
        "counterfactual_actions": counterfactual_actions,
    }
    episode["truth_by_action"] = {
        candidate_action: truth_for(episode, candidate_action)
        for candidate_action in ACTIONS
    }
    return episode


def _training_episodes(seed: int) -> list[dict[str, Any]]:
    episodes = []
    index = 0
    for signal in range(0, 6):
        for topology in range(0, 4):
            for risk in range(0, 5):
                phase = (signal + topology + risk + seed) % 3
                episodes.append(
                    _episode(
                        seed=seed,
                        split="train",
                        index=index,
                        signal=signal,
                        topology=topology,
                        risk=risk,
                        phase=phase,
                    )
                )
                index += 1
    return episodes


def _heldout_values(seed: int, index: int) -> tuple[int, int, int, int]:
    unseen_family = index % 4
    signal = 6 + ((seed + index) % 4) if unseen_family == 0 else (seed + index) % 6
    topology = 4 + ((seed + index) % 2) if unseen_family == 1 else (seed + index) % 4
    risk = 5 + ((seed + index) % 3) if unseen_family == 2 else (seed + index) % 5
    phase = 3 + ((seed + index) % 2) if unseen_family == 3 else (seed + index) % 3
    return signal, topology, risk, phase


def generate_distribution(seed: int, heldout_count: int = 128) -> dict[str, Any]:
    train = _training_episodes(seed)
    heldout = []
    for index in range(heldout_count):
        signal, topology, risk, phase = _heldout_values(seed, index)
        heldout.append(
            _episode(
                seed=seed,
                split="heldout",
                index=index,
                signal=signal,
                topology=topology,
                risk=risk,
                phase=phase,
            )
        )
    return {
        "seed": seed,
        "train": train,
        "heldout": heldout,
        "factorization_families": deepcopy(FACTOR_FAMILIES),
    }


def _key(episode: dict[str, Any], action: str) -> tuple[int, int, int, int, str]:
    observation = episode["observation"]
    return (
        int(observation["signal_code"]),
        int(observation["topology_code"]),
        int(observation["risk_code"]),
        int(observation["phase_code"]),
        action,
    )


def distribution_manifest(dataset: dict[str, Any]) -> dict[str, Any]:
    train = dataset["train"]
    heldout = dataset["heldout"]
    train_keys = {_key(episode, action) for episode in train for action in ACTIONS}
    heldout_keys = [_key(episode, episode["chosen_action"]) for episode in heldout]
    unseen_rows = []
    ratios: dict[str, float] = {}
    counts: dict[str, int] = {}
    for family_name, family in FACTOR_FAMILIES.items():
        key = family["observation_key"]
        count = sum(1 for episode in heldout if int(episode["observation"][key]) in family["unseen"])
        counts[family_name] = count
        ratios[family_name] = round(count / len(heldout), 6) if heldout else 0.0
    for episode in heldout:
        has_unseen = any(
            int(episode["observation"][family["observation_key"]]) in family["unseen"]
            for family in FACTOR_FAMILIES.values()
        )
        if has_unseen:
            unseen_rows.append(episode["episode_id"])
    lookup_complete = sum(1 for key in heldout_keys if key in train_keys)
    heldout_count = len(heldout)
    unseen_count = len(unseen_rows)
    required_unseen = max(8, ceil(0.40 * heldout_count))
    return {
        "producer_function": "distribution_manifest",
        "seed": dataset["seed"],
        "train_count": len(train),
        "heldout_count": heldout_count,
        "minimum_heldout_count": 128,
        "unseen_heldout_count": unseen_count,
        "required_unseen_heldout_count": required_unseen,
        "unseen_heldout_ratio": round(unseen_count / heldout_count, 6) if heldout_count else 0.0,
        "lookup_complete_heldout_count": lookup_complete,
        "lookup_complete_heldout_ratio": round(lookup_complete / heldout_count, 6) if heldout_count else 0.0,
        "factorization_families": sorted(FACTOR_FAMILIES),
        "unseen_component_count_by_family": counts,
        "unseen_component_ratio_by_family": ratios,
        "constraints_satisfied": (
            heldout_count >= 128
            and unseen_count >= required_unseen
            and all(ratio >= 0.25 for ratio in ratios.values())
            and (round(lookup_complete / heldout_count, 6) if heldout_count else 1.0) <= 0.75
        ),
        "candidate_authored_truth_keys_present": False,
    }


def combined_distribution_manifest(datasets: list[dict[str, Any]]) -> dict[str, Any]:
    per_seed = [distribution_manifest(dataset) for dataset in datasets]
    return {
        "producer_function": "combined_distribution_manifest",
        "seeds": [dataset["seed"] for dataset in datasets],
        "per_seed": per_seed,
        "all_constraints_satisfied": all(row["constraints_satisfied"] for row in per_seed),
        "minimum_unseen_heldout_ratio": min(row["unseen_heldout_ratio"] for row in per_seed),
        "maximum_lookup_complete_heldout_ratio": max(row["lookup_complete_heldout_ratio"] for row in per_seed),
        "factorization_families": sorted(FACTOR_FAMILIES),
    }
