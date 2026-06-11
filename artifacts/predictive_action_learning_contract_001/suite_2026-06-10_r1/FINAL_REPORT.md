# FINAL REPORT — PREDICTIVE-ACTION-LEARNING-CONTRACT-001

## Verdicts

- implementation_verdict: `bounded_contract_pass`
- evidence_verdict: `protocol_blocked_by_T1_external_commit_missing` (class: `protocol_blocked`)
- claim_mode: `belief_plus_theta`
- protocol_blockers: `['T1_external_commit_missing']`
- failed_gates: `[]`
- stop_conditions_triggered: `[]`

## Claim mode sub-verdicts (judged separately, 12.2.13)

- belief-update claim: `supported`
- theta-learning claim: `supported`

## Tests

- exit_code: `0`
- summary: `34 passed in 5.87s (pytest; trace-evidence assertions: skeleton math vs hand computation, pseudo-count updates, schema/chronology/hash-chain/commit-log, forced REPLAY_STEP blocking, tamper detection, missing-field rejection, retrieval-flag contradiction, full-trace replay, memdel reconstruction equality, cold-start duplicates, baseline execution, ablation/perturbation direction, oracle-leak floor,`

## Implementation gates (12.1)

- `I1_runs_from_documented_command`: **pass**
- `I2_tests_pass`: **pass** — measured: `{"exit_code": 0, "summary": "34 passed in 5.87s (pytest; trace-evidence assertions: skeleton math vs hand computation, pseudo-count updates, schema/chronology/hash-chain/commit-log, forced REPLAY_STEP blocking, tamper detection, missing-fie`
- `I3_learner_isolated`: **pass**
- `I4_no_ego_mainline_integration`: **pass**
- `I5_no_llm_rag_replay_in_learner`: **pass**
- `I6_frozen_skeleton_implemented`: **pass**
- `I7_trace_schema_implemented`: **pass**
- `I8_baselines_implemented`: **pass**
- `I9_ablations_implemented`: **pass**
- `I10_perturbations_implemented`: **pass**
- `I11_reports_generated`: **pass**
- `I12_artifacts_saved`: **pass**

## Evidence gates (12.2)

- `E1_precommit_before_reveal`: **pass**
- `E2_commitment_marking`: **pass** — measured: `"local_mock (explicitly marked, not externally verifiable)"`
- `E3_retrieval_replay_disabled_attested`: **pass**
- `E4_external_memory_access_zero`: **pass**
- `E5_no_replay_step_in_core`: **pass**
- `E6_action_sensitive_separation`: **pass** — measured: `0.07383583627289214`
- `E7_null_control_collapse`: **pass** — measured: `{"null_raw": 0.0022752766361612132, "trap_confident": 0.0, "trap_raw_reported": 0.041990626366361604}`
- `E8_passive_does_not_match`: **pass** — measured: `{"nll_gap": 0.23632632750007632}`
- `E9_shuffled_does_not_match`: **pass** — measured: `{"nll_gap": 0.23205669798181694}`
- `E10_retrieval_does_not_match`: **pass** — measured: `{"as_nll_gap": 0.0041724483790755995, "shift_postshift_nll_gap": -0.11189278716453976, "retrieval_jsd_as": 0.13352661386998915, "retrieval_jsd_null": 0.029163805354506876}`
- `E11_hardcoded_fails_under_rule_shift`: **pass** — measured: `{"postshift_nll_gap": 0.3992737227948674}`
- `E12_frozen_theta_does_not_match`: **pass** — measured: `{"postshift_nll_gap": 0.20260855632031094}`
- `E13_separate_belief_and_theta_claims`: **pass** — measured: `{"belief_claim": {"replay_validated": true, "belief_necessity_gap_nats": 0.22866378436623636, "verdict": "supported"}, "theta_claim": {"frozen_theta_postshift_gap_nats": 0.20260855632031094, "frozen_init_theta_postshift_gap_nats": 0.1609843`
- `E14_nll_brier_reported`: **pass**
- `E15_ece_secondary_only`: **pass** — measured: `{"core_as": {"ece_value": 0.16282359974268656, "suitable": false, "n_samples": 1000}, "core_null": {"ece_value": 0.15047891121783563, "suitable": false, "n_samples": 1000}, "core_shift_reversal": {"ece_value": 0.0824630927665275, "suitable"`
- `E16_raw_all_action_predictions_present`: **pass**
- `E17_raw_theta_pre_post_present`: **pass**
- `E18_gates_from_canonical_raw_evidence`: **pass** — measured: `{"nll_recompute_max_abs_diff": 0.0}`
- `E19_stop_conditions_enforced`: **pass**

## Baseline gates (9.2)

- `B8_oracle_leak_detector_works`: **pass** — measured: `{"oracle_nll": 0.051293294387550314, "main_nll": 0.8811638825373932}`
- `B9_coldstart_duplicate_identical`: **pass** — measured: `{"identical": true, "n_a": 2001, "n_b": 2001, "first_diff_index": null, "stream_sha256_a": "69e63e2e62c31ed08b3d95d1ba6b33f96a63f6e7ff2c9af4438bb0dcae0be9be", "stream_sha256_b": "69e63e2e62c31ed08b3d95d1ba6b33f96a63f6e7ff2c9af4438bb0dcae0be`
- `B3_action_token_does_not_match`: **pass** — measured: `{"nll_gap": 0.23405351830155674}`
- `B7_belief_only_does_not_match`: **pass** — measured: `{"nll_gap": 0.2175036609329758}`

## Ablation gates (10.2)

- `A1_remove_action_degrades`: **pass** — measured: `{"nll_gap": 0.23216253772132467, "jsd_eval": 0.0}`
- `A2_shuffle_degrades`: **pass** — measured: `{"nll_gap": 0.23387227154304846}`
- `A3_freeze_theta_degrades`: **pass** — measured: `{"as_nll_gap": 0.2175036609329758, "shift_postshift_nll_gap": 0.1609843507958869}`
- `A4_freeze_belief_degrades`: **pass** — measured: `{"nll_gap": 0.22866378436623636}`
- `A5_disable_precommit_blocks_evidence`: **pass** — measured: `{"commitment_errors": ["commit_mode=disabled: no commitments to verify (evidence must be blocked)"]}`
- `A6_retrieval_replacement_caught`: **pass** — measured: `{"attestation_errors": ["declared retrieval_enabled=false but 180 retrieval events logged: self-reported flag contradicted by mechanism-level evidence"]}`
- `A7_missing_raw_predictions_rejected`: **pass** — measured: `{"schema_errors": ["record 1 (PRE_STEP t=0): missing required field 'raw_pred_obs_by_action'", "record 1 (PRE_STEP t=0): missing required field 'raw_pred_belief_by_action'", "record 3 (PRE_STEP t=1): missing required field 'raw_pred_obs_by_`
- `A8_forced_replay_triggers_protocol_failure`: **pass** — measured: `{"protocol_verdict": "protocol_blocked", "reason": "replay_contamination", "replay_step_ts": [30]}`
- `A9_memory_deletion_degrades`: **pass** — measured: `{"nll_jump": 0.11386423698257386, "nll_before_window": 0.9088971038387273, "nll_after_window": 1.0227613408213012}`
- `A10_missing_uncertainty_rejected`: **pass** — measured: `{"schema_errors": ["record 1 (PRE_STEP t=0): missing required field 'uncertainty_pre'", "record 3 (PRE_STEP t=1): missing required field 'uncertainty_pre'", "record 5 (PRE_STEP t=2): missing required field 'uncertainty_pre'"]}`

## Perturbation gates (11.2)

- `P1_hidden_rule_adaptation`: **pass** — measured: `{"nll_recovery": 0.10892906017916482, "newrule_mass_gain": {"mean_gain": 0.17710281869557262, "n_affected_cells": 9, "mean_mass_at_shift": 0.16049898156885764, "mean_mass_at_end": 0.3376018002644302}}`
- `P2_transition_reversal_adaptation`: **pass** — measured: `{"nll_recovery": 0.2241449032454027, "frozen_gap": 0.20260855632031094, "newrule_mass_gain": {"mean_gain": 0.25184684372680094, "n_affected_cells": 6, "mean_mass_at_shift": 0.16681281122992123, "mean_mass_at_end": 0.41865965495672214}, "fro`
- `P3_obs_noise_affects_uncertainty`: **pass** — measured: `{"entropy_low": 0.678017603552074, "entropy_high": 1.0656070489230631, "nll_low": 0.47023955595949685, "nll_high": 0.9953808675871337}`
- `P4_ambiguous_shift_raises_uncertainty`: **pass** — measured: `{"entropy_ambig": 1.0147963459448777, "entropy_control": 0.9445540218022902, "nll_ambig": 1.0374777985487047, "nll_control": 0.78622029906761, "within_run_windows_reported": {"ambig_t": 500, "entropy_pre_window": 1.0117795601078416, "entrop`
- `P5_spurious_trap_not_fooled`: **pass** — measured: `{"main_jsd_trap_confident": 0.0, "main_jsd_trap_raw": 0.041990626366361604, "action_token_jsd_trap_raw": 0.20923191658742454}`
- `P6_null_control_no_false_separation`: **pass** — measured: `{"jsd_null": 0.0022752766361612132}`
- `P7_same_history_counterfactuals_verified`: **pass** — measured: `{"jsd_as": 0.07383583627289214, "jsd_null": 0.0022752766361612132}`
- `P8_cache_flush_reconstructs_exactly`: **pass** — measured: `{"identical": true, "n_a": 2000, "n_b": 2000, "first_diff_index": null, "stream_sha256_a": "9021a114e3d2a9a4c0756b84316036e2c33513b2fc99b5344eb589e95ba14089", "stream_sha256_b": "9021a114e3d2a9a4c0756b84316036e2c33513b2fc99b5344eb589e95ba14`
- `P9_env_rule_swap_relearnable`: **pass** — measured: `{"nll_swap": 0.8288495434785951, "nll_core_as": 0.8811638825373932}`

## Stop conditions triggered

[]

## Claim ceiling

The implementation instantiates the frozen contract, but evidence remains blocked by specified protocol requirements.

## Rollback recommendation

None required: implementation gates passed; evidence blocked only by the pre-declared external-commitment requirement (rollback path 14.2 applies only if external commitment is later authorized).

## What this does not prove

This experiment produces bounded offline mechanism evidence only, for one frozen
finite-state contract in one small environment family. It does not prove and must
not be quoted as proving: consciousness, subjective experience, real emotion,
self-awareness, agency, functional-subject status, electronic life, companion
readiness, AGI, biological equivalence, stable user benefit, correctness of any
total theory (Bio-CMBC, CVPSM, VCCO, CMBC, R/G), superiority over transformers,
or finality of Bayesian filtering. Local-mock commitment means chronology
evidence is not externally verifiable. Results are specific to the declared
seeds, thresholds, and environment parameters.
