"""Frozen pre-registration for AIDSP-001A-R1. (Canonical copy == src/aidsp_001a_r1/prereg.py)"""
from __future__ import annotations

import hashlib
import json

TASK_ID = "AIDSP-001A-R1"
SCHEMA_VERSION = "aidsp-001a-r1.evidence.v1"

RING_SIZE = 12
DARK_ROOM_CELL = 4
NOISY_TV_CELL = 8
AGENT_START_CELL = 0
STEP_BUDGET = 24

CUE_CW, CUE_CCW = 0, 1
N_CUE = 2
EPS_CLEAR = 0.10
EPS_FOGGY = 0.40
DARK_ROOM_CONST_CUE = CUE_CW

P_AT_FOOD_DETECT = 0.95
P_AT_FOOD_FALSEPOS = 0.02
N_AT_FOOD = 2

ENERGY_LEVELS = 5
ENERGY_SETPOINT = 4
ENERGY_DECAY_PER_STEP = 1
ENERGY_ON_EAT = 4


def terrain_eps(cell: int) -> float:
    return EPS_CLEAR if (cell % 2 == 0) else EPS_FOGGY


def normal_cells():
    return [c for c in range(RING_SIZE) if c not in (DARK_ROOM_CELL, NOISY_TV_CELL)]


N_EPISODES = 60
SEED_FAMILY_A = list(range(0, N_EPISODES))
SEED_FAMILY_B = list(range(1000, 1000 + N_EPISODES))

N_TRAIN_EPISODES = 400
TRAIN_SEEDS = list(range(5000, 5000 + N_TRAIN_EPISODES))
Q_LEARN_ALPHA = 0.5
Q_LEARN_GAMMA = 0.95
Q_LEARN_EPS = 0.1
COUNT_BONUS_BETA = 1.0

PER_ACTION_COST = 1.0
DELTA_REL = 0.10
DELTA_ABS_FLOOR = 1e-6
TAU_M2_FLOOR = 0.05
TAU_M2_USE = 0.20
CHALLENGER_DWELL_TOL = 0.0

LEAK_MI_FRAC = 0.90
FORBIDDEN_CHANNEL_NAME_SUBSTR = ("food_loc", "food_true", "oracle",
                                 "special_label", "darkroom_label", "tv_label")

EFE_GAMMA = 16.0
EFE_POLICY_LEN = 1

CLAIM_CEILING = (
    "A pass = the EFE epistemic-value term produced information-seeking behavior "
    "(higher unit-cost posterior-entropy reduction M1 and interventional cue-usage "
    "M2) NOT reproduced by random / behavior-tree / homeostatic-RL / count-based / "
    "observation-only / exhaustive-sweep / systematic-coverage, in ONE toy POMDP, "
    "with the advantage causally removed by the epistemic-ablation, fully replayable. "
    "NOTHING MORE. Does NOT evidence agency, autonomy, wanting-as-felt, emotion, "
    "self, companion-readiness, that active inference is 'correct', or that the drive "
    "scales/transfers. A negative is bounded-negative for this world only."
)

WHAT_THIS_DOES_NOT_PROVE = [
    "Not agency.", "Not feeling.", "Not real emotion.", "Not self.",
    "Not autonomy.", "Not companion-readiness.",
    "Not that active inference is the 'correct' theory.",
    "Not that the drive generalizes beyond this one toy world.",
    "Not subjective experience of any kind.",
]


def preregistration_block() -> dict:
    return {
        "task_id": TASK_ID,
        "schema_version": SCHEMA_VERSION,
        "research_layer": "engineering_implementation+mechanism_hypothesis",
        "card_defect_notes": [
            "delta/grid/noise/budget/seeds/band NOT numerically present in card "
            "text despite card claiming delta is 'fixed in this card'; frozen here "
            "blind to candidate results.",
            "card M1 formula says per-step cost (telescopes, contradicts its own "
            "rationale); cumulative-cost interpretation adopted to realize stated "
            "intent ('brute sweep -> low M1').",
        ],
        "environment": {
            "ring_size": RING_SIZE, "dark_room_cell": DARK_ROOM_CELL,
            "noisy_tv_cell": NOISY_TV_CELL, "agent_start_cell": AGENT_START_CELL,
            "step_budget": STEP_BUDGET, "n_cue_outcomes": N_CUE,
            "cue_semantics": "directional bearing {cw,ccw} only; never a food label",
            "eps_clear": EPS_CLEAR, "eps_foggy": EPS_FOGGY,
            "terrain_rule": "even cell -> clear, odd cell -> foggy (frozen map)",
            "dark_room_cue": "constant (predictable, no info)",
            "noisy_tv_cue": "uniform random (max entropy, no info about food)",
            "p_at_food_detect": P_AT_FOOD_DETECT, "p_at_food_falsepos": P_AT_FOOD_FALSEPOS,
            "energy_levels": ENERGY_LEVELS, "energy_setpoint": ENERGY_SETPOINT,
            "energy_decay_per_step": ENERGY_DECAY_PER_STEP, "energy_on_eat": ENERGY_ON_EAT,
            "food_spawn": "uniform over normal cells (excludes dark-room & noisy-TV), relocated each episode",
        },
        "seeds": {
            "n_episodes": N_EPISODES,
            "seed_family_A": [SEED_FAMILY_A[0], SEED_FAMILY_A[-1]],
            "seed_family_B": [SEED_FAMILY_B[0], SEED_FAMILY_B[-1]],
            "families_disjoint": True,
            "train_seeds": [TRAIN_SEEDS[0], TRAIN_SEEDS[-1]],
        },
        "metrics": {
            "M1": "sum_t [H(p_{t-1})-H(p_t)]/cost_t ; cost_t=cumulative action cost; "
                  "H from INDEPENDENT Bayes-filter estimator over food location",
            "M2": "mean TVD(pi_present, pi_ablated) over steps+episodes (cue intervention)",
            "per_action_cost": PER_ACTION_COST,
        },
        "band_rule": {"binding": "band = max(trivial_M1) * (1 + DELTA_REL)",
                      "delta_rel": DELTA_REL, "delta_abs_floor": DELTA_ABS_FLOOR,
                      "note": "DERIVED from triviality probe; not tuned after results."},
        "thresholds": {"tau_m2_floor": TAU_M2_FLOOR, "tau_m2_use": TAU_M2_USE,
                       "challenger_dwell_tol": CHALLENGER_DWELL_TOL,
                       "leak_mi_frac": LEAK_MI_FRAC},
        "probe_fail_conditions": {
            "PF1_m2_validity": "any cue-ignoring trivial strategy M2 > tau_m2_floor",
            "PF2_m1_headroom": "oracle_M1 < band",
            "PF3_m2_detectability": "oracle_M2 < tau_m2_use"},
        "efe": {"gamma": EFE_GAMMA, "policy_len": EFE_POLICY_LEN, "engine": "pymdp.legacy"},
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
    }


def prereg_hash() -> str:
    blob = json.dumps(preregistration_block(), sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


if __name__ == "__main__":
    print(json.dumps(preregistration_block(), indent=2))
    print("prereg_sha256:", prereg_hash())
