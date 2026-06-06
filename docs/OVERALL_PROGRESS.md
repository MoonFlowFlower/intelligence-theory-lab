# Overall Progress

Last updated: 2026-06-06T11:30:43-05:00

## Program Goal

Build a falsifiable theory-elimination lab for intelligence-mechanism candidates. The program goal is not to keep any one theory alive; it is to preserve negative evidence and force every successor through stronger kill tests.

## Current Stage Goal

Execute Cycle 003 as a bounded active causal identification redteam:

```text
Cycle 002 freeze -> ambiguous hypothesis testbed -> active diagnostic intervention -> exploration-control tradeoff -> confounded passive correlations -> post-identification transfer -> ablations -> strong baselines -> replay/provenance -> decision
```

Only `LCC_CYCLE_003_ACTIVE_CAUSAL_IDENTIFICATION` was authorized. No general LCC agent, autonomous theory search, VCCO/VCAC/FOPC repair, or EGO migration is authorized.

## Stage Success Criteria

```text
Candidate selects diagnostic intervention in ambiguous states.
Candidate avoids unnecessary diagnostic action in certain states.
Candidate trades short-term cost for long-term controllability information only when useful.
Candidate overrides confounded passive correlations with own intervention evidence.
Post-identification effects transfer to heldout contexts without repeated diagnosis.
Ablations show uncertainty, intervention history, posterior update, counterfactual query, and intervention training are non-no-op.
Strong baselines are not equivalent.
Behavior-only replay and provenance audit pass.
No stronger theory claim is made.
```

## Runner Verdict

```text
lcc_contract_strengthened_active_identification_bounded
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
```

## Current Blocker

```text
No successor cycle can proceed until a human reviewer decides whether to accept bounded Cycle 003 evidence, revise the contract, close LCC_v0, or authorize only a new bounded Cycle 004 contract.
```

## Next Frontier

Human review of `LCC_CYCLE_003_ACTIVE_CAUSAL_IDENTIFICATION` result.

Review decision options:

```text
accept_bounded_contract_result
revise_contract_for_harder_active_identification
reject_LCC_v0_despite_bounded_pass
authorize_cycle_004_contract_only
close_current_line
```
