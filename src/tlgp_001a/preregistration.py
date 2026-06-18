"""Frozen pre-registration for TLGP-001A.

ALL numeric constants, the rule family, the held-out split, the metric thresholds,
and the verdict rule are fixed HERE, before any run, and hashed (sha256 of canonical
JSON). The harness writes this block + its sha into result.json BEFORE computing any
score. Nothing in this file may be tuned after seeing results (anti-hardcoding).

Design decision (documented, not hidden):
  Headroom source is the mod-K NON-LINEARITY. effect = (sum_i w_i*x_i + c*a) mod K.
  Held-out queries use property VALUES never seen during adaptation (extrapolation).
  An ideal observer that knows the rule FAMILY (the K^(D+1) linear-mod hypotheses)
  recovers the rule by exact Bayesian filtering and extrapolates. Fair baselines get
  the SAME numeric features (NO one-hot starvation, K4) but lack the mod prior, so
  they cannot extrapolate the wrapped arithmetic to unseen values. The
  shuffle-structure ablation (random table instead of a linear rule) collapses the
  ideal observer's advantage, proving the headroom comes from compositional structure
  and not from privileged peeking.

Leak-detector refinement (documented deviation from the card's single-target wording):
  The card says "MI between observation channels and the latent rule >= frac*H_rule".
  Leak (ii) leaks the held-out ANSWER, which carries only ~log2(K) bits of the
  ~log2(K^(D+1)) bits of rule identity, so an MI-vs-rule_id test alone cannot flag it.
  We therefore make the detector DUAL-TARGET: a channel is flagged if
  MI(channel; rule_id) >= frac*H(rule_id) OR MI(channel; held_out_answer) >= frac*H(answer).
  This is strictly more capable (K4/K6) and is the only deviation from the card text.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

# --- world / rule family -------------------------------------------------------
K: int = 5                      # modulus AND number of effect classes (prime -> invertible)
D: int = 3                      # number of symbol properties
M: int = 5                      # property cardinality; values 0..M-1
ACTION_CARD: int = 5            # actions 0..ACTION_CARD-1
TRAIN_VALUES = (0, 1, 2)        # property values usable during adaptation
HELDOUT_VALUES = (3, 4)         # property values reserved for held-out queries (unseen)
RULE_SPACE_SIZE: int = K ** (D + 1)   # 5^4 = 625 enumerable linear-mod rules

# --- sampling sizes ------------------------------------------------------------
N_ADAPT: int = 24               # adaptation interactions per episode (>= D+1 for identifiability)
N_QUERY: int = 30               # held-out queries per episode
N_EPISODES: int = 200           # episodes per condition

# --- metric / verdict thresholds (frozen) -------------------------------------
FLOOR: float = 1.0 / K          # balanced-accuracy chance floor = 0.20
DELTA: float = 0.10             # band used for headroom + baseline-failure + ceiling checks
MI_FRAC: float = 0.5            # leak flagged if MI(channel;target) >= MI_FRAC * H(target)

# --- seeds (frozen) ------------------------------------------------------------
MASTER_SEED: int = 20260618
SEED_REAL: int = MASTER_SEED + 1
SEED_SHUFFLE: int = MASTER_SEED + 2
SEED_LEAK: int = MASTER_SEED + 3
SEED_BASELINE_FIT: int = MASTER_SEED + 4

# --- verdict labels ------------------------------------------------------------
VERDICT_PASS = "world_discriminates_structure_inference"
VERDICT_WEAK = "world_cannot_discriminate__lookup_or_degenerate"
VERDICT_INVALID = "invalid_due_to_leakage_or_contract_failure"

CLAIM_CEILING = (
    "A minimal procedural world that separates compositional-latent inference from "
    "lookup/memorization on a held-out, balanced, leak-free metric, with measured "
    "headroom vs an ideal (Bayesian) observer -- IF the computed verdict is "
    f"'{VERDICT_PASS}'. Tests NO candidate; not generalization-mechanism evidence; "
    "evidences nothing about agency, learning-as-mechanism, self, feeling, or "
    "subjectivity. A negative verdict is bounded to THIS world. This run was "
    "drafter-implemented in a non-outcome-neutral session and REQUIRES independent "
    "audit before its verdict may be treated as banked lab evidence."
)


def prereg_dict() -> Dict[str, Any]:
    """Canonical pre-registration payload (order-stable for hashing)."""
    return {
        "task_id": "TLGP-001A",
        "research_layer": "engineering_implementation+mechanism_hypothesis_preflight",
        "candidate_free": True,
        "world": {
            "rule": "effect = (sum_i w_i * x_i + c * a) mod K",
            "K": K, "D": D, "M": M, "ACTION_CARD": ACTION_CARD,
            "train_values": list(TRAIN_VALUES),
            "heldout_values": list(HELDOUT_VALUES),
            "rule_space_size": RULE_SPACE_SIZE,
            "heldout_definition": "every query property value drawn from heldout_values (unseen during adaptation)",
        },
        "sizes": {"n_adapt": N_ADAPT, "n_query": N_QUERY, "n_episodes": N_EPISODES},
        "metric": {
            "primary": "mean over episodes of per-episode balanced accuracy on held-out queries",
            "floor": FLOOR,
            "delta_band": DELTA,
            "headroom": "ideal_observer - max(fair_non_inference_baselines)",
            "margin_rule": "margin = max_trivial_baseline + DELTA (reported); pass also requires headroom > DELTA",
        },
        "leakage": {
            "detector": "dual-target mutual information",
            "mi_frac": MI_FRAC,
            "targets": ["rule_id", "held_out_answer"],
            "flag_if": "MI(channel;rule_id) >= MI_FRAC*H(rule_id) OR MI(channel;answer) >= MI_FRAC*H(answer)",
            "planted_controls": ["rule_id_channel", "heldout_answer_channel", "renamed_rule_id_channel"],
        },
        "seeds": {
            "master": MASTER_SEED, "real": SEED_REAL, "shuffle": SEED_SHUFFLE,
            "leak": SEED_LEAK, "baseline_fit": SEED_BASELINE_FIT,
        },
        "verdict_rule": {
            "pass": VERDICT_PASS,
            "weak": VERDICT_WEAK,
            "invalid": VERDICT_INVALID,
            "pass_iff_all": [
                "headroom > DELTA",
                "max_fair_baseline <= FLOOR + DELTA",
                "single_step_decoder <= FLOOR + DELTA",
                "ideal_observer >= FLOOR + 2*DELTA",
                "all planted leaks caught AND no clean channel falsely flagged",
                "shuffle ablation collapses headroom (headroom_shuffle <= DELTA)",
                "replay exact",
            ],
            "invalid_iff": "any planted leak uncaught OR any clean channel falsely flagged",
            "weak_otherwise": True,
        },
        "claim_ceiling": CLAIM_CEILING,
    }


def prereg_sha256() -> str:
    payload = json.dumps(prereg_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


if __name__ == "__main__":
    print(json.dumps(prereg_dict(), indent=2))
    print("sha256:", prereg_sha256())
