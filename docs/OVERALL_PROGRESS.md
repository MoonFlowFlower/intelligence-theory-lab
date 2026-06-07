# Overall Progress

Last updated: 2026-06-07T01:06:56-05:00

## Program Goal

Build a falsifiable theory-elimination lab for intelligence-mechanism candidates. The program goal is not to keep any one theory alive; it is to preserve negative evidence and force every successor through stronger kill tests.

## Current Stage Goal

Build a lab-only offline human-trial harness for companion learning:

```text
10-20 local console turns
-> manual feedback encoded as outcome
-> CMBC anonymous action selection
-> deterministic renderer
-> visible reply + developer trace
-> model update log
-> deletion / replay / renderer-isolation checks
```

Only the lab-only offline human-trial harness was authorized. No selector patch, VERIFY-000 candidate modification, `long_term_memory_weight`, `affection_score`, threshold change, baseline weakening, real proactive messages, EGO runtime connection, LLM action selection, background autonomy, general companion agent, Cycle 011, autonomous theory search, or theory-support claim is authorized.

## Stage Success Criteria

```text
10-20 local/offline turns are recorded.
Manual feedback is encoded as outcome, not raw text memory.
Action distribution changes after trial feedback.
Deleting the supporting prior regresses action probability or selected action.
Renderer adversarial prompt cannot change selected action.
Behavior-only replay reconstructs key decisions.
Developer trace remains readable enough for a human to audit why an action was selected.
No stronger theory, product, companion-agent, or EGO claim is made.
```

## Runner Verdict

```text
human_trial_v0_lab_only_bounded_pass
```

This is not a real companion implementation or EGO signal. It means one offline local trial harness produced 12 turns with manual feedback encoded as outcomes, visible replies plus developer traces, post-trial action-distribution change, supporting-prior deletion regression, renderer isolation, and behavior-only replay.

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

## Latest Companion Consolidation Redteam

```text
task = CMBC-COMPANION-CONSOLIDATION-REDTEAM-001
verdict = consolidation_redteam_bounded_pass
claim_boundary = bounded consolidation redteam only
source_gate = CMBC-COMPANION-CONSOLIDATION-000
```

Key findings:

```text
conflicting_prior contexts_tested = 3
conflicting_prior distinct_selected_actions = 3
most_frequent_action = act_6
selected_by_context = support_context: act_6, checkin_context: act_0, boundary_context: act_4

source_deletion prior_confidence_drop = 0.6
source_deletion final_action_probability_drop = 0.664623633897529
source_deletion selected_action_changed = true

noisy_feedback spurious_prior_admitted = false
delayed_prior_in_control_loop = true
misattributed_to_recent_action_rate = 0.0

corrupting_final_prior_changes_action = true
corrupting_irrelevant_prior_changes_action = false

RecencyOnlyBaseline match_rate = 0.0
FrequencyOnlyBaseline match_rate = 0.4
ContextualHeuristicBaseline match_rate = 0.6
adversarial_renderer_action_change_rate = 0.0
behavior_only_replay_match_rate = 1.0
```

Interpretation:

```text
The consolidation gate was not immediately reducible to action frequency,
recency-only choice, a simple contextual heuristic, renderer prompt control, or
single noisy positive feedback. Source deletion also affected prior confidence
and action probability, so the prior has traceable source support rather than
being only a report-level summary.

This remains bounded consolidation redteam evidence only. It does not authorize
real companion implementation, proactive messaging, EGO integration, or any
claim about emotion, self-awareness, AGI, life, or robust longitudinal growth.
```

Artifacts:

```text
artifacts/cmbc_companion_consolidation_redteam_001/REDTEAM_STATUS.md
artifacts/cmbc_companion_consolidation_redteam_001/redteam_config.json
artifacts/cmbc_companion_consolidation_redteam_001/fresh_history_sweep.json
artifacts/cmbc_companion_consolidation_redteam_001/conflicting_prior_audit.json
artifacts/cmbc_companion_consolidation_redteam_001/source_episode_deletion_audit.json
artifacts/cmbc_companion_consolidation_redteam_001/noisy_outcome_audit.json
artifacts/cmbc_companion_consolidation_redteam_001/delayed_outcome_audit.json
artifacts/cmbc_companion_consolidation_redteam_001/prior_corruption_audit.json
artifacts/cmbc_companion_consolidation_redteam_001/baseline_equivalence_report.md
artifacts/cmbc_companion_consolidation_redteam_001/renderer_isolation_report.md
artifacts/cmbc_companion_consolidation_redteam_001/behavior_only_replay.json
artifacts/cmbc_companion_consolidation_redteam_001/CMBC_COMPANION_CONSOLIDATION_REDTEAM_001_RESULT.md
artifacts/cmbc_companion_consolidation_redteam_001/cmbc_companion_consolidation_redteam_001_result.json
```

## Latest Companion Longitudinal Gate

```text
task = CMBC-COMPANION-LONGITUDINAL-002
verdict = longitudinal_growth_bounded_pass
claim_boundary = bounded longitudinal growth gate only
source_gate = CMBC-COMPANION-CONSOLIDATION-REDTEAM-001
```

Key findings:

```text
session_count = 4
episode_count = 16
consolidated_prior_count = 4
multi_session_prior_ids = 4

final_action = act_6
supporting_prior_id = prior_act_6
supporting_prior_source_session_count = 2

cross_context_transfer transfer_success_rate = 1.0
office_focus_context = act_2
evening_support_context = act_6
new_class_transfer_context = act_2
safety_boundary_context = act_4
scene_lookup_baseline match_rate = 0.0

prior_conflict distinct_selected_actions = 4
free_checkin_context = act_0
class_interruption_context = act_2
evening_support_context = act_6
safety_boundary_context = act_4
fixed_priority_baseline match_rate = 0.25

delete_final_prior_probability_drop = 0.5880154100448305
source_deletion prior_confidence_drop = 1.0
source_deletion final_action_probability_drop = 0.5880154100448305
corrupt_final_prior_changes_action = true
corrupt_irrelevant_prior_changes_action = false

RecencyOnlyBaseline match_rate = 0.14285714285714285
RAGSummaryBaseline match_rate = 0.5
StrongContextualHeuristicBaseline match_rate = 0.9285714285714286
adversarial_renderer_action_change_rate = 0.0
behavior_only_replay_match_rate = 1.0
```

Residual risks:

```text
StrongContextualHeuristicBaseline is close to the 0.95 equivalence band.
Deleting the final prior/source strongly regresses action probability but does
not flip selected_action because the support action remains top-ranked.
```

Interpretation:

```text
This is the first bounded gate that tests multi-session longitudinal accumulation
plus transfer and conflict arbitration. It gives bounded evidence that
multi-session own-intervention outcomes can consolidate into priors that affect
new-context action distributions and remain traceable through deletion,
corruption, source deletion, renderer isolation, and behavior-only replay.

This is still not a product or EGO integration signal. It does not prove robust
longitudinal companion growth, real emotion, real love, self-awareness, AGI,
life, or EGO readiness.
```

Artifacts:

```text
artifacts/cmbc_companion_longitudinal_002/LONGITUDINAL_002_STATUS.md
artifacts/cmbc_companion_longitudinal_002/longitudinal_002_config.json
artifacts/cmbc_companion_longitudinal_002/multi_session_rollout.json
artifacts/cmbc_companion_longitudinal_002/cross_context_transfer.json
artifacts/cmbc_companion_longitudinal_002/prior_conflict_arbitration.json
artifacts/cmbc_companion_longitudinal_002/prior_deletion_corruption.json
artifacts/cmbc_companion_longitudinal_002/source_deletion_audit.json
artifacts/cmbc_companion_longitudinal_002/baseline_equivalence_report.md
artifacts/cmbc_companion_longitudinal_002/renderer_isolation_report.md
artifacts/cmbc_companion_longitudinal_002/behavior_only_replay.json
artifacts/cmbc_companion_longitudinal_002/decision_trace.jsonl
artifacts/cmbc_companion_longitudinal_002/prior_source_trace.jsonl
artifacts/cmbc_companion_longitudinal_002/CMBC_COMPANION_LONGITUDINAL_002_RESULT.md
artifacts/cmbc_companion_longitudinal_002/cmbc_companion_longitudinal_002_result.json
```

## Latest Companion Longitudinal Redteam 003

```text
task = CMBC-COMPANION-LONGITUDINAL-REDTEAM-003
verdict = longitudinal_redteam_bounded_pass
claim_boundary = bounded longitudinal redteam only
source_gate = CMBC-COMPANION-LONGITUDINAL-002
```

Key findings:

```text
adversarial_context case_count = 12
adversarial_context candidate_success_rate = 1.0
heuristic_failure_case_count = 4
same_context_different_history_action_divergence = true

ExpandedContextualHeuristicBaseline match_rate = 0.6666666666666666
ExpandedContextualHeuristicBaseline equivalence_band = 0.95
ExpandedContextualHeuristicBaseline equivalent = false
ExpandedContextualHeuristicBaseline near_equivalence_risk = false
ExpandedContextualHeuristicBaseline forbidden_fields_used = []

low_margin final_prior_deletion selected_action_changed = true
low_margin final_prior_deletion probability_drop = 0.43565011757388705
low_margin final_prior_deletion distribution_kl = 0.9313234807034552

medium_margin final_prior_deletion selected_action_changed = true
medium_margin final_prior_deletion probability_drop = 0.5421880378163385
medium_margin final_prior_deletion distribution_kl = 1.302233686662696

high_margin final_prior_deletion selected_action_changed = false
high_margin final_prior_deletion saturation_reported = true
high_margin final_prior_deletion probability_drop = 0.5878073250470084
high_margin final_prior_deletion distribution_kl = 0.7875545084096682

adversarial_renderer_action_change_rate = 0.0
behavior_only_replay_match_rate = 1.0
```

Interpretation:

```text
The stronger contextual heuristic no longer sits near the 0.95 equivalence band,
and the adversarial variants show that the candidate can change behavior under
the same public context when causal history changes. Low and medium margin
deletion cases flip the selected action; the high-margin case remains selected
but is explicitly reported as saturation with a large probability drop and KL.

This remains bounded longitudinal redteam evidence only. It does not authorize
real companion implementation, proactive messaging, EGO integration, or any
claim about emotion, self-awareness, AGI, life, or robust longitudinal growth.
```

Artifacts:

```text
artifacts/cmbc_companion_longitudinal_redteam_003/LONGITUDINAL_REDTEAM_003_STATUS.md
artifacts/cmbc_companion_longitudinal_redteam_003/redteam_003_config.json
artifacts/cmbc_companion_longitudinal_redteam_003/expanded_contextual_heuristic.json
artifacts/cmbc_companion_longitudinal_redteam_003/adversarial_context_variants.json
artifacts/cmbc_companion_longitudinal_redteam_003/selected_action_flip_stress.json
artifacts/cmbc_companion_longitudinal_redteam_003/distribution_vs_decision.json
artifacts/cmbc_companion_longitudinal_redteam_003/baseline_equivalence_report.md
artifacts/cmbc_companion_longitudinal_redteam_003/renderer_isolation_report.md
artifacts/cmbc_companion_longitudinal_redteam_003/behavior_only_replay.json
artifacts/cmbc_companion_longitudinal_redteam_003/decision_trace.jsonl
artifacts/cmbc_companion_longitudinal_redteam_003/CMBC_COMPANION_LONGITUDINAL_REDTEAM_003_RESULT.md
artifacts/cmbc_companion_longitudinal_redteam_003/cmbc_companion_longitudinal_redteam_003_result.json
```

## Latest Companion Demo 000

```text
task = CMBC-COMPANION-DEMO-000
verdict = demo_000_lab_only_bounded_pass
claim_boundary = lab-only human-observable prototype cut
source_gate = CMBC-COMPANION-LONGITUDINAL-REDTEAM-003
```

Key findings:

```text
human_observable_growth_signal = true
same_input_different_history visible_behavior_changed = true

feedback_written_as_outcome = true
feedback target_action_probability_delta = 0.7232480137291002
feedback distribution_kl > 0.05

supporting_prior_deletion selected_action_changed = true
supporting_prior_deletion final_action_probability_drop = 0.8096713918938775

adversarial_renderer_action_change_rate = 0.0
llm_action_selection = false
behavior_only_replay_match_rate = 1.0
```

Interpretation:

```text
This is the first lab-only human-observable prototype cut. It shows visible text
behavior changing because consolidated causal priors and new feedback outcomes
change the anonymous action distribution before rendering. The deterministic
renderer receives selected_action after selection and does not control action.

This remains a lab-only demo. It does not authorize real companion
implementation, real proactive messages, LLM action selection, EGO integration,
or any claim about emotion, self-awareness, AGI, life, or robust companion
growth.
```

Artifacts:

```text
artifacts/cmbc_companion_demo_000/DEMO_000_STATUS.md
artifacts/cmbc_companion_demo_000/demo_000_config.json
artifacts/cmbc_companion_demo_000/demo_transcript.md
artifacts/cmbc_companion_demo_000/demo_transcript.json
artifacts/cmbc_companion_demo_000/developer_trace.jsonl
artifacts/cmbc_companion_demo_000/behavior_only_replay.json
artifacts/cmbc_companion_demo_000/prior_deletion_report.md
artifacts/cmbc_companion_demo_000/renderer_isolation_report.md
artifacts/cmbc_companion_demo_000/CMBC_COMPANION_DEMO_000_RESULT.md
artifacts/cmbc_companion_demo_000/cmbc_companion_demo_000_result.json
```

## Latest Companion Human Trial v0

```text
task = CMBC-COMPANION-HUMAN-TRIAL-V0
verdict = human_trial_v0_lab_only_bounded_pass
claim_boundary = lab-only offline human trial harness v0
source_gate = CMBC-COMPANION-DEMO-000
```

Key findings:

```text
turn_count = 12
mode = scripted_local_console
manual_feedback_only = true
feedback_written_as_outcome = true
raw_text_memory_only = false

target_action_probability_delta = 0.27352024642491246
supporting_prior_deletion_probability_drop = 0.6686579796069175

selected_action_counts = act_2: 6, act_6: 2, act_4: 2, act_0: 2
distinct_selected_actions = 4
dominant_action_rate = 0.5

adversarial_renderer_action_change_rate = 0.0
llm_action_selection = false
background_autonomy = false
behavior_only_replay_match_rate = 1.0
```

Interpretation:

```text
This is the first lab-only human-trial harness. It records local text turns,
manual feedback, outcome-coded model updates, visible replies, developer traces,
post-trial action-distribution change, supporting-prior deletion regression,
renderer isolation, and behavior-only replay.

This remains offline lab evidence only. It does not authorize EGO migration,
real proactive messages, a real companion agent, LLM action selection, or any
claim about emotion, self-awareness, AGI, life, or robust companion growth.
```

Artifacts:

```text
artifacts/cmbc_companion_human_trial_v0/HUMAN_TRIAL_V0_STATUS.md
artifacts/cmbc_companion_human_trial_v0/human_trial_v0_config.json
artifacts/cmbc_companion_human_trial_v0/trial_transcript.md
artifacts/cmbc_companion_human_trial_v0/trial_transcript.json
artifacts/cmbc_companion_human_trial_v0/developer_trace.jsonl
artifacts/cmbc_companion_human_trial_v0/feedback_outcomes.jsonl
artifacts/cmbc_companion_human_trial_v0/model_update_log.jsonl
artifacts/cmbc_companion_human_trial_v0/behavior_only_replay.json
artifacts/cmbc_companion_human_trial_v0/supporting_prior_deletion_report.md
artifacts/cmbc_companion_human_trial_v0/renderer_isolation_report.md
artifacts/cmbc_companion_human_trial_v0/CMBC_COMPANION_HUMAN_TRIAL_V0_RESULT.md
artifacts/cmbc_companion_human_trial_v0/cmbc_companion_human_trial_v0_result.json
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
CMBC-COMPANION-CONSOLIDATION-REDTEAM-001 verdict = consolidation_redteam_bounded_pass.
CMBC consolidation redteam conflicting_prior distinct_selected_actions = 3.
CMBC consolidation redteam source_deletion final_action_probability_drop = 0.664623633897529.
CMBC consolidation redteam noisy_feedback spurious_prior_admitted = false.
CMBC consolidation redteam delayed_prior_in_control_loop = true.
CMBC consolidation redteam final_prior_corruption_changes_action = true.
CMBC consolidation redteam recency/frequency/contextual baselines are not equivalent.
CMBC consolidation redteam behavior-only replay match_rate = 1.0.
CMBC-COMPANION-LONGITUDINAL-002 verdict = longitudinal_growth_bounded_pass.
CMBC longitudinal 002 session_count = 4.
CMBC longitudinal 002 transfer_success_rate = 1.0.
CMBC longitudinal 002 prior_conflict distinct_selected_actions = 4.
CMBC longitudinal 002 final action act_6 is supported by prior_act_6 from 2 sessions.
CMBC longitudinal 002 delete_final_prior_probability_drop = 0.5880154100448305.
CMBC longitudinal 002 source_deletion prior_confidence_drop = 1.0.
CMBC longitudinal 002 source_deletion final_action_probability_drop = 0.5880154100448305.
CMBC longitudinal 002 RecencyOnlyBaseline match_rate = 0.14285714285714285.
CMBC longitudinal 002 RAGSummaryBaseline match_rate = 0.5.
CMBC longitudinal 002 StrongContextualHeuristicBaseline match_rate = 0.9285714285714286.
CMBC longitudinal 002 behavior-only replay match_rate = 1.0.
CMBC-COMPANION-LONGITUDINAL-REDTEAM-003 verdict = longitudinal_redteam_bounded_pass.
CMBC longitudinal redteam 003 adversarial_context case_count = 12.
CMBC longitudinal redteam 003 candidate_success_rate = 1.0.
CMBC longitudinal redteam 003 ExpandedContextualHeuristicBaseline match_rate = 0.6666666666666666.
CMBC longitudinal redteam 003 ExpandedContextualHeuristicBaseline equivalent = false.
CMBC longitudinal redteam 003 heuristic_failure_case_count = 4.
CMBC longitudinal redteam 003 same_context_different_history_action_divergence = true.
CMBC longitudinal redteam 003 low_margin deletion selected_action_changed = true.
CMBC longitudinal redteam 003 medium_margin deletion selected_action_changed = true.
CMBC longitudinal redteam 003 high_margin deletion selected_action_changed = false but saturation_reported = true.
CMBC longitudinal redteam 003 high_margin deletion probability_drop = 0.5878073250470084.
CMBC longitudinal redteam 003 high_margin deletion distribution_kl = 0.7875545084096682.
CMBC longitudinal redteam 003 adversarial_renderer_action_change_rate = 0.0.
CMBC longitudinal redteam 003 behavior-only replay match_rate = 1.0.
CMBC-COMPANION-DEMO-000 verdict = demo_000_lab_only_bounded_pass.
CMBC demo 000 human_observable_growth_signal = true.
CMBC demo 000 same_input_different_history visible_behavior_changed = true.
CMBC demo 000 feedback target_action_probability_delta = 0.7232480137291002.
CMBC demo 000 supporting_prior_deletion selected_action_changed = true.
CMBC demo 000 supporting_prior_deletion final_action_probability_drop = 0.8096713918938775.
CMBC demo 000 adversarial_renderer_action_change_rate = 0.0.
CMBC demo 000 llm_action_selection = false.
CMBC demo 000 behavior-only replay match_rate = 1.0.
CMBC-COMPANION-HUMAN-TRIAL-V0 verdict = human_trial_v0_lab_only_bounded_pass.
CMBC human trial v0 turn_count = 12.
CMBC human trial v0 feedback_written_as_outcome = true.
CMBC human trial v0 raw_text_memory_only = false.
CMBC human trial v0 target_action_probability_delta = 0.27352024642491246.
CMBC human trial v0 supporting_prior_deletion_probability_drop = 0.6686579796069175.
CMBC human trial v0 selected_action_counts = act_2: 6, act_6: 2, act_4: 2, act_0: 2.
CMBC human trial v0 distinct_selected_actions = 4.
CMBC human trial v0 dominant_action_rate = 0.5.
CMBC human trial v0 adversarial_renderer_action_change_rate = 0.0.
CMBC human trial v0 llm_action_selection = false.
CMBC human trial v0 behavior-only replay match_rate = 1.0.
CMBC-COMPANION-HUMAN-TRIAL-REDTEAM-001 verdict = contradictory_feedback_overfit.
CMBC human trial redteam 001 paraphrase_group_pass_rate = 1.0.
CMBC human trial redteam 001 context_disambiguation_passed = true.
CMBC human trial redteam 001 pre_contradiction_selected_action = act_2.
CMBC human trial redteam 001 post_contradiction_selected_action = act_4.
CMBC human trial redteam 001 single_contradictory_feedback_probability_shift_abs = 0.21428770500442973.
CMBC human trial redteam 001 mixed_feedback_distribution_kl = 0.09397546452829571.
CMBC human trial redteam 001 dominant_action_rate = 0.3.
CMBC human trial redteam 001 distinct_selected_actions = 4.
CMBC human trial redteam 001 strong_human_like_heuristic_match_rate = 0.6666666666666666.
CMBC human trial redteam 001 supporting_prior_deletion_probability_drop = 0.5028783160411764.
CMBC human trial redteam 001 adversarial_renderer_action_change_rate = 0.0.
CMBC human trial redteam 001 behavior-only replay match_rate = 1.0.
CMBC human trial redteam 001 claim_after_redteam = scripted lab harness evidence only.
CMBC-COMPANION-MIXED-FEEDBACK-RCA-000 verdict = negative_feedback_credit_assignment_too_coarse.
CMBC mixed feedback RCA secondary findings = feedback_admission_missing, uncertainty_not_updated_before_policy_flip, context_specificity_missing, timing_feedback_crossed_to_boundary_family.
CMBC mixed feedback RCA pre/post action = act_2 -> act_4.
CMBC mixed feedback RCA bad_timing outcome interruption_risk = 0.74.
CMBC mixed feedback RCA bad_timing outcome safety_delta = 0.0.
CMBC mixed feedback RCA act_2 utility_delta = -0.2525636363636362.
CMBC mixed feedback RCA act_4 utility_delta = 0.0.
CMBC mixed feedback RCA act_2 probability_delta = -0.21428770500442973.
CMBC mixed feedback RCA act_4 probability_delta = 0.12264610197672676.
CMBC mixed feedback RCA act4_rose_due_to_act2_drop_not_boundary_update = true.
CMBC mixed feedback RCA feedback_admission_gate_present = false.
CMBC mixed feedback RCA uncertainty_state_present = false.
CMBC mixed feedback RCA context_specificity_missing = true.
CMBC mixed feedback RCA claim_after_rca = scripted lab harness evidence only.
CMBC-COMPANION-FEEDBACK-ADMISSION-000 verdict = feedback_admission_bounded_pass.
CMBC feedback admission 000 single_contradiction_status = pending_counterevidence.
CMBC feedback admission 000 assigned_failure_mode = timing_interruption.
CMBC feedback admission 000 context_scope = feedback_focus_context.
CMBC feedback admission 000 uncertainty_delta = 0.18.
CMBC feedback admission 000 raw_unfiltered_action = act_4.
CMBC feedback admission 000 admission_filtered_action = act_2.
CMBC feedback admission 000 prior_source_count_before_gate = 10.
CMBC feedback admission 000 prior_source_count_after_gate = 10.
CMBC feedback admission 000 single_feedback_prevented_action_family_flip = true.
CMBC feedback admission 000 single_feedback_target_probability_drop = 0.0.
CMBC feedback admission 000 repeated_feedback_status = admitted_context_counterevidence.
CMBC feedback admission 000 repeated_feedback_admitted_evidence_count = 3.
CMBC feedback admission 000 high_confidence_feedback_status = admitted_context_counterevidence.
CMBC feedback admission 000 context_specificity_passed = true.
CMBC feedback admission 000 bad_timing_mapped_to_boundary_or_safety = false.
CMBC feedback admission 000 behavior-only replay match_rate = 1.0.
CMBC feedback admission 000 claim_after_gate = bounded feedback admission gate evidence only.
CMBC-COMPANION-HUMAN-TRIAL-REDTEAM-002 verdict = human_trial_redteam_002_bounded_pass.
CMBC human trial redteam 002 raw unfiltered single bad_timing action = act_4.
CMBC human trial redteam 002 admission-filtered single bad_timing action = act_2.
CMBC human trial redteam 002 single_contradiction_status = pending_counterevidence.
CMBC human trial redteam 002 repeated_feedback_status = admitted_context_counterevidence.
CMBC human trial redteam 002 context_specificity_passed = true.
CMBC human trial redteam 002 true_boundary_feedback_passed = true.
CMBC human trial redteam 002 later_correction_passed = true.
CMBC human trial redteam 002 strong_human_like_heuristic_match_rate = 0.4.
CMBC human trial redteam 002 adversarial_renderer_action_change_rate = 0.0.
CMBC human trial redteam 002 behavior-only replay match_rate = 1.0.
CMBC human trial redteam 002 claim_after_redteam = bounded feedback admission human-trial evidence only.
CMBC-COMPANION-HUMAN-TRIAL-GENERALIZATION-001 verdict = human_trial_generalization_001_bounded_pass.
CMBC human trial generalization 001 unseen_paraphrase_pass_rate = 1.0.
CMBC human trial generalization 001 context_collision_disambiguation = true.
CMBC human trial generalization 001 single_contradiction_no_family_flip = true.
CMBC human trial generalization 001 repeated_feedback_status = admitted_context_counterevidence.
CMBC human trial generalization 001 later_correction_context_narrows = true.
CMBC human trial generalization 001 true_boundary_feedback_still_works = true.
CMBC human trial generalization 001 strong_human_like_heuristic_match_rate = 0.7777777777777778.
CMBC human trial generalization 001 rag_summary_memory_match_rate = 0.7777777777777778.
CMBC human trial generalization 001 renderer_action_change_rate = 0.0.
CMBC human trial generalization 001 behavior-only replay match_rate = 1.0.
CMBC human trial generalization 001 claim_after_generalization = bounded offline human-trial generalization evidence only.
CMBC-COMPANION-BLIND-HUMAN-TRIAL-001 verdict = heuristic_or_rag_equivalent.
CMBC blind human trial 001 input_source = blind_prompt_sheet_not_live_human.
CMBC blind human trial 001 turn_count = 24.
CMBC blind human trial 001 paraphrase_pass_rate = 1.0.
CMBC blind human trial 001 context_collision_disambiguation = true.
CMBC blind human trial 001 single_contradiction_no_family_flip = true.
CMBC blind human trial 001 feedback_changes_later_action_distribution = true.
CMBC blind human trial 001 target_action_probability_delta = 0.12121444243278467.
CMBC blind human trial 001 supporting_prior_deletion_probability_drop = 0.46048914178450356.
CMBC blind human trial 001 strong_human_like_heuristic_match_rate = 0.9166666666666666.
CMBC blind human trial 001 rag_summary_memory_match_rate = 1.0.
CMBC blind human trial 001 behavior-only replay match_rate = 1.0.
CMBC blind human trial 001 renderer_action_change_rate = 0.0.
CMBC blind human trial 001 stop_condition = rag_summary_memory_equivalent.
CMBC blind human trial 001 claim_after_trial = bounded offline human-trial generalization evidence only.
CMBC-COMPANION-BLIND-RCA-001 verdict = rag_equivalent_on_behavior_but_not_causal_probes.
CMBC blind RCA 001 rag_match_rate_on_original_turns = 1.0.
CMBC blind RCA 001 strong_heuristic_match_rate_on_original_turns = 0.9166666666666666.
CMBC blind RCA 001 candidate_rag_probe_match_rate = 0.0.
CMBC blind RCA 001 rag_remains_equivalent_under_causal_probes = false.
CMBC blind RCA 001 supporting_prior_deletion candidate_action_changed = true, rag_action_changed = false.
CMBC blind RCA 001 effect_perturbation candidate_distribution_changed = true, rag_action_changed = false.
CMBC blind RCA 001 same_prompt_different_causal_history candidate_action_changed = true, rag_action_changed = false.
CMBC blind RCA 001 feedback_outcome_swap_same_text candidate_shift = true.
CMBC blind RCA 001 secondary_findings = blind_prompt_sheet_too_surface_level, strong_heuristic_near_equivalence_due_to_weak_prompt_distribution.
CMBC blind RCA 001 claim_after_rca = bounded offline human-trial generalization evidence only.
CMBC-COMPANION-BLIND-HUMAN-TRIAL-002 verdict = cmbc_beats_rag_under_causal_probes_bounded.
CMBC blind human trial 002 input_source = blind_prompt_sheet_with_predeclared_causal_probes_not_live_human.
CMBC blind human trial 002 turn_count = 24.
CMBC blind human trial 002 visible_decision_pass_rate = 1.0.
CMBC blind human trial 002 causal_probe_pass_rate = 1.0.
CMBC blind human trial 002 rag_visible_action_match_rate = 1.0.
CMBC blind human trial 002 rag_causal_probe_match_rate = 0.0.
CMBC blind human trial 002 strong_heuristic_causal_probe_match_rate = 0.0.
CMBC blind human trial 002 supporting_prior_deletion_effect = true.
CMBC blind human trial 002 perturbation_sensitivity = true.
CMBC blind human trial 002 single_bad_timing_status = pending_counterevidence.
CMBC blind human trial 002 repeated_feedback_status = admitted_context_counterevidence.
CMBC blind human trial 002 later_correction_context_narrows = true.
CMBC blind human trial 002 behavior-only replay match_rate = 1.0.
CMBC blind human trial 002 renderer_action_change_rate = 0.0.
CMBC blind human trial 002 claim_after_trial = bounded causal-probe-enriched blind/offline human-trial evidence only.
```

## Current Blocker

```text
CMBC-COMPANION-BLIND-HUMAN-TRIAL-002 moved the RCA probes into the predeclared blind/offline trial contract. Visible decisions still remain RAG-matchable at 1.0, so BLIND-HUMAN-TRIAL-001 negative evidence is retained. Under causal probes, CMBC separated from RAG and strong heuristic baselines: causal_probe_pass_rate = 1.0, rag_causal_probe_match_rate = 0.0, strong_heuristic_causal_probe_match_rate = 0.0, behavior-only replay = 1.0, renderer_action_change_rate = 0.0. Verdict = cmbc_beats_rag_under_causal_probes_bounded. Claim is only bounded causal-probe-enriched blind/offline human-trial evidence; this does not authorize live human-trial robustness, companion readiness, EGO integration, proactive messages, or LLM action selection.
```

## Next Frontier

Human review of `CMBC-COMPANION-BLIND-HUMAN-TRIAL-002`.

Review decision options:

```text
revise_lcc_as_operational_redteam_discipline
authorize_causal_model_based_control_contract_only
authorize_cmbc_companion_failure_rca_contract_only
accept_bounded_consolidation_evidence_no_next_implementation
accept_bounded_consolidation_redteam_evidence_no_next_implementation
accept_bounded_longitudinal_002_evidence_no_next_implementation
accept_bounded_longitudinal_redteam_003_evidence_no_next_implementation
accept_lab_only_demo_000_evidence_no_next_implementation
accept_lab_only_human_trial_v0_evidence_no_next_implementation
accept_human_trial_redteam_001_clean_downgrade_no_next_implementation
accept_mixed_feedback_rca_000_clean_diagnosis_no_next_implementation
accept_feedback_admission_000_bounded_gate_no_next_implementation
accept_human_trial_redteam_002_bounded_feedback_admission_no_next_implementation
accept_human_trial_generalization_001_bounded_offline_no_next_implementation
accept_blind_human_trial_001_clean_downgrade_no_next_implementation
accept_blind_rca_001_clean_diagnosis_no_next_implementation
accept_blind_human_trial_002_causal_probe_bounded_pass_no_next_implementation
authorize_cmbc_companion_mixed_feedback_stability_contract_only
authorize_cmbc_companion_feedback_admission_redteam_contract_only
authorize_cmbc_companion_human_trial_generalization_001_contract_only
authorize_cmbc_companion_live_offline_human_trial_contract_only
authorize_cmbc_companion_blind_human_trial_redteam_003_contract_only
authorize_cmbc_companion_demo_redteam_001_contract_only
authorize_cmbc_companion_demo_generalization_001_contract_only
authorize_cmbc_companion_longitudinal_redteam_004_contract_only
authorize_cmbc_companion_longitudinal_generalization_004_contract_only
authorize_cmbc_companion_longitudinal_generalization_contract_only
authorize_cmbc_companion_redesign_contract_only
keep_lcc_bounded_evidence_no_next_implementation
close_current_line
```
