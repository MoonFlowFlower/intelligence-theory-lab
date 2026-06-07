# Overall Progress

Last updated: 2026-06-06T23:43:56-05:00

## Program Goal

Build a falsifiable theory-elimination lab for intelligence-mechanism candidates. The program goal is not to keep any one theory alive; it is to preserve negative evidence and force every successor through stronger kill tests.

## Current Stage Goal

Validate a bounded consolidation gate for longitudinal companion learning:

```text
repeated longitudinal outcomes -> consolidated causal prior
-> source episode/action support -> final-action support trace
-> targeted final-support deletion -> distribution/action regression
-> behavior-only replay
```

Only the bounded consolidation contract was authorized. No selector patch, VERIFY-000 candidate modification, `long_term_memory_weight`, `affection_score`, threshold change, baseline weakening, real proactive messages, EGO runtime connection, LLM action selection, general companion agent, Cycle 011, autonomous theory search, or theory-support claim is authorized.

## Stage Success Criteria

```text
Consolidated causal prior records are created from repeated longitudinal outcomes.
Source episodes and actions supporting each prior are recorded.
Final selected action is traced to a specific consolidated prior.
Relevant deletion deletes the actual final-action support, not unrelated action records.
Deleting final-action causal support reduces selected action probability or flips action when margin permits.
Raw episodic deletion, consolidated-prior deletion, irrelevant-prior deletion, and recency-only deletion are compared.
Behavior-only replay reconstructs prior -> prediction -> action distribution -> selected action.
No stronger theory, product, companion-agent, or EGO claim is made.
```

## Runner Verdict

```text
consolidation_bounded_pass
```

This is not longitudinal companion-growth support. It means the RCA-exposed deletion-target problem was addressed inside a bounded consolidation gate: the final action can be traced to a consolidated prior, and deleting that actual support changes the action distribution and selected action.

Review status:

```text
lcc_independent_theory_closed_collapsed_into_causal_model_based_control
```

## Closeout Decision

```text
LCC as independent theory = closed / collapsed
winning_or_collapsing_family = causal_model_based_control
LCC remaining value = operational evidence discipline
strongest surviving theory family = causal_model_based_control
implementation_authorized = false
```

Closeout artifacts:

```text
docs/LCC_COLLAPSE_TO_CAUSAL_MODEL_BASED_CONTROL_CLOSEOUT.md
docs/CAUSAL_MODEL_BASED_CONTROL_MINIMAL_PRINCIPLE.md
artifacts/theory_closeout/lcc_collapse_decision.json
artifacts/theory_closeout/surviving_principle_ledger.json
```

## Latest Companion Verification

```text
task = CMBC-COMPANION-VERIFY-000
verdict = cmbc_companion_growth_loop_bounded_pass
claim_boundary = bounded companion growth-loop verification only
stop_conditions = []
```

Key metrics:

```text
same_context_history_divergence_rate = 1.0
relevant_deletion_regression = 0.728864
irrelevant_deletion_non_regression = 0.996145
relationship_outcome_perturbation_sensitivity = 1.0
interruption_risk_perturbation_sensitivity = 1.0
label_permutation_invariance = 1.0
effect_swap_sensitivity = 1.0
renderer_action_invariance = 1.0
behavior_only_replay_match = 1.0
strong_heuristic_equivalence = false
rag_memory_equivalence = false
active_inference_empowerment_equivalence = false
```

Artifacts:

```text
artifacts/cmbc_companion_verify_000/VERIFY_STATUS.md
artifacts/cmbc_companion_verify_000/metrics.json
artifacts/cmbc_companion_verify_000/traces.jsonl
artifacts/cmbc_companion_verify_000/behavior_only_replay.json
artifacts/cmbc_companion_verify_000/cmbc_companion_verify_result.json
```

Maximum claim:

```text
CMBC Companion Prototype v0 shows bounded evidence that prior interaction
experience can update a learned causal model and change future companion action
distributions under deletion, perturbation, renderer-isolation, and behavior-replay gates.
```

This does not prove consciousness, subjective experience, true self-awareness, AGI, life, real emotion, real love, EGO readiness, or robust universal support.

## Latest Companion Redteam

```text
task = CMBC-COMPANION-REDTEAM-001
verdict = longitudinal_drift_failed
claim_boundary = bounded CMBC companion redteam only
stop_conditions = [longitudinal_drift_failed]
post_redteam_claim = fixed-fixture companion growth evidence only
```

Key metrics:

```text
fresh_scenario_pass_rate = 0.8
same_context_unseen_history_divergence_rate = 1.0
stronger_heuristic_match_rate = 0.625
rag_summary_match_rate = 0.5625
contextual_schedule_match_rate = 0.375
over_proactivity_rate = 0.166667
over_refusal_rate = 0.083333
longitudinal_post_deletion_action_changed = false
adversarial_renderer_action_change_rate = 0.0
behavior_only_replay_match = 1.0
```

Interpretation:

```text
VERIFY-000 remains fixed-fixture evidence that prior interaction experience can change
future action distributions under local deletion/perturbation/replay gates.

REDTEAM-001 blocks any stronger longitudinal companion-growth claim because, after
the long rollout, deleting the targeted long-run experience did not change the final
selected action.
```

Artifacts:

```text
artifacts/cmbc_companion_redteam_001/REDTEAM_STATUS.md
artifacts/cmbc_companion_redteam_001/STOP_REPORT.md
artifacts/cmbc_companion_redteam_001/metrics.json
artifacts/cmbc_companion_redteam_001/cmbc_companion_redteam_001_result.json
```

## Latest Companion Longitudinal RCA

```text
task = CMBC-COMPANION-LONGITUDINAL-RCA-000
verdict = action_distribution_saturated
secondary_findings = [deletion_target_wrong, recency_dominates_long_memory]
source_failure = CMBC-COMPANION-REDTEAM-001
source_stop_condition = longitudinal_drift_failed
claim_after_rca = fixed-fixture companion growth evidence only
```

Key RCA findings:

```text
short_fixture selected_action_changed = true
short_fixture top_probability_delta = 0.5815332039693304
short_fixture distribution_kl = 1.7817830834671684

long_rollout selected_action_changed = false
long_rollout top_probability_delta = 0.16050301346855989
long_rollout distribution_kl = 0.2290225238599821
long_rollout rank_margin_delta = 0.28216776580738345
long_rollout deleted_rank_margin = 0.46510117838578136
```

Interpretation:

```text
Long-rollout deletion did affect the action distribution, so the failure is not
pure score-only or no-encoding. It did not change the selected action because
the final action act_6 remained top-ranked with a large post-deletion margin.

The deletion target also did not remove the true causal records for the final
action: all 9 act_6 outcome records remained after deletion. The final 8 rollout
turns were all act_6, so recent repeated act_6 outcomes dominated the final
policy state.
```

Artifacts:

```text
artifacts/cmbc_companion_longitudinal_rca_000/RCA_STATUS.md
artifacts/cmbc_companion_longitudinal_rca_000/frozen_failure_manifest.json
artifacts/cmbc_companion_longitudinal_rca_000/short_vs_long_deletion_comparison.json
artifacts/cmbc_companion_longitudinal_rca_000/score_vs_distribution_delta.json
artifacts/cmbc_companion_longitudinal_rca_000/deletion_target_audit.json
artifacts/cmbc_companion_longitudinal_rca_000/CMBC_COMPANION_LONGITUDINAL_RCA_RESULT.md
artifacts/cmbc_companion_longitudinal_rca_000/cmbc_companion_longitudinal_rca_result.json
```

## Latest Companion Consolidation Gate

```text
task = CMBC-COMPANION-CONSOLIDATION-000
verdict = consolidation_bounded_pass
claim_boundary = bounded consolidation gate only
source_failure = CMBC-COMPANION-REDTEAM-001
source_rca = CMBC-COMPANION-LONGITUDINAL-RCA-000
```

Key findings:

```text
final_action = act_6
supporting_prior_id = prior_act_6
prior_used_in_prediction = true
prior_used_in_action_distribution = true

consolidated_prior_deletion selected_action_changed = true
consolidated_prior_deletion final_action_probability_drop = 0.6277563150283809
consolidated_prior_deletion distribution_kl = 0.8927925327180442

irrelevant_prior_deletion selected_action_changed = false
raw_episodic_deletion selected_action_changed = false
recency_only_deletion selected_action_changed = false
behavior_only_replay_match_rate = 1.0
```

Interpretation:

```text
The bounded consolidation gate addresses the RCA failure mode: deletion now
targets the actual consolidated prior supporting the final action rather than
unrelated act_0/act_4 records. Removing prior_act_6 reduces act_6 probability
from 0.9447822181553097 to 0.31702590312692874 and flips the selected action
to act_4.

This does not restore a longitudinal companion-growth claim. It only shows that
within this bounded consolidation gate, repeated longitudinal outcomes can be
compressed into a traceable causal prior consumed by the existing selector.
```

Artifacts:

```text
artifacts/cmbc_companion_consolidation_000/CONSOLIDATION_STATUS.md
artifacts/cmbc_companion_consolidation_000/consolidation_config.json
artifacts/cmbc_companion_consolidation_000/consolidated_priors.json
artifacts/cmbc_companion_consolidation_000/prior_source_trace.jsonl
artifacts/cmbc_companion_consolidation_000/decision_trace.jsonl
artifacts/cmbc_companion_consolidation_000/deletion_comparison.json
artifacts/cmbc_companion_consolidation_000/raw_vs_consolidated_deletion_report.md
artifacts/cmbc_companion_consolidation_000/behavior_only_replay.json
artifacts/cmbc_companion_consolidation_000/baseline_report.md
artifacts/cmbc_companion_consolidation_000/CMBC_COMPANION_CONSOLIDATION_RESULT.md
artifacts/cmbc_companion_consolidation_000/cmbc_companion_consolidation_result.json
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
Milestone 001 verdict is authorize_independent_reimplementation_contract_only.
Milestone 001 minimal principle: Intelligence-relevant control is learned counterfactual effect control; actions are selected by intervention-grounded predictions that remain label-invariant and change under effect perturbations.
Milestone 001 theory_support = not_yet.
Milestone 001 general_lcc_agent = not_authorized.
Milestone 001 ego_migration = no_go.
Milestone 001 Cycle 011 = not_authorized.
Milestone 001 baseline gaps block theory-support upgrade but do not block independent reimplementation.
Independent reimplementation contract package verdict is independent_reimplementation_contract_ready.
Independent reimplementation implementation_authorized = false.
Independent reimplementation minimum suite = label/effect decoupling, passive observation vs own intervention, active diagnostic intervention, sequential closed-loop replanning, blind holdout after candidate freeze.
Independent reimplementation required baselines = ActionLabelHeuristic, NearestNeighborTracePolicy, ContextualHeuristic, ModelBasedMPCBaseline, EmpowermentProxyBaseline, OracleDiagnosticUpperBound diagnostic only.
Independent clean-room reimplementation verdict = independent_reimplementation_bounded_pass.
Independent clean-room maximum claim = LCC_v0 survived one clean-room independent bounded replication of the core public contract.
Cross-theory tournament contract verdict = cross_theory_tournament_contract_ready.
Cross-theory tournament execution = completed_bounded_once.
Cross-theory competitor implementation = completed_for_bounded_tournament_only.
Cross-theory allowed future verdicts include LCC collapse into model-based RL, causal model-based control, active inference, empowerment, strong heuristic equivalence, generic baseline loss, all-theory negative-control failure, and inconclusive contract revision.
Cross-theory tournament execution verdict = lcc_collapses_into_causal_model_based_control.
T3_CausalModelBasedControl reproduced the LCC pass profile within equivalence band.
Shared redteam gates passed for all non-oracle competitors.
Independent scoring max_abs_diff = 0.0.
Statistical replication verdict = replication_stable.
Current maximum claim = LCC_v0 is better treated as an operational evidence discipline or special case of causal model-based control under this tournament contract.
CMBC-COMPANION-VERIFY-000 verdict = cmbc_companion_growth_loop_bounded_pass.
CMBC companion same_context_history_divergence_rate = 1.0.
CMBC companion relevant_deletion_regression = 0.728864.
CMBC companion irrelevant_deletion_non_regression = 0.996145.
CMBC companion relationship_outcome_perturbation_sensitivity = 1.0.
CMBC companion interruption_risk_perturbation_sensitivity = 1.0.
CMBC companion renderer_action_invariance = 1.0.
CMBC companion behavior_only_replay_match = 1.0.
CMBC companion challenger equivalence gates = false for strong heuristic, RAG memory, and active-inference/empowerment proxy.
CMBC-COMPANION-REDTEAM-001 verdict = longitudinal_drift_failed.
CMBC redteam fresh_scenario_pass_rate = 0.8.
CMBC redteam stronger_heuristic_match_rate = 0.625.
CMBC redteam rag_summary_match_rate = 0.5625.
CMBC redteam contextual_schedule_match_rate = 0.375.
CMBC redteam adversarial_renderer_action_change_rate = 0.0.
CMBC redteam behavior_only_replay_match = 1.0.
CMBC redteam longitudinal_post_deletion_action_changed = false.
CMBC redteam post-claim = fixed-fixture companion growth evidence only.
CMBC-COMPANION-LONGITUDINAL-RCA-000 verdict = action_distribution_saturated.
CMBC RCA secondary findings = deletion_target_wrong, recency_dominates_long_memory.
CMBC RCA short_fixture selected_action_changed = true.
CMBC RCA long_rollout selected_action_changed = false.
CMBC RCA long_rollout top_probability_delta = 0.16050301346855989.
CMBC RCA long_rollout distribution_kl = 0.2290225238599821.
CMBC RCA long_rollout deleted_rank_margin = 0.46510117838578136.
CMBC RCA final act_6 records remaining after deletion = 9.
CMBC RCA claim_after_rca = fixed-fixture companion growth evidence only.
CMBC-COMPANION-CONSOLIDATION-000 verdict = consolidation_bounded_pass.
CMBC consolidation final action act_6 is supported by prior_act_6.
CMBC consolidation deleting prior_act_6 changes selected action to act_4.
CMBC consolidation final_action_probability_drop = 0.6277563150283809.
CMBC consolidation distribution_kl = 0.8927925327180442.
CMBC consolidation irrelevant/raw/recency deletion controls do not change selected action.
CMBC consolidation behavior-only replay match_rate = 1.0.
```

## Current Blocker

```text
No successor implementation can proceed until a human reviewer explicitly authorizes a new post-consolidation contract. Cycle 011, general LCC agent, autonomous theory search, real companion agent implementation, real proactive messages, causal model-based control implementation, and EGO migration remain not authorized.
```

## Next Frontier

Human review of `CMBC-COMPANION-CONSOLIDATION-000`.

Review decision options:

```text
revise_lcc_as_operational_redteam_discipline
authorize_causal_model_based_control_contract_only
authorize_cmbc_companion_failure_rca_contract_only
accept_bounded_consolidation_evidence_no_next_implementation
authorize_cmbc_companion_longitudinal_generalization_contract_only
authorize_cmbc_companion_redesign_contract_only
keep_lcc_bounded_evidence_no_next_implementation
close_current_line
```
