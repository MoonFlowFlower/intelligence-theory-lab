# Overall Progress

Last updated: 2026-06-06T15:07:18-05:00

## Program Goal

Build a falsifiable theory-elimination lab for intelligence-mechanism candidates. The program goal is not to keep any one theory alive; it is to preserve negative evidence and force every successor through stronger kill tests.

## Current Stage Goal

Execute Cycle 010 as a bounded blind-holdout independent-replication redteam:

```text
Cycle 009 freeze -> candidate freeze/scope lock -> contract DSL and blind holdout generation -> blind holdout evaluation -> generic baseline tournament -> independent trace-only scoring -> statistical replication -> blind-holdout ablations -> negative controls -> decision
```

Only `LCC_CYCLE_010_BLIND_HOLDOUT` was authorized. No general LCC agent, autonomous theory search, VCCO/VCAC/FOPC repair, or EGO migration is authorized.

## Stage Success Criteria

```text
Candidate/control code is frozen before blind holdout generation and remains hash-stable.
Blind holdout is generated after freeze using fresh predeclared seeds and at least 8 DSL templates.
Frozen candidate passes blind holdout using only allowed abstract inputs.
Strong generic baselines, including model-based MPC and empowerment proxies, do not dominate.
Independent trace-only scorer reproduces primary metrics without evaluator coupling.
Statistical replication passes on fresh seeds without candidate/control code changes.
Blind-holdout ablations remain non-equivalent.
Negative controls do not trigger hallucinated effects or false overclaiming.
No stronger theory claim is made.
```

## Runner Verdict

```text
lcc_contract_strengthened_blind_holdout_bounded
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
Cycle 006 verdict is lcc_contract_strengthened_representation_grounded_bounded.
Cycle 006 nuisance_swap_behavior_change_rate = 0.0
Cycle 006 causal_swap_behavior_change_rate = 1.0
Cycle 006 heldout_spurious_token_failure_rate = 0.08
Cycle 006 history_dependent_disambiguation_success = 0.90
Cycle 006 diagnostic_disambiguation_success = 0.88
Cycle 006 causal_latent_perturbation_action_change_rate = 0.84
Cycle 006 nuisance_latent_perturbation_action_change_rate = 0.06
Cycle 006 cross_renderer_success_rate = 0.89
Cycle 006 behavior-only replay reconstructed 20/20 decisions.
Cycle 007 verdict is lcc_contract_strengthened_relational_compositional_bounded.
Cycle 007 entity_permutation_behavior_change_rate = 0.0
Cycle 007 role_swap_behavior_change_rate = 1.0
Cycle 007 variable_cardinality_success_rate = 0.88
Cycle 007 distractor_invariance_rate = 0.90
Cycle 007 novel_composition_success_rate = 0.84
Cycle 007 tool_chain_success_rate = 0.86
Cycle 007 relation_edge_perturbation_action_change_rate = 0.82
Cycle 007 entity_id_swap_rank_flip_rate = 0.05
Cycle 007 behavior-only replay reconstructed 24/24 decisions.
Cycle 008 verdict is lcc_contract_strengthened_goal_conditioned_reuse_bounded.
Cycle 008 goal_switch_action_change_rate = 1.0
Cycle 008 task_label_invariance_rate = 1.0
Cycle 008 goal_label_permutation_change_rate = 0.0
Cycle 008 goal_vector_perturbation_action_change_rate = 1.0
Cycle 008 constraint_reweighting_action_change_rate = 0.83
Cycle 008 constraint_violation_rate = 0.08
Cycle 008 novel_goal_composition_success_rate = 0.86
Cycle 008 goal_lookup_gap = 0.32
Cycle 008 nearest_neighbor_task_gap = 0.29
Cycle 008 weight_sensitive_tradeoff_rate = 0.82
Cycle 008 zero_shot_goal_switch_success_rate = 0.88
Cycle 008 old_goal_recovery_success = 0.90
Cycle 008 behavior-only replay reconstructed 24/24 decisions.
Cycle 009 verdict is lcc_contract_strengthened_unified_mechanism_bounded.
Cycle 009 overall_family_pass_rate = 0.855556
Cycle 009 min_family_pass_rate = 0.82
Cycle 009 label_permutation_change_rate = 0.0
Cycle 009 effect_swap_change_rate = 0.977778
Cycle 009 mixed behavior-only replay reconstructed 45/45 decisions.
Cycle 009 hybrid_success_rate = 0.82
Cycle 009 specialist_ensemble_gap = 0.24
Cycle 009 nearest_neighbor_gap = 0.27
Cycle 009 static_recipe_gap = 0.31
Cycle 009 metadata_mutation_action_change_rate = 0.0
Cycle 009 contract_id_mutation_action_change_rate = 0.0
Cycle 010 verdict is lcc_contract_strengthened_blind_holdout_bounded.
Cycle 010 freeze candidate_hash_unchanged = true
Cycle 010 blind_holdout instance_count = 200
Cycle 010 blind_holdout template_count = 8
Cycle 010 blind_holdout hybrid_template_count = 4
Cycle 010 overall_success_rate = 1.0
Cycle 010 min_template_success_rate = 1.0
Cycle 010 label_permutation_change_rate = 0.0
Cycle 010 effect_swap_change_rate = 0.995
Cycle 010 behavior-only replay reconstructed 200/200 decisions.
Cycle 010 candidate_beats_non_oracle_count = 10
Cycle 010 model_based_mpc_gap = 0.18
Cycle 010 empowerment_gap = 0.21
Cycle 010 independent_scoring max_abs_diff = 0.0
Cycle 010 replication_success_rate = 1.0
Cycle 010 false_confidence_rate = 0.02
```

## Current Blocker

```text
No successor cycle can proceed until a human reviewer decides whether to accept bounded Cycle 010 evidence, revise the contract, close LCC_v0, or authorize only a new bounded Cycle 011 contract.
```

## Next Frontier

Human review of `LCC_CYCLE_010_BLIND_HOLDOUT` result.

Review decision options:

```text
accept_bounded_contract_result
revise_contract_for_harder_blind_holdout
reject_LCC_v0_despite_bounded_pass
authorize_cycle_011_contract_only
close_current_line
```
