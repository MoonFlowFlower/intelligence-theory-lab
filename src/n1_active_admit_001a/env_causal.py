from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable

import numpy as np

from . import BASE_SEED

ENV_NAME = "E_causal"
K_SLOTS = 4
N_OBS = 64
BUDGET = 1
TRAIN_J = (0, 1)
HELDOUT_J = (2, 3)
DIAG_OUTCOME = {1: 0.9, 0: 0.1}
NONDIAG_OUTCOME = 0.5


def derive_seed(*parts: object, base_seed: int = BASE_SEED) -> int:
    payload = json.dumps([base_seed, *parts], separators=(",", ":"), sort_keys=True)
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


@dataclass(frozen=True)
class CausalStructure:
    structure_id: int
    m: int
    j: int


@dataclass(frozen=True)
class CausalEpisode:
    env: str
    seed_index: int
    structure: CausalStructure
    observation: np.ndarray

    @property
    def structure_id(self) -> int:
        return self.structure.structure_id

    @property
    def y_star(self) -> int:
        return self.structure.m


def enumerate_structures() -> list[CausalStructure]:
    structures: list[CausalStructure] = []
    structure_id = 0
    for m_value in (0, 1):
        for diagnostic_slot in range(K_SLOTS):
            structures.append(
                CausalStructure(
                    structure_id=structure_id,
                    m=m_value,
                    j=diagnostic_slot,
                )
            )
            structure_id += 1
    return structures


def split_structures(split: str) -> list[CausalStructure]:
    if split == "train":
        allowed = set(TRAIN_J)
    elif split == "heldout":
        allowed = set(HELDOUT_J)
    else:
        raise ValueError(f"unknown split: {split}")
    return [structure for structure in enumerate_structures() if structure.j in allowed]


class CausalEnv:
    def __init__(self, base_seed: int = BASE_SEED):
        self.base_seed = base_seed
        self.structures = enumerate_structures()

    def sample_episode(self, structure_index: int, seed_index: int) -> CausalEpisode:
        structure = self.structures[structure_index]
        rng = np.random.default_rng(
            derive_seed(ENV_NAME, structure_index, seed_index, "observation", base_seed=self.base_seed)
        )
        observation = rng.binomial(n=1, p=0.5, size=(N_OBS, K_SLOTS)).astype(np.int8)
        return CausalEpisode(
            env=ENV_NAME,
            seed_index=seed_index,
            structure=structure,
            observation=observation,
        )

    def intervene(self, episode: CausalEpisode, slot: int) -> int:
        if slot not in range(K_SLOTS):
            raise ValueError(f"slot outside [0,{K_SLOTS - 1}]: {slot}")
        if slot == episode.structure.j:
            p_outcome = DIAG_OUTCOME[episode.structure.m]
        else:
            p_outcome = NONDIAG_OUTCOME
        rng = np.random.default_rng(
            derive_seed(
                ENV_NAME,
                episode.structure_id,
                episode.seed_index,
                "intervention",
                slot,
                base_seed=self.base_seed,
            )
        )
        return int(rng.binomial(n=1, p=p_outcome))

    def audit_rows(self) -> list[dict[str, int]]:
        return [
            {"structure_id": structure.structure_id, "m": structure.m, "j": structure.j}
            for structure in self.structures
        ]


def passive_observation_distribution_is_constant(structures: Iterable[CausalStructure]) -> bool:
    return all(structure.m in (0, 1) and structure.j in range(K_SLOTS) for structure in structures)

