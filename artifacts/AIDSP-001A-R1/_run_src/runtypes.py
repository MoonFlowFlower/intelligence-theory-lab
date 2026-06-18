"""Shared per-episode record types so M1/M2/dwell are computed uniformly across
the candidate and every baseline (no per-agent metric code paths)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class StepRecord:
    t: int
    pos: int
    action: int
    action_dist: List[float]            # distribution over actions (one-hot if deterministic)
    cue: int
    at_food: int
    energy: int
    in_dark_room: bool
    in_noisy_tv: bool
    cum_cost: float
    # candidate / model-based only (None for model-free baselines)
    belief_food_before: Optional[List[float]] = None
    efe_pragmatic: Optional[List[float]] = None    # per action
    efe_epistemic: Optional[List[float]] = None    # per action
    neg_efe_G: Optional[List[float]] = None        # per action
    pred_cue_dist: Optional[List[float]] = None     # predicted cue dist for chosen action
    pred_error: Optional[float] = None
    belief_food_after: Optional[List[float]] = None


@dataclass
class EpisodeRun:
    agent: str
    seed: int
    food: int
    mode: str
    steps: List[StepRecord] = field(default_factory=list)
    # observation stream for the INDEPENDENT estimator: (cue, pos, at_food)
    observations: List[Tuple[int, int, int]] = field(default_factory=list)

    def action_dists(self) -> List[List[float]]:
        return [s.action_dist for s in self.steps]

    def positions(self) -> List[int]:
        return [s.pos for s in self.steps]
