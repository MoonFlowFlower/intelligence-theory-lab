from pathlib import Path


TASK_ID = "ACOLB-001A-IMPL-001A"
ARTIFACT_DIR = Path("artifacts") / "acolb_001a"

EQUIV_BAND = 0.08
OOD_BAND = 0.05
RHO = 0.35
SCORE_SCALE = 3.0
THRESHOLDS_FROZEN_BEFORE_RUN = True

D = 2
PRIOR_VAR = 4.0
OBS_VAR = 0.08
DECAY_CANDIDATES = [0.35, 0.55, 0.75, 0.9, 1.0]
DEFAULT_DECAY = DECAY_CANDIDATES[0]
REPLAY_TOL = 1e-9
CANDIDATE_EFFECTIVE_CAPACITY = 8
MAX_EPOCHS = 8
CONV_EPS = 1e-9

PROBE_ACTIONS = ["p0", "p1", "p2", "p3", "p4", "p5", "p0", "p1", "p2", "p3"]
QUERY_ACTIONS = ["q0", "q1", "q2"]
ACTION_BASIS = {
    "p0": (1.0, 0.0),
    "p1": (0.0, 1.0),
    "p2": (1.0, 1.0),
    "p3": (-1.0, 1.0),
    "p4": (1.0, -1.0),
    "p5": (-1.0, -1.0),
    "q0": (1.0, 0.5),
    "q1": (0.5, 1.0),
    "q2": (-0.5, 1.0),
}

SEED_FAMILIES = {
    "train": [1001, 1002, 1003, 1004],
    "validation": [2001, 2002, 2003],
    "id_test": [3001, 3002, 3003],
    "amortized_train": [4001, 4002, 4003],
    "ood_test": [5001, 5002, 5003],
}

CLAIM_CEILING = (
    "bounded local mechanism-discrimination evidence on this constructed ACOLB "
    "generator / seeds / thresholds only; no Gate pass, no mainline effect, no live path, "
    "no agency, no autonomy, no consciousness, no emotion, no stable user benefit, no EGO readiness"
)
