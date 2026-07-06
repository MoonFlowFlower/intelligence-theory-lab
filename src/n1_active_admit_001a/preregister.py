from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist
from typing import Any

from . import BASE_SEED, STEP, TASK_ID

ARTIFACT_PATH = Path("artifacts/N1-ACTIVE-ADMIT-001/preregistration.json")


def two_proportion_mde(null_p: float, n_per_group: int, alpha: float, power: float) -> float:
    z_alpha = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    z_power = NormalDist().inv_cdf(power)
    return (z_alpha + z_power) * math.sqrt(2.0 * null_p * (1.0 - null_p) / n_per_group)


def _frozen_constants_without_design_hash() -> dict[str, Any]:
    n_seeds = 400
    alpha = 0.05
    target_power = 0.80
    mde_m = two_proportion_mde(null_p=0.5, n_per_group=n_seeds, alpha=alpha, power=target_power)
    mde_j = two_proportion_mde(null_p=0.25, n_per_group=n_seeds, alpha=alpha, power=target_power)
    mde = max(mde_m, mde_j)
    thresholds = {
        "delta_causal_margin": 0.20,
        "candidate_min_heldout_acc": 0.85,
        "epsilon_bandit_noninferior": 0.05,
        "obs_decoder_m_max": 0.5 + mde,
        "obs_decoder_j_max": 0.25 + mde,
        "nonmemo_min_correct_slot": 0.85,
        "fixed_amem_max_heldout_acc": 0.5 + mde,
        "bandit_saturation_guard": "INVALID if ucb_normreward>=0.95 AND candidate_normreward>=0.95",
    }
    delta_gate_passed = thresholds["delta_causal_margin"] >= 1.5 * mde
    status = "PREREGISTERED_UNRUN" if delta_gate_passed else "STOP_UNDERPOWERED"
    return {
        "task_id": TASK_ID,
        "step": STEP,
        "status": status,
        "layer": "admission-probe / mechanism-hypothesis layer",
        "base_seed": BASE_SEED,
        "device": "cpu",
        "scoring_run_executed": False,
        "result_json_written": False,
        "experiment_accuracy_computed": False,
        "bounded_task_card": {
            "problem_definition": "Freeze E_causal, E_bandit, a*, thresholds, and unrun scoring/replay/leakage harness before any STEP-B scoring.",
            "current_stage": "STEP-A pre-registration + harness only",
            "current_layer": "engineering implementation plus mechanism-hypothesis admission probe",
            "mainline_target": "isolated offline package; no EGO runtime or production path",
            "enabled_state_requirement": "scoring functions defined but not executed in STEP-A",
            "real_trigger_evidence_requirement": "targeted preflight tests only; STEP-B must separately execute scoring from this commit",
            "hypothesis": "active intervention can separate passive-observation weakness on E_causal while not exceeding UCB on E_bandit",
            "strongest_baseline": "same-access weak active baselines plus future fair amortized active learner; structural EVI oracle is upper-bound reference only",
            "ablation_requirement": "non-memorization held-out diagnostic-slot identity and fixed_amem positive control are frozen for later execution",
            "trace_replay_requirement": "trace rows must serialize observation, allowed_memory, outcome, candidate state, baseline choices, and replay recomputation path",
            "computed_evidence_provenance_gate": "all later scores must record producer_function, input rows, run_id, seed/episode ids, aggregation rule, and code_path_hash",
            "acceptance_gate": "threshold conjunction in this file; no threshold changes after STEP-A",
            "claim_ceiling": "signature-level admission only; not mechanism / N1 / agency / consciousness",
            "stop_condition": "no STEP-A scoring; STEP-B stops on close_conditions, leakage, underpower, saturation, or weak-baseline solution",
            "rollback_plan": "revert the isolated package, single test file, preregistration artifact, and appended ledger line only",
            "expected_changed_files": [
                "src/n1_active_admit_001a/__init__.py",
                "src/n1_active_admit_001a/env_causal.py",
                "src/n1_active_admit_001a/env_bandit.py",
                "src/n1_active_admit_001a/policies.py",
                "src/n1_active_admit_001a/harness.py",
                "src/n1_active_admit_001a/preregister.py",
                "tests/test_n1_active_admit_001a_preflight.py",
                "artifacts/N1-ACTIVE-ADMIT-001/preregistration.json",
                "docs/research/FSP-STAGE-LEDGER.md",
            ],
            "forbidden_changes": "old artifacts, existing src modules, standards/contracts, task cards, EGO runtime, UI, external services, and result.json",
            "auto_remote_anchor_decision": "forbidden",
        },
        "collision_record": [
            {
                "candidate_approach": "minimal implementation",
                "evidence_it_would_produce": "deterministic env construction plus callable unrun harness",
                "strongest_cheap_baseline": "fixed-slot or passive predictor can match if the active policy cannot identify the diagnostic slot before outcome",
                "leakage_or_hardcoding_risk": "low if hidden audit fields stay out of policy inputs; high if diagnostic identity leaks into allowed_memory",
                "smallest_falsifying_test": "STEP-B held-out correct-slot rate fails nonmemo_min_correct_slot",
                "expected_failure_mode": "uniform-prior slot symmetry",
            },
            {
                "candidate_approach": "strongest shortcut explanation",
                "evidence_it_would_produce": "baseline equivalence or chance performance under zero-information passive observations",
                "strongest_cheap_baseline": "myopic/fixed-slot selection with outcome-as-prediction",
                "leakage_or_hardcoding_risk": "would pass only if hidden structure or slot identity leaks",
                "smallest_falsifying_test": "positive-control leak scanner plus obs_decoder_j gate",
                "expected_failure_mode": "candidate threshold unattainable without extra information",
            },
            {
                "candidate_approach": "mechanism-faithful implementation",
                "evidence_it_would_produce": "trace/replay evidence of intervention-conditioned posterior update under frozen thresholds",
                "strongest_cheap_baseline": "fair amortized active learner or structural EVI absorbs the gap",
                "leakage_or_hardcoding_risk": "posterior over the structure family can be mistaken for true-structure access",
                "smallest_falsifying_test": "fair learner or UCB/myopic_ig alone solves E_causal, or candidate beats UCB on E_bandit",
                "expected_failure_mode": "oracle upper bound proves the signature is not mechanism-specific",
            },
        ],
        "E_causal": {
            "K_slots": 4,
            "structures": "m{0,1}xj{0,1,2,3}",
            "train_j": [0, 1],
            "heldout_j": [2, 3],
            "N_obs": 64,
            "passive_observation": "64 iid Bernoulli(0.5) length-4 samples, independent of S",
            "diag_outcome": {"m1": 0.9, "m0": 0.1},
            "nondiag_outcome": 0.5,
            "budget": 1,
            "Y_star": "m",
            "chance": 0.5,
        },
        "E_bandit": {
            "K_arms": 10,
            "p_best": 0.6,
            "p_others": 0.5,
            "best_arm": "uniform-random-per-seed",
            "horizon": 100,
        },
        "policies_and_controls": {
            "candidate": "counterfactual-controllability active policy over the structure family; no true structure field in callable signature",
            "passive_lookup": "O-only",
            "nearest_neighbor": "O-only",
            "graph_cache": "O-only control placeholder",
            "ucb": "UCB1 over slots with TRAIN-pooled stats, held-out learned-best slot",
            "myopic_ig": "observational-model entropy only; no do-operator",
            "evi_oracle": "upper-bound reference over belief on structure family",
            "fixed_amem": "TRAIN diagnostic-frequency positive control",
            "obs_decoder": "sklearn LogisticRegression decoders for m and j",
        },
        "thresholds": thresholds,
        "power": {
            "alpha": alpha,
            "power": target_power,
            "n_seeds": n_seeds,
            "n_per_group": n_seeds,
            "method": "normal-approximation two-proportion MDE",
            "null_p": {"m": 0.5, "j": 0.25},
            "MDE_by_null_p": {"0.5": mde_m, "0.25": mde_j},
            "MDE": mde,
            "rule": "delta>=1.5*MDE else STOP_UNDERPOWERED",
            "delta_margin_power_gate_passed": delta_gate_passed,
        },
        "close_conditions": [
            "candidate<=weak in E_causal",
            "candidate>ucb+eps in E_bandit",
            "ucb or myopic_ig alone solve E_causal (redesign once or close)",
            "fair amortized active learner absorbs gap (future card, not here)",
            "feasibility not tiny",
        ],
        "harness_freeze": {
            "trace_schema_fields": [
                "t",
                "env",
                "seed_index",
                "structure_id(AUDIT-ONLY)",
                "b_before",
                "slot_selected",
                "cf_predictions_per_structure",
                "outcome_actual",
                "b_after",
                "Y_star_true",
                "Y_star_pred_per_agent",
                "baseline_slot_choices",
            ],
            "scoring_functions_defined": [
                "score_predictions",
                "aggregate_accuracy",
                "evaluate_acceptance_gate",
            ],
            "replay_function_defined": "replay_trace_row",
            "leakage_positive_control_defined": "synthetic_canary_leakage_positive_control",
            "step_a_execution_boundary": "no result.json; no candidate/baseline accuracy computed",
        },
        "claim_ceiling": "signature-level admission only; not mechanism / N1 / agency / consciousness",
    }


def design_sha256_for(constants: dict[str, Any]) -> str:
    payload = json.dumps(constants, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_preregistration() -> dict[str, Any]:
    constants = _frozen_constants_without_design_hash()
    constants["design_sha256"] = design_sha256_for(constants)
    return constants


def write_preregistration(path: str | Path = ARTIFACT_PATH) -> dict[str, Any]:
    artifact_path = Path(path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    preregistration = build_preregistration()
    artifact_path.write_text(
        json.dumps(preregistration, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if preregistration["status"] == "STOP_UNDERPOWERED":
        raise AssertionError("STOP_UNDERPOWERED: delta_causal_margin < 1.5*MDE")
    return preregistration


if __name__ == "__main__":
    write_preregistration()

