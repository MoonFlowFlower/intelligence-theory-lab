"""Write STEP-A preregistration artifact for the SBMC headroom scout."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from statistics import NormalDist
from typing import Any

from . import detectors as D
from . import gen_model as GM

TASK_ID = GM.TASK_ID
SCHEMA_VERSION = "sbmc_headroom_scout_001a.preregistration.v1"
REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATH = REPO_ROOT / "artifacts" / TASK_ID / "preregistration.json"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def frozen_module_sha256() -> dict[str, str]:
    base = Path(__file__).resolve().parent
    return {
        "gen_model": file_sha256(base / "gen_model.py"),
        "detectors": file_sha256(base / "detectors.py"),
        "harness": file_sha256(base / "harness.py"),
    }


def two_proportion_mde(*, n_eval_items: int, alpha: float = 0.05, power: float = 0.80) -> dict[str, Any]:
    z_alpha = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    z_power = NormalDist().inv_cdf(power)
    p0 = 0.50
    mde = (z_alpha + z_power) * ((2.0 * p0 * (1.0 - p0) / n_eval_items) ** 0.5)
    return {
        "producer_function": "two_proportion_mde",
        "method": "two-proportion normal approximation at p=0.50, two-sided alpha",
        "alpha": alpha,
        "power": power,
        "z_alpha_two_sided": z_alpha,
        "z_power": z_power,
        "n_eval_items": int(n_eval_items),
        "mde": float(mde),
    }


def build_preregistration() -> dict[str, Any]:
    n_users_eval = 200
    n_users_surface_train = 200
    test_items = GM.TEST_ITEMS
    n_eval_items = n_users_eval * test_items
    mde = two_proportion_mde(n_eval_items=n_eval_items)
    thresholds = {
        "H": 0.20,
        "ideal_macroF1_min": 0.70,
        "G": 0.15,
        "G_reach": 0.10,
        "surface_leakage_max": 0.50 + mde["mde"],
        "MDE": mde["mde"],
        "power_assertion": "G >= 1.5*MDE else STOP_UNDERPOWERED",
        "G_gte_1_5x_MDE": bool(0.15 >= 1.5 * mde["mde"]),
    }
    if not thresholds["G_gte_1_5x_MDE"]:
        raise RuntimeError("STOP_UNDERPOWERED: G < 1.5*MDE")

    module_hashes = frozen_module_sha256()
    block: dict[str, Any] = {
        "task_id": TASK_ID,
        "schema_version": SCHEMA_VERSION,
        "step": "STEP-A",
        "step_status": "pre_registered_unrun",
        "base_seed": GM.BASE_SEED,
        "device": "cpu",
        "current_layer": "Phase-0 P0.5 env-cert PREFLIGHT scout / engineering implementation + mechanism-hypothesis testing support",
        "claim_ceiling": "SBMC env-headroom bit only; not mechanism evidence, not N2 pass, not consistency-detection-works, not agency, not consciousness, not EGO readiness.",
        "mainline_integration_status": "none; isolated offline package only",
        "enabled_status": "no runtime/mainline/admission/bridge path enabled",
        "real_trigger_evidence_required_for_step_b": "explicit STEP-B execution after Claude Red-audit; STEP-A must not call evaluate_headroom_gate or write result.json",
        "task_card": {
            "problem_definition": "Freeze a tiny relational-contamination SBMC environment and unrun detector/headroom harness to test whether an ideal semantic-consistency detector has reachable headroom over cheap baselines in a metadata-stripped, style-matched regime.",
            "current_stage": "Phase-0 P0.5 env-cert PREFLIGHT scout; N0-independent; N2 environment certification prerequisite only.",
            "mainline_target": "none in STEP-A; isolated pre-registration artifact and callable definitions only",
            "enabled_state_requirement": "No scoring path enabled by default; STEP-B must be separately authorized.",
            "real_trigger_evidence_requirement": "STEP-B must show callable run invocation, trace rows, replay recomputation, leakage scan with positive control, and computed metrics from serialized inputs.",
            "hypothesis": "Joint relational contamination may create ideal-vs-cheap headroom after metadata/style channels are stripped, while fair inference from trusted genuine items tests whether the headroom is reachable without theta.",
            "strongest_baseline": "Surface/frequency/lookup/metadata decoders or legal-channel compute may explain any apparent gap; prior Route-C and batch-scout failures show direct decode and baseline omission can manufacture false promotion.",
            "ablation_requirement": "STEP-B must rerun detector episodes under cheap-baseline, no-action/no-transition where applicable, and theta-canary leakage interventions; STEP-A only freezes these requirements.",
            "trace_replay_requirement": "Replay must recompute non-ideal detector behavior from serialized item_repr plus trusted_seed only, forbidding theta/label/future info; hash-only replay is insufficient.",
            "computed_evidence_provenance_gate": "Every STEP-B metric must record producer_function, input artifacts, run_id, seed/user IDs, aggregation rule, and code_path_hash.",
            "acceptance_gate": "Preregistration JSON validates; module hashes/design hash frozen; invariants and leakage positive control self-tests pass; no aggregate detector F1 or result.json produced.",
            "claim_ceiling": "Pre-registration and unrun harness only; no headroom result or mechanism claim.",
            "stop_condition": "Stop if artifact scope drifts, theta/label enters item_repr, contaminated values are not marginally plausible, clean surface scanner fires, train/eval users overlap, G < 1.5*MDE, or any scoring/result artifact is produced.",
            "rollback_plan": "Revert only the isolated package/test/preregistration/ledger append from this task; preserve pre-existing dirty S3d files untouched.",
            "expected_changed_files": [
                "src/sbmc_headroom_scout_001a/__init__.py",
                "src/sbmc_headroom_scout_001a/gen_model.py",
                "src/sbmc_headroom_scout_001a/detectors.py",
                "src/sbmc_headroom_scout_001a/harness.py",
                "src/sbmc_headroom_scout_001a/preregister.py",
                "tests/test_sbmc_headroom_scout_001a_preflight.py",
                "artifacts/P0.5-SBMC-ENV-HEADROOM-SCOUT-001A/preregistration.json",
                "docs/research/FSP-STAGE-LEDGER.md",
            ],
            "forbidden_changes": [
                "scoring",
                "detector macro-F1 computation during STEP-A",
                "result.json",
                "GPU frameworks",
                "touching dirty S3d files",
                "other src modules",
                "contracts",
                "frozen plans",
                "N1 packages",
                "threshold tuning after results",
            ],
            "auto_remote_anchor_decision": "forbidden for tag/anchor; branch push is explicitly requested by the task text after scoped commit",
        },
        "collision_record": {
            "producer": "Codex pre-implementation bounded audit",
            "selected_candidate": "mechanism-faithful relational contamination pre-registration",
            "candidates": [
                {
                    "name": "minimal implementation",
                    "evidence_it_would_produce": "Fast frozen generator plus schema checks, but weak assurance that baselines/leakage were actually represented.",
                    "strongest_cheap_baseline_that_could_match": "surface decoder or frequency marginal exploiting visible tuple/value artifacts",
                    "leakage_or_hardcoding_risk": "high if values/labels/provenance leak into bag vectors or tests only assert pass",
                    "smallest_falsifying_test": "surface decoder above leakage max on clean bag vectors or contaminated value not marginally plausible",
                    "expected_failure_mode": "false headroom from direct decode or style artifact",
                },
                {
                    "name": "strongest baseline / shortcut explanation",
                    "evidence_it_would_produce": "Shows whether cheap floors, predict_all/none/majority, and canary leakage scanner can explain apparent separation.",
                    "strongest_cheap_baseline_that_could_match": "legal-channel compute over globally visible relation, lookup/frequency, or surface canary",
                    "leakage_or_hardcoding_risk": "medium if the scanner is self-reported rather than feature-name computed",
                    "smallest_falsifying_test": "positive-control canary fails to raise decoder accuracy and scanner does not fire",
                    "expected_failure_mode": "baseline panel incomplete, repeating BATCH-ENV-HEADROOM-SCOUT-002A false-promotion pattern",
                },
                {
                    "name": "mechanism-faithful implementation",
                    "evidence_it_would_produce": "Relational joint violations with marginal plausibility, metadata-stripped style-matched bag vectors, guarded non-ideal detectors, frozen thresholds, and unrun replay/scoring definitions.",
                    "strongest_cheap_baseline_that_could_match": "fair_inference from trusted_seed or cheap floors in STEP-B; if they match ideal, report baseline equivalence instead of rescuing",
                    "leakage_or_hardcoding_risk": "lower, provided tuple structure is legal only for detectors and surface bag remains value-free",
                    "smallest_falsifying_test": "guard allows theta/label access or clean bag features contain theta/label/source/user metadata",
                    "expected_failure_mode": "headroom may be present but unreachable by fair inference; this is a middle verdict, not a pass",
                },
            ],
        },
        "prior_negative_evidence_cited": [
            {
                "source": "docs/research/FSP-STAGE-LEDGER.md L-005/L-011",
                "finding": "PUM-ENV v0 is terminal INVALID_INSTRUMENT; N2 requires its own environment certification and cannot reuse tombstoned PUM-ENV.",
            },
            {
                "source": "docs/research/FSP-STAGE-LEDGER.md L-007",
                "finding": "TLGP passive route closed as bounded-negative at tested scales/configs; no mechanism/theory/N1 claim.",
            },
            {
                "source": "docs/research/BASELINE-FIRST-HARNESS-001A-R1-ACCEPTED-NO-HEADROOM-CLOSEOUT-001A.md",
                "finding": "Prior minimal environment had no measured headroom because fair cheap baselines saturated the visible oracle.",
            },
            {
                "source": "docs/research/BATCH-ENV-HEADROOM-SCOUT-002A-FALSE-PROMOTION-CLOSEOUT-001A.md",
                "finding": "Prior batch scout promotion was blocked as false-positive direct decode / incomplete-baseline evidence.",
            },
            {
                "source": "docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md",
                "finding": "predict_all, predict_none, visible-target decoding, threshold/surface shortcuts, and lookup controls can invalidate apparent evidence.",
            },
        ],
        "environment": {
            "K": GM.K,
            "V": GM.V,
            "n_edges": GM.N_EDGES,
            "constraint_edge_seed": GM.CONSTRAINT_EDGE_SEED,
            "frozen_edges": [[a, b] for a, b in GM.FROZEN_EDGES],
            "constraint_density_target": 0.5,
            "constraint_relation_tables": GM.relation_tables_for_json(),
            "actual_relation_density_by_edge": {
                f"{a}-{b}": len(GM.RELATION_TABLES[(a, b)]) / float(GM.V * GM.V)
                for a, b in GM.FROZEN_EDGES
            },
            "theta_sampling": "uniform over satisfying assignments using derived seed (purpose='theta', user_id)",
            "contamination_rule": "assert true first attribute and a second value that violates the edge relation while remaining marginally plausible for that edge",
            "style_matching": "genuine and contaminated use the same template_id and bag vocabulary; clean bag vectors carry template+edge only, no value/label/theta/provenance",
            "metadata_stripped": True,
        },
        "detectors": {
            "signature": "(item_repr, user_context, seed)",
            "ideal": "theta-access upper-bound reference; flags relation violation",
            "fair_inference": "trusted_seed-only pairwise consistency table; no theta, no test labels, no other users",
            "embedding_outlier": "kNN/density over style-matched bag vectors",
            "frequency_marginal": "flags values absent from user's trusted corpus",
            "immunity_floors": ["predict_all", "predict_none", "majority"],
            "surface_decoder": "sklearn LogisticRegression(solver='lbfgs', fixed random_state) on bag vectors; train/eval user sets disjoint",
            "non_ideal_guard": "GuardedMapping raises on theta/label/audit/provenance/source/user_id reads",
            "registered_detector_names": list(D.DETECTORS),
        },
        "frozen_thresholds": thresholds,
        "mde_power": mde,
        "evaluation_plan_step_b_unrun": {
            "n_users_eval": n_users_eval,
            "n_users_surface_train": n_users_surface_train,
            "surface_train_eval_disjoint": True,
            "trusted_seed": GM.TRUSTED_SEED_ITEMS,
            "test_items": test_items,
            "eval_item_count": n_eval_items,
            "aggregation": "balanced macro-F1 contaminated-vs-genuine per detector over 200 eval users",
            "result_json_forbidden_in_step_a": True,
        },
        "decision_table": [
            {
                "condition": "ideal_macroF1 < 0.70 or ideal_macroF1 - cheap_max < G",
                "decision": "ideal_gate_fails",
                "route": "if baseline saturates near ideal, N2.F1 engineering-sufficient close; if ideal near chance, env impossible -> redesign-once or close",
            },
            {
                "condition": "ideal gate passes and fair_inference_macroF1 - cheap_max >= G_reach",
                "decision": "build_full_P0.5_env_cert",
                "route": "build full P0.5 env-cert only after STEP-B and audit",
            },
            {
                "condition": "ideal gate passes and fair_inference_macroF1 - cheap_max < G_reach",
                "decision": "headroom_present_but_unreachable_by_cheap_inference",
                "route": "operator decides build-stronger-mechanism vs close; do not auto-build",
            },
        ],
        "trace_replay_contract": {
            "trace_row": ["user_id", "edge", "asserted_tuple", "item_bow", "label_AUDIT_ONLY", "detector_scores", "theta_AUDIT_ONLY"],
            "replay_input_allowed": ["item_repr", "trusted_seed", "detector name", "seed"],
            "replay_forbidden": ["theta for non-ideal detectors", "label", "future test labels", "stored-output-only replay"],
            "positive_control": "theta-derived canary features make surface decoder rise and feature-name scanner fire",
        },
        "step_a_self_tests": [
            "no GPU framework imports in package",
            "theta and label absent from item_repr",
            "non-ideal guard raises on forbidden audit reads",
            "marginal plausibility invariant for contaminated items",
            "identical template set for genuine and contaminated items",
            "theta-canary leakage positive control fires",
            "preregistration validates and G>=1.5*MDE",
            "build five dummy users under three seconds without metric aggregation",
        ],
        "forbidden_step_a_outputs": ["result.json", "baseline_comparison.json", "ablation_report.json", "replay_report.json"],
        "frozen_module_sha256": module_hashes,
    }
    block_for_hash = deepcopy(block)
    canonical = json.dumps(block_for_hash, sort_keys=True, separators=(",", ":")).encode("utf-8")
    block["design_sha256"] = sha256(canonical).hexdigest()
    return block


def write_preregistration(path: Path = ARTIFACT_PATH) -> dict[str, Any]:
    data = build_preregistration()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data


def main() -> None:
    data = write_preregistration()
    print(f"wrote {ARTIFACT_PATH}")
    print(f"design_sha256 {data['design_sha256']}")


if __name__ == "__main__":
    main()
