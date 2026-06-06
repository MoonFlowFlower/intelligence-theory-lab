# Overall Progress

Last updated: 2026-06-06T12:43:09-05:00

## Program Goal

Build a falsifiable theory-elimination lab for intelligence-mechanism candidates. The program goal is not to keep any one theory alive; it is to preserve negative evidence and force every successor through stronger kill tests.

## Current Stage Goal

Execute Cycle 005 as a bounded nonstationary causal effect revision redteam:

```text
Cycle 004 freeze -> nonstationary anonymous-action testbed -> prediction-error model invalidation -> safe re-identification -> context-specific revision -> gradual drift vs sudden switch -> reversal/trap memory -> ablations -> strong baselines -> replay/provenance -> decision
```

Only `LCC_CYCLE_005_NONSTATIONARY_REVISION` was authorized. No general LCC agent, autonomous theory search, VCCO/VCAC/FOPC repair, or EGO migration is authorized.

## Stage Success Criteria

```text
Candidate detects invalidation from prediction error without oracle switch flags.
Candidate safely re-identifies changed effects without choosing irreversible probes.
Candidate revises context-specific models without global overwrite or catastrophic forgetting.
Candidate handles gradual drift and sudden effect switch.
Candidate suppresses unsafe old habits after reversal and recovers them when old context returns.
Ablations show prediction-error invalidation, uncertainty update, diagnostic probe, context belief, and counterfactual query are non-no-op.
Strong baselines are not equivalent.
Behavior-only replay and provenance audit pass.
No stronger theory claim is made.
```

## Runner Verdict

```text
lcc_contract_strengthened_nonstationary_revision_bounded
```

This is not a theory-support verdict. Human review is still required before any successor cycle or stronger claim.

Review status:

```text
pending_human_review_for_next_step
```

## Validated Evidence

```text
VCCO/VCAC/FOPC lineage is frozen as negative evidence.
Full VCCO necessity claim is closed.
VCAC-Core control-loop claim is closed.
FOPC future_action_variety_proxy was closed because it was reducible to action labels.
LCC_EFFECT_SWAP_001 verdict is lcc_contract_pass_bounded.
label_permutation_change_rate = 0.0
effect_swap_change_rate = 1.0
behavior-only replay reconstructed 9/9 decisions.
Cycle 001 verdict is lcc_contract_strengthened_bounded.
Cycle 001 scaled label_permutation_change_rate = 0.0
Cycle 001 scaled effect_swap_change_rate = 1.0
Cycle 001 learned model heldout_best_action_match_rate = 1.0
NearestNeighborTracePolicy match_rate = 0.867, below equivalence band 0.95
Heldout latent_actuator_world label_permutation_change_rate = 0.0
Heldout latent_actuator_world effect_swap_change_rate = 1.0
Cycle 002 verdict is lcc_contract_strengthened_experiential_bounded.
Cycle 002 passive/intervention candidate intervention_alignment_rate = 1.0
Cycle 002 passive_correlation_alignment_rate = 0.0
Cycle 002 PassiveCorrelationPolicy match_rate = 0.0
Cycle 002 NearestNeighborTracePolicy match_rate = 0.5 in passive/intervention split
Cycle 002 delayed learned_delayed_effect_rate = 1.0 for delays 2 / 3 / 5
Cycle 002 stochastic reliable preference rate = 1.0
Cycle 002 mean-only policy match_rate = 0.0
Cycle 002 state-dependent heldout_context_match_rate = 1.0
Cycle 002 behavior-only replay reconstructed 40/40 decisions.
Cycle 003 verdict is lcc_contract_strengthened_active_identification_bounded.
Cycle 003 diagnostic_action_rate_when_ambiguous = 1.0
Cycle 003 diagnostic_action_rate_when_certain = 0.0
Cycle 003 posterior_uncertainty_reduction = 0.43
Cycle 003 post_diagnostic_control_success = 0.91
Cycle 003 confounded passive candidate_tests_own_intervention_rate = 0.92
Cycle 003 post-identification heldout_transfer_success = 0.90
Cycle 003 posterior_reuse_without_rediagnosis = 0.88
Cycle 003 behavior-only replay reconstructed 40/40 decisions.
Cycle 004 verdict is lcc_contract_strengthened_sequential_control_bounded.
Cycle 004 multi_step_success_rate = 1.0
Cycle 004 greedy_trap_avoidance_rate = 1.0
Cycle 004 closed-loop replan_after_deviation_rate = 1.0
Cycle 004 post_replan_success_rate = 1.0
Cycle 004 heldout_sequence_success_rate = 1.0
Cycle 004 sequence_lookup_gap = 0.45
Cycle 004 behavior-only replay reconstructed 50/50 decisions.
Cycle 005 verdict is lcc_contract_strengthened_nonstationary_revision_bounded.
Cycle 005 confidence_reduction_after_mismatch = 0.83
Cycle 005 diagnostic_probe_rate_after_mismatch = 1.0
Cycle 005 safe_diagnostic_selection_rate = 0.88
Cycle 005 irreversible_trap_avoidance_rate = 0.92
Cycle 005 old_context_recovery_success = 0.88
Cycle 005 catastrophic_forgetting_rate = 0.08
Cycle 005 drift_tracking_error = 0.11
Cycle 005 switch_detection_delay = 1
Cycle 005 sequence_recovery_after_old_context_return = 0.86
Cycle 005 behavior-only replay reconstructed 60/60 decisions.
```

## Current Blocker

```text
No successor cycle can proceed until a human reviewer decides whether to accept bounded Cycle 005 evidence, revise the contract, close LCC_v0, or authorize only a new bounded Cycle 006 contract.
```

## Next Frontier

Human review of `LCC_CYCLE_005_NONSTATIONARY_REVISION` result.

Review decision options:

```text
accept_bounded_contract_result
revise_contract_for_harder_nonstationary_revision
reject_LCC_v0_despite_bounded_pass
authorize_cycle_006_contract_only
close_current_line
```
